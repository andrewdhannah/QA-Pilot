#!/bin/bash
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TD_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-review-depth-thresholds.py"
TD_CLI="$SCRIPT_DIR/qa_pilot_review_depth_thresholds.py"
TD_FIXTURE_DIR="$PROJECT_ROOT/docs/examples/qa-pilot-review-depth-thresholds"
TD_STORE="$PROJECT_ROOT/data/review-depth-thresholds"
echo "=== QA Pilot Review Depth Threshold Test Runner ==="; echo ""; PASS=0; FAIL=0
cleanup() { rm -rf "$TD_STORE"; }; trap cleanup EXIT

echo "--- G1: Validate valid fixtures ---"
output=$(python3 "$TD_VALIDATOR" fixture "$TD_FIXTURE_DIR" 2>&1 || true)
if echo "$output" | grep -q "6 pass"; then echo "[PASS] All fixture validation"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G2: Validate specific valid fixture ---"
output=$(python3 "$TD_VALIDATOR" validate "$TD_FIXTURE_DIR/valid-sufficient.json" 2>&1)
if echo "$output" | grep -q "VALID:"; then echo "[PASS] Validate valid fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G3: Validate invalid fixture ---"
output=$(python3 "$TD_VALIDATOR" validate "$TD_FIXTURE_DIR/invalid-auto-accept-claim.json" 2>&1 || true)
if echo "$output" | grep -q "INVALID:"; then echo "[PASS] Validate invalid fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G4: Evaluate threshold (sufficient) ---"
output=$(python3 "$TD_CLI" threshold-evaluate --state sufficient --rationale "All checks pass. Evidence depth adequate." --evidence-count 12 --consistency-total 11 --consistency-pass 11 2>&1)
if echo "$output" | grep -q "Threshold evaluated"; then echo "[PASS] Evaluate sufficient"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G5: Evaluate with custom ID ---"
output=$(python3 "$TD_CLI" threshold-evaluate --threshold-id TD-CUSTOM-0001 --state needs_more_context --rationale "Only 8 of 11 consistency checks pass." --evidence-count 4 --consistency-total 11 --consistency-pass 8 2>&1)
if echo "$output" | grep -q "TD-CUSTOM-0001"; then echo "[PASS] Custom threshold ID"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G6: Evaluate blocked ---"
output=$(python3 "$TD_CLI" threshold-evaluate --threshold-id TD-BLOCK-EVAL-0001 --state blocked --rationale "Critical evidence gaps. Only 2 of 11 checks pass." --evidence-count 1 --consistency-total 11 --consistency-pass 2 2>&1)
if echo "$output" | grep -q "TD-BLOCK-EVAL-0001"; then echo "[PASS] Evaluate blocked"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G7: Read threshold ---"
output=$(python3 "$TD_CLI" threshold-read TD-CUSTOM-0001 2>&1)
if echo "$output" | grep -q "threshold_id"; then echo "[PASS] Read threshold"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G8: List thresholds ---"
output=$(python3 "$TD_CLI" threshold-list 2>&1)
if echo "$output" | grep -q "Review Depth Thresholds"; then echo "[PASS] List thresholds"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G9: Validate live threshold ---"
output=$(python3 "$TD_CLI" threshold-validate TD-CUSTOM-0001 2>&1)
if echo "$output" | grep -q "ALL CHECKS PASS"; then echo "[PASS] Validate live"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G10: Threshold status ---"
output=$(python3 "$TD_CLI" threshold-status 2>&1)
if echo "$output" | grep -q "Review Depth Threshold Status"; then echo "[PASS] Threshold status"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G11: Live validator passes ---"
output=$(python3 "$TD_VALIDATOR" live 2>&1)
if echo "$output" | grep -q "pass"; then echo "[PASS] Live validator passes"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G12: Advisory-only ---"
tj=$(python3 "$TD_CLI" threshold-read TD-CUSTOM-0001 2>&1)
if echo "$tj" | grep -q '"advisory_only": true'; then echo "[PASS] Advisory-only"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G13: All three states represented ---"
output=$(python3 "$TD_CLI" threshold-status 2>&1)
suff=$(echo "$output" | grep -c "sufficient" || true); need=$(echo "$output" | grep -c "needs_more_context" || true); blk=$(echo "$output" | grep -c "blocked" || true)
if [ "$suff" -ge 1 ] && [ "$need" -ge 1 ] && [ "$blk" -ge 1 ]; then echo "[PASS] All three states"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "--- G14: Validate from file ---"
output=$(python3 "$TD_CLI" threshold-validate --threshold-file "$TD_FIXTURE_DIR/valid-sufficient.json" 2>&1)
if echo "$output" | grep -q "ALL CHECKS PASS"; then echo "[PASS] Validate from file"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""; echo "=== Test Results: $PASS pass, $FAIL fail ==="
exit $FAIL
