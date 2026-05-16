#!/usr/bin/env bash
# mark-complete.sh — Move completed sprint prompts to Documents/Completed/
# Run from repo root: bash mark-complete.sh

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="$ROOT/Documents"
DST="$ROOT/Documents/Completed"

mkdir -p "$DST"
echo ""
echo "── Moving completed sprints → Documents/Completed/ ──────────────────────"

DONE=(
  "SPRINT-C1-COPILOT-Dynamics-Role-Gating.md"
  "SPRINT-C2-COPILOT-ADO-Save-Validation.md"
  "SPRINT-C3-COPILOT-Dynamics-CRM-State.md"
  "SPRINT-C4-COPILOT-IndexedDB-OS-Bridge.md"
  "SPRINT-C5-COPILOT-OS-Visual-Polish.md"
  "SPRINT-C6-COPILOT-Teams-Shell.md"
  "SPRINT-C7-COPILOT-Teams-Scenario-Threads.md"
  "SPRINT-C8-COPILOT-Teams-Sprint-Review.md"
  "SPRINT-C9-COPILOT-Enhanced-Apps.md"
  "SPRINT-G1-GEMMA-Browser-Cheatsheet.md"
  "SPRINT-G2-GEMMA-Certificate.md"
  "SPRINT-G3-GEMMA-Academy-Visual-Refresh.md"
  "SPRINT-G4-GEMMA-Certificate-Redesign.md"
  "SPRINT-G5-GEMMA-Admin-Dashboard-Polish.md"
  "SPRINT-G6-GEMMA-QOutlook-Easter-Egg.md"
)

for f in "${DONE[@]}"; do
  if [ -f "$SRC/$f" ]; then
    mv "$SRC/$f" "$DST/$f"
    echo "  DONE → Completed/$f"
  elif [ -f "$DST/$f" ]; then
    echo "  SKIP (already in Completed/): $f"
  else
    echo "  SKIP (not found): $f"
  fi
done

echo ""
echo "── Pending (staying in Documents/) ─────────────────────────────────────"
for f in "$SRC"/SPRINT-*.md; do
  [ -f "$f" ] && echo "  PENDING: $(basename "$f")"
done

echo ""
echo "── Done ─────────────────────────────────────────────────────────────────"
