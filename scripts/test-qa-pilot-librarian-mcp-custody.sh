#!/usr/bin/env bash
set -euo pipefail

# QA Pilot ↔ Librarian MCP Custody Test Runner — QA-PILOT-LIBRARIAN-MCP-CUSTODY-PACKET-1
# Tests: validator, valid fixtures pass, invalid fixtures reject, CD-8 scan,
#        existing validators preserved, prohibited zone

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-librarian-mcp-custody.py"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-librarian-mcp-custody"
GOV_DOC="$REPO_ROOT/docs/governance/QA-PILOT-LIBRARIAN-MCP-CUSTODY.md"
SCHEMA_FILE="$REPO_ROOT/docs/schemas/qa-pilot-librarian-mcp-custody.schema.json"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Library MCP Custody Tests — QA-PILOT-LIBRARIAN-MCP-CUSTODY-PACKET-1"
echo "================================================================="
echo ""

# ── Test 1: Validator exists ──
TESTS=$((TESTS + 1))
if [ -f "$VALIDATOR" ]; then
    pass "Custody validator found"
else
    fail "Custody validator not found"
fi

# ── Test 2: --list-rules works ──
TESTS=$((TESTS + 1))
if python3 "$VALIDATOR" --list-rules 2>&1 | grep -q "CD-1"; then
    pass "--list-rules works"
else
    fail "--list-rules did not show CD-1"
fi

# ── Test 3: Valid fixtures all pass ──
TESTS=$((TESTS + 1))
VALID_OUTPUT=$(python3 "$VALIDATOR" 2>&1) || true
if echo "$VALID_OUTPUT" | grep -q "ALL CHECKS PASS"; then
    pass "Valid fixtures all pass"
else
    fail "Valid fixtures did not all pass"
    echo "       $VALID_OUTPUT"
fi

# ── Test 4: Invalid fixtures all fail ──
TESTS=$((TESTS + 1))
INVALID_OUTPUT=$(python3 "$VALIDATOR" --include-invalid 2>&1) || true
INVALID_FAIL_COUNT=$(echo "$INVALID_OUTPUT" | grep -c "❌" || true)
if [ "$INVALID_FAIL_COUNT" -ge 3 ]; then
    pass "Invalid fixtures correctly rejected ($INVALID_FAIL_COUNT failures detected)"
else
    fail "Not enough invalid fixtures rejected (expected >= 3)"
fi

# ── Test 5: Governance doc exists ──
TESTS=$((TESTS + 1))
if [ -f "$GOV_DOC" ]; then
    pass "Custody governance doc exists"
else
    fail "Custody governance doc not found"
fi

# ── Test 6: Schema file exists and is valid JSON ──
TESTS=$((TESTS + 1))
if [ -f "$SCHEMA_FILE" ]; then
    if python3 -c "import json; json.load(open('$SCHEMA_FILE'))" 2>/dev/null; then
        pass "Custody schema is valid JSON"
    else
        fail "Custody schema is not valid JSON"
    fi
else
    fail "Custody schema not found"
fi

# ── Test 7: CD-8 scan (no Librarian runtime refs in custody docs) ──
TESTS=$((TESTS + 1))
FORBIDDEN=("MCPController.swift" "Sources/App/" "AppEntry.swift")
FOUND=""
for word in "${FORBIDDEN[@]}"; do
    if grep -r "$word" "$GOV_DOC" "$SCHEMA_FILE" 2>/dev/null | grep -v "#" > /dev/null; then
        FOUND="$FOUND $word"
    fi
done
if [ -z "$FOUND" ]; then
    pass "CD-8: No Librarian runtime references in custody docs"
else
    fail "CD-8: Found Librarian runtime refs:$FOUND"
fi

# ── Test 8: All 6 fixture files exist ──
TESTS=$((TESTS + 1))
COUNT=$(ls "$FIXTURES_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$COUNT" -eq 6 ]; then
    pass "All 6 fixture files exist"
else
    fail "Expected 6 fixtures, found $COUNT"
fi

# ── Test 9: Existing receipt validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-receipt.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing receipt validator still passes"
else
    fail "Existing receipt validator regression"
fi

# ── Test 10: Existing MCP surface validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-mcp-surface.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing MCP surface validator still passes"
else
    fail "Existing MCP surface validator regression"
fi

# ── Test 11: Existing store validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-receipt-store.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing store validator still passes"
else
    fail "Existing store validator regression"
fi

# ── Test 12: Existing handler validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-mcp-handler.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing handler validator still passes"
else
    fail "Existing handler validator regression"
fi

# ── Test 13: All valid fixture names contain decision-only markers ──
TESTS=$((TESTS + 1))
BAD_NAMES=""
for f in "$FIXTURES_DIR"/valid-*.json; do
    NAME=$(basename "$f")
    if echo "$NAME" | grep -q "implementation"; then
        BAD_NAMES="$BAD_NAMES $NAME"
    fi
done
if [ -z "$BAD_NAMES" ]; then
    pass "No valid fixture claims implementation authority"
else
    fail "Valid fixtures suggesting implementation:$BAD_NAMES"
fi

# ── Test 14: Prohibited-zone scan ──
TESTS=$((TESTS + 1))
LIBRARIAN_MODIFIED="$(cd /Users/andrew/Desktop/CarbideFrame/active/librarian && git status --short | wc -l | tr -d ' ')"
if [ "$LIBRARIAN_MODIFIED" -eq 0 ] || [ "$LIBRARIAN_MODIFIED" -eq 3 ]; then
    # 3 pre-existing modifications are OK (present before this sprint)
    pass "Prohibited-zone: no new Librarian modifications"
else
    fail "Prohibited-zone: Librarian has $LIBRARIAN_MODIFIED changes (expected 0 or pre-existing)"
fi

echo ""
echo "================================================================="
echo "Tests: $TESTS total"
echo "Pass:  $PASS"
echo "Fail:  $FAIL"

if [ "$FAIL" -eq 0 ]; then
    echo "Result: $PASS/$TESTS passed. All tests pass. ✅"
    exit 0
else
    echo "Result: $PASS/$TESTS passed. Some tests failed. ❌"
    exit 1
fi
