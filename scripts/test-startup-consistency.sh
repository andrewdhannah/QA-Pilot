#!/usr/bin/env bash
# ── QA Pilot Startup Consistency Test Suite ───────────────────────────────
# Tests the validate-qa-pilot-startup-consistency.py validator.
# Uses a bounded workspace skeleton instead of recursive project copies.
# ===========================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-qa-pilot-startup-consistency.py"
RUN_CHECKS="$SCRIPT_DIR/run-startup-checks.sh"

# Temp directory for test output — outside the project tree
TEST_BASE="$(mktemp -d)/qa-pilot-startup-consistency"
trap 'rm -rf "$(dirname "$TEST_BASE")"' EXIT

# ── Workspace skeleton ────────────────────────────────────────────────────
# Builds a minimal project directory with symlinks to only the files
# that run-startup-checks.sh actually needs. Avoids recursive project copies.
create_skeleton() {
  local target="$1"
  rm -rf "$target"
  mkdir -p "$target/scripts" "$target/project-state"

  # Symlink scripts needed by run-startup-checks.sh
  for f in run-startup-checks.sh check-mcp-health.sh; do
    ln -s "$SCRIPT_DIR/$f" "$target/scripts/$f"
  done

  # Symlink all validator scripts (counted by run-startup-checks.sh)
  for f in "$SCRIPT_DIR"/validate-qa-pilot-*.py; do
    ln -s "$f" "$target/scripts/$(basename "$f")"
  done

  # Symlink all test runner scripts (counted by run-startup-checks.sh)
  for f in "$SCRIPT_DIR"/test-qa-pilot-*.sh; do
    ln -s "$f" "$target/scripts/$(basename "$f")"
  done

  # Symlink required project files checked by run-startup-checks.sh
  ln -s "$PROJECT_ROOT/PROJECT-IDENTITY.md"  "$target/PROJECT-IDENTITY.md"
  ln -s "$PROJECT_ROOT/PROJECT-PROFILE.json" "$target/PROJECT-PROFILE.json"
  ln -s "$PROJECT_ROOT/SESSION-HANDOFF.md"   "$target/SESSION-HANDOFF.md"
  ln -s "$PROJECT_ROOT/startup-contract.json" "$target/startup-contract.json"
  ln -s "$PROJECT_ROOT/FEATURE-STATUS.md"    "$target/FEATURE-STATUS.md"
  ln -s "$PROJECT_ROOT/project-state/sprint-ledger.json" "$target/project-state/sprint-ledger.json"
}

# ── Test runner ───────────────────────────────────────────────────────────
# Usage: run_test <test_name> <setup_command> <expected_exit_code>
run_test() {
  local name="$1"
  local setup_cmd="$2"
  local expected_code="$3"

  echo "Running test: $name..."

  local test_run_dir="$TEST_BASE/$name"
  create_skeleton "$test_run_dir"
  cd "$test_run_dir"

  # Run setup (e.g. remove file, mock script)
  eval "$setup_cmd"

  # Run startup checks
  bash "$test_run_dir/scripts/run-startup-checks.sh" > "$test_run_dir/stdout.txt" 2> "$test_run_dir/stderr.txt"
  cat "$test_run_dir/stdout.txt" "$test_run_dir/stderr.txt" > "$test_run_dir/combined_output.txt"

  # Run the validator
  local exit_code=0
  python3 "$VALIDATOR" "$test_run_dir/STARTUP-STATE.md" "$test_run_dir/combined_output.txt" > "$test_run_dir/validator_output.txt" 2>&1 || exit_code=$?

  # Check result
  if [[ $expected_code -eq 0 ]]; then
    if [[ $exit_code -eq 0 ]]; then
      echo "  ✅ PASS"
    else
      echo "  ❌ FAIL (Expected 0, got $exit_code)"
      echo "  Validator output:"
      cat "$test_run_dir/validator_output.txt"
      exit 1
    fi
  else
    if [[ $exit_code -ne 0 ]]; then
      echo "  ✅ PASS"
    else
      echo "  ❌ FAIL (Expected non-zero, got 0)"
      exit 1
    fi
  fi

  cd "$PROJECT_ROOT"
}

# ── Tests ──────────────────────────────────────────────────────────────────

echo "Starting QA Pilot Startup Consistency Test Suite..."
echo "--------------------------------------------------"

# 1. All required files present (Managed)
run_test "all_present" "true" 0

# 2. One required file missing (Blocked)
run_test "one_missing" "rm -f FEATURE-STATUS.md" 0

# 3. Multiple required files missing (Blocked)
run_test "multiple_missing" "rm -f FEATURE-STATUS.md PROJECT-PROFILE.json" 0

# 4. Contradictory emitted state (Manual injection)
run_test "contradictory_state" "
  rm -f FEATURE-STATUS.md
  bash scripts/run-startup-checks.sh > stdout.txt 2> stderr.txt
  cat <<'EOF' > STARTUP-STATE.md
# STARTUP-STATE.md — QA Pilot

**Generated:** 2026-07-05T00:00:00Z

## Current State

- **Project:** QA Pilot
- **Workspace root:** unknown
- **Active project root:** $PROJECT_ROOT
- **Historical root:** unknown
- **Operating mode:** blocked
- **Active work session:** none
- **MCP:** partial
- **Git branch:** main
- **Last commit:** aed58a8
- **Working tree:** dirty
- **Validators:** 14
- **Test runners:** 13
- **Blockers:** 1 required project files missing

## QA Pilot Identity

- **Identity file:** $PROJECT_ROOT/PROJECT-IDENTITY.md
- **Profile file:** $PROJECT_ROOT/PROJECT-PROFILE.json
- **Startup contract:** $PROJECT_ROOT/startup-contract.json
- **Sprint ledger:** $PROJECT_ROOT/project-state/sprint-ledger.json
- **Web app:** false
- **Sandbox boundary:** harness_governed

## Required Files

- ✅ PROJECT-IDENTITY.md
- ✅ PROJECT-PROFILE.json
- ✅ project-state/sprint-ledger.json
- ✅ SESSION-HANDOFF.md
- ✅ FEATURE-STATUS.md  # Manually forced to present (contradiction)
- ✅ startup-contract.json

## Execution Contract (ENV-CONTRACT-1)

- **OS/Version:** Darwin
- **Python version:** Python 3.14.4
- **Startup checks:** $PROJECT_ROOT/scripts/run-startup-checks.sh
- **Validator count:** 14
- **Test runner count:** 13

## Next

- Review SESSION-HANDOFF.md for next concrete task
- Keep startup bounded; do not search the repository unless the task requires it.
- Use project-root handoff at $PROJECT_ROOT/SESSION-HANDOFF.md.

## Do Not Touch Unless Asked

- The Librarian repo (active/librarian/)
- Canonical docs without checkout receipt
- Cross-project mutation paths defined in PROJECT-PROFILE.json

## Required Behavior

- Output the bounded startup report from AGENT-START.md.
- Mark agent work 🔍 Pending; never mark ✅ Verified.
- Use deterministic tools/scripts for exact paths, counts, JSON/YAML, markdown slots, custody, and destructive dry runs.
- This is a Python/script project — no web app checks apply.
EOF
" 0  # Expect validator to exit with non-zero (contradiction detected)

# 5. Degraded MCP state
run_test "degraded_mcp" "
  echo 'echo \"partial (simulated)\"' > scripts/check-mcp-health.sh
  chmod +x scripts/check-mcp-health.sh
" 0

# 6. Blocked startup (MCP unreachable)
run_test "blocked_mcp" "
  echo 'echo \"unreachable\"' > scripts/check-mcp-health.sh
  chmod +x scripts/check-mcp-health.sh
" 0

echo "--------------------------------------------------"
echo "ALL TESTS PASSED!"
echo "Test output: $TEST_BASE"
