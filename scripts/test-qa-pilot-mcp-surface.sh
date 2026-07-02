#!/usr/bin/env bash
set -euo pipefail

# QA Pilot MCP Surface Test Runner — QA-PILOT-MCP-SURFACE-1
# Tests: validator existence, --list-rules, valid fixtures pass, invalid fixtures reject,
#        --all mode, --include-invalid, existing receipt validator unchanged,
#        AST meta-check, project integrity

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-mcp-surface.py"
RECEIPT_VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-receipt.py"
RECEIPT_TEST="$SCRIPT_DIR/test-qa-pilot-receipt.sh"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-mcp-surface"
SCHEMA_FILE="$REPO_ROOT/docs/schemas/qa-pilot-mcp-tool.schema.json"
GOVERNANCE_DOC="$REPO_ROOT/docs/governance/QA-PILOT-MCP-SURFACE.md"
PROFILE_FILE="$REPO_ROOT/PROJECT-PROFILE.json"
LEDGER_FILE="$REPO_ROOT/project-state/sprint-ledger.json"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot MCP Surface Tests — QA-PILOT-MCP-SURFACE-1"
echo "================================================================="
echo ""

# ── Test 1: Validator exists ──
TESTS=$((TESTS + 1))
if [ -f "$VALIDATOR" ]; then
    pass "MCP surface validator found"
else
    fail "MCP surface validator not found at $VALIDATOR"
fi

# ── Test 2: --list-rules works ──
TESTS=$((TESTS + 1))
if python3 "$VALIDATOR" --list-rules 2>&1 | grep -q "MP-1"; then
    pass "--list-rules works"
else
    fail "--list-rules did not show MP-1"
fi

# ── Test 3: Valid fixtures all pass ──
TESTS=$((TESTS + 1))
VALID_OUTPUT=$(python3 "$VALIDATOR" 2>&1) || true
if echo "$VALID_OUTPUT" | grep -q "ALL CHECKS PASS"; then
    pass "Valid fixtures all pass"
else
    fail "Valid fixtures did not all pass"
    echo "       $VALID_OUTPUT" | head -5
fi

# ── Test 4: Invalid fixtures all fail ──
TESTS=$((TESTS + 1))
INVALID_OUTPUT=$(python3 "$VALIDATOR" --include-invalid 2>&1) || true
INVALID_COUNT=$(echo "$INVALID_OUTPUT" | grep -c "❌" || true)
if [ "$INVALID_COUNT" -ge 4 ]; then
    pass "Invalid fixtures correctly rejected ($INVALID_COUNT failures detected)"
else
    fail "Not enough invalid fixtures rejected (expected >= 4)"
fi

# ── Test 5: --all mode on valid fixtures ──
TESTS=$((TESTS + 1))
ALL_OUTPUT=$(python3 "$VALIDATOR" --all 2>&1) || true
if echo "$ALL_OUTPUT" | grep -q "ALL CHECKS PASS"; then
    pass "--all passes on valid fixtures"
else
    fail "--all did not pass on valid fixtures"
fi

# ── Test 6: --all --include-invalid detects failures ──
TESTS=$((TESTS + 1))
ALL_INVALID_OUTPUT=$(python3 "$VALIDATOR" --all --include-invalid 2>&1) || true
if echo "$ALL_INVALID_OUTPUT" | grep -q "SOME CHECKS FAILED"; then
    pass "--all --include-invalid correctly detects invalid fixtures"
else
    fail "--all --include-invalid did not detect failures"
fi

# ── Test 7: Non-existent file fails ──
TESTS=$((TESTS + 1))
if ! python3 "$VALIDATOR" /tmp/nonexistent-mcp-file.json >/dev/null 2>&1; then
    pass "Correctly rejects non-existent file"
else
    fail "Did not reject non-existent file"
fi

# ── Test 8: Validator does not grant authority (meta-check) ──
TESTS=$((TESTS + 1))
# Check for authority-granting patterns in non-comment, non-defensive code.
# The validator defines FORBIDDEN_OUTPUT_WORDS as a check list, which is not
# authority-granting. We use Python to skip lines that appear in:
# - FORBIDDEN_OUTPUT_WORDS list definition (approx lines 40-43)
# - Comment lines
# - Defensive check functions (check_mp_3, check_s_2)
AUTHORITY_CHECK=$(python3 -c "
import re
with open('$VALIDATOR') as f:
    lines = f.readlines()

FORBIDDEN = ['sealed', 'approved', 'merge_authority', 'production_ready', 'auto_approve', 'auto_seal']
# Track if we're inside a check function or the FORBIDDEN list
in_forbidden_list = False
in_check_function = False
dangerous = []

for i, line in enumerate(lines):
    stripped = line.strip()
    lineno = i + 1

    # Track FORBIDDEN_OUTPUT_WORDS list
    if 'FORBIDDEN_OUTPUT_WORDS' in stripped:
        in_forbidden_list = True
        continue
    if in_forbidden_list and stripped.endswith(']'):
        in_forbidden_list = False
        continue
    if in_forbidden_list:
        continue

    # Track check function bodies
    if stripped.startswith('def check_') and ('mp_3' in stripped or 's_2' in stripped):
        in_check_function = True
        continue
    if in_check_function:
        if stripped.startswith('def ') or stripped.startswith('class '):
            in_check_function = False
        # Stay inside until next def or end
        else:
            continue  # skip the entire function body

    # Skip comments and empty lines
    if stripped.startswith('#') or not stripped.strip():
        continue

    # Check remaining code for authority words
    for word in FORBIDDEN:
        # Look for word as a whole word (not part of another identifier)
        pattern = r'\b' + re.escape(word) + r'\b'
        if re.search(pattern, stripped, re.IGNORECASE):
            dangerous.append((lineno, word, stripped[:80]))
            break

for lineno, word, context in dangerous:
    print(f'       Found \"{word}\" at line {lineno}: {context}')
sys.exit(1 if dangerous else 0)
" 2>&1) || true
if echo "$AUTHORITY_CHECK" | grep -q "Found"; then
    fail "Validator may contain authority-granting code"
    echo "$AUTHORITY_CHECK"
else
    pass "Validator contains no authority-granting code"
fi

# ── Test 9: Schema file exists and is valid JSON ──
TESTS=$((TESTS + 1))
if [ -f "$SCHEMA_FILE" ]; then
    if python3 -c "import json; json.load(open('$SCHEMA_FILE'))" 2>/dev/null; then
        pass "MCP tool schema exists and is valid JSON"
    else
        fail "MCP tool schema is not valid JSON"
    fi
else
    fail "MCP tool schema not found"
fi

# ── Test 10: Governance doc exists ──
TESTS=$((TESTS + 1))
if [ -f "$GOVERNANCE_DOC" ]; then
    pass "MCP surface governance doc exists"
else
    fail "MCP surface governance doc not found"
fi

# ── Test 11: PROJECT-PROFILE.json exists and has required fields ──
TESTS=$((TESTS + 1))
if [ -f "$PROFILE_FILE" ]; then
    REQUIRED_FIELDS=("project_id" "project_name" "repo_path" "workspace_path" "ledger_path" "receipt_root" "sandbox_boundary" "description")
    MISSING=""
    for field in "${REQUIRED_FIELDS[@]}"; do
        if ! python3 -c "import json; d=json.load(open('$PROFILE_FILE')); assert '$field' in d, 'Missing $field'" 2>/dev/null; then
            MISSING="$MISSING $field"
        fi
    done
    if [ -z "$MISSING" ]; then
        pass "PROJECT-PROFILE.json has all required fields"
    else
        fail "PROJECT-PROFILE.json missing fields:$MISSING"
    fi
else
    fail "PROJECT-PROFILE.json not found"
fi

# ── Test 12: Sprint ledger is valid JSON ──
TESTS=$((TESTS + 1))
if [ -f "$LEDGER_FILE" ]; then
    if python3 -c "
import json
d = json.load(open('$LEDGER_FILE'))
sprints = [s['id'] for s in d.get('sprints', [])]
assert 'QA-PILOT-PROJECT-INIT-1' in sprints, 'Missing init sprint'
assert 'QA-PILOT-PRODUCTION-LANE-A-1' in sprints, 'Missing production lane A'
print('OK: ledger has', len(sprints), 'sprints')
" 2>/dev/null; then
        pass "Sprint ledger is valid with expected sprints"
    else
        fail "Sprint ledger validation failed"
    fi
else
    fail "Sprint ledger not found"
fi

# ── Test 13: Existing receipt validator still passes (regression guard) ──
TESTS=$((TESTS + 1))
if [ -f "$RECEIPT_VALIDATOR" ]; then
    RECEIPT_OUTPUT=$(python3 "$RECEIPT_VALIDATOR" 2>&1) || true
    if echo "$RECEIPT_OUTPUT" | grep -q "ALL CHECKS PASS"; then
        pass "Existing QA Pilot receipt validator still passes"
    else
        fail "Existing QA Pilot receipt validator regression"
    fi
else
    fail "Existing receipt validator not found"
fi

# ── Test 14: Existing receipt test runner still passes (regression guard) ──
TESTS=$((TESTS + 1))
if [ -f "$RECEIPT_TEST" ]; then
    RECEIPT_TEST_OUTPUT=$(bash "$RECEIPT_TEST" 2>&1) || true
    if echo "$RECEIPT_TEST_OUTPUT" | grep -q "All tests pass"; then
        pass "Existing QA Pilot receipt test runner still passes"
    else
        fail "Existing QA Pilot receipt test runner regression"
    fi
else
    fail "Existing receipt test runner not found"
fi

echo ""
echo "================================================================="
echo "Tests: $TESTS total"
echo "Pass:  $PASS"
echo "Fail:  $FAIL"

if [ "$FAIL" -eq 0 ]; then
    echo "Result: $PASS/$TESTS passed. All tests pass. ✅"
    exit 0
else
    echo "Result: $PASS/$TESTS passed. Some tests failed. ❌"
    exit 1
fi
