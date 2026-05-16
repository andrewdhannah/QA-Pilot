#!/usr/bin/env bash
# commit-v1rc.sh — Stage and commit current state as v1.0-rc
# Run from anywhere: bash commit-v1rc.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "── QA Pilot — v1.0-rc Commit ───────────────────────────────────────────"

# Rebuild first so dist.html and capstone.html are current
echo "  Rebuilding dist.html..."
cd desktop && node build.js && cd ..
echo ""

# Stage everything
echo "  Staging all changes..."
git add -A

# Show what's being committed
echo ""
echo "  Changes staged:"
git status --short
echo ""

# Commit
git commit -m "v1.0-rc — full Academy + OS audit and bug-fix pass

Academy fixes:
- course.html: countsAs() corruption, SVG path, chaptersS typo, unclosed div
- lesson-4.html: unclosed </div and </body tags
- lesson-5.html: </div} malformed closing tag

Admin backend (lesson-5 wiring — systemic fix):
- admin/dashboard.html: ALL_LESSONS, LESSON_META, TAG_COLORS, calcProgress(),
  buildDetailContent(), .dot-5 CSS all updated to include lesson-5
- admin/assign.html: allLessons, LESSON_META, tagColor, CSS updated for lesson-5
- admin/editor.html: broken viewport meta fixed
- data/content.js: courseMetadata.lessons updated with lesson-5 entry

OS simulator fixes:
- os-core.js: toggleStartMenu() inverted logic fixed — auto-focus now works
- dynamics.html: BUG_FOUND checks (checkStatusViolation, checkDateField)
  now fire on APP_BOOT, not just on change events
- browser.html: os:// route normalization in address bar + buildContentForRoute()
- browser.html: Coffee escaping bug fixed (\\\" → \")
- health-checks.js: EventBus/Compositor variable names corrected
  (window.EventBus → window.QA_OS.EventBus, etc.)

Build pipeline:
- scoring.js confirmed bundled — Submit for Certification fully wired
- All V1 blockers resolved except Training app UI (C12, in progress)

Verified clean: quiz-questions.js, progress.js, assignments.js,
students.js, main.css, dynamics-mock.css, ado-mock.css,
capstone-2.html, certificate.html, bugs.html"

echo ""
echo "── Tag as v1.0-rc ───────────────────────────────────────────────────────"
git tag -a v1.0-rc -m "v1.0-rc — Academy + OS fully audited, one V1 blocker remaining (Training UI)"

echo ""
echo "── Push to GitHub ───────────────────────────────────────────────────────"
echo "  Pushing branch..."
git push

echo "  Pushing tag..."
git push origin v1.0-rc

echo ""
echo "── Done ─────────────────────────────────────────────────────────────────"
echo "  Committed and tagged v1.0-rc"
echo "  Repository: https://github.com/andrewdhannah/QA-Pilot"
echo ""
