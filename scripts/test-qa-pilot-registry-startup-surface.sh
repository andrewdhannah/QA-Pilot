#!/usr/bin/env bash
set -euo pipefail

# QA Pilot Registry Startup Surface Tests — QA-PILOT-REGISTRY-STARTUP-SURFACE-1
# Tests: registry posture reporting, RSS validation rules, fixture coverage.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SURFACE_SCRIPT="$SCRIPT_DIR/qa_pilot_pipeline_startup_surface.py"
SURFACE_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-epic-regression-startup-surface.py"
OLD_FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-epic-regression-startup-surface"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-registry-startup-surface"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Registry Startup Surface Tests — QA-PILOT-REGISTRY-STARTUP-SURFACE-1"
echo "================================================================================="
echo ""

# ── Test 1: Surface script exists ──
TESTS=$((TESTS + 1))
[ -f "$SURFACE_SCRIPT" ] && pass "Surface script found" || fail "Surface script not found"

# ── Test 2: Report shows Registry Posture section ──
TESTS=$((TESTS + 1))
ROUT=$(python3 "$SURFACE_SCRIPT" report 2>&1) || true
echo "$ROUT" | grep -q "Registry Posture" && pass "Report shows Registry Posture section" || fail "Report missing Registry Posture"

# ── Test 3: Report shows layer count ──
TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "Layer count" && pass "Report shows layer count" || fail "Report missing layer count"

# ── Test 4: Report shows PH-12 status ──
TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "PH-12" && pass "Report shows PH-12 registry status" || fail "Report missing PH-12"

# ── Test 5: Report shows DR-3/DR-4 status ──
TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "DR-3/DR-4" && pass "Report shows DR-3/DR-4 registry status" || fail "Report missing DR-3/DR-4"

# ── Test 6: Report shows PLR status ──
TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "PLR registry" && pass "Report shows PLR registry status" || fail "Report missing PLR"

# ── Test 7: Report shows SR-8 status ──
TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "SR-8" && pass "Report shows SR-8 all-validators status" || fail "Report missing SR-8"

# ── Test 8: Report shows classification ──
TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "Classification" && pass "Report shows classification" || fail "Report missing classification"

# ── Test 9: JSON format includes registry_posture ──
TESTS=$((TESTS + 1))
JSON_OUT=$(python3 "$SURFACE_SCRIPT" report --format json 2>&1) || true
RP_CLASS=$(echo "$JSON_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['pipeline']['registry_posture']['classification'])" 2>/dev/null || echo "fail")
[ "$RP_CLASS" != "fail" ] && pass "JSON report: registry_posture.classification=$RP_CLASS" || fail "JSON report: missing registry_posture"

# ── Test 10: Legacy validators still pass (SS regression) ──
TESTS=$((TESTS + 1))
VOUT=$(python3 "$SURFACE_VALIDATOR" 2>&1) || true
echo "$VOUT" | grep -q "ALL CHECKS PASS" && pass "Legacy startup surface validator ALL CHECKS PASS" || { fail "Legacy validator failed"; echo "       $(echo "$VOUT" | tail -3)"; }

# ── Test 11: Live validate passes (includes RSS rules) ──
TESTS=$((TESTS + 1))
VAL_OUT=$(python3 "$SURFACE_SCRIPT" validate 2>&1) || true
echo "$VAL_OUT" | grep -q "ALL STARTUP SURFACE CHECKS PASS" && pass "Live validate passes (SS + RSS rules)" || { fail "Live validate failed"; echo "       $VAL_OUT"; }

# ── Test 12: Validate shows RSS rules ──
TESTS=$((TESTS + 1))
echo "$VAL_OUT" | grep -q "RSS-" && pass "Validate reports RSS-* rules" || fail "Validate missing RSS rules"

# ── Test 13: Validate valid fixture passes ──
TESTS=$((TESTS + 1))
FIXX_OUT=$(python3 "$SURFACE_SCRIPT" validate --input "$OLD_FIXTURES_DIR/valid-pipeline-report.json" 2>&1) || true
echo "$FIXX_OUT" | grep -q "ALL STARTUP SURFACE CHECKS PASS" && pass "Validate valid fixture passes" || fail "Validate valid fixture failed"

# ── Test 14: Status command shows registry info ──
TESTS=$((TESTS + 1))
SOUT=$(python3 "$SURFACE_SCRIPT" status 2>&1) || true
echo "$SOUT" | grep -q "Registry:" && pass "Status shows Registry info" || fail "Status missing Registry info"

# ── Test 15: Status shows classification ──
TESTS=$((TESTS + 1))
echo "$SOUT" | grep -q "classification" && pass "Status shows classification" || fail "Status missing classification"

# ── Test 16: Valid clean-registry fixture validates ──
TESTS=$((TESTS + 1))
FIXTURE_VALID="$FIXTURES_DIR/valid-clean-registry.json"
[ -f "$FIXTURE_VALID" ] && pass "Clean-registry fixture exists" || fail "Clean-registry fixture missing"

# ── Test 17: Invalid degraded-drift fixture exists ──
TESTS=$((TESTS + 1))
[ -f "$FIXTURES_DIR/invalid-degraded-drift.json" ] && pass "Degraded-drift fixture exists" || fail "Degraded-drift fixture missing"

# ── Test 18: Invalid blocked-authority fixture exists ──
TESTS=$((TESTS + 1))
[ -f "$FIXTURES_DIR/invalid-blocked-authority-claim.json" ] && pass "Blocked-authority fixture exists" || fail "Blocked-authority fixture missing"

# ── Test 19: Report verbose shows packet layers ──
TESTS=$((TESTS + 1))
VROUT=$(python3 "$SURFACE_SCRIPT" report -v 2>&1) || true
echo "$VROUT" | grep -q "Evidence packets\|Test cases" && pass "Verbose report shows packet counts" || fail "Verbose report missing packet counts"

# ── Test 20: All registry posture fields present in JSON ──
TESTS=$((TESTS + 1))
ALL_FIELDS=$(echo "$JSON_OUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
rp = d['pipeline']['registry_posture']
required = ['registry_layer_count', 'latest_registry_layer', 'ph_12_status', 
            'dr_3_4_status', 'plr_status', 'sr_8_status', 'classification']
missing = [f for f in required if f not in rp]
print('all' if not missing else f'missing: {missing}')
" 2>/dev/null)
[ "$ALL_FIELDS" = "all" ] && pass "JSON registry_posture has all required fields" || fail "JSON registry_posture missing: $ALL_FIELDS"

# ── Test 21: Report shows RCR section ──
TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "Registry Change Receipts" && pass "Report shows Registry Change Receipts section" || fail "Report missing RCR section"

# ── Test 22: Report shows RCR receipt count ──
TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "Receipts found" && pass "Report shows RCR receipts count" || fail "Report missing RCR receipt count"

# ── Test 23: Report shows latest RCR impact ──
TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "Latest impact" && pass "Report shows latest RCR impact" || fail "Report missing RCR impact"

# ── Test 24: Validate shows RCS rules ──
TESTS=$((TESTS + 1))
echo "$VAL_OUT" | grep -q "RCS-" && pass "Validate reports RCS-* rules" || fail "Validate missing RCS rules"

# ── Test 25: Status shows RCR info ──
TESTS=$((TESTS + 1))
echo "$SOUT" | grep -q "RCR:" && pass "Status shows RCR info" || fail "Status missing RCR info"

# ── Test 26: Valid RCR-ready fixture exists ──
TESTS=$((TESTS + 1))
[ -f "$FIXTURES_DIR/valid-rcr-ready.json" ] && pass "RCR-ready fixture exists" || fail "RCR-ready fixture missing"

# ── Test 27: Invalid RCR-no-receipts fixture exists ──
TESTS=$((TESTS + 1))
[ -f "$FIXTURES_DIR/invalid-rcr-no-receipts.json" ] && pass "RCR-no-receipts fixture exists" || fail "RCR-no-receipts fixture missing"

# ── Test 28: Invalid RCR-stale fixture exists ──
TESTS=$((TESTS + 1))
[ -f "$FIXTURES_DIR/invalid-rcr-stale.json" ] && pass "RCR-stale fixture exists" || fail "RCR-stale fixture missing"

# ── Test 29: Report shows Closeout Gate section ──
TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "Closeout Gate" && pass "Report shows Closeout Gate section" || fail "Report missing Closeout Gate"

# ── Test 30: Report shows coverage gap ──
TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "Coverage gap" && pass "Report shows coverage gap" || fail "Report missing coverage gap"

# ── Test 31: Report shows RCG status ──
TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "RCG status" && pass "Report shows RCG status" || fail "Report missing RCG status"

# ── Test 32: Report shows RCG classification ──
TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "RCG classification" && pass "Report shows RCG classification" || fail "Report missing RCG classification"

# ── Test 33: Validate shows RCGS rules ──
TESTS=$((TESTS + 1))
echo "$VAL_OUT" | grep -q "RCGS-" && pass "Validate reports RCGS-* rules" || fail "Validate missing RCGS rules"

# ── Test 34: Status shows RCG info ──
TESTS=$((TESTS + 1))
echo "$SOUT" | grep -q "RCG:" && pass "Status shows RCG info" || fail "Status missing RCG info"

# ── Test 35: Valid RCG-ready fixture exists ──
TESTS=$((TESTS + 1))
[ -f "$FIXTURES_DIR/valid-rcg-ready.json" ] && pass "RCG-ready fixture exists" || fail "RCG-ready fixture missing"

# ── Test 36: Invalid RCG-blocked fixture exists ──
TESTS=$((TESTS + 1))
[ -f "$FIXTURES_DIR/invalid-rcg-blocked.json" ] && pass "RCG-blocked fixture exists" || fail "RCG-blocked fixture missing"

# ── Test 37: Invalid RCG-unknown-authority fixture exists ──
TESTS=$((TESTS + 1))
[ -f "$FIXTURES_DIR/invalid-rcg-unknown-authority.json" ] && pass "RCG-unknown-authority fixture exists" || fail "RCG-unknown-authority fixture missing"

# ── Test 38: Report shows Snapshot Update Gate section ──
TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "Snapshot Update Gate" && pass "Report shows Snapshot Update Gate section" || fail "Report missing SUG section"

# ── Test 39: Report shows active snapshot ID ──
TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "Active snapshot" && pass "Report shows active snapshot ID" || fail "Report missing active snapshot"

# ── Test 40: Report shows snapshot state current/stale ──
TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "Snapshot state" && pass "Report shows snapshot state" || fail "Report missing snapshot state"

# ── Test 41: Report shows update pending ──
TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "Update pending" && pass "Report shows update pending" || fail "Report missing update pending"

# ── Test 42: Report shows SUG status ──
TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "SUG status" && pass "Report shows SUG status" || fail "Report missing SUG status"

# ── Test 43: Report shows SUG classification ──
TESTS=$((TESTS + 1))
echo "$ROUT" | grep -q "SUG classification" && pass "Report shows SUG classification" || fail "Report missing SUG classification"

# ── Test 44: Validate shows SUGS rules ──
TESTS=$((TESTS + 1))
echo "$VAL_OUT" | grep -q "SUGS-" && pass "Validate reports SUGS-* rules" || fail "Validate missing SUGS rules"

# ── Test 45: Status shows SUG info ──
TESTS=$((TESTS + 1))
echo "$SOUT" | grep -q "SUG:" && pass "Status shows SUG info" || fail "Status missing SUG info"

# ── Test 46: SUG-ready fixture exists ──
TESTS=$((TESTS + 1))
[ -f "$FIXTURES_DIR/valid-sug-ready.json" ] && pass "SUG-ready fixture exists" || fail "SUG-ready fixture missing"

# ── Test 47: SUG-stale fixture exists ──
TESTS=$((TESTS + 1))
[ -f "$FIXTURES_DIR/invalid-sug-stale-snapshot.json" ] && pass "SUG-stale fixture exists" || fail "SUG-stale fixture missing"

# ── Test 48: SUG-blocked fixture exists ──
TESTS=$((TESTS + 1))
[ -f "$FIXTURES_DIR/invalid-sug-blocked.json" ] && pass "SUG-blocked fixture exists" || fail "SUG-blocked fixture missing"

echo ""
echo "================================================================================="
echo "Tests: $TESTS total  Pass: $PASS  Fail: $FAIL"
[ "$FAIL" -eq 0 ] && echo "Result: $PASS/$TESTS passed. All tests pass. ✅" && exit 0 \
  || echo "Result: $PASS/$TESTS passed. Some failed. ❌" && exit 1
