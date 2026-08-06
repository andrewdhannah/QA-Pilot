#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKFILL_VAL="$SCRIPT_DIR/validate-qa-pilot-registry-change-receipt-backfill.py"
RCR_VAL="$SCRIPT_DIR/validate-qa-pilot-registry-change-receipt.py"
SURFACE_SCRIPT="$SCRIPT_DIR/qa_pilot_pipeline_startup_surface.py"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-registry-change-receipt-backfill"
PASS=0; FAIL=0; TESTS=0
pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot RCR Backfill Tests — QA-PILOT-REGISTRY-CHANGE-RECEIPT-BACKFILL-1"
echo "======================================================================"
echo ""

TESTS=$((TESTS + 1))
BOUT=$(python3 "$BACKFILL_VAL" 2>&1) || true
echo "$BOUT" | grep -q "0 issues" && pass "Backfill validator: coverage OK (#48-#53 all present)" || { fail "Backfill issues"; echo "       $BOUT"; }

TESTS=$((TESTS + 1))
ROUT=$(python3 "$SURFACE_SCRIPT" report 2>&1) || true
echo "$ROUT" | grep -q "Classification.*✅ ready" && pass "Surface classification: ready" || fail "Surface not ready"

TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "RCR posture.*✅" && pass "RCR posture: pass" || fail "RCR posture not pass"

TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "Receipts found:.*6" && pass "6 RCR receipts present (#48-#53)" || fail "Expected 6 receipts"

TESTS=$((TESTS + 1))
python3 "$RCR_VAL" 2>&1 | grep -q "ALL CHECKS PASS" && pass "Existing RCR validator still passes" || fail "RCR validator regression"

TESTS=$((TESTS + 1))
python3 "$SURFACE_SCRIPT" validate 2>&1 | grep -q "ALL STARTUP SURFACE CHECKS PASS" \
  && pass "Startup surface validate passes" || fail "Surface validate regression"

# Fixture checks
for f in valid-backfill invalid-duplicate-backfill invalid-inconsistent-counts invalid-missing-rationale; do
  TESTS=$((TESTS + 1))
  fpath="$FIXTURES_DIR/$f.json"
  [ -f "$fpath" ] && pass "Fixture $f.json exists" || fail "Fixture $f.json missing"
done

echo ""
echo "======================================================================"
echo "Tests: $TESTS total  Pass: $PASS  Fail: $FAIL"
[ "$FAIL" -eq 0 ] && echo "Result: $PASS/$TESTS passed. All tests pass. ✅" && exit 0 \
  || echo "Result: $PASS/$TESTS passed. Some failed. ❌" && exit 1
