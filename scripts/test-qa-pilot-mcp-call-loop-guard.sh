#!/usr/bin/env bash
set -euo pipefail

# QA Pilot MCP Call Loop Guard Test Runner — QA-PILOT-MCP-CALL-LOOP-GUARD-1
# Tests: schema validity, fixture acceptance/rejection, validator rules,
#        aggregate consistency, boundary enforcement, governance doc.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-mcp-call-loop-guard.py"
SCHEMA="$REPO_ROOT/docs/schemas/qa-pilot-mcp-call-loop-guard.schema.json"
GOV_DOC="$REPO_ROOT/docs/governance/QA-PILOT-MCP-CALL-LOOP-GUARD.md"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-mcp-call-loop-guard"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot MCP Call Loop Guard Tests — QA-PILOT-MCP-CALL-LOOP-GUARD-1"
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

# ── Test 9: Valid fixture (bounded-startup) exists and is valid JSON ──
TESTS=$((TESTS + 1))
VF1="$FIXTURES_DIR/valid-bounded-startup-only.json"
[ -f "$VF1" ] && python3 -c "import json; json.load(open('$VF1'))" 2>/dev/null \
  && pass "Valid fixture (bounded-startup) exists and is valid JSON" || fail "Valid fixture missing or invalid"

# ── Test 10: Valid fixture has MG-* guard_id ──
TESTS=$((TESTS + 1))
LID=$(python3 -c "import json; print(json.load(open('$VF1')).get('guard_id',''))" 2>/dev/null)
echo "$LID" | grep -q "^MG-" && pass "Valid fixture: guard_id=$LID" || fail "Valid fixture: guard_id=$LID (expected MG-*)"

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

# ── Test 14: Valid fixture aggregate — bounded=true, stop_reason_present=true ──
TESTS=$((TESTS + 1))
AG_OK=$(python3 -c "
import json
d=json.load(open('$VF1'))
a=d.get('aggregate',{})
print('PASS' if a.get('bounded') and a.get('stop_reason_present') and a.get('no_auto_retry_loop') and a.get('terminal_result_recognized') else 'FAIL')
" 2>/dev/null)
[ "$AG_OK" = "PASS" ] && pass "Valid fixture: bounded, stop_reason, no_retry, terminal_recognized" || fail "Valid fixture: aggregate guard flags not all set"

# ── Test 15: Valid fixture (impl-no-mcp) has correct aggregate ──
TESTS=$((TESTS + 1))
VF2="$FIXTURES_DIR/valid-implementation-no-mcp.json"
AG_OK2=$(python3 -c "
import json
d=json.load(open('$VF2'))
a=d.get('aggregate',{})
l=d.get('mcp_calls',[])
print('PASS' if a['total_calls']==len(l) and a['repeated_identical_calls']==0 and a['cross_lane_detected']==False else 'FAIL')
" 2>/dev/null)
[ "$AG_OK2" = "PASS" ] && pass "Valid fixture (impl-no-mcp): aggregate consistent" || fail "Valid fixture (impl-no-mcp): aggregate mismatch"

# ── Test 16: All 6 fixtures present ──
TESTS=$((TESTS + 1))
EXPECTED=6
ACTUAL=$(find "$FIXTURES_DIR" -name "*.json" -maxdepth 1 2>/dev/null | wc -l | tr -d ' ')
[ "$ACTUAL" -eq "$EXPECTED" ] && pass "All $EXPECTED fixtures present" || fail "Expected $EXPECTED fixtures, found $ACTUAL"

# ── Test 17: Invalid repeated-identical-calls rejected ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "invalid-repeated-identical-calls.json.*correctly rejected" \
  && pass "Invalid repeated-identical-calls correctly rejected" || fail "Invalid repeated-identical-calls NOT rejected"

# ── Test 18: Invalid no-stop-reason rejected ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "invalid-no-stop-reason.json.*correctly rejected" \
  && pass "Invalid no-stop-reason correctly rejected" || fail "Invalid no-stop-reason NOT rejected"

# ── Test 19: Invalid cross-lane-unauthorized rejected ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "invalid-cross-lane-unauthorized.json.*correctly rejected" \
  && pass "Invalid cross-lane-unauthorized correctly rejected" || fail "Invalid cross-lane-unauthorized NOT rejected"

# ── Test 20: Invalid auto-retry-loop rejected ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "invalid-auto-retry-loop.json.*correctly rejected" \
  && pass "Invalid auto-retry-loop correctly rejected" || fail "Invalid auto-retry-loop NOT rejected"

# ── Test 21: MG-8 enforcement verified (repeated identical calls flagged) ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "MG-8:" \
  && pass "MG-8: repeated identical call detection active" || fail "MG-8: no repeated call detections reported"

# ── Test 22: MG-9 enforcement verified (repeated health checks flagged) ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "MG-9:" \
  && pass "MG-9: repeated health check detection active" || fail "MG-9: no health check detections reported"

# ── Test 23: MG-10 enforcement verified (cross-lane calls flagged) ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "MG-10:" \
  && pass "MG-10: cross-lane detection active" || fail "MG-10: no cross-lane detections reported"

# ── Test 24: MG-12 enforcement verified (stop reason enforcement) ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "MG-12:" \
  && pass "MG-12: stop reason enforcement active" || fail "MG-12: no stop reason enforcement reported"

# ── Test 25: MG-13 enforcement verified (auto-retry loop detection) ──
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" 2>&1 | grep -q "MG-13:" \
  && pass "MG-13: auto-retry loop detection active" || fail "MG-13: no auto-retry detections reported"

# ── Test 26: Valid fixture has not_seal_authority >= 20 chars ──
TESTS=$((TESTS + 1))
NSA_LEN=$(python3 -c "import json; print(len(json.load(open('$VF1')).get('not_seal_authority','')))" 2>/dev/null)
[ "$NSA_LEN" -ge 20 ] && pass "not_seal_authority: $NSA_LEN chars" || fail "not_seal_authority: $NSA_LEN chars (need >=20)"

# ── Test 27: Valid fixture has not_librarian_mutation_authority >= 20 chars ──
TESTS=$((TESTS + 1))
NLMA_LEN=$(python3 -c "import json; print(len(json.load(open('$VF1')).get('not_librarian_mutation_authority','')))" 2>/dev/null)
[ "$NLMA_LEN" -ge 20 ] && pass "not_librarian_mutation_authority: $NLMA_LEN chars" || fail "not_librarian_mutation_authority: $NLMA_LEN chars (need >=20)"

echo ""
echo "==============================================================================="
echo "Tests: $TESTS total  Pass: $PASS  Fail: $FAIL"
[ "$FAIL" -eq 0 ] && echo "Result: $PASS/$TESTS passed. All tests pass. ✅" && exit 0 \
  || echo "Result: $PASS/$TESTS passed. Some failed. ❌" && exit 1
