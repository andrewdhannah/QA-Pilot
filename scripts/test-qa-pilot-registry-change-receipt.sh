#!/usr/bin/env bash
set -euo pipefail

# QA Pilot Registry Change Receipt Test Runner — QA-PILOT-REGISTRY-CHANGE-RECEIPT-1
# Tests: schema validity, fixture acceptance/rejection, RCR rules,
#        boundary enforcement, governance doc.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-registry-change-receipt.py"
SCHEMA="$REPO_ROOT/docs/schemas/qa-pilot-registry-change-receipt.schema.json"
GOV_DOC="$REPO_ROOT/docs/governance/QA-PILOT-REGISTRY-CHANGE-RECEIPT.md"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-registry-change-receipt"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Registry Change Receipt Tests — QA-PILOT-REGISTRY-CHANGE-RECEIPT-1"
echo "=============================================================================="
echo ""

# ── Test 1: Validator script exists ──
TESTS=$((TESTS + 1))
[ -f "$VALIDATOR" ] && pass "Validator script found" || fail "Validator script not found"

# ── Test 2: Validator ALL CHECKS PASS ──
TESTS=$((TESTS + 1))
VOUT=$(python3 "$VALIDATOR" 2>&1) || true
echo "$VOUT" | grep -q "ALL CHECKS PASS" && pass "Validator ALL CHECKS PASS" || { fail "Validator failed"; echo "       $(echo "$VOUT" | tail -3)"; }

# ── Test 3: Schema exists ──
TESTS=$((TESTS + 1))
[ -f "$SCHEMA" ] && pass "Schema document found" || fail "Schema not found"

# ── Test 4: Schema is valid JSON ──
TESTS=$((TESTS + 1))
python3 -c "import json; json.load(open('$SCHEMA'))" 2>/dev/null && pass "Schema is valid JSON" || fail "Schema not valid JSON"

# ── Test 5: Schema uses Draft 2020-12 ──
TESTS=$((TESTS + 1))
SV=$(python3 -c "import json; print(json.load(open('$SCHEMA')).get('\$schema',''))" 2>/dev/null)
[ "$SV" = "https://json-schema.org/draft/2020-12/schema" ] && pass "Schema uses Draft 2020-12" || fail "Schema version: $SV"

# ── Test 6: Governance doc exists ──
TESTS=$((TESTS + 1))
[ -f "$GOV_DOC" ] && pass "Governance doc found" || fail "Governance doc not found"

# ── Test 7: Governance doc has required sections ──
TESTS=$((TESTS + 1))
grep -q "^## 1. Purpose" "$GOV_DOC" && grep -q "^## 6. Authority" "$GOV_DOC" && grep -q "^## 7. Invariants" "$GOV_DOC" \
  && pass "Governance doc has Purpose, Authority, Invariants" || fail "Governance doc missing required sections"

# ── Test 8: Governance doc declares advisory + no-Librarian-mutation ──
TESTS=$((TESTS + 1))
grep -qi "advisory" "$GOV_DOC" && grep -qi "no Librarian mutation" "$GOV_DOC" \
  && pass "Governance doc: advisory-only, no-Librarian-mutation" || fail "Governance doc missing boundary declarations"

# ── Test 9: Valid adds-layer fixture passes ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "valid-adds-layer.json.*passes" \
  && pass "Valid adds-layer fixture passes" || fail "Valid adds-layer fixture check failed"

# ── Test 10: Valid no-impact fixture passes ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "valid-no-impact.json.*passes" \
  && pass "Valid no-impact fixture passes" || fail "Valid no-impact fixture check failed"

# ── Test 11: Valid updates-layer fixture passes ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "valid-updates-layer.json.*passes" \
  && pass "Valid updates-layer fixture passes" || fail "Valid updates-layer fixture check failed"

# ── Test 12: Valid deprecates-layer fixture passes ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "valid-deprecates-layer.json.*passes" \
  && pass "Valid deprecates-layer fixture passes" || fail "Valid deprecates-layer fixture check failed"

# ── Test 13: Invalid no-impact rationale too short rejected ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "invalid-no-impact-rationale-too-short.json.*correctly rejected" \
  && pass "Invalid no-impact rationale rejected" || fail "Invalid no-impact rationale NOT rejected"

# ── Test 14: Invalid advisory-false rejected ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "invalid-advisory-false.json.*correctly rejected" \
  && pass "Invalid advisory-false rejected" || fail "Invalid advisory-false NOT rejected"

# ── Test 15: Invalid layer-count mismatch rejected ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "invalid-layer-count-mismatch.json.*correctly rejected" \
  && pass "Invalid layer-count mismatch rejected" || fail "Invalid layer-count mismatch NOT rejected"

# ── Test 16: Invalid brief summaries rejected ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "invalid-brief-summaries-and-disclaimers.json.*correctly rejected" \
  && pass "Invalid brief summaries rejected" || fail "Invalid brief summaries NOT rejected"

# ── Test 17: All 8 fixtures present ──
TESTS=$((TESTS + 1))
EXPECTED=8
ACTUAL=$(find "$FIXTURES_DIR" -name "*.json" -maxdepth 1 2>/dev/null | wc -l | tr -d ' ')
[ "$ACTUAL" -eq "$EXPECTED" ] && pass "All $EXPECTED fixtures present" || fail "Expected $EXPECTED fixtures, found $ACTUAL"

# ── Test 18: RCR-13 layer count enforcement active ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "RCR-13:" \
  && pass "RCR-13: layer count consistency enforcement active" || fail "RCR-13: no layer count enforcement reported"

# ── Test 19: RCR-10 no-impact rationale enforcement active ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "RCR-10:" \
  && pass "RCR-10: no-impact rationale length enforcement active" || fail "RCR-10: no enforcement reported"

# ── Test 20: Valid fixture has RCR-* receipt_id ──
TESTS=$((TESTS + 1))
LID=$(python3 -c "import json; print(json.load(open('$FIXTURES_DIR/valid-adds-layer.json')).get('receipt_id',''))" 2>/dev/null)
echo "$LID" | grep -q "^RCR-" && pass "Valid fixture: receipt_id=$LID" || fail "Valid fixture: receipt_id=$LID (expected RCR-*)"

echo ""
echo "=============================================================================="
echo "Tests: $TESTS total  Pass: $PASS  Fail: $FAIL"
[ "$FAIL" -eq 0 ] && echo "Result: $PASS/$TESTS passed. All tests pass. ✅" && exit 0 \
  || echo "Result: $PASS/$TESTS passed. Some failed. ❌" && exit 1
