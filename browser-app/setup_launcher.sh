#!/bin/bash
# ─────────────────────────────────────────────────────────────
# setup_launcher.sh — one-time QA Pilot launcher setup
# Run this once from the QA Pilot folder:
#   bash setup_launcher.sh
#
# What it does:
#   1. Makes the launcher script executable (required by macOS)
#   2. Installs Pillow if needed, then generates AppIcon.icns
#   3. Removes macOS quarantine flag so the app opens without
#      the "unidentified developer" Gatekeeper warning
#   4. Prints next steps
# ─────────────────────────────────────────────────────────────

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP="$SCRIPT_DIR/QA Pilot.app"
LAUNCHER="$APP/Contents/MacOS/launch"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║     QA Pilot Launcher Setup          ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── Pre-flight: check for Node.js ───────────────────────────
echo "Pre-flight check …"
if command -v node &>/dev/null; then
    NODE_VER="$(node --version)"
    echo "       ✓ Node.js found ($NODE_VER)"
else
    echo ""
    echo "  ⚠️   Node.js not found."
    echo "       The launcher will still work, but 'node build.js' won't"
    echo "       run automatically — dist.html won't be rebuilt on launch."
    echo "       Install Node from https://nodejs.org (LTS recommended)."
    echo ""
fi

# ── Step 1: Make the launcher executable ────────────────────
echo "1 / 4  Making launcher executable …"
chmod +x "$LAUNCHER"
echo "       ✓ Done"

# ── Step 2: Install Pillow if missing ───────────────────────
echo ""
echo "2 / 4  Checking for Pillow (icon generator dependency) …"
if ! python3 -c "import PIL" 2>/dev/null; then
    echo "       Pillow not found — installing …"
    pip3 install pillow --quiet
    echo "       ✓ Pillow installed"
else
    echo "       ✓ Pillow already present"
fi

# ── Step 3: Generate the icon ───────────────────────────────
echo ""
echo "3 / 4  Generating AppIcon.icns …"
python3 "$APP/make_icon.py"

# ── Step 4: Remove quarantine flag ──────────────────────────
# macOS quarantines files downloaded from the internet. Since
# this was created locally the flag may or may not be set, but
# running this is harmless and prevents the Gatekeeper prompt.
echo ""
echo "4 / 4  Clearing Gatekeeper quarantine flag …"
xattr -rd com.apple.quarantine "$APP" 2>/dev/null || true
echo "       ✓ Done"

# ── All done ─────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  ✅  Setup complete!                                 ║"
echo "║                                                      ║"
echo "║  Double-click 'QA Pilot.app' to launch the site.    ║"
echo "║                                                      ║"
echo "║  Tip: drag the .app to your Dock or Desktop for      ║"
echo "║       quick access — it works from anywhere.         ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
