#!/bin/bash
# QA Workbench Review Decision Receipt test runner
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WDR_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-review-decision-receipt.py"
WDR_CLI="$SCRIPT_DIR/qa_pilot_review_decision_receipt.py"
WDR_FIXTURE_DIR="$PROJECT_ROOT/docs/examples/qa-pilot-review-decision-receipt"
WDR_STORE="$PROJECT_ROOT/data/review-decision-receipts"

echo "=== QA Workbench Review Decision Receipt Test Runner ==="
echo ""
PASS=0; FAIL=0

cleanup() { rm -rf "$WDR_STORE"; }
trap cleanup EXIT

echo "--- G1: Validate valid fixtures ---"
output=$(python3 "$WDR_VALIDATOR" fixture "$WDR_FIXTURE_DIR" 2>&1 || true)
if echo "$output" | grep -q "8 pass"; then echo "[PASS] All fixture validation"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G2: Validate specific valid fixture ---"
output=$(python3 "$WDR_VALIDATOR" validate "$WDR_FIXTURE_DIR/valid-accepted-for-action.json" 2>&1)
if echo "$output" | grep -q "VALID:"; then echo "[PASS] Validate valid fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G3: Validate specific invalid fixture ---"
output=$(python3 "$WDR_VALIDATOR" validate "$WDR_FIXTURE_DIR/invalid-seal-claim.json" 2>&1 || true)
if echo "$output" | grep -q "INVALID:"; then echo "[PASS] Validate invalid fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G4: Record a decision receipt ---"
output=$(python3 "$WDR_CLI" decision-record --summary-id DS-REVIEW-0001 --intake-id IR-REVIEW-0001 --item-ids QA-FUNC-0001 --decision accepted_for_action --rationale "Test receipt" 2>&1)
if echo "$output" | grep -q "Receipt recorded"; then echo "[PASS] Record receipt"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G5: Record authorized decision ---"
output=$(python3 "$WDR_CLI" decision-record --receipt-id WDR-AUTH-0001 --summary-id DS-REVIEW-0001 --intake-id IR-REVIEW-0001 --item-ids QA-FUNC-0001 --decision authorized --rationale "Authorized by Owner" 2>&1)
if echo "$output" | grep -q "WDR-AUTH-0001"; then echo "[PASS] Record authorized"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G6: Record deferred decision ---"
output=$(python3 "$WDR_CLI" decision-record --receipt-id WDR-DEFER-0001 --summary-id DS-REVIEW-0004 --intake-id IR-REVIEW-0004 --item-ids QA-PERF-0005 --decision deferred --rationale "Deferred pending infra" 2>&1)
if echo "$output" | grep -q "WDR-DEFER-0001"; then echo "[PASS] Record deferred"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G7: Record rejected decision ---"
output=$(python3 "$WDR_CLI" decision-record --receipt-id WDR-REJECT-0001 --summary-id DS-REVIEW-0005 --intake-id IR-REVIEW-0005 --item-ids QA-DOCS-0100,QA-DOCS-0101 --decision rejected --rationale "Rejected by Owner" 2>&1)
if echo "$output" | grep -q "WDR-REJECT-0001"; then echo "[PASS] Record rejected"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G8: Read a receipt ---"
output=$(python3 "$WDR_CLI" decision-read WDR-AUTH-0001 2>&1)
if echo "$output" | grep -q "receipt_id"; then echo "[PASS] Read receipt"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G9: List receipts ---"
output=$(python3 "$WDR_CLI" decision-list 2>&1)
if echo "$output" | grep -q "Review Decision Receipts"; then echo "[PASS] List receipts"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G10: Validate live receipt ---"
output=$(python3 "$WDR_CLI" decision-validate WDR-AUTH-0001 2>&1)
if echo "$output" | grep -q "ALL CHECKS PASS"; then echo "[PASS] Validate live receipt"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G11: Decision status ---"
output=$(python3 "$WDR_CLI" decision-status 2>&1)
if echo "$output" | grep -q "Review Decision Receipt Status"; then echo "[PASS] Decision status"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G12: Live validator passes ---"
output=$(python3 "$WDR_VALIDATOR" live 2>&1)
if echo "$output" | grep -q "pass"; then echo "[PASS] Live validator passes"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G13: Receipt is advisory-only ---"
receipt_json=$(python3 "$WDR_CLI" decision-read WDR-AUTH-0001 2>&1)
if echo "$receipt_json" | grep -q '"advisory_only": true'; then echo "[PASS] Receipt is advisory-only"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G14: Reject nonexistent receipt ---"
output=$(python3 "$WDR_CLI" decision-read WDR-NONEXISTENT-9999 2>&1 || true)
if echo "$output" | grep -q "not found"; then echo "[PASS] Reject nonexistent receipt"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G15: Validate from file ---"
output=$(python3 "$WDR_CLI" decision-validate --receipt-file "$WDR_FIXTURE_DIR/valid-authorized.json" 2>&1)
if echo "$output" | grep -q "ALL CHECKS PASS"; then echo "[PASS] Validate from file"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "=== Test Results: $PASS pass, $FAIL fail ==="
exit $FAIL
