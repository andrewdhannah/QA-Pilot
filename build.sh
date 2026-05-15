#!/usr/bin/env bash
# Run from anywhere — script always finds desktop/build.js relative to itself
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/desktop"
node build.js
