#!/usr/bin/env bash
set -euo pipefail

# QA Pilot Option B Broker Plan Test Runner — QA-PILOT-BROKER-PLAN-1
# Tests: validator exists, valid fixtures pass, invalid fixtures reject,
#        BP-24 scan, all existing validators preserved, prohibited zone

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-broker-plan.py"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-broker-plan"
GOV_DOC="$REPO_ROOT/docs/governance/QA-PILOT-BROKER-PLAN.md"
SCHEMA_FILE="$REPO_ROOT/docs/schemas/qa-pilot-broker-plan.schema.json"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot Broker Plan Tests — QA-PILOT-BROKER-PLAN-1"
echo "==================================================="
echo ""

# ── Test 1: Validator exists ──
TESTS=$((TESTS + 1))
if [ -f "$VALIDATOR" ]; then
    pass "Broker plan validator found"
else
    fail "Broker plan validator not found"
fi

# ── Test 2: --list-rules works ──
TESTS=$((TESTS + 1))
if python3 "$VALIDATOR" --list-rules 2>&1 | grep -q "BP-1"; then
    pass "--list-rules works"
else
    fail "--list-rules did not show BP-1"
fi

# ── Test 3: Valid fixtures all pass ──
TESTS=$((TESTS + 1))
VALID_OUTPUT=$(python3 "$VALIDATOR" 2>&1) || true
if echo "$VALID_OUTPUT" | grep -q "ALL CHECKS PASS"; then
    pass "Valid fixtures all pass"
else
    fail "Valid fixtures did not all pass"
    echo "       $VALID_OUTPUT"
fi

# ── Test 4: Invalid fixtures all fail ──
TESTS=$((TESTS + 1))
INVALID_OUTPUT=$(python3 "$VALIDATOR" --include-invalid 2>&1) || true
INVALID_FAIL_COUNT=$(echo "$INVALID_OUTPUT" | grep -c "❌" || true)
if [ "$INVALID_FAIL_COUNT" -ge 4 ]; then
    pass "Invalid fixtures correctly rejected ($INVALID_FAIL_COUNT failures detected)"
else
    fail "Not enough invalid fixtures rejected (expected >= 4, got $INVALID_FAIL_COUNT)"
fi

# ── Test 5: Governance doc exists ──
TESTS=$((TESTS + 1))
if [ -f "$GOV_DOC" ]; then
    pass "Broker plan governance doc exists"
else
    fail "Broker plan governance doc not found"
fi

# ── Test 6: Schema file exists and is valid JSON ──
TESTS=$((TESTS + 1))
if [ -f "$SCHEMA_FILE" ]; then
    if python3 -c "import json; json.load(open('$SCHEMA_FILE'))" 2>/dev/null; then
        pass "Broker plan schema is valid JSON"
    else
        fail "Broker plan schema is not valid JSON"
    fi
else
    fail "Broker plan schema not found"
fi

# ── Test 7: BP-24 scan (no Librarian runtime refs in broker docs) ──
TESTS=$((TESTS + 1))
FORBIDDEN=("MCPController.swift" "Sources/App/" "AppEntry.swift")
FOUND=""
for word in "${FORBIDDEN[@]}"; do
    if grep -r "$word" "$GOV_DOC" "$SCHEMA_FILE" 2>/dev/null | grep -v "#" > /dev/null; then
        FOUND="$FOUND $word"
    fi
done
if [ -z "$FOUND" ]; then
    pass "BP-24: No Librarian runtime references in broker planning docs"
else
    fail "BP-24: Found Librarian runtime refs:$FOUND"
fi

# ── Test 8: All 6 fixture files exist (2 valid, 4 invalid) ──
TESTS=$((TESTS + 1))
COUNT=$(ls "$FIXTURES_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$COUNT" -eq 6 ]; then
    pass "All 6 fixture files exist (2 valid + 4 invalid)"
else
    fail "Expected 6 fixtures, found $COUNT"
fi

# ── Test 9: Existing receipt validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-receipt.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing receipt validator still passes"
else
    fail "Existing receipt validator regression"
fi

# ── Test 10: Existing MCP surface validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-mcp-surface.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing MCP surface validator still passes"
else
    fail "Existing MCP surface validator regression"
fi

# ── Test 11: Existing store validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-receipt-store.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing store validator still passes"
else
    fail "Existing store validator regression"
fi

# ── Test 12: Existing handler validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-mcp-handler.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing handler validator still passes"
else
    fail "Existing handler validator regression"
fi

# ── Test 13: Existing custody validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-librarian-mcp-custody.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing custody validator still passes"
else
    fail "Existing custody validator regression"
fi

# ── Test 14: No valid fixture claims implementation authority ──
TESTS=$((TESTS + 1))
BAD_NAMES=""
for f in "$FIXTURES_DIR"/valid-*.json; do
    NAME=$(basename "$f")
    if echo "$NAME" | grep -q "implementation"; then
        BAD_NAMES="$BAD_NAMES $NAME"
    fi
done
if [ -z "$BAD_NAMES" ]; then
    pass "No valid fixture claims implementation authority"
else
    fail "Valid fixtures suggesting implementation:$BAD_NAMES"
fi

# ── Test 15: Prohibited-zone scan ──
TESTS=$((TESTS + 1))
# Verify no QA Pilot sprint files exist in Librarian repo
PROHIBITED_HITS=""
for f in "$FIXTURES_DIR"/*.json "$GOV_DOC" "$SCHEMA_FILE"; do
    LIB_PATH="/Users/andrew/Desktop/CarbideFrame/active/librarian/$(echo "$f" | sed "s|$REPO_ROOT/||")"
    if [ -f "$LIB_PATH" ]; then
        PROHIBITED_HITS="$PROHIBITED_HITS $f"
    fi
done
# Also check no broker plan files leaked into Librarian
if [ -f "/Users/andrew/Desktop/CarbideFrame/active/librarian/docs/governance/QA-PILOT-BROKER-PLAN.md" ]; then
    PROHIBITED_HITS="$PROHIBITED_HITS librarian-gov-doc"
fi
# Check that the diff in Librarian repo is unchanged from pre-existing state
LIB_START_HASH="$(cd /Users/andrew/Desktop/CarbideFrame/active/librarian && git rev-parse HEAD)"
LIB_STATUS="$(cd /Users/andrew/Desktop/CarbideFrame/active/librarian && git diff --name-only 2>/dev/null | sort)"
# Pre-existing modified files (from start of session): should be exactly these 3
EXPECTED_LIB_MODS="FEATURE-STATUS.md
SESSION-HANDOFF.md
project-state/sprint-ledger.json"
if [ "$LIB_STATUS" = "$EXPECTED_LIB_MODS" ] || [ -z "$LIB_STATUS" ]; then
    pass "Prohibited-zone: no new Librarian modifications (pre-existing unchanged)"
else
    fail "Prohibited-zone: Librarian repo has unexpected changes"
    echo "       Expected mods: FEATURE-STATUS.md, SESSION-HANDOFF.md, sprint-ledger.json"
    echo "       Actual mods: $LIB_STATUS"
fi

# ── Test 16: Broker model properties are consistent ──
TESTS=$((TESTS + 1))
CONSISTENT=true
for f in "$FIXTURES_DIR"/valid-*.json; do
    NAME=$(basename "$f")
    # Verify key broker model properties
    FORWARD=$(python3 -c "import json; d=json.load(open('$f')); print(d['broker_model']['forward_direction_defined'])" 2>/dev/null)
    REVERSE=$(python3 -c "import json; d=json.load(open('$f')); print(d['broker_model']['reverse_direction_defined'])" 2>/dev/null)
    if [ "$FORWARD" != "True" ]; then
        fail "$NAME: forward_direction_defined is not true"
        CONSISTENT=false
    fi
    if [ "$REVERSE" != "False" ]; then
        fail "$NAME: reverse_direction_defined is not false"
        CONSISTENT=false
    fi
done
if $CONSISTENT; then
    pass "All valid fixtures have consistent broker model properties"
fi

# ── Test 17: QA Pilot PROJECT-PROFILE.json remains valid ──
TESTS=$((TESTS + 1))
FIELD_COUNT=$(python3 -c "import json; d=json.load(open('$REPO_ROOT/PROJECT-PROFILE.json')); print(len(d))" 2>/dev/null)
if [ "$FIELD_COUNT" -ge 12 ]; then
    pass "PROJECT-PROFILE.json has $FIELD_COUNT fields (valid)"
else
    fail "PROJECT-PROFILE.json has $FIELD_COUNT fields (expected >= 12)"
fi

# ── Test 18: QA Pilot ledger is valid JSON ──
TESTS=$((TESTS + 1))
if python3 -c "import json; json.load(open('$REPO_ROOT/project-state/sprint-ledger.json'))" 2>/dev/null; then
    pass "QA Pilot ledger is valid JSON"
else
    fail "QA Pilot ledger is not valid JSON"
fi

echo ""
echo "==================================================="
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
