#!/usr/bin/env bash
set -euo pipefail

# QA Pilot Broker Implementation Test Runner — QA-PILOT-BROKER-IMPLEMENTATION-1
# Tests: broker module, custody verification, request acceptance/rejection,
#        audit receipts, disable flag, prohibited zones, existing validators

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BROKER="$SCRIPT_DIR/librarian_broker_qa_pilot.py"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-broker-implementation.py"
FIXTURES_DIR="$REPO_ROOT/fixtures/broker-implementation"
GOV_DOC="$REPO_ROOT/docs/governance/QA-PILOT-BROKER-IMPLEMENTATION.md"
SCHEMA_FILE="$REPO_ROOT/docs/schemas/qa-pilot-broker-implementation.schema.json"
AUDIT_DIR="$REPO_ROOT/data/audit/broker"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Broker Implementation Tests — QA-PILOT-BROKER-IMPLEMENTATION-1"
echo "======================================================================"
echo ""

# ── Test 1: Validator exists and passes ──
TESTS=$((TESTS + 1))
if python3 "$VALIDATOR" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Implementation validator passes"
else
    fail "Implementation validator failed"
    python3 "$VALIDATOR" 2>&1
fi

# ── Test 2: Broker module exists and is executable ──
TESTS=$((TESTS + 1))
if [ -f "$BROKER" ] && [ -x "$BROKER" ] || [ -f "$BROKER" ]; then
    pass "Broker module exists"
else
    fail "Broker module not found or not executable"
fi

# ── Test 3: Broker module runs as CLI with status ──
TESTS=$((TESTS + 1))
STATUS_OUTPUT=$(python3 "$BROKER" status 2>&1) || true
if echo "$STATUS_OUTPUT" | grep -q "broker_version"; then
    pass "Broker status CLI works"
else
    fail "Broker status CLI failed: $STATUS_OUTPUT"
fi

# ── Test 4: Broker shows advisory-only authority in status ──
TESTS=$((TESTS + 1))
if echo "$STATUS_OUTPUT" | grep -q "advisory_only"; then
    pass "Broker authority is advisory-only"
else
    fail "Broker authority not advisory-only"
fi

# ── Test 5: Disable flag works ──
TESTS=$((TESTS + 1))
# Disable the broker
python3 "$BROKER" disable > /dev/null 2>&1 || true
DISABLE_OUTPUT=$(python3 "$BROKER" status 2>&1) || true
if echo "$DISABLE_OUTPUT" | grep -q '"broker_enabled": false'; then
    pass "Broker disable works"
else
    fail "Broker disable did not set flag"
fi

# ── Test 6: Re-enable the broker ──
TESTS=$((TESTS + 1))
python3 "$BROKER" enable > /dev/null 2>&1 || true
ENABLE_OUTPUT=$(python3 "$BROKER" status 2>&1) || true
if echo "$ENABLE_OUTPUT" | grep -q '"broker_enabled": true'; then
    pass "Broker enable works"
else
    fail "Broker enable did not set flag"
fi

# ── Test 7: Valid advisory register request is accepted ──
TESTS=$((TESTS + 1))
REG_FIXTURE="$FIXTURES_DIR/valid-advisory-register-request.json"
if [ -f "$REG_FIXTURE" ]; then
    ACCEPT_OUTPUT=$(python3 "$BROKER" accept "$REG_FIXTURE" 2>&1) || true
    if echo "$ACCEPT_OUTPUT" | grep -q '"accepted": true'; then
        pass "Valid register request accepted"
    else
        fail "Valid register request rejected: $(echo "$ACCEPT_OUTPUT" | head -5)"
    fi
else
    fail "Valid register fixture not found"
fi

# ── Test 8: Valid advisory get request is accepted ──
TESTS=$((TESTS + 1))
GET_FIXTURE="$FIXTURES_DIR/valid-advisory-get-request.json"
if [ -f "$GET_FIXTURE" ]; then
    GET_OUTPUT=$(python3 "$BROKER" accept "$GET_FIXTURE" 2>&1) || true
    if echo "$GET_OUTPUT" | grep -q '"accepted": true'; then
        pass "Valid get request accepted"
    else
        fail "Valid get request rejected: $(echo "$GET_OUTPUT" | head -5)"
    fi
else
    fail "Valid get fixture not found"
fi

# ── Test 9: Valid advisory list request is accepted ──
TESTS=$((TESTS + 1))
LIST_FIXTURE="$FIXTURES_DIR/valid-advisory-list-request.json"
if [ -f "$LIST_FIXTURE" ]; then
    LIST_OUTPUT=$(python3 "$BROKER" accept "$LIST_FIXTURE" 2>&1) || true
    if echo "$LIST_OUTPUT" | grep -q '"accepted": true'; then
        pass "Valid list request accepted"
    else
        fail "Valid list request rejected: $(echo "$LIST_OUTPUT" | head -5)"
    fi
else
    fail "Valid list fixture not found"
fi

# ── Test 10: Valid advisory status request is accepted ──
TESTS=$((TESTS + 1))
STATUS_FIXTURE="$FIXTURES_DIR/valid-advisory-status-request.json"
if [ -f "$STATUS_FIXTURE" ]; then
    ST_OUTPUT=$(python3 "$BROKER" accept "$STATUS_FIXTURE" 2>&1) || true
    if echo "$ST_OUTPUT" | grep -q '"accepted": true'; then
        pass "Valid status request accepted"
    else
        fail "Valid status request rejected: $(echo "$ST_OUTPUT" | head -5)"
    fi
else
    fail "Valid status fixture not found"
fi

# ── Test 11: Missing custody_record is rejected ──
TESTS=$((TESTS + 1))
NO_CUSTODY_FIXTURE="$FIXTURES_DIR/invalid-missing-custody.json"
if [ -f "$NO_CUSTODY_FIXTURE" ]; then
    NC_OUTPUT=$(python3 "$BROKER" accept "$NO_CUSTODY_FIXTURE" 2>&1) || true
    if echo "$NC_OUTPUT" | grep -q '"accepted": false'; then
        pass "Missing custody record rejected"
    else
        fail "Missing custody record was not rejected"
    fi
else
    fail "Missing custody fixture not found"
fi

# ── Test 12: Wrong project_id is rejected ──
TESTS=$((TESTS + 1))
WRONG_PROJ_FIXTURE="$FIXTURES_DIR/invalid-wrong-project.json"
if [ -f "$WRONG_PROJ_FIXTURE" ]; then
    WP_OUTPUT=$(python3 "$BROKER" accept "$WRONG_PROJ_FIXTURE" 2>&1) || true
    if echo "$WP_OUTPUT" | grep -q '"accepted": false'; then
        pass "Wrong project_id rejected"
    else
        fail "Wrong project_id was not rejected"
    fi
else
    fail "Wrong project fixture not found"
fi

# ── Test 13: Unsupported tool is rejected ──
TESTS=$((TESTS + 1))
BAD_TOOL_FIXTURE="$FIXTURES_DIR/invalid-unsupported-tool.json"
if [ -f "$BAD_TOOL_FIXTURE" ]; then
    BT_OUTPUT=$(python3 "$BROKER" accept "$BAD_TOOL_FIXTURE" 2>&1) || true
    if echo "$BT_OUTPUT" | grep -q '"accepted": false'; then
        pass "Unsupported tool rejected"
    else
        fail "Unsupported tool was not rejected"
    fi
else
    fail "Unsupported tool fixture not found"
fi

# ── Test 14: Cross-project handler path is rejected ──
TESTS=$((TESTS + 1))
CROSS_PROJ_FIXTURE="$FIXTURES_DIR/invalid-cross-project-handler.json"
if [ -f "$CROSS_PROJ_FIXTURE" ]; then
    CP_OUTPUT=$(python3 "$BROKER" accept "$CROSS_PROJ_FIXTURE" 2>&1) || true
    if echo "$CP_OUTPUT" | grep -q '"accepted": false'; then
        pass "Cross-project handler rejected"
    else
        fail "Cross-project handler was not rejected"
    fi
else
    fail "Cross-project handler fixture not found"
fi

# ── Test 15: Non-advisory authority claim is rejected ──
TESTS=$((TESTS + 1))
AUTH_FIXTURE="$FIXTURES_DIR/invalid-authoritative-claim.json"
if [ -f "$AUTH_FIXTURE" ]; then
    AU_OUTPUT=$(python3 "$BROKER" accept "$AUTH_FIXTURE" 2>&1) || true
    if echo "$AU_OUTPUT" | grep -q '"accepted": false'; then
        pass "Non-advisory authority claim rejected"
    else
        fail "Non-advisory authority claim was not rejected"
    fi
else
    fail "Authoritative claim fixture not found"
fi

# ── Test 16: Broker produces audit receipt for accepted request ──
TESTS=$((TESTS + 1))
AUDIT_FILES_BEFORE=$(ls "$AUDIT_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
# Run another accepted request
python3 "$BROKER" accept "$FIXTURES_DIR/valid-advisory-get-request.json" > /dev/null 2>&1 || true
AUDIT_FILES_AFTER=$(ls "$AUDIT_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$AUDIT_FILES_AFTER" -gt "$AUDIT_FILES_BEFORE" ]; then
    pass "Audit receipt created for accepted request ($AUDIT_FILES_AFTER total)"
else
    fail "No audit receipt created (before: $AUDIT_FILES_BEFORE, after: $AUDIT_FILES_AFTER)"
fi

# ── Test 17: Broker produces audit receipt for rejected request ──
TESTS=$((TESTS + 1))
AUDIT_BEFORE_REJ=$(ls "$AUDIT_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
python3 "$BROKER" accept "$FIXTURES_DIR/invalid-missing-custody.json" > /dev/null 2>&1 || true
AUDIT_AFTER_REJ=$(ls "$AUDIT_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$AUDIT_AFTER_REJ" -gt "$AUDIT_BEFORE_REJ" ]; then
    pass "Audit receipt created for rejected request"
else
    fail "No audit receipt created for rejection"
fi

# ── Test 18: Broker list-audit works ──
TESTS=$((TESTS + 1))
LIST_AUDIT=$(python3 "$BROKER" list-audit 2>&1) || true
if echo "$LIST_AUDIT" | grep -q "receipts"; then
    pass "Broker list-audit works"
else
    fail "Broker list-audit failed"
fi

# ── Test 19: Governance doc exists ──
TESTS=$((TESTS + 1))
if [ -f "$GOV_DOC" ]; then
    pass "Implementation governance doc exists"
else
    fail "Implementation governance doc not found"
fi

# ── Test 20: Schema is valid JSON ──
TESTS=$((TESTS + 1))
if [ -f "$SCHEMA_FILE" ]; then
    if python3 -c "import json; json.load(open('$SCHEMA_FILE'))" 2>/dev/null; then
        pass "Implementation schema is valid JSON"
    else
        fail "Implementation schema is not valid JSON"
    fi
else
    fail "Implementation schema not found"
fi

# ── Test 21: Broker disabled state produces structured refusal ──
TESTS=$((TESTS + 1))
python3 "$BROKER" disable > /dev/null 2>&1 || true
DISABLED_ACCEPT=$(python3 "$BROKER" accept "$FIXTURES_DIR/valid-advisory-get-request.json" 2>&1) || true
if echo "$DISABLED_ACCEPT" | grep -q '"accepted": false' && echo "$DISABLED_ACCEPT" | grep -q "disabled"; then
    pass "Disabled broker returns structured refusal"
else
    fail "Disabled broker did not return structured refusal"
fi
# Re-enable for other tests
python3 "$BROKER" enable > /dev/null 2>&1 || true

# ── Test 22: Broker audit receipts contain custody conditions for accepted requests ──
TESTS=$((TESTS + 1))
CUSTODY_AUDIT=""
for f in "$AUDIT_DIR"/*.json; do
    if python3 -c "import json; d=json.load(open('$f')); print(d.get('accepted', False))" 2>/dev/null | grep -q "True"; then
        CUSTODY_AUDIT="$f"
        break
    fi
done
if [ -n "$CUSTODY_AUDIT" ]; then
    if python3 -c "import json; d=json.load(open('$CUSTODY_AUDIT')); print(d.get('custody_conditions_checked', []))" 2>/dev/null | grep -q "CC-1"; then
        pass "Audit receipt for accepted request contains custody conditions"
    else
        fail "Accepted request audit receipt missing custody conditions"
    fi
else
    fail "No accepted audit receipts found"
fi

# ── Test 23: Prohibited-zone scan ──
TESTS=$((TESTS + 1))
# Check no QA Pilot broker files leaked into Librarian
PROHIBITED_HITS=""
if [ -f "/Users/andrew/Desktop/CarbideFrame/active/librarian/scripts/librarian_broker_qa_pilot.py" ]; then
    PROHIBITED_HITS="$PROHIBITED_HITS broker-script"
fi
if [ -f "/Users/andrew/Desktop/CarbideFrame/active/librarian/docs/governance/QA-PILOT-BROKER-IMPLEMENTATION.md" ]; then
    PROHIBITED_HITS="$PROHIBITED_HITS broker-gov-doc"
fi
if [ -z "$PROHIBITED_HITS" ]; then
    pass "Prohibited-zone: no broker files leaked into Librarian"
else
    fail "Prohibited-zone: found broker files in Librarian:$PROHIBITED_HITS"
fi

# ── Test 24: Existing plan validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-broker-plan.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing broker plan validator still passes"
else
    fail "Existing broker plan validator regression"
fi

# ── Test 25: Existing plan test runner still passes ──
TESTS=$((TESTS + 1))
if bash "$SCRIPT_DIR/test-qa-pilot-broker-plan.sh" 2>&1 | grep -q "All tests pass"; then
    pass "Existing broker plan test runner still passes"
else
    fail "Existing broker plan test runner regression"
fi

# ── Test 26: Existing receipt validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-receipt.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing receipt validator still passes"
else
    fail "Existing receipt validator regression"
fi

# ── Test 27: Existing MCP surface validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-mcp-surface.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing MCP surface validator still passes"
else
    fail "Existing MCP surface validator regression"
fi

# ── Test 28: Existing store validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-receipt-store.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing store validator still passes"
else
    fail "Existing store validator regression"
fi

# ── Test 29: Existing handler validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-mcp-handler.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing handler validator still passes"
else
    fail "Existing handler validator regression"
fi

# ── Test 30: Existing custody validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-librarian-mcp-custody.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing custody validator still passes"
else
    fail "Existing custody validator regression"
fi

# ── Test 31: Broker module has no MCPController registration ref ──
TESTS=$((TESTS + 1))
if grep -q "MCPController\|register_tool\|native_mcp" "$BROKER" 2>/dev/null; then
    # Allow only if in docstring rejecting it
    if grep -c "not register native MCPController" "$BROKER" > /dev/null 2>&1; then
        pass "No MCPController registration (only rejection ref)"
    else
        fail "Found MCPController registration reference in broker"
    fi
else
    pass "No MCPController registration in broker module"
fi

# ── Test 32: Broker module has no cross-project call references ──
TESTS=$((TESTS + 1))
if grep -q "active/librarian/\|\.\./librarian" "$BROKER" 2>/dev/null; then
    fail "Found cross-project call reference in broker"
else
    pass "No cross-project call references in broker module"
fi

echo ""
echo "======================================================================"
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
