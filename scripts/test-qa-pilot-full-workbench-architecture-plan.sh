#!/usr/bin/env bash
# ── QA Pilot Full Workbench Architecture Plan Test Runner ─────────────────
# Validates that the planning sprint produces all required docs, schemas,
# sections, and invariants.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PASS=0
FAIL=0

echo "=========================================="
echo " QA-PILOT-FULL-WORKBENCH-ARCHITECTURE-PLAN-1"
echo "=========================================="
echo ""

# ── Step 1: Plan validator ──────────────────────────────────────────────────
echo "=== Group 1: Plan document validation ==="

VALIDATOR="$PROJECT_ROOT/scripts/validate-qa-pilot-full-workbench-architecture-plan.py"

if python3 "$VALIDATOR" 2>&1; then
    echo ""
    echo "  ✅ Plan validator: ALL 12 AP RULES PASS"
    PASS=$((PASS + 1))
else
    echo ""
    echo "  ❌ Plan validator: FAILED"
    FAIL=$((FAIL + 1))
fi

# ── Step 2: External regression ────────────────────────────────────────────
echo ""
echo "=== Group 2: External regression ==="

echo -n "  AG-1: Startup regression green... "
if python3 "$PROJECT_ROOT/scripts/validate-qa-pilot-startup-regression.py" > /dev/null 2>&1; then
    echo "✅"
    PASS=$((PASS + 1))
else
    echo "❌"
    FAIL=$((FAIL + 1))
fi

echo -n "  AG-2: Parity matrix green... "
if python3 "$PROJECT_ROOT/scripts/validate-qa-pilot-startup-parity-matrix.py" > /dev/null 2>&1; then
    echo "✅"
    PASS=$((PASS + 1))
else
    echo "❌"
    FAIL=$((FAIL + 1))
fi

echo -n "  AG-3: Existing validators green... "
existing_pass=0
existing_fail=0
for v in "$PROJECT_ROOT"/scripts/validate-*.py; do
    vname=$(basename "$v")
    case "$vname" in
        validate-qa-pilot-full-workbench-architecture-plan.py|\
        validate-custody-authorization-decision-queue.py|\
        validate-custody-startup-regression-lock.py|\
        validate-qa-pilot-startup-regression.py|\
        validate-qa-pilot-startup-consistency.py)
            continue;;
    esac
    if python3 "$v" > /dev/null 2>&1; then
        existing_pass=$((existing_pass + 1))
    else
        existing_fail=$((existing_fail + 1))
    fi
done
if [ "$existing_fail" -eq 0 ]; then
    echo "✅ ($existing_pass validators pass)"
    PASS=$((PASS + 1))
else
    echo "❌ ($existing_fail validators failing)"
    FAIL=$((FAIL + 1))
fi

echo -n "  AG-4: CRL lock (#30) still green... "
if python3 "$PROJECT_ROOT/scripts/validate-custody-startup-regression-lock.py" live > /dev/null 2>&1; then
    echo "✅"
    PASS=$((PASS + 1))
else
    echo "❌"
    FAIL=$((FAIL + 1))
fi

echo -n "  AG-5: CDQ (#31) fixtures still green... "
if python3 "$PROJECT_ROOT/scripts/validate-custody-authorization-decision-queue.py" fixture > /dev/null 2>&1; then
    echo "✅"
    PASS=$((PASS + 1))
else
    echo "❌"
    FAIL=$((FAIL + 1))
fi

# ── Summary ─────────────────────────────────────────────────────────────────
echo ""
echo "=========================================="
echo " QA-PILOT-FULL-WORKBENCH-ARCHITECTURE-PLAN-1"
echo "=========================================="
echo "  ✅ Passed: $PASS"
echo "  ❌ Failed: $FAIL"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
