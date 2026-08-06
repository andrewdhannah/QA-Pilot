#!/usr/bin/env bash
# QA Pilot Librarian Knowledge Adapter Test Runner
# QA-PILOT-LIBRARIAN-KNOWLEDGE-ADAPTER-1

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-knowledge-adapter.py"
ADAPTER="$SCRIPT_DIR/qa_pilot_knowledge_adapter.py"
FIXTURES_DIR="$PROJECT_DIR/docs/examples/qa-pilot-knowledge-adapter"
SCHEMA="$PROJECT_DIR/docs/schemas/qa-pilot-knowledge-adapter.schema.json"
GOV_DOC="$PROJECT_DIR/docs/governance/QA-PILOT-LIBRARIAN-KNOWLEDGE-ADAPTER.md"

pass_count=0; fail_count=0
pass() { pass_count=$((pass_count + 1)); echo "  ✅ $1"; }
fail() { fail_count=$((fail_count + 1)); echo "  ❌ $1: $2"; }

echo "================================================================"
echo "  QA Pilot Librarian Knowledge Adapter — Test Runner"
echo "  QA-PILOT-LIBRARIAN-KNOWLEDGE-ADAPTER-1"
echo "================================================================"

# T1: Validator script exists
[ -f "$VALIDATOR" ] && pass "T1: Validator script found" || fail "T1" "Not found"

# T2: Adapter script exists
[ -f "$ADAPTER" ] && pass "T2: Adapter CLI script found" || fail "T2" "Not found"

# T3: Schema is valid JSON
python3 -c "import json; json.load(open('$SCHEMA'))" 2>/dev/null \
  && pass "T3: Schema is valid JSON" \
  || fail "T3" "Schema parse error"

# T4: Governance doc exists
[ -f "$GOV_DOC" ] && pass "T4: Governance doc exists" || fail "T4" "Not found"

# T5: Fixture directory has files
fixture_count=$(ls "$FIXTURES_DIR"/*.json 2>/dev/null | wc -l)
[ "$fixture_count" -ge 6 ] && pass "T5: Fixture directory has $fixture_count files" \
  || fail "T5" "Expected >=6 fixtures, found $fixture_count"

# T6: Valid fixtures pass validator
set +e
valid_out=$(python3 "$VALIDATOR" 2>&1)
valid_rc=$?
set -e
if [ "$valid_rc" -eq 0 ]; then
  pass "T6: Valid fixtures all pass validator"
else
  fail "T6" "Validator failed on valid fixtures"
  echo "$valid_out" | tail -5
fi

# T7: Invalid fixtures rejected
set +e
invalid_out=$(python3 "$VALIDATOR" --include-invalid 2>&1)
invalid_rc=$?
set -e
# Should pass overall (valid pass + invalid reject)
[ "$invalid_rc" -eq 0 ] && pass "T7: Invalid fixtures correctly rejected" \
  || fail "T7" "Validator issues with invalid fixtures"

# T8: Adapter --help works
set +e
help_out=$(python3 "$ADAPTER" --help 2>&1)
help_rc=$?
set -e
[ "$help_rc" -eq 0 ] && pass "T8: Adapter --help works" || fail "T8" "Exit code $help_rc"

# T9: Adapter scan produces valid JSON
set +e
scan_out=$(python3 "$ADAPTER" scan 2>&1)
scan_rc=$?
set -e
if [ "$scan_rc" -eq 0 ]; then
  echo "$scan_out" | python3 -c "import json,sys; json.load(sys.stdin)" 2>/dev/null \
    && pass "T9: Adapter scan produces valid JSON" \
    || fail "T9" "Invalid JSON"
else
  fail "T9" "Scan failed with exit code $scan_rc"
fi

# T10: Adapter status shows advisory-only
set +e
status_out=$(python3 "$ADAPTER" status 2>&1)
status_rc=$?
set -e
if [ "$status_rc" -eq 0 ]; then
  echo "$status_out" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['result']['authority']=='advisory-only'" 2>/dev/null \
    && pass "T10: Status reports advisory-only authority" \
    || fail "T10" "Authority not advisory-only"
else
  fail "T10" "Status failed"
fi

# T11: Adapter reference existing file
set +e
ref_out=$(python3 "$ADAPTER" reference "docs/governance/AGENT-HANDOFF-AND-PROVENANCE-PROTOCOL.md" 2>&1)
ref_rc=$?
set -e
if [ "$ref_rc" -eq 0 ]; then
  accessible=$(echo "$ref_out" | python3 -c "import json,sys; print(json.load(sys.stdin)['result']['accessible_count'])" 2>/dev/null || echo "0")
  [ "$accessible" -gt 0 ] && pass "T11: Reference existing file (accessible=$accessible)" \
    || fail "T11" "File not accessible"
else
  fail "T11" "Reference failed"
fi

# T12: Adapter reference non-existing file
set +e
ref_missing=$(python3 "$ADAPTER" reference "nonexistent/path.md" 2>&1)
ref_missing_rc=$?
set -e
if [ "$ref_missing_rc" -eq 0 ]; then
  accessible=$(echo "$ref_missing" | python3 -c "import json,sys; print(json.load(sys.stdin)['result']['accessible_count'])" 2>/dev/null || echo "0")
  [ "$accessible" -eq 0 ] && pass "T12: Reference missing file returns accessible=false" \
    || fail "T12" "Missing file shows as accessible"
else
  fail "T12" "Reference failed for missing file"
fi

# T13: Adapter provenance creates record
set +e
prov_out=$(python3 "$ADAPTER" provenance "docs/governance/AGENT-HANDOFF-AND-PROVENANCE-PROTOCOL.md" 2>&1)
prov_rc=$?
set -e
if [ "$prov_rc" -eq 0 ]; then
  echo "$prov_out" | python3 -c "import json,sys; d=json.load(sys.stdin); p=d['result']['provenance']; assert p['advisory']==True; assert p['no_authority_promotion']==True; assert len(p['sources'])>0" 2>/dev/null \
    && pass "T13: Provenance record created with advisory=true" \
    || fail "T13" "Provenance record validation failed"
else
  fail "T13" "Provenance failed"
fi

# T14: Adapter verify existing file
set +e
ver_out=$(python3 "$ADAPTER" verify "docs/governance/AGENT-HANDOFF-AND-PROVENANCE-PROTOCOL.md" 2>&1)
ver_rc=$?
set -e
[ "$ver_rc" -eq 0 ] && pass "T14: Verify existing file passes" \
  || fail "T14" "Verify failed for existing file"

# T15: All --list-rules prints expected count
set +e
rules_out=$(python3 "$VALIDATOR" --list-rules 2>&1)
rules_count=$(echo "$rules_out" | grep -c "^  KA-" || true)
set -e
[ "$rules_count" -eq 14 ] && pass "T15: Validator has $rules_count rules (KA-1 to KA-14)" \
  || fail "T15" "Expected 14 rules, found $rules_count"

# T16: Adapter query with pattern filter
set +e
query_out=$(python3 "$ADAPTER" query governance 2>&1)
query_rc=$?
set -e
if [ "$query_rc" -eq 0 ]; then
  matches=$(echo "$query_out" | python3 -c "import json,sys; print(json.load(sys.stdin)['result']['total_matches'])" 2>/dev/null || echo "0")
  pass "T16: Query 'governance' found $matches matches"
else
  fail "T16" "Query failed"
fi

# T17: Prohibited-zone: no knowledge adapter files in Librarian
librarian_leak=$(find "$PROJECT_DIR/../librarian" -name "*knowledge*adapter*" 2>/dev/null | wc -l)
[ "$librarian_leak" -eq 0 ] && pass "T17: No knowledge adapter files leaked into Librarian" \
  || fail "T17" "Found $librarian_leak files in Librarian"

# Summary
echo ""
echo "================================================================"
echo "Tests: $((pass_count + fail_count)) total"
echo "Pass:  $pass_count"
echo "Fail:  $fail_count"
echo "================================================================"
if [ "$fail_count" -eq 0 ]; then
  echo "Result: $pass_count/$((pass_count + fail_count)) passed. All tests pass. ✅"
else
  echo "Result: $pass_count/$((pass_count + fail_count)) passed. Some tests failed. ❌"
fi
exit $fail_count
