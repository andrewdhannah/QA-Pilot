#!/usr/bin/env bash
set -euo pipefail

# QA Pilot Result Packet Export Test Runner — QA-PILOT-RESULT-PACKET-EXPORT-1
# Tests: export script, validator, fixtures, store operations, RP rules,
#        boundary enforcement, regression across #23-#34

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
EXPORT_SCRIPT="$SCRIPT_DIR/qa_pilot_result_packet_export.py"
EXPORT_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-result-packet-export.py"
INTAKE_SCRIPT="$SCRIPT_DIR/qa_pilot_mcp_evidence_intake.py"
COMPOSITION_SCRIPT="$SCRIPT_DIR/qa_pilot_test_composition.py"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-result-packet-export"
COMP_FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-test-composition"
RESULT_DIR="$REPO_ROOT/data/result-packets"
PASS=0
FAIL=0
TESTS=0

cleanup() {
    python3 "$EXPORT_SCRIPT" clear >/dev/null 2>&1 || true
    python3 "$COMPOSITION_SCRIPT" clear >/dev/null 2>&1 || true
    python3 "$INTAKE_SCRIPT" clear >/dev/null 2>&1 || true
}

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Result Packet Export Tests — QA-PILOT-RESULT-PACKET-EXPORT-1"
echo "====================================================================="
echo ""

cleanup

# ── Test 1: Export script exists ──
TESTS=$((TESTS + 1))
if [ -f "$EXPORT_SCRIPT" ]; then
    pass "Export script found"
else
    fail "Export script not found at $EXPORT_SCRIPT"
fi

# ── Test 2: Validator passes ──
TESTS=$((TESTS + 1))
VALIDATOR_OUTPUT=$(python3 "$EXPORT_VALIDATOR" 2>&1) || true
if echo "$VALIDATOR_OUTPUT" | grep -q "ALL CHECKS PASS"; then
    pass "Validator ALL CHECKS PASS"
else
    fail "Validator failed"
    echo "       $(echo "$VALIDATOR_OUTPUT" | tail -5)"
fi

# ── Test 3: Ingest evidence and compose tests for export ──
TESTS=$((TESTS + 1))
EVIDENCE_SOURCE="$COMP_FIXTURES_DIR/valid-evidence-source.json"
if [ -f "$EVIDENCE_SOURCE" ]; then
    INGEST_OUT=$(python3 "$INTAKE_SCRIPT" ingest "$EVIDENCE_SOURCE" 2>&1) || true
    INGEST_OK=$(echo "$INGEST_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "false")
    if [ "$INGEST_OK" = "True" ]; then
        COMP_OUT=$(python3 "$COMPOSITION_SCRIPT" compose 2>&1) || true
        COMP_COUNT=$(echo "$COMP_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_test_cases_composed',0))" 2>/dev/null || echo "0")
        if [ "$COMP_COUNT" -ge 1 ]; then
            pass "Evidence ingested ($COMP_COUNT test cases composed)"
        else
            fail "Test composition produced 0 cases"
        fi
    else
        fail "Failed to ingest evidence"
    fi
else
    fail "Evidence fixture not found at $EVIDENCE_SOURCE"
fi

# ── Test 4: Export generates a result packet ──
TESTS=$((TESTS + 1))
EXPORT_OUTPUT=$(python3 "$EXPORT_SCRIPT" export 2>&1) || true
EXPORT_SUCCESS=$(echo "$EXPORT_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "false")
EXPORT_ID=$(echo "$EXPORT_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('result_id',''))" 2>/dev/null || echo "")
if [ "$EXPORT_SUCCESS" = "True" ] && [ -n "$EXPORT_ID" ]; then
    pass "Export generated result packet '$EXPORT_ID'"
else
    fail "Export failed"
    echo "       $EXPORT_OUTPUT"
fi

# ── Test 5: Exported result has advisory=true and owner_action_required=true ──
TESTS=$((TESTS + 1))
RP_ADVISORY=$(echo "$EXPORT_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); rp=d.get('result_packet',{}); print(rp.get('advisory', False))" 2>/dev/null || echo "false")
RP_OWNER=$(echo "$EXPORT_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); rp=d.get('result_packet',{}); print(rp.get('owner_action_required', False))" 2>/dev/null || echo "false")
if [ "$RP_ADVISORY" = "True" ] && [ "$RP_OWNER" = "True" ]; then
    pass "Result packet has advisory=true and owner_action_required=true"
else
    fail "Result packet missing advisory or owner_action_required"
fi

# ── Test 6: Result packet has evidence and test provenance ──
TESTS=$((TESTS + 1))
EVID_COUNT=$(echo "$EXPORT_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); rp=d.get('result_packet',{}); prov=rp.get('provenance',{}); print(len(prov.get('evidence_packets',[])))" 2>/dev/null || echo "0")
TC_COUNT=$(echo "$EXPORT_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); rp=d.get('result_packet',{}); prov=rp.get('provenance',{}); print(len(prov.get('test_cases',[])))" 2>/dev/null || echo "0")
if [ "$EVID_COUNT" -ge 1 ] && [ "$TC_COUNT" -ge 1 ]; then
    pass "Result packet has $EVID_COUNT evidence + $TC_COUNT test case provenance"
else
    fail "Result packet missing provenance: ev=$EVID_COUNT tc=$TC_COUNT"
fi

# ── Test 7: Result packet has findings ──
TESTS=$((TESTS + 1))
FINDING_COUNT=$(echo "$EXPORT_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); rp=d.get('result_packet',{}); print(len(rp.get('findings',[])))" 2>/dev/null || echo "0")
if [ "$FINDING_COUNT" -ge 1 ]; then
    pass "Result packet has $FINDING_COUNT finding(s)"
else
    fail "Result packet has 0 findings"
fi

# ── Test 8: Response includes advisory_only and source_project ──
TESTS=$((TESTS + 1))
RESP_ADVISORY=$(echo "$EXPORT_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('advisory_only', False))" 2>/dev/null || echo "false")
RESP_SRC=$(echo "$EXPORT_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('source_project',''))" 2>/dev/null || echo "")
if [ "$RESP_ADVISORY" = "True" ] && [ "$RESP_SRC" = "qa-pilot" ]; then
    pass "Export response includes advisory_only and source_project='qa-pilot'"
else
    fail "Export response missing advisory_only or source_project"
fi

# ── Test 9: List exported results ──
TESTS=$((TESTS + 1))
LIST_OUTPUT=$(python3 "$EXPORT_SCRIPT" list --limit 50 2>&1) || true
LIST_COUNT=$(echo "$LIST_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('result_packets',[])))" 2>/dev/null || echo "0")
if [ "$LIST_COUNT" -ge 1 ]; then
    pass "List returns $LIST_COUNT result packet(s)"
else
    fail "List returned 0 results"
fi

# ── Test 10: Read result packet ──
TESTS=$((TESTS + 1))
READ_OUTPUT=$(python3 "$EXPORT_SCRIPT" read "$EXPORT_ID" 2>&1) || true
READ_FOUND=$(echo "$READ_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('found', False))" 2>/dev/null || echo "false")
if [ "$READ_FOUND" = "True" ]; then
    pass "Read found result packet '$EXPORT_ID'"
else
    fail "Read did not find result packet"
    echo "       $READ_OUTPUT"
fi

# ── Test 11: Read returns result_packet with advisory ──
TESTS=$((TESTS + 1))
RP_ADVISORY2=$(echo "$READ_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); rp=d.get('result_packet',{}); print(rp.get('advisory', False))" 2>/dev/null || echo "false")
if [ "$RP_ADVISORY2" = "True" ]; then
    pass "Read result packet has advisory=true"
else
    fail "Read result packet missing advisory"
fi

# ── Test 12: Read unknown returns not found ──
TESTS=$((TESTS + 1))
NOTFOUND_OUTPUT=$(python3 "$EXPORT_SCRIPT" read "QR-NONEXISTENT-0001" 2>&1) || true
NOTFOUND_FOUND=$(echo "$NOTFOUND_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('found', 'missing'))" 2>/dev/null || echo "missing")
if [ "$NOTFOUND_FOUND" = "False" ]; then
    pass "Read unknown returns found=False"
else
    fail "Read unknown did not return found=False"
fi

# ── Test 13: Validate valid result packet ──
TESTS=$((TESTS + 1))
VAL_OUTPUT=$(python3 "$EXPORT_SCRIPT" validate "$FIXTURES_DIR/valid-result-packet.json" 2>&1) || true
VAL_SUCCESS=$(echo "$VAL_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "false")
if [ "$VAL_SUCCESS" = "True" ]; then
    pass "Validate accepts valid result packet"
else
    fail "Validate rejected valid result packet"
    echo "       $VAL_OUTPUT"
fi

# ── Test 14: Validate invalid result packet ──
TESTS=$((TESTS + 1))
VAL_INV_OUTPUT=$(python3 "$EXPORT_SCRIPT" validate "$FIXTURES_DIR/invalid-result-packet-schema-violation.json" 2>&1) || true
VAL_INV_SUCCESS=$(echo "$VAL_INV_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "true")
if [ "$VAL_INV_SUCCESS" = "False" ]; then
    pass "Validate rejects invalid result packet"
else
    fail "Validate accepted invalid result packet"
fi

# ── Test 15: Validate authority-claiming result packet rejected ──
TESTS=$((TESTS + 1))
VAL_AUTH_OUTPUT=$(python3 "$EXPORT_SCRIPT" validate "$FIXTURES_DIR/invalid-authority-claiming-result.json" 2>&1) || true
VAL_AUTH_SUCCESS=$(echo "$VAL_AUTH_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "true")
if [ "$VAL_AUTH_SUCCESS" = "False" ]; then
    pass "Authority-claiming result packet rejected"
else
    fail "Authority-claiming result packet accepted"
fi

# ── Test 16: Status reports result packet count ──
TESTS=$((TESTS + 1))
STATUS_OUTPUT=$(python3 "$EXPORT_SCRIPT" status 2>&1) || true
STATUS_COUNT=$(echo "$STATUS_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_result_packets',0))" 2>/dev/null || echo "0")
if [ "$STATUS_COUNT" -ge 1 ]; then
    pass "Status reports $STATUS_COUNT result packet(s)"
else
    fail "Status reports 0 results"
fi

# ── Test 17: Status includes advisory-only boundary ──
TESTS=$((TESTS + 1))
STATUS_ADVISORY=$(echo "$STATUS_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('advisory_only', 'missing'))" 2>/dev/null || echo "missing")
STATUS_NOTICE=$(echo "$STATUS_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('advisory_notice','')))" 2>/dev/null || echo "0")
if [ "$STATUS_ADVISORY" = "True" ] && [ "$STATUS_NOTICE" -ge 10 ]; then
    pass "Status includes advisory_only=True and advisory_notice"
else
    fail "Status missing advisory boundary"
fi

# ── Test 18: Clear removes all result packets ──
TESTS=$((TESTS + 1))
CLEAR_OUTPUT=$(python3 "$EXPORT_SCRIPT" clear 2>&1) || true
CLEAR_COUNT=$(echo "$CLEAR_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('cleared_count',0))" 2>/dev/null || echo "0")
STATUS_AFTER=$(python3 "$EXPORT_SCRIPT" status 2>&1 || true)
EMPTY_COUNT=$(echo "$STATUS_AFTER" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_result_packets',999))" 2>/dev/null || echo "999")
if [ "$CLEAR_COUNT" -ge 1 ] && [ "$EMPTY_COUNT" -eq 0 ]; then
    pass "Clear removed $CLEAR_COUNT result packet(s), store now empty"
else
    fail "Clear did not work: cleared=$CLEAR_COUNT, after=$EMPTY_COUNT"
fi

# ── Test 19: Export from empty store returns error ──
TESTS=$((TESTS + 1))
python3 "$INTAKE_SCRIPT" clear >/dev/null 2>&1 || true
python3 "$COMPOSITION_SCRIPT" clear >/dev/null 2>&1 || true
EMPTY_EXPORT=$(python3 "$EXPORT_SCRIPT" export 2>&1) || true
EMPTY_SUCCESS=$(echo "$EMPTY_EXPORT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "true")
if [ "$EMPTY_SUCCESS" = "False" ]; then
    pass "Export from empty store returns error"
else
    fail "Export from empty store should have returned error"
fi

# ── Test 20: Export filtered by source evidence ──
TESTS=$((TESTS + 1))
python3 "$INTAKE_SCRIPT" ingest "$EVIDENCE_SOURCE" >/dev/null 2>&1 || true
python3 "$COMPOSITION_SCRIPT" compose >/dev/null 2>&1 || true
FILTERED_EXPORT=$(python3 "$EXPORT_SCRIPT" export --source-evidence "EP-20260706-010" 2>&1) || true
FILTERED_SUCCESS=$(echo "$FILTERED_EXPORT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "false")
if [ "$FILTERED_SUCCESS" = "True" ]; then
    pass "Export filtered by source evidence succeeds"
else
    fail "Export filtered by source evidence failed"
fi

# ── Test 21: Read response has advisory_only and source_project ──
TESTS=$((TESTS + 1))
READ2_ID=$(echo "$FILTERED_EXPORT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('result_id',''))" 2>/dev/null || echo "")
if [ -n "$READ2_ID" ]; then
    READ2_OUTPUT=$(python3 "$EXPORT_SCRIPT" read "$READ2_ID" 2>&1) || true
    READ2_ADVISORY=$(echo "$READ2_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('advisory_only', False))" 2>/dev/null || echo "false")
    READ2_SRC=$(echo "$READ2_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('source_project',''))" 2>/dev/null || echo "")
    READ2_CUSTODY=$(echo "$READ2_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('custody',''))" 2>/dev/null || echo "")
    if [ "$READ2_ADVISORY" = "True" ] && [ "$READ2_SRC" = "qa-pilot" ]; then
        pass "Read response has advisory_only=True, source_project='qa-pilot', custody='$READ2_CUSTODY'"
    else
        fail "Read response missing advisory_only or source_project"
    fi
else
    fail "No result_id from filtered export"
fi

# ── Test 22: Result packet has sprint_ids and summary ──
TESTS=$((TESTS + 1))
HAS_SPRINTS=$(echo "$FILTERED_EXPORT" | python3 -c "import sys,json; d=json.load(sys.stdin); rp=d.get('result_packet',{}); print(len(rp.get('sprint_ids',[])) >= 1)" 2>/dev/null || echo "False")
HAS_SUMMARY=$(echo "$FILTERED_EXPORT" | python3 -c "import sys,json; d=json.load(sys.stdin); rp=d.get('result_packet',{}); s=rp.get('summary',{}); print('tests_passed' in s)" 2>/dev/null || echo "False")
if [ "$HAS_SPRINTS" = "True" ] && [ "$HAS_SUMMARY" = "True" ]; then
    pass "Result packet has sprint_ids and summary"
else
    fail "Result packet missing sprint_ids or summary"
fi

# ── Test 23: Multiple responses include advisory_notice ──
TESTS=$((TESTS + 1))
SAMPLE_OUT=$(python3 "$EXPORT_SCRIPT" list --limit 5 2>&1 && python3 "$EXPORT_SCRIPT" status 2>&1) || true
NOTICE_COUNT=$(echo "$SAMPLE_OUT" | grep -c "advisory_notice" 2>/dev/null || echo "0")
if [ "$NOTICE_COUNT" -ge 2 ]; then
    pass "Multiple responses include advisory_notice"
else
    fail "Less than 2 responses have advisory_notice: found $NOTICE_COUNT"
fi

# ── Test 24: Exported response has advisory in result_packet ──
TESTS=$((TESTS + 1))
EXPORT_ADVISORY_IN_RP=$(echo "$FILTERED_EXPORT" | python3 -c "import sys,json; d=json.load(sys.stdin); rp=d.get('result_packet',{}); print(rp.get('advisory', False))" 2>/dev/null || echo "false")
if [ "$EXPORT_ADVISORY_IN_RP" = "True" ]; then
    pass "Exported result_packet.advisory=True"
else
    fail "Exported result_packet.advisory is not True"
fi

cleanup

echo ""
echo "====================================================================="
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
