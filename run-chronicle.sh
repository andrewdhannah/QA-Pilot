#!/usr/bin/env bash
# run-chronicle.sh — Generate QA Pilot Development Chronicle .docx
# Run from anywhere: bash run-chronicle.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT_DIR="$SCRIPT_DIR"
WORK_DIR="$SCRIPT_DIR/.chronicle-tmp"

echo ""
echo "── QA Pilot Development Chronicle ───────────────────────────────────────"

# 1. Set up temp working dir with docx installed
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

echo "  Installing docx library..."
npm install docx --silent 2>/dev/null
echo "  ✓ docx ready"

# 2. Copy the script in (node needs node_modules in same dir)
CHRONICLE_SRC="/Users/andrew/Library/Application Support/Claude/local-agent-mode-sessions/6128d209-a392-492d-b4a4-ea70679be42b/5ba4dac8-409f-47c8-a970-adb50e96ce86/local_deb4e33c-3549-42c0-824e-13b0b6f4efa2/outputs/chronicle.js"

# Patch output path to write to QA Pilot folder
sed "s|/sessions/wizardly-exciting-keller/mnt/outputs|$OUT_DIR|g" "$CHRONICLE_SRC" > chronicle-run.js

echo "  Generating document..."
node chronicle-run.js
echo "  ✓ Done"

# 3. Tidy up
cd "$SCRIPT_DIR"
rm -rf "$WORK_DIR"

echo ""
echo "── Output ───────────────────────────────────────────────────────────────"
echo "  $OUT_DIR/QA-Pilot-Development-Chronicle.docx"
echo ""
