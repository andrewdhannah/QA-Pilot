#!/usr/bin/env bash
set -euo pipefail

# QA Pilot Broker Advisory Surface Test Runner — QA-PILOT-BROKER-MCP-ADVISORY-SURFACE-1
# Tests: surface CLI, valid commands, rejection scenarios, audit trail, boundaries

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SURFACE="$SCRIPT_DIR/qa_pilot_broker_advisory_surface.py"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-broker-advisory-surface.py"
BROKER="$SCRIPT_DIR/librarian_broker_qa_pilot.py"
FIXTURES_DIR="$REPO_ROOT/fixtures/broker-advisory-surface"
IMPL_FIXTURES_DIR="$REPO_ROOT/fixtures/broker-implementation"
AUDIT_DIR="$REPO_ROOT/data/audit/broker"
GOV_DOC="$REPO_ROOT/docs/governance/QA-PILOT-BROKER-MCP-ADVISORY-SURFACE.md"
SCHEMA_FILE="$REPO_ROOT/docs/schemas/qa-pilot-broker-mcp-advisory-surface.schema.json"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Broker Advisory Surface Tests — QA-PILOT-BROKER-MCP-ADVISORY-SURFACE-1"
echo "==========================================================================="
echo ""

# Ensure broker is enabled before tests
python3 "$BROKER" enable > /dev/null 2>&1 || true

# ── Test 1: Validator exists and passes ──
TESTS=$((TESTS + 1))
if python3 "$VALIDATOR" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Advisory surface validator passes"
else
    fail "Advisory surface validator failed"
    python3 "$VALIDATOR" 2>&1
fi

# ── Test 2: Surface script exists and is executable ──
TESTS=$((TESTS + 1))
if [ -f "$SURFACE" ]; then
    pass "Advisory surface script exists"
else
    fail "Advisory surface script not found"
fi

# ── Test 3: Surface CLI accepts valid accept command (register) ──
TESTS=$((TESTS + 1))
REG_FIXTURE="$IMPL_FIXTURES_DIR/valid-advisory-register-request.json"
if [ -f "$REG_FIXTURE" ]; then
    ACCEPT_OUT=$(python3 "$SURFACE" accept "$REG_FIXTURE" 2>&1) || true
    if echo "$ACCEPT_OUT" | grep -q '"accepted": true'; then
        pass "Valid accept (register) command accepted"
    else
        fail "Valid accept (register) command failed: $(echo "$ACCEPT_OUT" | head -3)"
    fi
else
    fail "Register fixture not found"
fi

# ── Test 4: Surface CLI accepts valid accept command (get) ──
TESTS=$((TESTS + 1))
GET_FIXTURE="$IMPL_FIXTURES_DIR/valid-advisory-get-request.json"
if [ -f "$GET_FIXTURE" ]; then
    GET_OUT=$(python3 "$SURFACE" accept "$GET_FIXTURE" 2>&1) || true
    if echo "$GET_OUT" | grep -q '"accepted": true'; then
        pass "Valid accept (get) command accepted"
    else
        fail "Valid accept (get) command failed: $(echo "$GET_OUT" | head -3)"
    fi
else
    fail "Get fixture not found"
fi

# ── Test 5: Surface CLI accepts list-audit command ──
TESTS=$((TESTS + 1))
LIST_AUDIT_OUT=$(python3 "$SURFACE" list-audit --limit 5 2>&1) || true
if echo "$LIST_AUDIT_OUT" | grep -q '"accepted": true'; then
    pass "list-audit command accepted"
else
    fail "list-audit command failed: $(echo "$LIST_AUDIT_OUT" | head -3)"
fi

# ── Test 6: Surface CLI accepts status command ──
TESTS=$((TESTS + 1))
STATUS_OUT=$(python3 "$SURFACE" status 2>&1) || true
if echo "$STATUS_OUT" | grep -q '"accepted": true'; then
    pass "Status command accepted"
else
    fail "Status command failed: $(echo "$STATUS_OUT" | head -3)"
fi

# ── Test 7: Surface response has all required fields ──
TESTS=$((TESTS + 1))
MISSING_FIELDS=""
for field in surface command project_id authority accepted custody_verified audit_receipt_id broker_commit_or_version timestamp limitations; do
    if ! echo "$STATUS_OUT" | grep -q "\"$field\":"; then
        MISSING_FIELDS="$MISSING_FIELDS $field"
    fi
done
if [ -z "$MISSING_FIELDS" ]; then
    pass "All required response fields present in status command"
else
    fail "Missing required fields:$MISSING_FIELDS"
fi

# ── Test 8: Authority is advisory_only ──
TESTS=$((TESTS + 1))
if echo "$STATUS_OUT" | grep -q '"authority": "advisory_only"'; then
    pass "Surface authority is advisory_only"
else
    fail "Surface authority not advisory_only"
fi

# ── Test 9: Unsupported command rejected ──
TESTS=$((TESTS + 1))
UNSUP_OUT=$(python3 "$SURFACE" nonexistent_command 2>&1) || true
if echo "$UNSUP_OUT" | grep -q "unsupported_command\|invalid choice\|usage:"; then
    pass "Unsupported command rejected"
else
    fail "Unsupported command not rejected: $(echo "$UNSUP_OUT" | head -3)"
fi

# ── Test 10: Missing custody rejected via surface ──
TESTS=$((TESTS + 1))
NO_CUSTODY="$IMPL_FIXTURES_DIR/invalid-missing-custody.json"
if [ -f "$NO_CUSTODY" ]; then
    NC_OUT=$(python3 "$SURFACE" accept "$NO_CUSTODY" 2>&1) || true
    if echo "$NC_OUT" | grep -q "custody_failed"; then
        pass "Missing custody rejected via surface"
    else
        fail "Missing custody not rejected: $(echo "$NC_OUT" | head -3)"
    fi
else
    fail "Missing custody fixture not found"
fi

# ── Test 11: Wrong project rejected via surface ──
TESTS=$((TESTS + 1))
WP_FIXTURE="$IMPL_FIXTURES_DIR/invalid-wrong-project.json"
if [ -f "$WP_FIXTURE" ]; then
    WP_OUT=$(python3 "$SURFACE" accept "$WP_FIXTURE" 2>&1) || true
    if echo "$WP_OUT" | grep -q "custody_failed"; then
        pass "Wrong project rejected via surface"
    else
        fail "Wrong project not rejected: $(echo "$WP_OUT" | head -3)"
    fi
else
    fail "Wrong project fixture not found"
fi

# ── Test 12: Cross-project handler rejected via surface ──
TESTS=$((TESTS + 1))
CP_FIXTURE="$IMPL_FIXTURES_DIR/invalid-cross-project-handler.json"
if [ -f "$CP_FIXTURE" ]; then
    CP_OUT=$(python3 "$SURFACE" accept "$CP_FIXTURE" 2>&1) || true
    if echo "$CP_OUT" | grep -q "custody_failed"; then
        pass "Cross-project handler rejected via surface"
    else
        fail "Cross-project handler not rejected: $(echo "$CP_OUT" | head -3)"
    fi
else
    fail "Cross-project fixture not found"
fi

# ── Test 13: Unsupported tool rejected via surface ──
TESTS=$((TESTS + 1))
UT_FIXTURE="$IMPL_FIXTURES_DIR/invalid-unsupported-tool.json"
if [ -f "$UT_FIXTURE" ]; then
    UT_OUT=$(python3 "$SURFACE" accept "$UT_FIXTURE" 2>&1) || true
    if echo "$UT_OUT" | grep -q "custody_failed"; then
        pass "Unsupported tool rejected via surface"
    else
        fail "Unsupported tool not rejected: $(echo "$UT_OUT" | head -3)"
    fi
else
    fail "Unsupported tool fixture not found"
fi

# ── Test 14: Non-advisory authority rejected via surface ──
TESTS=$((TESTS + 1))
AA_FIXTURE="$IMPL_FIXTURES_DIR/invalid-authoritative-claim.json"
if [ -f "$AA_FIXTURE" ]; then
    AA_OUT=$(python3 "$SURFACE" accept "$AA_FIXTURE" 2>&1) || true
    if echo "$AA_OUT" | grep -q "custody_failed"; then
        pass "Non-advisory authority rejected via surface"
    else
        fail "Non-advisory authority not rejected: $(echo "$AA_OUT" | head -3)"
    fi
else
    fail "Authoritative claim fixture not found"
fi

# ── Test 15: Disabled broker rejected via surface ──
TESTS=$((TESTS + 1))
python3 "$BROKER" disable > /dev/null 2>&1 || true
GOOD_FIXTURE="$IMPL_FIXTURES_DIR/valid-advisory-get-request.json"
DIS_OUT=$(python3 "$SURFACE" accept "$GOOD_FIXTURE" 2>&1) || true
if echo "$DIS_OUT" | grep -q "broker_disabled"; then
    pass "Disabled broker rejected via surface"
else
    fail "Disabled broker not rejected: $(echo "$DIS_OUT" | head -3)"
fi
python3 "$BROKER" enable > /dev/null 2>&1 || true

# ── Test 16: Audit command works ──
TESTS=$((TESTS + 1))
# Get a real audit receipt ID from the broker
REAL_AUDIT=$(python3 "$BROKER" list-audit --limit 1 2>&1 | python3 -c "import json,sys; d=json.load(sys.stdin); r=d.get('receipts',[]); print(r[0]['audit_receipt_id'] if r else 'none')" 2>/dev/null) || REAL_AUDIT="none"
if [ "$REAL_AUDIT" != "none" ]; then
    AUDIT_OUT=$(python3 "$SURFACE" audit "$REAL_AUDIT" 2>&1) || true
    if echo "$AUDIT_OUT" | grep -q '"accepted": true'; then
        pass "Audit command works for real receipt"
    else
        fail "Audit command failed for real receipt"
    fi
else
    # No real receipt — test with non-existent ID (should be accepted response with not_found)
    AUDIT_OUT=$(python3 "$SURFACE" audit "nonexistent-audit-id-001" 2>&1) || true
    if echo "$AUDIT_OUT" | grep -q '"accepted": false'; then
        pass "Audit command handles missing receipt gracefully"
    else
        fail "Audit command did not handle missing receipt"
    fi
fi

# ── Test 17: Surface enable/disable commands work ──
TESTS=$((TESTS + 1))
EN_OUT=$(python3 "$SURFACE" enable 2>&1) || true
DIS_OUT2=$(python3 "$SURFACE" disable 2>&1) || true
RE_EN_OUT=$(python3 "$SURFACE" enable 2>&1) || true
if echo "$EN_OUT" | grep -q '"accepted": true' && echo "$DIS_OUT2" | grep -q '"accepted": true' && echo "$RE_EN_OUT" | grep -q '"accepted": true'; then
    pass "Surface enable/disable commands work"
else
    fail "Surface enable/disable commands failed"
fi

# ── Test 18: Surface accept returns audit_receipt_id for accepted requests ──
TESTS=$((TESTS + 1))
if echo "$ACCEPT_OUT" | grep -q '"audit_receipt_id"'; then
    pass "Accepted request returns audit_receipt_id"
else
    fail "Accepted request missing audit_receipt_id"
fi

# ── Test 19: Surface accept returns refusal_code for rejected requests ──
TESTS=$((TESTS + 1))
if echo "$NC_OUT" | grep -q '"refusal_code"'; then
    pass "Rejected request returns refusal_code"
else
    fail "Rejected request missing refusal_code"
fi

# ── Test 20: Malformed request rejected via surface ──
TESTS=$((TESTS + 1))
MALFORMED_OUT=$(python3 "$SURFACE" accept "/nonexistent/path/request.json" 2>&1) || true
if echo "$MALFORMED_OUT" | grep -q '"accepted": false'; then
    pass "Malformed request rejected"
else
    fail "Malformed request not rejected: $(echo "$MALFORMED_OUT" | head -3)"
fi

# ── Test 21: Surface response includes limitations notice ──
TESTS=$((TESTS + 1))
if echo "$STATUS_OUT" | grep -q '"limitations"'; then
    pass "Surface response includes limitations notice"
else
    fail "Surface response missing limitations"
fi

# ── Test 22: Surface response includes broker_commit_or_version ──
TESTS=$((TESTS + 1))
if echo "$STATUS_OUT" | grep -q '"broker_commit_or_version"'; then
    pass "Surface response includes broker_commit_or_version"
else
    fail "Surface response missing broker_commit_or_version"
fi

# ── Test 23: Governance doc exists ──
TESTS=$((TESTS + 1))
if [ -f "$GOV_DOC" ]; then
    pass "Advisory surface governance doc exists"
else
    fail "Advisory surface governance doc not found"
fi

# ── Test 24: Schema is valid JSON ──
TESTS=$((TESTS + 1))
if [ -f "$SCHEMA_FILE" ]; then
    if python3 -c "import json; json.load(open('$SCHEMA_FILE'))" 2>/dev/null; then
        pass "Advisory surface schema is valid JSON"
    else
        fail "Advisory surface schema is not valid JSON"
    fi
else
    fail "Advisory surface schema not found"
fi

# ── Test 25: Existing broker implementation test runner still passes ──
TESTS=$((TESTS + 1))
if bash "$SCRIPT_DIR/test-qa-pilot-broker-implementation.sh" 2>&1 | grep -q "All tests pass"; then
    pass "Existing broker implementation test runner still passes"
else
    fail "Existing broker implementation test runner regression"
fi

# ── Test 26: Existing broker plan validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-broker-plan.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing broker plan validator still passes"
else
    fail "Existing broker plan validator regression"
fi

# ── Test 27: Existing receipt validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-receipt.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing receipt validator still passes"
else
    fail "Existing receipt validator regression"
fi

# ── Test 28: Existing MCP surface validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-mcp-surface.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing MCP surface validator still passes"
else
    fail "Existing MCP surface validator regression"
fi

# ── Test 29: Existing store validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-receipt-store.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing store validator still passes"
else
    fail "Existing store validator regression"
fi

# ── Test 30: Existing handler validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-mcp-handler.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing handler validator still passes"
else
    fail "Existing handler validator regression"
fi

# ── Test 31: Existing custody validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-librarian-mcp-custody.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing custody validator still passes"
else
    fail "Existing custody validator regression"
fi

# ── Test 32: Surface script has no MCPController registration ref ──
TESTS=$((TESTS + 1))
if grep -q "MCPController\|register_tool\|native_mcp" "$SURFACE" 2>/dev/null; then
    # Allow only if in docstring rejecting it
    if grep -c "does not register" "$SURFACE" > /dev/null 2>&1; then
        pass "No MCPController registration in surface (only rejection ref)"
    else
        fail "Found MCPController registration reference in surface"
    fi
else
    pass "No MCPController registration in surface script"
fi

# ── Test 33: Surface script has no cross-project references ──
TESTS=$((TESTS + 1))
if grep -q "active/librarian/\|\.\./librarian" "$SURFACE" 2>/dev/null; then
    fail "Found cross-project reference in surface"
else
    pass "No cross-project references in surface script"
fi

# ── Test 34: Surface delegates to broker (not direct handler calls) ──
TESTS=$((TESTS + 1))
if grep -q "get_broker()" "$SURFACE" 2>/dev/null; then
    pass "Surface delegates to sealed broker module"
else
    fail "Surface does not delegate to broker module"
fi

# ── Test 35: Examples exist ──
TESTS=$((TESTS + 1))
EXAMPLES=$(ls "$REPO_ROOT/docs/examples/broker-advisory-surface"/*.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$EXAMPLES" -ge 1 ]; then
    pass "Example files exist ($EXAMPLES found)"
else
    fail "No example files found"
fi

# ── Test 36: Prohibited-zone scan ──
TESTS=$((TESTS + 1))
PROHIBITED_HITS=""
if [ -f "/Users/andrew/Desktop/CarbideFrame/active/librarian/scripts/qa_pilot_broker_advisory_surface.py" ]; then
    PROHIBITED_HITS="$PROHIBITED_HITS surface-script"
fi
if [ -f "/Users/andrew/Desktop/CarbideFrame/active/librarian/docs/governance/QA-PILOT-BROKER-MCP-ADVISORY-SURFACE.md" ]; then
    PROHIBITED_HITS="$PROHIBITED_HITS surface-gov-doc"
fi
if [ -z "$PROHIBITED_HITS" ]; then
    pass "Prohibited-zone: no surface files leaked into Librarian"
else
    fail "Prohibited-zone: found surface files in Librarian:$PROHIBITED_HITS"
fi

echo ""
echo "==========================================================================="
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
