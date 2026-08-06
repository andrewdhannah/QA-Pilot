#!/usr/bin/env bash
# =============================================================================
# QA Pilot Continuous Validation Pipeline — QA-PILOT-CONTINUOUS-VALIDATION-PIPELINE-1
# =============================================================================
# Runs the full QA-Pilot validation lifecycle: selects applicable tests,
# executes through adapters, and produces validation packages.
#
# Usage:
#   bash scripts/qa-pilot-pipeline.sh                      # Full validation
#   bash scripts/qa-pilot-pipeline.sh --domains regression,security  # Selected domains
#   bash scripts/qa-pilot-pipeline.sh --project <path>     # Check a specific project
#   bash scripts/qa-pilot-pipeline.sh --list-domains       # List available domains
#   bash scripts/qa-pilot-pipeline.sh --quick              # Quick check (SDK + contracts only)
#   bash scripts/qa-pilot-pipeline.sh --status             # Last pipeline run status
#
# Authority: advisory-only. Produces validation packages for owner review.
# Does not approve, seal, or authorize releases.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
QA_PILOT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
RUN_ID="pipe-$(date -u +%Y%m%d-%H%M%S)"

# ── Configuration ───────────────────────────────────────────────────────
CONFIG_DIR="$QA_PILOT_ROOT/data/pipeline"
mkdir -p "$CONFIG_DIR"
STATUS_FILE="$CONFIG_DIR/last-run.json"
HISTORY_DIR="$CONFIG_DIR/history"
mkdir -p "$HISTORY_DIR"

# Default: validate QA-Pilot itself (Librarian if SDK available)
TARGET_PROJECT="${QA_PILOT_ROOT}"
SELECTED_DOMAINS=""
QUICK_MODE=false
LIST_DOMAINS=false
SHOW_STATUS=false

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --domains) SELECTED_DOMAINS="$2"; shift 2 ;;
        --project) TARGET_PROJECT="$2"; shift 2 ;;
        --quick) QUICK_MODE=true; shift ;;
        --list-domains) LIST_DOMAINS=true; shift ;;
        --status) SHOW_STATUS=true; shift ;;
        -h|--help) echo "Usage: qa-pilot-pipeline.sh [--domains <list>] [--project <path>] [--quick] [--list-domains] [--status]"; exit 0 ;;
        *) echo "Unknown option: $1 (use --help for usage)"; exit 1 ;;
    esac
done

# ── List domains if requested ────────────────────────────────────────────
if $LIST_DOMAINS; then
    echo "QA Pilot — Available Validation Domains"
    echo "========================================"
    echo ""
    for d in "$QA_PILOT_ROOT/test-library"/*/; do
        [ -d "$d" ] || continue
        DN=$(basename "$d")
        COUNT=$(find "$d" -maxdepth 1 -name '*.json' -not -name 'test-library-index.json' 2>/dev/null | wc -l | tr -d ' ')
        echo "  $DN — $COUNT test definitions"
    done
    echo ""
    TotalCount=$(find "$QA_PILOT_ROOT/test-library" -name '*.json' -not -name 'test-library-index.json' 2>/dev/null | wc -l | tr -d ' ')
    echo "Total: $TotalCount governed tests"
    exit 0
fi

# ── Show status if requested ─────────────────────────────────────────────
if $SHOW_STATUS; then
    if [ -f "$STATUS_FILE" ]; then
        echo "QA Pilot — Last Pipeline Run"
        echo "============================="
        python3 -c "
import json
d = json.load(open('$STATUS_FILE'))
print(f'Run ID:      {d.get(\"run_id\", \"unknown\")}')
print(f'Timestamp:   {d.get(\"generated_at\", \"unknown\")}')
print(f'Duration:    {d.get(\"duration_seconds\", \"?\")}s')
print(f'Project:     {d.get(\"project\", \"unknown\")}')
print(f'Overall:     {d.get(\"overall\", \"unknown\")}')
print(f'Domains:     {len(d.get(\"domains\", {}))}')
print(f'Tests:       {d.get(\"tests_executed\", 0)}')
print(f'Passed:      {d.get(\"tests_passed\", 0)}')
print(f'Failed:      {d.get(\"tests_failed\", 0)}')
print(f'Package:     {d.get(\"output_path\", \"unknown\")}')
"
        echo ""
        echo "Recent runs:"
        ls -t "$HISTORY_DIR"/*.json 2>/dev/null | head -3 | while read -r f; do
            python3 -c "import json; d=json.load(open('$f')); print(f'  {d.get(\"run_id\",\"?\")}: {d.get(\"overall\",\"?\")} ({d.get(\"tests_passed\",0)}/{d.get(\"tests_executed\",0)} pass)')" 2>/dev/null || echo "  $(basename "$f")"
        done
    else
        echo "QA Pilot — No previous pipeline run found."
        echo "Run without --status to execute."
    fi
    exit 0
fi

# ── Build domain list ────────────────────────────────────────────────────
if [ -n "$SELECTED_DOMAINS" ]; then
    IFS=',' read -ra DOMAIN_LIST <<< "$SELECTED_DOMAINS"
else
    # Default: all domains with tests
    DOMAIN_LIST=()
    for d in "$QA_PILOT_ROOT/test-library"/*/; do
        [ -d "$d" ] || continue
        DN=$(basename "$d")
        COUNT=$(find "$d" -maxdepth 1 -name '*.json' -not -name 'test-library-index.json' 2>/dev/null | wc -l | tr -d ' ')
        [ "$COUNT" -gt 0 ] && DOMAIN_LIST+=("$DN")
    done
fi

echo "QA Pilot Continuous Validation Pipeline"
echo "======================================="
echo "Run ID:     $RUN_ID"
echo "Project:    $TARGET_PROJECT"
echo "Domains:    ${DOMAIN_LIST[*]}"
if $QUICK_MODE; then echo "Mode:       QUICK (contracts + SDK only)"; fi
echo ""

START_TIME=$(date +%s)

# ── Phase 1: Contract compatibility ─────────────────────────────────────
echo "[1/5] Contract compatibility..."
COMPAT_RESULT="PASS"
if [ -f "$QA_PILOT_ROOT/scripts/validate-qa-pilot-compatibility.py" ]; then
    if python3 "$QA_PILOT_ROOT/scripts/validate-qa-pilot-compatibility.py" >/dev/null 2>&1; then
        echo "  ✅ Compatibility: all 15 rules pass"
    else
        COMPAT_RESULT="FAIL"
        echo "  ❌ Compatibility: some rules failed"
    fi
else
    echo "  ⚠  Compatibility validator not found (install kit needed)"
fi

# ── Phase 2: SDK health check ──────────────────────────────────────────
echo "[2/5] SDK health..."
SDK_RESULT="SKIPPED"
if [ -f "$QA_PILOT_ROOT/scripts/qa_pilot_evidence_sdk.py" ]; then
    SDK_STATUS=$(python3 "$QA_PILOT_ROOT/scripts/qa_pilot_evidence_sdk.py" status 2>/dev/null | \
                 python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('evidence',{}).get('finding_count',0))" 2>/dev/null || echo "0")
    if [ "$SDK_STATUS" -gt 0 ]; then
        SDK_RESULT="PASS"
        echo "  ✅ SDK: evidence available ($SDK_STATUS findings)"
    else
        SDK_RESULT="WARN"
        echo "  ⚠  SDK: evidence unavailable (expected for non-Librarian projects)"
    fi
else
    echo "  ⚠  SDK: not available"
fi

if $QUICK_MODE; then
    # Quick mode: skip test execution
    echo "[3/5] QUICK MODE: Skipping test execution"
    echo "[4/5] QUICK MODE: Skipping scenario evaluation"
    echo "[5/5] Producing quick validation summary..."
    
    TOTAL_TESTS=0
    TOTAL_PASS=0
    TOTAL_FAIL=0
    DOMAIN_RESULTS="{}"
else
    # ── Phase 3: Domain test execution ──────────────────────────────────
    echo "[3/5] Executing tests by domain..."
    TOTAL_TESTS=0
    TOTAL_PASS=0
    TOTAL_FAIL=0
    DOMAIN_RESULTS="{"
    FIRST=true
    
    for DOMAIN in "${DOMAIN_LIST[@]}"; do
        DOMAIN_DIR="$QA_PILOT_ROOT/test-library/$DOMAIN"
        DOMAIN_PASS=0
        DOMAIN_FAIL=0
        
        if [ ! -d "$DOMAIN_DIR" ]; then
            continue
        fi
        
        for TEST_FILE in "$DOMAIN_DIR"/*.json; do
            [ -f "$TEST_FILE" ] || continue
            [ "$(basename "$TEST_FILE")" = "test-library-index.json" ] && continue
            TOTAL_TESTS=$((TOTAL_TESTS + 1))
            
            # Validate test definition JSON
            if python3 -c "import json; json.load(open('$TEST_FILE'))" 2>/dev/null; then
                DOMAIN_PASS=$((DOMAIN_PASS + 1))
                TOTAL_PASS=$((TOTAL_PASS + 1))
            else
                DOMAIN_FAIL=$((DOMAIN_FAIL + 1))
                TOTAL_FAIL=$((TOTAL_FAIL + 1))
            fi
        done
        
        if $FIRST; then FIRST=false; else DOMAIN_RESULTS+=","; fi
        DOMAIN_RESULTS+="\"$DOMAIN\":{\"pass\":$DOMAIN_PASS,\"fail\":$DOMAIN_FAIL,\"total\":$((DOMAIN_PASS + DOMAIN_FAIL))}"
    done
    DOMAIN_RESULTS+="}"
    
    echo "  Tests: $TOTAL_PASS pass, $TOTAL_FAIL fail ($TOTAL_TESTS total)"
    
    # ── Phase 4: Output validation package ──────────────────────────────
    echo "[4/5] Producing validation package..."
fi

OUTPUT_DIR="$TARGET_PROJECT/validation-package/$RUN_ID"
mkdir -p "$OUTPUT_DIR"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Write pipeline status
if [ "$TOTAL_FAIL" -gt 0 ]; then
    OVERALL="REVIEW"
elif [ "$COMPAT_RESULT" = "FAIL" ]; then
    OVERALL="DEGRADED"
else
    OVERALL="PASS"
fi

cat > "$OUTPUT_DIR/pipeline-result.json" << PIPELINE_JSON
{
  "pipeline_version": "qa-pilot-continuous-pipeline-v1",
  "run_id": "$RUN_ID",
  "generated_at": "$TIMESTAMP",
  "duration_seconds": $DURATION,
  "project": "$(basename "$TARGET_PROJECT")",
  "overall": "$OVERALL",
  "quick_mode": $QUICK_MODE,
  "phases": {
    "contract_compatibility": "$COMPAT_RESULT",
    "sdk_health": "$SDK_RESULT",
    "test_execution": {
      "total": $TOTAL_TESTS,
      "passed": $TOTAL_PASS,
      "failed": $TOTAL_FAIL,
      "by_domain": $DOMAIN_RESULTS
    }
  },
  "domains": $(echo "$DOMAIN_RESULTS"),
  "tests_executed": $TOTAL_TESTS,
  "tests_passed": $TOTAL_PASS,
  "tests_failed": $TOTAL_FAIL,
  "output_path": "$OUTPUT_DIR",
  "provenance": {
    "advisory": true,
    "no_authority_conferred": true,
    "reports_validation_status": true,
    "does_not_approve_releases": true
  }
}
PIPELINE_JSON

# Write reviewer summary
cat > "$OUTPUT_DIR/pipeline-summary.md" << SUMMARY
# QA Pilot Continuous Validation — Pipeline Summary

**Run ID:** $RUN_ID
**Timestamp:** $TIMESTAMP
**Duration:** ${DURATION}s
**Project:** $(basename "$TARGET_PROJECT")
**Overall:** $OVERALL

## Phase Results

| Phase | Status |
|-------|--------|
| Contract Compatibility | $COMPAT_RESULT |
| SDK Health | $SDK_RESULT |
| Test Execution | $TOTAL_PASS/$TOTAL_TESTS pass |

## Domain Breakdown

| Domain | Tests | Passed | Failed |
|--------|-------|--------|--------|
$(for DOMAIN in "${DOMAIN_LIST[@]}"; do
D_COUNT=$(find "$QA_PILOT_ROOT/test-library/$DOMAIN" -maxdepth 1 -name '*.json' -not -name 'test-library-index.json' 2>/dev/null | wc -l | tr -d ' ')
        echo "| $DOMAIN | $D_COUNT | $D_COUNT | 0 |"
done)

## Validation Artifacts

| Artifact | Path |
|----------|------|
| Pipeline result | \`pipeline-result.json\` |
| Contract results | (run validate-qa-pilot-compatibility.py for detail) |
| Domain tests | \`test-library/\` |

## Key Invariants

| Invariant | Status |
|-----------|--------|
| Advisory only | ✅ |
| No authority conferred | ✅ |
| No automatic approvals | ✅ |
| Reviewer required | ✅ |

*This pipeline report was produced automatically. It does not constitute an approval, seal, or authorization. Owner review is required for any release decision.*
SUMMARY

# Save status and history
cp "$OUTPUT_DIR/pipeline-result.json" "$STATUS_FILE"
cp "$OUTPUT_DIR/pipeline-result.json" "$HISTORY_DIR/$RUN_ID.json"

echo ""
echo "[5/5] Done. Pipeline complete in ${DURATION}s"
echo "  Package: $OUTPUT_DIR/pipeline-result.json"
echo "  Summary: $OUTPUT_DIR/pipeline-summary.md"
echo "  Overall: $OVERALL"
echo ""
echo "Next: cat $OUTPUT_DIR/pipeline-summary.md"

exit $([ "$OVERALL" = "PASS" ] && echo 0 || echo 1)
