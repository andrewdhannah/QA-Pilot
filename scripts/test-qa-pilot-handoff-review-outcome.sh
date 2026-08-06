#!/bin/bash
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HO_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-handoff-review-outcome.py"
HO_CLI="$SCRIPT_DIR/qa_pilot_handoff_review_outcome.py"
AP_CLI="$SCRIPT_DIR/qa_pilot_owner_action_packet.py"
AXP_CLI="$SCRIPT_DIR/qa_pilot_owner_action_packet_export.py"
HI_CLI="$SCRIPT_DIR/qa_pilot_action_handoff_intake.py"
HO_FIXTURE_DIR="$PROJECT_ROOT/docs/examples/qa-pilot-handoff-review-outcome"
HO_STORE="$PROJECT_ROOT/data/workbench-handoff-review-outcomes"
HI_STORE="$PROJECT_ROOT/data/workbench-action-handoff-intake"
AXP_STORE="$PROJECT_ROOT/data/workbench-action-packet-exports"
AP_STORE="$PROJECT_ROOT/data/workbench-owner-action-packets"
echo "=== QA Workbench Handoff Review Outcome Test Runner ==="; echo ""; PASS=0; FAIL=0
cleanup() { rm -rf "$HO_STORE" "$HI_STORE" "$AXP_STORE" "$AP_STORE"; }; trap cleanup EXIT

echo "--- G1: Validate valid fixtures ---"
output=$(python3 "$HO_VALIDATOR" fixture "$HO_FIXTURE_DIR" 2>&1 || true)
if echo "$output" | grep -q "7 pass"; then echo "[PASS] All fixture validation"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G2: Validate specific valid fixture ---"
output=$(python3 "$HO_VALIDATOR" validate "$HO_FIXTURE_DIR/valid-ready-for-owner-action.json" 2>&1)
if echo "$output" | grep -q "VALID:"; then echo "[PASS] Validate valid fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G3: Validate specific invalid fixture ---"
output=$(python3 "$HO_VALIDATOR" validate "$HO_FIXTURE_DIR/invalid-execution-claim.json" 2>&1 || true)
if echo "$output" | grep -q "INVALID:"; then echo "[PASS] Validate invalid fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G4: Create source chain (AP->export->handoff) ---"
python3 "$AP_CLI" action-create --packet-id AP-HO-SRC-0001 --receipt-id WDR-ACTION-0001 --summary-id DS-REVIEW-0003 --intake-id IR-REVIEW-0003 --item-ids QA-SEC-0001,QA-SEC-0002 --state proposed --decision accepted_for_action --rationale "Source for HO test" > /dev/null 2>&1
python3 "$AXP_CLI" action-export AP-HO-SRC-0001 --export-id AXPK-HO-SRC-0001 > /dev/null 2>&1
python3 "$HI_CLI" handoff-intake AXPK-HO-SRC-0001 --handoff-id HI-HO-SRC-0001 > /dev/null 2>&1
echo "[INFO] Source chain created"

echo ""; echo "--- G5: Record outcome (ready_for_owner_action) ---"
output=$(python3 "$HO_CLI" outcome-record HI-HO-SRC-0001 --outcome-state ready_for_owner_action --review-summary "Downstream review complete. Ready for Owner." 2>&1)
if echo "$output" | grep -q "Outcome recorded"; then echo "[PASS] Record outcome"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G6: Record outcome with custom ID ---"
output=$(python3 "$HO_CLI" outcome-record HI-HO-SRC-0001 --outcome-id HO-CUSTOM-0001 --outcome-state needs_revision --review-summary "Additional evidence needed before proceeding." 2>&1)
if echo "$output" | grep -q "HO-CUSTOM-0001"; then echo "[PASS] Custom outcome ID"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G7: Record blocked outcome ---"
output=$(python3 "$HO_CLI" outcome-record HI-HO-SRC-0001 --outcome-id HO-BLOCKED-TEST-0001 --outcome-state blocked --review-summary "Blocked by infrastructure dependency." 2>&1)
if echo "$output" | grep -q "HO-BLOCKED-TEST-0001"; then echo "[PASS] Record blocked"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G8: Record rejected outcome ---"
output=$(python3 "$HO_CLI" outcome-record HI-HO-SRC-0001 --outcome-id HO-REJECT-TEST-0001 --outcome-state rejected --review-summary "Non-actionable after detailed analysis." 2>&1)
if echo "$output" | grep -q "HO-REJECT-TEST-0001"; then echo "[PASS] Record rejected"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G9: Read outcome ---"
output=$(python3 "$HO_CLI" outcome-read HO-CUSTOM-0001 2>&1)
if echo "$output" | grep -q "outcome_id"; then echo "[PASS] Read outcome"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G10: List outcomes ---"
output=$(python3 "$HO_CLI" outcome-list 2>&1)
if echo "$output" | grep -q "Handoff Review Outcomes"; then echo "[PASS] List outcomes"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G11: Validate live outcome ---"
output=$(python3 "$HO_CLI" outcome-validate HO-CUSTOM-0001 2>&1)
if echo "$output" | grep -q "ALL CHECKS PASS"; then echo "[PASS] Validate live outcome"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G12: Outcome status ---"
output=$(python3 "$HO_CLI" outcome-status 2>&1)
if echo "$output" | grep -q "Handoff Review Outcome Status"; then echo "[PASS] Outcome status"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G13: Live validator passes ---"
output=$(python3 "$HO_VALIDATOR" live 2>&1)
if echo "$output" | grep -q "pass"; then echo "[PASS] Live validator passes"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G14: Outcome is advisory-only ---"
oj=$(python3 "$HO_CLI" outcome-read HO-CUSTOM-0001 2>&1)
if echo "$oj" | grep -q '"advisory_only": true'; then echo "[PASS] Outcome is advisory-only"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G15: Reject nonexistent handoff ---"
output=$(python3 "$HO_CLI" outcome-record HI-NONEXISTENT-9999 --outcome-state ready_for_owner_action --review-summary "Test" 2>&1 || true)
if echo "$output" | grep -q "not found"; then echo "[PASS] Reject nonexistent handoff"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G16: All four states represented ---"
output=$(python3 "$HO_CLI" outcome-status 2>&1)
ready=$(echo "$output" | grep -c "ready_for_owner_action" || true)
revise=$(echo "$output" | grep -c "needs_revision" || true)
blocked=$(echo "$output" | grep -c "blocked" || true)
rejected=$(echo "$output" | grep -c "rejected" || true)
if [ "$ready" -ge 1 ] && [ "$revise" -ge 1 ] && [ "$blocked" -ge 1 ] && [ "$rejected" -ge 1 ]; then echo "[PASS] All four states"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "=== Test Results: $PASS pass, $FAIL fail ==="
exit $FAIL
