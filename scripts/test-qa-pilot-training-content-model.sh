#!/usr/bin/env bash
# QA Pilot Training Content Model Test Runner
# QA-PILOT-TRAINING-CONTENT-MODEL-1

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-training-content-model.py"
FIXTURES_DIR="$PROJECT_DIR/docs/examples/qa-pilot-training-content-model"
SCHEMA="$PROJECT_DIR/docs/schemas/qa-pilot-training-content-model.schema.json"
GOV_DOC="$PROJECT_DIR/docs/governance/QA-PILOT-TRAINING-CONTENT-MODEL.md"

pass_count=0; fail_count=0
pass() { pass_count=$((pass_count + 1)); echo "  ✅ $1"; }
fail() { fail_count=$((fail_count + 1)); echo "  ❌ $1: $2"; }

echo "================================================================"
echo "  QA Pilot Training Content Model — Test Runner"
echo "  QA-PILOT-TRAINING-CONTENT-MODEL-1"
echo "================================================================"

# T1: Validator exists
[ -f "$VALIDATOR" ] && pass "T1: Validator script found" || fail "T1" "Not found"

# T2: Schema valid JSON
python3 -c "import json; json.load(open('$SCHEMA'))" && pass "T2: Schema is valid JSON" || fail "T2" "Parse error"

# T3: Governance doc exists
[ -f "$GOV_DOC" ] && pass "T3: Governance doc exists" || fail "T3" "Not found"

# T4: 7 valid fixtures exist
valid_count=$(ls "$FIXTURES_DIR"/valid-*.json 2>/dev/null | wc -l)
[ "$valid_count" -eq 7 ] && pass "T4: 7 valid fixtures found" || fail "T4" "Found $valid_count, expected 7"

# T5: 3 invalid fixtures exist
invalid_count=$(ls "$FIXTURES_DIR"/invalid-*.json 2>/dev/null | wc -l)
[ "$invalid_count" -ge 3 ] && pass "T5: $invalid_count invalid fixtures found" || fail "T5" "Expected >=3, found $invalid_count"

# T6: All valid fixtures pass
set +e
valid_out=$(python3 "$VALIDATOR" 2>&1)
valid_rc=$?
set -e
if [ "$valid_rc" -eq 0 ]; then
  pass "T6: All valid fixtures pass"
else
  fail "T6" "Validator failed on valid fixtures"
  echo "$valid_out" | tail -10
fi

# T7: Invalid fixtures rejected
set +e
invalid_out=$(python3 "$VALIDATOR" --include-invalid 2>&1)
invalid_rc=$?
set -e
[ "$invalid_rc" -eq 0 ] && pass "T7: Invalid fixtures correctly rejected" || fail "T7" "Issues with invalid fixtures"

# T8: List rules shows 14
set +e
rules_count=$(python3 "$VALIDATOR" --list-rules 2>&1 | grep -c "^  CM-" || true)
set -e
[ "$rules_count" -eq 14 ] && pass "T8: 14 rules (CM-1 to CM-14)" || fail "T8" "Expected 14, found $rules_count"

# T9: Each artifact type present in valid fixtures
for type in onboarding_guide operator_guide developer_guide troubleshooting_guide architecture_explanation workflow_tutorial validation_exercise; do
  short=$(echo "$type" | sed 's/_/-/g')
  if [ -f "$FIXTURES_DIR/valid-$short.json" ]; then
    pass "T9: Fixture for $type exists"
  else
    fail "T9" "Missing fixture: valid-$short.json"
  fi
done

# T10: No content model files in Librarian
leak=$(find "$PROJECT_DIR/../librarian" -name "*content-model*" 2>/dev/null | wc -l)
[ "$leak" -eq 0 ] && pass "T10: No content model files leaked into Librarian" || fail "T10" "Found $leak files"

# T11: Schema valid jsonschema
python3 -c "
import json
schema = json.load(open('$SCHEMA'))
# Verify it has the required artifact_type enum
types = schema['properties']['artifact_type']['enum']
assert len(types) == 7, f'Expected 7 types, got {len(types)}'
assert 'onboarding_guide' in types
assert 'validation_exercise' in types
" && pass "T11: Schema has 7 artifact types" || fail "T11" "Schema type count wrong"

echo ""
echo "================================================================"
echo "Tests: $((pass_count + fail_count)) total"
echo "Pass:  $pass_count"
echo "Fail:  $fail_count"
echo "================================================================"
[ "$fail_count" -eq 0 ] && echo "Result: All tests pass. ✅" || echo "Result: Some tests failed. ❌"
exit $fail_count
