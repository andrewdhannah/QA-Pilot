#!/bin/bash
#
# QA Pilot Work Proposal Test Runner — QA-PILOT-LIBRARIAN-WORK-QUEUE-INTEGRATION-1
#
# Tests:
#   1. Compiler produces valid proposal from diagnostic report
#   2. Validator passes on valid fixtures
#   3. Validator rejects invalid fixtures
#   4. Compiler rejects invalid diagnostic reports
#   5. Forbidden fields are not in schema
#   6. Compiler does not call Librarian MCP tools
#   7. Tier 2 gates are documented as blocked
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
COMPILER="$SCRIPT_DIR/qa_pilot_work_proposal_compiler.py"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-work-proposal.py"
FIXTURES_DIR="$REPO_ROOT/fixtures/work-proposal"
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

PASS=0
FAIL=0

pass() {
    echo "  PASS: $1"
    PASS=$((PASS + 1))
}

fail() {
    echo "  FAIL: $1"
    FAIL=$((FAIL + 1))
}

echo "=== QA Pilot Work Proposal Test Runner ==="
echo ""

# Test 1: Compiler produces valid proposal from a valid diagnostic report
echo "Test 1: Compiler produces valid proposal from diagnostic report..."
if [ -f "$FIXTURES_DIR/valid-diagnostic-regression.json" ]; then
    PROPOSAL_OUTPUT="$TEMP_DIR/test-proposal.json"
    if python3 "$COMPILER" compile "$FIXTURES_DIR/valid-diagnostic-regression.json" --output "$PROPOSAL_OUTPUT" 2>/dev/null; then
        if python3 "$COMPILER" validate "$PROPOSAL_OUTPUT" 2>/dev/null; then
            pass "Compiler produced valid proposal from regression diagnostic"
        else
            fail "Compiler produced invalid proposal (validation failed)"
        fi
    else
        fail "Compiler failed to produce proposal"
    fi
else
    fail "Missing fixture: valid-diagnostic-regression.json"
fi

# Test 2: Compiler produces valid proposal from security diagnostic
echo "Test 2: Compiler produces valid proposal from security diagnostic..."
if [ -f "$FIXTURES_DIR/valid-diagnostic-security.json" ]; then
    PROPOSAL_OUTPUT2="$TEMP_DIR/test-proposal-sec.json"
    if python3 "$COMPILER" compile "$FIXTURES_DIR/valid-diagnostic-security.json" --output "$PROPOSAL_OUTPUT2" 2>/dev/null; then
        if python3 "$COMPILER" validate "$PROPOSAL_OUTPUT2" 2>/dev/null; then
            pass "Compiler produced valid proposal from security diagnostic"
        else
            fail "Compiler produced invalid security proposal"
        fi
    else
        fail "Compiler failed to produce security proposal"
    fi
else
    fail "Missing fixture: valid-diagnostic-security.json"
fi

# Test 3: Compiler rejects invalid diagnostic report
echo "Test 3: Compiler rejects invalid diagnostic report..."
if [ -f "$FIXTURES_DIR/invalid-diagnostic-missing-report-id.json" ]; then
    if python3 "$COMPILER" compile "$FIXTURES_DIR/invalid-diagnostic-missing-report-id.json" --output "$TEMP_DIR/bad.json" 2>/dev/null; then
        fail "Compiler accepted invalid diagnostic (missing report_id)"
    else
        pass "Compiler rejected invalid diagnostic (missing report_id)"
    fi
else
    fail "Missing fixture: invalid-diagnostic-missing-report-id.json"
fi

# Test 4: Compiler rejects diagnostic with advisory=false
echo "Test 4: Compiler rejects diagnostic with advisory=false..."
if [ -f "$FIXTURES_DIR/invalid-diagnostic-advisory-false.json" ]; then
    if python3 "$COMPILER" compile "$FIXTURES_DIR/invalid-diagnostic-advisory-false.json" --output "$TEMP_DIR/bad2.json" 2>/dev/null; then
        fail "Compiler accepted diagnostic with advisory=false"
    else
        pass "Compiler rejected diagnostic with advisory=false"
    fi
else
    fail "Missing fixture: invalid-diagnostic-advisory-false.json"
fi

# Test 5: Validator passes on valid fixtures
echo "Test 5: Validator passes on valid fixtures..."
for fixture in valid-regression-proposal.json valid-security-proposal.json; do
    if [ -f "$FIXTURES_DIR/$fixture" ]; then
        if python3 "$COMPILER" validate "$FIXTURES_DIR/$fixture" 2>/dev/null; then
            pass "Validator accepted valid fixture: $fixture"
        else
            fail "Validator rejected valid fixture: $fixture"
        fi
    else
        fail "Missing fixture: $fixture"
    fi
done

# Test 6: Validator rejects invalid fixtures
echo "Test 6: Validator rejects invalid fixtures..."
for fixture in \
    invalid-missing-proposal-id.json \
    invalid-missing-diagnostic-id.json \
    invalid-empty-verification.json \
    invalid-owner-approval-field.json \
    invalid-execution-permission-field.json \
    invalid-advisory-false.json \
    invalid-no-provenance.json; do
    if [ -f "$FIXTURES_DIR/$fixture" ]; then
        if python3 "$COMPILER" validate "$FIXTURES_DIR/$fixture" 2>/dev/null; then
            fail "Validator accepted invalid fixture: $fixture"
        else
            pass "Validator rejected invalid fixture: $fixture"
        fi
    else
        fail "Missing fixture: $fixture"
    fi
done

# Test 7: Schema does not contain forbidden fields
echo "Test 7: Schema does not contain forbidden fields..."
SCHEMA="$REPO_ROOT/docs/schemas/qa-work-proposal.schema.json"
if [ -f "$SCHEMA" ]; then
    if python3 -c "
import json
schema = json.load(open('$SCHEMA'))
props = schema.get('properties', {})
forbidden = ['owner_approval', 'execution_permission', 'mutation_authority']
for f in forbidden:
    if f in props:
        print(f'FORBIDDEN: {f}')
        exit(1)
exit(0)
" 2>/dev/null; then
        pass "Schema does not contain forbidden fields"
    else
        fail "Schema contains forbidden fields"
    fi
else
    fail "Schema file not found"
fi

# Test 8: Compiler does not call Librarian MCP tools
echo "Test 8: Compiler does not call Librarian MCP tools..."
if grep -qE "project_work_packet_draft|project_work_packet_authorize|project_work_packet_dispatch|project_work_result_intake|project_work_result_verify" "$COMPILER" 2>/dev/null; then
    fail "Compiler contains Librarian MCP tool calls"
else
    pass "Compiler does not call Librarian MCP tools"
fi

# Test 9: Full validator passes
echo "Test 9: Full validator passes..."
if python3 "$VALIDATOR" 2>/dev/null; then
    pass "Full validator passed"
else
    fail "Full validator failed"
fi

# Test 10: Compiler status command works
echo "Test 10: Compiler status command works..."
if python3 "$COMPILER" status 2>/dev/null | grep -q "QA Pilot Work Proposal Compiler"; then
    pass "Compiler status command works"
else
    fail "Compiler status command failed"
fi

# Test 11: Determinism — same input produces same output
echo "Test 11: Compiler is deterministic..."
if [ -f "$FIXTURES_DIR/valid-diagnostic-regression.json" ]; then
    OUT1="$TEMP_DIR/det1.json"
    OUT2="$TEMP_DIR/det2.json"
    python3 "$COMPILER" compile "$FIXTURES_DIR/valid-diagnostic-regression.json" --output "$OUT1" 2>/dev/null
    python3 "$COMPILER" compile "$FIXTURES_DIR/valid-diagnostic-regression.json" --output "$OUT2" 2>/dev/null
    # Compare excluding compiled_at (timestamp)
    python3 -c "
import json
p1 = json.load(open('$OUT1'))
p2 = json.load(open('$OUT2'))
p1['provenance'].pop('compiled_at', None)
p2['provenance'].pop('compiled_at', None)
if p1 == p2:
    exit(0)
else:
    exit(1)
" 2>/dev/null
    if [ $? -eq 0 ]; then
        pass "Compiler is deterministic (same input → same output)"
    else
        fail "Compiler is not deterministic"
    fi
else
    fail "Missing fixture for determinism test"
fi

# Test 12: WQI-008 — Fail-closed invariant (regression gate)
echo "Test 12: WQI-008 fail-closed invariant..."
SPEC="$REPO_ROOT/docs/governance/QA-PILOT-LIBRARIAN-CONSUMPTION-SPECIFICATION.md"
SPRINT_DOC="$REPO_ROOT/docs/sprints/QA-PILOT-LIBRARIAN-WORK-QUEUE-INTEGRATION-1.md"

WQI008_PASS=true

# Check consumption spec documents the diagnostic trail
if ! grep -q "work_packet_service_available" "$SPEC" 2>/dev/null; then
    fail "WQI-008: Consumption spec does not document work_packet_service_available"
    WQI008_PASS=false
fi
if ! grep -q "degraded" "$SPEC" 2>/dev/null; then
    fail "WQI-008: Consumption spec does not document bridge_status: degraded"
    WQI008_PASS=false
fi

# Check sprint doc documents fail-closed behavior
if ! grep -qi "fail-closed\|failed closed\|fail closed" "$SPRINT_DOC" 2>/dev/null; then
    fail "WQI-008: Sprint doc does not document fail-closed behavior"
    WQI008_PASS=false
fi

# Check compiler has no silent fallback
if grep -qE "fallback_to_work_packet|create_work_packet_if_service_unavailable|bypass_service_check|silent_downgrade" "$COMPILER" 2>/dev/null; then
    fail "WQI-008: Compiler contains forbidden silent fallback"
    WQI008_PASS=false
fi

if [ "$WQI008_PASS" = true ]; then
    pass "WQI-008: Fail-closed invariant verified (diagnostic trail documented, no silent downgrade)"
fi

echo ""
echo "=== Results ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "ALL TESTS PASSED"
    exit 0
else
    echo "TESTS FAILED"
    exit 1
fi
