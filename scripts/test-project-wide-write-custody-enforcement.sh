#!/usr/bin/env bash
# test-project-wide-write-custody-enforcement.sh
# Test runner for PROJECT-WIDE-WRITE-CUSTODY-ENFORCEMENT-1
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENFORCER="$SCRIPT_DIR/enforce-project-wide-write-custody.py"
FIXTURES_DIR="$PROJECT_ROOT/docs/examples/project-wide-write-custody-enforcement"

PASS=0
FAIL=0
SKIP=0

test_fixture() {
    local fixture="$1"
    local name
    name="$(basename "$fixture")"

    # Parse expected decision from fixture
    local expected
    expected=$(python3 -c "
import json
with open('$fixture') as f:
    d = json.load(f)
print(d.get('expected_decision', 'ALLOW'))
" 2>/dev/null)

    # Run enforcement
    local output
    output=$(python3 "$ENFORCER" --input "$fixture" 2>&1 || true)

    # Extract actual decision from first JSON block only
    local actual
    actual=$(echo "$output" | python3 -c "
import sys, json
text = sys.stdin.read()
# Find the first complete JSON object by counting braces
depth = 0
start = -1
for i, ch in enumerate(text):
    if ch == '{':
        if start < 0:
            start = i
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0 and start >= 0:
            try:
                d = json.loads(text[start:i+1])
                print(d.get('decision', 'UNKNOWN'))
            except:
                print('PARSE_ERROR')
            break
" 2>/dev/null)

    if [ "$actual" = "$expected" ]; then
        echo "  ✅ $name — decision=$actual (expected=$expected)"
        PASS=$((PASS + 1))
    else
        echo "  ❌ $name — decision=$actual (expected=$expected)"
        FAIL=$((FAIL + 1))
    fi
}

# ── Test group 1: Valid fixtures ──────────────────────────────────────────
echo ""
echo "=== Group 1: Valid fixtures — ALLOW expected ==="
for fixture in "$FIXTURES_DIR"/valid-*.json; do
    [ -f "$fixture" ] && test_fixture "$fixture"
done

# ── Test group 2: Invalid fixtures ────────────────────────────────────────
echo ""
echo "=== Group 2: Invalid fixtures — BLOCK expected ==="
for fixture in "$FIXTURES_DIR"/invalid-*.json; do
    [ -f "$fixture" ] && test_fixture "$fixture"
done

# ── Test group 3: Sealed evidence fixtures ────────────────────────────────
echo ""
echo "=== Group 3: Sealed evidence — FORBIDDEN_SEALED_EVIDENCE ==="
for fixture in "$FIXTURES_DIR"/invalid-sealed-*.json; do
    [ -f "$fixture" ] && test_fixture "$fixture"
done

# ── Test group 4: CLI mode tests ──────────────────────────────────────────
echo ""
echo "=== Group 4: CLI mode — manual tests ==="

# Helper: extract decision from enforcement output
extract_decision() {
    echo "$1" | python3 -c "
import sys, json
text = sys.stdin.read()
depth = 0; start = -1
for i, ch in enumerate(text):
    if ch == '{':
        if start < 0: start = i
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0 and start >= 0:
            try:
                print(json.loads(text[start:i+1]).get('decision', 'UNKNOWN'))
            except:
                print('PARSE_ERROR')
            break
" 2>/dev/null
}

# Test 4a: No authority → WRITE_SCOPE_VIOLATION
output=$(python3 "$ENFORCER" --project qa-pilot --path "random/file.txt" --action "read" 2>&1 || true)
actual=$(extract_decision "$output")
if [ "$actual" = "BLOCK_WRITE_SCOPE_VIOLATION" ]; then
    echo "  ✅ CLI: No authority → BLOCK_WRITE_SCOPE_VIOLATION"
    PASS=$((PASS + 1))
else
    echo "  ❌ CLI: No authority → $actual (expected BLOCK_WRITE_SCOPE_VIOLATION)"
    FAIL=$((FAIL + 1))
fi

# Test 4b: Authority file without approval → REQUIRES_OWNER_APPROVAL
output=$(python3 "$ENFORCER" --project qa-pilot --path "startup-contract.json" --action "modify" 2>&1 || true)
actual=$(extract_decision "$output")
if [ "$actual" = "REQUIRES_OWNER_APPROVAL" ]; then
    echo "  ✅ CLI: Authority file no approval → REQUIRES_OWNER_APPROVAL"
    PASS=$((PASS + 1))
else
    echo "  ❌ CLI: Authority file no approval → $actual (expected REQUIRES_OWNER_APPROVAL)"
    FAIL=$((FAIL + 1))
fi

# Test 4c: Sealed → FORBIDDEN_SEALED_EVIDENCE
output=$(python3 "$ENFORCER" --project qa-pilot --path "receipts/decisions/x.json" --sealed --action "edit" 2>&1 || true)
actual=$(extract_decision "$output")
if [ "$actual" = "FORBIDDEN_SEALED_EVIDENCE" ]; then
    echo "  ✅ CLI: Sealed evidence → FORBIDDEN_SEALED_EVIDENCE"
    PASS=$((PASS + 1))
else
    echo "  ❌ CLI: Sealed evidence → $actual (expected FORBIDDEN_SEALED_EVIDENCE)"
    FAIL=$((FAIL + 1))
fi

# Test 4d: Post-release without patch → FORBIDDEN_POST_RELEASE_ROUTINE_EDIT
output=$(python3 "$ENFORCER" --project qa-pilot --path "release/release.zip" --release-state released --action "edit" 2>&1 || true)
actual=$(extract_decision "$output")
if [ "$actual" = "FORBIDDEN_POST_RELEASE_ROUTINE_EDIT" ]; then
    echo "  ✅ CLI: Post-release no patch → FORBIDDEN_POST_RELEASE_ROUTINE_EDIT"
    PASS=$((PASS + 1))
else
    echo "  ❌ CLI: Post-release no patch → $actual (expected FORBIDDEN_POST_RELEASE_ROUTINE_EDIT)"
    FAIL=$((FAIL + 1))
fi

# Test 4e: Warning output check
output=$(python3 "$ENFORCER" --project qa-pilot --path "startup-contract.json" --action "modify" 2>&1 || true)
has_warning=$(echo "$output" | grep -c "WRITE AUTHORITY WARNING" || true)
if [ "$has_warning" -ge 1 ]; then
    echo "  ✅ CLI: WRITE AUTHORITY WARNING emitted"
    PASS=$((PASS + 1))
else
    echo "  ❌ CLI: No WRITE AUTHORITY WARNING found"
    FAIL=$((FAIL + 1))
fi

# Test 4f: Broad approval → BLOCK_WRITE_SCOPE_VIOLATION
output=$(python3 "$ENFORCER" --project qa-pilot --path "docs/planning/all.md" \
    --action "Approve everything" --owner-approved --owner-broad 2>&1 || true)
actual=$(extract_decision "$output")
if [ "$actual" = "BLOCK_WRITE_SCOPE_VIOLATION" ]; then
    echo "  ✅ CLI: Broad approval → BLOCK_WRITE_SCOPE_VIOLATION"
    PASS=$((PASS + 1))
else
    echo "  ❌ CLI: Broad approval → $actual (expected BLOCK_WRITE_SCOPE_VIOLATION)"
    FAIL=$((FAIL + 1))
fi

# Test 4g: Allowlisted write → ALLOW
output=$(python3 "$ENFORCER" --project qa-pilot --path "scripts/my-script.py" \
    --action "Update" --allowlisted 2>&1 || true)
actual=$(extract_decision "$output")
if [ "$actual" = "ALLOW" ]; then
    echo "  ✅ CLI: Allowlisted → ALLOW"
    PASS=$((PASS + 1))
else
    echo "  ❌ CLI: Allowlisted → $actual (expected ALLOW)"
    FAIL=$((FAIL + 1))
fi

# ── Results ────────────────────────────────────────────────────────────────
echo ""
echo "=========================================="
echo " PROJECT-WIDE-WRITE-CUSTODY-ENFORCEMENT-1"
echo "=========================================="
echo "  ✅ Passed: $PASS"
echo "  ❌ Failed: $FAIL"
echo "  ⚠️  Skipped: $SKIP"
echo ""

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0
