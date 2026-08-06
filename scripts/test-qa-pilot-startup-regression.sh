#!/usr/bin/env bash
# ── QA Pilot Startup Regression Test Runner ────────────────────────────────
# Proves the restored QA Pilot startup chain stays managed.
# Runs the regression validator and reports pass/fail for all 15 SR rules.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "QA Pilot Startup Regression Test Runner"
echo "======================================="
echo ""

# ── Step 1: Run regression validator ───────────────────────────────────────
echo "1. Running regression validator..."
VALIDATOR="$PROJECT_ROOT/scripts/validate-qa-pilot-startup-regression.py"

if python3 "$VALIDATOR"; then
  echo ""
  echo "✅ Regression validator: ALL 15 SR RULES PASS"
else
  EXIT_CODE=$?
  echo ""
  echo "❌ Regression validator: FAILED (exit code $EXIT_CODE)"
  exit $EXIT_CODE
fi

echo ""
echo "======================================="
echo "All regression checks pass."
echo "QA Pilot startup chain: locked."
