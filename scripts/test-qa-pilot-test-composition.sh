#!/usr/bin/env bash
set -euo pipefail

# QA Pilot Test Composition Test Runner — QA-PILOT-TEST-COMPOSITION-1
# Tests: composition script, validator, fixtures, store operations, TC rules,
#        boundary enforcement, regression across #23-#33

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSITION_SCRIPT="$SCRIPT_DIR/qa_pilot_test_composition.py"
COMPOSITION_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-test-composition.py"
INTAKE_SCRIPT="$SCRIPT_DIR/qa_pilot_mcp_evidence_intake.py"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-test-composition"
EVIDENCE_DIR="$REPO_ROOT/data/evidence"
TEST_CASES_DIR="$REPO_ROOT/data/test-cases"
PASS=0
FAIL=0
TESTS=0

cleanup() {
    python3 "$COMPOSITION_SCRIPT" clear >/dev/null 2>&1 || true
    python3 "$INTAKE_SCRIPT" clear >/dev/null 2>&1 || true
}

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Test Composition Tests — QA-PILOT-TEST-COMPOSITION-1"
echo "=============================================================="
echo ""

cleanup

# ── Test 1: Composition script exists ──
TESTS=$((TESTS + 1))
if [ -f "$COMPOSITION_SCRIPT" ]; then
    pass "Composition script found"
else
    fail "Composition script not found at $COMPOSITION_SCRIPT"
fi

# ── Test 2: Validator passes ──
TESTS=$((TESTS + 1))
VALIDATOR_OUTPUT=$(python3 "$COMPOSITION_VALIDATOR" 2>&1) || true
if echo "$VALIDATOR_OUTPUT" | grep -q "ALL CHECKS PASS"; then
    pass "Validator ALL CHECKS PASS"
else
    fail "Validator failed"
    echo "       $(echo "$VALIDATOR_OUTPUT" | tail -5)"
fi

# ── Test 3: Ingest evidence for composition tests ──
TESTS=$((TESTS + 1))
VALID_FIXTURE="$FIXTURES_DIR/valid-evidence-source.json"
INGEST_OUTPUT=$(python3 "$INTAKE_SCRIPT" ingest "$VALID_FIXTURE" 2>&1) || true
INGEST_SUCCESS=$(echo "$INGEST_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "false")
if [ "$INGEST_SUCCESS" = "True" ]; then
    pass "Evidence ingested for composition"
else
    fail "Failed to ingest evidence"
    echo "       $INGEST_OUTPUT"
fi

# ── Test 4: Compose test cases from evidence ──
TESTS=$((TESTS + 1))
COMPOSE_OUTPUT=$(python3 "$COMPOSITION_SCRIPT" compose 2>&1) || true
COMPOSE_SUCCESS=$(echo "$COMPOSE_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "false")
COMPOSE_COUNT=$(echo "$COMPOSE_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_test_cases_composed', 0))" 2>/dev/null || echo "0")
if [ "$COMPOSE_SUCCESS" = "True" ] && [ "$COMPOSE_COUNT" -ge 1 ]; then
    pass "Compose produced $COMPOSE_COUNT test case(s)"
else
    fail "Compose failed or produced 0 cases"
    echo "       $COMPOSE_OUTPUT"
fi

FIRST_TEST_ID=$(echo "$COMPOSE_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); ids=d.get('test_ids',[]); print(ids[0] if ids else '')" 2>/dev/null || echo "")

# ── Test 5: Composed tests have advisory_only=true in response ──
TESTS=$((TESTS + 1))
ADVISORY=$(echo "$COMPOSE_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('advisory_only', False))" 2>/dev/null || echo "false")
if [ "$ADVISORY" = "True" ]; then
    pass "Compose response includes advisory_only=true"
else
    fail "Compose response missing advisory_only"
fi

# ── Test 6: List composed tests ──
TESTS=$((TESTS + 1))
LIST_OUTPUT=$(python3 "$COMPOSITION_SCRIPT" list --limit 50 2>&1) || true
LIST_COUNT=$(echo "$LIST_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('test_cases',[])))" 2>/dev/null || echo "0")
if [ "$LIST_COUNT" -ge 1 ]; then
    pass "List returns $LIST_COUNT test case(s)"
else
    fail "List returned 0 test cases"
    echo "       $LIST_OUTPUT"
fi

# ── Test 7: Read composed test case ──
TESTS=$((TESTS + 1))
if [ -n "$FIRST_TEST_ID" ]; then
    READ_OUTPUT=$(python3 "$COMPOSITION_SCRIPT" read "$FIRST_TEST_ID" 2>&1) || true
    READ_FOUND=$(echo "$READ_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('found', False))" 2>/dev/null || echo "false")
    if [ "$READ_FOUND" = "True" ]; then
        pass "Read found test case '$FIRST_TEST_ID'"
    else
        fail "Read did not find test case"
        echo "       $READ_OUTPUT"
    fi
else
    fail "No test ID from compose"
fi

# ── Test 8: Read returns test_case with advisory_only ──
TESTS=$((TESTS + 1))
if [ -n "$FIRST_TEST_ID" ]; then
    TC_ADVISORY=$(echo "$READ_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); tc=d.get('test_case',{}); print(tc.get('advisory_only', False))" 2>/dev/null || echo "false")
    TC_SOURCE=$(echo "$READ_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); tc=d.get('test_case',{}); print(tc.get('source_artifact',''))" 2>/dev/null || echo "")
    if [ "$TC_ADVISORY" = "True" ] && [ -n "$TC_SOURCE" ]; then
        pass "Read test case has advisory_only=true and source_artifact='$TC_SOURCE'"
    else
        fail "Read test case missing advisory_only or source_artifact"
    fi
else
    fail "No test ID from compose"
fi

# ── Test 9: Read unknown test returns not found ──
TESTS=$((TESTS + 1))
NOTFOUND_OUTPUT=$(python3 "$COMPOSITION_SCRIPT" read "TC-NONEXISTENT-001" 2>&1) || true
NOTFOUND_FOUND=$(echo "$NOTFOUND_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('found', 'missing'))" 2>/dev/null || echo "missing")
if [ "$NOTFOUND_FOUND" = "False" ]; then
    pass "Read unknown test returns found=False"
else
    fail "Read unknown test did not return found=False"
fi

# ── Test 10: Validate valid test case ──
TESTS=$((TESTS + 1))
VAL_TC_OUTPUT=$(python3 "$COMPOSITION_SCRIPT" validate "$FIXTURES_DIR/valid-composed-test-case.json" 2>&1) || true
VAL_TC_SUCCESS=$(echo "$VAL_TC_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "false")
if [ "$VAL_TC_SUCCESS" = "True" ]; then
    pass "Validate accepts valid test case"
else
    fail "Validate rejected valid test case"
    echo "       $VAL_TC_OUTPUT"
fi

# ── Test 11: Validate invalid test case ──
TESTS=$((TESTS + 1))
VAL_INV_OUTPUT=$(python3 "$COMPOSITION_SCRIPT" validate "$FIXTURES_DIR/invalid-test-case-schema-violation.json" 2>&1) || true
VAL_INV_SUCCESS=$(echo "$VAL_INV_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "true")
if [ "$VAL_INV_SUCCESS" = "False" ]; then
    pass "Validate rejects invalid test case"
else
    fail "Validate accepted invalid test case"
fi

# ── Test 12: Validate authority-bearing evidence rejected ──
TESTS=$((TESTS + 1))
AUTH_FIXTURE="$FIXTURES_DIR/invalid-authority-bearing-evidence.json"
AUTH_OUTPUT=$(python3 "$COMPOSITION_SCRIPT" validate "$AUTH_FIXTURE" 2>&1) || true
AUTH_SUCCESS=$(echo "$AUTH_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "true")
if [ "$AUTH_SUCCESS" = "False" ]; then
    pass "Authority-bearing evidence rejected by validate"
else
    fail "Authority-bearing evidence accepted"
    echo "       $AUTH_OUTPUT"
fi

# ── Test 13: Validate mutation path evidence rejected ──
TESTS=$((TESTS + 1))
MUT_FIXTURE="$FIXTURES_DIR/invalid-mutation-path-evidence.json"
MUT_OUTPUT=$(python3 "$COMPOSITION_SCRIPT" validate "$MUT_FIXTURE" 2>&1) || true
MUT_SUCCESS=$(echo "$MUT_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "true")
if [ "$MUT_SUCCESS" = "False" ]; then
    pass "Mutation path evidence rejected by validate"
else
    fail "Mutation path evidence accepted"
fi

# ── Test 14: Validate malformed evidence rejected ──
TESTS=$((TESTS + 1))
MAL_FIXTURE="$FIXTURES_DIR/invalid-malformed-evidence.json"
MAL_OUTPUT=$(python3 "$COMPOSITION_SCRIPT" validate "$MAL_FIXTURE" 2>&1) || true
MAL_SUCCESS=$(echo "$MAL_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "true")
if [ "$MAL_SUCCESS" = "False" ]; then
    pass "Malformed evidence rejected by validate"
else
    fail "Malformed evidence accepted"
fi

# ── Test 15: Status reports counts ──
TESTS=$((TESTS + 1))
STATUS_OUTPUT=$(python3 "$COMPOSITION_SCRIPT" status 2>&1) || true
STATUS_COUNT=$(echo "$STATUS_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_test_cases',0))" 2>/dev/null || echo "0")
if [ "$STATUS_COUNT" -ge 1 ]; then
    pass "Status reports $STATUS_COUNT test case(s)"
else
    fail "Status reports 0 test cases"
fi

# ── Test 16: Status includes advisory-only boundary ──
TESTS=$((TESTS + 1))
STATUS_ADVISORY=$(echo "$STATUS_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('advisory_only', 'missing'))" 2>/dev/null || echo "missing")
STATUS_NOTICE=$(echo "$STATUS_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('advisory_notice','')))" 2>/dev/null || echo "0")
if [ "$STATUS_ADVISORY" = "True" ] && [ "$STATUS_NOTICE" -ge 10 ]; then
    pass "Status includes advisory_only=True and advisory_notice"
else
    fail "Status missing advisory boundary"
fi

# ── Test 17: Ingest cross-project evidence and compose ──
TESTS=$((TESTS + 1))
CROSS_FIXTURE="$FIXTURES_DIR/valid-cross-project-evidence-source.json"
CROSS_INGEST=$(python3 "$INTAKE_SCRIPT" ingest "$CROSS_FIXTURE" 2>&1) || true
CROSS_SUCCESS=$(echo "$CROSS_INGEST" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "false")
if [ "$CROSS_SUCCESS" = "True" ]; then
    # Cross-project ingested — now compose all
    COMPOSE2_OUTPUT=$(python3 "$COMPOSITION_SCRIPT" compose 2>&1) || true
    COMPOSE2_COUNT=$(echo "$COMPOSE2_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_test_cases_composed', 0))" 2>/dev/null || echo "0")
    if [ "$COMPOSE2_COUNT" -ge 1 ]; then
        pass "Cross-project evidence produced $COMPOSE2_COUNT test case(s)"
    else
        # Could be 0 if all new tests were already composed (from prior compose)
        fail "Cross-project evidence produced 0 new test cases"
    fi
else
    fail "Failed to ingest cross-project evidence"
fi

# ── Test 18: Validate cross-project evidence with metadata ──
TESTS=$((TESTS + 1))
CROSS_VAL_OUTPUT=$(python3 "$COMPOSITION_SCRIPT" validate "$CROSS_FIXTURE" 2>&1) || true
CROSS_VAL_SUCCESS=$(echo "$CROSS_VAL_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "false")
if [ "$CROSS_VAL_SUCCESS" = "True" ]; then
    pass "Cross-project evidence with metadata validates"
else
    fail "Cross-project evidence with metadata rejected"
    echo "       $CROSS_VAL_OUTPUT"
fi

# ── Test 19: Clear removes all test cases ──
TESTS=$((TESTS + 1))
CLEAR_OUTPUT=$(python3 "$COMPOSITION_SCRIPT" clear 2>&1) || true
CLEAR_COUNT=$(echo "$CLEAR_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('cleared_count',0))" 2>/dev/null || echo "0")
STATUS_AFTER=$(python3 "$COMPOSITION_SCRIPT" status 2>&1 || true)
EMPTY_COUNT=$(echo "$STATUS_AFTER" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_test_cases',999))" 2>/dev/null || echo "999")
if [ "$CLEAR_COUNT" -ge 1 ] && [ "$EMPTY_COUNT" -eq 0 ]; then
    pass "Clear removed $CLEAR_COUNT test case(s), store now empty"
else
    fail "Clear did not work: cleared=$CLEAR_COUNT, after=$EMPTY_COUNT"
fi

# ── Test 20: Compose from empty store returns error ──
TESTS=$((TESTS + 1))
python3 "$INTAKE_SCRIPT" clear >/dev/null 2>&1 || true
EMPTY_COMPOSE=$(python3 "$COMPOSITION_SCRIPT" compose 2>&1) || true
EMPTY_SUCCESS=$(echo "$EMPTY_COMPOSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "true")
if [ "$EMPTY_SUCCESS" = "False" ]; then
    pass "Compose from empty store returns error"
else
    fail "Compose from empty store should have returned error"
fi

# ── Test 21: Read response has advisory_only ──
TESTS=$((TESTS + 1))
python3 "$COMPOSITION_SCRIPT" clear >/dev/null 2>&1 || true
python3 "$INTAKE_SCRIPT" ingest "$VALID_FIXTURE" >/dev/null 2>&1 || true
COMPOSE3_OUTPUT=$(python3 "$COMPOSITION_SCRIPT" compose 2>&1) || true
COMPOSE3_ID=$(echo "$COMPOSE3_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); ids=d.get('test_ids',[]); print(ids[0] if ids else '')" 2>/dev/null || echo "")
if [ -n "$COMPOSE3_ID" ]; then
    READ3_OUTPUT=$(python3 "$COMPOSITION_SCRIPT" read "$COMPOSE3_ID" 2>&1) || true
    READ3_ADVISORY=$(echo "$READ3_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('advisory_only', False))" 2>/dev/null || echo "false")
    READ3_SOURCE=$(echo "$READ3_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('source_project',''))" 2>/dev/null || echo "")
    READ3_CUSTODY=$(echo "$READ3_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('custody',''))" 2>/dev/null || echo "")
    if [ "$READ3_ADVISORY" = "True" ] && [ "$READ3_SOURCE" = "qa-pilot" ]; then
        pass "Read response includes advisory_only=true, source_project='qa-pilot', custody='$READ3_CUSTODY'"
    else
        fail "Read response missing advisory_only or source_project"
    fi
else
    fail "No test ID for read advisory check"
fi

# ── Test 22: Existing test-case files are QA Pilot-local (no cross-project index) ──
TESTS=$((TESTS + 1))
if [ -f "$TEST_CASES_DIR/test-case-index.json" ]; then
    TC_INDEX=$(python3 -c "import json; d=json.load(open('$TEST_CASES_DIR/test-case-index.json')); print(d.get('store_version',''))" 2>/dev/null || echo "")
    if echo "$TC_INDEX" | grep -q "qap-test-cases"; then
        pass "Test-case index is QA Pilot-local (version: $TC_INDEX)"
    else
        fail "Test-case index has unexpected version"
    fi
else
    fail "Test-case index not found at $TEST_CASES_DIR/test-case-index.json"
fi

# ── Test 23: Responses include advisory_notice (sampled) ──
TESTS=$((TESTS + 1))
SAMPLE_OUTPUTS=$(python3 "$COMPOSITION_SCRIPT" list --limit 5 2>&1 && python3 "$COMPOSITION_SCRIPT" status 2>&1) || true
NOTICE_COUNT=$(echo "$SAMPLE_OUTPUTS" | grep -c "advisory_notice" 2>/dev/null || echo "0")
if [ "$NOTICE_COUNT" -ge 2 ]; then
    pass "Multiple responses include advisory_notice"
else
    fail "Less than 2 responses have advisory_notice: found $NOTICE_COUNT"
fi

# ── Test 24: Validate cross-project evidence contains source_project_metadata ──
TESTS=$((TESTS + 1))
CROSS_DATA=$(python3 -c "
import json
d = json.load(open('$CROSS_FIXTURE'))
print(d.get('_source_project_metadata', {}).get('source_project_id', 'missing'))
" 2>/dev/null || echo "missing")
if [ "$CROSS_DATA" != "missing" ]; then
    pass "Cross-project fixture has source_project_metadata.source_project_id='$CROSS_DATA'"
else
    fail "Cross-project fixture missing source_project_metadata"
fi

cleanup

echo ""
echo "=============================================================="
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
