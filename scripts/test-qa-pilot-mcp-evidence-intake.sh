#!/usr/bin/env bash
set -euo pipefail

# QA Pilot MCP Evidence Intake Test Runner — QA-PILOT-MCP-EVIDENCE-INTAKE-1
# Tests: intake script, validator, fixtures, store operations, EM rules,
#        boundary enforcement, regression across #23-#32

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
INTAKE_SCRIPT="$SCRIPT_DIR/qa_pilot_mcp_evidence_intake.py"
INTAKE_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-mcp-evidence-intake.py"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-mcp-evidence-intake"
EVIDENCE_DIR="$REPO_ROOT/data/evidence"
PASS=0
FAIL=0
TESTS=0

# Clear evidence store before starting
cleanup() {
    python3 "$INTAKE_SCRIPT" clear >/dev/null 2>&1 || true
}

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot MCP Evidence Intake Tests — QA-PILOT-MCP-EVIDENCE-INTAKE-1"
echo "=================================================================="
echo ""

cleanup

# ── Test 1: Intake script exists ──
TESTS=$((TESTS + 1))
if [ -f "$INTAKE_SCRIPT" ]; then
    pass "Intake script found"
else
    fail "Intake script not found at $INTAKE_SCRIPT"
fi

# ── Test 2: Validator passes ──
TESTS=$((TESTS + 1))
VALIDATOR_OUTPUT=$(python3 "$INTAKE_VALIDATOR" 2>&1) || true
if echo "$VALIDATOR_OUTPUT" | grep -q "ALL CHECKS PASS"; then
    pass "Validator ALL CHECKS PASS"
else
    fail "Validator failed"
    echo "       $(echo "$VALIDATOR_OUTPUT" | tail -5)"
fi

# ── Test 3: qa_evidence_validate accepts valid fixture ──
TESTS=$((TESTS + 1))
VALID_FIXTURE="$FIXTURES_DIR/valid-evidence-packet.json"
VAL_OUTPUT=$(python3 "$INTAKE_SCRIPT" validate "$VALID_FIXTURE" 2>&1) || true
VAL_SUCCESS=$(echo "$VAL_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "false")
if [ "$VAL_SUCCESS" = "True" ]; then
    pass "qa_evidence_validate accepts valid evidence packet"
else
    fail "qa_evidence_validate rejected valid packet"
    echo "       $VAL_OUTPUT"
fi

# ── Test 4: qa_evidence_validate rejects invalid fixture ──
TESTS=$((TESTS + 1))
INVALID_FIXTURE="$FIXTURES_DIR/invalid-evidence-missing-fields.json"
VAL_INV_OUTPUT=$(python3 "$INTAKE_SCRIPT" validate "$INVALID_FIXTURE" 2>&1) || true
VAL_INV_SUCCESS=$(echo "$VAL_INV_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "true")
if [ "$VAL_INV_SUCCESS" = "False" ]; then
    pass "qa_evidence_validate rejects invalid evidence packet"
else
    fail "qa_evidence_validate accepted invalid packet"
    echo "       $VAL_INV_OUTPUT"
fi

# ── Test 5: qa_evidence_ingest accepts valid fixture ──
TESTS=$((TESTS + 1))
INGEST_OUTPUT=$(python3 "$INTAKE_SCRIPT" ingest "$VALID_FIXTURE" 2>&1) || true
INGEST_SUCCESS=$(echo "$INGEST_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "false")
INGEST_PID=$(echo "$INGEST_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('packet_id',''))" 2>/dev/null || echo "")
if [ "$INGEST_SUCCESS" = "True" ]; then
    pass "qa_evidence_ingest accepted valid packet: $INGEST_PID"
else
    fail "qa_evidence_ingest rejected valid packet"
    echo "       $INGEST_OUTPUT"
fi

# ── Test 6: Ingest returns advisory_only=true ──
TESTS=$((TESTS + 1))
ADVISORY_ONLY=$(echo "$INGEST_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('advisory_only', False))" 2>/dev/null || echo "false")
if [ "$ADVISORY_ONLY" = "True" ]; then
    pass "Ingest response returns advisory_only=true"
else
    fail "Ingest response missing advisory_only"
fi

# ── Test 7: Ingest includes source_project and custody ──
TESTS=$((TESTS + 1))
SRC_PROJ=$(echo "$INGEST_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('source_project',''))" 2>/dev/null || echo "")
CUSTODY=$(echo "$INGEST_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('custody',''))" 2>/dev/null || echo "")
if [ "$SRC_PROJ" = "qa-pilot" ] && echo "$CUSTODY" | grep -q "qa-pilot"; then
    pass "Ingest response includes source_project='qa-pilot' and custody='$CUSTODY'"
else
    fail "Ingest response missing source_project or custody: src='$SRC_PROJ' custody='$CUSTODY'"
fi

# ── Test 8: qa_evidence_ingest rejects duplicate ──
TESTS=$((TESTS + 1))
DUP_OUTPUT=$(python3 "$INTAKE_SCRIPT" ingest "$VALID_FIXTURE" 2>&1) || true
DUP_SUCCESS=$(echo "$DUP_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "true")
if [ "$DUP_SUCCESS" = "False" ]; then
    pass "Duplicate packet rejected"
else
    fail "Duplicate packet was accepted"
    echo "       $DUP_OUTPUT"
fi

# ── Test 9: qa_evidence_list returns evidence ──
TESTS=$((TESTS + 1))
LIST_OUTPUT=$(python3 "$INTAKE_SCRIPT" list --limit 50 2>&1) || true
LIST_COUNT=$(echo "$LIST_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('evidence',[])))" 2>/dev/null || echo "0")
if [ "$LIST_COUNT" -ge 1 ]; then
    pass "qa_evidence_list returns $LIST_COUNT evidence(s)"
else
    fail "qa_evidence_list returned no evidence"
    echo "       $LIST_OUTPUT"
fi

# ── Test 10: qa_evidence_list with project filter ──
TESTS=$((TESTS + 1))
LIST_PROJ_OUTPUT=$(python3 "$INTAKE_SCRIPT" list --project qa-pilot 2>&1) || true
LIST_PROJ_COUNT=$(echo "$LIST_PROJ_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('evidence',[])))" 2>/dev/null || echo "0")
if [ "$LIST_PROJ_COUNT" -ge 1 ]; then
    pass "qa_evidence_list with --project qa-pilot returns $LIST_PROJ_COUNT"
else
    fail "qa_evidence_list with --project returned 0"
fi

# ── Test 11: qa_evidence_read returns stored packet ──
TESTS=$((TESTS + 1))
READ_OUTPUT=$(python3 "$INTAKE_SCRIPT" read "$INGEST_PID" 2>&1) || true
READ_FOUND=$(echo "$READ_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('found', False))" 2>/dev/null || echo "false")
if [ "$READ_FOUND" = "True" ]; then
    pass "qa_evidence_read found packet '$INGEST_PID'"
else
    fail "qa_evidence_read did not find packet '$INGEST_PID'"
    echo "       $READ_OUTPUT"
fi

# ── Test 12: qa_evidence_read returns correct packet_id ──
TESTS=$((TESTS + 1))
READ_PID=$(echo "$READ_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('packet_id',''))" 2>/dev/null || echo "")
if [ "$READ_PID" = "$INGEST_PID" ]; then
    pass "Read returned correct packet_id '$READ_PID'"
else
    fail "Read returned wrong packet_id: '$READ_PID' vs '$INGEST_PID'"
fi

# ── Test 13: qa_evidence_read returns advisory_only in response ──
TESTS=$((TESTS + 1))
READ_ADVISORY=$(echo "$READ_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('advisory_only', False))" 2>/dev/null || echo "false")
if [ "$READ_ADVISORY" = "True" ]; then
    pass "Read response includes advisory_only=true"
else
    fail "Read response missing advisory_only"
fi

# ── Test 14: Read unknown packet returns not found ──
TESTS=$((TESTS + 1))
NOTFOUND_OUTPUT=$(python3 "$INTAKE_SCRIPT" read "EP-NONEXISTENT-001" 2>&1) || true
NOTFOUND_FOUND=$(echo "$NOTFOUND_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('found', 'missing'))" 2>/dev/null || echo "missing")
if [ "$NOTFOUND_FOUND" = "False" ]; then
    pass "Read unknown packet returns found=False"
else
    fail "Read unknown packet did not return found=False"
fi

# ── Test 15: List with invalid limit returns error ──
TESTS=$((TESTS + 1))
BAD_LIMIT_OUTPUT=$(python3 "$INTAKE_SCRIPT" list --limit 0 2>&1) || true
BAD_LIMIT_ERROR=$(echo "$BAD_LIMIT_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error',''))" 2>/dev/null || echo "")
if [ -n "$BAD_LIMIT_ERROR" ]; then
    pass "List with limit=0 returns error: $BAD_LIMIT_ERROR"
else
    fail "List with limit=0 did not return error"
    echo "       $BAD_LIMIT_OUTPUT"
fi

# ── Test 16: Status reports evidence count ──
TESTS=$((TESTS + 1))
STATUS_OUTPUT=$(python3 "$INTAKE_SCRIPT" status 2>&1) || true
STATUS_COUNT=$(echo "$STATUS_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_evidence',0))" 2>/dev/null || echo "0")
if [ "$STATUS_COUNT" -ge 1 ]; then
    pass "Status reports $STATUS_COUNT evidence(s)"
else
    fail "Status reports 0 evidence"
fi

# ── Test 17: Status includes advisory-only statement ──
TESTS=$((TESTS + 1))
STATUS_ADVISORY=$(echo "$STATUS_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('advisory_only', 'missing'))" 2>/dev/null || echo "missing")
STATUS_NOTICE=$(echo "$STATUS_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('advisory_notice','')))" 2>/dev/null || echo "0")
if [ "$STATUS_ADVISORY" = "True" ] && [ "$STATUS_NOTICE" -ge 10 ]; then
    pass "Status includes advisory_only=True and advisory_notice"
else
    fail "Status missing advisory boundary"
fi

# ── Test 18: Validate cross-project with metadata passes ──
TESTS=$((TESTS + 1))
CROSS_FIXTURE="$FIXTURES_DIR/valid-evidence-packet-cross-project.json"
CROSS_OUTPUT=$(python3 "$INTAKE_SCRIPT" validate "$CROSS_FIXTURE" 2>&1) || true
CROSS_SUCCESS=$(echo "$CROSS_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "false")
if [ "$CROSS_SUCCESS" = "True" ]; then
    pass "Cross-project evidence with metadata validates"
else
    fail "Cross-project evidence with metadata rejected"
    echo "       $CROSS_OUTPUT"
fi

# ── Test 19: Validate cross-project without metadata rejected ──
TESTS=$((TESTS + 1))
NO_META_FIXTURE="$FIXTURES_DIR/invalid-evidence-cross-project-no-metadata.json"
NO_META_OUTPUT=$(python3 "$INTAKE_SCRIPT" validate "$NO_META_FIXTURE" 2>&1) || true
NO_META_SUCCESS=$(echo "$NO_META_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "true")
if [ "$NO_META_SUCCESS" = "False" ]; then
    pass "Cross-project without metadata rejected"
else
    fail "Cross-project without metadata incorrectly accepted"
fi

# ── Test 20: Validate stale/future timestamp rejects ──
TESTS=$((TESTS + 1))
STALE_FIXTURE="$FIXTURES_DIR/invalid-evidence-stale-timestamp.json"
STALE_OUTPUT=$(python3 "$INTAKE_SCRIPT" validate "$STALE_FIXTURE" 2>&1) || true
STALE_SUCCESS=$(echo "$STALE_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "true")
if [ "$STALE_SUCCESS" = "False" ]; then
    pass "Stale/future timestamp rejected"
else
    fail "Stale/future timestamp incorrectly accepted"
fi

# ── Test 21: Validate forbidden mutation rejected ──
TESTS=$((TESTS + 1))
MUTATION_FIXTURE="$FIXTURES_DIR/invalid-evidence-forbidden-mutation.json"
MUTATION_OUTPUT=$(python3 "$INTAKE_SCRIPT" validate "$MUTATION_FIXTURE" 2>&1) || true
MUTATION_SUCCESS=$(echo "$MUTATION_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "true")
if [ "$MUTATION_SUCCESS" = "False" ]; then
    pass "Forbidden mutation evidence rejected"
else
    fail "Forbidden mutation evidence incorrectly accepted"
fi

# ── Test 22: Clear removes all evidence ──
TESTS=$((TESTS + 1))
CLEAR_OUTPUT=$(python3 "$INTAKE_SCRIPT" clear 2>&1) || true
CLEAR_COUNT=$(echo "$CLEAR_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('cleared_count',0))" 2>/dev/null || echo "0")
STATUS_AFTER=$(python3 "$INTAKE_SCRIPT" status 2>&1 || true)
EMPTY_COUNT=$(echo "$STATUS_AFTER" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_evidence',999))" 2>/dev/null || echo "999")
if [ "$CLEAR_COUNT" -ge 1 ] && [ "$EMPTY_COUNT" -eq 0 ]; then
    pass "Clear removed $CLEAR_COUNT evidence(s), store now empty"
else
    fail "Clear did not work: cleared=$CLEAR_COUNT, after=$EMPTY_COUNT"
fi

# ── Test 23: Ingest cross-project with metadata ──
TESTS=$((TESTS + 1))
CROSS_INGEST_OUTPUT=$(python3 "$INTAKE_SCRIPT" ingest "$CROSS_FIXTURE" 2>&1) || true
CROSS_INGEST_SUCCESS=$(echo "$CROSS_INGEST_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "false")
if [ "$CROSS_INGEST_SUCCESS" = "True" ]; then
    pass "Cross-project evidence with metadata ingested"
else
    fail "Cross-project evidence with metadata not ingested"
    echo "       $CROSS_INGEST_OUTPUT"
fi

# ── Test 24: List with --project librarian returns cross-project entries ──
TESTS=$((TESTS + 1))
LIST_LIB_OUTPUT=$(python3 "$INTAKE_SCRIPT" list --project librarian 2>&1) || true
LIST_LIB_COUNT=$(echo "$LIST_LIB_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('evidence',[])))" 2>/dev/null || echo "0")
if [ "$LIST_LIB_COUNT" -ge 1 ]; then
    pass "List --project librarian returns $LIST_LIB_COUNT cross-project entry"
else
    fail "List --project librarian returned 0 entries"
fi

# ── Test 25: All responses include advisory_notice (sampled) ──
TESTS=$((TESTS + 1))
SAMPLE_OUTPUTS=$(python3 "$INTAKE_SCRIPT" list --limit 5 2>&1 && python3 "$INTAKE_SCRIPT" status 2>&1) || true
NOTICE_COUNT=$(echo "$SAMPLE_OUTPUTS" | grep -c "advisory_notice" 2>/dev/null || echo "0")
if [ "$NOTICE_COUNT" -ge 2 ]; then
    pass "Multiple responses include advisory_notice"
else
    fail "Less than 2 responses have advisory_notice: found $NOTICE_COUNT"
fi

cleanup

echo ""
echo "=================================================================="
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
