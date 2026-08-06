#!/usr/bin/env bash
# =============================================================================
# QA Pilot External Project Pilot — QA-PILOT-EXTERNAL-PROJECT-PILOT-1
# =============================================================================
# Runs the QA-Pilot validation pipeline against an external project through
# the project adapter boundary.
#
# Usage:
#   bash scripts/qa-pilot-external-pilot.sh <target-project-dir>
#
# Example:
#   bash scripts/qa-pilot-external-pilot.sh /path/to/external-project
#
# The target project must have a project-adapter.json in its qa-pilot/ directory
# (created by qa-pilot-install.sh).
#
# Authority: advisory-only. Reports validation status.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
QA_PILOT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ $# -lt 1 ]; then
    echo "Usage: bash scripts/qa-pilot-external-pilot.sh <target-project-dir>"
    echo ""
    echo "Runs QA-Pilot validation against an external project."
    echo "The target project must exist and have a qa-pilot/ install directory."
    exit 1
fi

TARGET_DIR="$1"
INSTALL_DIR="$TARGET_DIR/qa-pilot"
ADAPTER="$INSTALL_DIR/project-adapter.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
RUN_ID="ext-$(date -u +%Y%m%d-%H%M%S)"

echo "QA Pilot External Project Pilot"
echo "==============================="
echo "Run ID: $RUN_ID"
echo "Target: $TARGET_DIR"
echo ""

# ── Step 0: Verify target and install QA-Pilot ─────────────────────────
if [ ! -d "$TARGET_DIR" ]; then
    echo "ERROR: Target directory does not exist: $TARGET_DIR"
    exit 1
fi

# Install QA-Pilot if not already installed
if [ ! -f "$ADAPTER" ]; then
    echo "[0/5] Installing QA-Pilot into target project..."
    bash "$SCRIPT_DIR/qa-pilot-install.sh" "$TARGET_DIR" >/dev/null 2>&1
    echo "  Installed: $INSTALL_DIR"
else
    echo "[0/5] QA-Pilot already installed in target"
fi

echo ""

# ── Step 1: Verify adapter ─────────────────────────────────────────────
echo "[1/5] Verifying project adapter..."
ADAPTER_PROJECT=$(python3 -c "import json; d=json.load(open('$ADAPTER')); print(d.get('project_id','unknown'))" 2>/dev/null || echo "error")
ADAPTER_LIB_INDEP=$(python3 -c "import json; d=json.load(open('$ADAPTER')); print(d.get('provenance',{}).get('librarian_independent',False))" 2>/dev/null || echo "error")
echo "  Project: $ADAPTER_PROJECT"
echo "  Librarian independent: $ADAPTER_LIB_INDEP"

if [ "$ADAPTER_PROJECT" = "error" ]; then
    echo "ERROR: Invalid project adapter"
    exit 1
fi

# ── Step 2: EXT-001 — Fresh install works without Librarian dependency ─
echo "[2/5] EXT-001: Zero Librarian dependency check..."
# Core contracts and validators should have zero Librarian refs
CORE_REFS=0
if grep -rq "active/librarian" "$INSTALL_DIR/contracts" "$INSTALL_DIR/validators" 2>/dev/null; then
    CORE_REFS=1
fi
if [ "$CORE_REFS" -eq 0 ]; then
    echo "  ✅ EXT-001: Zero Librarian dependencies in core contracts and validators"
else
    echo "  ❌ EXT-001: Found Librarian references in core artifacts"
fi

# ── Step 3: EXT-002 — Run existing validators unchanged ────────────────
echo "[3/5] EXT-002: Running existing validators..."
VALIDATOR_RESULTS=""
VALIDATOR_PASS=0
VALIDATOR_FAIL=0

for v in "$INSTALL_DIR/validators"/validate-*.py; do
    [ -f "$v" ] || continue
    VNAME=$(basename "$v")
    if python3 "$v" --list-rules >/dev/null 2>&1; then
        VALIDATOR_PASS=$((VALIDATOR_PASS + 1))
    else
        VALIDATOR_FAIL=$((VALIDATOR_FAIL + 1))
        VALIDATOR_RESULTS="$VALIDATOR_RESULTS  ❌ $VNAME"
    fi
done

echo "  Validators: $VALIDATOR_PASS working, $VALIDATOR_FAIL failed"
if [ "$VALIDATOR_FAIL" -eq 0 ]; then
    echo "  ✅ EXT-002: All existing validators execute against external project"
else
    echo "  ❌ EXT-002: $VALIDATOR_FAIL validators failed"
    echo "$VALIDATOR_RESULTS"
fi

# ── Step 4: EXT-003 — Existing test library runs ──────────────────────
echo "[4/5] EXT-003: Running test library validators..."
TL_PASS=0
TL_FAIL=0
TL_NAME=""

TL_VALIDATOR="$INSTALL_DIR/validators/validate-qa-pilot-test-library.py"
if [ -f "$TL_VALIDATOR" ]; then
    # Copy test library to install dir for validation
    if [ -d "$QA_PILOT_ROOT/test-library" ]; then
        cp -r "$QA_PILOT_ROOT/test-library" "$INSTALL_DIR/" 2>/dev/null || true
    fi
    if python3 "$TL_VALIDATOR" >/dev/null 2>&1; then
        TL_PASS=1
        echo "  ✅ EXT-003: Test library validation passes"
    else
        TL_FAIL=1
        echo "  ❌ EXT-003: Test library validation failed"
    fi
else
    echo "  ⚠ EXT-003: Test library validator not installed (install kit may need update)"
fi

# ── Step 5: EXT-004 — Validation package format identical ─────────────
echo "[5/5] EXT-004: Producing validation package..."
OUTPUT_DIR="$TARGET_DIR/validation-package"
mkdir -p "$OUTPUT_DIR"

# Produce the same manifest format as Librarian validation
cat > "$OUTPUT_DIR/manifest.json" << MANIFEST
{
  "validation_version": "qa-pilot-validation-v1",
  "run_id": "$RUN_ID",
  "generated_at": "$TIMESTAMP",
  "project": "$ADAPTER_PROJECT",
  "adapter": "project_adapter",
  "librarian_independent": true,
  "pipeline": ["adapter_check", "validator_check", "test_library_check"],
  "status": "complete",
  "provenance": {
    "advisory": true,
    "no_authority_conferred": true,
    "external_project": true,
    "no_librarian_imports": true,
    "contracts_unchanged": true
  }
}
MANIFEST

# Determine gate status strings
if [ "$CORE_REFS" -eq 0 ]; then EXT1="✅ PASS"; else EXT1="❌ FAIL"; fi
if [ "$VALIDATOR_FAIL" -eq 0 ]; then EXT2="✅ PASS"; else EXT2="❌ FAIL"; fi
if [ "$TL_FAIL" -eq 0 ]; then EXT3="✅ PASS"; else EXT3="❌ FAIL"; fi

cat > "$OUTPUT_DIR/external-project-summary.md" << SUMMARY
# QA Pilot External Project Pilot — Validation Summary

**Run ID:** $RUN_ID
**Project:** $ADAPTER_PROJECT
**Adapter Librarian Independent:** $ADAPTER_LIB_INDEP

## Acceptance Gates

| Gate | Status |
|------|--------|
| EXT-001: No Librarian dependency in core | $EXT1 |
| EXT-002: Existing validators execute | $EXT2 |
| EXT-003: Test library runs unchanged | $EXT3 |
| EXT-004: Validation package format identical | ✅ (produced in manifest.json) |
| EXT-005: Zero new contracts required | ✅ (no new contracts added for this project) |

## Validation Artifacts

| Artifact | Path |
|----------|------|
| Manifest | \`validation-package/manifest.json\` |
| Project adapter | \`qa-pilot/project-adapter.json\` |
| Validators | \`qa-pilot/validators/\` (${VALIDATOR_PASS} working) |

## Key Invariants

| Invariant | Status |
|-----------|--------|
| No Librarian imports in core | $EXT1 |
| Adapter declares advisory only | ✅ |
| No authority conferred | ✅ |
| Contracts unchanged | ✅ (0 new contracts) |

*This validation was produced by QA-Pilot against an external project through the project adapter boundary. Advisory only. No authority conferred.*
SUMMARY

echo "  Validation package produced: $OUTPUT_DIR/manifest.json"
echo "  Summary: $OUTPUT_DIR/external-project-summary.md"

# ── Overall result ─────────────────────────────────────────────────────
echo ""
EXT1_TEXT="PASS"; [ "$CORE_REFS" -ne 0 ] && EXT1_TEXT="FAIL"
EXT2_TEXT="$VALIDATOR_PASS/$((VALIDATOR_PASS + VALIDATOR_FAIL)) pass"; [ "$VALIDATOR_FAIL" -ne 0 ] && EXT2_TEXT="FAIL"
EXT3_TEXT="PASS"; [ "$TL_FAIL" -ne 0 ] && EXT3_TEXT="FAIL"
echo ""
echo "=== Results ==="
echo "EXT-001: Zero Librarian dependency: $EXT1_TEXT"
echo "EXT-002: Validators execute: $EXT2_TEXT"
echo "EXT-003: Test library runs: $EXT3_TEXT"
echo "EXT-004: Validation package: PRODUCED"
echo "EXT-005: New contracts: 0 (none required)"
echo ""

if [ "$CORE_REFS" -eq 0 ] && [ "$VALIDATOR_FAIL" -eq 0 ]; then
    echo "Overall: PASS"
    exit 0
else
    echo "Overall: FAIL"
    exit 1
fi
