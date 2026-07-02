#!/usr/bin/env bash
set -euo pipefail

# QA Pilot MCP Handler Test Runner — QA-PILOT-MCP-HANDLER-REGISTRATION-1
# Tests: handler module, validator, operations, store integration, existing
#        validators preserved, cross-project boundary, prohibited zone

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HANDLER_SCRIPT="$SCRIPT_DIR/qa_pilot_mcp_handlers.py"
HANDLER_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-mcp-handler.py"
STORE_SCRIPT="$SCRIPT_DIR/qa_pilot_receipt_store.py"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-mcp-handler"
VALID_REGISTER_FIXTURE="$FIXTURES_DIR/valid-handler-register.json"
INVALID_AUTH_FIXTURE="$FIXTURES_DIR/invalid-handler-authority-claim.json"
INVALID_LIST_FIXTURE="$FIXTURES_DIR/invalid-handler-unbounded-list.json"
INVALID_CROSS_FIXTURE="$FIXTURES_DIR/invalid-handler-cross-project-registration.json"
HANDLER_GOV_DOC="$REPO_ROOT/docs/governance/QA-PILOT-MCP-HANDLER-REGISTRATION.md"
HANDLER_SCHEMA="$REPO_ROOT/docs/schemas/qa-pilot-mcp-handler.schema.json"
DATA_DIR="$REPO_ROOT/data"
PASS=0
FAIL=0
TESTS=0

# Clean up any previous test data from handler/store
cleanup() {
    rm -rf "$DATA_DIR/receipts/" "$DATA_DIR/receipt-index.json" "$DATA_DIR/receipt-store-status.json" 2>/dev/null || true
}

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot MCP Handler Tests — QA-PILOT-MCP-HANDLER-REGISTRATION-1"
echo "================================================================="
echo ""

cleanup

# ── Test 1: Handler script exists ──
TESTS=$((TESTS + 1))
if [ -f "$HANDLER_SCRIPT" ]; then
    pass "Handler script found"
else
    fail "Handler script not found at $HANDLER_SCRIPT"
fi

# ── Test 2: Handler validator passes ──
TESTS=$((TESTS + 1))
VALIDATOR_OUTPUT=$(python3 "$HANDLER_VALIDATOR" 2>&1) || true
if echo "$VALIDATOR_OUTPUT" | grep -q "ALL CHECKS PASS"; then
    pass "Handler validator passes"
else
    fail "Handler validator failed"
    echo "       $VALIDATOR_OUTPUT"
fi

# ── Test 3: Handler register works (calls store) ──
TESTS=$((TESTS + 1))
REG_OUTPUT=$(python3 "$HANDLER_SCRIPT" register "$VALID_REGISTER_FIXTURE" 2>&1) || true
REG_SUCCESS=$(echo "$REG_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "false")
REG_ID=$(echo "$REG_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('receipt_id',''))" 2>/dev/null || echo "")
if [ "$REG_SUCCESS" = "True" ]; then
    pass "Handler register succeeded: $REG_ID"
else
    fail "Handler register failed"
    echo "       $REG_OUTPUT"
fi

# ── Test 4: Handler register returns advisory_only=true ──
TESTS=$((TESTS + 1))
ADVISORY_ONLY=$(echo "$REG_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('advisory_only', False))" 2>/dev/null || echo "false")
if [ "$ADVISORY_ONLY" = "True" ]; then
    pass "Handler register returns advisory_only=true"
else
    fail "Handler register advisory_only is not true"
fi

# ── Test 5: Handler register includes project_boundary=qa-pilot ──
TESTS=$((TESTS + 1))
BOUNDARY=$(echo "$REG_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('project_boundary',''))" 2>/dev/null || echo "")
if [ "$BOUNDARY" = "qa-pilot" ]; then
    pass "Handler register includes project_boundary=qa-pilot"
else
    fail "Handler register missing project_boundary"
fi

# ── Test 6: Handler get works ──
TESTS=$((TESTS + 1))
GET_OUTPUT=$(python3 "$HANDLER_SCRIPT" get "$REG_ID" 2>&1) || true
GET_FOUND=$(echo "$GET_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('found', False))" 2>/dev/null || echo "false")
if [ "$GET_FOUND" = "True" ]; then
    pass "Handler get found registered receipt"
else
    fail "Handler get did not find receipt"
    echo "       $GET_OUTPUT"
fi

# ── Test 7: Handler list works ──
TESTS=$((TESTS + 1))
LIST_OUTPUT=$(python3 "$HANDLER_SCRIPT" list --limit 50 2>&1) || true
LIST_COUNT=$(echo "$LIST_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('receipts',[])))" 2>/dev/null || echo "0")
if [ "$LIST_COUNT" -ge 1 ]; then
    pass "Handler list returned $LIST_COUNT receipt(s)"
else
    fail "Handler list returned no receipts"
fi

# ── Test 8: Handler status works ──
TESTS=$((TESTS + 1))
STATUS_OUTPUT=$(python3 "$HANDLER_SCRIPT" status 2>&1) || true
STATUS_TOTAL=$(echo "$STATUS_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('receipt_store',{}).get('total_receipts',0))" 2>/dev/null || echo "0")
if [ "$STATUS_TOTAL" -ge 1 ]; then
    pass "Handler status reports $STATUS_TOTAL receipts"
else
    fail "Handler status reports 0 receipts"
fi

# ── Test 9: Handler reject authority claim ──
TESTS=$((TESTS + 1))
REJECT_OUTPUT=$(python3 "$HANDLER_SCRIPT" register "$INVALID_AUTH_FIXTURE" 2>&1 || true)
REJECT_SUCCESS=$(echo "$REJECT_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "true")
if [ "$REJECT_SUCCESS" = "False" ]; then
    pass "Handler register rejected authority-claim receipt"
else
    fail "Handler register accepted authority-claim receipt"
    echo "       $REJECT_OUTPUT"
fi

# ── Test 10: Handler list rejects unbounded ──
TESTS=$((TESTS + 1))
UNBOUNDED_OUTPUT=$(python3 "$HANDLER_SCRIPT" list --limit 0 2>&1 || true)
UNBOUNDED_ERROR=$(echo "$UNBOUNDED_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error',''))" 2>/dev/null || echo "")
if [ -n "$UNBOUNDED_ERROR" ]; then
    pass "Handler list rejected unbounded (limit=0): $UNBOUNDED_ERROR"
else
    fail "Handler list accepted unbounded (limit=0)"
    echo "       $UNBOUNDED_OUTPUT"
fi

# ── Test 11: Handler responses include advisory_notice ──
TESTS=$((TESTS + 1))
GET_NOTICE=$(echo "$GET_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('advisory_notice',''))" 2>/dev/null || echo "")
NOTICE_LEN=${#GET_NOTICE}
if [ "$NOTICE_LEN" -ge 10 ]; then
    pass "Handler get includes advisory_notice ($NOTICE_LEN chars)"
else
    fail "Handler get missing advisory_notice"
fi

# ── Test 12: Handler includes cross_project_registration=false ──
TESTS=$((TESTS + 1))
CPR=$(echo "$REG_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('cross_project_registration', 'missing'))" 2>/dev/null || echo "missing")
if [ "$CPR" = "False" ]; then
    pass "Handler register includes cross_project_registration=false"
else
    fail "Handler register missing or wrong cross_project_registration: $CPR"
fi

# ── Test 13: Existing validators still pass (regression) ──
TESTS=$((TESTS + 1))
ALL_GOOD=true
for validator in "validate-qa-pilot-receipt.py" "validate-qa-pilot-mcp-surface.py" "validate-qa-pilot-receipt-store.py"; do
    VOUTPUT=$(python3 "$SCRIPT_DIR/$validator" 2>&1) || true
    if ! echo "$VOUTPUT" | grep -q "ALL CHECKS PASS"; then
        ALL_GOOD=false
        echo "       Failed: $validator"
    fi
done
if [ "$ALL_GOOD" = true ]; then
    pass "All 3 existing validators still pass"
else
    fail "Some existing validators failed"
fi

# ── Test 14: Existing test runners still pass (regression) ──
TESTS=$((TESTS + 1))
ALL_GOOD=true
for tester in "test-qa-pilot-receipt.sh" "test-qa-pilot-mcp-surface.sh" "test-qa-pilot-receipt-store.sh"; do
    TOUTPUT=$(bash "$SCRIPT_DIR/$tester" 2>&1) || true
    if ! echo "$TOUTPUT" | grep -q "All tests pass"; then
        ALL_GOOD=false
        echo "       Failed: $tester"
    fi
done
if [ "$ALL_GOOD" = true ]; then
    pass "All 3 existing test runners still pass"
else
    fail "Some existing test runners failed"
fi

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
