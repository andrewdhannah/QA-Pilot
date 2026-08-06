#!/bin/bash
# QA Pilot Risk-Based Review Depth Test Runner
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CLI="$SCRIPT_DIR/qa_pilot_risk_based_review_depth.py"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-risk-based-review-depth.py"
PASS=0
FAIL=0
TOTAL=0
SKIP=0

report() {
    TOTAL=$((TOTAL + 1))
    if [ "$1" = "pass" ]; then
        PASS=$((PASS + 1))
        echo "  ✅ $2"
    elif [ "$1" = "fail" ]; then
        FAIL=$((FAIL + 1))
        echo "  ❌ $2"
        [ -n "$3" ] && echo "      $3"
    elif [ "$1" = "skip" ]; then
        SKIP=$((SKIP + 1))
        echo "  ⏭️  $2"
    fi
}

cleanup() {
    rm -rf "$PROJECT_ROOT/data/risk-based-review-depths"
}
trap cleanup EXIT

echo "=============================================="
echo " QA Pilot Risk-Based Review Depth Tests"
echo "=============================================="
echo ""

# =========== SCENARIO 1: Low-risk lightweight ===========
echo "--- Scenario 1: Low-risk lightweight change ---"
OUTPUT=$("$CLI" depth-evaluate \
    --eval-id "RD-EVAL-TEST-LOW-001" \
    --result-ref "QR-TEST-001" \
    --lightweight-lane true \
    --rc-failure-count 0 --rc-total-count 11 \
    --e4-failure-count 0 --e4-total-count 10 2>&1) && report "pass" "CLI evaluate: low-risk lightweight" || report "fail" "CLI evaluate: low-risk lightweight" "$OUTPUT"
echo "$OUTPUT" | grep -q "Final depth: none" && report "pass" "Low-risk lightweight → depth=none" || report "fail" "Low-risk lightweight → depth=none" "$OUTPUT"

# =========== SCENARIO 2: Authority change ===========
echo ""
echo "--- Scenario 2: Authority-sensitive change ---"
OUTPUT=$("$CLI" depth-evaluate \
    --eval-id "RD-EVAL-TEST-AUTH-002" \
    --result-ref "QR-TEST-002" \
    --authority-change true \
    --production-path-impact true \
    --rc-failure-count 0 --rc-total-count 11 \
    --e4-failure-count 0 --e4-total-count 10 2>&1) && report "pass" "CLI evaluate: authority change" || report "fail" "CLI evaluate: authority change" "$OUTPUT"
echo "$OUTPUT" | grep -q "Final depth: heavy" && report "pass" "Authority change → depth=heavy" || report "fail" "Authority change → depth=heavy" "$OUTPUT"

# =========== SCENARIO 3: Partial completion ===========
echo ""
echo "--- Scenario 3: Incomplete-plan result ---"
OUTPUT=$("$CLI" depth-evaluate \
    --eval-id "RD-EVAL-TEST-PARTIAL-003" \
    --result-ref "QR-TEST-003" \
    --partial-completion true \
    --incomplete-requirements 3 \
    --rc-failure-count 0 --rc-total-count 11 \
    --e4-failure-count 0 --e4-total-count 10 2>&1) && report "pass" "CLI evaluate: partial completion" || report "fail" "CLI evaluate: partial completion" "$OUTPUT"
echo "$OUTPUT" | grep -q "Final depth: standard" && report "pass" "Partial completion → depth=standard" || report "fail" "Partial completion → depth=standard" "$OUTPUT"

# =========== SCENARIO 4: Failed RC/E4 ===========
echo ""
echo "--- Scenario 4: Failed RC/E4 checks ---"
OUTPUT=$("$CLI" depth-evaluate \
    --eval-id "RD-EVAL-TEST-RCFAIL-004" \
    --result-ref "QR-TEST-004" \
    --lightweight-lane true \
    --rc-failure-count 4 --rc-total-count 11 \
    --e4-failure-count 3 --e4-total-count 10 2>&1) && report "pass" "CLI evaluate: RC/E4 failures" || report "fail" "CLI evaluate: RC/E4 failures" "$OUTPUT"
echo "$OUTPUT" | grep -q "Final depth: standard" && report "pass" "RC/E4 failures → depth=standard (escalated from light)" || report "fail" "RC/E4 failures → depth=standard" "$OUTPUT"

# =========== SCENARIO 5: Authority boundary (advisory-only) ===========
echo ""
echo "--- Scenario 5: Authority boundary enforcement ---"
# Check that CLI produces advisory-only disclaimer
OUTPUT=$("$CLI" depth-evaluate \
    --eval-id "RD-EVAL-TEST-BOUNDARY-005" \
    --result-ref "QR-TEST-005" \
    --authority-change true \
    --rc-failure-count 0 --rc-total-count 11 \
    --e4-failure-count 0 --e4-total-count 10 2>&1) && report "pass" "CLI evaluate: boundary enforcement" || report "fail" "CLI evaluate: boundary enforcement" "$OUTPUT"
echo "$OUTPUT" | grep -q "Advisory-only: True" && report "pass" "Advisory-only flag present" || report "fail" "Advisory-only flag missing" "$OUTPUT"
# Validate the stored record
"$VALIDATOR" --store-scan 2>&1 | tail -5 | grep -q "ALL CHECKS PASS" && report "pass" "Store validation: authority boundary passes" || report "fail" "Store validation: authority boundary" "See validator output"

# =========== SCENARIO 6: Existing validators unaffected ===========
echo ""
echo "--- Scenario 6: Regression check ---"
"$VALIDATOR" --live --fixtures --regression 2>&1 | tail -5 | grep -q "ALL CHECKS PASS" && report "pass" "Validator regression: all checks pass" || report "fail" "Validator regression" "See validator output"

# =========== CLI Commands ===========
echo ""
echo "--- CLI: depth-list ---"
"$CLI" depth-list 2>&1 | grep -q "RD-EVAL-TEST-LOW-001" && report "pass" "CLI depth-list: shows evaluations" || report "fail" "CLI depth-list" "Expected RD-EVAL-TEST-LOW-001 in output"

echo ""
echo "--- CLI: depth-read ---"
"$CLI" depth-read "RD-EVAL-TEST-LOW-001" 2>&1 | grep -q "assigned_depth" && report "pass" "CLI depth-read: returns record" || report "fail" "CLI depth-read" "Expected assigned_depth field"

echo ""
echo "--- CLI: depth-status ---"
"$CLI" depth-status 2>&1 | grep -q "Total evaluations" && report "pass" "CLI depth-status: shows aggregate" || report "fail" "CLI depth-status" "Expected total evaluations"

# =========== Card and Packet Creation ===========
echo ""
echo "--- CLI: card-create ---"
OUTPUT=$("$CLI" card-create "RD-EVAL-TEST-LOW-001" 2>&1) && report "pass" "CLI card-create: created" || report "fail" "CLI card-create" "$OUTPUT"

echo ""
echo "--- CLI: packet-create ---"
OUTPUT=$("$CLI" packet-create "RD-EVAL-TEST-PARTIAL-003" 2>&1) && report "pass" "CLI packet-create: created" || report "fail" "CLI packet-create" "$OUTPUT"

echo ""
echo "--- CLI: packet-heavy-create ---"
OUTPUT=$("$CLI" packet-heavy-create "RD-EVAL-TEST-AUTH-002" 2>&1) && report "pass" "CLI packet-heavy-create: created" || report "fail" "CLI packet-heavy-create" "$OUTPUT"

# =========== Validator Fixtures ===========
echo ""
echo "--- Validator: fixtures ---"
OUTPUT=$("$VALIDATOR" --fixtures 2>&1) && report "pass" "Validator fixtures: all pass" || report "fail" "Validator fixtures" "$OUTPUT"

# =========== Summary ===========
echo ""
echo "=============================================="
echo " Results: $PASS/$TOTAL pass, $FAIL fail, $SKIP skip"
echo "=============================================="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
