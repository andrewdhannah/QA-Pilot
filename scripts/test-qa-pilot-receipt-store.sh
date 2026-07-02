#!/usr/bin/env bash
set -euo pipefail

# QA Pilot Receipt Store Test Runner — QA-PILOT-RECEIPT-STORE-1
# Tests: store module exists, store validator passes, store operations work,
#        register/get/list/status behavior, existing validators preserved

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
STORE_SCRIPT="$SCRIPT_DIR/qa_pilot_receipt_store.py"
STORE_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-receipt-store.py"
RECEIPT_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-receipt.py"
RECEIPT_TEST="$SCRIPT_DIR/test-qa-pilot-receipt.sh"
MCP_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-mcp-surface.py"
MCP_TEST="$SCRIPT_DIR/test-qa-pilot-mcp-surface.sh"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-receipt-store"
STORE_GOV_DOC="$REPO_ROOT/docs/governance/QA-PILOT-RECEIPT-STORE.md"
STORE_SCHEMA="$REPO_ROOT/docs/schemas/qa-pilot-receipt-store.schema.json"
VALID_REGISTER_FIXTURE="$FIXTURES_DIR/valid-register-request.json"
INVALID_AUTH_FIXTURE="$FIXTURES_DIR/invalid-register-authority-claim.json"
INVALID_LIST_FIXTURE="$FIXTURES_DIR/invalid-list-unbounded.json"
DATA_DIR="$REPO_ROOT/data"
INDEX_PATH="$DATA_DIR/receipt-index.json"
PASS=0
FAIL=0
TESTS=0

# Clean up any previous test data
cleanup() {
    rm -rf "$DATA_DIR/receipts/" "$DATA_DIR/receipt-index.json" "$DATA_DIR/receipt-store-status.json" 2>/dev/null || true
}

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Receipt Store Tests — QA-PILOT-RECEIPT-STORE-1"
echo "================================================================="
echo ""

# Clean start
cleanup

# ── Test 1: Store script exists ──
TESTS=$((TESTS + 1))
if [ -f "$STORE_SCRIPT" ]; then
    pass "Receipt store script found"
else
    fail "Store script not found at $STORE_SCRIPT"
fi

# ── Test 2: Store validator passes ──
TESTS=$((TESTS + 1))
VALIDATOR_OUTPUT=$(python3 "$STORE_VALIDATOR" 2>&1) || true
if echo "$VALIDATOR_OUTPUT" | grep -q "ALL CHECKS PASS"; then
    pass "Store validator passes"
else
    fail "Store validator failed"
    echo "       $VALIDATOR_OUTPUT"
fi

# ── Test 3: Register a valid receipt ──
TESTS=$((TESTS + 1))
REGISTER_OUTPUT=$(python3 "$STORE_SCRIPT" register "$VALID_REGISTER_FIXTURE" 2>&1) || true
REGISTER_SUCCESS=$(echo "$REGISTER_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "false")
if [ "$REGISTER_SUCCESS" = "True" ]; then
    REGISTER_ID=$(echo "$REGISTER_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('receipt_id',''))" 2>/dev/null)
    pass "Register succeeded: $REGISTER_ID"
else
    fail "Register failed"
    echo "       $REGISTER_OUTPUT"
fi

# ── Test 4: Get a registered receipt ──
TESTS=$((TESTS + 1))
GET_OUTPUT=$(python3 "$STORE_SCRIPT" get "qapr-20260702-101" 2>&1) || true
GET_FOUND=$(echo "$GET_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('found', False))" 2>/dev/null || echo "false")
if [ "$GET_FOUND" = "True" ]; then
    pass "Get found registered receipt"
else
    fail "Get did not find registered receipt"
    echo "       $GET_OUTPUT"
fi

# ── Test 5: List receipts ──
TESTS=$((TESTS + 1))
LIST_OUTPUT=$(python3 "$STORE_SCRIPT" list --limit 50 2>&1) || true
LIST_COUNT=$(echo "$LIST_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('receipts',[])))" 2>/dev/null || echo "0")
if [ "$LIST_COUNT" -ge 1 ]; then
    pass "List returned $LIST_COUNT receipt(s)"
else
    fail "List returned no receipts"
fi

# ── Test 6: Status works ──
TESTS=$((TESTS + 1))
STATUS_OUTPUT=$(python3 "$STORE_SCRIPT" status 2>&1) || true
STATUS_TOTAL=$(echo "$STATUS_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('receipt_store',{}).get('total_receipts',0))" 2>/dev/null || echo "0")
if [ "$STATUS_TOTAL" -ge 1 ]; then
    pass "Status reports $STATUS_TOTAL total receipts"
else
    fail "Status reports 0 receipts"
    echo "       $STATUS_OUTPUT"
fi

# ── Test 7: Register rejects authority claim ──
TESTS=$((TESTS + 1))
REJECT_OUTPUT=$(python3 "$STORE_SCRIPT" register "$INVALID_AUTH_FIXTURE" 2>&1 || true)
REJECT_SUCCESS=$(echo "$REJECT_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "true")
if [ "$REJECT_SUCCESS" = "False" ]; then
    pass "Register rejected authority-claim receipt"
else
    fail "Register accepted authority-claim receipt"
    echo "       $REJECT_OUTPUT"
fi

# ── Test 8: List rejects unbounded ──
TESTS=$((TESTS + 1))
UNBOUNDED_OUTPUT=$(python3 "$STORE_SCRIPT" list --limit 0 2>&1 || true)
UNBOUNDED_ERROR=$(echo "$UNBOUNDED_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error',''))" 2>/dev/null || echo "")
if [ -n "$UNBOUNDED_ERROR" ]; then
    pass "List rejected unbounded (limit=0): $UNBOUNDED_ERROR"
else
    fail "List accepted unbounded (limit=0)"
fi

# ── Test 9: Get returns advisory_notice ──
TESTS=$((TESTS + 1))
GET_NOTICE=$(echo "$GET_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('advisory_notice',''))" 2>/dev/null || echo "")
NOTICE_LEN=${#GET_NOTICE}
if [ "$NOTICE_LEN" -ge 10 ]; then
    pass "Get includes advisory_notice ($NOTICE_LEN chars)"
else
    fail "Get missing or short advisory_notice"
fi

# ── Test 10: Existing receipt validator still passes (regression) ──
TESTS=$((TESTS + 1))
RECEIPT_VALID_OUTPUT=$(python3 "$RECEIPT_VALIDATOR" 2>&1) || true
if echo "$RECEIPT_VALID_OUTPUT" | grep -q "ALL CHECKS PASS"; then
    pass "Existing receipt validator still passes"
else
    fail "Existing receipt validator regression"
fi

# ── Test 11: Existing receipt test runner still passes (regression) ──
TESTS=$((TESTS + 1))
RECEIPT_TEST_OUTPUT=$(bash "$RECEIPT_TEST" 2>&1) || true
if echo "$RECEIPT_TEST_OUTPUT" | grep -q "All tests pass"; then
    pass "Existing receipt test runner still passes"
else
    fail "Existing receipt test runner regression"
fi

# ── Test 12: Existing MCP surface validator still passes (regression) ──
TESTS=$((TESTS + 1))
MCP_VALID_OUTPUT=$(python3 "$MCP_VALIDATOR" 2>&1) || true
if echo "$MCP_VALID_OUTPUT" | grep -q "ALL CHECKS PASS"; then
    pass "Existing MCP surface validator still passes"
else
    fail "Existing MCP surface validator regression"
fi

# ── Test 13: Existing MCP surface test runner still passes (regression) ──
TESTS=$((TESTS + 1))
MCP_TEST_OUTPUT=$(bash "$MCP_TEST" 2>&1) || true
if echo "$MCP_TEST_OUTPUT" | grep -q "All tests pass"; then
    pass "Existing MCP surface test runner still passes"
else
    fail "Existing MCP surface test runner regression"
fi

# ── Test 14: Store index file is valid JSON ──
TESTS=$((TESTS + 1))
if [ -f "$INDEX_PATH" ]; then
    if python3 -c "import json; json.load(open('$INDEX_PATH'))" 2>/dev/null; then
        pass "Store index is valid JSON"
    else
        fail "Store index is not valid JSON"
    fi
else
    fail "Store index not found"
fi

# Cleanup
cleanup

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
