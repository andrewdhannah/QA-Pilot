#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-training-package-generator.py"
GENERATOR="$SCRIPT_DIR/qa_pilot_training_package_generator.py"
GOV_DOC="$SCRIPT_DIR/../docs/governance/QA-PILOT-TRAINING-PACKAGE-GENERATOR.md"

pass_count=0; fail_count=0
pass() { pass_count=$((pass_count + 1)); echo "  ✅ $1"; }
fail() { fail_count=$((fail_count + 1)); echo "  ❌ $1: $2"; }

echo "=== QA Pilot Training Package Generator — Test Runner ==="

# T1: Generator exists
[ -f "$GENERATOR" ] && pass "T1: Generator found" || fail "T1" "Not found"
# T2: Validator exists
[ -f "$VALIDATOR" ] && pass "T2: Validator found" || fail "T2" "Not found"
# T3: Governance doc exists
[ -f "$GOV_DOC" ] && pass "T3: Governance doc exists" || fail "T3" "Not found"
# T4: Validator PG checks pass
set +e
pg_out=$(python3 "$VALIDATOR" 2>&1)
pg_rc=$?
set -e
[ "$pg_rc" -eq 0 ] && pass "T4: All PG checks pass" || fail "T4" "Validator failed"
# T5: Generator init + list + status + validate cycle
# Test init
set +e
python3 "$GENERATOR" init "TP-TEST-1" "onboarding_guide" --title "Test Guide" --audience "onboarding" >/dev/null 2>&1
rc1=$?
# Test generate
python3 "$GENERATOR" generate "TP-TEST-1" >/dev/null 2>&1
rc2=$?
# Test list
python3 "$GENERATOR" list >/dev/null 2>&1
rc3=$?
# Test status
python3 "$GENERATOR" status >/dev/null 2>&1
rc4=$?
# Test validate
python3 "$GENERATOR" validate "TP-TEST-1" >/dev/null 2>&1
rc5=$?
# Cleanup
python3 "$GENERATOR" init "TP-TEST-2" "validation_exercise" --title "Test Exercise" --audience "all" >/dev/null 2>&1
python3 "$GENERATOR" generate "TP-TEST-2" >/dev/null 2>&1
python3 "$GENERATOR" provenance "TP-TEST-2" "docs/governance/QA-PILOT-PROJECT-GOVERNANCE.md" >/dev/null 2>&1
python3 "$GENERATOR" validate "TP-TEST-2" >/dev/null 2>&1
rc6=$?
# Remove test packages
rm -rf "$SCRIPT_DIR/../data/training-packages/TP-TEST-1" "$SCRIPT_DIR/../data/training-packages/TP-TEST-2" 2>/dev/null
# Also clean up index
python3 -c "import json; f='$SCRIPT_DIR/../data/training-packages/package-index.json'; d=json.load(open(f)); d['packages']=[p for p in d['packages'] if not p['pack_id'].startswith('TP-TEST')]; d['generated_count']=len(d['packages']); json.dump(d,open(f,'w'),indent=2)" 2>/dev/null || true
set -e

all_ok=true
[ "$rc1" -eq 0 ] && pass "T5a: init works" || { fail "T5a" "exit=$rc1"; all_ok=false; }
[ "$rc2" -eq 0 ] && pass "T5b: generate works" || { fail "T5b" "exit=$rc2"; all_ok=false; }
[ "$rc3" -eq 0 ] && pass "T5c: list works" || { fail "T5c" "exit=$rc3"; all_ok=false; }
[ "$rc4" -eq 0 ] && pass "T5d: status works" || { fail "T5d" "exit=$rc4"; all_ok=false; }
[ "$rc5" -eq 1 ] && pass "T5e: validate rejects unsourced package (expected)" || { fail "T5e" "expected exit=1, got $rc5"; all_ok=false; }
[ "$rc6" -eq 0 ] && pass "T5f: provenance+validate works" || { fail "T5f" "exit=$rc6"; all_ok=false; }

# T6: No leak into Librarian
leak=$(find "$SCRIPT_DIR/../active/librarian" -name "*package-generator*" 2>/dev/null | wc -l)
[ "$leak" -eq 0 ] && pass "T6: No Librarian leak" || fail "T6" "Found $leak files"

echo ""
echo "Tests: $((pass_count+fail_count)) total, $pass_count pass, $fail_count fail"
[ "$fail_count" -eq 0 ] && echo "✅ ALL TESTS PASS" || echo "❌ SOME FAILED"
exit $fail_count
