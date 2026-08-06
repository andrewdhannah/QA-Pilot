#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-startup-surface-regression-snapshot.py"
SNAPSHOT="$REPO_ROOT/data/startup-surface-regression-snapshots/SRS-BASELINE-001.json"
SCHEMA="$REPO_ROOT/docs/schemas/qa-pilot-startup-surface-regression-snapshot.schema.json"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-startup-surface-regression-snapshot"
PASS=0; FAIL=0; TESTS=0
pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Startup Surface Regression Snapshot Tests"
echo "  — QA-PILOT-STARTUP-SURFACE-REGRESSION-SNAPSHOT-1"
echo "================================================================"
echo ""

TESTS=$((TESTS + 1)); [ -f "$VALIDATOR" ] && pass "Validator script found" || fail "Not found"
TESTS=$((TESTS + 1)); [ -f "$SNAPSHOT" ] && pass "Snapshot baseline found" || fail "Snapshot not found"

TESTS=$((TESTS + 1))
python3 -c "import json; json.load(open('$SNAPSHOT'))" 2>/dev/null && pass "Snapshot is valid JSON" || fail "Snapshot invalid JSON"

TESTS=$((TESTS + 1))
SID=$(python3 -c "import json; print(json.load(open('$SNAPSHOT')).get('snapshot_id',''))" 2>/dev/null)
echo "$SID" | grep -q "^SRS-" && pass "Snapshot ID: $SID" || fail "Snapshot missing SRS- ID"

TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "ALL SNAPSHOT CHECKS PASS" && pass "Live surface matches snapshot" || { fail "Snapshot mismatch"; python3 "$VALIDATOR" 2>&1 | grep "❌" | head -3; }

TESTS=$((TESTS + 1))
python3 "$VALIDATOR" --fixtures 2>&1 | grep -q "ALL FIXTURES PRESENT" && pass "All fixtures present" || fail "Missing fixtures"

TESTS=$((TESTS + 1))
[ -f "$FIXTURES_DIR/valid-snapshot-match.json" ] && pass "Valid snapshot fixture exists" || fail "Valid fixture missing"
TESTS=$((TESTS + 1))
[ -f "$FIXTURES_DIR/invalid-stale-head.json" ] && pass "Invalid stale-head fixture exists" || fail "Stale-head fixture missing"
TESTS=$((TESTS + 1))
[ -f "$FIXTURES_DIR/invalid-wrong-layer-count.json" ] && pass "Invalid wrong-count fixture exists" || fail "Wrong-count fixture missing"
TESTS=$((TESTS + 1))
[ -f "$FIXTURES_DIR/invalid-missing-rcr-section.json" ] && pass "Invalid missing-RCR fixture exists" || fail "Missing-RCR fixture missing"

TESTS=$((TESTS + 1))
python3 "/Users/andrew/Desktop/CarbideFrame/active/qa-pilot/scripts/qa_pilot_pipeline_startup_surface.py" validate 2>&1 | grep -q "ALL STARTUP SURFACE CHECKS PASS" \
  && pass "Startup surface validate still passes after snapshot" || fail "Surface validate regression"

echo ""
echo "================================================================"
echo "Tests: $TESTS total  Pass: $PASS  Fail: $FAIL"
[ "$FAIL" -eq 0 ] && echo "Result: $PASS/$TESTS passed. All tests pass. ✅" && exit 0 \
  || echo "Result: $PASS/$TESTS passed. Some failed. ❌" && exit 1
