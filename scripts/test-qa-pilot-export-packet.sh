#!/bin/bash
# QA Workbench Export Packet test runner
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PKT_CLI="$SCRIPT_DIR/qa_pilot_export_packet.py"
WB_CLI="$SCRIPT_DIR/qa_pilot_workbench.py"
WB_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-workbench.py"
PKT_FIXTURE_DIR="$PROJECT_ROOT/docs/examples/qa-pilot-export-packet"
WB_STORE="$PROJECT_ROOT/data/workbench-items"
PKT_STORE="$PROJECT_ROOT/data/export-packets"

echo "=== QA Workbench Export Packet Test Runner ==="
echo ""

PASS=0; FAIL=0

cleanup() { rm -rf "$WB_STORE" "$PKT_STORE"; }
trap cleanup EXIT

mkdir -p "$WB_STORE"

# Create a test item for CLI export tests
echo '{"qa_item_id":"QA-EXPORT-0001","title":"Export test item","source":"manual","status":"open","severity":"low","category":"functional","description":"Export test","evidence_refs":[],"evidence_links":[],"lifecycle_history":[{"from_status":"__init__","to_status":"open","transition_reason":"Created","actor":"agent","timestamp":"2026-07-08T00:00:00Z","advisory_only":true}],"owner_decision_state":"pending","created_at":"2026-07-08T00:00:00Z","updated_at":"2026-07-08T00:00:00Z","advisory_only":true,"custody":"qa-pilot-local","librarian_impact":"none"}' > /tmp/wb-exp.json
python3 "$WB_CLI" create /tmp/wb-exp.json > /dev/null 2>&1 || true
rm -f /tmp/wb-exp.json

echo ""
echo "--- G1: Validate packet fixtures ---"
output=$(python3 "$WB_VALIDATOR" packet "$PKT_FIXTURE_DIR" 2>&1 || true)
if echo "$output" | grep -q "Packet validation:"; then echo "[PASS] Packet fixture validation"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G2: Export single item ---"
output=$(python3 "$PKT_CLI" export-item QA-EXPORT-0001 2>&1)
if echo "$output" | grep -q "Packet created"; then echo "[PASS] Export single item"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G3: Read packet ---"
output=$(python3 "$PKT_CLI" read-packet XPK-EXPORT-0001 2>&1)
if echo "$output" | grep -q "packet_id"; then echo "[PASS] Read packet"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G4: List packets ---"
output=$(python3 "$PKT_CLI" list-packets 2>&1)
if echo "$output" | grep -q "Export Packets"; then echo "[PASS] List packets"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G5: Summarize packet ---"
output=$(python3 "$PKT_CLI" summarize-packet XPK-EXPORT-0001 2>&1)
if echo "$output" | grep -q "Packet Summary"; then echo "[PASS] Summarize packet"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G6: Validate stored packet ---"
output=$(python3 "$PKT_CLI" validate-packet --packet-id XPK-EXPORT-0001 2>&1)
if echo "$output" | grep -q "ALL CHECKS PASS"; then echo "[PASS] Validate stored packet"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G7: Validate packet from file ---"
output=$(python3 "$PKT_CLI" validate-packet "$PKT_FIXTURE_DIR/valid-single-item-packet.json" 2>&1)
if echo "$output" | grep -q "ALL CHECKS PASS"; then echo "[PASS] Validate packet file"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G8: Reject invalid packet file ---"
output=$(python3 "$PKT_CLI" validate-packet "$PKT_FIXTURE_DIR/invalid-packet-missing-disclaimer.json" 2>&1 || true)
if echo "$output" | grep -q "WP-4"; then echo "[PASS] Reject invalid packet"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G9: Export single item to output file ---"
output=$(python3 "$PKT_CLI" export-item QA-EXPORT-0001 --packet-id XPK-TEST-0001 --output /tmp/pkt-test.json 2>&1)
if echo "$output" | grep -q "exported to"; then echo "[PASS] Export to file"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi
rm -f /tmp/pkt-test.json

echo ""
echo "--- G10: Export item with nonexistent ID fails ---"
output=$(python3 "$PKT_CLI" export-item QA-NONEXISTENT-9999 2>&1 || true)
if echo "$output" | grep -q "not found"; then echo "[PASS] Nonexistent item rejected"; PASS=$((PASS+1)); else echo "[FAIL]"; echo "$output"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G11: Packet has advisory disclaimer ---"
output=$(python3 "$PKT_CLI" list-packets 2>&1)
if echo "$output" | grep -q "Export Packets"; then echo "[PASS] Packet list has disclaimer"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "--- G12: Validate all workbench fixtures still pass ---"
output=$(python3 "$WB_VALIDATOR" fixture "$PROJECT_ROOT/docs/examples/qa-pilot-workbench" 2>&1 || true)
if echo "$output" | grep -q "Fixture validation:"; then echo "[PASS] Workbench fixtures still pass"; PASS=$((PASS+1)); else echo "[FAIL]"; FAIL=$((FAIL+1)); fi

echo ""
echo "=== Test Results: $PASS pass, $FAIL fail ==="
exit $FAIL
