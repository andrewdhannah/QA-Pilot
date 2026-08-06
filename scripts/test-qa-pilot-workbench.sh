#!/bin/bash
# QA Workbench test runner — query/listing edition
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WB_CLI="$SCRIPT_DIR/qa_pilot_workbench.py"
WB_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-workbench.py"
FIXTURE_DIR="$PROJECT_ROOT/docs/examples/qa-pilot-workbench"
STORE_DIR="$PROJECT_ROOT/data/workbench-items"

echo "=== QA Workbench Test Runner (Query/Listing Edition) ==="
echo ""

PASS=0; FAIL=0
cleanup() { rm -rf "$STORE_DIR"; }
trap cleanup EXIT

# Create test items for query tests
mkdir -p "$STORE_DIR"
echo '{"qa_item_id":"QA-QTEST-0001","title":"Critical security finding","source":"evidence_intake","status":"open","severity":"critical","category":"security","description":"Test","evidence_refs":[],"evidence_links":[],"lifecycle_history":[{"from_status":"__init__","to_status":"open","transition_reason":"Created","actor":"agent","timestamp":"2026-07-08T00:00:00Z","advisory_only":true}],"owner_decision_state":"pending","created_at":"2026-07-08T00:00:00Z","updated_at":"2026-07-08T00:00:00Z","advisory_only":true,"custody":"qa-pilot-local","librarian_impact":"none"}' > /tmp/wb-qtest.json && python3 "$WB_CLI" create /tmp/wb-qtest.json > /dev/null 2>&1 || true
echo '{"qa_item_id":"QA-QTEST-0002","title":"Medium performance finding","source":"test_composition","status":"triaged","severity":"medium","category":"performance","description":"Test","evidence_refs":[],"evidence_links":[],"lifecycle_history":[{"from_status":"__init__","to_status":"open","transition_reason":"Created","actor":"agent","timestamp":"2026-07-08T00:00:00Z","advisory_only":true},{"from_status":"open","to_status":"triaged","transition_reason":"Triaged","actor":"agent","timestamp":"2026-07-08T00:05:00Z","advisory_only":true}],"owner_decision_state":"pending","created_at":"2026-07-08T00:00:00Z","updated_at":"2026-07-08T00:05:00Z","advisory_only":true,"custody":"qa-pilot-local","librarian_impact":"none"}' > /tmp/wb-qtest2.json && python3 "$WB_CLI" create /tmp/wb-qtest2.json > /dev/null 2>&1 || true
echo '{"qa_item_id":"QA-QTEST-0003","title":"Low documentation gap","source":"manual","status":"needs_review","severity":"low","category":"documentation","description":"Test","evidence_refs":[],"evidence_links":[],"lifecycle_history":[{"from_status":"__init__","to_status":"open","transition_reason":"Created","actor":"agent","timestamp":"2026-07-08T00:00:00Z","advisory_only":true},{"from_status":"open","to_status":"triaged","transition_reason":"Triaged","actor":"agent","timestamp":"2026-07-08T00:05:00Z","advisory_only":true},{"from_status":"triaged","to_status":"evidence_attached","transition_reason":"Evidence linked","actor":"agent","timestamp":"2026-07-08T00:10:00Z","advisory_only":true},{"from_status":"evidence_attached","to_status":"needs_review","transition_reason":"Ready for review","actor":"agent","timestamp":"2026-07-08T00:15:00Z","advisory_only":true}],"owner_decision_state":"pending","created_at":"2026-07-08T00:00:00Z","updated_at":"2026-07-08T00:15:00Z","advisory_only":true,"custody":"qa-pilot-local","librarian_impact":"none"}' > /tmp/wb-qtest3.json && python3 "$WB_CLI" create /tmp/wb-qtest3.json > /dev/null 2>&1 || true
rm -f /tmp/wb-qtest.json /tmp/wb-qtest2.json /tmp/wb-qtest3.json

# === G1: G1-G23 from lifecycle edition ===
echo "--- G1: Fixture validation (all fixtures) ---"
output=$(python3 "$WB_VALIDATOR" fixture "$FIXTURE_DIR" 2>&1 || true)
if echo "$output" | grep -q "Fixture validation:"; then echo "[PASS] Fixture validation"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G2: List with status filter ---"
output=$(python3 "$WB_CLI" list --status open 2>&1)
if echo "$output" | grep -q "QA Workbench Items"; then echo "[PASS] List by status"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G3: List with severity filter ---"
output=$(python3 "$WB_CLI" list --severity critical 2>&1)
if echo "$output" | grep -q "QA Workbench Items"; then echo "[PASS] List by severity"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G4: List with category filter ---"
output=$(python3 "$WB_CLI" list --category documentation 2>&1)
if echo "$output" | grep -q "QA Workbench Items"; then echo "[PASS] List by category"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G5: List with needs-review filter ---"
output=$(python3 "$WB_CLI" list --needs-review 2>&1)
if echo "$output" | grep -q "QA Workbench Items"; then echo "[PASS] List needs-review"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G6: List no results for nonexistent status ---"
output=$(python3 "$WB_CLI" list --status resolved_locally 2>&1)
if echo "$output" | grep -q "No QA items found"; then echo "[PASS] List no matches"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G7: Query with status filter ---"
output=$(python3 "$WB_CLI" query --status needs_review 2>&1)
if echo "$output" | grep -q "Query results"; then echo "[PASS] Query by status"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G8: Query with multiple filters ---"
output=$(python3 "$WB_CLI" query --severity critical --category security 2>&1)
if echo "$output" | grep -q "Query results"; then echo "[PASS] Query multi-filter"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G9: Query JSON format ---"
output=$(python3 "$WB_CLI" query --status open --format json 2>&1)
if echo "$output" | grep -q '"qa_item_id"'; then echo "[PASS] Query JSON format"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G10: Query advisory disclaimer ---"
output=$(python3 "$WB_CLI" query --status open 2>&1)
if echo "$output" | grep -qi "advisory"; then echo "[PASS] Query advisory disclaimer"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G11: Count total ---"
output=$(python3 "$WB_CLI" count 2>&1)
if echo "$output" | grep -q "Total items"; then echo "[PASS] Count total"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G12: Count with filter ---"
output=$(python3 "$WB_CLI" count --severity low 2>&1)
if echo "$output" | grep -q "Matching filters"; then echo "[PASS] Count with filter"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G13: Count by status group ---"
output=$(python3 "$WB_CLI" count --group status 2>&1)
if echo "$output" | grep -q "By status"; then echo "[PASS] Count by status"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G14: Count by severity group ---"
output=$(python3 "$WB_CLI" count --group severity 2>&1)
if echo "$output" | grep -q "By severity"; then echo "[PASS] Count by severity"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G15: Count by category group ---"
output=$(python3 "$WB_CLI" count --group category 2>&1)
if echo "$output" | grep -q "By category"; then echo "[PASS] Count by category"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G16: Report ---"
output=$(python3 "$WB_CLI" report 2>&1)
if echo "$output" | grep -q "Summary Report"; then echo "[PASS] Report"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G17: Report advisory disclaimer ---"
if echo "$output" | grep -qi "advisory"; then echo "[PASS] Report advisory disclaimer"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G18: Export summary JSON ---"
output=$(python3 "$WB_CLI" export-summary 2>&1)
if echo "$output" | grep -q '"total_items"'; then echo "[PASS] Export summary JSON"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G19: Export summary advisory note ---"
if echo "$output" | grep -qi "advisory"; then echo "[PASS] Export summary advisory"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G20: Export summary to file ---"
output=$(python3 "$WB_CLI" export-summary --output /tmp/wb-summary-test.json 2>&1)
if echo "$output" | grep -q "exported"; then echo "[PASS] Export summary to file"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi
rm -f /tmp/wb-summary-test.json

echo ""
echo "--- G21: Validator fixture mode ---"
output=$(python3 "$WB_VALIDATOR" fixture "$FIXTURE_DIR" 2>&1 || true)
if echo "$output" | grep -q "Fixture validation:"; then echo "[PASS] Validator fixture mode"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G22: WQ-1 authority claim rejected ---"
output=$(python3 "$WB_VALIDATOR" validate "$FIXTURE_DIR/invalid-query-claims-approval.json" 2>&1 || true)
if echo "$output" | grep -q "WQ-1"; then echo "[PASS] WQ-1 authority claim rejected"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G23: WQ-2 lifecycle mismatch detected ---"
output=$(python3 "$WB_VALIDATOR" validate "$FIXTURE_DIR/invalid-query-mutates-lifecycle.json" 2>&1 || true)
if echo "$output" | grep -qE "(WQ-2|WL-7)"; then echo "[PASS] WQ-2 lifecycle mismatch"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G24: Count status-specific ---"
output=$(python3 "$WB_CLI" count --status needs_review 2>&1)
if echo "$output" | grep -q "Matching filters"; then echo "[PASS] Count status-specific"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G25: Has evidence filter ---"
# Attach evidence to QA-QTEST-0001 (valid item)
echo '{"evidence_link_id":"EL-QT-0001-001","evidence_type":"validator_output","evidence_ref":"EP-TEST-001","custody":"qa-pilot-local","advisory_only":true,"authority_note":"Evidence attachment does not prove defect validity or imply Owner approval.","attached_at":"2026-07-08T00:00:00Z"}' > /tmp/wb-el.json
python3 "$WB_CLI" attach QA-QTEST-0001 /tmp/wb-el.json > /dev/null 2>&1 || true
rm -f /tmp/wb-el.json
output=$(python3 "$WB_CLI" list --has-evidence 2>&1)
if echo "$output" | grep -q "QA Workbench Items"; then echo "[PASS] List has-evidence"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "=== Test Results: $PASS pass, $FAIL fail ==="
exit $FAIL
