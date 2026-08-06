#!/usr/bin/env bash
# QA Pilot Qualification Substrate — 17 Acceptance Gates
set +e  # Don't exit on error — we count failures
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VALIDATOR="$PROJECT_ROOT/scripts/validate-qa-pilot-qualification.py"
FIXTURE_DIR="$PROJECT_ROOT/docs/examples/qa-pilot-qualification"
STORE_DIR="$PROJECT_ROOT/data/qualification-records"
SCHEMA_PATH="$PROJECT_ROOT/docs/schemas/qa-pilot-qualification-record.schema.json"
PASS=0
FAIL=0

header() { echo -e "\n=== $1 ==="; }
pass() { echo "  ✅ $1"; ((PASS++)); }
fail() { echo "  ❌ $1"; ((FAIL++)); }

cd "$PROJECT_ROOT"

# ---- AG-1: Schema file exists and is valid JSON ----
header "AG-1: Schema exists and is valid JSON"
if python3 -c "import json; json.load(open('$SCHEMA_PATH'))" 2>/dev/null; then
    pass "Schema at $SCHEMA_PATH is valid JSON"
else
    fail "Schema missing or invalid at $SCHEMA_PATH"
fi

# ---- AG-2: Validator script exists ----
header "AG-2: Validator script exists"
if [ -f "$VALIDATOR" ]; then
    chmod +x "$VALIDATOR" 2>/dev/null
    pass "Validator exists"
else
    fail "Validator not found at $VALIDATOR"
fi

# ---- AG-3: All valid fixtures pass ----
header "AG-3: All valid fixtures pass"
VALID_OK=0
VALID_COUNT=0
for fx in "$FIXTURE_DIR"/valid/*.json; do
    fn=$(basename "$fx")
    ((VALID_COUNT++))
    # Run the fixture validation and check for valid->valid match
    output=$(python3 "$VALIDATOR" fixture 2>&1)
    if echo "$output" | grep -q "$fn.*actual=valid"; then
        pass "$fn"
        ((VALID_OK++))
    else
        fail "$fn did not pass as valid"
    fi
done
if [ "$VALID_OK" -eq "$VALID_COUNT" ]; then
    pass "All $VALID_COUNT valid fixtures pass"
else
    fail "Expected $VALID_COUNT valid fixtures to pass, got $VALID_OK"
fi

# ---- AG-4: All invalid fixtures are rejected ----
header "AG-4: All invalid fixtures are rejected"
INVALID_OK=0
INVALID_COUNT=0
for fx in "$FIXTURE_DIR"/invalid/*.json; do
    fn=$(basename "$fx")
    ((INVALID_COUNT++))
    output=$(python3 "$VALIDATOR" fixture 2>&1)
    if echo "$output" | grep -q "$fn.*actual=invalid"; then
        pass "$fn"
        ((INVALID_OK++))
    else
        fail "$fn was not rejected as invalid"
    fi
done
if [ "$INVALID_OK" -eq "$INVALID_COUNT" ]; then
    pass "All $INVALID_COUNT invalid fixtures rejected"
else
    fail "Expected $INVALID_COUNT invalid fixtures rejected, got $INVALID_OK"
fi

# ---- AG-5: Qualification store exists ----
header "AG-5: Qualification store exists"
if [ -d "$STORE_DIR" ] && [ -f "$STORE_DIR/qualification-index.json" ]; then
    pass "Store directory and index exist"
else
    fail "Store or index missing"
fi

# ---- AG-6: Validator chain self-test passes ----
header "AG-6: Validator chain self-test passes"
output=$(python3 "$VALIDATOR" chain 2>&1)
if echo "$output" | grep -q "Self-test.*PASS"; then
    pass "Validator chain self-test passes"
else
    fail "Validator chain self-test failed"
fi

# ---- AG-7: Store index is valid JSON ----
header "AG-7: Store index is valid JSON"
if python3 -c "import json; json.load(open('$STORE_DIR/qualification-index.json'))" 2>/dev/null; then
    pass "Store index is valid JSON"
else
    fail "Store index is not valid JSON"
fi

# ---- AG-8: Schema loads in validator ----
header "AG-8: Validator loads schema"
output=$(python3 "$VALIDATOR" chain 2>&1)
if echo "$output" | grep -q "Schema.*✅"; then
    pass "Schema loads in validator"
else
    fail "Schema not loaded"
fi

# ---- AG-9: Fixture mode runs ----
header "AG-9: Fixture mode runs"
output=$(python3 "$VALIDATOR" fixture 2>&1)
if echo "$output" | grep -q "Fixtures:"; then
    pass "Fixture mode runs"
else
    fail "Fixture mode failed"
fi

# ---- AG-10: Live mode handles store (empty or populated) ----
header "AG-10: Live mode handles store"
output=$(python3 "$VALIDATOR" live 2>&1)
if echo "$output" | grep -q "pass, 0 fail"; then
    pass "Live mode validates correctly"
else
    fail "Live mode unexpected: $output"
fi

# ---- AG-11: Validate mode handles missing record ----
header "AG-11: Validate mode handles missing record"
output=$(python3 "$VALIDATOR" validate --record-id "QR-NONEXIST-0001" 2>&1) || true
if echo "$output" | grep -q "not found"; then
    pass "Validate mode reports missing record"
else
    fail "Validate mode unexpected: $output"
fi

# ---- AG-12: Record ID naming convention ----
header "AG-12: Record ID naming convention"
BAD=0
for fx in "$FIXTURE_DIR"/valid/*.json; do
    rid=$(python3 -c "import json; print(json.load(open('$fx')).get('record_id',''))" 2>/dev/null)
    if [[ ! "$rid" =~ ^QR-[A-Z0-9]{4,12}-[0-9]{4}$ ]]; then
        fail "Bad record_id format: $rid (in $(basename $fx))"
        ((BAD++))
    fi
done
if [ "$BAD" -eq 0 ]; then
    pass "All valid fixture record_ids match naming convention"
fi

# ---- AG-13: Prohibited fields enforcement ----
header "AG-13: Authority-claiming field enforcement (QR-9)"
if python3 "$VALIDATOR" fixture 2>&1 | grep -q "authority-claiming.json.*actual=invalid"; then
    pass "Authority-claiming fields detected"
else
    fail "Authority-claiming fixture not properly rejected"
fi

# ---- AG-14: Custody enforcement ----
header "AG-14: Custody enforcement (QR-7)"
if python3 "$VALIDATOR" fixture 2>&1 | grep -q "bad-custody.json.*actual=invalid"; then
    pass "Bad custody detected"
else
    fail "Bad custody fixture not properly rejected"
fi

# ---- AG-15: Level/score mismatch enforcement ----
header "AG-15: Level/score mismatch enforcement (QR-17)"
if python3 "$VALIDATOR" fixture 2>&1 | grep -q "bad-level-for-score.json.*actual=invalid"; then
    pass "Level/score mismatch detected"
else
    fail "Level/score mismatch fixture not properly rejected"
fi

# ---- AG-16: Reviewer type requires owner_decision ----
header "AG-16: Reviewer type requires owner_decision (QR-25)"
if python3 "$VALIDATOR" fixture 2>&1 | grep -q "reviewer-no-decision-evidence.json.*actual=invalid"; then
    pass "Reviewer without owner_decision detected"
else
    fail "Reviewer without owner_decision fixture not properly rejected"
fi

# ---- AG-17: Evidence lineage enforcement ----
header "AG-17: Evidence lineage enforcement (QR-14 stale)"
if python3 "$VALIDATOR" fixture 2>&1 | grep -q "stale-evidence.json.*actual=invalid"; then
    pass "Stale evidence detected"
else
    fail "Stale evidence fixture not properly rejected"
fi

# ---- Summary ----
header "Summary"
echo "  Passed: $PASS"
echo "  Failed: $FAIL"
echo "  Total:  $((PASS + FAIL))"
if [ "$FAIL" -eq 0 ]; then
    echo ""
    echo "✅ All acceptance gates pass."
    exit 0
else
    echo ""
    echo "❌ $FAIL gate(s) failed."
    exit 1
fi
