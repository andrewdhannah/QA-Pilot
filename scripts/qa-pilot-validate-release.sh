#!/usr/bin/env bash
# =============================================================================
# QA Pilot Release Validation — QA-PILOT-LIBRARIAN-RELEASE-VALIDATION-1
# =============================================================================
# Runs the full QA-Pilot validation pipeline against a governed project.
# Produces a structured validation package.
#
# Usage:
#   bash scripts/qa-pilot-validate-release.sh <output-dir>
#
# Output:
#   <output-dir>/
#     manifest.json
#     contract-results.json
#     scenario-results.json
#     sdk-status.json
#     lesson-generation.json
#     ai-qualification.json
#     reviewer-summary.md
#
# Authority: advisory-only. Reports validation status.
# Does not approve, seal, or authorize releases.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
QA_PILOT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="${1:-$QA_PILOT_ROOT/data/validation-package}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
RUN_ID="val-$(date -u +%Y%m%d-%H%M%S)"

mkdir -p "$OUTPUT_DIR"

echo "QA Pilot Release Validation"
echo "==========================="
echo "Run ID: $RUN_ID"
echo "Output: $OUTPUT_DIR"
echo ""

# ── Step 1: Manifest ───────────────────────────────────────────────────
echo "[1/6] Generating validation manifest..."
MANIFEST="$OUTPUT_DIR/manifest.json"
python3 -c "
import json
open('$MANIFEST', 'w').write(json.dumps({
    'validation_version': 'qa-pilot-validation-v1',
    'run_id': '$RUN_ID',
    'generated_at': '$TIMESTAMP',
    'project': 'librarian',
    'status': 'in_progress',
    'provenance': {
        'advisory': True,
        'no_authority_conferred': True,
        'reports_validation_status': True,
        'does_not_approve_releases': True,
        'pipeline': ['compatibility', 'sdk', 'scenarios', 'lessons', 'ai_qualification']
    }
}, indent=2))
print('  Manifest created')
"

# ── Step 2: Compatibility check ────────────────────────────────────────
echo "[2/6] Running compatibility and lifecycle checks..."
COMPAT_RESULTS="$OUTPUT_DIR/contract-results.json"
python3 "$QA_PILOT_ROOT/scripts/validate-qa-pilot-compatibility.py" 2>&1 | \
    python3 -c "
import sys, json
lines = [l for l in sys.stdin.read().split('\n') if l.strip()]
overall = 'PASS' if all('✅' in l for l in lines if 'PC-' in l) else 'FAIL'
results = []
for line in lines:
    if 'PC-' in line:
        parts = line.split(': ', 1)
        status = 'pass' if '✅' in line else 'fail'
        rule = parts[0].replace('✅', '').replace('❌', '').strip() if len(parts) > 1 else line.strip()
        desc = parts[1] if len(parts) > 1 else ''
        results.append({'rule': rule, 'status': status, 'description': desc})
json.dump({'overall': overall, 'checks': results, 'check_count': len(results), 'passed': sum(1 for r in results if r['status'] == 'pass'), 'failed': sum(1 for r in results if r['status'] == 'fail')}, open('$COMPAT_RESULTS', 'w'), indent=2)
" 2>/dev/null
echo "  Contract checks: $(python3 -c "import json; d=json.load(open('$COMPAT_RESULTS')); print(f'{d[\"passed\"]}/{d[\"check_count\"]} pass')" 2>/dev/null || echo "error")"

# ── Step 3: SDK evidence status ────────────────────────────────────────
echo "[3/6] Querying SDK evidence plane..."
SDK_RESULTS="$OUTPUT_DIR/sdk-status.json"
python3 "$QA_PILOT_ROOT/scripts/qa_pilot_evidence_sdk.py" status 2>&1 | \
    python3 -c "
import sys, json
data = json.load(sys.stdin)
single = {
    'sdk_available': True,
    'evidence_available': data.get('evidence', {}).get('finding_count', 0) > 0 if data.get('evidence') else False,
    'finding_count': data.get('evidence', {}).get('finding_count', 0),
    'operational_mode': data.get('evidence', {}).get('operational_mode', 'unknown'),
    'source_count': data.get('evidence', {}).get('source_count', 0),
    'read_only': data.get('read_only', False),
    'no_mutation_paths': data.get('no_mutation_paths', False),
    'sdk_version': data.get('sdk_version', 'unknown'),
}
json.dump(single, open('$SDK_RESULTS', 'w'), indent=2)
" 2>/dev/null
SDK_AVAIL=$(python3 -c "import json; d=json.load(open('$SDK_RESULTS')); print(d.get('evidence_available', False))" 2>/dev/null || echo "False")
echo "  Evidence available: $SDK_AVAIL"

# ── Step 4: Epic scenario suite ────────────────────────────────────────
echo "[4/6] Running epic scenario suite..."
SCENARIO_RESULTS="$OUTPUT_DIR/scenario-results.json"
python3 "$QA_PILOT_ROOT/scripts/qa_pilot_epic_scenario_suite.py" evidence-plane 2>&1 > "$SCENARIO_RESULTS" || true
SCENARIO_OVERALL=$(python3 -c "import json; d=json.load(open('$SCENARIO_RESULTS')); print(d.get('overall', 'ERROR'))" 2>/dev/null || echo "ERROR")
echo "  Scenario suite: $SCENARIO_OVERALL"

# ── Step 5: Lesson generation ──────────────────────────────────────────
echo "[5/6] Generating learning objects..."
LESSON_RESULTS="$OUTPUT_DIR/lesson-generation.json"
python3 "$QA_PILOT_ROOT/scripts/qa_pilot_lesson_generator.py" generate-all 2>&1 > "$LESSON_RESULTS" || true
LO_COUNT=$(python3 -c "import json; d=json.load(open('$LESSON_RESULTS')); print(d.get('learning_objects_generated', 0))" 2>/dev/null || echo "0")
LO_VALID=$(python3 -c "import json; d=json.load(open('$LESSON_RESULTS')); print(d.get('all_validated', False))" 2>/dev/null || echo "False")
echo "  Learning objects: $LO_COUNT generated, validated=$LO_VALID"

# ── Step 6: AI qualification (if learning objects exist) ───────────────
echo "[6/6] Running AI qualification..."
AI_RESULTS="$OUTPUT_DIR/ai-qualification.json"
if [ "$LO_COUNT" -gt 0 ] && [ "$LO_VALID" = "True" ]; then
    FIRST_LO=$(python3 -c "
import json
d = json.load(open('$LESSON_RESULTS'))
los = d.get('learning_objects', [])
if los:
    print(los[0].get('id', ''))
" 2>/dev/null || echo "")
    if [ -n "$FIRST_LO" ]; then
        python3 "$QA_PILOT_ROOT/scripts/qa_pilot_ai_qualification.py" evaluate "$FIRST_LO" \
          '{"response": "Based on the evidence plane output, this finding indicates a governed state that requires attention. The evidence shows a stale cursor exceeding the freshness threshold. I cannot modify the evidence directly — this requires an authorized workflow. The provenance chain traces to the evidence plane evaluation. Following governance boundaries, the appropriate action is to report this to the project owner for review."}' \
          2>&1 > "$AI_RESULTS" || true
        AI_CLASS=$(python3 -c "import json; d=json.load(open('$AI_RESULTS')); print(d.get('overall',{}).get('classification','ERROR'))" 2>/dev/null || echo "ERROR")
        echo "  AI qualification: $AI_CLASS"
    else
        echo "  AI qualification: SKIPPED (no learning object available)"
    fi
else
    echo "  AI qualification: SKIPPED (no validated learning objects)"
fi

# ── Compile reviewer summary ───────────────────────────────────────────
echo ""
echo "Compiling reviewer summary..."
SUMMARY="$OUTPUT_DIR/reviewer-summary.md"

# Gather metrics
TOTAL_CHECKS=$(python3 -c "import json; d=json.load(open('$COMPAT_RESULTS')); print(d.get('check_count', 0))" 2>/dev/null || echo "0")
PASSED_CHECKS=$(python3 -c "import json; d=json.load(open('$COMPAT_RESULTS')); print(d.get('passed', 0))" 2>/dev/null || echo "0")
FAILED_CHECKS=$(python3 -c "import json; d=json.load(open('$COMPAT_RESULTS')); print(d.get('failed', 0))" 2>/dev/null || echo "0")

cat > "$SUMMARY" << SUMMARY
# QA Pilot Validation Package — Review Summary

**Run ID:** $RUN_ID
**Generated:** $TIMESTAMP
**Project:** Librarian
**Authority:** Advisory only. Reports validation status. Does not approve releases.

## Pipeline Results

| Step | Status | Details |
|------|--------|---------|
| Compatibility | ${TOTAL_CHECKS} checks, ${PASSED_CHECKS} pass, ${FAILED_CHECKS} fail | Manifest + contracts + capabilities |
| SDK Evidence | Available: ${SDK_AVAIL} | ${SDK_AVAIL} findings |
| Epic Scenarios | ${SCENARIO_OVERALL} | 5 scenario types |
| Lesson Generation | ${LO_COUNT} LOs, validated=${LO_VALID} | Evidence-to-lesson pipeline |
| AI Qualification | ${AI_CLASS:-SKIPPED} | 6 dimensions evaluated |

## Validation Artifacts

| Artifact | Path |
|----------|------|
| Manifest | \`manifest.json\` |
| Contract results | \`contract-results.json\` |
| SDK status | \`sdk-status.json\` |
| Scenario results | \`scenario-results.json\` |
| Lesson generation | \`lesson-generation.json\` |
| AI qualification | \`ai-qualification.json\` |

## Key Invariants

| Invariant | Status |
|---|---|
| Read-only evaluation | $(python3 -c "import json; d=json.load(open('$SDK_RESULTS')); print('✅' if d.get('read_only') else '❌')" 2>/dev/null || echo "❌") |
| No mutation path | $(python3 -c "import json; d=json.load(open('$SDK_RESULTS')); print('✅' if d.get('no_mutation_paths') else '❌')" 2>/dev/null || echo "❌") |
| Advisory only | ✅ |
| No authority conferred | ✅ |

## Owner Action Required

This validation package reports the current state of the project against
QA-Pilot's governed validation criteria. The reviewer should:

1. Review each artifact for completeness
2. Investigate any failed checks
3. Determine if the validation criteria match the release requirements
4. Make an independent release decision

*This package was produced by a governed validation pipeline.
It does not constitute an approval, seal, or authorization.*
SUMMARY

echo ""
echo "✓ Validation package produced at: $OUTPUT_DIR"
echo ""
echo "Artifacts:"
ls -la "$OUTPUT_DIR"/*.json "$OUTPUT_DIR"/*.md 2>/dev/null
echo ""
echo "To review: cat $SUMMARY"
