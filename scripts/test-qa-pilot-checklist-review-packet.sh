#!/usr/bin/env bash
set -euo pipefail

# QA Pilot Checklist Review Packet Test Runner — QA-PILOT-CHECKLIST-REVIEW-PACKET-1
# Tests: schema validity, fixture acceptance/rejection, validator rules,
#        boundary enforcement, governance doc, authority assertions.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-checklist-review-packet.py"
SCHEMA="$REPO_ROOT/docs/schemas/qa-pilot-checklist-review-packet.schema.json"
GOV_DOC="$REPO_ROOT/docs/governance/QA-PILOT-CHECKLIST-REVIEW-PACKET.md"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-checklist-review-packet"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Checklist Review Packet Tests — QA-PILOT-CHECKLIST-REVIEW-PACKET-1"
echo "============================================================================"
echo ""

# ── Test 1: Validator script exists ──
TESTS=$((TESTS + 1))
if [ -f "$VALIDATOR" ]; then
    pass "Validator script found"
else
    fail "Validator script not found at $VALIDATOR"
fi

# ── Test 2: Validator ALL CHECKS PASS ──
TESTS=$((TESTS + 1))
VALIDATOR_OUTPUT=$(python3 "$VALIDATOR" 2>&1) || true
if echo "$VALIDATOR_OUTPUT" | grep -q "ALL CHECKS PASS"; then
    pass "Validator ALL CHECKS PASS"
else
    fail "Validator failed"
    echo "       $(echo "$VALIDATOR_OUTPUT" | tail -3)"
fi

# ── Test 3: Schema document exists ──
TESTS=$((TESTS + 1))
if [ -f "$SCHEMA" ]; then
    pass "Schema document found"
else
    fail "Schema not found at $SCHEMA"
fi

# ── Test 4: Schema is valid JSON ──
TESTS=$((TESTS + 1))
if python3 -c "import json; json.load(open('$SCHEMA'))" 2>/dev/null; then
    pass "Schema is valid JSON"
else
    fail "Schema is not valid JSON"
fi

# ── Test 5: Schema uses Draft 2020-12 ──
TESTS=$((TESTS + 1))
SCHEMA_VERSION=$(python3 -c "import json; print(json.load(open('$SCHEMA')).get('\$schema',''))" 2>/dev/null)
if [ "$SCHEMA_VERSION" = "https://json-schema.org/draft/2020-12/schema" ]; then
    pass "Schema uses Draft 2020-12"
else
    fail "Schema version mismatch: $SCHEMA_VERSION"
fi

# ── Test 6: Governance doc exists ──
TESTS=$((TESTS + 1))
if [ -f "$GOV_DOC" ]; then
    pass "Governance doc found"
else
    fail "Governance doc not found at $GOV_DOC"
fi

# ── Test 7: Governance doc has required sections ──
TESTS=$((TESTS + 1))
if grep -q "^## 1. Purpose" "$GOV_DOC" && \
   grep -q "^## 6. Authority" "$GOV_DOC" && \
   grep -q "^## 7. Invariants" "$GOV_DOC"; then
    pass "Governance doc has Purpose, Authority, and Invariants sections"
else
    fail "Governance doc missing required sections"
fi

# ── Test 8: Governance doc declares advisory-only and no-Librarian-mutation ──
TESTS=$((TESTS + 1))
if grep -qi "advisory" "$GOV_DOC" && grep -qi "no Librarian mutation" "$GOV_DOC"; then
    pass "Governance doc declares advisory-only and no-Librarian-mutation"
else
    fail "Governance doc missing authority boundary declarations"
fi

# ── Test 9: Valid fixture exists and is valid JSON ──
TESTS=$((TESTS + 1))
VALID_FIXTURE="$FIXTURES_DIR/valid-pipeline-review-packet.json"
if [ -f "$VALID_FIXTURE" ] && python3 -c "import json; json.load(open('$VALID_FIXTURE'))" 2>/dev/null; then
    pass "Valid fixture exists and is valid JSON"
else
    fail "Valid fixture missing or invalid JSON"
fi

# ── Test 10: Valid fixture has advisory_only=true ──
TESTS=$((TESTS + 1))
ADVISORY=$(python3 -c "import json; print(json.load(open('$VALID_FIXTURE')).get('advisory_only',False))" 2>/dev/null)
if [ "$ADVISORY" = "True" ]; then
    pass "Valid fixture: advisory_only=True"
else
    fail "Valid fixture: advisory_only is $ADVISORY (expected True)"
fi

# ── Test 11: Valid fixture has qa-pilot-local custody ──
TESTS=$((TESTS + 1))
CUSTODY=$(python3 -c "import json; print(json.load(open('$VALID_FIXTURE')).get('custody',''))" 2>/dev/null)
if [ "$CUSTODY" = "qa-pilot-local" ]; then
    pass "Valid fixture: custody=qa-pilot-local"
else
    fail "Valid fixture: custody=$CUSTODY (expected qa-pilot-local)"
fi

# ── Test 12: Valid fixture has librarian_impact=none ──
TESTS=$((TESTS + 1))
LIB_IMPACT=$(python3 -c "import json; print(json.load(open('$VALID_FIXTURE')).get('librarian_impact',''))" 2>/dev/null)
if [ "$LIB_IMPACT" = "none" ]; then
    pass "Valid fixture: librarian_impact=none"
else
    fail "Valid fixture: librarian_impact=$LIB_IMPACT (expected none)"
fi

# ── Test 13: Valid fixture has not_seal_authority ──
TESTS=$((TESTS + 1))
NSA=$(python3 -c "import json; print(len(json.load(open('$VALID_FIXTURE')).get('not_seal_authority','')))" 2>/dev/null)
if [ "$NSA" -ge 20 ]; then
    pass "Valid fixture: not_seal_authority ($NSA chars)"
else
    fail "Valid fixture: not_seal_authority too short ($NSA chars, need >=20)"
fi

# ── Test 14: Valid fixture has not_librarian_mutation_authority ──
TESTS=$((TESTS + 1))
NLMA=$(python3 -c "import json; print(len(json.load(open('$VALID_FIXTURE')).get('not_librarian_mutation_authority','')))" 2>/dev/null)
if [ "$NLMA" -ge 20 ]; then
    pass "Valid fixture: not_librarian_mutation_authority ($NLMA chars)"
else
    fail "Valid fixture: not_librarian_mutation_authority too short ($NLMA chars, need >=20)"
fi

# ── Test 15: Valid fixture has item_summary with consistent totals ──
TESTS=$((TESTS + 1))
SUMMARY_OK=$(python3 -c "
import json
d = json.load(open('$VALID_FIXTURE'))
s = d.get('item_summary', {})
t = s.get('total', 0)
b = s.get('blocked', 0)
dg = s.get('degraded', 0)
r = s.get('ready', 0)
print('PASS' if t == b + dg + r else f'FAIL: {t} != {b}+{dg}+{r}')
" 2>/dev/null)
if echo "$SUMMARY_OK" | grep -q "PASS"; then
    pass "Valid fixture: item_summary totals consistent"
else
    fail "Valid fixture: $SUMMARY_OK"
fi

# ── Test 16: All fixtures present (2 valid + 4 invalid = 6) ──
TESTS=$((TESTS + 1))
EXPECTED_COUNT=6
ACTUAL_COUNT=$(find "$FIXTURES_DIR" -name "*.json" -maxdepth 1 2>/dev/null | wc -l | tr -d ' ')
if [ "$ACTUAL_COUNT" -eq "$EXPECTED_COUNT" ]; then
    pass "All $EXPECTED_COUNT fixtures present"
else
    fail "Expected $EXPECTED_COUNT fixtures, found $ACTUAL_COUNT"
fi

# ── Test 17: Invalid fixture advisory=false is rejected ──
TESTS=$((TESTS + 1))
INV_ADVISORY="$FIXTURES_DIR/invalid-advisory-false.json"
if [ -f "$INV_ADVISORY" ]; then
    VOUT=$(python3 "$VALIDATOR" 2>&1) || true
    if echo "$VOUT" | grep -q "invalid-advisory-false.json.*correctly rejected"; then
        pass "Invalid fixture advisory=false correctly rejected"
    else
        fail "Invalid fixture advisory=false was NOT rejected"
    fi
else
    fail "Invalid fixture advisory=false not found"
fi

# ── Test 18: Invalid fixture wrong custody is rejected ──
TESTS=$((TESTS + 1))
INV_CUSTODY="$FIXTURES_DIR/invalid-wrong-custody.json"
if [ -f "$INV_CUSTODY" ]; then
    VOUT=$(python3 "$VALIDATOR" 2>&1) || true
    if echo "$VOUT" | grep -q "invalid-wrong-custody.json.*correctly rejected"; then
        pass "Invalid fixture wrong custody correctly rejected"
    else
        fail "Invalid fixture wrong custody was NOT rejected"
    fi
else
    fail "Invalid fixture wrong custody not found"
fi

# ── Test 19: Invalid fixture librarian mutation is rejected ──
TESTS=$((TESTS + 1))
INV_MUTATION="$FIXTURES_DIR/invalid-librarian-mutation.json"
if [ -f "$INV_MUTATION" ]; then
    VOUT=$(python3 "$VALIDATOR" 2>&1) || true
    if echo "$VOUT" | grep -q "invalid-librarian-mutation.json.*correctly rejected"; then
        pass "Invalid fixture librarian mutation correctly rejected"
    else
        fail "Invalid fixture librarian mutation was NOT rejected"
    fi
else
    fail "Invalid fixture librarian mutation not found"
fi

# ── Test 20: Invalid fixture blocked no items is rejected ──
TESTS=$((TESTS + 1))
INV_BLOCKED="$FIXTURES_DIR/invalid-blocked-no-items.json"
if [ -f "$INV_BLOCKED" ]; then
    VOUT=$(python3 "$VALIDATOR" 2>&1) || true
    if echo "$VOUT" | grep -q "invalid-blocked-no-items.json.*correctly rejected"; then
        pass "Invalid fixture blocked no items correctly rejected"
    else
        fail "Invalid fixture blocked no items was NOT rejected"
    fi
else
    fail "Invalid fixture blocked no items not found"
fi

# ── Test 21: Second valid fixture (blocked) passes validation ──
TESTS=$((TESTS + 1))
VALID2_FIXTURE="$FIXTURES_DIR/valid-blocked-review-packet.json"
if [ -f "$VALID2_FIXTURE" ]; then
    VOUT=$(python3 "$VALIDATOR" 2>&1) || true
    if echo "$VOUT" | grep -q "valid-blocked-review-packet.json.*passes"; then
        pass "Second valid fixture (blocked) passes validation"
    else
        fail "Second valid fixture did not pass validation"
    fi
else
    fail "Second valid fixture not found"
fi

# ── Test 22: Second valid fixture has blocked_items with rationale ──
TESTS=$((TESTS + 1))
BLOCKED_ITEMS_OK=$(python3 -c "
import json
d = json.load(open('$VALID2_FIXTURE'))
items = d.get('blocked_items', [])
if len(items) > 0 and all(len(i.get('rationale','')) >= 10 for i in items):
    print('PASS')
else:
    print('FAIL')
" 2>/dev/null)
if [ "$BLOCKED_ITEMS_OK" = "PASS" ]; then
    pass "Second valid fixture: blocked_items with rationale"
else
    fail "Second valid fixture: blocked_items missing or rationale too short"
fi

# ── Test 23: Pipeline refs contain no Librarian sprint references ──
TESTS=$((TESTS + 1))
LIB_REF_COUNT=$(python3 -c "
import json
data = json.load(open('$FIXTURES_DIR/valid-pipeline-review-packet.json'))
refs = data.get('pipeline_refs', [])
lib_refs = [r for r in refs if 'librarian' in r.get('sprint_id','').lower()]
print(len(lib_refs))
" 2>/dev/null)
if [ "$LIB_REF_COUNT" -eq 0 ]; then
    pass "Pipeline refs contain no Librarian sprint references"
else
    fail "Pipeline refs contain $LIB_REF_COUNT Librarian sprint references"
fi

# ── Test 24: Valid fixture has source_checklist_id matching EC-* ──
TESTS=$((TESTS + 1))
SCI=$(python3 -c "import json; print(json.load(open('$VALID_FIXTURE')).get('source_checklist_id',''))" 2>/dev/null)
if echo "$SCI" | grep -q "^EC-"; then
    pass "Valid fixture: source_checklist_id=$SCI"
else
    fail "Valid fixture: source_checklist_id=$SCI (expected EC-* pattern)"
fi

echo ""
echo "============================================================================"
echo "Tests: $TESTS total  Pass: $PASS  Fail: $FAIL"
if [ "$FAIL" -eq 0 ]; then
    echo "Result: $PASS/$TESTS passed. All tests pass. ✅"
    exit 0
else
    echo "Result: $PASS/$TESTS passed. Some failed. ❌"
    exit 1
fi
