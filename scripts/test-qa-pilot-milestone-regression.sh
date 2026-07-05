#!/usr/bin/env bash
set -euo pipefail

# QA Pilot Milestone Regression Test Runner — QA-PILOT-MILESTONE-REGRESSION-SUITE-1
#
# One-command regression suite for the sealed QA packet ingest chain.
# Tests: custody invariants, advisory boundary, derived-store behavior,
#        invalid-packet rejection, no-cross-project-write rule.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REGRESSION_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-milestone-regression.py"
REGRESSION_FIXTURES="$REPO_ROOT/docs/examples/qa-pilot-milestone-regression"
INGEST_FIXTURES="$REPO_ROOT/docs/examples/qa-pilot-qa-packet-ingest"
INGEST_CLI="$SCRIPT_DIR/qa_pilot_qa_packet_ingest.py"
INGEST_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-qa-packet-ingest.py"
INGESTED_DIR="$REPO_ROOT/data/packets/ingested"
INDEX_FILE="$REPO_ROOT/data/packets/ingested-index.json"
GOV_DOC="$REPO_ROOT/docs/governance/QA-PILOT-MILESTONE-REGRESSION.md"
LIBRARIAN_BASE="$REPO_ROOT/../librarian"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Milestone Regression Test Runner — QA-PILOT-MILESTONE-REGRESSION-SUITE-1"
echo "========================================================================"
echo ""

# ── Test 1: Regression validator script exists ──
TESTS=$((TESTS + 1))
if [ -f "$REGRESSION_VALIDATOR" ]; then
    pass "Regression validator script found"
else
    fail "Regression validator script not found"
fi

# ── Test 2: Regression validator runs and all checks pass ──
TESTS=$((TESTS + 1))
VALIDATOR_OUTPUT=$(python3 "$REGRESSION_VALIDATOR" 2>&1) || true
if echo "$VALIDATOR_OUTPUT" | grep -q "ALL REGRESSION CHECKS PASS"; then
    pass "Regression validator: all checks pass"
else
    fail "Regression validator: checks failed"
    echo "$VALIDATOR_OUTPUT" | tail -30
fi

# ── Test 3: Regression fixtures directory exists with correct count ──
TESTS=$((TESTS + 1))
FIXTURE_COUNT=$(ls "$REGRESSION_FIXTURES"/*.json 2>/dev/null | wc -l | tr -d ' ')
VALID_COUNT=$(ls "$REGRESSION_FIXTURES"/regression-valid-*.json 2>/dev/null | wc -l | tr -d ' ')
INVALID_COUNT=$(ls "$REGRESSION_FIXTURES"/regression-invalid-*.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$FIXTURE_COUNT" -ge 10 ] && [ "$VALID_COUNT" -ge 4 ] && [ "$INVALID_COUNT" -ge 6 ]; then
    pass "Regression fixtures: $FIXTURE_COUNT total ($VALID_COUNT valid, $INVALID_COUNT invalid)"
else
    fail "Regression fixtures: expected >=10 total (>=4 valid, >=6 invalid), found $FIXTURE_COUNT ($VALID_COUNT valid, $INVALID_COUNT invalid)"
fi

# ── Test 4: Existing ingest validator still passes after regression ──
TESTS=$((TESTS + 1))
if python3 "$INGEST_VALIDATOR" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing PI-1-14 validator still passes (no regression)"
else
    fail "Existing PI-1-14 validator regression detected"
    python3 "$INGEST_VALIDATOR" 2>&1 | head -20
fi

# ── Test 5: Existing ingest test runner still passes ──
TESTS=$((TESTS + 1))
if bash "$SCRIPT_DIR/test-qa-pilot-qa-packet-ingest.sh" 2>&1 | grep -q "All tests pass"; then
    pass "Existing ingest test runner still passes (no regression)"
else
    fail "Existing ingest test runner regression detected"
fi

# ── Test 6: Valid regression fixtures can be ingested through CLI ──
TESTS=$((TESTS + 1))
INGEST_OK=0
INGEST_FAIL=0
for f in "$REGRESSION_FIXTURES"/regression-valid-*.json; do
    if python3 "$INGEST_CLI" ingest "$f" 2>&1 | grep -q "IMPORTED"; then
        INGEST_OK=$((INGEST_OK + 1))
    else
        INGEST_FAIL=$((INGEST_FAIL + 1))
        echo "       FAIL: ingest rejected valid fixture $(basename "$f")"
    fi
done
if [ "$INGEST_FAIL" -eq 0 ] && [ "$INGEST_OK" -ge 4 ]; then
    pass "Ingest CLI accepts all $INGEST_OK valid regression fixtures"
else
    fail "Ingest CLI rejected $INGEST_FAIL/$((INGEST_OK + INGEST_FAIL)) valid fixtures"
fi

# ── Test 7: Ingested records have correct invariant properties ──
TESTS=$((TESTS + 1))
if [ -f "$INDEX_FILE" ]; then
    ADVISORY_OK=$(python3 -c "
import json; idx=json.load(open('$INDEX_FILE'))
all_a=all(p.get('advisory') is True for p in idx.get('packets',[]))
all_c=all(p.get('cross_project_write_authorized') is False for p in idx.get('packets',[]))
all_o=all(p.get('owner_apply_required') is True for p in idx.get('packets',[]))
print(f'advisory={all_a},cross_write={all_c},owner_apply={all_o}')
" 2>&1 || echo "error")
    if echo "$ADVISORY_OK" | grep -q "advisory=True,cross_write=True,owner_apply=True"; then
        pass "Ingested records: advisory=true, cross_project_write=false, owner_apply_required=true"
    else
        fail "Ingested records invariant violation: $ADVISORY_OK"
    fi
else
    fail "No ingested index file found"
fi

# ── Test 8: Ingest CLI list command shows ingested records ──
TESTS=$((TESTS + 1))
if python3 "$INGEST_CLI" list 2>&1 | grep -q "ingested\|total\|Ingested"; then
    pass "Ingest CLI list shows ingested records"
else
    fail "Ingest CLI list failed"
fi

# ── Test 9: Ingest CLI status shows correct authority markers ──
TESTS=$((TESTS + 1))
STATUS_OUT=$(python3 "$INGEST_CLI" status 2>&1)
if echo "$STATUS_OUT" | grep -q "advisory-only" && echo "$STATUS_OUT" | grep -q "NOT AUTHORIZED"; then
    pass "Ingest CLI status shows advisory-only, cross-project-write NOT AUTHORIZED"
else
    fail "Ingest CLI status missing authority markers"
    echo "  Output: $STATUS_OUT"
fi

# ── Test 10: Reconstruction test — clear and re-ingest ──
TESTS=$((TESTS + 1))
python3 "$INGEST_CLI" clear 2>&1 > /dev/null
COUNT1=0
for f in "$REGRESSION_FIXTURES"/regression-valid-*.json; do
    python3 "$INGEST_CLI" ingest "$f" 2>&1 > /dev/null && COUNT1=$((COUNT1 + 1)) || true
done
RECON_COUNT=$(python3 -c "import json; idx=json.load(open('$INDEX_FILE')); print(len(idx.get('packets',[])))" 2>&1 || echo "0")
if [ "$RECON_COUNT" -eq "$COUNT1" ] && [ "$COUNT1" -ge 4 ]; then
    pass "Derived state reconstructable: cleared and re-ingested $COUNT1 packets"
else
    fail "Reconstruction mismatch: expected $COUNT1, found $RECON_COUNT"
fi

# ── Test 11: Invalid regression fixtures cannot be ingested ──
TESTS=$((TESTS + 1))
REJECTED=0
TOTAL_INVALID=0
for f in "$REGRESSION_FIXTURES"/regression-invalid-*.json; do
    TOTAL_INVALID=$((TOTAL_INVALID + 1))
    if ! python3 "$INGEST_CLI" ingest "$f" 2>&1 | grep -q "IMPORTED"; then
        REJECTED=$((REJECTED + 1))
    fi
done
if [ "$REJECTED" -eq "$TOTAL_INVALID" ]; then
    pass "All $TOTAL_INVALID invalid regression fixtures rejected by ingest CLI"
else
    fail "Only $REJECTED/$TOTAL_INVALID invalid fixtures rejected"
fi

# ── Test 12: Boundary scan — no regression files in Librarian ──
TESTS=$((TESTS + 1))
LEAKED=""
if [ -f "$LIBRARIAN_BASE/scripts/validate-qa-pilot-milestone-regression.py" ]; then
    LEAKED="$LEAKED validator"
fi
if [ -f "$LIBRARIAN_BASE/scripts/test-qa-pilot-milestone-regression.sh" ]; then
    LEAKED="$LEAKED test-runner"
fi
if [ -d "$LIBRARIAN_BASE/docs/examples/qa-pilot-milestone-regression" ]; then
    LEAKED="$LEAKED fixtures"
fi
if [ -f "$LIBRARIAN_BASE/docs/governance/QA-PILOT-MILESTONE-REGRESSION.md" ]; then
    LEAKED="$LEAKED gov-doc"
fi
if [ -z "$LEAKED" ]; then
    pass "Boundary scan CLEAN: no regression files in Librarian"
else
    fail "Boundary scan: regression files found in Librarian:$LEAKED"
fi

# ── Test 13: Clear works and resets state ──
TESTS=$((TESTS + 1))
python3 "$INGEST_CLI" clear 2>&1 > /dev/null
CLEAR_COUNT=$(python3 -c "import json; idx=json.load(open('$INDEX_FILE')); print(len(idx.get('packets',[])))" 2>&1 || echo "error")
if [ "$CLEAR_COUNT" = "0" ] || [ "$CLEAR_COUNT" = "error" ]; then
    pass "Clear command resets ingested state"
else
    fail "Clear did not reset state: $CLEAR_COUNT packets remain"
fi

# ── Test 14: Governance doc exists ──
TESTS=$((TESTS + 1))
if [ -f "$GOV_DOC" ]; then
    pass "Regression governance doc exists"
else
    fail "Regression governance doc not found"
fi

# ── Test 15: QA Pilot sprint ledger is valid JSON  
TESTS=$((TESTS + 1))
if python3 -c "import json; json.load(open('$REPO_ROOT/project-state/sprint-ledger.json'))" 2>/dev/null; then
    pass "QA Pilot sprint ledger is valid JSON"
else
    fail "QA Pilot sprint ledger is not valid JSON"
fi

echo ""
echo "========================================================================"
echo "Tests: $TESTS total"
echo "Pass:  $PASS"
echo "Fail:  $FAIL"

if [ "$FAIL" -eq 0 ]; then
    echo "Result: $PASS/$TESTS passed. All regression tests pass. ✅"
    exit 0
else
    echo "Result: $PASS/$TESTS passed. Some tests failed. ❌"
    exit 1
fi
