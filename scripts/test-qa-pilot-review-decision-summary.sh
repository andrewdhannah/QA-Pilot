#!/bin/bash
# QA Workbench Review Decision Summary test runner
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DS_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-review-decision-summary.py"
INTAKE_CLI="$SCRIPT_DIR/qa_pilot_review_intake.py"
WB_CLI="$SCRIPT_DIR/qa_pilot_workbench.py"
PKT_CLI="$SCRIPT_DIR/qa_pilot_export_packet.py"
DS_FIXTURE_DIR="$PROJECT_ROOT/docs/examples/qa-pilot-review-decision-summary"
DS_STORE="$PROJECT_ROOT/data/review-decision-summaries"
INT_STORE="$PROJECT_ROOT/data/review-intake"
WB_STORE="$PROJECT_ROOT/data/workbench-items"
PKT_STORE="$PROJECT_ROOT/data/export-packets"

echo "=== QA Workbench Review Decision Summary Test Runner ==="
echo ""
PASS=0; FAIL=0

cleanup() { rm -rf "$DS_STORE" "$INT_STORE" "$WB_STORE" "$PKT_STORE"; }
trap cleanup EXIT

mk_store() {
  mkdir -p "$WB_STORE" "$INT_STORE" "$PKT_STORE" "$DS_STORE"
}

echo "--- G1: Validate valid fixtures ---"
output=$(python3 "$DS_VALIDATOR" fixture "$DS_FIXTURE_DIR" 2>&1 || true)
if echo "$output" | grep -q "11 pass"; then echo "[PASS] All fixture validation"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G2: Validate specific valid fixture ---"
output=$(python3 "$DS_VALIDATOR" validate "$DS_FIXTURE_DIR/valid-single-item-summary.json" 2>&1)
if echo "$output" | grep -q "VALID:"; then echo "[PASS] Validate single valid fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G3: Validate specific invalid fixture ---"
output=$(python3 "$DS_VALIDATOR" validate "$DS_FIXTURE_DIR/invalid-claiming-approval.json" 2>&1 || true)
if echo "$output" | grep -q "INVALID:"; then echo "[PASS] Validate invalid fixture"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G4: Reject invalid acceptance fixture ---"
output=$(python3 "$DS_VALIDATOR" validate "$DS_FIXTURE_DIR/invalid-accepting-defects.json" 2>&1 || true)
if echo "$output" | grep -q "DS-1"; then echo "[PASS] Reject defect acceptance"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G5: Reject invalid mutation fixture ---"
output=$(python3 "$DS_VALIDATOR" validate "$DS_FIXTURE_DIR/invalid-mutating-intake-source.json" 2>&1 || true)
if echo "$output" | grep -q "DS-7"; then echo "[PASS] Reject mutation attempt"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G6: Reject invalid registry fixture ---"
output=$(python3 "$DS_VALIDATOR" validate "$DS_FIXTURE_DIR/invalid-carries-registry-state.json" 2>&1 || true)
if echo "$output" | grep -q "DS-8"; then echo "[PASS] Reject registry state"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G7: Reject invalid closure fixture ---"
output=$(python3 "$DS_VALIDATOR" validate "$DS_FIXTURE_DIR/invalid-closing-items.json" 2>&1 || true)
if echo "$output" | grep -q "DS-1"; then echo "[PASS] Reject closure claim"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G8: Reject invalid verification fixture ---"
output=$(python3 "$DS_VALIDATOR" validate "$DS_FIXTURE_DIR/invalid-claiming-verification.json" 2>&1 || true)
if echo "$output" | grep -q "DS-6"; then echo "[PASS] Reject verification claim"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G9: Create summary from intake (live workflow) ---"
mk_store
# Create a workbench item, export it, register intake, then create summary
echo '{"qa_item_id":"QA-DS-0001","title":"Decision summary test item","source":"manual","status":"open","severity":"low","category":"functional","description":"Test item for decision summary","evidence_refs":[],"evidence_links":[],"lifecycle_history":[{"from_status":"__init__","to_status":"open","transition_reason":"Created","actor":"agent","timestamp":"2026-07-08T02:00:00Z","advisory_only":true}],"owner_decision_state":"pending","created_at":"2026-07-08T02:00:00Z","updated_at":"2026-07-08T02:00:00Z","advisory_only":true,"custody":"qa-pilot-local","librarian_impact":"none"}' > /tmp/ds-test-item.json
python3 "$WB_CLI" create /tmp/ds-test-item.json > /dev/null 2>&1 || true
rm -f /tmp/ds-test-item.json

# Export as packet
python3 "$PKT_CLI" export-item QA-DS-0001 > /dev/null 2>&1 || true

# Register intake
python3 "$INTAKE_CLI" intake-register --packet-id XPK-EXPORT-0001 > /dev/null 2>&1 || true

# Create summary
output=$(python3 "$INTAKE_CLI" summary-create IR-REVIEW-0001 2>&1)
if echo "$output" | grep -q "Summary created"; then echo "[PASS] Create summary from intake"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G10: Read created summary ---"
output=$(python3 "$INTAKE_CLI" summary-read DS-REVIEW-0001 2>&1)
if echo "$output" | grep -q "summary_id"; then echo "[PASS] Read summary"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G11: List summaries ---"
output=$(python3 "$INTAKE_CLI" summary-list 2>&1)
if echo "$output" | grep -q "Review Decision Summaries"; then echo "[PASS] List summaries"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G12: Validate live summary ---"
output=$(python3 "$INTAKE_CLI" summary-validate DS-REVIEW-0001 2>&1)
if echo "$output" | grep -q "ALL CHECKS PASS"; then echo "[PASS] Validate live summary"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G13: Generate human-readable report ---"
output=$(python3 "$INTAKE_CLI" summary-report DS-REVIEW-0001 2>&1)
if echo "$output" | grep -q "Review Decision Summary"; then echo "[PASS] Summary report"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G14: Export summary ---"
output=$(python3 "$INTAKE_CLI" summary-export DS-REVIEW-0001 2>&1)
if echo "$output" | grep -q "summary_id"; then echo "[PASS] Export summary"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G15: Summary is advisory-only ---"
summary_json=$(python3 "$INTAKE_CLI" summary-read DS-REVIEW-0001 2>&1)
if echo "$summary_json" | grep -q '"advisory_only": true'; then echo "[PASS] Summary is advisory-only"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G16: Live validator pass ---"
output=$(python3 "$DS_VALIDATOR" live 2>&1)
if echo "$output" | grep -q "1 pass"; then echo "[PASS] Live validator passes"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G17: Reject nonexistent summary ---"
output=$(python3 "$INTAKE_CLI" summary-read DS-NONEXISTENT-9999 2>&1 || true)
if echo "$output" | grep -q "not found"; then echo "[PASS] Reject nonexistent summary"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G18: Validate summary from file ---"
output=$(python3 "$INTAKE_CLI" summary-validate --summary-file "$DS_FIXTURE_DIR/valid-needs-review-summary.json" 2>&1)
if echo "$output" | grep -q "ALL CHECKS PASS"; then echo "[PASS] Validate summary from file"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G19: Create summary with custom ID ---"
# Need fresh store for this
rm -rf "$WB_STORE" "$INT_STORE" "$PKT_STORE"
mkdir -p "$WB_STORE" "$INT_STORE" "$PKT_STORE"
echo '{"qa_item_id":"QA-DS-0002","title":"Custom ID summary test","source":"manual","status":"needs_review","severity":"high","category":"security","description":"Test for custom summary ID","evidence_refs":["EP-SEC-001"],"evidence_links":[{"evidence_link_id":"EL-DS-0002-001","evidence_type":"validator_output","evidence_ref":"EP-SEC-001","producing_validator":"test.sh","attachment_reason":"Test evidence","custody":"qa-pilot-local","advisory_only":true,"authority_note":"Evidence attachment does not prove defect validity or imply Owner approval.","attached_at":"2026-07-08T02:00:00Z"}],"lifecycle_history":[{"from_status":"__init__","to_status":"open","transition_reason":"Created","actor":"agent","timestamp":"2026-07-08T02:00:00Z","advisory_only":true},{"from_status":"open","to_status":"triaged","transition_reason":"Triaged","actor":"agent","timestamp":"2026-07-08T02:01:00Z","advisory_only":true},{"from_status":"triaged","to_status":"evidence_attached","transition_reason":"Evidence attached","actor":"agent","timestamp":"2026-07-08T02:02:00Z","advisory_only":true},{"from_status":"evidence_attached","to_status":"needs_review","transition_reason":"Ready for review","actor":"agent","timestamp":"2026-07-08T02:03:00Z","advisory_only":true}],"owner_decision_state":"pending","created_at":"2026-07-08T02:00:00Z","updated_at":"2026-07-08T02:03:00Z","advisory_only":true,"custody":"qa-pilot-local","librarian_impact":"none"}' > /tmp/ds-test-item2.json
python3 "$WB_CLI" create /tmp/ds-test-item2.json > /dev/null 2>&1 || true
rm -f /tmp/ds-test-item2.json
python3 "$PKT_CLI" export-item QA-DS-0002 > /dev/null 2>&1 || true
python3 "$INTAKE_CLI" intake-register --packet-id XPK-EXPORT-0002 > /dev/null 2>&1 || true
output=$(python3 "$INTAKE_CLI" summary-create IR-REVIEW-0002 --summary-id DS-CUSTOM-0001 2>&1)
if echo "$output" | grep -q "DS-CUSTOM-0001"; then echo "[PASS] Create summary with custom ID"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "=== Test Results: $PASS pass, $FAIL fail ==="
exit $FAIL
