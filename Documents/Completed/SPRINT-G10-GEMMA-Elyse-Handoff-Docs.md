# Sprint G10 — Elyse Handoff Documentation
## Gemma Build Prompt

Read GEMMA-STYLE-GUIDE.md before writing any code.
**Prerequisites:** All V1 sprints (C10, C11, G9) merged and built. Training app (C12) merged.

This sprint creates the facilitator and student documentation package for releasing
QA Pilot to Elyse (the first live trainer/admin user).

---

## Context

QA Pilot is a file:// based offline training platform. There is no server, no login system,
no database to set up. Elyse will:
- Open `dist.html` in a browser to run the OS simulator with trainees
- Point trainees to `index.html` to access the Academy (lessons + capstone)
- Review trainee results (written to IndexedDB — readable via the Reports app in the OS)

Elyse's technical comfort level: moderate. She can open files, use a browser, and follow
a checklist — but should not need to touch code or run terminal commands.

---

## Deliverable 1: `docs/FACILITATOR-GUIDE.html`

Create a `docs/` folder in the project root and create `FACILITATOR-GUIDE.html` inside it.
This is a standalone HTML file — no external dependencies, no CDN. Self-contained.

### Content sections

#### 1. Welcome & Overview
Brief intro: what QA Pilot is, what it teaches, who it's for.

```
QA Pilot trains junior QA analysts to:
  • Identify defects in a simulated CRM (Dynamics)
  • File structured bug reports in a simulated ADO tracker
  • Reference acceptance criteria correctly
  • Work within role-appropriate permissions

The platform runs entirely offline in a browser.
No installation, no accounts, no internet connection required.
```

#### 2. What Elyse Does

Two modes:

**Training Mode (guided learning)**
1. Trainee opens `index.html` in their browser
2. Logs in (any name — it's not verified)
3. Completes Lessons 1–5 in order
4. Opens the Training app inside the OS (`dist.html`) to do guided practice

**Assessment Mode (scored capstone)**
1. Trainee completes all lessons first
2. Opens `capstone.html` (beginner) or `capstone-2.html` (advanced, requires Lesson 5)
3. Works through the scenario in the OS simulator
4. Clicks "Submit for Certification"
5. Result is written to the browser's local storage and displayed

#### 3. Reviewing Results

Results are stored in the browser's IndexedDB. To review:
1. Open `dist.html`
2. Open the **Reports** app from the desktop
3. Select a trainee session to see: score, pass/fail, bugs found, bugs missed, report quality

Note: results are stored per-browser-per-device. If the trainee used a different computer
or cleared their browser data, results will not appear.

#### 4. Scenario Overview

| Scenario | Level | Bugs | Used in |
|----------|-------|------|---------|
| case-001 | Beginner | 2 | Capstone (beginner), Training app |
| case-002 | Advanced | 3 | Capstone (advanced) |

Brief description of each scenario's bug set (what the trainee is expected to find):

**case-001:**
- Bug 1: Case Status set to "Escalated" — not permitted for Junior role (AC-2.1)
- Bug 2: Created Date set to a future date — invalid (AC-1.3)

**case-002:**
- Bug 1: Case Status set to "Escalated" — not permitted for Junior role (AC-2.1)
- Bug 2: Escalation Reason field blank when Status is Escalated — required field (AC-2.2)
- Bug 3: Created Date set to a future date — invalid (AC-1.3)

#### 5. Pass Mark

| Scenario | Max score | Pass threshold |
|----------|-----------|----------------|
| case-001 | 6 pts | 3 pts (50%) |
| case-002 | 9 pts | 5 pts (50%) |

Points awarded: 1 pt per bug found in CRM, 1 pt per complete ADO report, 1 pt per correct AC reference.

#### 6. Known Limitations

- Results are stored in the browser only — not synced anywhere
- If trainee clears browser data, results are lost
- The platform is tested in Chrome and Edge; Firefox and Safari may have minor visual differences
- The Training app step-through uses built-in steps — custom scenarios require a developer
- The "Reports" and "Inspector" apps show basic data only (advanced analytics not yet implemented)

#### 7. Troubleshooting

| Issue | Fix |
|-------|-----|
| OS simulator is blank / not loading | Make sure you are opening `dist.html`, not `index.html` |
| Apps won't open when double-clicked | Try a second double-click; if still stuck, refresh the page |
| Score not showing after Submit | Check that the trainee reached the Submit button inside the OS (not the browser back button) |
| Lesson marked incomplete unexpectedly | Each lesson must be completed in order — ensure quiz was submitted before proceeding |
| Two navigation bars stacked on Lesson 4 quiz | Fixed in V1 — if still occurring, ensure the latest build is being used |

#### 8. File Structure Reference

```
index.html           — Academy login + course page
course.html          — Lesson list
lesson-1.html        — Lesson 1: Dynamics CRM intro
lesson-2.html        — Lesson 2: Acceptance Criteria
lesson-3.html        — Lesson 3: Bug filing basics
lesson-4.html        — Lesson 4: Azure DevOps
lesson-5.html        — Lesson 5: Test Planning & Triage
capstone.html        — Beginner capstone (case-001)
capstone-2.html      — Advanced capstone (case-002)
certificate.html     — Result / certificate page
desktop/dist.html    — OS simulator (offline, self-contained)
docs/                — This documentation
```

### Styling

Match the Academy's existing visual language (clean, light, professional).
Use only inline CSS and standard HTML — no external dependencies.
Include a simple print stylesheet so Elyse can print the guide if needed.
Section headings should be clearly delineated. Include a table of contents at the top
with anchor links to each section.

---

## Deliverable 2: `docs/STUDENT-QUICKSTART.html`

A one-page quick reference card for trainees. Designed to be printed or shown on a second monitor.

### Content

```
QA Pilot — Quick Start

Your task:
  1. Open the OS simulator (dist.html)
  2. Read your case brief in the Teams app
  3. Open Dynamics CRM — examine every field for defects
  4. Check the AC Panel for the rules each field must follow
  5. Open Azure DevOps — file a bug report for each defect you find
  6. When confident, click Submit for Certification

A complete bug report needs:
  ✓ Clear title describing the defect
  ✓ Severity set (Critical / High / Medium / Low)
  ✓ AC Reference (e.g. AC-2.1)
  ✓ Steps to reproduce

Scoring:
  1 pt — Bug found in CRM
  1 pt — Complete ADO report filed
  1 pt — Correct AC reference
  Pass = 50%+

Common mistakes:
  ✗ Filing an ADO report without finding the bug in CRM first
  ✗ Leaving the AC Reference blank
  ✗ No steps to reproduce
  ✗ Clicking browser Back instead of using the OS navigation
```

Style as a clean card — white background, clear typography, easy to scan.
Add the QA Pilot name/logo treatment at the top matching the Academy header style.
Keep it to one printed page.

---

## Deliverable 3: `docs/index.html`

A simple docs landing page linking to both documents:

```
QA Pilot Documentation
  → Facilitator Guide      (for trainers and admins)
  → Student Quick Start    (for trainees)
```

Minimal styling — just navigation links, consistent with the Academy look.

---

## What NOT to Change

- Do not modify any Academy pages (lesson-*.html, capstone*.html, etc.)
- Do not modify the OS simulator or any desktop/ files
- Do not add CDN links or external assets to any docs file
- Do not create a README.md (Andrew manages those separately)

---

## Definition of Done

- [ ] `docs/` folder created at project root
- [ ] `docs/FACILITATOR-GUIDE.html` — self-contained, table of contents, all 8 sections
- [ ] `docs/STUDENT-QUICKSTART.html` — one-page printable card
- [ ] `docs/index.html` — landing page linking to both
- [ ] All three files are fully self-contained (no external dependencies)
- [ ] Print stylesheet included in Facilitator Guide
- [ ] Styling consistent with Academy visual language
