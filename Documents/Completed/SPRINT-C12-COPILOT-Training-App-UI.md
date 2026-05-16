# Sprint C-12 — Training App: Scenario Selector + Step-Through UI
## Copilot Prompt — GitHub repo: andrewdhannah/QA-Pilot

You are working in the QA Pilot repository.
No CDN links, no external imports, no fetch(). File:// safe architecture.
Run `node build.js` from the `desktop/` folder after making changes.

**Prerequisites:** SPRINT-C9 must be merged. The SCENARIOS data structure must be current.

---

## Context

`desktop/apps/training.html` currently opens but has no UI — it is a stub.

The Training app serves a different purpose to the Capstone:
- **Capstone** = free exploration, submit when ready, scored on accuracy
- **Training** = guided walkthrough, step-by-step instructions, learning mode

The trainee picks a scenario from a selector, then follows guided steps.
The OS stays live around them — they interact with real apps as instructed.
There is no scoring or submission. Completion is tracked via a simple flag.

---

## Deliverable: `desktop/apps/training.html`

**Read the existing `training.html` before writing anything.**
Match its HTML structure, class naming conventions, and any CSS variables it already uses.
Read `apps/dynamics.html` and `apps/ado.html` to understand the `APP_BOOT` / `ROLE_CHANGE`
postMessage pattern — the Training app receives the same messages.

---

## Phase 1: Scenario Selector

When the Training app opens (before any scenario is active), show a scenario picker panel.

### Layout

```
┌─────────────────────────────────────────────────────────┐
│  Training Mode                                          │
│  Select a scenario to begin guided practice.            │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  📋  Case 001 — Northgate Logistics             │    │
│  │      Beginner · 2 bugs · Dynamics + ADO         │    │
│  │                                        [Start]  │    │
│  └─────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────┐    │
│  │  📋  Case 002 — Customer Portal Login Failure   │    │
│  │      Advanced · 3 bugs · Dynamics + ADO + Teams │    │
│  │                                        [Start]  │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Data source

Read available scenarios from `window.parent.SCENARIOS`. Each entry has an `id` and
`title` field at minimum. For the difficulty badge and app list, read from the scenario's
`trainingMeta` property if present — fall back to the values below if absent:

```javascript
var TRAINING_META_DEFAULTS = {
  "case-001":    { difficulty: "Beginner",  apps: "Dynamics + ADO",               bugs: 2 },
  "case-002":    { difficulty: "Advanced",  apps: "Dynamics + ADO + Teams",        bugs: 3 },
  "capstone-001":{ difficulty: "Beginner",  apps: "Dynamics + ADO",               bugs: 2 },
};
```

Skip any scenario ID that starts with `"bug-"` (those are unit-test scenarios, not training
scenarios). Only show IDs that appear in `TRAINING_META_DEFAULTS` or have a `trainingMeta` key.

### Selector behaviour

- Render one card per eligible scenario on app load
- If `window.parent.SCENARIOS` is undefined or empty, show:
  `"No training scenarios available. Check that the OS loaded correctly."`
- Clicking **Start** on a card calls `beginScenario(scenarioId)`

---

## Phase 2: Step-Through UI

`beginScenario(scenarioId)` hides the selector and shows the step-through panel.

### Layout

```
┌────────────────────────────────────────────────────────────┐
│  [← Back]   Case 001 — Northgate Logistics   Step 2 of 5  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Step 2 — Open Dynamics CRM                               │
│                                                            │
│  Open the Dynamics CRM app from the desktop.               │
│  Look at the Case Status field.                            │
│  Notice that it is set to "Escalated".                     │
│                                                            │
│  💡 Hint: A Junior analyst should not have access          │
│     to change the status to Escalated.                     │
│                                                            │
├────────────────────────────────────────────────────────────┤
│                          [Next Step →]                     │
└────────────────────────────────────────────────────────────┘
```

### Step data

Steps are defined in the scenario's `trainingSteps` array. If `trainingSteps` is absent
from the scenario, use the built-in fallback steps defined below.

Each step object:
```javascript
{
  title:  "Step 2 — Open Dynamics CRM",    // displayed as the step heading
  body:   "Open the Dynamics CRM app...",  // main instruction (supports \n for line breaks)
  hint:   "A Junior analyst should not...", // optional — shown with 💡 prefix, omit if absent
}
```

### Fallback steps for case-001 / capstone-001

```javascript
var FALLBACK_STEPS = {
  "case-001": [
    {
      title: "Step 1 — Read the scenario brief",
      body:  "A new case has been assigned: CASE-00134, Northgate Logistics.\nYour role is Junior QA Analyst.\nYour task is to find any defects in the case data and file ADO bug reports.",
      hint:  "There are 2 bugs hidden in this scenario. Look carefully at field values and permissions.",
    },
    {
      title: "Step 2 — Open Dynamics CRM",
      body:  "Double-click the Dynamics CRM icon on the desktop.\nExamine each field in the case form carefully.",
      hint:  "Pay attention to the Case Status field and the Escalation Reason field.",
    },
    {
      title: "Step 3 — Identify the first bug",
      body:  "Look at the Case Status field.\nIs this value appropriate for a Junior analyst to set?\nCheck the Acceptance Criteria panel (AC) for the rule.",
      hint:  "AC-2.1: Junior analysts may not set Status to Escalated or Closed.",
    },
    {
      title: "Step 4 — File your first ADO bug report",
      body:  "Open Azure DevOps from the desktop.\nFile a bug report for the status violation you found.\nMake sure to: give it a clear title, set a severity, reference the AC (e.g. AC-2.1), and include steps to reproduce.",
      hint:  "A complete report needs all four fields filled — title, severity, AC reference, and steps.",
    },
    {
      title: "Step 5 — Find and file the second bug",
      body:  "Return to Dynamics CRM.\nLook at the Created Date field.\nIs the date value valid for a case that was just opened today?",
      hint:  "A case cannot have a future date. Check the date against today's date.",
    },
    {
      title: "Step 6 — Training complete",
      body:  "You have completed the guided walkthrough for Case 001.\nIn the real Capstone, you would now click Submit to have your work scored.\nFor now, well done — you have practised finding and reporting both bugs.",
      hint:  null,
    },
  ],
};
// Reuse case-001 steps for capstone-001
FALLBACK_STEPS["capstone-001"] = FALLBACK_STEPS["case-001"];
```

### Step-through behaviour

```javascript
var state = {
  scenarioId:   null,
  steps:        [],
  currentStep:  0,
};

function beginScenario(scenarioId) {
  state.scenarioId  = scenarioId;
  var scenario      = window.parent.SCENARIOS && window.parent.SCENARIOS[scenarioId];
  state.steps       = (scenario && scenario.trainingSteps) || FALLBACK_STEPS[scenarioId] || [];
  state.currentStep = 0;

  if (state.steps.length === 0) {
    // No steps available
    showError("No training steps defined for this scenario.");
    return;
  }

  showSelector(false);
  showStepPanel(true);
  renderStep();
}

function renderStep() {
  var step    = state.steps[state.currentStep];
  var total   = state.steps.length;
  var current = state.currentStep + 1;

  // Update: step counter, title, body (replace \n with <br>), hint (show/hide)
  // Update: Back button disabled on step 0
  // Update: Next button text = "Finish" on last step
}

function nextStep() {
  if (state.currentStep < state.steps.length - 1) {
    state.currentStep++;
    renderStep();
  } else {
    finishTraining();
  }
}

function prevStep() {
  if (state.currentStep > 0) {
    state.currentStep--;
    renderStep();
  }
}

function finishTraining() {
  // Write completion flag to localStorage
  try {
    localStorage.setItem("qa-training-complete-" + state.scenarioId, "1");
  } catch(e) {}

  // Show a simple completion message with a "Choose another scenario" button
  showStepPanel(false);
  showComplete(true);
}

function backToSelector() {
  showStepPanel(false);
  showComplete(false);
  showSelector(true);
  state.scenarioId  = null;
  state.currentStep = 0;
}
```

---

## Phase 3: postMessage handling

The Training app receives `APP_BOOT` and `ROLE_CHANGE` from the OS.
On `APP_BOOT`: note the role and scenario data (store but don't auto-start — let trainee choose).
On `ROLE_CHANGE`: update a stored `currentRole` variable (used for future hints if needed).

```javascript
window.addEventListener("message", function(e) {
  if (!e.data || !e.data.type) return;

  if (e.data.type === "APP_BOOT") {
    currentRole = e.data.role || "junior";
    // Do not auto-start — trainee picks from selector
  }

  if (e.data.type === "ROLE_CHANGE") {
    currentRole = e.data.role || currentRole;
  }
});
```

---

## Styling guidelines

- Match the visual language of `dynamics.html` and `ado.html` (CSS variables, font, border radius)
- Scenario cards: subtle border, hover highlight, clear Start button
- Step panel: clear step counter at top right, well-spaced instruction body, hint in a
  lightly shaded block with 💡 prefix
- Completion screen: green accent, encouraging message, "Choose another scenario" CTA
- No CDN, no external fonts — use `var(--qa-font, 'Segoe UI', sans-serif)`

---

## What NOT to Change

- Do not modify any other app files
- Do not modify `os-core.js`, `build.js`, or any lesson files
- Do not add CDN links or external dependencies
- Do not implement scoring — this is learning mode only

---

## After the fix is applied

Update `FEATURE-STATUS.md` in the repo root — change these rows:

| Row | New status |
|-----|-----------|
| Training app — Scenario selector UI | ✅ |
| Training app — Scenario step-through | ✅ |

Also remove "Training app has no UI" from the V1 Release Blockers table.

---

## Definition of Done

- [ ] Training app opens and shows scenario selector
- [ ] Selector reads from `window.parent.SCENARIOS` and shows eligible scenarios
- [ ] Clicking Start on a scenario card begins step-through mode
- [ ] Steps render with title, body, and optional hint
- [ ] Back / Next buttons navigate between steps; Next shows "Finish" on last step
- [ ] Finishing writes `qa-training-complete-{scenarioId}` to localStorage
- [ ] Completion screen shown after Finish; "Choose another scenario" returns to selector
- [ ] Back button (← Back) in step panel returns to selector mid-walkthrough
- [ ] `APP_BOOT` and `ROLE_CHANGE` messages handled
- [ ] No scoring, no submission — training mode only
- [ ] Styling consistent with other app iframes
