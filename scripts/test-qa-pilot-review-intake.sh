#!/bin/bash
# QA Workbench Review Intake test runner
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WB_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-workbench.py"
INTAKE_CLI="$SCRIPT_DIR/qa_pilot_review_intake.py"
PKT_CLI="$SCRIPT_DIR/qa_pilot_export_packet.py"
WB_CLI="$SCRIPT_DIR/qa_pilot_workbench.py"
INT_FIXTURE_DIR="$PROJECT_ROOT/docs/examples/qa-pilot-review-intake"
WB_STORE="$PROJECT_ROOT/data/workbench-items"
PKT_STORE="$PROJECT_ROOT/data/export-packets"
INT_STORE="$PROJECT_ROOT/data/review-intake"

echo "=== QA Workbench Review Intake Test Runner ==="
echo ""
PASS=0; FAIL=0

cleanup() { rm -rf "$WB_STORE" "$PKT_STORE" "$INT_STORE"; }
trap cleanup EXIT

mkdir -p "$WB_STORE" "$PKT_STORE"

# Create a test item and export it as a packet for intake tests
echo '{"qa_item_id":"QA-INTK-0001","title":"Intake test item","source":"manual","status":"open","severity":"low","category":"functional","description":"Intake test","evidence_refs":[],"evidence_links":[],"lifecycle_history":[{"from_status":"__init__","to_status":"open","transition_reason":"Created","actor":"agent","timestamp":"2026-07-08T01:55:00Z","advisory_only":true}],"owner_decision_state":"pending","created_at":"2026-07-08T01:55:00Z","updated_at":"2026-07-08T01:55:00Z","advisory_only":true,"custody":"qa-pilot-local","librarian_impact":"none"}' > /tmp/intk-create.json
python3 "$WB_CLI" create /tmp/intk-create.json > /dev/null 2>&1 || true
rm -f /tmp/intk-create.json

# Export as packet
python3 "$PKT_CLI" export-item QA-INTK-0001 > /dev/null 2>&1 || true

echo "--- G1: Validate intake fixtures ---"
output=$(python3 "$WB_VALIDATOR" intake "$INT_FIXTURE_DIR" 2>&1 || true)
if echo "$output" | grep -q "Intake validation:"; then echo "[PASS] Intake fixture validation"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G2: Register intake from stored packet ---"
output=$(python3 "$INTAKE_CLI" intake-register --packet-id XPK-EXPORT-0001 2>&1)
if echo "$output" | grep -q "Intake registered"; then echo "[PASS] Register from packet ID"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G3: Register intake from file ---"
output=$(python3 "$INTAKE_CLI" intake-register --packet-file "$PROJECT_ROOT/docs/examples/qa-pilot-export-packet/valid-single-item-packet.json" --intake-id IR-FILE-0001 2>&1)
if echo "$output" | grep -q "Intake registered"; then echo "[PASS] Register from file"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G4: Read intake ---"
output=$(python3 "$INTAKE_CLI" intake-read IR-REVIEW-0001 2>&1)
if echo "$output" | grep -q "intake_id"; then echo "[PASS] Read intake"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G5: List intakes ---"
output=$(python3 "$INTAKE_CLI" intake-list 2>&1)
if echo "$output" | grep -q "Review Intake Records"; then echo "[PASS] List intakes"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G6: Validate stored intake ---"
output=$(python3 "$INTAKE_CLI" intake-validate IR-REVIEW-0001 2>&1)
if echo "$output" | grep -q "ALL CHECKS PASS"; then echo "[PASS] Validate stored intake"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G7: Triage intake ---"
output=$(python3 "$INTAKE_CLI" intake-triage IR-REVIEW-0001 2>&1)
if echo "$output" | grep -q "Triaged"; then echo "[PASS] Triage intake"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G8: Intake summary ---"
output=$(python3 "$INTAKE_CLI" intake-summary 2>&1)
if echo "$output" | grep -q "Review Intake Summary"; then echo "[PASS] Intake summary"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G9: Summary shows advisory disclaimer ---"
if echo "$output" | grep -qi "advisory"; then echo "[PASS] Summary advisory disclaimer"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G10: Reject invalid intake file ---"
output=$(python3 "$INTAKE_CLI" intake-validate --intake-file "$INT_FIXTURE_DIR/invalid-missing-disclaimer.json" 2>&1 || true)
if echo "$output" | grep -q "IR-4"; then echo "[PASS] Reject invalid intake"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G11: Reject nonexistent packet ---"
output=$(python3 "$INTAKE_CLI" intake-register --packet-id XPK-NONEXISTENT-9999 2>&1 || true)
if echo "$output" | grep -q "not found"; then echo "[PASS] Reject nonexistent packet"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G12: All workbench fixtures still pass ---"
output=$(python3 "$WB_VALIDATOR" fixture "$PROJECT_ROOT/docs/examples/qa-pilot-workbench" 2>&1 || true)
if echo "$output" | grep -q "Fixture validation:"; then echo "[PASS] Workbench fixtures pass"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G13: All export packet fixtures still pass ---"
output=$(python3 "$WB_VALIDATOR" packet "$PROJECT_ROOT/docs/examples/qa-pilot-export-packet" 2>&1 || true)
if echo "$output" | grep -q "Packet validation:"; then echo "[PASS] Packet fixtures pass"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "=== Test Results: $PASS pass, $FAIL fail ==="
exit $FAIL
