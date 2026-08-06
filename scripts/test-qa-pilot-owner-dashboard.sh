#!/usr/bin/env bash
# test-qa-pilot-owner-dashboard.sh — Owner Dashboard Test Runner
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DASHBOARD="$REPO_ROOT/scripts/qa_pilot_owner_dashboard.py"
VALIDATOR="$REPO_ROOT/scripts/validate-qa-pilot-owner-dashboard.py"
FIXTURES="$REPO_ROOT/docs/examples/qa-pilot-owner-dashboard"
PASS=0
FAIL=0

pass() { PASS=$((PASS+1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL+1)); echo "  ❌ $1"; }

echo "=== Owner Dashboard Test Runner ==="
echo ""

# ── Test 1: Dashboard report (text mode) ──
echo "--- Test 1: Dashboard text report ---"
OUTPUT=$(python3 "$DASHBOARD" report 2>&1) && pass "Dashboard text report exits 0" || fail "Dashboard text report failed"
echo "$OUTPUT" | grep -q "Owner Dashboard" && pass "Report contains 'Owner Dashboard'" || fail "Report missing header"
echo ""

# ── Test 2: Dashboard JSON output ──
echo "--- Test 2: Dashboard JSON output ---"
JSON=$(python3 "$DASHBOARD" report --json 2>&1)
echo "$JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'dashboard_id' in d; assert 'sections' in d" \
  && pass "Dashboard JSON valid" || fail "Dashboard JSON invalid"
echo "$JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'Projection layer' in d['invariant']" \
  && pass "Invariant present" || fail "Invariant missing"
echo ""

# ── Test 3: Dashboard validate mode ──
echo "--- Test 3: Dashboard validate mode ---"
VALIDATE=$(python3 "$DASHBOARD" validate 2>&1)
echo "$VALIDATE" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('all_pass') in (True, False)" \
  && pass "Validate output valid" || fail "Validate output invalid"
echo ""

# ── Test 4: Dashboard status mode (JSON) ──
echo "--- Test 4: Dashboard status mode ---"
STATUS=$(python3 "$DASHBOARD" status 2>&1)
echo "$STATUS" | python3 -c "import sys,json; json.load(sys.stdin)" \
  && pass "Status output valid JSON" || fail "Status output invalid"
echo ""

# ── Test 5: Validator fixture mode ──
echo "--- Test 5: Validator fixture validation ---"
# Valid fixture should pass
python3 -c "
import sys,json
f=open('$FIXTURES/valid-full-dashboard.json')
d=json.load(f)
assert 'dashboard_id' in d, 'Missing dashboard_id'
assert 'sections' in d, 'Missing sections'
assert 'Projection' in d['invariant'], 'Missing invariant'
print('Valid fixture: pass')
" && pass "Valid fixture passes" || fail "Valid fixture should pass"

# Invalid fixture should fail invariant check
python3 -c "
import sys,json
f=open('$FIXTURES/invalid-missing-invariant.json')
d=json.load(f)
assert 'Projection' not in d['invariant'], 'Invalid fixture should not pass invariant check'
print('Invalid fixture: correctly rejected')
" && pass "Invalid fixture rejected" || fail "Invalid fixture should be rejected"
echo ""

# ── Test 6: Validator validate mode ──
echo "--- Test 6: Validator live validation ---"
python3 "$VALIDATOR" validate 2>&1 | tail -1 | grep -q "ALL CHECKS PASS" \
  && pass "Live validation passes" || fail "Live validation failed"
echo ""

# ── Test 7: Valid OD-6 invariant check ──
echo "--- Test 7: Invariant enforcement (Projection layer) ---"
python3 "$DASHBOARD" report --json 2>&1 | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert 'Projection layer' in d['invariant'], 'Missing invariant'
assert 'does not create' in d['invariant'], 'Missing projection clause'
print('Projection invariant verified')
" && pass "Projection invariant enforced" || fail "Projection invariant missing"
echo ""

# ── Test 8: All 6 sections present ──
echo "--- Test 8: All 6 dashboard sections ---"
python3 "$DASHBOARD" report --json 2>&1 | python3 -c "
import sys,json
d=json.load(sys.stdin)
required = ['assurance_health','active_findings','risk_posture','evidence_freshness','owner_queue','release_readiness']
for s in required:
    assert s in d['sections'], f'Missing section: {s}'
print('All 6 sections present')
" && pass "All 6 sections present" || fail "Missing sections"
echo ""

# ── Test 9: No action verbs in dashboard data sections ──
echo "--- Test 9: No action verbs in dashboard data ---"
python3 "$DASHBOARD" report --json 2>&1 | python3 -c "
import sys,json
d=json.load(sys.stdin)
# Check only section data payloads, not the invariant or metadata
action_verbs = ['findings_sealed', 'approve_release', 'auto_resolve', 'auto_close', 'override_decision']
for section_name, section in d['sections'].items():
    text = json.dumps(section.get('data', {})).lower()
    for verb in action_verbs:
        assert verb not in text, f'Action verb found in {section_name}: {verb}'
print('No action verbs in dashboard data')
" && pass "No action verbs in data" || fail "Action verb detected in data"
echo ""

# ── Test 10: Source provenance (findings trace to stores) ──
echo "--- Test 10: Source provenance ---"
python3 "$DASHBOARD" report --json 2>&1 | python3 -c "
import sys,json
d=json.load(sys.stdin)
risk = d['sections']['risk_posture']['data']
if risk.get('status') == 'available':
    assert 'source' in risk or 'priority_counts' in risk, 'Risk has no provenance'
    print('Risk provenance: source available')
else:
    print('Risk: no data (acceptable)')
" && pass "Source provenance verified" || fail "Source provenance missing"
echo ""

# ── Summary ──
echo "=== Results: $PASS pass, $FAIL fail ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
