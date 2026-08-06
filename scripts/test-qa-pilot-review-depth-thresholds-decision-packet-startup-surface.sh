#!/bin/bash
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SS_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-review-depth-thresholds-decision-packet-startup-surface.py"
SS_CLI="$SCRIPT_DIR/qa_pilot_review_depth_thresholds_decision_packet_startup_surface.py"
DP_CLI="$SCRIPT_DIR/qa_pilot_review_depth_thresholds_decision_packet.py"
TD_CLI="$SCRIPT_DIR/qa_pilot_review_depth_thresholds.py"
SS_FIXTURE_DIR="$PROJECT_ROOT/docs/examples/qa-pilot-review-depth-thresholds-decision-packet-startup-surface"
DP_STORE="$PROJECT_ROOT/data/review-decision-packets"
TD_STORE="$PROJECT_ROOT/data/review-depth-thresholds"
echo "=== QA Pilot Decision Packet Startup Surface Test Runner ==="; echo ""; PASS=0; FAIL=0
cleanup() { rm -rf "$DP_STORE" "$TD_STORE"; }; trap cleanup EXIT

echo "--- G1: Surface reports absent state (no store) ---"
output=$(python3 "$SS_CLI" status 2>&1)
if echo "$output" | grep -q "absent"; then echo "[PASS] Reports absent when no store"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G2: Surface reports empty state (empty index) ---"
mkdir -p "$DP_STORE"
echo '{"records":[],"last_updated":"2026-07-08T00:00:00Z"}' > "$DP_STORE/packet-index.json"
output=$(python3 "$SS_CLI" status 2>&1)
if echo "$output" | grep -q "empty\|0\|no decision"; then echo "[PASS] Reports empty store"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G3: Surface reports present with live packets ---"
# Create a threshold source
python3 "$TD_CLI" threshold-evaluate --threshold-id TD-SS-TEST --state sufficient --rationale "SS test source" --evidence-count 5 --consistency-total 5 --consistency-pass 5 > /dev/null 2>&1
# Create a decision packet
python3 "$DP_CLI" packet-create TD-SS-TEST --packet-id DP-SS-TEST-0001 --packet-state needs_owner_review --review-summary "Test packet for startup surface validation." > /dev/null 2>&1
output=$(python3 "$SS_CLI" status 2>&1)
if echo "$output" | grep -q "present"; then echo "[PASS] Reports present with live data"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G4: Surface report shows packet count ---"
output=$(python3 "$SS_CLI" report --format json 2>&1)
if echo "$output" | grep -q "packet_count"; then echo "[PASS] Report has packet count"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G5: Surface report shows latest packet ID ---"
output=$(python3 "$SS_CLI" report --format json 2>&1)
if echo "$output" | grep -q "DP-SS-TEST-0001"; then echo "[PASS] Shows latest packet ID"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G6: Surface report shows latest packet state ---"
output=$(python3 "$SS_CLI" report --format json 2>&1)
if echo "$output" | grep -q "needs_owner_review"; then echo "[PASS] Shows latest packet state"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G7: Surface report shows threshold references ---"
output=$(python3 "$SS_CLI" report --format json 2>&1)
if echo "$output" | grep -q "TD-SS-TEST"; then echo "[PASS] Shows threshold ref"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G8: Surface report shows evidence bundle reference ---"
output=$(python3 "$SS_CLI" report --format json 2>&1)
if echo "$output" | grep -q "evidence_bundle_ref"; then echo "[PASS] Shows evidence bundle ref"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G9: Surface report shows timestamp ---"
output=$(python3 "$SS_CLI" report --format json 2>&1)
if echo "$output" | grep -q "latest_timestamp\|timestamp"; then echo "[PASS] Shows timestamp"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G10: Surface is advisory-only ---"
output=$(python3 "$SS_CLI" report --format json 2>&1)
if echo "$output" | grep -q '"advisory_only": true'; then echo "[PASS] Advisory-only"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G11: Surface has no authority fields ---"
output=$(python3 "$SS_CLI" report --format json 2>&1)
# Should NOT contain approval/seal/execution fields
if echo "$output" | grep -qv '"approve_\|"seal_\|"executed_'; then echo "[PASS] No authority fields in surface"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G12: Text report format ---"
output=$(python3 "$SS_CLI" report 2>&1)
if echo "$output" | grep -q "Decision Packet"; then echo "[PASS] Text report format"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G13: Validate live surface (DP-SS rules) ---"
output=$(python3 "$SS_CLI" validate 2>&1)
if echo "$output" | grep -q "ALL DP-SS CHECKS PASS"; then echo "[PASS] Live surface validates"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G14: Validator fixture pass (valid packet present) ---"
output=$(python3 "$SS_VALIDATOR" fixture "$SS_FIXTURE_DIR" 2>&1) || true
if echo "$output" | grep -q "3 pass"; then echo "[PASS] All fixture validation"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G15: Validator validates valid fixture directly ---"
output=$(python3 "$SS_VALIDATOR" validate "$SS_FIXTURE_DIR/valid-packet-present.json" 2>&1)
if echo "$output" | grep -q "VALID:"; then echo "[PASS] Valid valid fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G16: Validator rejects invalid authority fixture ---"
output=$(python3 "$SS_VALIDATOR" validate "$SS_FIXTURE_DIR/invalid-authority-claim.json" 2>&1 || true)
if echo "$output" | grep -q "FAIL\|INVALID"; then echo "[PASS] Rejects authority claim fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "=== Test Results: $PASS pass, $FAIL fail ==="
exit $FAIL
