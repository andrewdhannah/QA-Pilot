#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
V="$SCRIPT_DIR/validate-qa-pilot-advisory-review-consumer-readiness.py"
GV="$REPO_ROOT/docs/governance/QA-PILOT-ADVISORY-REVIEW-CONSUMER-READINESS.md"
D="$REPO_ROOT/docs/examples/qa-pilot-advisory-review-packet"
PASS=0; FAIL=0; TESTS=0
pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }
echo "QA Pilot Advisory Review Consumer Readiness Tests"
echo "  — QA-PILOT-ADVISORY-REVIEW-CONSUMER-READINESS-1"
echo "================================================================"
echo ""

TESTS=$((TESTS + 1)); [ -f "$V" ] && pass "Validator found" || fail "Not found"
TESTS=$((TESTS + 1))
python3 "$V" 2>&1 | grep -q "ALL CHECKS PASS" && pass "Validator ALL CHECKS PASS" || { fail "Failed"; echo "$(python3 "$V" 2>&1 | tail -3)"; }
TESTS=$((TESTS + 1)); [ -f "$GV" ] && pass "Governance doc found" || fail "Not found"
TESTS=$((TESTS + 1)); grep -q "QA Pilot is a consumer only" "$GV" && pass "Consumer-only contract declared" || fail "Missing consumer declaration"
TESTS=$((TESTS + 1)); grep -q "mode_owner.*librarian" "$GV" && pass "Librarian as mode owner declared" || fail "Missing mode owner"

for f in valid-sealed-posture-061 valid-pending-owner-review valid-evidence-gap \
         valid-contradiction-packet invalid-claims-seal-authority \
         invalid-omits-validator-evidence invalid-mutates-registry-state; do
  TESTS=$((TESTS + 1)); [ -f "$D/$f.json" ] && pass "Fixture $f.json exists" || fail "Missing $f.json"
done

TESTS=$((TESTS + 1))
python3 "$V" 2>&1 | grep -q "valid-sealed-posture-061.json.*passes" && pass "Valid sealed posture passes" || fail "Sealed posture failed"
TESTS=$((TESTS + 1))
python3 "$V" 2>&1 | grep -q "valid-pending-owner-review.json.*passes" && pass "Valid pending review passes" || fail "Pending review failed"
TESTS=$((TESTS + 1))
python3 "$V" 2>&1 | grep -q "valid-evidence-gap.json.*passes" && pass "Valid evidence gap passes" || fail "Evidence gap failed"
TESTS=$((TESTS + 1))
python3 "$V" 2>&1 | grep -q "valid-contradiction-packet.json.*passes" && pass "Valid contradiction packet passes" || fail "Contradiction failed"
TESTS=$((TESTS + 1))
python3 "$V" 2>&1 | grep -q "invalid-claims-seal-authority.json.*rejected" && pass "Invalid claims seal rejected" || fail "Claims seal NOT rejected"
TESTS=$((TESTS + 1))
python3 "$V" 2>&1 | grep -q "invalid-omits-validator-evidence.json.*rejected" && pass "Invalid omits evidence rejected" || fail "Omits evidence NOT rejected"
TESTS=$((TESTS + 1))
python3 "$V" 2>&1 | grep -q "invalid-mutates-registry-state.json.*rejected" && pass "Invalid mutates registry rejected" || fail "Mutates registry NOT rejected"

echo ""
echo "================================================================"
echo "Tests: $TESTS total  Pass: $PASS  Fail: $FAIL"
[ "$FAIL" -eq 0 ] && echo "Result: $PASS/$TESTS passed. All tests pass. ✅" && exit 0 \
  || echo "Result: $PASS/$TESTS passed. Some failed. ❌" && exit 1
