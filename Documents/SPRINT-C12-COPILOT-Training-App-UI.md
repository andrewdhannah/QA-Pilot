# SPRINT-C12 — COPILOT — Training App: Scenario Selector + Step-Through

**Assigned to:** GitHub Copilot  
**File:** `desktop/apps/training.html`  
**Depends on:** C11 complete ✅ (keyboard-shortcuts.js, health-checks.js bundled)  
**V1 blocker:** YES — last remaining blocker before Elyse handoff  

---

## Context

The Training app (`training.html`) currently renders but has no UI — it's a stub.  
Its purpose is to let a trainee **pick a scenario and step through guided training** before  
attempting the live capstone. It runs inside the OS window manager like any other app.

The OS already exposes `window.parent.QA_OS.loadScenario(id)` and `window.SCENARIOS`  
which contain the full scenario data (crmState, expectedBugs, trainingSteps, etc.).

When `openApp("training")` is called from os-core.js, it currently calls  
`startCapstoneScenario("capstone-001")` — **remove that redirect** and let Training open  
as a normal window instead.

---

## Deliverable

A fully working `training.html` with three phases:

1. **Scenario selector** — list of available training scenarios with title, difficulty, description  
2. **Step-through view** — one step at a time, with Back / Next / Finish controls  
3. **Completion screen** — summary + button to return to selector  

Must work standalone (no server), inside the OS srcdoc iframe chain, and respect  
the Junior/Senior role from APP_BOOT.

---

## Phase 1 — Scenario Selector

```javascript
// On APP_BOOT, load available scenarios from the OS
// Use window.parent.QA_OS.loadScenario(id) — try known IDs
// OR read window.parent.SCENARIOS directly if available

const KNOWN_SCENARIO_IDS = ["case-001", "bug-001"];

// Fallback metadata if scenario data isn't available
const TRAINING_META_DEFAULTS = {
  "case-001": {
    title:       "Case #00247 — Invoice Processing Failure",
    difficulty:  "Beginner",
    description: "Practice investigating a CRM case with a pre-loaded scenario. " +
                 "Identify status violations and date field issues.",
    estimatedMins: 10,
  },
  "bug-001": {
    title:       "Bug Report Practice",
    difficulty:  "Beginner",
    description: "File a bug report in Azure DevOps using provided scenario data.",
    estimatedMins: 8,
  },
};
```

**Selector UI requirements:**
- One card per scenario: title, difficulty badge, description, estimated time, Start button
- If `localStorage.getItem("qa-training-complete-" + id)` is set, show a ✅ Complete badge
- "Reset progress" link clears the localStorage flag and re-renders
- If no scenarios are found (SCENARIOS not loaded), show a friendly message:  
  _"No training scenarios available. Launch from the Capstone lesson to load scenario data."_

---

## Phase 2 — Step-Through View

```javascript
// State object — reset on beginScenario()
var trainingState = {
  scenarioId:  null,
  steps:       [],    // array of { title, body } objects
  currentStep: 0,     // 0-based index
};
```

**Loading steps:**
```javascript
function beginScenario(scenarioId) {
  var OS = window.parent.QA_OS || window.parent.OS || {};
  var scenario = OS.loadScenario ? OS.loadScenario(scenarioId) : null;

  // Use scenario.trainingSteps if present, else use fallback
  var steps = (scenario && Array.isArray(scenario.trainingSteps))
    ? scenario.trainingSteps
    : FALLBACK_STEPS[scenarioId] || FALLBACK_STEPS["case-001"];

  trainingState.scenarioId  = scenarioId;
  trainingState.steps       = steps;
  trainingState.currentStep = 0;
  renderStep();
  showView("step");
}
```

**Fallback steps for case-001** (use these if trainingSteps not in scenario data):
```javascript
const FALLBACK_STEPS = {
  "case-001": [
    {
      title: "Step 1 of 6 — Open the Case",
      body:  "Open Dynamics CRM from the desktop. You should see Case #00247 — " +
             "Invoice Processing Failure pre-loaded. Review the case header: " +
             "Status, Priority, Date Opened, and Owner."
    },
    {
      title: "Step 2 of 6 — Check the Status",
      body:  "As a Junior analyst, you cannot close or resolve cases directly. " +
             "Check the Status field. If it reads 'Closed' or 'Resolved', this is " +
             "a violation — a Junior should have escalated, not closed the case. " +
             "Note this for your bug report."
    },
    {
      title: "Step 3 of 6 — Check the Date",
      body:  "Review the Date Opened field. If the date is in the future, this is " +
             "a data integrity bug — cases cannot be opened before they exist. " +
             "Compare today's date with the field value carefully."
    },
    {
      title: "Step 4 of 6 — Review Acceptance Criteria",
      body:  "Open the AC Panel app. Review the Acceptance Criteria for this case. " +
             "The AC defines what 'done' means. Check each criterion against what " +
             "you see in the CRM form. Any mismatch is a potential bug."
    },
    {
      title: "Step 5 of 6 — File Your Bug Report",
      body:  "Open Azure DevOps. File a bug report for each issue you found. " +
             "Include: a clear title, steps to reproduce, expected vs actual result, " +
             "and the relevant AC reference (e.g. AC-1.3). Use the correct severity."
    },
    {
      title: "Step 6 of 6 — Training Complete",
      body:  "Well done. You have completed the guided training for this scenario. " +
             "When you feel ready, return to the Academy and attempt the live Capstone " +
             "to be assessed and earn your certificate."
    },
  ],
};
```

**Step view UI requirements:**
- Progress indicator: "Step X of Y" + a thin progress bar filling left-to-right
- Step title (h2 style)
- Step body text (paragraph, readable line length ~60ch)
- Back button (disabled on step 0), Next button (disabled on last step)  
- On last step: Next button becomes "Finish Training →"
- Keyboard: Left arrow = Back, Right arrow = Next (only when step view is active)

---

## Phase 3 — Completion Screen

```javascript
function finishTraining() {
  // Mark complete in localStorage so the selector shows ✅
  try {
    localStorage.setItem("qa-training-complete-" + trainingState.scenarioId, "1");
  } catch(e) {}
  showView("complete");
}
```

**Completion screen UI:**
- Checkmark icon (SVG, green)
- Heading: "Training Complete"
- Subtext: "You've finished the guided walkthrough for [scenario title]. " +
           "You're ready to attempt the live Capstone."
- Two buttons: "← Back to Scenarios" (calls backToSelector()) and "Close" (calls window.parent.QA_OS.openApp or just closes — use `window.parent.postMessage({ type: 'CLOSE_SELF' }, '*')`)

---

## Phase 4 — APP_BOOT / ROLE_CHANGE wiring

```javascript
window.addEventListener("message", function(event) {
  var msg = event.data;
  if (!msg || !msg.type) return;

  if (msg.type === "APP_BOOT" && msg.appId === "training") {
    state.role      = msg.role || "junior";
    state.theme     = msg.theme || "light";
    state.sessionId = msg.sessionId || null;
    applyTheme();
    // If a scenarioId was passed (future: scenario launched from capstone),
    // auto-start it. Otherwise show the selector.
    if (msg.scenarioId) {
      beginScenario(msg.scenarioId);
    } else {
      showView("selector");
      renderSelector();
    }
  }

  if (msg.type === "ROLE_CHANGE") {
    state.role = msg.role;
    // Role affects nothing visible in training — no re-render needed
  }
});
```

---

## os-core.js change

Remove the Training redirect in `openApp()`. Change:

```javascript
// BEFORE — redirects Training to capstone (wrong):
if (appId === "training") {
  startCapstoneScenario("capstone-001");
  return;
}
```

```javascript
// AFTER — Training opens as a normal window:
// (just delete the training redirect — it falls through to the normal openApp path)
```

---

## Visual style

Match the existing app aesthetic:
- Background: `var(--qa-surface)` or `#faf9f8` (light) / `#1e1e2e` (dark)
- Font: `Segoe UI, system-ui, sans-serif`, 13px base
- Accent colour for progress bar and badges: `#0078d4` (blue)
- Difficulty badge colours: Beginner = green `#107c10`, Intermediate = orange `#ca5010`
- Card border: `1px solid rgba(0,0,0,0.08)`, border-radius `8px`, subtle box-shadow
- Buttons: match the existing `btn`/`btn-primary` pattern from the Academy CSS

No external assets. No imports. Everything inline in `training.html`.

---

## Definition of Done

- [ ] `training.html` renders a scenario selector with at least case-001 listed
- [ ] Clicking Start enters step-through view with 6 steps for case-001
- [ ] Progress bar and step counter update correctly
- [ ] Back / Next / Finish work; keyboard left/right arrow navigation works
- [ ] Completion screen appears after Finish; localStorage flag is set
- [ ] Returning to selector shows ✅ Complete badge on completed scenarios
- [ ] APP_BOOT message sets role and theme correctly
- [ ] The Training redirect in `openApp()` in `os-core.js` is removed
- [ ] `node build.js` runs without errors after changes
- [ ] `dist.html` opens — Training icon on desktop launches the scenario selector

## After completing this sprint

Run `node build.js` from `desktop/`, verify `dist.html` works end-to-end,  
then update `FEATURE-STATUS.md`:
- Training app scenario selector UI → ✅
- Training app step-through → ✅
- V1 Release Blocker #7 (Training app has no UI) → ✅ Fixed
