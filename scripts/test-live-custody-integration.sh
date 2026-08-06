#!/usr/bin/env bash
# test-live-custody-integration.sh — Test runner for LIVE-CUSTODY-INTEGRATION-1
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
INTEGRATOR="$SCRIPT_DIR/live-custody-integration.py"
FIXTURES_DIR="$PROJECT_ROOT/docs/examples/live-custody-integration"
AUDIT_DIR="$PROJECT_ROOT/data/custody-audit"

PASS=0
FAIL=0

# Helper: extract decision from integration output
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

extract_write_executed() {
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
                print(json.loads(text[start:i+1]).get('write_executed', 'UNKNOWN'))
            except:
                print('PARSE_ERROR')
            break
" 2>/dev/null
}

extract_receipt_id() {
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
                print(json.loads(text[start:i+1]).get('receipt_id', ''))
            except:
                print('')
            break
" 2>/dev/null
}

run_fixture_test() {
    local fixture="$1"
    local name
    name="$(basename "$fixture")"

    local expected_decision
    expected_decision=$(python3 -c "import json; print(json.load(open('$fixture')).get('expected_decision',''))" 2>/dev/null)
    local expected_write
    expected_write=$(python3 -c "import json; print(json.load(open('$fixture')).get('expected_write_executed','false'))" 2>/dev/null)
    local mode
    mode=$(python3 -c "import json; print(json.load(open('$fixture')).get('mode','live'))" 2>/dev/null)

    # Build temp input
    local tmp_input
    tmp_input=$(mktemp)
    python3 -c "
import json
d = json.load(open('$fixture'))
req = d['request']
json.dump({**req, 'content': req.get('content','')}, open('$tmp_input','w'))
"
    local output
    output=$(python3 "$INTEGRATOR" "$mode" --input "$tmp_input" 2>&1 || true)
    rm -f "$tmp_input"

    local actual_decision
    actual_decision=$(extract_decision "$output")
    local actual_write
    actual_write=$(extract_write_executed "$output")

    if [ "$actual_decision" = "$expected_decision" ] && [ "$actual_write" = "$expected_write" ]; then
        echo "  ✅ $name — decision=$actual_decision write=$actual_write"
        PASS=$((PASS + 1))
    else
        echo "  ❌ $name — expected decision=$expected_decision write=$expected_write, got decision=$actual_decision write=$actual_write"
        FAIL=$((FAIL + 1))
    fi
}

# Clean audit dir before tests
rm -f "$AUDIT_DIR"/*.json

echo "=========================================="
echo " LIVE-CUSTODY-INTEGRATION-1 Test Runner"
echo "=========================================="
echo ""

# ── Test Group 1: Fixture-based tests ─────────────────────────────────────
echo "=== Group 1: Fixture-based integration tests ==="
for fixture in "$FIXTURES_DIR"/*.json; do
    [ -f "$fixture" ] && run_fixture_test "$fixture"
done

# ── Test Group 2: Acceptance gate tests (CLI) ─────────────────────────────
echo ""
echo "=== Group 2: Acceptance gate tests ==="

# AG-1: Live write path invokes custody before mutation
output=$(python3 "$INTEGRATOR" live --path "scripts/_ag1_test.py" --content "# AG-1" \
    --project qa-pilot --allowlisted --sprint "AG-1" 2>&1 || true)
dec=$(extract_decision "$output")
we=$(extract_write_executed "$output")
if [ "$dec" = "ALLOW" ] && [ "$we" = "True" ]; then
    echo "  ✅ AG-1: Live write path invokes custody — ALLOW, file written"
    PASS=$((PASS + 1))
else
    echo "  ❌ AG-1: Expected ALLOW+write, got $dec/$we"
    FAIL=$((FAIL + 1))
fi

# AG-2: WRITE_SCOPE_VIOLATION blocks mutation
output=$(python3 "$INTEGRATOR" live --path "some/unlisted.txt" --content "data" \
    --project qa-pilot --sprint "AG-2" 2>&1 || true)
dec=$(extract_decision "$output")
we=$(extract_write_executed "$output")
if [ "$dec" = "BLOCK_WRITE_SCOPE_VIOLATION" ] && [ "$we" = "False" ]; then
    echo "  ✅ AG-2: WRITE_SCOPE_VIOLATION blocks mutation"
    PASS=$((PASS + 1))
else
    echo "  ❌ AG-2: Expected BLOCK, got $dec/$we"
    FAIL=$((FAIL + 1))
fi

# AG-3: Authority file emits warning + requires Owner approval
output=$(python3 "$INTEGRATOR" live --path "docs/governance/some-authority-file.md" --content "# test" \
    --project qa-pilot --sprint "AG-3" 2>&1 || true)
dec=$(extract_decision "$output")
we=$(extract_write_executed "$output")
has_warning=$(echo "$output" | grep -c "WRITE AUTHORITY WARNING" || true)
if [ "$dec" != "ALLOW" ] && [ "$we" = "False" ] && [ "$has_warning" -ge 1 ]; then
    echo "  ✅ AG-3: Authority file blocked with warning"
    PASS=$((PASS + 1))
else
    echo "  ❌ AG-3: Expected blocked+warning, got $dec/$we warning=$has_warning"
    FAIL=$((FAIL + 1))
fi

# AG-4: Sealed evidence immutable in live path
output=$(python3 "$INTEGRATOR" live --path "receipts/dummy.json" --content "{}" \
    --project qa-pilot --sealed --sprint "AG-4" 2>&1 || true)
dec=$(extract_decision "$output")
we=$(extract_write_executed "$output")
if echo "$dec" | grep -q "FORBIDDEN" && [ "$we" = "False" ]; then
    echo "  ✅ AG-4: Sealed evidence immutable in live path"
    PASS=$((PASS + 1))
else
    echo "  ❌ AG-4: Expected FORBIDDEN, got $dec/$we"
    FAIL=$((FAIL + 1))
fi

# AG-5: Post-release path requires patch order
output=$(python3 "$INTEGRATOR" live --path "Public/app.js" --content "// edit" \
    --project qa-pilot --release-state released --sprint "AG-5" 2>&1 || true)
dec=$(extract_decision "$output")
we=$(extract_write_executed "$output")
if echo "$dec" | grep -q "POST_RELEASE" && [ "$we" = "False" ]; then
    echo "  ✅ AG-5: Post-release requires patch order"
    PASS=$((PASS + 1))
else
    echo "  ❌ AG-5: Expected POST_RELEASE, got $dec/$we"
    FAIL=$((FAIL + 1))
fi

# AG-6: Generated state deterministic-tool-only
output=$(python3 "$INTEGRATOR" live --path "STARTUP-STATE.md" --content "# State" \
    --project qa-pilot --generated --sprint "AG-6" 2>&1 || true)
dec=$(extract_decision "$output")
we=$(extract_write_executed "$output")
if echo "$dec" | grep -q "GENERATED" && [ "$we" = "False" ]; then
    echo "  ✅ AG-6: Generated state — non-deterministic tool blocked"
    PASS=$((PASS + 1))
else
    echo "  ❌ AG-6: Expected GENERATED block, got $dec/$we"
    FAIL=$((FAIL + 1))
fi

# AG-6b: Generated state WITH deterministic tool → ALLOW
output=$(python3 "$INTEGRATOR" live --path "STARTUP-STATE.md" --content "# State" \
    --project qa-pilot --generated --tool-deterministic --sprint "AG-6b" 2>&1 || true)
dec=$(extract_decision "$output")
we=$(extract_write_executed "$output")
if [ "$dec" = "ALLOW" ] && [ "$we" = "True" ]; then
    echo "  ✅ AG-6b: Generated state — deterministic tool allowed"
    PASS=$((PASS + 1))
else
    echo "  ❌ AG-6b: Expected ALLOW, got $dec/$we"
    FAIL=$((FAIL + 1))
fi

# AG-7: Broad project-root approval rejected
output=$(python3 "$INTEGRATOR" live --path "docs/planning/stuff.md" --content "# All" \
    --project qa-pilot --owner-approved --owner-broad --sprint "AG-7" 2>&1 || true)
dec=$(extract_decision "$output")
we=$(extract_write_executed "$output")
if echo "$dec" | grep -q "BLOCK" && [ "$we" = "False" ]; then
    echo "  ✅ AG-7: Broad project-root approval rejected"
    PASS=$((PASS + 1))
else
    echo "  ❌ AG-7: Expected BLOCK, got $dec/$we"
    FAIL=$((FAIL + 1))
fi

# AG-8: Dry-run produces custody decision without writing
output=$(python3 "$INTEGRATOR" dry-run --path "some/file.txt" --content "test" \
    --project qa-pilot --sprint "AG-8" 2>&1 || true)
dec=$(extract_decision "$output")
we=$(extract_write_executed "$output")
if [ "$we" = "False" ] && [ -n "$dec" ] && [ "$dec" != "PARSE_ERROR" ]; then
    echo "  ✅ AG-8: Dry-run produces decision, no write (decision=$dec)"
    PASS=$((PASS + 1))
else
    echo "  ❌ AG-8: Expected dry-run decision, got $dec write=$we"
    FAIL=$((FAIL + 1))
fi

# AG-9: Denied writes produce evidence receipts
audit_count_before=$(ls "$AUDIT_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
python3 "$INTEGRATOR" live --path "blocked-test.txt" --content "x" \
    --project qa-pilot --sprint "AG-9" > /dev/null 2>&1 || true
audit_count_after=$(ls "$AUDIT_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$audit_count_after" -gt "$audit_count_before" ]; then
    echo "  ✅ AG-9: Denied writes produce evidence receipts ($((audit_count_after - audit_count_before)) new)"
    PASS=$((PASS + 1))
else
    echo "  ❌ AG-9: Expected new audit receipt, count: $audit_count_before → $audit_count_after"
    FAIL=$((FAIL + 1))
fi

# AG-10: Approved writes preserve approval provenance
output=$(python3 "$INTEGRATOR" live --path "scripts/_ag10_test.py" --content "# AG-10" \
    --project qa-pilot --allowlisted --sprint "AG-10" --owner-approved \
    --owner-approval-ref "OD-AG-10-TEST" 2>&1 || true)
receipt_id=$(extract_receipt_id "$output")
if [ -n "$receipt_id" ]; then
    receipt_path="$AUDIT_DIR/$receipt_id.json"
    if [ -f "$receipt_path" ]; then
        approval_ref=$(python3 -c "import json; print(json.load(open('$receipt_path')).get('result',{}).get('owner_approval_ref',''))" 2>/dev/null)
        if [ "$approval_ref" = "OD-AG-10-TEST" ]; then
            echo "  ✅ AG-10: Approved write preserves approval provenance (ref=$approval_ref)"
            PASS=$((PASS + 1))
        else
            echo "  ❌ AG-10: Approval ref mismatch, got '$approval_ref'"
            FAIL=$((FAIL + 1))
        fi
    else
        echo "  ❌ AG-10: Receipt not found at $receipt_path"
        FAIL=$((FAIL + 1))
    fi
else
    echo "  ❌ AG-10: No receipt_id in output"
    FAIL=$((FAIL + 1))
fi

# AG-11: Existing #23 enforcement fixtures still pass
enforcement_output=$(bash "$PROJECT_ROOT/scripts/test-project-wide-write-custody-enforcement.sh" 2>&1 || true)
enf_pass=$(echo "$enforcement_output" | grep -c "Passed: 16" || true)
enf_fail=$(echo "$enforcement_output" | grep -c "Failed: 0" || true)
if [ "$enf_pass" -ge 1 ] && [ "$enf_fail" -ge 1 ]; then
    echo "  ✅ AG-11: Existing #23 enforcement fixtures still pass (16/16)"
    PASS=$((PASS + 1))
else
    echo "  ❌ AG-11: Enforcement regression detected"
    echo "$enforcement_output" | tail -5
    FAIL=$((FAIL + 1))
fi

# Final audit count
total_audits=$(ls "$AUDIT_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
echo ""
echo "=== Audit trail: $total_audits receipts in $AUDIT_DIR ==="

# Results
echo ""
echo "=========================================="
echo " LIVE-CUSTODY-INTEGRATION-1 Test Runner"
echo "=========================================="
echo "  ✅ Passed: $PASS"
echo "  ❌ Failed: $FAIL"
echo ""

# Cleanup test files
rm -f "$PROJECT_ROOT/scripts/_ag1_test.py" "$PROJECT_ROOT/scripts/_ag10_test.py" 2>/dev/null || true

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0
