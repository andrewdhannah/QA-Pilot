#!/usr/bin/env bash
set -euo pipefail

# QA Pilot QA Packet Ingest Test Runner — QA-PILOT-QA-PACKET-INGEST-1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-qa-packet-ingest.py"
INGEST_CLI="$SCRIPT_DIR/qa_pilot_qa_packet_ingest.py"
FIXTURES_DIR="$REPO_ROOT/docs/examples/qa-pilot-qa-packet-ingest"
GOV_DOC="$REPO_ROOT/docs/governance/QA-PILOT-QA-PACKET-INGEST.md"
SCHEMA_FILE="$REPO_ROOT/docs/schemas/qa-pilot-qa-packet-ingest.schema.json"
PASS=0
FAIL=0
TESTS=0

pass() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ❌ $1"; }

echo "QA Pilot QA Packet Ingest Tests — QA-PILOT-QA-PACKET-INGEST-1"
echo "========================================================================"
echo ""

# ── Test 1: Validator exists ──
TESTS=$((TESTS + 1))
if [ -f "$VALIDATOR" ]; then
    pass "Packet ingest validator found"
else
    fail "Packet ingest validator not found"
fi

# ── Test 2: --list-rules works ──
TESTS=$((TESTS + 1))
if python3 "$VALIDATOR" --list-rules 2>&1 | grep -q "PI-1"; then
    pass "--list-rules works"
else
    fail "--list-rules did not show PI-1"
fi

# ── Test 3: Valid fixtures all pass ──
TESTS=$((TESTS + 1))
if python3 "$VALIDATOR" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Valid fixtures all pass"
else
    fail "Valid fixtures did not all pass"
    python3 "$VALIDATOR" 2>&1
fi

# ── Test 4: Invalid fixtures all fail ──
TESTS=$((TESTS + 1))
INVALID_OUTPUT=$(python3 "$VALIDATOR" --include-invalid 2>&1) || true
INVALID_FAIL_COUNT=$(echo "$INVALID_OUTPUT" | grep -c "❌" || true)
if [ "$INVALID_FAIL_COUNT" -ge 4 ]; then
    pass "Invalid fixtures correctly rejected ($INVALID_FAIL_COUNT failures detected)"
else
    fail "Not enough invalid fixtures rejected (expected >= 4)"
fi

# ── Test 5: All 8 fixture files exist ──
TESTS=$((TESTS + 1))
COUNT=$(ls "$FIXTURES_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$COUNT" -eq 8 ]; then
    pass "All 8 fixture files exist (4 valid + 4 invalid)"
else
    fail "Expected 8 fixtures, found $COUNT"
fi

# ── Test 6: Ingest CLI exists ──
TESTS=$((TESTS + 1))
if [ -f "$INGEST_CLI" ]; then
    pass "Packet ingest CLI found"
else
    fail "Packet ingest CLI not found"
fi

# ── Test 7: Ingest CLI --help works ──
TESTS=$((TESTS + 1))
if python3 "$INGEST_CLI" --help 2>&1 | grep -q "usage\|Usage"; then
    pass "Ingest CLI --help works"
else
    fail "Ingest CLI --help did not produce output"
fi

# ── Test 8: Ingest CLI validate command works on valid fixture ──
TESTS=$((TESTS + 1))
VALID_FIXTURE="$FIXTURES_DIR/valid-claim-registry-packet.json"
if python3 "$INGEST_CLI" validate "$VALID_FIXTURE" 2>&1 | grep -q "VALID"; then
    pass "Ingest CLI validate accepts valid fixture"
else
    fail "Ingest CLI validate rejected valid fixture"
    python3 "$INGEST_CLI" validate "$VALID_FIXTURE" 2>&1
fi

# ── Test 9: Ingest CLI validate rejects invalid fixture ──
TESTS=$((TESTS + 1))
INVALID_FIXTURE="$FIXTURES_DIR/invalid-wrong-source-project.json"
INVALID_OUTPUT=$(python3 "$INGEST_CLI" validate "$INVALID_FIXTURE" 2>&1) || true
if echo "$INVALID_OUTPUT" | grep -q "INVALID\|REJECTED\|FAIL"; then
    pass "Ingest CLI validate rejects invalid fixture"
else
    fail "Ingest CLI validate accepted invalid fixture"
    echo "$INVALID_OUTPUT"
fi

# ── Test 10: Ingest CLI list command works ──
TESTS=$((TESTS + 1))
if python3 "$INGEST_CLI" list 2>&1 | grep -q "fixture\|packet\|Ingested\|total\|ingested"; then
    pass "Ingest CLI list command works"
else
    fail "Ingest CLI list command did not produce output"
fi

# ── Test 11: Ingest CLI status command works ──
TESTS=$((TESTS + 1))
if python3 "$INGEST_CLI" status 2>&1 | grep -q "packet\|store\|total\|status\|Ingest"; then
    pass "Ingest CLI status command works"
else
    fail "Ingest CLI status command did not produce output"
fi

# ── Test 12: Governance doc exists ──
TESTS=$((TESTS + 1))
if [ -f "$GOV_DOC" ]; then
    pass "Packet ingest governance doc exists"
else
    fail "Packet ingest governance doc not found"
fi

# ── Test 13: Schema file exists and is valid JSON ──
TESTS=$((TESTS + 1))
if [ -f "$SCHEMA_FILE" ]; then
    if python3 -c "import json; json.load(open('$SCHEMA_FILE'))" 2>/dev/null; then
        pass "Packet ingest schema is valid JSON"
    else
        fail "Packet ingest schema is not valid JSON"
    fi
else
    fail "Packet ingest schema not found"
fi

# ── Test 14: PI-14 scan (no Librarian runtime refs) ──
TESTS=$((TESTS + 1))
FORBIDDEN=("MCPController.swift" "Sources/App/" "AppEntry.swift")
FOUND=""
for word in "${FORBIDDEN[@]}"; do
    if grep -r "$word" "$GOV_DOC" "$SCHEMA_FILE" 2>/dev/null | grep -v "#" > /dev/null; then
        FOUND="$FOUND $word"
    fi
done
if [ -z "$FOUND" ]; then
    pass "PI-14: No Librarian runtime references in ingestion docs"
else
    fail "PI-14: Found Librarian runtime refs:$FOUND"
fi

# ── Test 15: Existing broker plan validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-broker-plan.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing broker plan validator still passes"
else
    fail "Existing broker plan validator regression"
fi

# ── Test 16: Existing broker audit store validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-broker-audit-store.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing broker audit store validator still passes"
else
    fail "Existing broker audit store validator regression"
fi

# ── Test 17: Existing receipt validator still passes ──
TESTS=$((TESTS + 1))
if python3 "$SCRIPT_DIR/validate-qa-pilot-receipt.py" 2>&1 | grep -q "ALL CHECKS PASS"; then
    pass "Existing receipt validator still passes"
else
    fail "Existing receipt validator regression"
fi

# ── Test 18: Valid fixture names do not claim authority ──
TESTS=$((TESTS + 1))
BAD_NAMES=""
for f in "$FIXTURES_DIR"/valid-*.json; do
    NAME=$(basename "$f")
    if echo "$NAME" | grep -q "approval\|seal\|merge\|production"; then
        BAD_NAMES="$BAD_NAMES $NAME"
    fi
done
if [ -z "$BAD_NAMES" ]; then
    pass "No valid fixture claims approval/seal/merge authority"
else
    fail "Valid fixtures claiming authority:$BAD_NAMES"
fi

# ── Test 19: QA Pilot ledger is valid JSON ──
TESTS=$((TESTS + 1))
if python3 -c "import json; json.load(open('$REPO_ROOT/project-state/sprint-ledger.json'))" 2>/dev/null; then
    pass "QA Pilot ledger is valid JSON"
else
    fail "QA Pilot ledger is not valid JSON"
fi

# ── Test 20: Prohibited-zone scan ──
TESTS=$((TESTS + 1))
PROHIBITED_HITS=""
if [ -f "/Users/andrew/Desktop/CarbideFrame/active/librarian/docs/governance/QA-PILOT-QA-PACKET-INGEST.md" ]; then
    PROHIBITED_HITS="$PROHIBITED_HITS gov-doc"
fi
if [ -f "/Users/andrew/Desktop/CarbideFrame/active/librarian/scripts/validate-qa-pilot-qa-packet-ingest.py" ]; then
    PROHIBITED_HITS="$PROHIBITED_HITS validator"
fi
if [ -z "$PROHIBITED_HITS" ]; then
    pass "Prohibited-zone: no QA Pilot packet-ingest files leaked into Librarian"
else
    fail "Prohibited-zone: found packet-ingest files in Librarian:$PROHIBITED_HITS"
fi

# ── Test 21: Ingest CLI ingest command imports valid fixture ──
TESTS=$((TESTS + 1))
INGEST_OUTPUT=$(python3 "$INGEST_CLI" ingest "$FIXTURES_DIR/valid-project-state-packet.json" 2>&1) || true
if echo "$INGEST_OUTPUT" | grep -q "imported\|ingested\|stored\|DONE"; then
    pass "Ingest CLI ingest imports valid packet"
else
    fail "Ingest CLI ingest did not import valid packet"
    echo "  Output: $INGEST_OUTPUT"
fi

# ── Test 22: Ingest CLI clear command works ──
TESTS=$((TESTS + 1))
if python3 "$INGEST_CLI" clear 2>&1 | grep -q "cleared\|Cleared\|DONE"; then
    pass "Ingest CLI clear command works"
else
    fail "Ingest CLI clear command did not produce output"
fi

echo ""
echo "========================================================================"
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
