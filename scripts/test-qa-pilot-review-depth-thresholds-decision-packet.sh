#!/bin/bash
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DP_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-review-depth-thresholds-decision-packet.py"
DP_CLI="$SCRIPT_DIR/qa_pilot_review_depth_thresholds_decision_packet.py"
TD_CLI="$SCRIPT_DIR/qa_pilot_review_depth_thresholds.py"
DP_FIXTURE_DIR="$PROJECT_ROOT/docs/examples/qa-pilot-review-depth-thresholds-decision-packet"
DP_STORE="$PROJECT_ROOT/data/review-decision-packets"
TD_STORE="$PROJECT_ROOT/data/review-depth-thresholds"
echo "=== QA Pilot Decision Packet Test Runner ==="; echo ""; PASS=0; FAIL=0
cleanup() { rm -rf "$DP_STORE" "$TD_STORE"; }; trap cleanup EXIT

echo "--- G1: Validate valid fixtures ---"
output=$(python3 "$DP_VALIDATOR" fixture "$DP_FIXTURE_DIR" 2>&1 || true)
if echo "$output" | grep -q "7 pass"; then echo "[PASS] All fixture validation"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G2: Validate specific valid fixture ---"
output=$(python3 "$DP_VALIDATOR" validate "$DP_FIXTURE_DIR/valid-prepared.json" 2>&1)
if echo "$output" | grep -q "VALID:"; then echo "[PASS] Validate valid fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G3: Validate invalid fixture ---"
output=$(python3 "$DP_VALIDATOR" validate "$DP_FIXTURE_DIR/invalid-auto-accept-claim.json" 2>&1 || true)
if echo "$output" | grep -q "INVALID:"; then echo "[PASS] Validate invalid fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G4: Create threshold source ---"
python3 "$TD_CLI" threshold-evaluate --threshold-id TD-SRC-DP-0001 --state sufficient --rationale "Source for DP test" --evidence-count 12 --consistency-total 11 --consistency-pass 11 > /dev/null 2>&1
echo "[INFO] Threshold created"

echo ""; echo "--- G5: Create decision packet (prepared) ---"
output=$(python3 "$DP_CLI" packet-create TD-SRC-DP-0001 --packet-state prepared --review-summary "Packet prepared for Owner review queue." 2>&1)
if echo "$output" | grep -q "Decision packet created"; then echo "[PASS] Create prepared"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G6: Create with custom ID ---"
output=$(python3 "$DP_CLI" packet-create TD-SRC-DP-0001 --packet-id DP-CUSTOM-0001 --packet-state needs_owner_review --review-summary "Evidence sufficient. Forwarded for Owner review." 2>&1)
if echo "$output" | grep -q "DP-CUSTOM-0001"; then echo "[PASS] Custom packet ID"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G7: Create deferred ---"
output=$(python3 "$DP_CLI" packet-create TD-SRC-DP-0001 --packet-id DP-DEFER-TEST-0001 --packet-state deferred --review-summary "Additional evidence needed before Owner review." 2>&1)
if echo "$output" | grep -q "DP-DEFER-TEST-0001"; then echo "[PASS] Create deferred"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G8: Create closed_by_owner ---"
output=$(python3 "$DP_CLI" packet-create TD-SRC-DP-0001 --packet-id DP-CLOSE-TEST-0001 --packet-state closed_by_owner --review-summary "Owner reviewed and finalized. Owner remains the only decision authority." 2>&1)
if echo "$output" | grep -q "DP-CLOSE-TEST-0001"; then echo "[PASS] Create closed_by_owner"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G9: Read packet ---"
output=$(python3 "$DP_CLI" packet-read DP-CUSTOM-0001 2>&1)
if echo "$output" | grep -q "packet_id"; then echo "[PASS] Read packet"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G10: List packets ---"
output=$(python3 "$DP_CLI" packet-list 2>&1)
if echo "$output" | grep -q "Decision Packets"; then echo "[PASS] List packets"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G11: Validate live packet ---"
output=$(python3 "$DP_CLI" packet-validate DP-CUSTOM-0001 2>&1)
if echo "$output" | grep -q "ALL CHECKS PASS"; then echo "[PASS] Validate live"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G12: Packet status ---"
output=$(python3 "$DP_CLI" packet-status 2>&1)
if echo "$output" | grep -q "Decision Packet Status"; then echo "[PASS] Packet status"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G13: Live validator passes ---"
output=$(python3 "$DP_VALIDATOR" live 2>&1)
if echo "$output" | grep -q "pass"; then echo "[PASS] Live validator passes"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G14: Advisory-only ---"
pj=$(python3 "$DP_CLI" packet-read DP-CUSTOM-0001 2>&1)
if echo "$pj" | grep -q '"advisory_only": true'; then echo "[PASS] Advisory-only"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G15: All four packet states ---"
output=$(python3 "$DP_CLI" packet-status 2>&1)
prep=$(echo "$output" | grep -c "prepared" || true); need=$(echo "$output" | grep -c "needs_owner_review" || true)
defr=$(echo "$output" | grep -c "deferred" || true); clsd=$(echo "$output" | grep -c "closed_by_owner" || true)
if [ "$prep" -ge 1 ] && [ "$need" -ge 1 ] && [ "$defr" -ge 1 ] && [ "$clsd" -ge 1 ]; then echo "[PASS] All four states"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "=== Test Results: $PASS pass, $FAIL fail ==="
exit $FAIL
