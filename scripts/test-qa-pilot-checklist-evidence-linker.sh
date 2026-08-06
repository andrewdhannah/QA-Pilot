#!/usr/bin/env bash
set -euo pipefail

# QA Pilot Checklist Evidence Linker Test Runner — QA-PILOT-CHECKLIST-EVIDENCE-LINKER-1
# Tests: schema validity, fixture acceptance/rejection, validator rules,
#        aggregate consistency, boundary enforcement, governance doc.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-checklist-evidence-linker.py"
SCHEMA="$REPO_ROOT/docs/schemas/qa-pilot-checklist-evidence-linker.schema.json"
GOV_DOC="$REPO_ROOT/docs/governance/QA-PILOT-CHECKLIST-EVIDENCE-LINKER.md"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-checklist-evidence-linker"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Checklist Evidence Linker Tests — QA-PILOT-CHECKLIST-EVIDENCE-LINKER-1"
echo "==============================================================================="
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

# ── Test 9: Valid fixture exists and is valid JSON ──
TESTS=$((TESTS + 1))
VF1="$FIXTURES_DIR/valid-all-found.json"
[ -f "$VF1" ] && python3 -c "import json; json.load(open('$VF1'))" 2>/dev/null \
  && pass "Valid fixture (all-found) exists and is valid JSON" || fail "Valid fixture missing or invalid"

# ── Test 10: Valid fixture has EL-* linker_id ──
TESTS=$((TESTS + 1))
LID=$(python3 -c "import json; print(json.load(open('$VF1')).get('linker_id',''))" 2>/dev/null)
echo "$LID" | grep -q "^EL-" && pass "Valid fixture: linker_id=$LID" || fail "Valid fixture: linker_id=$LID (expected EL-*)"

# ── Test 11: Valid fixture has advisory_only=true ──
TESTS=$((TESTS + 1))
python3 -c "import json; d=json.load(open('$VF1')); assert d.get('advisory_only') is True" 2>/dev/null \
  && pass "Valid fixture: advisory_only=True" || fail "Valid fixture: advisory_only not True"

# ── Test 12: Valid fixture has custody=qa-pilot-local ──
TESTS=$((TESTS + 1))
CUST=$(python3 -c "import json; print(json.load(open('$VF1')).get('custody',''))" 2>/dev/null)
[ "$CUST" = "qa-pilot-local" ] && pass "Valid fixture: custody=qa-pilot-local" || fail "Valid fixture: custody=$CUST"

# ── Test 13: Valid fixture has librarian_impact=none ──
TESTS=$((TESTS + 1))
LIB=$(python3 -c "import json; print(json.load(open('$VF1')).get('librarian_impact',''))" 2>/dev/null)
[ "$LIB" = "none" ] && pass "Valid fixture: librarian_impact=none" || fail "Valid fixture: librarian_impact=$LIB"

# ── Test 14: Valid fixture has aggregate all_found=true when all links found ──
TESTS=$((TESTS + 1))
AF=$(python3 -c "import json; d=json.load(open('$VF1')); print(d.get('aggregate',{}).get('all_found',False))" 2>/dev/null)
STATUSES=$(python3 -c "import json; d=json.load(open('$VF1')); ls=d.get('links',[]); print(any(l.get('status')!='found' for l in ls))" 2>/dev/null)
if [ "$AF" = "True" ] && [ "$STATUSES" = "False" ]; then
  pass "Valid fixture: all_found=true with all links found"
else
  fail "Valid fixture: all_found=$AF but status check=$STATUSES"
fi

# ── Test 15: Valid fixture (some-missing) has correct aggregate ──
TESTS=$((TESTS + 1))
VF2="$FIXTURES_DIR/valid-some-missing.json"
AG_OK=$(python3 -c "
import json
d=json.load(open('$VF2'))
a=d.get('aggregate',{})
l=d.get('links',[])
actual_found=sum(1 for x in l if x.get('status')=='found')
actual_missing=sum(1 for x in l if x.get('status')=='missing')
print('PASS' if a['found']==actual_found and a['missing']==actual_missing and a['total_links']==len(l) else 'FAIL')
" 2>/dev/null)
[ "$AG_OK" = "PASS" ] && pass "Valid fixture (some-missing): aggregate consistent" || fail "Valid fixture (some-missing): aggregate mismatch"

# ── Test 16: All 6 fixtures present ──
TESTS=$((TESTS + 1))
EXPECTED=6
ACTUAL=$(find "$FIXTURES_DIR" -name "*.json" -maxdepth 1 2>/dev/null | wc -l | tr -d ' ')
[ "$ACTUAL" -eq "$EXPECTED" ] && pass "All $EXPECTED fixtures present" || fail "Expected $EXPECTED fixtures, found $ACTUAL"

# ── Test 17: Invalid fixture advisory=false rejected ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "invalid-advisory-false.json.*correctly rejected" \
  && pass "Invalid fixture advisory=false correctly rejected" || fail "Invalid fixture advisory=false NOT rejected"

# ── Test 18: Invalid fixture wrong custody rejected ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "invalid-wrong-custody.json.*correctly rejected" \
  && pass "Invalid fixture wrong custody correctly rejected" || fail "Invalid fixture wrong custody NOT rejected"

# ── Test 19: Invalid fixture aggregate mismatch rejected ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "invalid-aggregate-mismatch.json.*correctly rejected" \
  && pass "Invalid fixture aggregate mismatch correctly rejected" || fail "Invalid fixture aggregate mismatch NOT rejected"

# ── Test 20: Invalid fixture missing no refs list rejected ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "invalid-missing-no-refs-list.json.*correctly rejected" \
  && pass "Invalid fixture missing no refs list correctly rejected" || fail "Invalid fixture missing no refs list NOT rejected"

# ── Test 21: Pipeline refs contain no Librarian sprint references ──
TESTS=$((TESTS + 1))
LIB_REFS=$(python3 -c "
import json
d=json.load(open('$FIXTURES_DIR/valid-all-found.json'))
refs=d.get('pipeline_refs',[])
lib=[r for r in refs if 'librarian' in r.get('sprint_id','').lower()]
print(len(lib))
" 2>/dev/null)
[ "$LIB_REFS" -eq 0 ] && pass "Pipeline refs: no Librarian sprint references" || fail "Pipeline refs: $LIB_REFS Librarian refs"

# ── Test 22: Valid fixture has EC-* source_checklist_id ──
TESTS=$((TESTS + 1))
SCI=$(python3 -c "import json; print(json.load(open('$VF1')).get('source_checklist_id',''))" 2>/dev/null)
echo "$SCI" | grep -q "^EC-" && pass "source_checklist_id=$SCI" || fail "source_checklist_id=$SCI (expected EC-*)"

# ── Test 23: Valid fixture has not_seal_authority >= 20 chars ──
TESTS=$((TESTS + 1))
NSA_LEN=$(python3 -c "import json; print(len(json.load(open('$VF1')).get('not_seal_authority','')))" 2>/dev/null)
[ "$NSA_LEN" -ge 20 ] && pass "not_seal_authority: $NSA_LEN chars" || fail "not_seal_authority: $NSA_LEN chars (need >=20)"

# ── Test 24: Valid fixture has not_librarian_mutation_authority >= 20 chars ──
TESTS=$((TESTS + 1))
NLMA_LEN=$(python3 -c "import json; print(len(json.load(open('$VF1')).get('not_librarian_mutation_authority','')))" 2>/dev/null)
[ "$NLMA_LEN" -ge 20 ] && pass "not_librarian_mutation_authority: $NLMA_LEN chars" || fail "not_librarian_mutation_authority: $NLMA_LEN chars (need >=20)"

echo ""
echo "==============================================================================="
echo "Tests: $TESTS total  Pass: $PASS  Fail: $FAIL"
[ "$FAIL" -eq 0 ] && echo "Result: $PASS/$TESTS passed. All tests pass. ✅" && exit 0 \
  || echo "Result: $PASS/$TESTS passed. Some failed. ❌" && exit 1
