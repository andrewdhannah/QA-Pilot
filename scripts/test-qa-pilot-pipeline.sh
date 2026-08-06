#!/usr/bin/env bash
# ── QA Pilot Continuous Validation Pipeline — Test Runner ──────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE="$SCRIPT_DIR/qa-pilot-pipeline.sh"

PASS=0; FAIL=0; TESTS=0
pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Continuous Pipeline — Test Runner"
echo "============================================="
echo ""

# Test 1: Script exists
TESTS=$((TESTS + 1))
[[ -f "$PIPELINE" ]] && pass "Pipeline script exists" || fail "Not found"

# Test 2: --help works
TESTS=$((TESTS + 1))
$PIPELINE --help 2>&1 | grep -q "Usage" && pass "--help shows usage" || fail "--help not handled"

# Test 3: --list-domains
TESTS=$((TESTS + 1))
DOMAIN_COUNT=$($PIPELINE --list-domains 2>&1 | grep -c "^  " || true)
[[ "$DOMAIN_COUNT" -ge 5 ]] && pass "Lists $DOMAIN_COUNT domains (expected >=5)" || fail "Expected >=5 domains, got $DOMAIN_COUNT"

# Test 4: --quick mode
TESTS=$((TESTS + 1))
QUICK_OUTPUT=$($PIPELINE --quick 2>&1 || true)
echo "$QUICK_OUTPUT" | grep -q "QUICK" && pass "Quick mode executes" || fail "Quick mode failed"

# Test 5: --status after quick run
TESTS=$((TESTS + 1))
STATUS_OUTPUT=$($PIPELINE --status 2>&1 || true)
echo "$STATUS_OUTPUT" | grep -q "Run ID" && pass "Status shows run data" || fail "Status empty"

# Test 6: Selected domains
TESTS=$((TESTS + 1))
SELECTED_OUTPUT=$($PIPELINE --domains regression,security 2>&1 || true)
echo "$SELECTED_OUTPUT" | grep -q "regression" && pass "Selected domains run correctly" || fail "Selected domains failed"

# Test 7: Pipeline produces result JSON
TESTS=$((TESTS + 1))
LAST_RUN=$(cat "$(dirname "$SCRIPT_DIR")/data/pipeline/last-run.json" 2>/dev/null || echo "{}")
echo "$LAST_RUN" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d.get('pipeline_version') == 'qa-pilot-continuous-pipeline-v1'
assert d.get('overall') in ('PASS', 'REVIEW', 'DEGRADED')
assert d.get('tests_executed', 0) >= 0
assert d.get('provenance', {}).get('advisory') == True
" 2>/dev/null && pass "Pipeline result JSON valid" || fail "Pipeline result invalid"

# Test 8: No authority in pipeline results
TESTS=$((TESTS + 1))
echo "$LAST_RUN" | python3 -c "
import sys, json
d = json.load(sys.stdin)
p = d.get('provenance', {})
assert p.get('no_authority_conferred') == True
assert p.get('does_not_approve_releases') == True
" 2>/dev/null && pass "Pipeline result preserves no_authority_conferred" || fail "Pipeline authority invariant broken"

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
