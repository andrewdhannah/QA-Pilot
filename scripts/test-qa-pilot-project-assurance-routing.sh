#!/usr/bin/env bash
# test-qa-pilot-project-assurance-routing.sh — Multi-Project Routing Test Runner
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ROUTING="$REPO_ROOT/scripts/qa_pilot_project_assurance_routing.py"
DASHBOARD="$REPO_ROOT/scripts/qa_pilot_owner_dashboard.py"
VALIDATOR="$REPO_ROOT/scripts/validate-qa-pilot-project-assurance-routing.py"
PASS=0
FAIL=0

pass() { PASS=$((PASS+1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL+1)); echo "  ❌ $1"; }

echo "=== Multi-Project Assurance Routing Test Runner ==="
echo ""

# ── Test 1: Routing report (text mode, single project) ──
echo "--- Test 1: Routing text report ---"
OUTPUT=$(python3 "$ROUTING" report 2>&1) && pass "Routing text report exits 0" || fail "Routing text report failed"
echo "$OUTPUT" | grep -q "Multi-Project Assurance Routing" && pass "Report contains header" || fail "Report missing header"
echo ""

# ── Test 2: Routing JSON output ──
echo "--- Test 2: Routing JSON output ---"
JSON=$(python3 "$ROUTING" report --json 2>&1)
echo "$JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'routing_id' in d; assert 'projects' in d; assert 'cross_project' in d" \
  && pass "Routing JSON valid" || fail "Routing JSON invalid"
echo ""

# ── Test 3: Project identity preserved in JSON ──
echo "--- Test 3: Project identity ---"
echo "$JSON" | python3 -c "
import sys,json; d=json.load(sys.stdin)
projects = d.get('projects', {})
assert len(projects) > 0, 'No projects found'
for pid in projects:
    assert isinstance(pid, str) and len(pid) > 0, f'Invalid project ID: {pid}'
print(f'Projects: {list(projects.keys())}')
" && pass "Project identity preserved" || fail "Project identity missing"
echo ""

# ── Test 4: Routing validate mode ──
echo "--- Test 4: Routing validate mode ---"
python3 "$ROUTING" validate 2>&1 | python3 -c "
import sys,json; d=json.load(sys.stdin)
assert 'checks' in d, 'Missing checks'
print(f'All pass: {d.get(\"all_pass\", False)}')
" && pass "Routing validate works" || fail "Routing validate failed"
echo ""

# ── Test 5: Validator PAR-1 through PAR-10 ──
echo "--- Test 5: PAR validator ---"
python3 "$VALIDATOR" validate 2>&1 | tail -1 | grep -q "ALL CHECKS PASS" \
  && pass "PAR-1 through PAR-10 all pass" || fail "Some PAR checks failed"
echo ""

# ── Test 6: Multi-project dashboard with --multi-project ──
echo "--- Test 6: Multi-project dashboard ---"
MP=$(python3 "$DASHBOARD" report --json --multi-project "$REPO_ROOT" 2>&1)
echo "$MP" | python3 -c "
import sys,json; d=json.load(sys.stdin)
assert 'multi_project' in d, 'Missing multi_project section'
assert 'cross_project' in d['multi_project'], 'Missing cross_project summary'
assert len(d['multi_project'].get('projects', {})) > 0, 'No projects in routing'
print('Multi-project dashboard: OK')
" && pass "Multi-project dashboard works" || fail "Multi-project dashboard failed"
echo ""

# ── Test 7: Invariant enforcement ──
echo "--- Test 7: Invariant ---"
echo "$JSON" | python3 -c "
import sys,json; d=json.load(sys.stdin)
assert 'Multiple projects' in d['invariant'], 'Missing invariant'
assert 'separate sources of truth' in d['invariant'], 'Missing separation clause'
print('Invariant preserved')
" && pass "Routing invariant enforced" || fail "Invariant violation"
echo ""

# ── Test 8: PAR-10 existing behavior unchanged ──
echo "--- Test 8: Single-project dashboard unchanged ---"
python3 "$DASHBOARD" report --json 2>&1 | python3 -c "
import sys,json; d=json.load(sys.stdin)
assert 'multi_project' not in d, 'Multi-project should not appear without --multi-project'
assert 'dashboard_id' in d, 'Dashboard should still work'
print('Single-project dashboard: OK')
" && pass "Existing dashboard unchanged" || fail "Existing dashboard broken"
echo ""

# ── Test 9: Validator fixture mode ──
echo "--- Test 9: Validator fixtures ---"
python3 "$VALIDATOR" fixture 2>&1 | tail -1 | grep -q "ALL FIXTURES VALID" \
  && pass "Fixture validation passes" || fail "Fixture validation failed"
echo ""

# ── Test 10: Cross-project comparison data ──
echo "--- Test 10: Cross-project comparison ---"
echo "$JSON" | python3 -c "
import sys,json; d=json.load(sys.stdin)
cp = d.get('cross_project', {})
assert 'total_projects' in cp, 'Missing total_projects'
assert 'total_findings' in cp, 'Missing total_findings'
assert 'total_risk_items' in cp, 'Missing total_risk_items'
print(f'Cross-project data: {cp[\"total_projects\"]} projects')
" && pass "Cross-project comparison data present" || fail "Cross-project data missing"
echo ""

# ── Summary ──
echo "=== Results: $PASS pass, $FAIL fail ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
