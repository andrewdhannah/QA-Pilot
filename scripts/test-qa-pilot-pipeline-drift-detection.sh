#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-pipeline-drift-detection.py"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-pipeline-drift-detection"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Pipeline Drift Detection Tests — QA-PILOT-PIPELINE-DRIFT-DETECTION-1"
echo "================================================================================="
echo ""

# ── Test 1: Script exists ──
TESTS=$((TESTS + 1))
if [ -f "$VALIDATOR" ]; then
    pass "Drift detection script found"
else
    fail "Not found"
fi

# ── Test 2: Live mode — no drift detected ──
TESTS=$((TESTS + 1))
VOUT=$(python3 "$VALIDATOR" 2>&1) || true
if echo "$VOUT" | grep -q "NO DRIFT DETECTED"; then
    pass "Live mode: NO DRIFT DETECTED"
else
    fail "Live mode: drift detected or error"
    echo "       $(echo "$VOUT" | tail -5)"
fi

# ── Test 3: Head match check ──
TESTS=$((TESTS + 1))
if echo "$VOUT" | grep -q "DR-1.*Match:"; then
    pass "DR-1: Sealed head matches"
else
    fail "DR-1: Sealed head mismatch"
fi

# ── Test 4: All registry layers present ──
TESTS=$((TESTS + 1))
if echo "$VOUT" | grep -q "DR-3.*registry layers present"; then
    pass "DR-3: All registry layers present (from governed registry)"
else
    fail "DR-3: Missing layers"
fi

# ── Test 5: No extra layers ──
TESTS=$((TESTS + 1))
if echo "$VOUT" | grep -q "DR-4.*No extra"; then
    pass "DR-4: No extra packet layers"
else
    fail "DR-4: Extra layers detected"
fi

# ── Test 6: PH validator agrees ──
TESTS=$((TESTS + 1))
if echo "$VOUT" | grep -q "DR-7.*PH checks pass"; then
    pass "DR-7: PH validator agrees"
else
    fail "DR-7: PH validator disagrees"
fi

# ── Test 7: Posture unchanged ──
TESTS=$((TESTS + 1))
if echo "$VOUT" | grep -q "DR-8.*boundary=harness_governed"; then
    pass "DR-8: Posture/custody unchanged"
else
    fail "DR-8: Posture changed"
fi

# ── Test 8: No authority claims ──
TESTS=$((TESTS + 1))
if echo "$VOUT" | grep -q "DR-9.*Clean"; then
    pass "DR-9: No authority claims"
else
    fail "DR-9: Authority claims found"
fi

# ── Test 9: Report mode generates formatted output ──
TESTS=$((TESTS + 1))
ROUT=$(python3 "$VALIDATOR" --report 2>&1) || true
if echo "$ROUT" | grep -q "QA Pilot Pipeline Drift Report"; then
    pass "Report mode generates drift report"
else
    fail "Report mode failed"
fi

# ── Test 10: Report shows STATUS line ──
TESTS=$((TESTS + 1))
if echo "$ROUT" | grep -q "STATUS:"; then
    pass "Report shows STATUS line"
else
    fail "Report missing STATUS"
fi

# ── Test 11: Report shows advisory notice ──
TESTS=$((TESTS + 1))
if echo "$ROUT" | grep -qi "advisory"; then
    pass "Report includes advisory notice"
else
    fail "Report missing advisory notice"
fi

# ── Test 12: Valid fixture passes ──
TESTS=$((TESTS + 1))
FOUT=$(python3 "$VALIDATOR" --fixture "$FIXTURES_DIR/valid-no-drift.json" 2>&1) || true
if echo "$FOUT" | grep -q "ALL FIXTURE CHECKS PASS"; then
    pass "Valid fixture passes"
else
    fail "Valid fixture failed"
fi

# ── Test 13: Invalid drifted fixture fails ──
TESTS=$((TESTS + 1))
IFOUT=$(python3 "$VALIDATOR" --fixture "$FIXTURES_DIR/invalid-drifted-state.json" 2>&1) || true
if echo "$IFOUT" | grep -q "FIXTURE CHECKS FAILED"; then
    pass "Invalid drifted fixture rejected"
else
    fail "Invalid drifted fixture should have failed"
fi

# ── Test 14: Bounded report count reported ──
TESTS=$((TESTS + 1))
if echo "$VOUT" | grep -q "Bounded report:"; then
    pass "DR-10: Bounded drift report"
else
    fail "DR-10: Report unbounded"
fi

# ── Test 15: Invalid missing-layer fixture fails ──
TESTS=$((TESTS + 1))
MLOUT=$(python3 "$VALIDATOR" --fixture "$FIXTURES_DIR/invalid-missing-layer.json" 2>&1) || true
if echo "$MLOUT" | grep -q "FIXTURE CHECKS FAILED"; then
    pass "Invalid missing-layer fixture rejected"
else
    fail "Invalid missing-layer fixture should have failed"
fi

# ── Test 16: Invalid duplicate-layer fixture fails ──
TESTS=$((TESTS + 1))
DLOUT=$(python3 "$VALIDATOR" --fixture "$FIXTURES_DIR/invalid-duplicate-layer.json" 2>&1) || true
if echo "$DLOUT" | grep -q "FIXTURE CHECKS FAILED"; then
    pass "Invalid duplicate-layer fixture rejected"
else
    fail "Invalid duplicate-layer fixture should have failed"
fi

# ── Test 17: Invalid unauthorized-extra fixture fails ──
TESTS=$((TESTS + 1))
UEOUT=$(python3 "$VALIDATOR" --fixture "$FIXTURES_DIR/invalid-unauthorized-extra.json" 2>&1) || true
if echo "$UEOUT" | grep -q "FIXTURE CHECKS FAILED"; then
    pass "Invalid unauthorized-extra fixture rejected"
else
    fail "Invalid unauthorized-extra fixture should have failed"
fi

# ── Test 18: DR-4 recognizes all sealed layers via registry (no false extra) ──
TESTS=$((TESTS + 1))
if echo "$VOUT" | grep -q "DR-4.*No extra"; then
    pass "DR-4: No false extra layers (dynamic pre-pipeline derivation)"
else
    fail "DR-4: Extra layers detected"
fi

# ── Test 19-22: New fixtures exist ──
for f in valid-post-seal-advancement invalid-stale-expected-count \
         invalid-extra-unsealed-layer invalid-stale-expected-range; do
  TESTS=$((TESTS + 1))
  [ -f "$FIXTURES_DIR/$f.json" ] && pass "Fixture $f.json exists" || fail "Missing $f.json"
done

echo ""
echo "================================================================================="
echo "Tests: $TESTS total"
echo "Pass:  $PASS"
echo "Fail:  $FAIL"

if [ "$FAIL" -eq 0 ]; then
    echo "Result: $PASS/$TESTS passed. All tests pass. ✅"
    exit 0
else
    echo "Result: $PASS/$TESTS passed. Some tests failed. ❌"
    exit 1
fi
