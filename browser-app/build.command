#!/usr/bin/env bash
# macOS click-to-run build — double-click this in Finder to rebuild
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
node build.js
echo ""
echo "────────────────────────────────────"
echo "✅ Build complete. You may close this window."
echo "────────────────────────────────────"
echo ""
# Keep Terminal open so user can see the result
read -p "Press Enter to close..."
