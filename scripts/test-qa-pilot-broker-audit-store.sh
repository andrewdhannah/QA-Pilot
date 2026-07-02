#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
STORE="$SCRIPT_DIR/qa_pilot_broker_audit_store.py"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-broker-audit-store.py"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-broker-audit-store"
AUDIT_DIR="$REPO_ROOT/data/audit/broker"
GOV_DOC="$REPO_ROOT/docs/governance/QA-PILOT-BROKER-AUDIT-STORE-IMPLEMENTATION.md"
SCHEMA_FILE="$REPO_ROOT/docs/schemas/qa-pilot-broker-audit-store.schema.json"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Broker Audit Store Tests — QA-PILOT-BROKER-AUDIT-STORE-IMPLEMENTATION-1"
echo "==============================================================================="
echo ""

# Clean up any test artifacts from previous runs
rm -f "$AUDIT_DIR"/qabr-audit-store-test-*.json
rm -f "$REPO_ROOT/data/audit/broker-index.json"
rm -f "$REPO_ROOT/data/audit/broker-store-status.json"

# ── Test 1: Validator exists and passes ──
TESTS=$((TESTS + 1))
if python3 "$VALIDATOR" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Audit store validator passes"
else
    fail "Audit store validator failed"
    python3 "$VALIDATOR" 2>&1
fi

# ── Test 2: Store module exists ──
TESTS=$((TESTS + 1))
if [ -f "$STORE" ]; then
    pass "Audit store module exists"
else
    fail "Audit store module not found"
fi

# ── Test 3: Store CLI works (status) ──
TESTS=$((TESTS + 1))
STATUS_OUT=$(python3 "$STORE" status 2>&1) || true
if echo "$STATUS_OUT" | grep -q "broker_audit_store"; then
    pass "Store status CLI works"
else
    fail "Store status CLI failed: $(echo "$STATUS_OUT" | head -3)"
fi

# ── Test 4: Register valid audit receipt ──
TESTS=$((TESTS + 1))
VALID_FIXTURE="$FIXTURES_DIR/valid-register-audit-request.json"
if [ -f "$VALID_FIXTURE" ]; then
    REG_OUT=$(python3 "$STORE" register "$VALID_FIXTURE" 2>&1) || true
    if echo "$REG_OUT" | grep -q '"success": true'; then
        pass "Valid register accepted"
    else
        fail "Valid register failed: $(echo "$REG_OUT" | head -5)"
    fi
else
    fail "Valid register fixture not found"
fi

# ── Test 5: Get stored audit receipt ──
TESTS=$((TESTS + 1))
GET_OUT=$(python3 "$STORE" get "qabr-audit-store-test-001" 2>&1) || true
if echo "$GET_OUT" | grep -q '"found": true'; then
    pass "Get returns stored audit receipt"
else
    fail "Get did not find stored receipt: $(echo "$GET_OUT" | head -3)"
fi

# ── Test 6: List audit receipts ──
TESTS=$((TESTS + 1))
LIST_OUT=$(python3 "$STORE" list --limit 10 2>&1) || true
if echo "$LIST_OUT" | grep -q "audit_receipts"; then
    pass "List returns audit receipts"
else
    fail "List failed: $(echo "$LIST_OUT" | head -3)"
fi

# ── Test 7: List total_count >= 1 ──
TESTS=$((TESTS + 1))
COUNT=$(echo "$LIST_OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('total_count', 0))" 2>/dev/null) || COUNT=0
if [ "$COUNT" -ge 1 ]; then
    pass "List returns at least 1 receipt"
else
    fail "List returned 0 receipts"
fi

# ── Test 8: Status shows registered receipt ──
TESTS=$((TESTS + 1))
ST_OUT=$(python3 "$STORE" status 2>&1) || true
TOTAL=$(echo "$ST_OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('broker_audit_store',{}).get('total_audit_receipts', 0))" 2>/dev/null) || TOTAL=0
if [ "$TOTAL" -ge 1 ]; then
    pass "Status shows registered receipt"
else
    fail "Status shows 0 receipts"
fi

# ── Test 9: Register invalid approval effect is rejected ──
TESTS=$((TESTS + 1))
INVALID_APPROVAL="$FIXTURES_DIR/invalid-register-approval-effect.json"
if [ -f "$INVALID_APPROVAL" ]; then
    REG_APPROVAL=$(python3 "$STORE" register "$INVALID_APPROVAL" 2>&1) || true
    if echo "$REG_APPROVAL" | grep -q '"success": false'; then
        pass "Approval effect register rejected"
    else
        fail "Approval effect was not rejected: $(echo "$REG_APPROVAL" | head -5)"
    fi
else
    fail "Approval effect fixture not found"
fi

# ── Test 10: Register invalid Librarian path is rejected ──
TESTS=$((TESTS + 1))
INVALID_LIB="$FIXTURES_DIR/invalid-register-librarian-path.json"
if [ -f "$INVALID_LIB" ]; then
    REG_LIB=$(python3 "$STORE" register "$INVALID_LIB" 2>&1) || true
    if echo "$REG_LIB" | grep -q '"success": false'; then
        pass "Librarian path register rejected"
    else
        fail "Librarian path was not rejected: $(echo "$REG_LIB" | head -5)"
    fi
else
    fail "Librarian path fixture not found"
fi

# ── Test 11: List with unbounded limit (0) is rejected ──
TESTS=$((TESTS + 1))
UNBOUNDED_OUT=$(python3 "$STORE" list --limit 0 2>&1) || true
if echo "$UNBOUNDED_OUT" | grep -q "error"; then
    pass "Unbounded list rejected"
else
    fail "Unbounded list was not rejected: $(echo "$UNBOUNDED_OUT" | head -3)"
fi

# ── Test 12: List with limit > 100 is rejected ──
TESTS=$((TESTS + 1))
OVER_OUT=$(python3 "$STORE" list --limit 200 2>&1) || true
if echo "$OVER_OUT" | grep -q "error"; then
    pass "Over-limit list rejected"
else
    fail "Over-limit list was not rejected"
fi

# ── Test 13: Get non-existent audit_id returns not_found ──
TESTS=$((TESTS + 1))
NOT_FOUND=$(python3 "$STORE" get "nonexistent-audit-id-999" 2>&1) || true
if echo "$NOT_FOUND" | grep -q '"found": false'; then
    pass "Get non-existent returns not_found"
else
    fail "Get non-existent did not return not_found"
fi

# ── Test 14: Advisory notice in get response ──
TESTS=$((TESTS + 1))
if echo "$GET_OUT" | grep -q "advisory_only\|advisory-only\|advisory_notice"; then
    pass "Get response includes advisory notice"
else
    fail "Get response missing advisory notice"
fi

# ── Test 15: Advisory notice in list response ──
TESTS=$((TESTS + 1))
if echo "$LIST_OUT" | grep -q "advisory"; then
    pass "List response includes advisory notice"
else
    fail "List response missing advisory notice"
fi

# ── Test 16: Advisory notice in status response ──
TESTS=$((TESTS + 1))
if echo "$ST_OUT" | grep -q "advisory"; then
    pass "Status response includes advisory notice"
else
    fail "Status response missing advisory notice"
fi

# ── Test 17: Governance doc exists ──
TESTS=$((TESTS + 1))
if [ -f "$GOV_DOC" ]; then
    pass "Audit store governance doc exists"
else
    fail "Audit store governance doc not found"
fi

# ── Test 18: Store schema is valid JSON ──
TESTS=$((TESTS + 1))
if [ -f "$SCHEMA_FILE" ]; then
    if python3 -c "import json; json.load(open('$SCHEMA_FILE'))" 2>/dev/null; then
        pass "Store schema is valid JSON"
    else
        fail "Store schema is not valid JSON"
    fi
else
    fail "Store schema not found"
fi

# ── Test 19: Existing broker plan validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-broker-plan.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing broker plan validator still passes"
else
    fail "Existing broker plan validator regression"
fi

# ── Test 20: Existing implementation validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-broker-implementation.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing implementation validator still passes"
else
    fail "Existing implementation validator regression"
fi

# ── Test 21: Existing advisory surface validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-broker-advisory-surface.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing advisory surface validator still passes"
else
    fail "Existing advisory surface validator regression"
fi

# ── Test 22: Existing audit receipt validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-broker-audit-receipt.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing audit receipt validator still passes"
else
    fail "Existing audit receipt validator regression"
fi

# ── Test 23: Existing receipt validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-receipt.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing receipt validator still passes"
else
    fail "Existing receipt validator regression"
fi

# ── Test 24: Existing MCP surface validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-mcp-surface.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing MCP surface validator still passes"
else
    fail "Existing MCP surface validator regression"
fi

# ── Test 25: Existing store validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-receipt-store.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing store validator still passes"
else
    fail "Existing store validator regression"
fi

# ── Test 26: Existing handler validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-mcp-handler.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing handler validator still passes"
else
    fail "Existing handler validator regression"
fi

# ── Test 27: Existing custody validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-librarian-mcp-custody.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing custody validator still passes"
else
    fail "Existing custody validator regression"
fi

# ── Test 28: All 8 fixture files exist ──
TESTS=$((TESTS + 1))
COUNT=$(ls "$FIXTURES_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$COUNT" -eq 8 ]; then
    pass "All 8 fixture files exist (4 valid + 4 invalid)"
else
    fail "Expected 8 fixtures, found $COUNT"
fi

# ── Test 29: Prohibited-zone scan ──
TESTS=$((TESTS + 1))
PROHIBITED_HITS=""
if [ -f "/Users/andrew/Desktop/CarbideFrame/active/librarian/scripts/qa_pilot_broker_audit_store.py" ]; then
    PROHIBITED_HITS="$PROHIBITED_HITS store-script"
fi
if [ -f "/Users/andrew/Desktop/CarbideFrame/active/librarian/docs/governance/QA-PILOT-BROKER-AUDIT-STORE-IMPLEMENTATION.md" ]; then
    PROHIBITED_HITS="$PROHIBITED_HITS store-gov-doc"
fi
if [ -z "$PROHIBITED_HITS" ]; then
    pass "Prohibited-zone: no QA Pilot audit store files leaked into Librarian"
else
    fail "Prohibited-zone: found audit store files in Librarian:$PROHIBITED_HITS"
fi

echo ""
echo "==============================================================================="
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
