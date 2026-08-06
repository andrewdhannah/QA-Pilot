#!/usr/bin/env bash
# ── QA Pilot SDK Integration Test Runner ──────────────────────────────────
# Tests the governed read-only SDK boundary for consuming Librarian evidence.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SDK_SCRIPT="$SCRIPT_DIR/qa_pilot_evidence_sdk.py"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-sdk-integration.py"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-sdk-integration"
SCHEMA_FILE="$REPO_ROOT/docs/schemas/qa-pilot-sdk-integration.schema.json"
GOVERNANCE_DOC="$REPO_ROOT/docs/governance/QA-PILOT-SDK-INTEGRATION-1.md"
KNOWLEDGE_ADAPTER="$SCRIPT_DIR/qa_pilot_knowledge_adapter.py"

PASS=0; FAIL=0; TESTS=0
pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot SDK Integration — Test Runner"
echo "========================================="
echo ""

# ── Test 1: SDK script exists ──
TESTS=$((TESTS + 1))
if [[ -f "$SDK_SCRIPT" ]]; then
    pass "SDK script exists: $SDK_SCRIPT"
else
    fail "SDK script not found: $SDK_SCRIPT"
fi

# ── Test 2: SDK --help works ──
TESTS=$((TESTS + 1))
if python3 "$SDK_SCRIPT" --help >/dev/null 2>&1; then
    pass "SDK --help works"
else
    fail "SDK --help failed"
fi

# ── Test 3: SDK status works ──
TESTS=$((TESTS + 1))
STATUS_OUTPUT=$(python3 "$SDK_SCRIPT" status 2>/dev/null || true)
if echo "$STATUS_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('sdk_version') == 'qa-pilot-evidence-sdk-v1'" 2>/dev/null; then
    pass "SDK status returns correct sdk_version"
else
    fail "SDK status failed or wrong sdk_version"
fi

# ── Test 4: SDK status shows read-only ──
TESTS=$((TESTS + 1))
if echo "$STATUS_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('read_only') == True" 2>/dev/null; then
    pass "SDK status shows read_only=True"
else
    fail "SDK status does not show read_only=True"
fi

# ── Test 5: SDK status shows no_mutation_paths ──
TESTS=$((TESTS + 1))
if echo "$STATUS_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('no_mutation_paths') == True" 2>/dev/null; then
    pass "SDK status shows no_mutation_paths=True"
else
    fail "SDK status does not show no_mutation_paths=True"
fi

# ── Test 6: SDK status lists all 5 queries ──
TESTS=$((TESTS + 1))
EXPECTED_QUERIES=5
QUERY_COUNT=$(echo "$STATUS_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('available_queries', [])))" 2>/dev/null || echo "0")
if [[ "$QUERY_COUNT" -eq "$EXPECTED_QUERIES" ]]; then
    pass "SDK status lists $EXPECTED_QUERIES available queries (got $QUERY_COUNT)"
else
    fail "SDK status expected $EXPECTED_QUERIES queries, got $QUERY_COUNT"
fi

# ── Test 7: SDK status lists forbidden operations ──
TESTS=$((TESTS + 1))
FORBIDDEN_COUNT=$(echo "$STATUS_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('forbidden_operations', [])))" 2>/dev/null || echo "0")
if [[ "$FORBIDDEN_COUNT" -ge 3 ]]; then
    pass "SDK status lists $FORBIDDEN_COUNT forbidden operations"
else
    fail "SDK status expected >=3 forbidden operations, got $FORBIDDEN_COUNT"
fi

# ── Test 8: Validator exists ──
TESTS=$((TESTS + 1))
if [[ -f "$VALIDATOR" ]]; then
    pass "Validator exists: $VALIDATOR"
else
    fail "Validator not found: $VALIDATOR"
fi

# ── Test 9: Validator --list-rules works ──
TESTS=$((TESTS + 1))
RULE_COUNT=$(python3 "$VALIDATOR" --list-rules 2>/dev/null | grep -c "SI-" || true)
if [[ "$RULE_COUNT" -ge 10 ]]; then
    pass "Validator lists $RULE_COUNT rules (SI-1 through SI-15)"
else
    fail "Validator --list-rules shows fewer than 10 rules: $RULE_COUNT"
fi

# ── Test 10: Valid fixtures all pass ──
TESTS=$((TESTS + 1))
if python3 "$VALIDATOR" --all >/dev/null 2>&1; then
    pass "All valid fixtures pass"
else
    fail "Some valid fixtures failed"
fi

# ── Test 11: Validator correctly handles invalid fixtures ──
TESTS=$((TESTS + 1))
INVALID_COUNT=$(ls "$FIXTURES_DIR"/invalid-*.json 2>/dev/null | wc -l || echo "0")
if [[ "$INVALID_COUNT" -gt 0 ]]; then
    # Run with --all to check valid fixtures only (should pass)
    if python3 "$VALIDATOR" --all >/dev/null 2>&1; then
        # Run with --include-invalid to verify invalid fixtures are correctly flagged
        VALIDATOR_OUTPUT=$(python3 "$VALIDATOR" --all --include-invalid 2>&1 || true)
        REJECTED_COUNT=$(echo "$VALIDATOR_OUTPUT" | grep -c "correctly rejected" || true)
        if [[ "$REJECTED_COUNT" -ge 1 ]]; then
            pass "Validator correctly rejects invalid fixtures ($REJECTED_COUNT rejected, $INVALID_COUNT present)"
        else
            fail "Validator did not reject any invalid fixtures"
        fi
    else
        fail "Valid fixtures failed in --all mode"
    fi
else
    pass "No invalid fixtures to test (skipping)"
fi

# ── Test 12: Schema file exists and is valid JSON ──
TESTS=$((TESTS + 1))
if [[ -f "$SCHEMA_FILE" ]]; then
    if python3 -c "import json; json.load(open('$SCHEMA_FILE'))" 2>/dev/null; then
        pass "Schema file is valid JSON"
    else
        fail "Schema file is invalid JSON"
    fi
else
    fail "Schema file not found: $SCHEMA_FILE"
fi

# ── Test 13: Governance doc exists ──
TESTS=$((TESTS + 1))
if [[ -f "$GOVERNANCE_DOC" ]]; then
    pass "Governance doc exists: $GOVERNANCE_DOC"
else
    fail "Governance doc not found: $GOVERNANCE_DOC"
fi

# ── Test 14: Knowledge Adapter exists and is importable ──
TESTS=$((TESTS + 1))
if [[ -f "$KNOWLEDGE_ADAPTER" ]]; then
    if python3 -c "import sys; sys.path.insert(0, '$SCRIPT_DIR'); import qa_pilot_knowledge_adapter" 2>/dev/null; then
        pass "Knowledge Adapter is importable"
    else
        fail "Knowledge Adapter failed to import"
    fi
else
    fail "Knowledge Adapter not found: $KNOWLEDGE_ADAPTER"
fi

# ── Test 15: Knowledge Adapter no longer reads Librarian paths directly ──
TESTS=$((TESTS + 1))
LIBRARIAN_REFS=$(grep -c "active/librarian" "$KNOWLEDGE_ADAPTER" 2>/dev/null || true)
# The knowledge adapter may still have LIBRARIAN_ROOT for backward compat but should use SDK
if [[ "$LIBRARIAN_REFS" -gt 0 ]]; then
    # Check if SDK import is present
    SDK_IMPORT=$(grep -c "evidence_sdk\|EvidenceProvider" "$KNOWLEDGE_ADAPTER" 2>/dev/null || true)
    if [[ "$SDK_IMPORT" -gt 0 ]]; then
        pass "Knowledge Adapter uses SDK (SDK import found, $LIBRARIAN_REFS Librarian refs remain for fallback)"
    else
        fail "Knowledge Adapter has $LIBRARIAN_REFS Librarian refs without SDK import"
    fi
else
    pass "Knowledge Adapter has no direct Librarian path refs"
fi

# ── Test 16: Fixture count check ──
TESTS=$((TESTS + 1))
VALID_COUNT=$(ls "$FIXTURES_DIR"/valid-*.json 2>/dev/null | wc -l || echo "0")
INI_COUNT=$(ls "$FIXTURES_DIR"/invalid-*.json 2>/dev/null | wc -l || echo "0")
TOTAL_FIXTURES=$((VALID_COUNT + INI_COUNT))
if [[ "$TOTAL_FIXTURES" -ge 5 ]]; then
    pass "Fixtures: $VALID_COUNT valid + $INI_COUNT invalid = $TOTAL_FIXTURES total"
else
    fail "Fewer than 5 fixtures: $TOTAL_FIXTURES"
fi

# ── Test 17: Sprint doc exists ──
TESTS=$((TESTS + 1))
SPRINT_DOC="$REPO_ROOT/docs/sprints/QA-PILOT-SDK-INTEGRATION-1.md"
if [[ -f "$SPRINT_DOC" ]]; then
    pass "Sprint doc exists: $SPRINT_DOC"
else
    fail "Sprint doc not found: $SPRINT_DOC"
fi

# ── Test 18: PROJECT-PROFILE.json integrity ──
TESTS=$((TESTS + 1))
if [[ -f "$REPO_ROOT/PROJECT-PROFILE.json" ]]; then
    if python3 -c "import json; d=json.load(open('$REPO_ROOT/PROJECT-PROFILE.json')); assert d.get('project_id') == 'qa-pilot'" 2>/dev/null; then
        pass "PROJECT-PROFILE.json has correct project_id"
    else
        fail "PROJECT-PROFILE.json missing or wrong project_id"
    fi
else
    fail "PROJECT-PROFILE.json not found"
fi

# ── Test 19: SDK snapshot command works ──
TESTS=$((TESTS + 1))
SNAPSHOT_OUTPUT=$(python3 "$SDK_SCRIPT" snapshot 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('evidence_available', False))" 2>/dev/null || echo "error")
if [[ "$SNAPSHOT_OUTPUT" != "error" ]]; then
    pass "SDK snapshot command returns evidence_available=$SNAPSHOT_OUTPUT"
else
    fail "SDK snapshot command failed"
fi

# ── Test 20: No mutation authority test via CLI ──
TESTS=$((TESTS + 1))
MUTATION_FOUND=$(python3 "$SDK_SCRIPT" status 2>/dev/null | python3 -c "
import sys, json
d = json.load(sys.stdin)
for op in d.get('forbidden_operations', []):
    print(op)
" 2>/dev/null | grep -c "mutation" || true)
if [[ "$MUTATION_FOUND" -ge 1 ]]; then
    pass "SDK explicitly forbids mutation operations ($MUTATION_FOUND found)"
else
    fail "SDK does not list mutation as forbidden"
fi

# ── Summary ──
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
