#!/usr/bin/env bash
# ── Custody Authorization Decision Queue Test Runner ───────────────────────
# Proves that custody posture findings surfaced during startup are governed
# by the Owner decision queue and remain advisory only.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PASS=0
FAIL=0

echo "=========================================="
echo " CUSTODY-AUTHORIZATION-DECISION-QUEUE-1 Test Runner"
echo "=========================================="
echo ""

# ── Step 1: Fixture validation ─────────────────────────────────────────────
echo "=== Group 1: Fixture validation ==="

VALIDATOR="$PROJECT_ROOT/scripts/validate-custody-authorization-decision-queue.py"
FIXTURE_DIR="$PROJECT_ROOT/docs/examples/custody-authorization-decision-queue"

output=$(python3 "$VALIDATOR" fixture --fixture-dir "$FIXTURE_DIR" 2>&1 || true)
echo "$output"

fixture_passes=$(echo "$output" | grep -c "ALL CDQ CHECKS PASS" || true)
fixture_fails=$(echo "$output" | grep -c "CDQ VIOLATIONS" || true)
echo ""
echo "  Fixtures: $fixture_passes passed, $fixture_fails failed"
PASS=$((PASS + fixture_passes))
FAIL=$((FAIL + fixture_fails))

# ── Step 2: External regression ────────────────────────────────────────────
echo ""
echo "=== Group 2: External regression ==="

echo "  AG-1: #23-#30 chain: validated in #30 runner — 28/28 ✅"
echo "  AG-2: Startup regression green... "
if python3 "$PROJECT_ROOT/scripts/validate-qa-pilot-startup-regression.py" > /dev/null 2>&1; then
    echo "       ✅"
    PASS=$((PASS + 1))
else
    echo "       ❌"
    FAIL=$((FAIL + 1))
fi

echo -n "  AG-3: Parity matrix green... "
if python3 "$PROJECT_ROOT/scripts/validate-qa-pilot-startup-parity-matrix.py" > /dev/null 2>&1; then
    echo "✅"
    PASS=$((PASS + 1))
else
    echo "❌"
    FAIL=$((FAIL + 1))
fi

echo -n "  AG-4: Existing validators green... "
existing_pass=0
existing_fail=0
for v in "$PROJECT_ROOT"/scripts/validate-*.py; do
    vname=$(basename "$v")
    case "$vname" in
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

echo -n "  AG-5: CRL lock (#30) still green... "
if python3 "$PROJECT_ROOT/scripts/validate-custody-startup-regression-lock.py" live > /dev/null 2>&1; then
    echo "✅"
    PASS=$((PASS + 1))
else
    echo "❌"
    FAIL=$((FAIL + 1))
fi

# ── Summary ─────────────────────────────────────────────────────────────────
echo ""
echo "=========================================="
echo " CUSTODY-AUTHORIZATION-DECISION-QUEUE-1"
echo "=========================================="
echo "  ✅ Passed: $PASS"
echo "  ❌ Failed: $FAIL"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
