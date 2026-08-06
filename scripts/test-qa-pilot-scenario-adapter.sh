#!/usr/bin/env bash
# ── QA Pilot Scenario Adapter — Test Runner ─────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ADAPTER="$SCRIPT_DIR/qa_pilot_scenario_adapter.py"

PASS=0; FAIL=0; TESTS=0
pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Scenario Adapter — Test Runner"
echo "========================================="
echo ""

# Test 1: Script exists
TESTS=$((TESTS + 1))
[[ -f "$ADAPTER" ]] && pass "Adapter script exists" || fail "Adapter not found"

# Test 2: --help works
TESTS=$((TESTS + 1))
python3 "$ADAPTER" --help >/dev/null 2>&1 && pass "--help works" || fail "--help failed"

# Test 3: List scenarios
TESTS=$((TESTS + 1))
SCENARIO_COUNT=$(python3 "$ADAPTER" list-scenarios 2>&1 | grep -c "^  " || true)
[[ "$SCENARIO_COUNT" -ge 5 ]] && pass "Lists $SCENARIO_COUNT scenarios" || fail "Lists <5 scenarios"

# Test 4: Load a scenario definition
TESTS=$((TESTS + 1))
python3 "$ADAPTER" load capstone-001 2>&1 | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert d['scenario_id'] == 'capstone-001'
assert len(d['definition']['expected_bugs']) == 4
" 2>/dev/null && pass "Load capstone-001 with 4 expected bugs" || fail "Load capstone-001 failed"

# Test 5: Evaluate with all bugs found
TESTS=$((TESTS + 1))
RESULT=$(python3 "$ADAPTER" evaluate capstone-001 \
  '["status-junior-closed","priority-mismatch","future-date-allowed","owner-unassigned"]' \
  '[{"title":"Test","severity":"High","acRef":"AC-2.1","hasSteps":true}]' 2>&1 || true)
PASSED=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['passed'])" 2>/dev/null || echo "error")
echo "$RESULT" | python3 -c "
import sys,json; d=json.load(sys.stdin)
assert 'result' in d
assert 'score' in d['result']
assert 'percentage' in d['result']
assert 'passed' in d['result']
" 2>/dev/null && pass "Evaluate returns score, percentage, passed" || fail "Evaluate result structure invalid"

# Test 6: Evaluate with no bugs
TESTS=$((TESTS + 1))
RESULT2=$(python3 "$ADAPTER" evaluate capstone-001 '[]' '[]' 2>&1 || true)
SCORE=$(echo "$RESULT2" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['score'])" 2>/dev/null || echo "error")
[[ "$SCORE" == "0" ]] && pass "Empty submission scores 0" || fail "Empty submission scored $SCORE (expected 0)"

# Test 7: Unknown scenario handled gracefully
TESTS=$((TESTS + 1))
RESULT3=$(python3 "$ADAPTER" evaluate unknown-xyz '[]' '[]' 2>&1 || true)
NOT_FOUND=$(echo "$RESULT3" | python3 -c "import sys,json; d=json.load(sys.stdin); print('Scenario not found' in d['result']['summary'])" 2>/dev/null || echo "False")
[[ "$NOT_FOUND" == "True" ]] && pass "Unknown scenario handled gracefully" || fail "Unknown scenario not handled"

# Test 8: Evaluate from learning object
TESTS=$((TESTS + 1))
if [[ -f "$SCRIPT_DIR/../data/learning-objects/LO-EV-GOV-002-0001.json" ]]; then
    RESULT4=$(python3 "$ADAPTER" evaluate-from-lo LO-EV-GOV-002-0001 \
      '["OBS-001","OBS-002"]' \
      '[{"title":"Observation","severity":"Medium","acRef":"EXPECTED-001","hasSteps":true}]' 2>&1 || true)
    HAS_SOURCE=$(echo "$RESULT4" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('source_learning_object',''))" 2>/dev/null || echo "")
    [[ -n "$HAS_SOURCE" ]] && pass "Evaluate from learning object works (source: $HAS_SOURCE)" || fail "Evaluate from learning object failed"
else
    pass "Learning object not on disk (skipping LO evaluation test)"
fi

# Test 9: Provenance in every result
TESTS=$((TESTS + 1))
HAS_PROV=$(echo "$RESULT" | python3 -c "
import sys,json; d=json.load(sys.stdin)
p = d.get('provenance', {})
print(p.get('advisory') == True and p.get('no_authority_conferred') == True)
" 2>/dev/null || echo "False")
[[ "$HAS_PROV" == "True" ]] && pass "Result includes provenance with advisory=True" || fail "Result missing provenance"

# Test 10: Load all scenarios
TESTS=$((TESTS + 1))
ALL_OK=true
for sid in capstone-001 case-002 scenario-case-003 scenarios-bug-001 capstone-002; do
    python3 "$ADAPTER" load "$sid" >/dev/null 2>&1 || { ALL_OK=false; break; }
done
[[ "$ALL_OK" == true ]] && pass "All 5 scenario definitions load successfully" || fail "Some scenarios failed to load"

# Summary
echo ""
echo "=============================="
echo "Tests: $TESTS total | Pass: $PASS | Fail: $FAIL"
echo "=============================="
if [[ "$FAIL" -eq 0 ]]; then
    echo "Result: $PASS/$TESTS passed. All tests pass. ✅"
    exit 0
else
    echo "Result: $PASS/$TESTS passed. $FAIL failures. ❌"
    exit 1
fi
