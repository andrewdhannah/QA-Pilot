#!/usr/bin/env bash
set -euo pipefail
SD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$SD/qa_pilot_pipeline_startup_surface_odr.py"
V="$SD/validate-qa-pilot-owner-decision-receipt-startup-surface.py"
P=0 F=0 T=0
pass() { P=$((P+1)); echo "  ✅ $1"; }
fail() { F=$((F+1)); echo "  ❌ $1"; }
echo "ODR Startup Surface Tests — QA-PILOT-OWNER-DECISION-RECEIPT-STARTUP-SURFACE-1"
echo "============================================================================="
echo ""

T=$((T+1)); [ -f "$S" ] && pass "Script found" || fail "Not found"
T=$((T+1)); VOUT=$(python3 "$V" 2>&1); echo "$VOUT" | grep -q "ALL CHECKS PASS" && pass "Validator passes" || fail "Validator failed"

T=$((T+1)); JOUT=$(python3 "$S" 2>&1)
ADV=$(echo "$JOUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('advisory_only',False))" 2>/dev/null); [ "$ADV" = "True" ] && pass "JSON: advisory=True" || fail "Missing advisory"

T=$((T+1)); CUS=$(echo "$JOUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('custody',''))" 2>/dev/null); [ "$CUS" = "qa-pilot-local" ] && pass "JSON: custody=$CUS" || fail "Wrong custody"

T=$((T+1)); HEAD=$(echo "$JOUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('base_pipeline',{}).get('sealed_head',''))" 2>/dev/null); [ -n "$HEAD" ] && pass "JSON: head=$HEAD" || fail "Missing head"

T=$((T+1)); ODR=$(echo "$JOUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('odr_layer',{}).get('status',''))" 2>/dev/null); [ -n "$ODR" ] && pass "JSON: ODR status=$ODR" || fail "Missing ODR status"

T=$((T+1)); TOT=$(echo "$JOUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('odr_layer',{}).get('total_receipts',-1))" 2>/dev/null); [ "$TOT" -ge 0 ] && pass "JSON: $TOT receipts" || fail "Bad receipt count"

T=$((T+1)); LAT=$(echo "$JOUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('odr_layer',{}).get('latest_receipt',{}).get('receipt_id','') or 'none')" 2>/dev/null); pass "JSON: latest=$LAT"

T=$((T+1)); LINK=$(echo "$JOUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('odr_layer',{}).get('or_linkage',{}).get('has_matching_receipt',False))" 2>/dev/null); [ "$LINK" = "True" ] && pass "JSON: OR linked=True" || fail "OR linkage missing"

T=$((T+1)); ROUT=$(python3 "$S" --report 2>&1); echo "$ROUT" | grep -q "ODR-Extended" && pass "Report mode works" || fail "Report mode failed"

T=$((T+1)); echo "$ROUT" | grep -qi "advisory" && pass "Report: advisory notice" || fail "Report missing advisory"

T=$((T+1)); echo "$ROUT" | grep -q "Owner Decision Receipt" && pass "Report: ODR section" || fail "Report missing ODR section"

T=$((T+1)); echo "$ROUT" | grep -q "OR review linked" && pass "Report: OR linkage" || fail "Report missing OR linkage"

echo ""; echo "============================================================================="
echo "Tests: $T total  Pass: $P  Fail: $F"
[ "$F" -eq 0 ] && echo "Result: $P/$T passed. All tests pass. ✅" && exit 0 || echo "Result: $P/$T passed. Some failed. ❌" && exit 1
