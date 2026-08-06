#!/usr/bin/env bash
# ── QA Pilot Startup Checks ────────────────────────────────────────────────
# Project-local startup checks for the QA Pilot project.
# Generates STARTUP-STATE.md at the QA Pilot project root.
# This script verifies only QA Pilot-local expectations:
#   - Working tree clean
#   - Project identity and profile files exist
#   - Sprint ledger is readable
#   - Known validators and test runners exist
#   - No Librarian paths required
#   - No web app Public/ checks
#
# Does NOT check: Public/, Swift build, macOS app UI, Librarian-only surfaces.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Resolve workspace root from pointer file
POINTER_FILE="$(cd "$PROJECT_ROOT/../.." 2>/dev/null && pwd)/.librarian/current-project.json"
if [[ ! -f "$POINTER_FILE" ]]; then
  POINTER_FILE="$(cd "$PROJECT_ROOT/.." 2>/dev/null && pwd)/../.librarian/current-project.json"
fi

if [[ -f "$POINTER_FILE" ]]; then
  WORKSPACE_ROOT="$(python3 -c "import json; print(json.load(open('$POINTER_FILE'))['workspace_root'])" 2>/dev/null || echo 'unknown')"
  HISTORICAL_ROOT="$(python3 -c "import json; print(json.load(open('$POINTER_FILE'))['historical_root'])" 2>/dev/null || echo 'unknown')"
else
  WORKSPACE_ROOT="$(cd "$PROJECT_ROOT/../.." && pwd)"
  HISTORICAL_ROOT="$WORKSPACE_ROOT/OpenWork"
fi

: "${WORKSPACE_ROOT:?}" "${PROJECT_ROOT:?}" "${HISTORICAL_ROOT:?}"

STARTUP_STATE_FILE="$PROJECT_ROOT/STARTUP-STATE.md"
SESSION_HANDOFF_FILE="$PROJECT_ROOT/SESSION-HANDOFF.md"
SPRINT_LEDGER_FILE="$PROJECT_ROOT/project-state/sprint-ledger.json"
IDENTITY_FILE="$PROJECT_ROOT/PROJECT-IDENTITY.md"
PROFILE_FILE="$PROJECT_ROOT/PROJECT-PROFILE.json"
CONTRACT_FILE="$PROJECT_ROOT/startup-contract.json"

now_utc() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

# ── MCP health ────────────────────────────────────────────────────────────
check_mcp_health() {
  if [[ -x "$PROJECT_ROOT/scripts/check-mcp-health.sh" ]]; then
    if "$PROJECT_ROOT/scripts/check-mcp-health.sh" >/tmp/qa_pilot_mcp_health.out 2>/tmp/qa_pilot_mcp_health.err; then
      echo "reachable"
    else
      echo "unreachable"
    fi
  else
    # If no QA Pilot-specific MCP check, probe the Librarian MCP health as fallback
    if [[ -x "$WORKSPACE_ROOT/active/librarian/scripts/check-mcp-health.sh" ]]; then
      if "$WORKSPACE_ROOT/active/librarian/scripts/check-mcp-health.sh" >/dev/null 2>/dev/null; then
        echo "reachable (via Librarian)"
      else
        echo "unreachable"
      fi
    else
      echo "partial (no check-mcp-health.sh found)"
    fi
  fi
}

working_tree_status() {
  if [[ ! -d "$PROJECT_ROOT/.git" ]]; then
    echo "unknown"
    return
  fi
  local status
  status=$(cd "$PROJECT_ROOT" && git status --porcelain 2>/dev/null || true)
  if [[ -z "$status" ]]; then
    echo "clean"
  else
    local count
    count=$(echo "$status" | sed '/^$/d' | wc -l | tr -d ' ')
    echo "dirty/$count changed or untracked"
  fi
}

git_field() {
  (cd "$PROJECT_ROOT" && eval "$1") 2>/dev/null || echo "unknown"
}

# ── Check required project files ─────────────────────────────────────────
check_required_files() {
  local missing=0
  local files=(
    "$IDENTITY_FILE"
    "$PROFILE_FILE"
    "$SPRINT_LEDGER_FILE"
    "$SESSION_HANDOFF_FILE"
    "$PROJECT_ROOT/FEATURE-STATUS.md"
    "$CONTRACT_FILE"
  )
  for f in "${files[@]}"; do
    if [[ ! -f "$f" ]]; then
      echo "MISSING: $f" >&2
      missing=$((missing + 1))
    fi
  done
  echo "$missing"
}

# ── Count existing validators ─────────────────────────────────────────────
count_validators() {
  local count=0
  for f in "$PROJECT_ROOT"/scripts/validate-*.py; do
    [[ -f "$f" ]] && count=$((count + 1))
  done
  echo "$count"
}

count_test_runners() {
  local count=0
  for f in "$PROJECT_ROOT"/scripts/test-*.sh; do
    [[ -f "$f" ]] && count=$((count + 1))
  done
  echo "$count"
}

# ── Custody posture ──────────────────────────────────────────────────────
CUSTODY_POSTURE=""
if [[ -f "$PROJECT_ROOT/scripts/custody-surface-startup-integration.py" ]]; then
  CUSTODY_POSTURE=$(python3 "$PROJECT_ROOT/scripts/custody-surface-startup-integration.py" report --format markdown 2>/dev/null || echo "")
fi

# ── Gather state ──────────────────────────────────────────────────────────
required_missing=$(check_required_files)
MCP_STATUS=$(check_mcp_health)

if [[ "$required_missing" -gt 0 ]]; then
  operating_mode="blocked"
elif [[ "$MCP_STATUS" == *"reachable"* ]]; then
  operating_mode="managed"
elif [[ "$MCP_STATUS" == *"partial"* ]]; then
  operating_mode="degraded"
else
  operating_mode="blocked"
fi

active_work_session="none"
branch=$(git_field "git branch --show-current")
last_commit=$(git_field "git log -1 --pretty=format:'%h %s'")
working_tree=$(working_tree_status)
validator_count=$(count_validators)
test_runner_count=$(count_test_runners)

# Read next task from handoff
next_task=""
if [[ -f "$SESSION_HANDOFF_FILE" ]]; then
  next_task=$(awk 'BEGIN{c=0} /^## Next Task/{c=1;next} /^## / && c==1{exit} c==1 && NF>0 {print; exit}' "$SESSION_HANDOFF_FILE" | sed 's/^[[:space:]-]*//')
fi
if [[ -z "$next_task" ]]; then
  next_task="Review SESSION-HANDOFF.md for next concrete task"
fi

blockers=""
if [[ "$required_missing" -gt 0 ]]; then
  blockers="$required_missing required project files missing"
elif [[ "$MCP_STATUS" == "unreachable" ]]; then
  blockers="MCP unreachable"
elif [[ "$MCP_STATUS" == "partial" ]]; then
  blockers="MCP partial"
fi

# ── Write STARTUP-STATE.md ────────────────────────────────────────────────
cat > "$STARTUP_STATE_FILE" <<STATE
# STARTUP-STATE.md — QA Pilot

**Generated:** $(now_utc)

## Current State

- **Project:** QA Pilot
- **Workspace root:** $WORKSPACE_ROOT
- **Active project root:** $PROJECT_ROOT
- **Historical root:** $HISTORICAL_ROOT
- **Operating mode:** $operating_mode
- **Active work session:** $active_work_session
- **MCP:** $MCP_STATUS
- **Git branch:** $branch
- **Last commit:** $last_commit
- **Working tree:** $working_tree
- **Validators:** $validator_count
- **Test runners:** $test_runner_count
- **Blockers:** ${blockers:-none detected}

${CUSTODY_POSTURE:-**Custody surface:** unavailable}

## QA Pilot Identity

- **Identity file:** $IDENTITY_FILE
- **Profile file:** $PROFILE_FILE
- **Startup contract:** $CONTRACT_FILE
- **Sprint ledger:** $SPRINT_LEDGER_FILE
- **Web app:** false (Python/script project)
- **Sandbox boundary:** harness_governed

## Required Files

$(for f in "PROJECT-IDENTITY.md" "PROJECT-PROFILE.json" "project-state/sprint-ledger.json" "SESSION-HANDOFF.md" "FEATURE-STATUS.md" "startup-contract.json"; do
  if [[ -f "$PROJECT_ROOT/$f" ]]; then echo "- ✅ $f"; else echo "- ❌ $f (MISSING)"; fi
done)

## Execution Contract (ENV-CONTRACT-1)

- **OS/Version:** $(uname -a 2>/dev/null | head -1 || echo 'unknown')
- **Python version:** $(python3 --version 2>/dev/null || echo 'unknown')
- **Startup checks:** $SCRIPT_DIR/run-startup-checks.sh
- **Validator count:** $validator_count
- **Test runner count:** $test_runner_count

## Next

- $next_task
- Keep startup bounded; do not search the repository unless the task requires it.
- Use project-root handoff at $SESSION_HANDOFF_FILE.

## Do Not Touch Unless Asked

- The Librarian repo (active/librarian/)
- Canonical docs without checkout receipt
- Cross-project mutation paths defined in PROJECT-PROFILE.json

## Required Behavior

- Output the bounded startup report from AGENT-START.md.
- Mark agent work 🔍 Pending; never mark ✅ Verified.
- Use deterministic tools/scripts for exact paths, counts, JSON/YAML, markdown slots, custody, and destructive dry runs.
- This is a Python/script project — no web app checks apply.
STATE

echo "QA Pilot startup checks complete."
echo "Operating mode: $operating_mode"
echo "Active work session: $active_work_session"
echo "Project root: $PROJECT_ROOT"
echo "MCP: $MCP_STATUS"
echo "Startup file written: $STARTUP_STATE_FILE"
if [[ -n "$blockers" ]]; then
  echo "Blockers: $blockers"
fi
