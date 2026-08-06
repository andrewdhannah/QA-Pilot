#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIAG_SCRIPT="$SCRIPT_DIR/qa_pilot_pipeline_recovery_diagnostics.py"
DIAG_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-pipeline-recovery-diagnostics.py"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-pipeline-recovery-diagnostics"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Pipeline Recovery Diagnostics Tests — QA-PILOT-PIPELINE-RECOVERY-DIAGNOSTICS-1"
echo "========================================================================================="
echo ""

# ── Test 1: Script exists ──
TESTS=$((TESTS + 1))
if [ -f "$DIAG_SCRIPT" ]; then
    pass "Diagnostics script found"
else
    fail "Not found"
fi

# ── Test 2: Validator passes ──
TESTS=$((TESTS + 1))
VOUT=$(python3 "$DIAG_VALIDATOR" 2>&1) || true
if echo "$VOUT" | grep -q "ALL CHECKS PASS"; then
    pass "Validator ALL CHECKS PASS"
else
    fail "Validator failed"
    echo "       $(echo "$VOUT" | tail -5)"
fi

# ── Test 3: JSON mode — advisory=true ──
TESTS=$((TESTS + 1))
JOUT=$(python3 "$DIAG_SCRIPT" 2>&1) || true
ADVISORY=$(echo "$JOUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('advisory', False))" 2>/dev/null || echo "false")
if [ "$ADVISORY" = "True" ]; then
    pass "JSON output: advisory=True"
else
    fail "JSON output: advisory missing"
fi

# ── Test 4: JSON has pipeline_layers ──
TESTS=$((TESTS + 1))
LAYERS=$(echo "$JOUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('pipeline_layers',{})))" 2>/dev/null || echo "0")
if [ "$LAYERS" -ge 7 ]; then
    pass "JSON has $LAYERS pipeline layers"
else
    fail "JSON has < 7 layers"
fi

# ── Test 5: JSON has summary ──
TESTS=$((TESTS + 1))
HAS_SUMMARY=$(echo "$JOUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('drifts' in d.get('summary',{}))" 2>/dev/null || echo "False")
if [ "$HAS_SUMMARY" = "True" ]; then
    pass "JSON includes drift summary"
else
    fail "JSON missing summary"
fi

# ── Test 6: JSON has findings ──
TESTS=$((TESTS + 1))
FINDINGS=$(echo "$JOUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('findings',[])))" 2>/dev/null || echo "0")
if [ "$FINDINGS" -ge 10 ]; then
    pass "JSON has $FINDINGS findings (10 DR checks)"
else
    fail "JSON has < 10 findings"
fi

# ── Test 7: Report mode produces formatted output ──
TESTS=$((TESTS + 1))
ROUT=$(python3 "$DIAG_SCRIPT" --report 2>&1) || true
if echo "$ROUT" | grep -q "Recovery Diagnostics"; then
    pass "Report mode generates diagnostics report"
else
    fail "Report mode failed"
fi

# ── Test 8: Report shows pipeline layers ──
TESTS=$((TESTS + 1))
if echo "$ROUT" | grep -q "Pipeline Layers"; then
    pass "Report shows pipeline layers"
else
    fail "Report missing pipeline layers"
fi

# ── Test 9: Report shows advisory notice ──
TESTS=$((TESTS + 1))
if echo "$ROUT" | grep -qi "advisory"; then
    pass "Report includes advisory notice"
else
    fail "Report missing advisory notice"
fi

# ── Test 10: Report shows custody ──
TESTS=$((TESTS + 1))
if echo "$ROUT" | grep -q "qa-pilot-local"; then
    pass "Report shows custody=qa-pilot-local"
else
    fail "Report missing custody"
fi

# ── Test 11: Report shows PH validator status ──
TESTS=$((TESTS + 1))
if echo "$ROUT" | grep -q "PH Validator"; then
    pass "Report shows PH validator status"
else
    fail "Report missing PH validator"
fi

# ── Test 12: Finding has cause classification ──
TESTS=$((TESTS + 1))
HAS_CAUSE=$(echo "$JOUT" | python3 -c "
import sys,json
d=json.load(sys.stdin)
for f in d.get('findings',[]):
    if 'cause' not in f:
        print('False')
        break
else:
    print('True')
" 2>/dev/null || echo "False")
if [ "$HAS_CAUSE" = "True" ]; then
    pass "Findings include cause classification"
else
    fail "Findings missing cause"
fi

# ── Test 13: No auto-repair in response ──
TESTS=$((TESTS + 1))
AUTO_REPAIR=$(echo "$JOUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('auto_repair', False))" 2>/dev/null || echo "true")
if [ "$AUTO_REPAIR" = "False" ]; then
    pass "No auto-repair in diagnostic output"
else
    fail "Auto-repair should be False/absent"
fi

# ── Test 14: Valid fixture validation via script ──
TESTS=$((TESTS + 1))
FIXT_OUT=$(python3 "$DIAG_SCRIPT" --fixture "$FIXTURES_DIR/valid-no-drift.json" 2>&1) || true
if echo "$FIXT_OUT" | grep -q "ALL FIXTURE CHECKS PASS"; then
    pass "Valid fixture passes"
else
    fail "Valid fixture failed"
fi

echo ""
echo "========================================================================================="
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
