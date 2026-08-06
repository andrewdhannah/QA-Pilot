#!/usr/bin/env bash
# QA Pilot Qualification Evidence Pipeline — 15 Acceptance Gates
set +e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PIPELINE="$PROJECT_ROOT/scripts/qa_pilot_qualification_evidence_pipeline.py"
VALIDATOR="$PROJECT_ROOT/scripts/validate-qa-pilot-qualification.py"
STORE_DIR="$PROJECT_ROOT/data/qualification-records"
PASS=0
FAIL=0

header() { echo -e "\n=== $1 ==="; }
pass() { echo "  ✅ $1"; ((PASS++)); }
fail() { echo "  ❌ $1"; ((FAIL++)); }

cd "$PROJECT_ROOT"

# AG-1: Pipeline script exists
header "AG-1: Pipeline script exists"
if [ -f "$PIPELINE" ]; then
    chmod +x "$PIPELINE"
    pass "Pipeline script exists"
else
    fail "Pipeline script missing"
fi

# AG-2: Pipeline has all 6 commands
header "AG-2: Pipeline has all 6 commands"
for cmd in discover collect ingest status validate receipt; do
    if python3 "$PIPELINE" "$cmd" --help 2>&1 | grep -q "usage:"; then
        pass "Command '$cmd' exists"
    else
        fail "Command '$cmd' missing or broken"
    fi
done

# AG-3: Discover shows sources
header "AG-3: Discover shows sources"
output=$(python3 "$PIPELINE" discover 2>&1)
if echo "$output" | grep -q "sources available"; then
    pass "Discover reports available sources"
else
    fail "Discover failed: $output"
fi

# AG-4: Status shows pipeline state
header "AG-4: Status shows pipeline state"
output=$(python3 "$PIPELINE" status 2>&1)
if echo "$output" | grep -q "QR- records"; then
    pass "Status shows QR- records"
else
    fail "Status failed: $output"
fi

# AG-5: Validate reports integrity
header "AG-5: Validate reports integrity"
output=$(python3 "$PIPELINE" validate 2>&1)
if echo "$output" | grep -q "No violations"; then
    pass "Pipeline integrity check passes"
else
    fail "Pipeline integrity check failed: $output"
fi

# AG-6: Ingest validates all records
header "AG-6: Ingest validates all records"
output=$(python3 "$PIPELINE" ingest 2>&1)
passed=$(echo "$output" | grep -c "validated")
failed=$(echo "$output" | grep -c "failed" | head -1)
if [ "$passed" -gt 0 ] && echo "$output" | grep -q "0 failed"; then
    pass "Ingest validates all $passed records"
else
    fail "Ingest validation had failures"
    echo "$output"
fi

# AG-7: Receipt generation works
header "AG-7: Receipt generation works"
output=$(python3 "$PIPELINE" receipt 2>&1)
if echo "$output" | grep -q "receipt written"; then
    pass "Collection receipt generated"
else
    fail "Receipt generation failed: $output"
fi

# AG-8: QR- records in store are valid JSON
header "AG-8: QR- records in store are valid JSON"
BAD=0
COUNT=0
for f in "$STORE_DIR"/QR-*.json; do
    ((COUNT++))
    if ! python3 -c "import json; json.load(open('$f'))" 2>/dev/null; then
        fail "Invalid JSON: $(basename $f)"
        ((BAD++))
    fi
done
if [ "$BAD" -eq 0 ]; then
    pass "All $COUNT QR- records are valid JSON"
fi

# AG-9: Store index is consistent
header "AG-9: Store index is consistent"
INDEX="$STORE_DIR/qualification-index.json"
if [ -f "$INDEX" ]; then
    python3 -c "
import json
with open('$INDEX') as f:
    idx = json.load(f)
records = idx.get('records', [])
missing = [r for r in records if not __import__('os').path.exists('$STORE_DIR/' + r + '.json')]
if missing:
    print('MISSING: ' + str(missing))
else:
    print('OK: ' + str(len(records)) + ' records referenced')
" 2>&1 | while read line; do
        if echo "$line" | grep -q "^OK"; then
            pass "Store index consistent: $line"
        else
            fail "Store index inconsistency: $line"
        fi
    done
else
    fail "Store index missing"
fi

# AG-10: Evidence collection log exists
header "AG-10: Evidence collection log exists"
LOG_DIR="$PROJECT_ROOT/data/qualification-evidence-logs"
if [ -f "$LOG_DIR/collection-log.json" ]; then
    pass "Collection log exists"
else
    fail "Collection log missing"
fi

# AG-11: Collection log has entries
header "AG-11: Collection log has entries"
log_entries=$(python3 -c "import json; f=open('$LOG_DIR/collection-log.json'); d=json.load(f); print(len(d.get('collections',[])))" 2>/dev/null)
if [ "$log_entries" -gt 0 ]; then
    pass "Collection log has $log_entries entries"
else
    fail "Collection log is empty"
fi

# AG-12: No schema modifications
header "AG-12: QR- schema invariants preserved"
SCHEMA="$PROJECT_ROOT/docs/schemas/qa-pilot-qualification-record.schema.json"
python3 -c "
import json
with open('$SCHEMA') as f:
    s = json.load(f)
props = s.get('properties', {})
ao = props.get('advisory_only', {}).get('const')
cu = props.get('custody', {}).get('const')
li = props.get('librarian_impact', {}).get('const')
if ao is True and cu == 'qa-pilot-local' and li == 'none':
    print('OK')
else:
    print(f'CHANGED: advisory_only={ao}, custody={cu}, librarian_impact={li}')
    exit(1)
" 2>&1
if [ $? -eq 0 ]; then
    pass "QR- schema invariants preserved (advisory_only, custody, librarian_impact)"
else
    fail "QR- schema invariants changed"
fi

# AG-13: Each QR- has evidence_refs with provenance
header "AG-13: Each QR- has evidence_refs with provenance"
ALL_OK=true
for f in "$STORE_DIR"/QR-*.json; do
    fn=$(basename "$f")
    result=$(python3 -c "
import json
with open('$f') as fh:
    r = json.load(fh)
refs = r.get('evidence_refs', [])
prov = r.get('provenance', {})
if len(refs) < 1:
    print('NO_REFS')
elif not prov.get('assessor_id'):
    print('NO_PROV')
else:
    has_source = any(ref.get('evidence_source') for ref in refs)
    print('OK' if has_source else 'NO_SOURCE')
" 2>/dev/null)
    if [ "$result" != "OK" ]; then
        fail "$fn: $result"
        ALL_OK=false
    fi
done
if $ALL_OK; then
    pass "All QR- records have evidence_refs with provenance"
fi

# AG-14: Advisory-only posture maintained
header "AG-14: Advisory-only posture maintained"
ADVISORY_OK=true
for f in "$STORE_DIR"/QR-*.json; do
    result=$(python3 -c "
import json
with open('$f') as fh:
    r = json.load(fh)
ao = r.get('advisory_only') == True
cu = r.get('custody') == 'qa-pilot-local'
li = r.get('librarian_impact') == 'none'
print('OK' if (ao and cu and li) else 'FAIL')
" 2>/dev/null)
    if [ "$result" != "OK" ]; then
        fail "$(basename $f): advisory/custody/impact violation"
        ADVISORY_OK=false
    fi
done
if $ADVISORY_OK; then
    pass "All QR- records maintain advisory-only posture"
fi

# AG-15: Provenance linking verified — every source_path exists
header "AG-15: Provenance linking verified"
LINK_OK=true
for f in "$STORE_DIR"/QR-*.json; do
    violations=$(python3 -c "
import json, os
with open('$f') as fh:
    r = json.load(fh)
bad = []
for ref in r.get('evidence_refs', []):
    src = ref.get('evidence_source', '')
    if src and not os.path.exists('$PROJECT_ROOT/' + src):
        bad.append(src)
print('; '.join(bad) if bad else 'OK')
" 2>/dev/null)
    if [ "$violations" != "OK" ]; then
        fail "$(basename $f): missing source: $violations"
        LINK_OK=false
    fi
done
if $LINK_OK; then
    pass "All QR- evidence_refs resolve to existing source files"
fi

# Summary
header "Summary"
echo "  Passed: $PASS"
echo "  Failed: $FAIL"
echo "  Total:  $((PASS + FAIL))"
if [ "$FAIL" -eq 0 ]; then
    echo ""
    echo "✅ All pipeline acceptance gates pass."
    echo "   Evidence pipeline: discover → collect → ingest → validate → receipt"
    exit 0
else
    echo ""
    echo "❌ $FAIL gate(s) failed."
    exit 1
fi
