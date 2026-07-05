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
rm -f "$AUDIT_DIR"/qabr-audit-harden-*.json
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

# ── Test 28 (updated): Fixture files exist (originals + hardening) ──
TESTS=$((TESTS + 1))
COUNT=$(ls "$FIXTURES_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
VALID_COUNT=$(ls "$FIXTURES_DIR"/valid-*.json 2>/dev/null | wc -l | tr -d ' ')
INVALID_COUNT=$(ls "$FIXTURES_DIR"/invalid-*.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$COUNT" -ge 8 ]; then
    pass "$COUNT total fixture files ($VALID_COUNT valid, $INVALID_COUNT invalid)"
else
    fail "Expected at least 8 fixtures, found $COUNT"
fi
# ── Test 29: Path traversal audit_id rejected ──
TESTS=$((TESTS + 1))
TRAVERSAL_FIXTURE="$FIXTURES_DIR/invalid-path-traversal-audit-id.json"
if [ -f "$TRAVERSAL_FIXTURE" ]; then
    REG_TRAV=$(python3 "$STORE" register "$TRAVERSAL_FIXTURE" 2>&1) || true
    if echo "$REG_TRAV" | grep -q '"success": false'; then
        pass "Path traversal audit_id rejected"
    else
        fail "Path traversal audit_id was not rejected: $(echo "$REG_TRAV" | head -3)"
    fi
else
    fail "Path traversal fixture not found"
fi

# ── Test 30: Absolute path in audit_id rejected ──
TESTS=$((TESTS + 1))
ABS_FIXTURE="$FIXTURES_DIR/invalid-absolute-path-audit-id.json"
if [ -f "$ABS_FIXTURE" ]; then
    REG_ABS=$(python3 "$STORE" register "$ABS_FIXTURE" 2>&1) || true
    if echo "$REG_ABS" | grep -q '"success": false'; then
        pass "Absolute path audit_id rejected"
    else
        fail "Absolute path audit_id was not rejected: $(echo "$REG_ABS" | head -3)"
    fi
else
    fail "Absolute path fixture not found"
fi

# ── Test 31: Duplicate audit_id rejected ──
TESTS=$((TESTS + 1))
DUP_FIXTURE="$FIXTURES_DIR/invalid-duplicate-audit-id.json"
if [ -f "$DUP_FIXTURE" ]; then
    REG_DUP=$(python3 "$STORE" register "$DUP_FIXTURE" 2>&1) || true
    if echo "$REG_DUP" | grep -q '"success": false'; then
        pass "Duplicate audit_id rejected"
    else
        fail "Duplicate audit_id was not rejected: $(echo "$REG_DUP" | head -3)"
    fi
else
    fail "Duplicate fixture not found"
fi

# ── Test 32: Missing required fields rejected ──
TESTS=$((TESTS + 1))
MISSING_FIXTURE="$FIXTURES_DIR/invalid-missing-required-field.json"
if [ -f "$MISSING_FIXTURE" ]; then
    REG_MISS=$(python3 "$STORE" register "$MISSING_FIXTURE" 2>&1) || true
    if echo "$REG_MISS" | grep -q '"success": false'; then
        pass "Missing required field rejected"
    else
        fail "Missing required field was not rejected: $(echo "$REG_MISS" | head -3)"
    fi
else
    fail "Missing field fixture not found"
fi

# ── Test 33: Invalid status rejected ──
TESTS=$((TESTS + 1))
BAD_STATUS_FIXTURE="$FIXTURES_DIR/invalid-bad-status.json"
if [ -f "$BAD_STATUS_FIXTURE" ]; then
    REG_BS=$(python3 "$STORE" register "$BAD_STATUS_FIXTURE" 2>&1) || true
    if echo "$REG_BS" | grep -q '"success": false'; then
        pass "Invalid status rejected"
    else
        fail "Invalid status was not rejected: $(echo "$REG_BS" | head -3)"
    fi
else
    fail "Invalid status fixture not found"
fi

# ── Test 34: Bad timestamp rejected ──
TESTS=$((TESTS + 1))
BAD_TS_FIXTURE="$FIXTURES_DIR/invalid-bad-timestamp.json"
if [ -f "$BAD_TS_FIXTURE" ]; then
    REG_BTS=$(python3 "$STORE" register "$BAD_TS_FIXTURE" 2>&1) || true
    if echo "$REG_BTS" | grep -q '"success": false'; then
        pass "Bad timestamp rejected"
    else
        fail "Bad timestamp was not rejected: $(echo "$REG_BTS" | head -3)"
    fi
else
    fail "Bad timestamp fixture not found"
fi

# ── Test 35: Project ID mismatch rejected ──
TESTS=$((TESTS + 1))
PID_FIXTURE="$FIXTURES_DIR/invalid-project-id-mismatch.json"
if [ -f "$PID_FIXTURE" ]; then
    REG_PID=$(python3 "$STORE" register "$PID_FIXTURE" 2>&1) || true
    if echo "$REG_PID" | grep -q '"success": false'; then
        pass "Project ID mismatch rejected"
    else
        fail "Project ID mismatch was not rejected: $(echo "$REG_PID" | head -3)"
    fi
else
    fail "Project ID mismatch fixture not found"
fi

# ── Test 36: Status transition completed -> running rejected ──
TESTS=$((TESTS + 1))
# First register a test audit, transition to completed, then try invalid transition
TRANS_TEST_ID="qabr-audit-harden-trans-complete"
# Register
python3 "$STORE" register "$FIXTURES_DIR/valid-register-audit-request.json" > /dev/null 2>&1 || true
# Need a separate audit for transition testing - register with unique ID
echo "{\"fixture_type\":\"test\",\"description\":\"transition test\",\"audit_receipt\":{\"audit_id\":\"$TRANS_TEST_ID\",\"receipt_type\":\"broker_audit\",\"active_project_id\":\"qa-pilot\",\"target_project_id\":\"qa-pilot\",\"requested_tool\":\"qa_pilot_receipt_register\",\"custody_record_id\":\"cc-trans-test\",\"handler_path\":\"active/qa-pilot/scripts/qa_pilot_mcp_handlers.py\",\"authority_level\":\"R1\",\"advisory_only\":true,\"output_effects\":[\"advisory_registration\"],\"audit_timestamp\":\"2026-07-02T23:00:00+00:00\",\"rollback_reference\":\"docs/governance/QA-PILOT-BROKER-IMPLEMENTATION.md\",\"validation_result\":\"pass\"}}" > /tmp/qa_pilot_trans_test.json
python3 "$STORE" register /tmp/qa_pilot_trans_test.json > /dev/null 2>&1 || true
# Transition to running then completed
python3 "$STORE" update-status "$TRANS_TEST_ID" running > /dev/null 2>&1 || true
python3 "$STORE" update-status "$TRANS_TEST_ID" completed > /dev/null 2>&1 || true
# Now try invalid transition
TRANS_OUT=$(python3 "$STORE" update-status "$TRANS_TEST_ID" running 2>&1) || true
if echo "$TRANS_OUT" | grep -q '"success": false'; then
    pass "Invalid transition (completed->running) rejected"
else
    fail "Invalid transition was not rejected: $(echo "$TRANS_OUT" | head -3)"
fi

# ── Test 37: Status transition failed -> running rejected ──
TESTS=$((TESTS + 1))
FAIL_TEST_ID="qabr-audit-harden-trans-fail"
echo "{\"fixture_type\":\"test\",\"description\":\"transition fail test\",\"audit_receipt\":{\"audit_id\":\"$FAIL_TEST_ID\",\"receipt_type\":\"broker_audit\",\"active_project_id\":\"qa-pilot\",\"target_project_id\":\"qa-pilot\",\"requested_tool\":\"qa_pilot_receipt_register\",\"custody_record_id\":\"cc-trans-fail\",\"handler_path\":\"active/qa-pilot/scripts/qa_pilot_mcp_handlers.py\",\"authority_level\":\"R1\",\"advisory_only\":true,\"output_effects\":[\"advisory_registration\"],\"audit_timestamp\":\"2026-07-02T23:00:00+00:00\",\"rollback_reference\":\"docs/governance/QA-PILOT-BROKER-IMPLEMENTATION.md\",\"validation_result\":\"pass\"}}" > /tmp/qa_pilot_trans_fail.json
python3 "$STORE" register /tmp/qa_pilot_trans_fail.json > /dev/null 2>&1 || true
# Transition to running then failed
python3 "$STORE" update-status "$FAIL_TEST_ID" running > /dev/null 2>&1 || true
python3 "$STORE" update-status "$FAIL_TEST_ID" failed > /dev/null 2>&1 || true
# Try invalid transition
TRANS_FAIL_OUT=$(python3 "$STORE" update-status "$FAIL_TEST_ID" running 2>&1) || true
if echo "$TRANS_FAIL_OUT" | grep -q '"success": false'; then
    pass "Invalid transition (failed->running) rejected"
else
    fail "Invalid transition was not rejected: $(echo "$TRANS_FAIL_OUT" | head -3)"
fi

# ── Test 38: Valid status transition registered -> running accepted ──
TESTS=$((TESTS + 1))
RUN_TEST_ID="qabr-audit-harden-trans-to-running"
echo "{\"fixture_type\":\"test\",\"description\":\"valid transition test\",\"audit_receipt\":{\"audit_id\":\"$RUN_TEST_ID\",\"receipt_type\":\"broker_audit\",\"active_project_id\":\"qa-pilot\",\"target_project_id\":\"qa-pilot\",\"requested_tool\":\"qa_pilot_receipt_register\",\"custody_record_id\":\"cc-trans-valid\",\"handler_path\":\"active/qa-pilot/scripts/qa_pilot_mcp_handlers.py\",\"authority_level\":\"R1\",\"advisory_only\":true,\"output_effects\":[\"advisory_registration\"],\"audit_timestamp\":\"2026-07-02T23:00:00+00:00\",\"rollback_reference\":\"docs/governance/QA-PILOT-BROKER-IMPLEMENTATION.md\",\"validation_result\":\"pass\"}}" > /tmp/qa_pilot_trans_valid.json
python3 "$STORE" register /tmp/qa_pilot_trans_valid.json > /dev/null 2>&1 || true
TRANS_VALID=$(python3 "$STORE" update-status "$RUN_TEST_ID" running 2>&1) || true
if echo "$TRANS_VALID" | grep -q '"success": true'; then
    pass "Valid transition (registered->running) accepted"
else
    fail "Valid transition was rejected: $(echo "$TRANS_VALID" | head -3)"
fi

# ── Test 39: Get with path traversal attempt returns error ──
TESTS=$((TESTS + 1))
TRAV_GET=$(python3 "$STORE" get "../../etc/passwd" 2>&1) || true
if echo "$TRAV_GET" | grep -q "error"; then
    pass "Get with path traversal returns error"
else
    fail "Get with path traversal did not return error: $(echo "$TRAV_GET" | head -3)"
fi

# ── Test 40: Listing order is deterministic ──
TESTS=$((TESTS + 1))
LIST_A=$(python3 "$STORE" list --limit 100 2>&1) || true
LIST_B=$(python3 "$STORE" list --limit 100 2>&1) || true
if [ "$LIST_A" = "$LIST_B" ]; then
    pass "Listing order is deterministic (identical outputs)"
else
    fail "Listing order is not deterministic (outputs differ)"
fi

# ── Test 41: Valid status transition running -> completed accepted ──
TESTS=$((TESTS + 1))
COMP_TEST_ID="qabr-audit-harden-trans-to-complete"
echo "{\"fixture_type\":\"test\",\"description\":\"valid complete transition\",\"audit_receipt\":{\"audit_id\":\"$COMP_TEST_ID\",\"receipt_type\":\"broker_audit\",\"active_project_id\":\"qa-pilot\",\"target_project_id\":\"qa-pilot\",\"requested_tool\":\"qa_pilot_receipt_register\",\"custody_record_id\":\"cc-trans-comp\",\"handler_path\":\"active/qa-pilot/scripts/qa_pilot_mcp_handlers.py\",\"authority_level\":\"R1\",\"advisory_only\":true,\"output_effects\":[\"advisory_registration\"],\"audit_timestamp\":\"2026-07-02T23:00:00+00:00\",\"rollback_reference\":\"docs/governance/QA-PILOT-BROKER-IMPLEMENTATION.md\",\"validation_result\":\"pass\"}}" > /tmp/qa_pilot_trans_comp.json
python3 "$STORE" register /tmp/qa_pilot_trans_comp.json > /dev/null 2>&1 || true
python3 "$STORE" update-status "$COMP_TEST_ID" running > /dev/null 2>&1 || true
TRANS_COMP=$(python3 "$STORE" update-status "$COMP_TEST_ID" completed 2>&1) || true
if echo "$TRANS_COMP" | grep -q '"success": true'; then
    pass "Valid transition (running->completed) accepted"
else
    fail "Valid transition was rejected: $(echo "$TRANS_COMP" | head -3)"
fi

# ── Test 42: Valid status transition running -> failed accepted ──
TESTS=$((TESTS + 1))
FAIL_OK_ID="qabr-audit-harden-trans-to-fail"
echo "{\"fixture_type\":\"test\",\"description\":\"valid fail transition\",\"audit_receipt\":{\"audit_id\":\"$FAIL_OK_ID\",\"receipt_type\":\"broker_audit\",\"active_project_id\":\"qa-pilot\",\"target_project_id\":\"qa-pilot\",\"requested_tool\":\"qa_pilot_receipt_register\",\"custody_record_id\":\"cc-trans-fail-ok\",\"handler_path\":\"active/qa-pilot/scripts/qa_pilot_mcp_handlers.py\",\"authority_level\":\"R1\",\"advisory_only\":true,\"output_effects\":[\"advisory_registration\"],\"audit_timestamp\":\"2026-07-02T23:00:00+00:00\",\"rollback_reference\":\"docs/governance/QA-PILOT-BROKER-IMPLEMENTATION.md\",\"validation_result\":\"pass\"}}" > /tmp/qa_pilot_trans_fail_ok.json
python3 "$STORE" register /tmp/qa_pilot_trans_fail_ok.json > /dev/null 2>&1 || true
python3 "$STORE" update-status "$FAIL_OK_ID" running > /dev/null 2>&1 || true
TRANS_FAIL_OK=$(python3 "$STORE" update-status "$FAIL_OK_ID" failed 2>&1) || true
if echo "$TRANS_FAIL_OK" | grep -q '"success": true'; then
    pass "Valid transition (running->failed) accepted"
else
    fail "Valid transition was rejected: $(echo "$TRANS_FAIL_OK" | head -3)"
fi

# ── Test 43: Status update with invalid status value rejected ──
TESTS=$((TESTS + 1))
BAD_STATUS=$(python3 "$STORE" update-status "$RUN_TEST_ID" nonexistent_status 2>&1) || true
if echo "$BAD_STATUS" | grep -q '"success": false'; then
    pass "Status update with invalid status rejected"
else
    fail "Invalid status not rejected: $(echo "$BAD_STATUS" | head -3)"
fi

# ── Test 44: Prohibited-zone scan ──
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
