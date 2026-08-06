#!/bin/bash
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RD_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-owner-action-readiness.py"
RD_CLI="$SCRIPT_DIR/qa_pilot_owner_action_readiness.py"
AP_CLI="$SCRIPT_DIR/qa_pilot_owner_action_packet.py"
AXP_CLI="$SCRIPT_DIR/qa_pilot_owner_action_packet_export.py"
HI_CLI="$SCRIPT_DIR/qa_pilot_action_handoff_intake.py"
HO_CLI="$SCRIPT_DIR/qa_pilot_handoff_review_outcome.py"
RD_FIXTURE_DIR="$PROJECT_ROOT/docs/examples/qa-pilot-owner-action-readiness"
for d in workbench-owner-action-readiness workbench-handoff-review-outcomes workbench-action-handoff-intake workbench-action-packet-exports workbench-owner-action-packets; do
    eval "${d//-/_}_STORE=\$PROJECT_ROOT/data/\$d"
done
echo "=== QA Workbench Owner Action Readiness Test Runner ==="; echo ""; PASS=0; FAIL=0
cleanup() { rm -rf data/workbench-owner-action-readiness data/workbench-handoff-review-outcomes data/workbench-action-handoff-intake data/workbench-action-packet-exports data/workbench-owner-action-packets; }; trap cleanup EXIT

echo "--- G1: Validate valid fixtures ---"
output=$(python3 "$RD_VALIDATOR" fixture "$RD_FIXTURE_DIR" 2>&1 || true)
if echo "$output" | grep -q "7 pass"; then echo "[PASS] All fixture validation"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G2: Validate specific valid fixture ---"
output=$(python3 "$RD_VALIDATOR" validate "$RD_FIXTURE_DIR/valid-ready.json" 2>&1)
if echo "$output" | grep -q "VALID:"; then echo "[PASS] Validate valid fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G3: Validate invalid fixture ---"
output=$(python3 "$RD_VALIDATOR" validate "$RD_FIXTURE_DIR/invalid-execution-claim.json" 2>&1 || true)
if echo "$output" | grep -q "INVALID:"; then echo "[PASS] Validate invalid fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G4: Create source chain (AP->export->handoff->outcome) ---"
python3 "$AP_CLI" action-create --packet-id AP-RD-SRC-0001 --receipt-id WDR-ACTION-0001 --summary-id DS-REVIEW-0003 --intake-id IR-REVIEW-0003 --item-ids QA-SEC-0001,QA-SEC-0002 --state proposed --decision accepted_for_action --rationale "Source for RD test" > /dev/null 2>&1
python3 "$AXP_CLI" action-export AP-RD-SRC-0001 --export-id AXPK-RD-SRC-0001 > /dev/null 2>&1
python3 "$HI_CLI" handoff-intake AXPK-RD-SRC-0001 --handoff-id HI-RD-SRC-0001 > /dev/null 2>&1
outcome_out=$(python3 "$HO_CLI" outcome-record HI-RD-SRC-0001 --outcome-id HO-RD-0001 --outcome-state ready_for_owner_action --review-summary "Ready for RD test" 2>&1)
echo "[INFO] Source chain created"

echo ""; echo "--- G5: Create readiness record ---"
output=$(python3 "$RD_CLI" readiness-create HO-RD-0001 --readiness-state ready_for_owner_decision --rationale "Chain complete and ready for Owner decision." 2>&1)
if echo "$output" | grep -q "Readiness created"; then echo "[PASS] Create readiness"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G6: Create with custom ID ---"
python3 "$HO_CLI" outcome-record HI-RD-SRC-0001 --outcome-id HO-RD-REVISE-0001 --outcome-state needs_revision --review-summary "Needs revision for RD test" > /dev/null 2>&1
output=$(python3 "$RD_CLI" readiness-create HO-RD-REVISE-0001 --readiness-id RD-CUSTOM-0001 --readiness-state needs_revision --rationale "Revision needed based on review outcome." 2>&1)
if echo "$output" | grep -q "RD-CUSTOM-0001"; then echo "[PASS] Custom readiness ID"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G7: Read readiness ---"
output=$(python3 "$RD_CLI" readiness-read RD-CUSTOM-0001 2>&1)
if echo "$output" | grep -q "readiness_id"; then echo "[PASS] Read readiness"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G8: List readiness ---"
output=$(python3 "$RD_CLI" readiness-list 2>&1)
if echo "$output" | grep -q "Owner Action Readiness"; then echo "[PASS] List readiness"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G9: Validate live readiness ---"
output=$(python3 "$RD_CLI" readiness-validate RD-CUSTOM-0001 2>&1)
if echo "$output" | grep -q "ALL CHECKS PASS"; then echo "[PASS] Validate live"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G10: Readiness status ---"
output=$(python3 "$RD_CLI" readiness-status 2>&1)
if echo "$output" | grep -q "Owner Action Readiness Status"; then echo "[PASS] Readiness status"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G11: Live validator passes ---"
output=$(python3 "$RD_VALIDATOR" live 2>&1)
if echo "$output" | grep -q "pass"; then echo "[PASS] Live validator passes"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G12: Advisory-only ---"
rj=$(python3 "$RD_CLI" readiness-read RD-CUSTOM-0001 2>&1)
if echo "$rj" | grep -q '"advisory_only": true'; then echo "[PASS] Advisory-only"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G13: Reject nonexistent outcome ---"
output=$(python3 "$RD_CLI" readiness-create HO-NONEXISTENT-9999 --readiness-state ready_for_owner_decision --rationale "Test" 2>&1 || true)
if echo "$output" | grep -q "not found"; then echo "[PASS] Reject nonexistent outcome"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G14: Validate from file ---"
output=$(python3 "$RD_CLI" readiness-validate --readiness-file "$RD_FIXTURE_DIR/valid-ready.json" 2>&1)
if echo "$output" | grep -q "ALL CHECKS PASS"; then echo "[PASS] Validate from file"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "=== Test Results: $PASS pass, $FAIL fail ==="
exit $FAIL
