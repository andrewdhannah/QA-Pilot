#!/bin/bash
# QA Workbench Owner Action Packet test runner
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
AP_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-owner-action-packet.py"
AP_CLI="$SCRIPT_DIR/qa_pilot_owner_action_packet.py"
AP_FIXTURE_DIR="$PROJECT_ROOT/docs/examples/qa-pilot-owner-action-packet"
AP_STORE="$PROJECT_ROOT/data/workbench-owner-action-packets"

echo "=== QA Workbench Owner Action Packet Test Runner ==="
echo ""
PASS=0; FAIL=0

cleanup() { rm -rf "$AP_STORE"; }
trap cleanup EXIT

echo "--- G1: Validate valid fixtures ---"
output=$(python3 "$AP_VALIDATOR" fixture "$AP_FIXTURE_DIR" 2>&1 || true)
if echo "$output" | grep -q "8 pass"; then echo "[PASS] All fixture validation"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G2: Validate specific valid fixture ---"
output=$(python3 "$AP_VALIDATOR" validate "$AP_FIXTURE_DIR/valid-proposed.json" 2>&1)
if echo "$output" | grep -q "VALID:"; then echo "[PASS] Validate valid fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G3: Validate specific invalid fixture ---"
output=$(python3 "$AP_VALIDATOR" validate "$AP_FIXTURE_DIR/invalid-autonomous-execution.json" 2>&1 || true)
if echo "$output" | grep -q "INVALID:"; then echo "[PASS] Validate invalid fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G4: Create proposed action packet ---"
output=$(python3 "$AP_CLI" action-create --packet-id AP-PROPOSED-0001 --receipt-id WDR-ACTION-0001 --summary-id DS-REVIEW-0003 --intake-id IR-REVIEW-0003 --item-ids QA-SEC-0001,QA-SEC-0002 --evidence-ids EP-SECURITY-001 --state proposed --decision accepted_for_action --rationale "Security action proposed for engineering team" 2>&1)
if echo "$output" | grep -q "Action packet created"; then echo "[PASS] Create proposed"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G5: Create authorized action packet ---"
output=$(python3 "$AP_CLI" action-create --packet-id AP-AUTHORIZED-0001 --receipt-id WDR-AUTH-0001 --summary-id DS-REVIEW-0001 --intake-id IR-REVIEW-0001 --item-ids QA-FUNC-0001 --state owner_authorized --decision authorized --rationale "Owner authorized triage and evidence collection" 2>&1)
if echo "$output" | grep -q "AP-AUTHORIZED-0001"; then echo "[PASS] Create authorized"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G6: Create deferred action packet ---"
output=$(python3 "$AP_CLI" action-create --packet-id AP-DEFERRED-0001 --receipt-id WDR-DEFER-0001 --summary-id DS-REVIEW-0004 --intake-id IR-REVIEW-0004 --item-ids QA-PERF-0005 --state deferred --decision deferred --rationale "Deferred pending infrastructure upgrade" 2>&1)
if echo "$output" | grep -q "AP-DEFERRED-0001"; then echo "[PASS] Create deferred"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G7: Create rejected action packet ---"
output=$(python3 "$AP_CLI" action-create --packet-id AP-REJECTED-0001 --receipt-id WDR-REJECT-0001 --summary-id DS-REVIEW-0005 --intake-id IR-REVIEW-0005 --item-ids QA-DOCS-0100,QA-DOCS-0101 --state rejected --decision rejected --rationale "Documentation findings acceptable as-is" 2>&1)
if echo "$output" | grep -q "AP-REJECTED-0001"; then echo "[PASS] Create rejected"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G8: Read an action packet ---"
output=$(python3 "$AP_CLI" action-read AP-AUTHORIZED-0001 2>&1)
if echo "$output" | grep -q "action_packet_id"; then echo "[PASS] Read packet"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G9: List action packets ---"
output=$(python3 "$AP_CLI" action-list 2>&1)
if echo "$output" | grep -q "Owner Action Packets"; then echo "[PASS] List packets"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G10: Validate live packet ---"
output=$(python3 "$AP_CLI" action-validate AP-AUTHORIZED-0001 2>&1)
if echo "$output" | grep -q "ALL CHECKS PASS"; then echo "[PASS] Validate live packet"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G11: Action status ---"
output=$(python3 "$AP_CLI" action-status 2>&1)
if echo "$output" | grep -q "Owner Action Packet Status"; then echo "[PASS] Action status"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G12: Live validator passes ---"
output=$(python3 "$AP_VALIDATOR" live 2>&1)
if echo "$output" | grep -q "pass"; then echo "[PASS] Live validator passes"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G13: Packet is advisory-only ---"
packet_json=$(python3 "$AP_CLI" action-read AP-AUTHORIZED-0001 2>&1)
if echo "$packet_json" | grep -q '"advisory_only": true'; then echo "[PASS] Packet is advisory-only"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G14: Reject nonexistent packet ---"
output=$(python3 "$AP_CLI" action-read AP-NONEXISTENT-9999 2>&1 || true)
if echo "$output" | grep -q "not found"; then echo "[PASS] Reject nonexistent packet"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G15: Validate from file ---"
output=$(python3 "$AP_CLI" action-validate --packet-file "$AP_FIXTURE_DIR/valid-authorized.json" 2>&1)
if echo "$output" | grep -q "ALL CHECKS PASS"; then echo "[PASS] Validate from file"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G16: All four states represented ---"
output=$(python3 "$AP_CLI" action-status 2>&1)
proposed=$(echo "$output" | grep -c "proposed" || true)
authorized=$(echo "$output" | grep -c "owner_authorized" || true)
deferred=$(echo "$output" | grep -c "deferred" || true)
rejected=$(echo "$output" | grep -c "rejected" || true)
if [ "$proposed" -ge 1 ] && [ "$authorized" -ge 1 ] && [ "$deferred" -ge 1 ] && [ "$rejected" -ge 1 ]; then
  echo "[PASS] All four states represented"; PASS=$((PASS+1))
else
  echo "[FAIL] Missing states: proposed=$proposed authorized=$authorized deferred=$deferred rejected=$rejected"; FAIL=$((FAIL+1))
fi

echo ""
echo "=== Test Results: $PASS pass, $FAIL fail ==="
exit $FAIL
