#!/usr/bin/env bash
set -euo pipefail

# QA Pilot Broker Audit Receipt Test Runner — QA-PILOT-BROKER-AUDIT-RECEIPT-STORE-1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-broker-audit-receipt.py"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-broker-audit"
GOV_DOC="$REPO_ROOT/docs/governance/QA-PILOT-BROKER-AUDIT-RECEIPT-STORE.md"
SCHEMA_FILE="$REPO_ROOT/docs/schemas/qa-pilot-broker-audit-receipt.schema.json"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Broker Audit Receipt Tests — QA-PILOT-BROKER-AUDIT-RECEIPT-STORE-1"
echo "=========================================================================="
echo ""

# ── Test 1: Validator exists ──
TESTS=$((TESTS + 1))
if [ -f "$VALIDATOR" ]; then
    pass "Audit receipt validator found"
else
    fail "Audit receipt validator not found"
fi

# ── Test 2: --list-rules works ──
TESTS=$((TESTS + 1))
if python3 "$VALIDATOR" --list-rules 2>&1 | grep -q "BA-1"; then
    pass "--list-rules works"
else
    fail "--list-rules did not show BA-1"
fi

# ── Test 3: Valid fixtures all pass ──
TESTS=$((TESTS + 1))
if python3 "$VALIDATOR" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Valid fixtures all pass"
else
    fail "Valid fixtures did not all pass"
    python3 "$VALIDATOR" 2>&1
fi

# ── Test 4: Invalid fixtures all fail ──
TESTS=$((TESTS + 1))
INVALID_OUTPUT=$(python3 "$VALIDATOR" --include-invalid 2>&1) || true
INVALID_FAIL_COUNT=$(echo "$INVALID_OUTPUT" | grep -c "❌" || true)
if [ "$INVALID_FAIL_COUNT" -ge 4 ]; then
    pass "Invalid fixtures correctly rejected ($INVALID_FAIL_COUNT failures detected)"
else
    fail "Not enough invalid fixtures rejected (expected >= 4)"
fi

# ── Test 5: All 7 fixture files exist ──
TESTS=$((TESTS + 1))
COUNT=$(ls "$FIXTURES_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$COUNT" -eq 7 ]; then
    pass "All 7 fixture files exist (3 valid + 4 invalid)"
else
    fail "Expected 7 fixtures, found $COUNT"
fi

# ── Test 6: Governance doc exists ──
TESTS=$((TESTS + 1))
if [ -f "$GOV_DOC" ]; then
    pass "Audit receipt governance doc exists"
else
    fail "Audit receipt governance doc not found"
fi

# ── Test 7: Schema file exists and is valid JSON ──
TESTS=$((TESTS + 1))
if [ -f "$SCHEMA_FILE" ]; then
    if python3 -c "import json; json.load(open('$SCHEMA_FILE'))" 2>/dev/null; then
        pass "Audit receipt schema is valid JSON"
    else
        fail "Audit receipt schema is not valid JSON"
    fi
else
    fail "Audit receipt schema not found"
fi

# ── Test 8: BA-12 scan (no Librarian runtime refs) ──
TESTS=$((TESTS + 1))
FORBIDDEN=("MCPController.swift" "Sources/App/" "AppEntry.swift")
FOUND=""
for word in "${FORBIDDEN[@]}"; do
    if grep -r "$word" "$GOV_DOC" "$SCHEMA_FILE" 2>/dev/null | grep -v "#" > /dev/null; then
        FOUND="$FOUND $word"
    fi
done
if [ -z "$FOUND" ]; then
    pass "BA-12: No Librarian runtime references in audit receipt docs"
else
    fail "BA-12: Found Librarian runtime refs:$FOUND"
fi

# ── Test 9: Existing broker plan validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-broker-plan.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing broker plan validator still passes"
else
    fail "Existing broker plan validator regression"
fi

# ── Test 10: Existing implementation validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-broker-implementation.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing implementation validator still passes"
else
    fail "Existing implementation validator regression"
fi

# ── Test 11: Existing advisory surface validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-broker-advisory-surface.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing advisory surface validator still passes"
else
    fail "Existing advisory surface validator regression"
fi

# ── Test 12: Existing receipt validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-receipt.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing receipt validator still passes"
else
    fail "Existing receipt validator regression"
fi

# ── Test 13: Existing MCP surface validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-mcp-surface.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing MCP surface validator still passes"
else
    fail "Existing MCP surface validator regression"
fi

# ── Test 14: Existing store validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-receipt-store.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing store validator still passes"
else
    fail "Existing store validator regression"
fi

# ── Test 15: Existing handler validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-mcp-handler.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing handler validator still passes"
else
    fail "Existing handler validator regression"
fi

# ── Test 16: Existing custody validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-librarian-mcp-custody.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing custody validator still passes"
else
    fail "Existing custody validator regression"
fi

# ── Test 17: Valid fixture names do not claim authority ──
TESTS=$((TESTS + 1))
BAD_NAMES=""
for f in "$FIXTURES_DIR"/valid-*.json; do
    NAME=$(basename "$f")
    if echo "$NAME" | grep -q "approval\|seal\|merge\|production"; then
        BAD_NAMES="$BAD_NAMES $NAME"
    fi
done
if [ -z "$BAD_NAMES" ]; then
    pass "No valid fixture claims approval/seal/merge authority"
else
    fail "Valid fixtures claiming authority:$BAD_NAMES"
fi

# ── Test 18: QA Pilot ledger is valid JSON ──
TESTS=$((TESTS + 1))
if python3 -c "import json; json.load(open('$REPO_ROOT/project-state/sprint-ledger.json'))" 2>/dev/null; then
    pass "QA Pilot ledger is valid JSON"
else
    fail "QA Pilot ledger is not valid JSON"
fi

# ── Test 19: Prohibited-zone scan ──
TESTS=$((TESTS + 1))
PROHIBITED_HITS=""
if [ -f "/Users/andrew/Desktop/CarbideFrame/active/librarian/docs/governance/QA-PILOT-BROKER-AUDIT-RECEIPT-STORE.md" ]; then
    PROHIBITED_HITS="$PROHIBITED_HITS gov-doc"
fi
if [ -f "/Users/andrew/Desktop/CarbideFrame/active/librarian/scripts/validate-qa-pilot-broker-audit-receipt.py" ]; then
    PROHIBITED_HITS="$PROHIBITED_HITS validator"
fi
if [ -z "$PROHIBITED_HITS" ]; then
    pass "Prohibited-zone: no QA Pilot audit files leaked into Librarian"
else
    fail "Prohibited-zone: found audit files in Librarian:$PROHIBITED_HITS"
fi

echo ""
echo "=========================================================================="
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
