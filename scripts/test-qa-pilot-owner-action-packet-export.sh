#!/bin/bash
# QA Workbench Action Packet Export test runner
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
AXP_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-owner-action-packet-export.py"
AXP_CLI="$SCRIPT_DIR/qa_pilot_owner_action_packet_export.py"
AP_CLI="$SCRIPT_DIR/qa_pilot_owner_action_packet.py"
AXP_FIXTURE_DIR="$PROJECT_ROOT/docs/examples/qa-pilot-action-packet-export"
AXP_STORE="$PROJECT_ROOT/data/workbench-action-packet-exports"
AP_STORE="$PROJECT_ROOT/data/workbench-owner-action-packets"

echo "=== QA Workbench Action Packet Export Test Runner ==="
echo ""
PASS=0; FAIL=0

cleanup() { rm -rf "$AXP_STORE" "$AP_STORE"; }
trap cleanup EXIT

echo "--- G1: Validate valid fixtures ---"
output=$(python3 "$AXP_VALIDATOR" fixture "$AXP_FIXTURE_DIR" 2>&1 || true)
if echo "$output" | grep -q "6 pass"; then echo "[PASS] All fixture validation"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G2: Validate specific valid fixture ---"
output=$(python3 "$AXP_VALIDATOR" validate "$AXP_FIXTURE_DIR/valid-proposed-export.json" 2>&1)
if echo "$output" | grep -q "VALID:"; then echo "[PASS] Validate valid fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G3: Validate specific invalid fixture ---"
output=$(python3 "$AXP_VALIDATOR" validate "$AXP_FIXTURE_DIR/invalid-execution-claim.json" 2>&1 || true)
if echo "$output" | grep -q "INVALID:"; then echo "[PASS] Validate invalid fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G4: Create action packet for export source ---"
output=$(python3 "$AP_CLI" action-create --packet-id AP-EXPORT-SRC-0001 --receipt-id WDR-ACTION-0001 --summary-id DS-REVIEW-0003 --intake-id IR-REVIEW-0003 --item-ids QA-SEC-0001,QA-SEC-0002 --evidence-ids EP-SECURITY-001 --state proposed --decision accepted_for_action --rationale "Source for export test" 2>&1)
if echo "$output" | grep -q "AP-EXPORT-SRC-0001"; then echo "[PASS] Create source AP"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G5: Export action packet ---"
output=$(python3 "$AXP_CLI" action-export AP-EXPORT-SRC-0001 2>&1)
if echo "$output" | grep -q "Action export created"; then echo "[PASS] Export action packet"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G6: Export with custom ID ---"
output=$(python3 "$AXP_CLI" action-export AP-EXPORT-SRC-0001 --export-id AXPK-CUSTOM-0001 2>&1)
if echo "$output" | grep -q "AXPK-CUSTOM-0001"; then echo "[PASS] Export with custom ID"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G7: Read export ---"
output=$(python3 "$AXP_CLI" action-export-read AXPK-CUSTOM-0001 2>&1)
if echo "$output" | grep -q "export_id"; then echo "[PASS] Read export"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G8: List exports ---"
output=$(python3 "$AXP_CLI" action-export-list 2>&1)
if echo "$output" | grep -q "Action Packet Exports"; then echo "[PASS] List exports"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G9: Validate live export ---"
output=$(python3 "$AXP_CLI" action-export-validate AXPK-CUSTOM-0001 2>&1)
if echo "$output" | grep -q "ALL CHECKS PASS"; then echo "[PASS] Validate live export"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G10: Export status ---"
output=$(python3 "$AXP_CLI" action-export-status 2>&1)
if echo "$output" | grep -q "Action Export Status"; then echo "[PASS] Export status"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G11: Live validator passes ---"
output=$(python3 "$AXP_VALIDATOR" live 2>&1)
if echo "$output" | grep -q "pass"; then echo "[PASS] Live validator passes"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G12: Export is advisory-only ---"
export_json=$(python3 "$AXP_CLI" action-export-read AXPK-CUSTOM-0001 2>&1)
if echo "$export_json" | grep -q '"advisory_only": true'; then echo "[PASS] Export is advisory-only"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G13: Reject nonexistent export ---"
output=$(python3 "$AXP_CLI" action-export-read AXPK-NONEXISTENT-9999 2>&1 || true)
if echo "$output" | grep -q "not found"; then echo "[PASS] Reject nonexistent export"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G14: Reject nonexistent source packet ---"
output=$(python3 "$AXP_CLI" action-export AP-NONEXISTENT-9999 2>&1 || true)
if echo "$output" | grep -q "not found"; then echo "[PASS] Reject nonexistent source"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G15: Validate from file ---"
output=$(python3 "$AXP_CLI" action-export-validate --export-file "$AXP_FIXTURE_DIR/valid-authorized-export.json" 2>&1)
if echo "$output" | grep -q "ALL CHECKS PASS"; then echo "[PASS] Validate from file"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "=== Test Results: $PASS pass, $FAIL fail ==="
exit $FAIL
