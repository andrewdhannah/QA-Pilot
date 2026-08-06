#!/usr/bin/env bash
set -euo pipefail

# QA Pilot Pipeline Layer Registry Test Runner — QA-PILOT-PIPELINE-HEALTH-LAYER-REGISTRY-1
# Tests: schema validity, registry data validity, fixture acceptance/rejection,
#        PLR rules, boundary enforcement, governance doc.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-pipeline-layer-registry.py"
SCHEMA="$REPO_ROOT/docs/schemas/qa-pilot-pipeline-layer-registry.schema.json"
REGISTRY="$REPO_ROOT/data/pipeline-layer-registry/registry.json"
GOV_DOC="$REPO_ROOT/docs/governance/QA-PILOT-PIPELINE-LAYER-REGISTRY.md"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-pipeline-layer-registry"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Pipeline Layer Registry Tests — QA-PILOT-PIPELINE-HEALTH-LAYER-REGISTRY-1"
echo "===================================================================================="
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

# ── Test 6: Registry data file exists ──
TESTS=$((TESTS + 1))
[ -f "$REGISTRY" ] && pass "Registry data file found" || fail "Registry data file not found"

# ── Test 7: Registry is valid JSON ──
TESTS=$((TESTS + 1))
python3 -c "import json; json.load(open('$REGISTRY'))" 2>/dev/null && pass "Registry is valid JSON" || fail "Registry not valid JSON"

# ── Test 8: Registry has PLR-* ID ──
TESTS=$((TESTS + 1))
RID=$(python3 -c "import json; print(json.load(open('$REGISTRY')).get('registry_id',''))" 2>/dev/null)
echo "$RID" | grep -q "^PLR-" && pass "Registry: registry_id=$RID" || fail "Registry: registry_id=$RID (expected PLR-*)"

# ── Test 9: Registry has all 15 pipeline layers (#33-#47) ──
TESTS=$((TESTS + 1))
LAYER_COUNT=$(python3 -c "import json; print(len(json.load(open('$REGISTRY')).get('layers',[])))" 2>/dev/null)
[ "$LAYER_COUNT" -eq 15 ] && pass "Registry: $LAYER_COUNT layers (#33-#47)" || fail "Registry: expected 15 layers, got $LAYER_COUNT"

# ── Test 10: Registry advisory_only=true ──
TESTS=$((TESTS + 1))
python3 -c "import json; d=json.load(open('$REGISTRY')); assert d.get('advisory_only') is True" 2>/dev/null \
  && pass "Registry: advisory_only=True" || fail "Registry: advisory_only not True"

# ── Test 11: Registry custody=qa-pilot-local ──
TESTS=$((TESTS + 1))
CUST=$(python3 -c "import json; print(json.load(open('$REGISTRY')).get('custody',''))" 2>/dev/null)
[ "$CUST" = "qa-pilot-local" ] && pass "Registry: custody=qa-pilot-local" || fail "Registry: custody=$CUST"

# ── Test 12: Registry librarian_impact=none ──
TESTS=$((TESTS + 1))
LIB=$(python3 -c "import json; print(json.load(open('$REGISTRY')).get('librarian_impact',''))" 2>/dev/null)
[ "$LIB" = "none" ] && pass "Registry: librarian_impact=none" || fail "Registry: librarian_impact=$LIB"

# ── Test 13: Governance doc exists ──
TESTS=$((TESTS + 1))
[ -f "$GOV_DOC" ] && pass "Governance doc found" || fail "Governance doc not found"

# ── Test 14: Governance doc has required sections ──
TESTS=$((TESTS + 1))
grep -q "^## 1. Purpose" "$GOV_DOC" && grep -q "^## 6. Authority" "$GOV_DOC" && grep -q "^## 7. Invariants" "$GOV_DOC" \
  && pass "Governance doc has Purpose, Authority, Invariants" || fail "Governance doc missing required sections"

# ── Test 15: Governance doc declares advisory + no-Librarian-mutation ──
TESTS=$((TESTS + 1))
grep -qi "advisory" "$GOV_DOC" && grep -qi "no Librarian mutation" "$GOV_DOC" \
  && pass "Governance doc: advisory-only, no-Librarian-mutation" || fail "Governance doc missing boundary declarations"

# ── Test 16: Valid fixture (full-chain) passes ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "valid-full-chain-33-47.json.*passes" \
  && pass "Valid full-chain fixture passes" || fail "Valid full-chain fixture check failed"

# ── Test 17: Valid fixture (minimal) passes ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "valid-minimal-chain.json.*passes" \
  && pass "Valid minimal-chain fixture passes" || fail "Valid minimal-chain fixture check failed"

# ── Test 18: Invalid duplicate slot rejected ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "invalid-duplicate-slot.json.*correctly rejected" \
  && pass "Invalid duplicate-slot correctly rejected" || fail "Invalid duplicate-slot NOT rejected"

# ── Test 19: Invalid slot gap rejected ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "invalid-missing-slot-gap.json.*correctly rejected" \
  && pass "Invalid slot-gap correctly rejected" || fail "Invalid slot-gap NOT rejected"

# ── Test 20: Invalid advisory-false rejected ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "invalid-advisory-false.json.*correctly rejected" \
  && pass "Invalid advisory-false correctly rejected" || fail "Invalid advisory-false NOT rejected"

# ── Test 21: Invalid unauthorized-extra-layer rejected ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "invalid-unauthorized-extra-layer.json.*correctly rejected" \
  && pass "Invalid unauthorized-extra-layer correctly rejected" || fail "Invalid unauthorized-extra-layer NOT rejected"

# ── Test 22: PLR-12 slot enforcement active ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "PLR-12:" \
  && pass "PLR-12: slot integrity enforcement active" || fail "PLR-12: no slot enforcement reported"

# ── Test 23: PLR-13 sprint_id ledger resolution active ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "PLR-13:" \
  && pass "PLR-13: sprint_id ledger resolution active" || fail "PLR-13: no ledger resolution reported"

# ── Test 24: All 6 fixtures present ──
TESTS=$((TESTS + 1))
EXPECTED=6
ACTUAL=$(find "$FIXTURES_DIR" -name "*.json" -maxdepth 1 2>/dev/null | wc -l | tr -d ' ')
[ "$ACTUAL" -eq "$EXPECTED" ] && pass "All $EXPECTED fixtures present" || fail "Expected $EXPECTED fixtures, found $ACTUAL"

# ── Test 25: Registry not_seal_authority >= 20 chars ──
TESTS=$((TESTS + 1))
NSA_LEN=$(python3 -c "import json; print(len(json.load(open('$REGISTRY')).get('not_seal_authority','')))" 2>/dev/null)
[ "$NSA_LEN" -ge 20 ] && pass "not_seal_authority: $NSA_LEN chars" || fail "not_seal_authority: $NSA_LEN chars (need >=20)"

# ── Test 26: Registry not_librarian_mutation_authority >= 20 chars ──
TESTS=$((TESTS + 1))
NLMA_LEN=$(python3 -c "import json; print(len(json.load(open('$REGISTRY')).get('not_librarian_mutation_authority','')))" 2>/dev/null)
[ "$NLMA_LEN" -ge 20 ] && pass "not_librarian_mutation_authority: $NLMA_LEN chars" || fail "not_librarian_mutation_authority: $NLMA_LEN chars (need >=20)"

echo ""
echo "===================================================================================="
echo "Tests: $TESTS total  Pass: $PASS  Fail: $FAIL"
[ "$FAIL" -eq 0 ] && echo "Result: $PASS/$TESTS passed. All tests pass. ✅" && exit 0 \
  || echo "Result: $PASS/$TESTS passed. Some failed. ❌" && exit 1
