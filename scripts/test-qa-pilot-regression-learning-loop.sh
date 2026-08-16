#!/usr/bin/env bash
# QA Pilot Regression Learning Loop — Acceptance Test Runner
# QA-PILOT-REGRESSION-LEARNING-LOOP-1
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
LOOP_SCRIPT="$SCRIPT_DIR/qa_pilot_regression_learning_loop.py"
LO_VALIDATOR="$SCRIPT_DIR/validate-learning-object.py"

passed=0
failed=0
total=0

check() {
    local desc="$1"
    shift
    total=$((total + 1))
    if "$@" >/dev/null 2>&1; then
        echo "  ✅ $desc"
        passed=$((passed + 1))
    else
        echo "  ❌ $desc"
        failed=$((failed + 1))
    fi
}

echo "=== AG-1: Loop script exists ==="
check "Loop script exists" test -f "$LOOP_SCRIPT"

echo ""
echo "=== AG-2: All 7 commands exist ==="
for cmd in ingest generate consume feedback receipt validate status; do
    check "Command '$cmd' exists" grep -q "def cmd_${cmd}" "$LOOP_SCRIPT"
done

echo ""
echo "=== AG-3: Ingest produces finding patterns ==="
python3 "$LOOP_SCRIPT" ingest >/dev/null 2>&1
check "Finding patterns directory has files" test -n "$(ls "$REPO_ROOT/data/learning-loop/finding-patterns/" 2>/dev/null)"

echo ""
echo "=== AG-4: Generate produces learning objects ==="
python3 "$LOOP_SCRIPT" generate >/dev/null 2>&1
check "Learning objects generated" test -n "$(ls "$REPO_ROOT/data/learning-loop/learning-objects/" 2>/dev/null)"

echo ""
echo "=== AG-5: Learning objects validate against schema ==="
lo_count=0
lo_pass=0
for lo_file in "$REPO_ROOT/data/learning-loop/learning-objects/"LO-*.json; do
    if [ -f "$lo_file" ]; then
        lo_count=$((lo_count + 1))
        # Validate inline: check schema, advisory_only, no_seal_authority
        if python3 -c "
import json, sys
d = json.load(open('$lo_file'))
assert d.get('schema') == 'learning-object-v1', f'wrong schema: {d.get(\"schema\")}'
assert d.get('advisory_only') == True, 'missing advisory_only'
assert d.get('no_seal_authority') == True, 'missing no_seal_authority'
assert d.get('source', {}).get('evidence_refs'), 'missing evidence_refs'
assert d.get('learning', {}).get('objective'), 'missing learning.objective'
assert d.get('learning', {}).get('explanation'), 'missing learning.explanation'
assert len(d.get('learning', {}).get('explanation', '')) >= 20, 'explanation too short'
" 2>/dev/null; then
            lo_pass=$((lo_pass + 1))
        fi
    fi
done
check "All $lo_count learning objects pass validation ($lo_pass/$lo_count)" test "$lo_pass" -eq "$lo_count"

echo ""
echo "=== AG-6: Consume simulates training ==="
python3 "$LOOP_SCRIPT" consume >/dev/null 2>&1
check "Training completions created" test -n "$(ls "$REPO_ROOT/data/learning-loop/feedback/"TC-*.json 2>/dev/null)"

echo ""
echo "=== AG-7: Feedback produces records ==="
python3 "$LOOP_SCRIPT" feedback >/dev/null 2>&1
check "Feedback records created" test -n "$(ls "$REPO_ROOT/data/learning-loop/feedback/"FB-*.json 2>/dev/null)"

echo ""
echo "=== AG-8: Receipt generates lifecycle receipt ==="
python3 "$LOOP_SCRIPT" receipt >/dev/null 2>&1
check "Lifecycle receipt created" test -n "$(ls "$REPO_ROOT/data/learning-loop/receipts/"LL-*.json 2>/dev/null)"

echo ""
echo "=== AG-9: Validate confirms loop integrity ==="
python3 "$LOOP_SCRIPT" validate >/dev/null 2>&1
check "Loop validation passes" test $? -eq 0

echo ""
echo "=== AG-10: All learning objects maintain advisory-only ==="
advisory_ok=true
for lo_file in "$REPO_ROOT/data/learning-loop/learning-objects/"LO-*.json; do
    if [ -f "$lo_file" ]; then
        if ! python3 -c "import json; d=json.load(open('$lo_file')); assert d.get('advisory_only')==True and d.get('no_seal_authority')==True" 2>/dev/null; then
            advisory_ok=false
            break
        fi
    fi
done
check "All LO-* maintain advisory_only=true, no_seal_authority=true" test "$advisory_ok" = "true"

echo ""
echo "=== AG-11: No QRX-* records were modified ==="
# Check that QRX-* files haven't changed (compare checksums)
qrx_checksum_before=$(find "$REPO_ROOT/data/qualification-results/" -name "QRX-*.json" -exec md5 -q {} \; 2>/dev/null | sort | md5 -q)
python3 "$LOOP_SCRIPT" ingest >/dev/null 2>&1
python3 "$LOOP_SCRIPT" generate >/dev/null 2>&1
qrx_checksum_after=$(find "$REPO_ROOT/data/qualification-results/" -name "QRX-*.json" -exec md5 -q {} \; 2>/dev/null | sort | md5 -q)
check "QRX-* records unchanged after loop operations" test "$qrx_checksum_before" = "$qrx_checksum_after"

echo ""
echo "=== AG-12: Feedback records cannot modify historical results ==="
# Verify FB-* records are advisory-only
fb_ok=true
for fb_file in "$REPO_ROOT/data/learning-loop/feedback/"FB-*.json; do
    if [ -f "$fb_file" ]; then
        if ! python3 -c "import json; d=json.load(open('$fb_file')); assert d.get('advisory_only')==True and d.get('no_seal_authority')==True" 2>/dev/null; then
            fb_ok=false
            break
        fi
    fi
done
check "All FB-* maintain advisory_only=true (no historical modification)" test "$fb_ok" = "true"

echo ""
echo "=== Summary ==="
echo "  Passed: $passed"
echo "  Failed: $failed"
echo "  Total:  $total"
echo ""

if [ "$failed" -eq 0 ]; then
    echo "✅ All regression learning loop acceptance gates pass."
    echo "   Loop: QRX-* → Finding Pattern → Learning Object → Training → Feedback → Receipt"
    exit 0
else
    echo "❌ Some gates failed."
    exit 1
fi
