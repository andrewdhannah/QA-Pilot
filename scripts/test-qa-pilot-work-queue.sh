#!/usr/bin/env bash
# ── QA Pilot Work Queue — Test Runner ──────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QUEUE="$SCRIPT_DIR/qa_pilot_work_queue.py"
QUEUE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/data/work-queue"
DIAG_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/data/diagnostics"

# Clean up test data
rm -f "$QUEUE_DIR"/QA-*.json "$DIAG_DIR"/DIAG-*.json 2>/dev/null || true

# Verify script is callable
python3 "$QUEUE" --help > /dev/null 2>&1 || { echo "  ⚠  Queue script not callable, checking..."; ls -la "$QUEUE"; }

PASS=0; FAIL=0; TESTS=0
pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Work Queue — Test Runner"
echo "==================================="
echo ""

# Test 1: Script exists
TESTS=$((TESTS + 1))
[[ -f "$QUEUE" ]] && pass "Queue script exists" || fail "Not found"

# Test 2: --help works
TESTS=$((TESTS + 1))
HELP_OUTPUT=$(python3 "$QUEUE" --help 2>&1 || true)
if echo "$HELP_OUTPUT" | grep -q "Usage"; then
    pass "--help works"
else
    fail "--help failed (output: ${HELP_OUTPUT:0:80})"
fi

# Test 3: Diagnose creates diagnostic report
TESTS=$((TESTS + 1))
python3 "$QUEUE" diagnose REG-TEST-001 regression "Expected value" "Actual value" 2>&1 | grep -q "DIAG-REG" && pass "Diagnose creates report" || fail "Diagnose failed"

# Test 4: Create queue item from diagnostic
TESTS=$((TESTS + 1))
DIAG_PATH=$(ls "$DIAG_DIR"/DIAG-*.json 2>/dev/null | head -1)
python3 "$QUEUE" create "$DIAG_PATH" 2>&1 | grep -q "QA-" && pass "Create queue item from diagnostic" || fail "Create failed"

# Test 5: List shows items
TESTS=$((TESTS + 1))
python3 "$QUEUE" list 2>&1 | grep -q "QA-" && pass "List shows items" || fail "List failed"

# Test 6: Transition works
TESTS=$((TESTS + 1))
ITEM_ID=$(python3 "$QUEUE" list 2>/dev/null | grep "QA-" | awk '{print $1}' | head -1)
python3 "$QUEUE" transition "$ITEM_ID" APPROVED 2>&1 | grep -q "APPROVED" && pass "Transition to APPROVED works" || fail "Transition failed"

# Test 7: Status shows queue summary
TESTS=$((TESTS + 1))
python3 "$QUEUE" status 2>&1 | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d.get('queue_version') == 'qa-pilot-work-queue-v1'
assert d.get('total_items', 0) >= 1
" 2>/dev/null && pass "Status returns valid JSON with queue_version" || fail "Status invalid"

# Test 8: Show item details
TESTS=$((TESTS + 1))
python3 "$QUEUE" show "$ITEM_ID" 2>&1 | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d.get('item_id') == '$ITEM_ID'
assert d.get('status') == 'APPROVED'
assert d.get('provenance', {}).get('advisory') == True
" 2>/dev/null && pass "Show returns item with correct status and advisory" || fail "Show failed"

# Test 9: Work packet schemas exist
TESTS=$((TESTS + 1))
SCHEMAS=("qa-diagnostic-report.schema.json" "qa-work-queue-item.schema.json" "qa-work-packet.schema.json")
ALL_EXIST=true
for s in "${SCHEMAS[@]}"; do
    if [[ ! -f "$(cd "$SCRIPT_DIR/.." && pwd)/docs/schemas/$s" ]]; then
        ALL_EXIST=false
    fi
done
[[ "$ALL_EXIST" == true ]] && pass "All 3 work queue schemas exist" || fail "Missing schemas"

# Test 10: Full lifecycle test
TESTS=$((TESTS + 1))
# Clean and run full cycle
rm -f "$QUEUE_DIR"/QA-*.json "$DIAG_DIR"/DIAG-*.json 2>/dev/null || true
python3 "$QUEUE" diagnose REG-LIFECYCLE regression "Expected X" "Got Y" >/dev/null 2>&1
DIAG=$(ls "$DIAG_DIR"/DIAG-*.json 2>/dev/null | head -1)
python3 "$QUEUE" create "$DIAG" >/dev/null 2>&1
ITEM=$(python3 "$QUEUE" list 2>/dev/null | grep "QA-" | awk '{print $1}' | head -1)
python3 "$QUEUE" transition "$ITEM" TRIAGED >/dev/null 2>&1
python3 "$QUEUE" transition "$ITEM" APPROVED >/dev/null 2>&1
python3 "$QUEUE" transition "$ITEM" IN_PROGRESS >/dev/null 2>&1
python3 "$QUEUE" transition "$ITEM" FIXED >/dev/null 2>&1
python3 "$QUEUE" transition "$ITEM" VERIFIED >/dev/null 2>&1
python3 "$QUEUE" transition "$ITEM" CLOSED >/dev/null 2>&1
FINAL_STATUS=$(python3 "$QUEUE" show "$ITEM" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','?'))" 2>/dev/null || echo "fail")
[[ "$FINAL_STATUS" == "CLOSED" ]] && pass "Full lifecycle: OPEN → CLOSED (all transitions work)" || fail "Lifecycle failed at $FINAL_STATUS"

# Summary
echo ""
echo "=============================="
echo "Tests: $TESTS total | Pass: $PASS | Fail: $FAIL"
echo "=============================="
if [[ "$FAIL" -eq 0 ]]; then
    echo "Result: $PASS/$TESTS passed. All tests pass. ✅"
    exit 0
else
    echo "Result: $PASS/$TESTS passed. $FAIL failures. ❌"
    exit 1
fi
