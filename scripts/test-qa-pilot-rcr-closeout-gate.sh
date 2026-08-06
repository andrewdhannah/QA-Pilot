#!/usr/bin/env bash
set -euo pipefail

# QA Pilot RCR Closeout Gate Test Runner — QA-PILOT-REGISTRY-CHANGE-RECEIPT-CLOSEOUT-GATE-1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-rcr-closeout-gate.py"
SCHEMA="$REPO_ROOT/docs/schemas/qa-pilot-rcr-closeout-gate.schema.json"
GOV_DOC="$REPO_ROOT/docs/governance/QA-PILOT-RCR-CLOSEOUT-GATE.md"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-rcr-closeout-gate"
PASS=0; FAIL=0; TESTS=0
pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot RCR Closeout Gate Tests — QA-PILOT-REGISTRY-CHANGE-RECEIPT-CLOSEOUT-GATE-1"
echo "===================================================================================="
echo ""

TESTS=$((TESTS + 1)); [ -f "$VALIDATOR" ] && pass "Validator script found" || fail "Not found"

TESTS=$((TESTS + 1))
VOUT=$(python3 "$VALIDATOR" 2>&1) || true
echo "$VOUT" | grep -q "ALL CHECKS PASS" && pass "Validator ALL CHECKS PASS" || { fail "Validator failed"; echo "       $(echo "$VOUT" | tail -3)"; }

TESTS=$((TESTS + 1)); [ -f "$SCHEMA" ] && pass "Schema found" || fail "Schema not found"

TESTS=$((TESTS + 1))
python3 -c "import json; json.load(open('$SCHEMA'))" 2>/dev/null && pass "Schema valid JSON" || fail "Schema invalid"

TESTS=$((TESTS + 1))
SV=$(python3 -c "import json; print(json.load(open('$SCHEMA')).get('\$schema',''))" 2>/dev/null)
[ "$SV" = "https://json-schema.org/draft/2020-12/schema" ] && pass "Schema Draft 2020-12" || fail "Schema version: $SV"

TESTS=$((TESTS + 1)); [ -f "$GOV_DOC" ] && pass "Governance doc found" || fail "Governance doc not found"

TESTS=$((TESTS + 1))
grep -q "^## 1. Purpose" "$GOV_DOC" && grep -q "^## 6. Authority" "$GOV_DOC" && grep -q "^## 7. Invariants" "$GOV_DOC" \
  && pass "Gov doc has Purpose, Authority, Invariants" || fail "Gov doc missing required sections"

TESTS=$((TESTS + 1))
grep -qi "advisory" "$GOV_DOC" && grep -qi "no Librarian mutation" "$GOV_DOC" \
  && pass "Gov doc: advisory, no-Librarian-mutation" || fail "Gov doc missing boundaries"

# Valid fixtures
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "valid-ready-adds-layer.json.*passes" \
  && pass "Valid adds-layer fixture passes" || fail "Valid adds-layer check failed"

TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "valid-ready-no-impact.json.*passes" \
  && pass "Valid no-impact fixture passes" || fail "Valid no-impact check failed"

# Invalid fixtures
for fixture in "invalid-missing-rcr-receipt" "invalid-no-impact-rationale-too-short" \
               "invalid-rcr-receipt-not-in-data" "invalid-inconsistent-layer-counts"; do
  TESTS=$((TESTS + 1))
  python3 "$VALIDATOR" 2>&1 | grep -q "$fixture.json.*correctly rejected" \
    && pass "Invalid $fixture rejected" || fail "Invalid $fixture NOT rejected"
done

TESTS=$((TESTS + 1))
EXPECTED=6; ACTUAL=$(find "$FIXTURES_DIR" -name "*.json" -maxdepth 1 2>/dev/null | wc -l | tr -d ' ')
[ "$ACTUAL" -eq "$EXPECTED" ] && pass "All $EXPECTED fixtures present" || fail "Expected $EXPECTED found $ACTUAL"

TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "RCG-9:" && pass "RCG-9: RCR receipt enforcement active" || fail "RCG-9 not reported"

TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "RCG-10:" && pass "RCG-10: rationale length enforcement active" || fail "RCG-10 not reported"

TESTS=$((TESTS + 1))
GID=$(python3 -c "import json; print(json.load(open('$FIXTURES_DIR/valid-ready-adds-layer.json')).get('gate_id',''))" 2>/dev/null)
echo "$GID" | grep -q "^RCG-" && pass "gate_id=$GID" || fail "gate_id=$GID (expected RCG-*)"

echo ""
echo "===================================================================================="
echo "Tests: $TESTS total  Pass: $PASS  Fail: $FAIL"
[ "$FAIL" -eq 0 ] && echo "Result: $PASS/$TESTS passed. All tests pass. ✅" && exit 0 \
  || echo "Result: $PASS/$TESTS passed. Some failed. ❌" && exit 1
