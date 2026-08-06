#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SURFACE_SCRIPT="$SCRIPT_DIR/qa_pilot_pipeline_startup_surface.py"
SURFACE_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-epic-regression-startup-surface.py"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-epic-regression-startup-surface"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Pipeline Startup Surface Tests — QA-PILOT-EPIC-REGRESSION-STARTUP-SURFACE-1"
echo "===================================================================================="
echo ""

# ── Test 1: Script exists ──
TESTS=$((TESTS + 1))
if [ -f "$SURFACE_SCRIPT" ]; then
    pass "Surface script found"
else
    fail "Not found"
fi

# ── Test 2: Validator passes ──
TESTS=$((TESTS + 1))
VOUT=$(python3 "$SURFACE_VALIDATOR" 2>&1) || true
if echo "$VOUT" | grep -q "ALL CHECKS PASS"; then
    pass "Validator ALL CHECKS PASS"
else
    fail "Validator failed"
    echo "       $(echo "$VOUT" | tail -5)"
fi

# ── Test 3: Report text mode shows pipeline ──
TESTS=$((TESTS + 1))
ROUT=$(python3 "$SURFACE_SCRIPT" report 2>&1) || true
if echo "$ROUT" | grep -q "Sealed head"; then
    pass "Report shows Sealed head"
else
    fail "Report missing Sealed head"
fi

# ── Test 4: Report shows pipeline layer references ──
TESTS=$((TESTS + 1))
# Use verbose to get layer details
VROUT=$(python3 "$SURFACE_SCRIPT" report -v 2>&1) || true
LAYER_COUNT=$(echo "$VROUT" | grep -cE "(EP-|TC-|QR-|ERS-)" 2>/dev/null || echo "0")
if [ "$LAYER_COUNT" -ge 4 ]; then
    pass "Verbose report shows $LAYER_COUNT layer references"
else
    fail "Verbose report shows < 4 layers"
fi

# ── Test 5: Report shows advisory-only ──
TESTS=$((TESTS + 1))
if echo "$ROUT" | grep -qi "advisory"; then
    pass "Report includes advisory posture"
else
    fail "Report missing advisory"
fi

# ── Test 6: Report shows zero Librarian mutation ──
TESTS=$((TESTS + 1))
if echo "$ROUT" | grep -q "NONE"; then
    pass "Report shows Librarian mutation: NONE"
else
    fail "Report missing Librarian mutation statement"
fi

# ── Test 7: Report verbose shows packet counts ──
TESTS=$((TESTS + 1))
VROUT=$(python3 "$SURFACE_SCRIPT" report -v 2>&1) || true
if echo "$VROUT" | grep -q "Evidence packets\|Test cases\|Result packets\|Epic suites"; then
    pass "Verbose report shows packet counts"
else
    fail "Verbose report missing packet counts"
fi

# ── Test 8: JSON format works ──
TESTS=$((TESTS + 1))
JSON_OUT=$(python3 "$SURFACE_SCRIPT" report --format json 2>&1) || true
JSON_VALID=$(echo "$JSON_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('advisory_only', False))" 2>/dev/null || echo "false")
if [ "$JSON_VALID" = "True" ]; then
    pass "JSON report valid with advisory_only=True"
else
    fail "JSON report invalid"
fi

# ── Test 9: Status command works ──
TESTS=$((TESTS + 1))
SOUT=$(python3 "$SURFACE_SCRIPT" status 2>&1) || true
if echo "$SOUT" | grep -qi "pipeline" && echo "$SOUT" | grep -qi "advisory"; then
    pass "Status shows pipeline and advisory"
else
    fail "Status missing pipeline info"
fi

# ── Test 10: Validate command passes live ──
TESTS=$((TESTS + 1))
VAL_OUT=$(python3 "$SURFACE_SCRIPT" validate 2>&1) || true
if echo "$VAL_OUT" | grep -q "ALL STARTUP SURFACE CHECKS PASS"; then
    pass "Live validate passes"
else
    fail "Live validate failed"
    echo "       $VAL_OUT"
fi

# ── Test 11: Validate valid fixture passes ──
TESTS=$((TESTS + 1))
FIXX_OUT=$(python3 "$SURFACE_SCRIPT" validate --input "$FIXTURES_DIR/valid-pipeline-report.json" 2>&1) || true
if echo "$FIXX_OUT" | grep -q "ALL STARTUP SURFACE CHECKS PASS"; then
    pass "Validate valid fixture passes"
else
    fail "Validate valid fixture failed"
fi

# ── Test 12: Report includes custody boundary ──
TESTS=$((TESTS + 1))
if echo "$ROUT" | grep -q "qa-pilot-local"; then
    pass "Report shows custody=qa-pilot-local"
else
    fail "Report missing custody"
fi

# ── Test 13: Report shows next authorized sprint ──
TESTS=$((TESTS + 1))
if echo "$ROUT" | grep -q "Next authorized"; then
    pass "Report shows next authorized sprint"
else
    fail "Report missing next authorized"
fi

# ── Test 14: Report shows active sprint ──
TESTS=$((TESTS + 1))
if echo "$ROUT" | grep -q "Active sprint"; then
    pass "Report shows active sprint"
else
    fail "Report missing active sprint"
fi

# ── Test 15: Status shows DS line ──
TESTS=$((TESTS + 1))
SOUT_DS=$(python3 "$SURFACE_SCRIPT" status 2>&1) || true
if echo "$SOUT_DS" | grep -q "DS:"; then
    pass "Status shows DS posture"
else
    fail "Status missing DS posture"
fi

# ── Test 16: Validate passes DS-SS rules ──
TESTS=$((TESTS + 1))
VAL_DS=$(python3 "$SURFACE_SCRIPT" validate 2>&1) || true
DS_COUNT=$(echo "$VAL_DS" | grep -c "DS-SS-" 2>/dev/null || echo "0")
DS_PASS=$(echo "$VAL_DS" | grep -c "✅ DS-SS-" 2>/dev/null || echo "0")
if [ "$DS_COUNT" -gt 0 ] && [ "$DS_COUNT" -eq "$DS_PASS" ]; then
    pass "All DS-SS rules pass ($DS_PASS/$DS_COUNT)"
else
    fail "DS-SS rules: $DS_PASS/$DS_COUNT pass"
fi

# ── Test 17: Report includes Decision Summaries section ──
ROUT_17=$(python3 "$SURFACE_SCRIPT" report 2>&1) || true
TESTS=$((TESTS + 1))
if echo "$ROUT_17" | grep -q "Decision Summaries"; then
    pass "Report shows Decision Summaries section"
else
    fail "Report missing Decision Summaries section"
fi

# ── Test 18: Status shows WDR line ──
TESTS=$((TESTS + 1))
SOUT_WDR=$(python3 "$SURFACE_SCRIPT" status 2>&1) || true
if echo "$SOUT_WDR" | grep -q "WDR:"; then
    pass "Status shows WDR posture"
else
    fail "Status missing WDR posture"
fi

# ── Test 19: Validate passes WDR-SS rules ──
TESTS=$((TESTS + 1))
VAL_WDR=$(python3 "$SURFACE_SCRIPT" validate 2>&1) || true
WDR_COUNT=$(echo "$VAL_WDR" | grep -c "WDR-SS-" 2>/dev/null || echo "0")
WDR_PASS=$(echo "$VAL_WDR" | grep -c "✅ WDR-SS-" 2>/dev/null || echo "0")
if [ "$WDR_COUNT" -gt 0 ] && [ "$WDR_COUNT" -eq "$WDR_PASS" ]; then
    pass "All WDR-SS rules pass ($WDR_PASS/$WDR_COUNT)"
else
    fail "WDR-SS rules: $WDR_PASS/$WDR_COUNT pass"
fi

# ── Test 20: Report includes Review Decision Receipts section ──
TESTS=$((TESTS + 1))
ROUT_20=$(python3 "$SURFACE_SCRIPT" report 2>&1) || true
TESTS=$((TESTS + 1))
if echo "$ROUT_20" | grep -q "Review Decision Receipts"; then
    pass "Report shows Review Decision Receipts section"
else
    fail "Report missing Review Decision Receipts section"
fi

# ── Test 21: Status shows AP line ──
TESTS=$((TESTS + 1))
SOUT_AP=$(python3 "$SURFACE_SCRIPT" status 2>&1) || true
if echo "$SOUT_AP" | grep -q "AP:"; then
    pass "Status shows AP posture"
else
    fail "Status missing AP posture"
fi

# ── Test 22: Validate passes AP-SS rules ──
TESTS=$((TESTS + 1))
VAL_AP=$(python3 "$SURFACE_SCRIPT" validate 2>&1) || true
AP_COUNT=$(echo "$VAL_AP" | grep -c "AP-SS-" 2>/dev/null || echo "0")
AP_PASS=$(echo "$VAL_AP" | grep -c "✅ AP-SS-" 2>/dev/null || echo "0")
if [ "$AP_COUNT" -gt 0 ] && [ "$AP_COUNT" -eq "$AP_PASS" ]; then
    pass "All AP-SS rules pass ($AP_PASS/$AP_COUNT)"
else
    fail "AP-SS rules: $AP_PASS/$AP_COUNT pass"
fi

# ── Test 23: Report includes Owner Action Packets section ──
TESTS=$((TESTS + 1))
ROUT_23=$(python3 "$SURFACE_SCRIPT" report 2>&1) || true
TESTS=$((TESTS + 1))
if echo "$ROUT_23" | grep -q "Owner Action Packets"; then
    pass "Report shows Owner Action Packets section"
else
    fail "Report missing Owner Action Packets section"
fi

# ── Test 24: Status shows AXP line ──
TESTS=$((TESTS + 1))
SOUT_AXP=$(python3 "$SURFACE_SCRIPT" status 2>&1) || true
if echo "$SOUT_AXP" | grep -q "AXP:"; then
    pass "Status shows AXP posture"
else
    fail "Status missing AXP posture"
fi

# ── Test 25: Validate passes AXP-SS rules ──
TESTS=$((TESTS + 1))
VAL_AXP=$(python3 "$SURFACE_SCRIPT" validate 2>&1) || true
AXP_COUNT=$(echo "$VAL_AXP" | grep -c "AXP-SS-" 2>/dev/null || echo "0")
AXP_PASS=$(echo "$VAL_AXP" | grep -c "✅ AXP-SS-" 2>/dev/null || echo "0")
if [ "$AXP_COUNT" -gt 0 ] && [ "$AXP_COUNT" -eq "$AXP_PASS" ]; then
    pass "All AXP-SS rules pass ($AXP_PASS/$AXP_COUNT)"
else
    fail "AXP-SS rules: $AXP_PASS/$AXP_COUNT pass"
fi

# ── Test 26: Report includes Action Packet Exports section ──
TESTS=$((TESTS + 1))
ROUT_26=$(python3 "$SURFACE_SCRIPT" report 2>&1) || true
TESTS=$((TESTS + 1))
if echo "$ROUT_26" | grep -q "Action Packet Exports"; then
    pass "Report shows Action Packet Exports section"
else
    fail "Report missing Action Packet Exports section"
fi

# ── Test 27: Status shows HI line ──
TESTS=$((TESTS + 1))
SOUT_HI=$(python3 "$SURFACE_SCRIPT" status 2>&1) || true
if echo "$SOUT_HI" | grep -q "HI:"; then
    pass "Status shows HI posture"
else
    fail "Status missing HI posture"
fi

# ── Test 28: Validate passes HI-SS rules ──
TESTS=$((TESTS + 1))
VAL_HI=$(python3 "$SURFACE_SCRIPT" validate 2>&1) || true
HI_COUNT=$(echo "$VAL_HI" | grep -c "HI-SS-" 2>/dev/null || echo "0")
HI_PASS=$(echo "$VAL_HI" | grep -c "✅ HI-SS-" 2>/dev/null || echo "0")
if [ "$HI_COUNT" -gt 0 ] && [ "$HI_COUNT" -eq "$HI_PASS" ]; then
    pass "All HI-SS rules pass ($HI_PASS/$HI_COUNT)"
else
    fail "HI-SS rules: $HI_PASS/$HI_COUNT pass"
fi

# ── Test 29: Report includes Action Handoff Intake section ──
TESTS=$((TESTS + 1))
ROUT_29=$(python3 "$SURFACE_SCRIPT" report 2>&1) || true
TESTS=$((TESTS + 1))
if echo "$ROUT_29" | grep -q "Action Handoff Intake"; then
    pass "Report shows Action Handoff Intake section"
else
    fail "Report missing Action Handoff Intake section"
fi

# ── Test 30: Status shows HRO line ──
TESTS=$((TESTS + 1))
SOUT_HRO=$(python3 "$SURFACE_SCRIPT" status 2>&1) || true
if echo "$SOUT_HRO" | grep -q "HRO:"; then
    pass "Status shows HRO posture"
else
    fail "Status missing HRO posture"
fi

# ── Test 31: Validate passes HRO-SS rules ──
TESTS=$((TESTS + 1))
VAL_HRO=$(python3 "$SURFACE_SCRIPT" validate 2>&1) || true
HRO_COUNT=$(echo "$VAL_HRO" | grep -c "HRO-SS-" 2>/dev/null || echo "0")
HRO_PASS=$(echo "$VAL_HRO" | grep -c "✅ HRO-SS-" 2>/dev/null || echo "0")
if [ "$HRO_COUNT" -gt 0 ] && [ "$HRO_COUNT" -eq "$HRO_PASS" ]; then
    pass "All HRO-SS rules pass ($HRO_PASS/$HRO_COUNT)"
else
    fail "HRO-SS rules: $HRO_PASS/$HRO_COUNT pass"
fi

# ── Test 32: Report includes Handoff Review Outcomes section ──
TESTS=$((TESTS + 1))
ROUT_32=$(python3 "$SURFACE_SCRIPT" report 2>&1) || true
TESTS=$((TESTS + 1))
if echo "$ROUT_32" | grep -q "Handoff Review Outcomes"; then
    pass "Report shows Handoff Review Outcomes section"
else
    fail "Report missing Handoff Review Outcomes section"
fi

# ── Test 33: Status shows RD line ──
TESTS=$((TESTS + 1))
SOUT_RD=$(python3 "$SURFACE_SCRIPT" status 2>&1) || true
if echo "$SOUT_RD" | grep -q "RD:"; then
    pass "Status shows RD posture"
else
    fail "Status missing RD posture"
fi

# ── Test 34: Validate passes RD-SS rules ──
TESTS=$((TESTS + 1))
VAL_RD=$(python3 "$SURFACE_SCRIPT" validate 2>&1) || true
RD_COUNT=$(echo "$VAL_RD" | grep -c "RD-SS-" 2>/dev/null || echo "0")
RD_PASS=$(echo "$VAL_RD" | grep -c "✅ RD-SS-" 2>/dev/null || echo "0")
if [ "$RD_COUNT" -gt 0 ] && [ "$RD_COUNT" -eq "$RD_PASS" ]; then
    pass "All RD-SS rules pass ($RD_PASS/$RD_COUNT)"
else
    fail "RD-SS rules: $RD_PASS/$RD_COUNT pass"
fi

# ── Test 35: Report includes Owner Action Readiness section ──
TESTS=$((TESTS + 1))
ROUT_35=$(python3 "$SURFACE_SCRIPT" report 2>&1) || true
TESTS=$((TESTS + 1))
if echo "$ROUT_35" | grep -q "Owner Action Readiness"; then
    pass "Report shows Owner Action Readiness section"
else
    fail "Report missing Owner Action Readiness section"
fi

# ── Test 36: Status shows TD line ──
TESTS=$((TESTS + 1))
SOUT_TD=$(python3 "$SURFACE_SCRIPT" status 2>&1) || true
if echo "$SOUT_TD" | grep -q "TD:"; then
    pass "Status shows TD posture"
else
    fail "Status missing TD posture"
fi

# ── Test 37: Validate passes TD-SS rules ──
TESTS=$((TESTS + 1))
VAL_TD=$(python3 "$SURFACE_SCRIPT" validate 2>&1) || true
TD_COUNT=$(echo "$VAL_TD" | grep -c "TD-SS-" 2>/dev/null || echo "0")
TD_PASS=$(echo "$VAL_TD" | grep -c "✅ TD-SS-" 2>/dev/null || echo "0")
if [ "$TD_COUNT" -gt 0 ] && [ "$TD_COUNT" -eq "$TD_PASS" ]; then
    pass "All TD-SS rules pass ($TD_PASS/$TD_COUNT)"
else
    fail "TD-SS rules: $TD_PASS/$TD_COUNT pass"
fi

# ── Test 38: Report includes Review Depth Thresholds section ──
TESTS=$((TESTS + 1))
ROUT_38=$(python3 "$SURFACE_SCRIPT" report 2>&1) || true
if echo "$ROUT_38" | grep -q "Review Depth Thresholds"; then
    pass "Report shows Review Depth Thresholds section"
else
    fail "Report missing Review Depth Thresholds section"
fi

echo ""
echo "===================================================================================="
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
