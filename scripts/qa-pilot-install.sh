#!/usr/bin/env bash
# =============================================================================
# QA Pilot Fresh Install Kit — QA-PILOT-FRESH-INSTALL-KIT-1
# =============================================================================
# Installs QA-Pilot contracts, validators, and test runners into a target
# project directory. Packages the governed teaching and qualification pipeline
# into a project-neutral deployment model.
#
# Usage:
#   bash scripts/qa-pilot-install.sh <target-project-dir>
#
# Example:
#   bash scripts/qa-pilot-install.sh /path/to/my-new-project
#
# The target project must already exist.
#
# After install:
#   <target-project-dir>/qa-pilot/
#   ├── contracts/           (schemas — learning-object, scenario, qualification)
#   ├── validators/          (validation scripts — no Librarian dependency)
#   ├── examples/            (sample fixtures)
#   ├── project-adapter.json (configure for your project)
#   └── README.md
#
# Authority: advisory-only. No authority conferred by installation.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
QA_PILOT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ $# -lt 1 ]; then
    echo "Usage: bash scripts/qa-pilot-install.sh <target-project-dir>"
    echo ""
    echo "Installs QA-Pilot contracts into a target project."
    echo "No Librarian paths are embedded in installed artifacts."
    exit 1
fi

TARGET_DIR="$1"

if [ ! -d "$TARGET_DIR" ]; then
    echo "ERROR: Target directory does not exist: $TARGET_DIR"
    exit 1
fi

INSTALL_DIR="$TARGET_DIR/qa-pilot"

echo "QA Pilot Fresh Install Kit"
echo "==========================="
echo "Source: $QA_PILOT_ROOT"
echo "Target: $TARGET_DIR"
echo "Install: $INSTALL_DIR"
echo ""

# ── Step 1: Create directory structure ──────────────────────────────────
echo "[1/5] Creating directory structure..."
mkdir -p "$INSTALL_DIR/contracts"
mkdir -p "$INSTALL_DIR/validators"
mkdir -p "$INSTALL_DIR/examples"
mkdir -p "$INSTALL_DIR/data"
mkdir -p "$INSTALL_DIR/test-library"

# ── Step 2: Copy contracts (schemas — no path dependencies) ────────────
echo "[2/5] Copying contracts..."
cp "$QA_PILOT_ROOT/docs/schemas/learning-object-v1.schema.json" \
   "$INSTALL_DIR/contracts/" 2>/dev/null || echo "  (learning-object schema not found)"
cp "$QA_PILOT_ROOT/docs/schemas/qa-pilot-sdk-integration.schema.json" \
   "$INSTALL_DIR/contracts/" 2>/dev/null || echo "  (sdk schema not found)"
cp "$QA_PILOT_ROOT/docs/schemas/qa-pilot-epic-scenario-suite.schema.json" \
   "$INSTALL_DIR/contracts/" 2>/dev/null || echo "  (scenario suite schema not found)"

ccount=$(ls "$INSTALL_DIR/contracts/" 2>/dev/null | wc -l | tr -d ' ')
echo "  Contracts: $ccount files"

# ── Step 3: Copy validators (standalone — no Librarian dependency) ──────
echo "[3/5] Copying validators..."
# Core validators with zero Librarian path dependencies
# Test library validator
if [ -f "$QA_PILOT_ROOT/scripts/validate-qa-pilot-test-library.py" ]; then
    cp "$QA_PILOT_ROOT/scripts/validate-qa-pilot-test-library.py" "$INSTALL_DIR/validators/"
    echo "  + validate-qa-pilot-test-library.py"
fi

CORE_VALIDATORS=(
    "validate-learning-object.py"
    "validate-qa-pilot-sdk-integration.py"
    "validate-qa-pilot-epic-scenario-suite.py"
)

for v in "${CORE_VALIDATORS[@]}"; do
    if [ -f "$QA_PILOT_ROOT/scripts/$v" ]; then
        cp "$QA_PILOT_ROOT/scripts/$v" "$INSTALL_DIR/validators/"
        echo "  + $v"
    fi
done

vcount=$(ls "$INSTALL_DIR/validators/" 2>/dev/null | wc -l | tr -d ' ')
echo "  Validators: $vcount files"

# ── Step 4: Copy example fixtures ──────────────────────────────────────
echo "[4/5] Copying example fixtures..."
EXAMPLE_DIRS=(
    "learning-object-v1"
    "qa-pilot-sdk-integration"
    "qa-pilot-epic-scenario-suite"
)

for dir in "${EXAMPLE_DIRS[@]}"; do
    src="$QA_PILOT_ROOT/docs/examples/$dir"
    if [ -d "$src" ]; then
mkdir -p "$INSTALL_DIR/examples/$dir"
            cp "$src"/*.json "$INSTALL_DIR/examples/$dir/" 2>/dev/null || true
            fcount=$(ls "$INSTALL_DIR/examples/$dir" 2>/dev/null | wc -l | tr -d ' ')
            echo "  + examples/$dir ($fcount files)"
    fi
done

# ── Step 4b: Copy test library structure ───────────────────────────────
if [ -d "$QA_PILOT_ROOT/test-library" ]; then
    echo "     Copying test library structure..."
    cp -r "$QA_PILOT_ROOT/test-library"/* "$INSTALL_DIR/test-library/" 2>/dev/null || true
    tlcount=$(find "$INSTALL_DIR/test-library" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
    echo "  + test-library ($tlcount test definitions)"
fi

# ── Step 5: Create project adapter ──────────────────────────────────────
echo "[5/5] Creating project adapter..."
cat > "$INSTALL_DIR/project-adapter.json" << ADAPTER
{
  "\$schema": "project-adapter-v1",
  "project_id": "$(basename "$TARGET_DIR")",
  "project_name": "$(basename "$TARGET_DIR")",
  "install_path": "$INSTALL_DIR",
  "installed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "install_version": "qa-pilot-fresh-install-v1",
  "contracts": {
    "learning_object": "contracts/learning-object-v1.schema.json",
    "sdk_integration": "contracts/qa-pilot-sdk-integration.schema.json",
    "epic_scenario_suite": "contracts/qa-pilot-epic-scenario-suite.schema.json"
  },
  "validators": [
    "validators/validate-learning-object.py",
    "validators/validate-qa-pilot-sdk-integration.py",
    "validators/validate-qa-pilot-epic-scenario-suite.py"
  ],
  "adapter": {
    "type": "project_local",
    "evidence_source": "configure_me",
    "governance_boundary": "advisory_only",
    "no_authority_conferred": true
  },
  "provenance": {
    "advisory": true,
    "no_authority_conferred": true,
    "source_package": "QA Pilot",
    "source_version": "fresh-install-v1",
    "librarian_independent": true
  }
}
ADAPTER

echo ""
echo "✓ QA Pilot installed into: $INSTALL_DIR"
echo ""
echo "Next steps:"
echo "  1. Review project-adapter.json and configure evidence_source"
echo "  2. Run: python3 qa-pilot/validators/validate-learning-object.py --list-rules"
echo "  3. Run: python3 qa-pilot/validators/validate-qa-pilot-test-library.py"
echo "  3. Run: python3 qa-pilot/validators/validate-learning-object.py --all"
echo ""
echo "All installed artifacts are project-neutral."
echo "No Librarian paths are embedded."
echo "All validators are advisory-only."
