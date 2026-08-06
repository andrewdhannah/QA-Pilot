#!/bin/bash
# QA Pilot Academy — macOS Launcher
# Opens index.html in the default browser with one double-click.
# Usage: Double-click this file, or run from terminal: bash launch.command

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OPEN_FILE="$SCRIPT_DIR/index.html"

if [ -f "$OPEN_FILE" ]; then
    open "$OPEN_FILE"
    echo "Opening QA Pilot Academy..."
else
    echo "Error: index.html not found in $SCRIPT_DIR"
    echo "Make sure this file is in the QA Pilot Academy folder."
    exit 1
fi
