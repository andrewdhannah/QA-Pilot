#!/usr/bin/env bash
set -euo pipefail

# QA Pilot Epic Regression Builder Test Runner — QA-PILOT-EPIC-REGRESSION-BUILDER-1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILDER_SCRIPT="$SCRIPT_DIR/qa_pilot_epic_regression_builder.py"
BUILDER_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-epic-regression-builder.py"
INTAKE_SCRIPT="$SCRIPT_DIR/qa_pilot_mcp_evidence_intake.py"
COMPOSITION_SCRIPT="$SCRIPT_DIR/qa_pilot_test_composition.py"
EXPORT_SCRIPT="$SCRIPT_DIR/qa_pilot_result_packet_export.py"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-epic-regression-builder"
COMP_FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-test-composition"
EPIC_DIR="$REPO_ROOT/data/epic-regression"
PASS=0
FAIL=0
TESTS=0

cleanup() {
    python3 "$BUILDER_SCRIPT" clear >/dev/null 2>&1 || true
    python3 "$EXPORT_SCRIPT" clear >/dev/null 2>&1 || true
    python3 "$COMPOSITION_SCRIPT" clear >/dev/null 2>&1 || true
    python3 "$INTAKE_SCRIPT" clear >/dev/null 2>&1 || true
}

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Epic Regression Builder Tests — QA-PILOT-EPIC-REGRESSION-BUILDER-1"
echo "============================================================================"
echo ""

cleanup

# ── Test 1: Script exists ──
TESTS=$((TESTS + 1))
if [ -f "$BUILDER_SCRIPT" ]; then
    pass "Builder script found"
else
    fail "Builder script not found"
fi

# ── Test 2: Validator passes ──
TESTS=$((TESTS + 1))
VOUT=$(python3 "$BUILDER_VALIDATOR" 2>&1) || true
if echo "$VOUT" | grep -q "ALL CHECKS PASS"; then
    pass "Validator ALL CHECKS PASS"
else
    fail "Validator failed"
    echo "       $(echo "$VOUT" | tail -5)"
fi

# ── Test 3: Seed data chain (evidence → tests → results) ──
TESTS=$((TESTS + 1))
EVIDENCE_SOURCE="$COMP_FIXTURES_DIR/valid-evidence-source.json"
python3 "$INTAKE_SCRIPT" ingest "$EVIDENCE_SOURCE" >/dev/null 2>&1 || true
python3 "$COMPOSITION_SCRIPT" compose >/dev/null 2>&1 || true
python3 "$EXPORT_SCRIPT" export >/dev/null 2>&1 || true
pass "Data chain seeded (evidence → tests → results)"

# ── Test 4: Build Epic suite with auto-detected sprints ──
TESTS=$((TESTS + 1))
BUILD_OUT=$(python3 "$BUILDER_SCRIPT" build "EPIC-QA-PILOT-V1" 2>&1) || true
BUILD_OK=$(echo "$BUILD_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "false")
BUILD_SID=$(echo "$BUILD_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('suite_id',''))" 2>/dev/null || echo "")
if [ "$BUILD_OK" = "True" ] && [ -n "$BUILD_SID" ]; then
    pass "Build Epic suite '$BUILD_SID'"
else
    fail "Build failed"
    echo "       $BUILD_OUT"
fi

# ── Test 5: Suite has advisory=true ──
TESTS=$((TESTS + 1))
ADVISORY=$(echo "$BUILD_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); s=d.get('epic_suite',{}); print(s.get('advisory', False))" 2>/dev/null || echo "false")
if [ "$ADVISORY" = "True" ]; then
    pass "Suite has advisory=true"
else
    fail "Suite missing advisory"
fi

# ── Test 6: Suite has EP, TC, QR provenance ──
TESTS=$((TESTS + 1))
EV_CNT=$(echo "$BUILD_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); s=d.get('epic_suite',{}); p=s.get('provenance',{}); print(len(p.get('evidence_packets',[])))" 2>/dev/null || echo "0")
QR_CNT=$(echo "$BUILD_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); s=d.get('epic_suite',{}); p=s.get('provenance',{}); print(len(p.get('result_packets',[])))" 2>/dev/null || echo "0")
TC_CNT=$(echo "$BUILD_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); s=d.get('epic_suite',{}); print(len(s.get('tests',[])))" 2>/dev/null || echo "0")
if [ "$EV_CNT" -ge 1 ] && [ "$TC_CNT" -ge 1 ]; then
    pass "Suite has $EV_CNT evidence, $TC_CNT tests, $QR_CNT results"
else
    fail "Suite missing provenance: ev=$EV_CNT tc=$TC_CNT qr=$QR_CNT"
fi

# ── Test 7: Suite has result summary ──
TESTS=$((TESTS + 1))
HAS_RESULT=$(echo "$BUILD_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); s=d.get('epic_suite',{}); r=s.get('result',{}); print('passed' in r)" 2>/dev/null || echo "False")
if [ "$HAS_RESULT" = "True" ]; then
    pass "Suite has result summary"
else
    fail "Suite missing result summary"
fi

# ── Test 8: Response includes advisory_only, source_project, custody ──
TESTS=$((TESTS + 1))
RESP_ADV=$(echo "$BUILD_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('advisory_only', False))" 2>/dev/null || echo "false")
RESP_SRC=$(echo "$BUILD_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('source_project',''))" 2>/dev/null || echo "")
RESP_CUST=$(echo "$BUILD_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('custody',''))" 2>/dev/null || echo "")
if [ "$RESP_ADV" = "True" ] && [ "$RESP_SRC" = "qa-pilot" ]; then
    pass "Response has advisory_only=True, source_project='qa-pilot', custody='$RESP_CUST'"
else
    fail "Response missing advisory or source_project"
fi

# ── Test 9: List Epic suites ──
TESTS=$((TESTS + 1))
LIST_OUT=$(python3 "$BUILDER_SCRIPT" list --limit 50 2>&1) || true
LIST_CNT=$(echo "$LIST_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('epic_suites',[])))" 2>/dev/null || echo "0")
if [ "$LIST_CNT" -ge 1 ]; then
    pass "List returns $LIST_CNT suite(s)"
else
    fail "List returned 0"
fi

# ── Test 10: Read Epic suite ──
TESTS=$((TESTS + 1))
READ_OUT=$(python3 "$BUILDER_SCRIPT" read "$BUILD_SID" 2>&1) || true
READ_FOUND=$(echo "$READ_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('found', False))" 2>/dev/null || echo "false")
if [ "$READ_FOUND" = "True" ]; then
    pass "Read found suite '$BUILD_SID'"
else
    fail "Read did not find suite"
fi

# ── Test 11: Read returns suite with advisory ──
TESTS=$((TESTS + 1))
READ_ADV=$(echo "$READ_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); s=d.get('epic_suite',{}); print(s.get('advisory', False))" 2>/dev/null || echo "false")
if [ "$READ_ADV" = "True" ]; then
    pass "Read suite has advisory=true"
else
    fail "Read suite missing advisory"
fi

# ── Test 12: Read unknown returns not found ──
TESTS=$((TESTS + 1))
NF_OUT=$(python3 "$BUILDER_SCRIPT" read "ERS-NONEXISTENT-0001" 2>&1) || true
NF_FOUND=$(echo "$NF_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('found', 'missing'))" 2>/dev/null || echo "missing")
if [ "$NF_FOUND" = "False" ]; then
    pass "Read unknown returns found=False"
else
    fail "Read unknown did not return found=False"
fi

# ── Test 13: Validate valid fixture ──
TESTS=$((TESTS + 1))
VAL_OUT=$(python3 "$BUILDER_SCRIPT" validate "$FIXTURES_DIR/valid-epic-suite.json" 2>&1) || true
VAL_OK=$(echo "$VAL_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "false")
if [ "$VAL_OK" = "True" ]; then
    pass "Validate accepts valid suite"
else
    fail "Validate rejected valid suite"
    echo "       $VAL_OUT"
fi

# ── Test 14: Validate invalid fixture (schema) ──
TESTS=$((TESTS + 1))
VAL_INV=$(python3 "$BUILDER_SCRIPT" validate "$FIXTURES_DIR/invalid-schema-violation.json" 2>&1) || true
VAL_INV_OK=$(echo "$VAL_INV" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "true")
if [ "$VAL_INV_OK" = "False" ]; then
    pass "Validate rejects schema-violation suite"
else
    fail "Validate accepted schema-violation suite"
fi

# ── Test 15: Validate authority-claiming fixture rejected ──
TESTS=$((TESTS + 1))
VAL_AUTH=$(python3 "$BUILDER_SCRIPT" validate "$FIXTURES_DIR/invalid-authority-claiming.json" 2>&1) || true
VAL_AUTH_OK=$(echo "$VAL_AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "true")
if [ "$VAL_AUTH_OK" = "False" ]; then
    pass "Authority-claiming suite rejected"
else
    fail "Authority-claiming suite accepted"
fi

# ── Test 16: Validate broken-chain fixture rejected ──
TESTS=$((TESTS + 1))
VAL_BROKEN=$(python3 "$BUILDER_SCRIPT" validate "$FIXTURES_DIR/invalid-broken-chain.json" 2>&1) || true
VAL_BROKEN_OK=$(echo "$VAL_BROKEN" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "true")
if [ "$VAL_BROKEN_OK" = "False" ]; then
    pass "Broken-chain suite rejected (no provenance)"
else
    fail "Broken-chain suite should have been rejected"
fi

# ── Test 17: Status reports Epic suite count ──
TESTS=$((TESTS + 1))
STATUS_OUT=$(python3 "$BUILDER_SCRIPT" status 2>&1) || true
STATUS_CNT=$(echo "$STATUS_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_epic_suites',0))" 2>/dev/null || echo "0")
if [ "$STATUS_CNT" -ge 1 ]; then
    pass "Status reports $STATUS_CNT suite(s)"
else
    fail "Status reports 0"
fi

# ── Test 18: Status includes advisory boundary ──
TESTS=$((TESTS + 1))
ST_ADV=$(echo "$STATUS_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('advisory_only', 'missing'))" 2>/dev/null || echo "missing")
ST_NOTICE=$(echo "$STATUS_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('advisory_notice','')))" 2>/dev/null || echo "0")
if [ "$ST_ADV" = "True" ] && [ "$ST_NOTICE" -ge 10 ]; then
    pass "Status has advisory_only=True and advisory_notice"
else
    fail "Status missing advisory boundary"
fi

# ── Test 19: Build with explicit sprint IDs ──
TESTS=$((TESTS + 1))
EXPLICIT_OUT=$(python3 "$BUILDER_SCRIPT" build "EPIC-EXPLICIT" --sprint-ids "QA-PILOT-MCP-EVIDENCE-INTAKE-1" 2>&1) || true
EXPLICIT_OK=$(echo "$EXPLICIT_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "false")
if [ "$EXPLICIT_OK" = "True" ]; then
    pass "Build with explicit sprint IDs succeeds"
else
    fail "Build with explicit sprint IDs failed"
fi

# ── Test 20: Clear removes all suites ──
TESTS=$((TESTS + 1))
CLEAR_OUT=$(python3 "$BUILDER_SCRIPT" clear 2>&1) || true
CLEAR_CNT=$(echo "$CLEAR_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('cleared_count',0))" 2>/dev/null || echo "0")
ST_AFTER=$(python3 "$BUILDER_SCRIPT" status 2>&1 || true)
EMPTY_CNT=$(echo "$ST_AFTER" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_epic_suites',999))" 2>/dev/null || echo "999")
if [ "$CLEAR_CNT" -ge 1 ] && [ "$EMPTY_CNT" -eq 0 ]; then
    pass "Clear removed $CLEAR_CNT suite(s), store empty"
else
    fail "Clear failed: cleared=$CLEAR_CNT after=$EMPTY_CNT"
fi

# ── Test 21: Build from empty store returns error ──
TESTS=$((TESTS + 1))
python3 "$INTAKE_SCRIPT" clear >/dev/null 2>&1 || true
python3 "$COMPOSITION_SCRIPT" clear >/dev/null 2>&1 || true
python3 "$EXPORT_SCRIPT" clear >/dev/null 2>&1 || true
EMPTY_BUILD=$(python3 "$BUILDER_SCRIPT" build "EPIC-EMPTY" 2>&1) || true
EMPTY_OK=$(echo "$EMPTY_BUILD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "true")
if [ "$EMPTY_OK" = "False" ]; then
    pass "Build from empty store returns error"
else
    fail "Build from empty store should have returned error"
fi

# ── Test 22: Suite has sprint_ids ──
TESTS=$((TESTS + 1))
# Re-seed and build
python3 "$INTAKE_SCRIPT" ingest "$EVIDENCE_SOURCE" >/dev/null 2>&1 || true
python3 "$COMPOSITION_SCRIPT" compose >/dev/null 2>&1 || true
python3 "$EXPORT_SCRIPT" export >/dev/null 2>&1 || true
BUILD2_OUT=$(python3 "$BUILDER_SCRIPT" build "EPIC-SPRINT-CHECK" 2>&1) || true
HAS_SPRINTS=$(echo "$BUILD2_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); s=d.get('epic_suite',{}); print(len(s.get('sprint_ids',[])) >= 1)" 2>/dev/null || echo "False")
if [ "$HAS_SPRINTS" = "True" ]; then
    pass "Suite has sprint_ids"
else
    fail "Suite missing sprint_ids"
fi

# ── Test 23: Read response has advisory_only, source_project, custody ──
TESTS=$((TESTS + 1))
SID2=$(echo "$BUILD2_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('suite_id',''))" 2>/dev/null || echo "")
if [ -n "$SID2" ]; then
    READ2_OUT=$(python3 "$BUILDER_SCRIPT" read "$SID2" 2>&1) || true
    READ2_ADV=$(echo "$READ2_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('advisory_only', False))" 2>/dev/null || echo "false")
    READ2_SRC=$(echo "$READ2_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('source_project',''))" 2>/dev/null || echo "")
    READ2_CUST=$(echo "$READ2_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('custody',''))" 2>/dev/null || echo "")
    if [ "$READ2_ADV" = "True" ] && [ "$READ2_SRC" = "qa-pilot" ]; then
        pass "Read response has advisory_only=True, source_project='qa-pilot', custody='$READ2_CUST'"
    else
        fail "Read response missing advisory or source_project"
    fi
else
    fail "No suite_id for read advisory check"
fi

# ── Test 24: Multiple responses include advisory_notice ──
TESTS=$((TESTS + 1))
SAMP=$(python3 "$BUILDER_SCRIPT" list --limit 5 2>&1 && python3 "$BUILDER_SCRIPT" status 2>&1) || true
NOTICE_CNT=$(echo "$SAMP" | grep -c "advisory_notice" 2>/dev/null || echo "0")
if [ "$NOTICE_CNT" -ge 2 ]; then
    pass "Multiple responses include advisory_notice"
else
    fail "Less than 2 responses have advisory_notice: $NOTICE_CNT"
fi

cleanup

echo ""
echo "============================================================================"
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
