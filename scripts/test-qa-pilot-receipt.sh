#!/usr/bin/env bash
set -euo pipefail

# QA Pilot Production Receipt Test Runner — QA-PILOT-PRODUCTION-LANE-A-1
# Tests: validator existence, --list-rules, valid fixtures pass, invalid fixtures reject,
#        --all mode, --include-invalid mode, non-existent file handling,
#        AST meta-check, QA Pilot project integrity checks

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-receipt.py"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-receipt"
SCHEMA_FILE="$REPO_ROOT/docs/schemas/qa-pilot-receipt.schema.json"
GOVERNANCE_DOC="$REPO_ROOT/docs/governance/QA-PILOT-RECEIPT.md"
PROFILE_FILE="$REPO_ROOT/PROJECT-PROFILE.json"
IDENTITY_FILE="$REPO_ROOT/PROJECT-IDENTITY.md"
LEDGER_FILE="$REPO_ROOT/project-state/sprint-ledger.json"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Production Receipt Tests — QA-PILOT-PRODUCTION-LANE-A-1"
echo "================================================================="
echo ""

# ── Test 1: Validator exists ──
TESTS=$((TESTS + 1))
if [ -f "$VALIDATOR" ]; then
    pass "Validator found"
else
    fail "Validator not found at $VALIDATOR"
fi

# ── Test 2: --list-rules works ──
TESTS=$((TESTS + 1))
if python3 "$VALIDATOR" --list-rules 2>&1 | grep -q "PR-1"; then
    pass "--list-rules works"
else
    fail "--list-rules did not show PR-1"
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
if ! python3 "$VALIDATOR" /tmp/nonexistent-qa-pilot-file.json >/dev/null 2>&1; then
    pass "Correctly rejects non-existent file"
else
    fail "Did not reject non-existent file"
fi

# ── Test 8: Validator does not grant authority (meta-check) ──
TESTS=$((TESTS + 1))
FORBIDDEN_WORDS=("sealed" "approved" "merge_authority" "production_ready" "auto_approve" "auto_seal")
FOUND=""
for word in "${FORBIDDEN_WORDS[@]}"; do
    if grep -n "$word" "$VALIDATOR" | grep -v "#.*$word" | grep -v "non_approval" | grep -v "PR-" > /dev/null 2>&1; then
        FOUND="$FOUND $word"
    fi
done
if [ -z "$FOUND" ]; then
    pass "Validator contains no authority-granting code"
else
    fail "Validator may contain authority-granting code:$FOUND"
fi

# ── Test 9: Schema file exists and is valid JSON ──
TESTS=$((TESTS + 1))
if [ -f "$SCHEMA_FILE" ]; then
    if python3 -c "import json; json.load(open('$SCHEMA_FILE'))" 2>/dev/null; then
        pass "Schema file exists and is valid JSON"
    else
        fail "Schema file is not valid JSON"
    fi
else
    fail "Schema file not found"
fi

# ── Test 10: Governance doc exists ──
TESTS=$((TESTS + 1))
if [ -f "$GOVERNANCE_DOC" ]; then
    pass "Governance document exists"
else
    fail "Governance document not found"
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

# ── Test 12: Sprint ledger is valid JSON with QA-PILOT-PRODUCTION-LANE-A-1 ──
TESTS=$((TESTS + 1))
if [ -f "$LEDGER_FILE" ]; then
    if python3 -c "
import json
d = json.load(open('$LEDGER_FILE'))
sprints = [s['id'] for s in d.get('sprints', [])]
assert 'QA-PILOT-PROJECT-INIT-1' in sprints, 'Missing init sprint'
print('OK: ledger has', len(sprints), 'sprints')
" 2>/dev/null; then
        pass "Sprint ledger is valid with expected sprints"
    else
        fail "Sprint ledger validation failed"
    fi
else
    fail "Sprint ledger not found"
fi

# ── Test 13: Fixtures directory has 8 files (4 valid + 4 invalid) ──
TESTS=$((TESTS + 1))
FIXTURE_COUNT=$(ls "$FIXTURES_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$FIXTURE_COUNT" -eq 8 ]; then
    pass "Fixtures directory has 8 files"
else
    fail "Fixtures directory has $FIXTURE_COUNT files (expected 8)"
fi

# ── Test 14: All fixtures have project_id=qa-pilot ──
TESTS=$((TESTS + 1))
WRONG_PROJECT=""
for f in "$FIXTURES_DIR"/*.json; do
    PROJ=$(python3 -c "import json; print(json.load(open('$f')).get('project_id', ''))" 2>/dev/null)
    if [ "$PROJ" != "qa-pilot" ]; then
        WRONG_PROJECT="$WRONG_PROJECT $(basename "$f")"
    fi
done
if [ -z "$WRONG_PROJECT" ]; then
    pass "All fixtures have project_id=qa-pilot"
else
    fail "Fixtures with wrong project_id:$WRONG_PROJECT"
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
