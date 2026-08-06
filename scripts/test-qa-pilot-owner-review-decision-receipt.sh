#!/usr/bin/env bash
set -euo pipefail
SD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RR="$(cd "$SD/.." && pwd)"
S="$SD/qa_pilot_owner_review_decision_receipt.py"
V="$SD/validate-qa-pilot-owner-review-decision-receipt.py"
P=0 F=0 T=0
pass() { P=$((P+1)); echo "  ✅ $1"; }
fail() { F=$((F+1)); echo "  ❌ $1"; }
cleanup() { python3 "$S" clear >/dev/null 2>&1 || true; }
echo "Owner Decision Receipt Tests — QA-PILOT-OWNER-REVIEW-DECISION-RECEIPT-1"
echo "======================================================================="
echo ""

cleanup
T=$((T+1)); [ -f "$S" ] && pass "Script found" || fail "Not found"
T=$((T+1)); VOUT=$(python3 "$V" 2>&1); echo "$VOUT" | grep -q "ALL CHECKS PASS" && pass "Validator passes" || fail "Validator failed"

T=$((T+1)); R1=$(python3 "$S" record accept --note "Test accept" 2>&1)
S1=$(echo "$R1" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success',False))" 2>/dev/null); [ "$S1" = "True" ] && pass "Record accept" || fail "Record accept failed"

T=$((T+1)); R2=$(python3 "$S" record authorize --note "Test authorize" 2>&1)
S2=$(echo "$R2" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success',False))" 2>/dev/null); [ "$S2" = "True" ] && pass "Record authorize" || fail "Record authorize failed"

T=$((T+1)); R3=$(python3 "$S" record defer 2>&1)
S3=$(echo "$R3" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success',False))" 2>/dev/null); [ "$S3" = "True" ] && pass "Record defer" || fail "Record defer failed"

T=$((T+1)); R4=$(python3 "$S" record reject 2>&1)
S4=$(echo "$R4" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success',False))" 2>/dev/null); [ "$S4" = "True" ] && pass "Record reject" || fail "Record reject failed"

T=$((T+1)); LOUT=$(python3 "$S" list 2>&1); LCNT=$(echo "$LOUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('total',0))" 2>/dev/null); [ "$LCNT" -ge 4 ] && pass "List $LCNT receipts" || fail "List < 4"

T=$((T+1)); SOUT=$(python3 "$S" status 2>&1); SCNT=$(echo "$SOUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('total',0))" 2>/dev/null); [ "$SCNT" -ge 4 ] && pass "Status $SCNT receipts" || fail "Status < 4"

T=$((T+1)); ADV=$(echo "$R1" | python3 -c "import sys,json; print(json.load(sys.stdin).get('advisory_only',False))" 2>/dev/null); [ "$ADV" = "True" ] && pass "Response advisory_only=True" || fail "Missing advisory_only"

T=$((T+1)); CUS=$(echo "$R1" | python3 -c "import sys,json; print(json.load(sys.stdin).get('custody',''))" 2>/dev/null); [ "$CUS" = "qa-pilot-local" ] && pass "Custody qa-pilot-local" || fail "Wrong custody"

T=$((T+1)); ECHO=$(echo "$R1" | python3 -c "import sys,json; d=json.load(sys.stdin); r=d.get('receipt',{}); print(r.get('librarian_mutation_authority',True))" 2>/dev/null); [ "$ECHO" = "False" ] && pass "Mutation authority NONE" || fail "Mutation present"

T=$((T+1)); DID=$(echo "$R1" | python3 -c "import sys,json; print(json.load(sys.stdin).get('receipt_id',''))" 2>/dev/null)
[ -n "$DID" ] && RDOUT=$(python3 "$S" read "$DID" 2>&1) && RDFOUND=$(echo "$RDOUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('found',False))" 2>/dev/null) && [ "$RDFOUND" = "True" ] && pass "Read $DID" || fail "Read failed"

T=$((T+1)); COUT=$(python3 "$S" clear 2>&1); CC=$(echo "$COUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('cleared',0))" 2>/dev/null); [ "$CC" -ge 4 ] && pass "Clear $CC receipts" || fail "Clear failed"

T=$((T+1)); EMPTY=$(python3 "$S" list 2>&1); EC=$(echo "$EMPTY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('total',999))" 2>/dev/null); [ "$EC" -eq 0 ] && pass "Store empty after clear" || fail "Store not empty"

cleanup
echo ""; echo "======================================================================="
echo "Tests: $T total  Pass: $P  Fail: $F"
[ "$F" -eq 0 ] && echo "Result: $P/$T passed. All tests pass. ✅" && exit 0 || echo "Result: $P/$T passed. Some failed. ❌" && exit 1
