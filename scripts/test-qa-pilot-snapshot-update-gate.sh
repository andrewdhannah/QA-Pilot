#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
V="$SCRIPT_DIR/validate-qa-pilot-snapshot-update-gate.py"
S="$REPO_ROOT/docs/schemas/qa-pilot-snapshot-update-gate.schema.json"
G="$REPO_ROOT/docs/governance/QA-PILOT-SNAPSHOT-UPDATE-GATE.md"
D="$REPO_ROOT/docs/examples/qa-pilot-snapshot-update-gate"
PASS=0; FAIL=0; TESTS=0
pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }
echo "QA Pilot Snapshot Update Gate Tests — QA-PILOT-SNAPSHOT-UPDATE-GATE-1"
echo "====================================================================="
echo ""
TESTS=$((TESTS + 1)); [ -f "$V" ] && pass "Validator found" || fail "Not found"
TESTS=$((TESTS + 1))
python3 "$V" 2>&1 | grep -q "ALL CHECKS PASS" && pass "Validator ALL CHECKS PASS" || { fail "Failed"; echo "$(python3 "$V" 2>&1 | tail -3)"; }
TESTS=$((TESTS + 1)); [ -f "$S" ] && pass "Schema found" || fail "Schema not found"
TESTS=$((TESTS + 1)); python3 -c "import json; json.load(open('$S'))" && pass "Schema valid JSON" || fail "Schema invalid"
TESTS=$((TESTS + 1)); [ -f "$G" ] && pass "Governance doc found" || fail "Gov doc not found"
for f in valid-legitimate-update valid-no-update-required invalid-stale-baseline \
         invalid-short-rationale invalid-masking-regression invalid-unjustified-downgrade; do
  TESTS=$((TESTS + 1))
  [ -f "$D/$f.json" ] && pass "Fixture $f.json exists" || fail "Fixture $f.json missing"
done
TESTS=$((TESTS + 1))
EXP=6; ACT=$(find "$D" -name "*.json" | wc -l | tr -d ' ')
[ "$ACT" -eq "$EXP" ] && pass "All $EXP fixtures present" || fail "Expected $EXP found $ACT"
TESTS=$((TESTS + 1))
python3 "$V" 2>&1 | grep -q "valid-legitimate-update.json.*passes" && pass "Valid update passes" || fail "Valid update failed"
TESTS=$((TESTS + 1))
python3 "$V" 2>&1 | grep -q "valid-no-update-required.json.*passes" && pass "Valid no-update passes" || fail "Valid no-update failed"
TESTS=$((TESTS + 1))
python3 "$V" 2>&1 | grep -q "invalid-stale-baseline.json.*rejected" && pass "Invalid stale rejected" || fail "Stale NOT rejected"
TESTS=$((TESTS + 1))
python3 "$V" 2>&1 | grep -q "SUG-9:" && pass "SUG-9: rationale enforcement active" || fail "SUG-9 missing"
TESTS=$((TESTS + 1))
python3 "$V" 2>&1 | grep -q "SUG-11:" && pass "SUG-11: stale snapshot enforcement active" || fail "SUG-11 missing"
echo ""
echo "====================================================================="
echo "Tests: $TESTS total  Pass: $PASS  Fail: $FAIL"
[ "$FAIL" -eq 0 ] && echo "Result: $PASS/$TESTS passed. All tests pass. ✅" && exit 0 \
  || echo "Result: $PASS/$TESTS passed. Some failed. ❌" && exit 1
