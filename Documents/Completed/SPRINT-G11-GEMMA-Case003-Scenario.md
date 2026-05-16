# Sprint G11 — case-003 Scenario: Multi-System Advanced Scenario
## Gemma Build Prompt

Read GEMMA-STYLE-GUIDE.md before writing any code.
**Prerequisites:** SPRINT-C7 merged (scenarios-case-002.js pattern established).
Read `desktop/scenarios/scenarios-case-001.js` and `desktop/scenarios/scenarios-case-002.js`
before writing anything — match the exact data structure.

---

## Context

The QA Pilot platform currently has two training scenarios:
- `case-001` — 2 bugs, beginner, Dynamics + ADO
- `case-002` — 3 bugs, advanced, Dynamics + ADO + Teams

This sprint adds `case-003` — a harder scenario designed for a future `capstone-3.html`
and as an advanced training option. It introduces a fourth bug type (a Browser app clue)
and requires the trainee to cross-reference multiple systems.

The scenario file is pure JavaScript data — no HTML, no UI logic.
Gemma's job is to write the scenario data file and a brief scenario narrative doc.

---

## Scenario Design: case-003

**Title:** CASE-00247 — Invoice Processing Failure
**Company:** Northgate Logistics (same company, different case)
**Trainee role:** Junior QA Analyst
**Delivery:** Teams message from QA Lead (same pattern as case-002)
**Bug count:** 4 bugs
**Pass mark:** 50% (same formula as other scenarios)

### Scenario narrative

```
The QA Lead has assigned you CASE-00247 via Teams.

A finance team member has raised a high-priority support ticket:
"Invoice #INV-8821 for £42,000 cannot be processed — the portal
is returning a permission error."

The case has been logged in Dynamics CRM. Your job is to examine
the case data and identify all defects before the finance team
escalates to the vendor.
```

### The four bugs

| Bug ID | System | Description | AC Reference |
|--------|--------|-------------|--------------|
| `status-junior-closed` | Dynamics CRM | Case Status set to "Closed" — not permitted for Junior role | AC-2.1 |
| `priority-mismatch` | Dynamics CRM | Priority set to "Low" — but the case description says "high-priority" and the linked AC specifies Critical for financial processing failures | AC-3.2 |
| `future-date-allowed` | Dynamics CRM | Created Date set 3 days in the future | AC-1.3 |
| `owner-unassigned` | Dynamics CRM | Case Owner field is blank — all cases must be assigned to a named analyst on creation | AC-1.1 |

### Teams message (from QA Lead)

```
From: Sarah Chen (QA Lead)
To: QA Team

Hi,

Please pick up CASE-00247 — Invoice Processing Failure at Northgate.

Finance have flagged this as urgent. The invoice value is £42,000
and the portal is throwing permission errors.

I've pre-loaded the case in Dynamics. Have a look and file ADO reports
for anything you find wrong with the case data before we escalate.

Key ACs to check: AC-1.1, AC-1.3, AC-2.1, AC-3.2.

Let me know when you've submitted.

— Sarah
```

### AC references for this scenario

```
AC-1.1: All cases must have a named Case Owner on creation. Blank owner is not permitted.
AC-1.3: Created Date must not be in the future.
AC-2.1: Junior analysts may not set Case Status to "Closed" or "Escalated".
AC-3.2: Cases with a description indicating financial impact of £10,000+ must be
         set to Priority: Critical.
```

---

## Deliverable 1: `desktop/scenarios/scenarios-case-003.js`

**Read `scenarios-case-001.js` and `scenarios-case-002.js` before writing.**
Match the exact structure and property names used in those files.

The file should define a scenario entry compatible with `window.SCENARIOS["case-003"]`.

Required top-level properties (match existing scenario structure exactly):
- `id`: `"case-003"`
- `title`: `"CASE-00247 — Invoice Processing Failure"`
- `company`: `"Northgate Logistics"`
- `role`: `"junior"`
- `expectedBugs`: array of the four bug IDs listed above
- `acRefs`: object mapping each bug ID to its AC reference string
- `teamsThread`: the Teams message defined above (same structure as case-002)
- `crmState`: initial Dynamics CRM field values (see below)
- `bugToggles`: which bugs are active (all four: true)
- `trainingMeta`: metadata for the Training app selector

### CRM state (initial field values for Dynamics)

```javascript
crmState: {
  caseId:            "CASE-00247",
  caseTitle:         "Invoice Processing Failure",
  status:            "Closed",          // Bug: Junior can't close cases (AC-2.1)
  priority:          "Low",             // Bug: should be Critical for £42k financial case (AC-3.2)
  createdDate:       "+3d",             // Bug: 3 days in the future (AC-1.3) — use relative date
  owner:             "",                // Bug: blank owner not permitted (AC-1.1)
  description:       "Finance team reports invoice INV-8821 (£42,000) cannot be processed due to a portal permission error. High-priority — finance team has escalated.",
  escalationReason:  "",
  category:          "Financial Processing",
  channel:           "Internal — Finance",
}
```

Note: `"+3d"` is a relative date token — read how `case-002` handles future dates and
use the same pattern. If case-002 uses a computed ISO string instead, do the same here.

### trainingMeta

```javascript
trainingMeta: {
  difficulty: "Expert",
  apps:       "Dynamics + ADO + Teams",
  bugs:       4,
}
```

### trainingSteps (for the Training app step-through)

Define 7 steps for guided walkthrough of this scenario:

```javascript
trainingSteps: [
  {
    title: "Step 1 — Read your Teams briefing",
    body:  "Open the Teams app from the desktop.\nRead the message from Sarah Chen (QA Lead).\nNote the AC references she has flagged: AC-1.1, AC-1.3, AC-2.1, AC-3.2.",
    hint:  "Sarah has given you exactly the ACs to check. Open the AC Panel alongside Dynamics to reference them.",
  },
  {
    title: "Step 2 — Open the AC Panel",
    body:  "Open the Acceptance Criteria app from the desktop.\nFind the rules for AC-1.1, AC-1.3, AC-2.1, and AC-3.2.\nKeep this open as you work through the case.",
    hint:  "Having both the AC Panel and Dynamics open at the same time (using snap layout) is the most efficient approach.",
  },
  {
    title: "Step 3 — Examine the Case Owner field",
    body:  "Open Dynamics CRM from the desktop.\nLook at the Case Owner field.\nIs it filled in?",
    hint:  "AC-1.1: All cases must have a named Case Owner on creation. A blank owner is a defect.",
  },
  {
    title: "Step 4 — Check the Case Status",
    body:  "Look at the Case Status field in Dynamics.\nWhat is the current value?\nIs this permitted for a Junior analyst?",
    hint:  "AC-2.1: Junior analysts may not set Status to Closed or Escalated.",
  },
  {
    title: "Step 5 — Check the Priority",
    body:  "Read the case description carefully.\nNote the invoice value and how the finance team described the urgency.\nNow look at the Priority field — does it match?",
    hint:  "AC-3.2: Cases with financial impact of £10,000+ must be Priority: Critical. The description says £42,000.",
  },
  {
    title: "Step 6 — Check the Created Date",
    body:  "Look at the Created Date field in Dynamics.\nCompare it to today's date.\nCan a case be created in the future?",
    hint:  "AC-1.3: Created Date must not be in the future. This is the same bug type as in Case 001.",
  },
  {
    title: "Step 7 — File your ADO reports",
    body:  "You should have found 4 defects.\nOpen Azure DevOps and file a separate bug report for each one.\nFor each report: clear title, correct severity, AC reference, and steps to reproduce.",
    hint:  "Bug priority/severity mapping: Blank Owner → High, Closed Status → High, Wrong Priority → Medium, Future Date → Medium.",
  },
],
```

---

## Deliverable 2: Register case-003 in `os-core.js`

**Read `desktop/src/os-core.js` before editing.**

Find where `scenarios-case-001.js` and `scenarios-case-002.js` are referenced or where
the SCENARIOS object is assembled. Register `case-003` in the same way.

If scenarios are registered via `window.SCENARIOS` assignments in their own files
(not in os-core.js), then no os-core change is needed — confirm by reading the files.

---

## Deliverable 3: Register in `build.js`

**Read `desktop/build.js` before editing.**

Find where `scenarios-case-001.js` and `scenarios-case-002.js` are bundled.
Add `scenarios-case-003.js` in the same position.

If scenarios are auto-discovered from the `scenarios/` folder, no change is needed —
confirm before editing.

---

## Deliverable 4: `desktop/Documents/Scenario-Case003-Brief.md`

A short internal reference doc (for Andrew / the dev team) describing the scenario design:

```markdown
# Scenario: case-003 — Invoice Processing Failure

## Overview
Expert-level scenario. 4 bugs. Requires cross-referencing Teams briefing + AC Panel + Dynamics.

## Bugs
| Bug ID | Field | Expected | Actual | AC |
|--------|-------|----------|--------|----|
| status-junior-closed | Case Status | not Closed (Junior) | Closed | AC-2.1 |
| priority-mismatch | Priority | Critical (£42k case) | Low | AC-3.2 |
| future-date-allowed | Created Date | today or past | +3 days | AC-1.3 |
| owner-unassigned | Case Owner | named analyst | blank | AC-1.1 |

## Scoring
Max score: 12 pts (4 bugs × 3 pts each)
Pass: 6 pts (50%)

## Intended use
- Advanced training mode (Training app, 7 guided steps)
- capstone-3.html (future sprint)
- case-002 should be completed before attempting case-003
```

---

## What NOT to Change

- Do not modify `scenarios-case-001.js` or `scenarios-case-002.js`
- Do not modify any lesson files or capstone pages
- Do not modify the OS apps (dynamics.html, ado.html, etc.)
- Do not create `capstone-3.html` — that is a future sprint
- Do not add CDN links or external assets

---

## After changes are applied

Update `FEATURE-STATUS.md` in the repo root — add a new row under Scenarios:

| Row | New status |
|-----|-----------|
| case-003 — Invoice Processing Failure (4 bugs) | ✅ |

---

## Definition of Done

- [ ] `desktop/scenarios/scenarios-case-003.js` created with correct structure
- [ ] All four bugs defined in `expectedBugs` and `acRefs`
- [ ] `teamsThread` includes Sarah Chen's message
- [ ] `crmState` sets all four buggy field values
- [ ] `trainingSteps` array has 7 steps with titles, body text, and hints
- [ ] `trainingMeta` defined (Expert, 4 bugs, Dynamics + ADO + Teams)
- [ ] Scenario registered in build pipeline (or confirmed auto-discovered)
- [ ] `desktop/Documents/Scenario-Case003-Brief.md` created
- [ ] `window.SCENARIOS["case-003"]` is accessible at runtime in dist.html
