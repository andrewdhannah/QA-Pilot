#!/usr/bin/env bash
# QA Pilot Qualification Review Surface — 15 Acceptance Gates
set +e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SURFACE="$PROJECT_ROOT/scripts/qa_pilot_qualification_review_surface.py"
STORE_DIR="$PROJECT_ROOT/data/qualification-records"
RESULTS_DIR="$PROJECT_ROOT/data/qualification-results"
DECISIONS_DIR="$PROJECT_ROOT/docs/decisions"
PASS=0
FAIL=0

header() { echo -e "\n=== $1 ==="; }
pass() { echo "  ✅ $1"; ((PASS++)); }
fail() { echo "  ❌ $1"; ((FAIL++)); }

cd "$PROJECT_ROOT"

# AG-1: Surface script exists
header "AG-1: Surface script exists"
if [ -f "$SURFACE" ]; then
    chmod +x "$SURFACE"
    pass "Surface script exists"
else
    fail "Surface script missing"
fi

# AG-2: All 6 commands exist
header "AG-2: All 6 commands exist"
for cmd in decision review status startup list read; do
    if python3 "$SURFACE" "$cmd" --help 2>&1 | grep -q "usage:"; then
        pass "Command '$cmd' exists"
    else
        fail "Command '$cmd' missing"
    fi
done

# AG-3: Review shows qualification summary
header "AG-3: Review shows qualification summary"
output=$(python3 "$SURFACE" review 2>&1)
if echo "$output" | grep -q "qualified targets"; then
    pass "Review shows qualification summary"
else
    fail "Review failed: $output"
fi

# AG-4: Status shows qualification status
header "AG-4: Status shows qualification status"
output=$(python3 "$SURFACE" status 2>&1)
if echo "$output" | grep -q "Coverage"; then
    pass "Status shows coverage"
else
    fail "Status failed: $output"
fi

# AG-5: List shows decisions
header "AG-5: List shows decisions"
output=$(python3 "$SURFACE" list 2>&1)
if echo "$output" | grep -q "Decision ID"; then
    pass "List shows decisions"
else
    fail "List failed: $output"
fi

# AG-6: Read shows decision content
header "AG-6: Read shows decision content"
FIRST_DEC=$(ls "$DECISIONS_DIR"/QUALIFICATION-DECISION-*.json 2>/dev/null | head -1)
if [ -n "$FIRST_DEC" ]; then
    DID=$(basename "$FIRST_DEC" .json)
    output=$(python3 "$SURFACE" read "$DID" 2>&1)
    if echo "$output" | grep -q "Qualification Decision"; then
        pass "Read shows decision content"
    else
        fail "Read failed for $DID"
    fi
else
    fail "No decisions to read"
fi

# AG-7: Decision generation creates JSON
header "AG-7: Decision generation creates JSON"
if [ -f "$DECISIONS_DIR/QUALIFICATION-DECISION-0001.json" ]; then
    if python3 -c "import json; json.load(open('$DECISIONS_DIR/QUALIFICATION-DECISION-0001.json'))" 2>/dev/null; then
        pass "Decision JSON is valid"
    else
        fail "Decision JSON invalid"
    fi
else
    fail "No decision JSON found"
fi

# AG-8: Decision generation creates Markdown
header "AG-8: Decision generation creates Markdown"
if [ -f "$DECISIONS_DIR/QUALIFICATION-DECISION-0001.md" ]; then
    if head -1 "$DECISIONS_DIR/QUALIFICATION-DECISION-0001.md" | grep -q "Qualification Decision"; then
        pass "Decision Markdown is valid"
    else
        fail "Decision Markdown invalid"
    fi
else
    fail "No decision Markdown found"
fi

# AG-9: Decision index is consistent
header "AG-9: Decision index is consistent"
if python3 -c "
import json
with open('$DECISIONS_DIR/decisions-index.json') as f:
    idx = json.load(f)
decs = idx.get('decisions', [])
missing = [d for d in decs if not __import__('os').path.exists('$DECISIONS_DIR/' + d + '.json')]
print('OK' if not missing else f'MISSING: {missing}')
" 2>&1 | grep -q "OK"; then
    pass "Decision index consistent"
else
    fail "Decision index inconsistent"
fi

# AG-10: Startup surface block is well-formed
header "AG-10: Startup surface block is well-formed"
output=$(python3 "$SURFACE" startup --format block 2>&1)
if echo "$output" | grep -q "Qualified targets"; then
    pass "Startup block is well-formed"
else
    fail "Startup block malformed"
fi

# AG-11: Startup surface JSON is valid
header "AG-11: Startup surface JSON is valid"
output=$(python3 "$SURFACE" startup --format json 2>&1)
if echo "$output" | python3 -c "import json,sys; json.load(sys.stdin)" 2>/dev/null; then
    pass "Startup JSON is valid"
else
    fail "Startup JSON invalid"
fi

# AG-12: Review detail mode works
header "AG-12: Review detail mode works"
output=$(python3 "$SURFACE" review --detail 5 2>&1)
if echo "$output" | grep -q "QRX-"; then
    pass "Review detail shows QRX- records"
else
    fail "Review detail failed: $(echo "$output" | tail -3)"
fi

# AG-13: Decision contains advisory disclaimer
header "AG-13: Decision contains advisory disclaimer"
if grep -q "does not authorize" "$DECISIONS_DIR/QUALIFICATION-DECISION-0001.md" 2>/dev/null; then
    pass "Decision contains advisory disclaimer"
else
    fail "Decision missing disclaimer"
fi

# AG-14: Advisory-only posture in decision JSON
header "AG-14: Advisory-only posture in decision JSON"
python3 -c "
import json
with open('$DECISIONS_DIR/QUALIFICATION-DECISION-0001.json') as f:
    d = json.load(f)
ao = d.get('advisory_only') == True
cu = d.get('custody') == 'qa-pilot-local'
li = d.get('librarian_impact') == 'none'
print('OK' if (ao and cu and li) else 'FAIL')
" 2>&1 | grep -q "OK"
if [ $? -eq 0 ]; then
    pass "Decision JSON maintains advisory-only posture"
else
    fail "Decision JSON posture violation"
fi

# AG-15: Decision generates with different decisions (accept/defer/reject/modify)
header "AG-15: Decision supports all 4 decision types"
ALL_OK=true
for dec in accept defer reject modify; do
    python3 "$SURFACE" decision \
        --source QR-F347C0US-0426 \
        --decision "$dec" \
        --rationale "Test $dec decision" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        fail "Decision type '$dec' failed"
        ALL_OK=false
    fi
done
if $ALL_OK; then
    pass "All 4 decision types work"
fi

# Summary
header "Summary"
echo "  Passed: $PASS"
echo "  Failed: $FAIL"
echo "  Total:  $((PASS + FAIL))"
if [ "$FAIL" -eq 0 ]; then
    echo ""
    echo "✅ All review surface acceptance gates pass."
    echo "   Pipeline: results → review → decision → startup surface"
    exit 0
else
    echo ""
    echo "❌ $FAIL gate(s) failed."
    exit 1
fi
