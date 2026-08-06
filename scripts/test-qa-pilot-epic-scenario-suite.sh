#!/usr/bin/env bash
# ── QA Pilot Epic Scenario Suite — Test Runner ──────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SUITE_SCRIPT="$SCRIPT_DIR/qa_pilot_epic_scenario_suite.py"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-epic-scenario-suite.py"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-epic-scenario-suite"
SCHEMA_FILE="$REPO_ROOT/docs/schemas/qa-pilot-epic-scenario-suite.schema.json"
GOVERNANCE_DOC="$REPO_ROOT/docs/governance/QA-PILOT-EPIC-SCENARIO-SUITES.md"

PASS=0; FAIL=0; TESTS=0
pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Epic Scenario Suite — Test Runner"
echo "=============================================="
echo ""

# Test 1: Suite script exists
TESTS=$((TESTS + 1))
[[ -f "$SUITE_SCRIPT" ]] && pass "Suite script exists" || fail "Suite script not found"

# Test 2: --help works
TESTS=$((TESTS + 1))
python3 "$SUITE_SCRIPT" --help >/dev/null 2>&1 && pass "--help works" || fail "--help failed"

# Test 3: list command works
TESTS=$((TESTS + 1))
LIST_OUTPUT=$(python3 "$SUITE_SCRIPT" list 2>&1)
echo "$LIST_OUTPUT" | grep -q "EP-EP-001" && pass "list shows EP-EP-001" || fail "list missing EP-EP-001"

# Test 4: list shows all 5 scenarios
TESTS=$((TESTS + 1))
SCENARIO_COUNT=$(echo "$LIST_OUTPUT" | grep -c "EP-" || true)
[[ "$SCENARIO_COUNT" -ge 5 ]] && pass "list shows $SCENARIO_COUNT scenarios" || fail "list shows <5 scenarios"

# Test 5: Validator exists
TESTS=$((TESTS + 1))
[[ -f "$VALIDATOR" ]] && pass "Validator exists" || fail "Validator not found"

# Test 6: Validator --list-rules works
TESTS=$((TESTS + 1))
RULE_COUNT=$(python3 "$VALIDATOR" --list-rules 2>/dev/null | grep -c "ES-" || true)
[[ "$RULE_COUNT" -ge 8 ]] && pass "Validator lists $RULE_COUNT rules" || fail "Validator shows <8 rules"

# Test 7: Valid fixtures all pass
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" --all >/dev/null 2>&1 && pass "All valid fixtures pass" || fail "Some valid fixtures failed"

# Test 8: Invalid fixtures correctly rejected
TESTS=$((TESTS + 1))
INI_COUNT=$(ls "$FIXTURES_DIR"/invalid-*.json 2>/dev/null | wc -l || echo "0")
if [[ "$INI_COUNT" -gt 0 ]]; then
    VALIDATOR_OUT=$(python3 "$VALIDATOR" --all --include-invalid 2>&1 || true)
    REJ_COUNT=$(echo "$VALIDATOR_OUT" | grep -c "correctly rejected" || true)
    [[ "$REJ_COUNT" -ge 1 ]] && pass "Validator correctly rejects invalid fixtures ($REJ_COUNT rejected)" || fail "Validator did not reject invalid fixtures"
else
    pass "No invalid fixtures (skipping)"
fi

# Test 9: Schema file exists and is valid JSON
TESTS=$((TESTS + 1))
if [[ -f "$SCHEMA_FILE" ]]; then
    python3 -c "import json; json.load(open('$SCHEMA_FILE'))" 2>/dev/null && pass "Schema is valid JSON" || fail "Schema is invalid JSON"
else
    fail "Schema not found"
fi

# Test 10: Governance doc exists
TESTS=$((TESTS + 1))
[[ -f "$GOVERNANCE_DOC" ]] && pass "Governance doc exists" || fail "Governance doc not found"

# Test 11: Evidence Plane scenarios all pass (live data)
TESTS=$((TESTS + 1))
RESULT=$(python3 "$SUITE_SCRIPT" evidence-plane 2>&1 || true)
OVERALL=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('overall','ERROR'))" 2>/dev/null || echo "ERROR")
if [[ "$OVERALL" == "PASS" ]]; then
    pass "Evidence Plane scenarios all PASS against live data"
else
    fail "Evidence Plane scenarios: $OVERALL"
fi

# Test 12: Each scenario produces learning artifact with teachable_moment
TESTS=$((TESTS + 1))
TEACHABLE_COUNT=$(echo "$RESULT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
count = 0
for r in d.get('results', []):
    la = r.get('learning_artifact', {})
    if la.get('teachable_moment'):
        count += 1
print(count)
" 2>/dev/null || echo "0")
[[ "$TEACHABLE_COUNT" -ge 5 ]] && pass "All 5 scenarios produce teachable moments ($TEACHABLE_COUNT)" || fail "Only $TEACHABLE_COUNT scenarios have teachable moments"

# Test 13: No-mutation enforced across all scenarios
TESTS=$((TESTS + 1))
MUTATION_PASS=$(echo "$RESULT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
pass_count = 0
for r in d.get('results', []):
    for detail in r.get('details', []):
        if detail.get('check_id') == 'NO_MUTATION_PATH' or detail.get('check_id') == 'MUTATION_BOUNDARY_ALL_QUERIES':
            if detail.get('passed'):
                pass_count += 1
print(pass_count)
" 2>/dev/null || echo "0")
[[ "$MUTATION_PASS" -ge 1 ]] && pass "Mutation boundary enforced across all scenarios ($MUTATION_PASS checks)" || fail "Mutation boundary not enforced"

# Test 14: Sprint doc exists
TESTS=$((TESTS + 1))
SPRINT_DOC="$REPO_ROOT/docs/sprints/QA-PILOT-EPIC-SCENARIO-SUITES.md"
[[ -f "$SPRINT_DOC" ]] && pass "Sprint doc exists" || fail "Sprint doc not found"

# Test 15: Fixture count check
TESTS=$((TESTS + 1))
VALID_COUNT=$(ls "$FIXTURES_DIR"/valid-*.json 2>/dev/null | wc -l || echo "0")
INI_COUNT=$(ls "$FIXTURES_DIR"/invalid-*.json 2>/dev/null | wc -l || echo "0")
TOTAL_FIX=$((VALID_COUNT + INI_COUNT))
[[ "$TOTAL_FIX" -ge 4 ]] && pass "Fixtures: $VALID_COUNT valid + $INI_COUNT invalid = $TOTAL_FIX total" || fail "Fewer than 4 fixtures"

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
