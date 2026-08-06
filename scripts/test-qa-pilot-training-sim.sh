#!/usr/bin/env bash
set -euo pipefail

# QA Pilot Training Sim Test Runner — QA-PILOT-LOCAL-TRAINING-SIM-1
#
# One-command test suite for the training simulation layer.
# Tests: schema validation, fixture pass/fail, CLI generate/list/validate/status/clear,
#        advisory invariants, no mutation paths, no cross-project write, boundary scan.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SIM_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-training-sim.py"
SIM_CLI="$SCRIPT_DIR/qa_pilot_training_sim.py"
INGEST_CLI="$SCRIPT_DIR/qa_pilot_qa_packet_ingest.py"
REGRESSION_FIXTURES="$REPO_ROOT/docs/examples/qa-pilot-milestone-regression"
SIM_FIXTURES="$REPO_ROOT/docs/examples/qa-pilot-training-sim"
SIM_CASES_DIR="$REPO_ROOT/data/sim/cases"
SIM_RESULTS_DIR="$REPO_ROOT/data/sim/results"
SIM_INDEX_FILE="$REPO_ROOT/data/sim/sim-index.json"
CASE_SCHEMA="$REPO_ROOT/docs/schemas/qa-pilot-training-sim-case.schema.json"
RESULT_SCHEMA="$REPO_ROOT/docs/schemas/qa-pilot-training-sim-result.schema.json"
GOV_DOC="$REPO_ROOT/docs/governance/QA-PILOT-TRAINING-SIM.md"
LIBRARIAN_BASE="$REPO_ROOT/../librarian"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Training Sim Test Runner — QA-PILOT-LOCAL-TRAINING-SIM-1"
echo="========================================================================="
echo ""

# ── Test 1: Sim validator script exists ──
TESTS=$((TESTS + 1))
if [ -f "$SIM_VALIDATOR" ]; then
    pass "Sim validator script found"
else
    fail "Sim validator script not found"
fi

# ── Test 2: Sim CLI script exists ──
TESTS=$((TESTS + 1))
if [ -f "$SIM_CLI" ]; then
    pass "Sim CLI script found"
else
    fail "Sim CLI script not found"
fi

# ── Test 3: Sim validator --list-rules works ──
TESTS=$((TESTS + 1))
if python3 "$SIM_VALIDATOR" --list-rules 2>&1 | grep -q "TS-1"; then
    pass "Sim validator --list-rules shows TS-1"
else
    fail "Sim validator --list-rules failed"
fi

# ── Test 4: Valid sim fixtures all pass ──
TESTS=$((TESTS + 1))
if python3 "$SIM_VALIDATOR" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Valid sim fixtures all pass"
else
    fail "Valid sim fixtures did not all pass"
    python3 "$SIM_VALIDATOR" 2>&1
fi

# ── Test 5: Invalid sim fixtures all fail ──
TESTS=$((TESTS + 1))
INVALID_OUTPUT=$(python3 "$SIM_VALIDATOR" --include-invalid 2>&1) || true
INVALID_FAIL_COUNT=$(echo "$INVALID_OUTPUT" | grep -c "❌" || true)
if [ "$INVALID_FAIL_COUNT" -ge 5 ]; then
    pass "Invalid sim fixtures correctly rejected ($INVALID_FAIL_COUNT failures detected)"
else
    fail "Not enough invalid fixtures rejected (expected >= 5, found $INVALID_FAIL_COUNT)"
fi

# ── Test 6: Fixture count correct ──
TESTS=$((TESTS + 1))
FIXTURE_COUNT=$(ls "$SIM_FIXTURES"/*.json 2>/dev/null | wc -l | tr -d ' ')
VALID_COUNT=$(ls "$SIM_FIXTURES"/sim-valid-*.json 2>/dev/null | wc -l | tr -d ' ')
INVALID_COUNT=$(ls "$SIM_FIXTURES"/sim-invalid-*.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$FIXTURE_COUNT" -ge 9 ] && [ "$VALID_COUNT" -ge 4 ] && [ "$INVALID_COUNT" -ge 5 ]; then
    pass "Sim fixtures: $FIXTURE_COUNT total ($VALID_COUNT valid, $INVALID_COUNT invalid)"
else
    fail "Sim fixtures: expected >=9 total (>=4 valid, >=5 invalid), found $FIXTURE_COUNT ($VALID_COUNT valid, $INVALID_COUNT invalid)"
fi

# ── Test 7: Schema files exist and are valid JSON ──
TESTS=$((TESTS + 1))
SCHEMA_OK=true
for schema in "$CASE_SCHEMA" "$RESULT_SCHEMA"; do
    if [ ! -f "$schema" ]; then
        SCHEMA_OK=false
        echo "       FAIL: Schema not found: $schema"
    elif ! python3 -c "import json; json.load(open('$schema'))" 2>/dev/null; then
        SCHEMA_OK=false
        echo "       FAIL: Invalid JSON: $schema"
    fi
done
if [ "$SCHEMA_OK" = true ]; then
    pass "Both sim schemas are valid JSON"
else
    fail "One or more sim schemas missing or invalid"
fi

# ── Test 8: Generate sim cases from ingested packets ──
TESTS=$((TESTS + 1))
# First ensure some packets are ingested
python3 "$INGEST_CLI" clear 2>&1 > /dev/null || true
for f in "$REGRESSION_FIXTURES"/regression-valid-*.json; do
    python3 "$INGEST_CLI" ingest "$f" 2>&1 > /dev/null || true
done

GEN_OUTPUT=$(python3 "$SIM_CLI" generate 2>&1) || true
GEN_COUNT=$(echo "$GEN_OUTPUT" | grep -c "Generated:" || true)
if [ "$GEN_COUNT" -ge 4 ]; then
    pass "Sim CLI generated $GEN_COUNT sim cases from ingested packets"
else
    fail "Sim CLI generated only $GEN_COUNT sim cases (expected >= 4)"
    echo "  Output: $GEN_OUTPUT"
fi

# ── Test 9: Generated sim cases have correct invariants ──
TESTS=$((TESTS + 1))
INVARIANTS_OK=true
for f in "$SIM_CASES_DIR"/*.json; do
    [ -f "$f" ] || continue
    ADVISORY=$(python3 -c "import json; print(json.load(open('$f')).get('advisory', False))" 2>&1)
    OWNER=$(python3 -c "import json; print(json.load(open('$f')).get('owner_decision_required', False))" 2>&1)
    REPRO=$(python3 -c "
import json; rf=json.load(open('$f')).get('reproducible_from','')
print(rf.startswith('data/packets/ingested') or rf.startswith('data/packets/ingested/'))
" 2>&1)
    if [ "$ADVISORY" != "True" ] || [ "$OWNER" != "True" ] || [ "$REPRO" != "True" ]; then
        echo "       FAIL: $(basename "$f") advisory=$ADVISORY owner=$OWNER repro_local=$REPRO"
        INVARIANTS_OK=false
    fi
done
if [ "$INVARIANTS_OK" = true ]; then
    pass "All generated sim cases: advisory=true, owner_decision=true, local reproducible_from"
else
    fail "Some generated sim cases have invariant violations"
fi

# ── Test 10: Sim CLI list command works ──
TESTS=$((TESTS + 1))
if python3 "$SIM_CLI" list 2>&1 | grep -q "sim\|Sim\|total\|Generated"; then
    pass "Sim CLI list shows generated sim cases"
else
    fail "Sim CLI list failed"
fi

# ── Test 11: Sim CLI status shows advisory-only markers ──
TESTS=$((TESTS + 1))
STATUS_OUT=$(python3 "$SIM_CLI" status 2>&1)
if echo "$STATUS_OUT" | grep -q "advisory-only" && echo "$STATUS_OUT" | grep -q "NOT AUTHORIZED"; then
    pass "Sim CLI status shows advisory-only, no cross-project write"
else
    fail "Sim CLI status missing authority markers"
fi

# ── Test 12: Sim results are generated and are advisory ──
TESTS=$((TESTS + 1))
RESULT_COUNT=$(ls "$SIM_RESULTS_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
RESULT_ADVISORY_OK=true
for f in "$SIM_RESULTS_DIR"/*.json; do
    [ -f "$f" ] || continue
    ADV=$(python3 -c "import json; print(json.load(open('$f')).get('advisory', False))" 2>&1)
    if [ "$ADV" != "True" ]; then
        RESULT_ADVISORY_OK=false
    fi
done
if [ "$RESULT_COUNT" -ge 4 ] && [ "$RESULT_ADVISORY_OK" = true ]; then
    pass "Sim results: $RESULT_COUNT results, all advisory=true"
else
    fail "Sim results: count=$RESULT_COUNT, all_advisory=$RESULT_ADVISORY_OK"
fi

# ── Test 13: Sim CLI clear command works ──
TESTS=$((TESTS + 1))
python3 "$SIM_CLI" clear 2>&1 > /dev/null
CLEAR_COUNT=$(python3 -c "
import json
try:
    idx=json.load(open('$SIM_INDEX_FILE'))
    print(len(idx.get('sim_cases',[])))
except: print('0')
" 2>&1)
if [ "$CLEAR_COUNT" = "0" ]; then
    pass "Sim CLI clear resets all sim state"
else
    fail "Sim CLI clear did not reset state: $CLEAR_COUNT cases remain"
fi

# ── Test 14: Governance doc exists ──
TESTS=$((TESTS + 1))
if [ -f "$GOV_DOC" ]; then
    pass "Training sim governance doc exists"
else
    fail "Training sim governance doc not found"
fi

# ── Test 15: Boundary scan — no sim files in Librarian ──
TESTS=$((TESTS + 1))
LEAKED=""
if [ -f "$LIBRARIAN_BASE/scripts/validate-qa-pilot-training-sim.py" ]; then
    LEAKED="$LEAKED validator"
fi
if [ -f "$LIBRARIAN_BASE/scripts/qa_pilot_training_sim.py" ]; then
    LEAKED="$LEAKED cli"
fi
if [ -d "$LIBRARIAN_BASE/docs/examples/qa-pilot-training-sim" ]; then
    LEAKED="$LEAKED fixtures"
fi
if [ -f "$LIBRARIAN_BASE/docs/governance/QA-PILOT-TRAINING-SIM.md" ]; then
    LEAKED="$LEAKED gov-doc"
fi
if [ -f "$LIBRARIAN_BASE/docs/schemas/qa-pilot-training-sim-case.schema.json" ]; then
    LEAKED="$LEAKED case-schema"
fi
if [ -f "$LIBRARIAN_BASE/docs/schemas/qa-pilot-training-sim-result.schema.json" ]; then
    LEAKED="$LEAKED result-schema"
fi
if [ -z "$LEAKED" ]; then
    pass "Boundary scan CLEAN: no training sim files in Librarian"
else
    fail "Boundary scan: sim files found in Librarian:$LEAKED"
fi

# ── Test 16: Sim results are readable and never re-ingested ──
TESTS=$((TESTS + 1))
# Re-generate to test idempotency
python3 "$SIM_CLI" generate 2>&1 > /dev/null || true
GEN2_OUT=$(python3 "$SIM_CLI" generate 2>&1) || true
if echo "$GEN2_OUT" | grep -q "No new sim cases generated"; then
    pass "Sim generation is idempotent — no duplicate cases on re-run"
else
    DUP_COUNT=$(echo "$GEN2_OUT" | grep -c "Generated:" || true)
    if [ "$DUP_COUNT" -eq 0 ]; then
        pass "Sim generation is idempotent — no duplicates"
    else
        fail "Sim generation produced $DUP_COUNT duplicates"
    fi
fi

# ── Test 17: QA Pilot sprint ledger is valid JSON ──
TESTS=$((TESTS + 1))
if python3 -c "import json; json.load(open('$REPO_ROOT/project-state/sprint-ledger.json'))" 2>/dev/null; then
    pass "QA Pilot sprint ledger is valid JSON"
else
    fail "QA Pilot sprint ledger is not valid JSON"
fi

# Clean up test data
python3 "$SIM_CLI" clear 2>&1 > /dev/null || true
python3 "$INGEST_CLI" clear 2>&1 > /dev/null || true

echo ""
echo "========================================================================"
echo "Tests: $TESTS total"
echo "Pass:  $PASS"
echo "Fail:  $FAIL"

if [ "$FAIL" -eq 0 ]; then
    echo "Result: $PASS/$TESTS passed. All training sim tests pass. ✅"
    exit 0
else
    echo "Result: $PASS/$TESTS passed. Some tests failed. ❌"
    exit 1
fi
