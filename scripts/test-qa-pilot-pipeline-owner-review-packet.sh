#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PACKET_SCRIPT="$SCRIPT_DIR/qa_pilot_pipeline_owner_review_packet.py"
PACKET_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-pipeline-owner-review-packet.py"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-pipeline-owner-review-packet"
P=0 F=0 T=0
pass() { P=$((P+1)); echo "  ✅ $1"; }
fail() { F=$((F+1)); echo "  ❌ $1"; }
echo "QA Pilot Owner Review Packet Tests — QA-PILOT-PIPELINE-OWNER-REVIEW-PACKET-1"
echo "============================================================================="
echo ""

T=$((T+1)); [ -f "$PACKET_SCRIPT" ] && pass "Script found" || fail "Not found"

T=$((T+1)); VOUT=$(python3 "$PACKET_VALIDATOR" 2>&1) || true
echo "$VOUT" | grep -q "ALL CHECKS PASS" && pass "Validator ALL CHECKS PASS" || fail "Validator failed"

T=$((T+1)); JOUT=$(python3 "$PACKET_SCRIPT" 2>&1) || true
ADV=$(echo "$JOUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('advisory',False))" 2>/dev/null || echo "false")
[ "$ADV" = "True" ] && pass "JSON: advisory=True" || fail "JSON: advisory missing"

T=$((T+1)); SEC=$(echo "$JOUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('sections',{})))" 2>/dev/null || echo "0")
[ "$SEC" -ge 4 ] && pass "JSON: $SEC sections" || fail "JSON: < 4 sections"

T=$((T+1)); OPT=$(echo "$JOUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('owner_options',[])))" 2>/dev/null || echo "0")
[ "$OPT" -ge 3 ] && pass "JSON: $OPT owner options" || fail "JSON: < 3 options"

T=$((T+1)); CUST=$(echo "$JOUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('custody',''))" 2>/dev/null || echo "")
[ "$CUST" = "qa-pilot-local" ] && pass "JSON: custody=$CUST" || fail "JSON: custody wrong"

T=$((T+1)); MUT=$(echo "$JOUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('librarian_mutation_authority',True))" 2>/dev/null || echo "True")
[ "$MUT" = "False" ] && pass "JSON: mutation=NONE" || fail "JSON: mutation present"

T=$((T+1)); ROUT=$(python3 "$PACKET_SCRIPT" --report 2>&1) || true
echo "$ROUT" | grep -q "Owner Review Packet" && pass "Report mode works" || fail "Report mode failed"

T=$((T+1)); echo "$ROUT" | grep -q "Owner Options" && pass "Report shows Owner Options" || fail "Report missing options"

T=$((T+1)); echo "$ROUT" | grep -qi "advisory" && pass "Report includes advisory notice" || fail "Report missing advisory"

T=$((T+1)); FO=$(python3 "$PACKET_SCRIPT" --fixture "$FIXTURES_DIR/valid-review-packet.json" 2>&1) || true
echo "$FO" | grep -q "ALL FIXTURE CHECKS PASS" && pass "Valid fixture passes" || fail "Valid fixture failed"

T=$((T+1)); IFO=$(python3 "$PACKET_SCRIPT" --fixture "$FIXTURES_DIR/invalid-authority-claim.json" 2>&1) || true
echo "$IFO" | grep -q "SOME CHECKS FAILED" && pass "Invalid fixture rejected" || fail "Invalid fixture should fail"

T=$((T+1)); RID=$(echo "$JOUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('review_id' in d)" 2>/dev/null || echo "False")
[ "$RID" = "True" ] && pass "Packet has review_id" || fail "Missing review_id"

T=$((T+1)); SUM=$(echo "$JOUT" | python3 -c "import sys,json; d=json.load(sys.stdin); s=d.get('summary',{}); print('all_sections_pass' in s)" 2>/dev/null || echo "False")
[ "$SUM" = "True" ] && pass "Packet has summary" || fail "Missing summary"

echo ""; echo "============================================================================="
echo "Tests: $T total  Pass: $P  Fail: $F"
[ "$F" -eq 0 ] && echo "Result: $P/$T passed. All tests pass. ✅" && exit 0 || echo "Result: $P/$T passed. Some failed. ❌" && exit 1
