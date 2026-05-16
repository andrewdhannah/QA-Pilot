#!/usr/bin/env bash
# cleanup.sh — QA Pilot repo organisation
# Run from the repo root: bash cleanup.sh
# Safe to re-run — moves are skipped if destination already exists.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

# ── Helpers ───────────────────────────────────────────────────────────────────

move() {
  local src="$1"
  local dst="$2"
  if [ ! -e "$ROOT/$src" ]; then
    echo "  SKIP (not found): $src"
    return
  fi
  if [ -e "$ROOT/$dst" ]; then
    echo "  SKIP (already exists at dest): $dst"
    return
  fi
  mv "$ROOT/$src" "$ROOT/$dst"
  echo "  MOVED: $src → $dst"
}

# ── 1. Ensure destination folders exist ───────────────────────────────────────

echo ""
echo "── Creating folders ──────────────────────────────────────────────────────"
mkdir -p "$ROOT/Documents"
mkdir -p "$ROOT/Documents/Archive"
echo "  Documents/ and Documents/Archive/ ready."

# ── 2. Move root-level sprint prompts to Documents/ ───────────────────────────

echo ""
echo "── Moving sprint prompts → Documents/ ───────────────────────────────────"

move "SPRINT-C4-COPILOT-IndexedDB-OS-Bridge.md"         "Documents/SPRINT-C4-COPILOT-IndexedDB-OS-Bridge.md"
move "SPRINT-C5-COPILOT-OS-Visual-Polish.md"             "Documents/SPRINT-C5-COPILOT-OS-Visual-Polish.md"
move "SPRINT-C6-COPILOT-Teams-Shell.md"                  "Documents/SPRINT-C6-COPILOT-Teams-Shell.md"
move "SPRINT-C7-COPILOT-Teams-Scenario-Threads.md"       "Documents/SPRINT-C7-COPILOT-Teams-Scenario-Threads.md"
move "SPRINT-C8-COPILOT-Teams-Sprint-Review.md"          "Documents/SPRINT-C8-COPILOT-Teams-Sprint-Review.md"
move "SPRINT-C9-COPILOT-Enhanced-Apps.md"                "Documents/SPRINT-C9-COPILOT-Enhanced-Apps.md"
move "SPRINT-C10-COPILOT-V1-Critical-Fixes.md"           "Documents/SPRINT-C10-COPILOT-V1-Critical-Fixes.md"
move "SPRINT-C11-COPILOT-Health-Keyboard-Settings.md"    "Documents/SPRINT-C11-COPILOT-Health-Keyboard-Settings.md"
move "SPRINT-G3-GEMMA-Academy-Visual-Refresh.md"         "Documents/SPRINT-G3-GEMMA-Academy-Visual-Refresh.md"
move "SPRINT-G4-GEMMA-Certificate-Redesign.md"           "Documents/SPRINT-G4-GEMMA-Certificate-Redesign.md"
move "SPRINT-G5-GEMMA-Admin-Dashboard-Polish.md"         "Documents/SPRINT-G5-GEMMA-Admin-Dashboard-Polish.md"
move "SPRINT-G6-GEMMA-QOutlook-Easter-Egg.md"            "Documents/SPRINT-G6-GEMMA-QOutlook-Easter-Egg.md"
move "SPRINT-G7-GEMMA-Lesson5-Test-Planning.md"          "Documents/SPRINT-G7-GEMMA-Lesson5-Test-Planning.md"
move "SPRINT-G8-GEMMA-Advanced-Capstone-Page.md"         "Documents/SPRINT-G8-GEMMA-Advanced-Capstone-Page.md"
move "SPRINT-G9-GEMMA-Lesson4-Layout-Fix.md"             "Documents/SPRINT-G9-GEMMA-Lesson4-Layout-Fix.md"

# ── 3. Move backup/copy files to Documents/Archive/ ───────────────────────────

echo ""
echo "── Archiving copy/backup files → Documents/Archive/ ─────────────────────"

move "css/dynamics-mock - Copy.txt"  "Documents/Archive/dynamics-mock - Copy.txt"
move "css/ado-mock - Copy.txt"       "Documents/Archive/ado-mock - Copy.txt"
move "css/main - Copy.txt"           "Documents/Archive/main - Copy.txt"
move "css/main.txt"                  "Documents/Archive/main.txt"
move "css/Stuff dor Github.txt"      "Documents/Archive/Stuff for Github.txt"
move "desktop/apps/dynamics copy"    "Documents/Archive/dynamics-app copy"
move "desktop/src/os-core copy"      "Documents/Archive/os-core copy"

# ── 4. Summary ────────────────────────────────────────────────────────────────

echo ""
echo "── Done ─────────────────────────────────────────────────────────────────"
echo "  Root-level SPRINT-*.md files → Documents/"
echo "  Backup/copy files            → Documents/Archive/"
echo ""
echo "  Files left in root (expected):"
echo "    FEATURE-STATUS.md    — active registry"
echo "    GEMMA-STYLE-GUIDE.md — active reference"
echo "    CHANGELOG.md         — project changelog"
echo "    GITHUB-RELEASE-CHECKLIST.md"
echo "    QA-PILOT-SETUP.md"
echo "    build.sh / build.bat"
echo "    .gitignore"
echo ""
