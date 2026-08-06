#!/bin/bash
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HI_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-action-handoff-intake.py"
HI_CLI="$SCRIPT_DIR/qa_pilot_action_handoff_intake.py"
AP_CLI="$SCRIPT_DIR/qa_pilot_owner_action_packet.py"
AXP_CLI="$SCRIPT_DIR/qa_pilot_owner_action_packet_export.py"
HI_FIXTURE_DIR="$PROJECT_ROOT/docs/examples/qa-pilot-action-handoff-intake"
HI_STORE="$PROJECT_ROOT/data/workbench-action-handoff-intake"
AXP_STORE="$PROJECT_ROOT/data/workbench-action-packet-exports"
AP_STORE="$PROJECT_ROOT/data/workbench-owner-action-packets"

echo "=== QA Workbench Action Handoff Intake Test Runner ==="
echo ""; PASS=0; FAIL=0
cleanup() { rm -rf "$HI_STORE" "$AXP_STORE" "$AP_STORE"; }
trap cleanup EXIT

echo "--- G1: Validate valid fixtures ---"
output=$(python3 "$HI_VALIDATOR" fixture "$HI_FIXTURE_DIR" 2>&1 || true)
if echo "$output" | grep -q "5 pass"; then echo "[PASS] All fixture validation"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G2: Validate specific valid fixture ---"
output=$(python3 "$HI_VALIDATOR" validate "$HI_FIXTURE_DIR/valid-received.json" 2>&1)
if echo "$output" | grep -q "VALID:"; then echo "[PASS] Validate valid fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G3: Validate specific invalid fixture ---"
output=$(python3 "$HI_VALIDATOR" validate "$HI_FIXTURE_DIR/invalid-execution-claim.json" 2>&1 || true)
if echo "$output" | grep -q "INVALID:"; then echo "[PASS] Validate invalid fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G4: Create source chain (AP -> export) ---"
python3 "$AP_CLI" action-create --packet-id AP-HI-SRC-0001 --receipt-id WDR-ACTION-0001 --summary-id DS-REVIEW-0003 --intake-id IR-REVIEW-0003 --item-ids QA-SEC-0001,QA-SEC-0002 --evidence-ids EP-SEC-001 --state proposed --decision accepted_for_action --rationale "Source for HI test" > /dev/null 2>&1
python3 "$AXP_CLI" action-export AP-HI-SRC-0001 --export-id AXPK-HI-SRC-0001 > /dev/null 2>&1
echo "[INFO] Source chain created"

echo ""; echo "--- G5: Handoff intake from export ---"
output=$(python3 "$HI_CLI" handoff-intake AXPK-HI-SRC-0001 2>&1)
if echo "$output" | grep -q "Handoff intake created"; then echo "[PASS] Handoff intake"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G6: Handoff intake with custom ID ---"
python3 "$AXP_CLI" action-export AP-HI-SRC-0001 --export-id AXPK-HI-SRC-0002 > /dev/null 2>&1
output=$(python3 "$HI_CLI" handoff-intake AXPK-HI-SRC-0002 --handoff-id HI-CUSTOM-0001 2>&1)
if echo "$output" | grep -q "HI-CUSTOM-0001"; then echo "[PASS] Custom handoff ID"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G7: Read handoff ---"
output=$(python3 "$HI_CLI" handoff-read HI-CUSTOM-0001 2>&1)
if echo "$output" | grep -q "handoff_id"; then echo "[PASS] Read handoff"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G8: List handoffs ---"
output=$(python3 "$HI_CLI" handoff-list 2>&1)
if echo "$output" | grep -q "Action Handoff Intakes"; then echo "[PASS] List handoffs"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G9: Validate live handoff ---"
output=$(python3 "$HI_CLI" handoff-validate HI-CUSTOM-0001 2>&1)
if echo "$output" | grep -q "ALL CHECKS PASS"; then echo "[PASS] Validate live handoff"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G10: Handoff status ---"
output=$(python3 "$HI_CLI" handoff-status 2>&1)
if echo "$output" | grep -q "Action Handoff Intake Status"; then echo "[PASS] Handoff status"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G11: Live validator passes ---"
output=$(python3 "$HI_VALIDATOR" live 2>&1)
if echo "$output" | grep -q "pass"; then echo "[PASS] Live validator passes"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G12: Handoff is advisory-only ---"
hj=$(python3 "$HI_CLI" handoff-read HI-CUSTOM-0001 2>&1)
if echo "$hj" | grep -q '"advisory_only": true'; then echo "[PASS] Handoff is advisory-only"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G13: Reject nonexistent export ---"
output=$(python3 "$HI_CLI" handoff-intake AXPK-NONEXISTENT-9999 2>&1 || true)
if echo "$output" | grep -q "not found"; then echo "[PASS] Reject nonexistent export"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G14: Reject nonexistent handoff ---"
output=$(python3 "$HI_CLI" handoff-read HI-NONEXISTENT-9999 2>&1 || true)
if echo "$output" | grep -q "not found"; then echo "[PASS] Reject nonexistent handoff"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G15: Validate from file ---"
output=$(python3 "$HI_CLI" handoff-validate --handoff-file "$HI_FIXTURE_DIR/valid-in-review.json" 2>&1)
if echo "$output" | grep -q "ALL CHECKS PASS"; then echo "[PASS] Validate from file"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "=== Test Results: $PASS pass, $FAIL fail ==="
exit $FAIL
