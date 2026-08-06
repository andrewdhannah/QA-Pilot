#!/usr/bin/env bash
# ── Learning Object v1 Contract Test Runner ──────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-learning-object.py"
FIXTURES_DIR="$REPO_ROOT/docs/examples/learning-object-v1"
SCHEMA_FILE="$REPO_ROOT/docs/schemas/learning-object-v1.schema.json"

PASS=0; FAIL=0; TESTS=0
pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "Learning Object v1 Contract — Test Runner"
echo "============================================="
echo ""

# Test 1: Validator exists
TESTS=$((TESTS + 1))
[[ -f "$VALIDATOR" ]] && pass "Validator exists" || fail "Validator not found"

# Test 2: --list-rules works
TESTS=$((TESTS + 1))
RULE_COUNT=$(python3 "$VALIDATOR" --list-rules 2>/dev/null | grep -c "LO-" || true)
[[ "$RULE_COUNT" -ge 10 ]] && pass "Validator lists $RULE_COUNT rules (LO-1 through LO-15)" || fail "Validator shows <10 rules"

# Test 3: Valid fixtures all pass
TESTS=$((TESTS + 1))
python3 "$VALIDATOR" --all >/dev/null 2>&1 && pass "All valid fixtures pass" || fail "Some valid fixtures failed"

# Test 4: Invalid fixtures correctly rejected
TESTS=$((TESTS + 1))
INI_COUNT=$(ls "$FIXTURES_DIR"/invalid-*.json 2>/dev/null | wc -l || echo "0")
if [[ "$INI_COUNT" -gt 0 ]]; then
    VALIDATOR_OUT=$(python3 "$VALIDATOR" --all --include-invalid 2>&1 || true)
    REJ_COUNT=$(echo "$VALIDATOR_OUT" | grep -c "correctly rejected" || true)
    [[ "$REJ_COUNT" -ge 1 ]] && pass "Validator correctly rejects invalid fixtures ($REJ_COUNT rejected)" || fail "Validator did not reject invalid fixtures"
else
    pass "No invalid fixtures (skipping)"
fi

# Test 5: Schema file exists and is valid JSON
TESTS=$((TESTS + 1))
if [[ -f "$SCHEMA_FILE" ]]; then
    python3 -c "import json; json.load(open('$SCHEMA_FILE'))" 2>/dev/null && pass "Schema is valid JSON" || fail "Schema is invalid JSON"
else
    fail "Schema not found"
fi

# Test 6: Schema has required fields
TESTS=$((TESTS + 1))
python3 -c "
import json
s = json.load(open('$SCHEMA_FILE'))
required = s.get('required', [])
expected = ['schema', 'id', 'source', 'learning', 'assessment', 'certification']
missing = [r for r in expected if r not in required]
if missing:
    print(f'schema missing required fields: {missing}')
    exit(1)
print('Schema has all required field declarations')
" 2>/dev/null && pass "Schema declares all required fields" || fail "Schema missing required field declarations"

# Test 7: Fixture count check
TESTS=$((TESTS + 1))
VALID_COUNT=$(ls "$FIXTURES_DIR"/valid-*.json 2>/dev/null | wc -l || echo "0")
INI_COUNT=$(ls "$FIXTURES_DIR"/invalid-*.json 2>/dev/null | wc -l || echo "0")
TOTAL_FIX=$((VALID_COUNT + INI_COUNT))
[[ "$TOTAL_FIX" -ge 4 ]] && pass "Fixtures: $VALID_COUNT valid + $INI_COUNT invalid = $TOTAL_FIX total" || fail "Fewer than 4 fixtures"

# Test 8: No valid fixture contains inline evidence
TESTS=$((TESTS + 1))
INLINE_FOUND=0
for f in "$FIXTURES_DIR"/valid-*.json; do
    [[ -f "$f" ]] || continue
    HAS_FINDINGS=$(python3 -c "import json; d=json.load(open('$f')); print('findings' in d)" 2>/dev/null || echo "False")
    HAS_EVIDENCE=$(python3 -c "import json; d=json.load(open('$f')); print('evidence' in d)" 2>/dev/null || echo "False")
    [[ "$HAS_FINDINGS" == "True" ]] && INLINE_FOUND=$((INLINE_FOUND + 1))
    [[ "$HAS_EVIDENCE" == "True" ]] && INLINE_FOUND=$((INLINE_FOUND + 1))
done
[[ "$INLINE_FOUND" -eq 0 ]] && pass "No valid fixture contains inline evidence fields" || fail "Found $INLINE_FOUND valid fixtures with inline evidence"

# Test 9: No valid fixture cert criteria contains forbidden keywords
TESTS=$((TESTS + 1))
FORBIDDEN_FOUND=0
for f in "$FIXTURES_DIR"/valid-*.json; do
    [[ -f "$f" ]] || continue
    HAS_SEAL=$(python3 -c "import json; d=json.load(open('$f')); cert=d.get('certification',{}); print(any('seal' in c.get('description','').lower() for c in cert.get('criteria',[])))" 2>/dev/null || echo "False")
    HAS_APPROVE=$(python3 -c "import json; d=json.load(open('$f')); cert=d.get('certification',{}); print(any('approve' in c.get('description','').lower() for c in cert.get('criteria',[])))" 2>/dev/null || echo "False")
    [[ "$HAS_SEAL" == "True" ]] && FORBIDDEN_FOUND=$((FORBIDDEN_FOUND + 1))
    [[ "$HAS_APPROVE" == "True" ]] && FORBIDDEN_FOUND=$((FORBIDDEN_FOUND + 1))
done
[[ "$FORBIDDEN_FOUND" -eq 0 ]] && pass "No valid fixture cert criteria contains forbidden keywords" || fail "Found $FORBIDDEN_FOUND valid fixtures with forbidden keywords"

# Test 10: Every valid fixture has advisory_only and no_seal_authority
TESTS=$((TESTS + 1))
ALL_INVARIANTS=true
for f in "$FIXTURES_DIR"/valid-*.json; do
    [[ -f "$f" ]] || continue
    python3 -c "
import json
d = json.load(open('$f'))
assert d.get('advisory_only') == True, 'advisory_only not True'
assert d.get('no_seal_authority') == True, 'no_seal_authority not True'
" 2>/dev/null || { ALL_INVARIANTS=false; break; }
done
[[ "$ALL_INVARIANTS" == true ]] && pass "All valid fixtures have advisory_only=True and no_seal_authority=True" || fail "Some valid fixtures missing authority invariants"

# Summary
echo ""
echo "=============================="
echo "Tests: $TESTS total | Pass: $PASS | Fail: $FAIL"
echo "=============================="
if [[ "$FAIL" -eq 0 ]]; then
    echo "Result: $PASS/$TESTS passed. All tests pass. ✅"
    exit 0
else
    echo "Result: $PASS/$TESTS passed. $FAIL failures. ❌"
    exit 1
fi
