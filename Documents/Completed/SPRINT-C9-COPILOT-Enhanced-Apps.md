# Sprint C-9 — Enhanced ADO + Dynamics for Complex Scenarios
## Copilot Prompt — GitHub repo: andrewdhannah/QA-Pilot

You are working in the QA Pilot repository.
No CDN links, no external imports, no fetch(). File:// safe architecture.
Run `node build.js` from the `desktop/` folder after making changes.

**Prerequisites:** Sprints C-1 (Dynamics Role-Gating) and C-2 (ADO Save + Validation) complete.
This sprint enhances both apps to handle the more complex `case-002` scenario (added in C-7).

---

## Context

The `case-002` scenario (from C-7) has three deliberate bugs the trainee must find:
- **BUG-A** (`status-junior-escalated`): Case Status is "Escalated" but assigned to Junior — AC-2.1
- **BUG-B** (`escalation-reason-blank`): Status is Escalated but Escalation Reason is blank — AC-4.1
- **BUG-C** (`future-date-allowed`): Date Opened is a future date — AC-3.2

Currently Dynamics only checks one of these (future date). ADO doesn't validate AC references
against the active scenario's acceptance criteria. This sprint adds the missing detection and
smarter validation to both apps.

---

## Part 1: Dynamics CRM enhancements (`apps/dynamics.html`)

### 1a — Detect BUG-A: Status = Escalated assigned to Junior

The existing `applyRole("junior")` removes "Escalated" from the Status dropdown.
However, when `populateCaseForm()` loads scenario data with `status: "Escalated"`,
the field is set BEFORE `applyRole()` strips the option — so the illegal value persists silently.

**Fix:** After populating the form and applying the role, check whether the status field
contains a value the current role is not permitted to hold. If so, post `BUG_FOUND`:

```javascript
function checkStatusViolation() {
  var statusEl  = document.getElementById("dyn-status");
  var currentValue = statusEl ? statusEl.value : "";
  var restricted   = ["Closed", "Escalated"];

  if (currentRole === "junior" && restricted.indexOf(currentValue) !== -1) {
    window.parent.postMessage({
      type:  "BUG_FOUND",
      bugId: "status-junior-" + currentValue.toLowerCase(),
    }, "*");

    var OS = window.parent && (window.parent.QA_OS || window.parent.OS);
    if (OS && OS.notify) {
      OS.notify("⚠ Case Status \"" + currentValue + "\" is not permitted for Junior role (AC-2.1).");
    }
  }
}
```

Call `checkStatusViolation()` at the end of `populateCaseForm()`, after the form fields
have been set and after `applyRole()` has run.

### 1b — Detect BUG-B: Escalation Reason blank when Status = Escalated

Add a validation check that fires when the trainee saves or when the form is reviewed.
Also fire it on form load if the scenario data has this state.

```javascript
function checkEscalationReason() {
  var statusEl  = document.getElementById("dyn-status");
  var reasonEl  = document.getElementById("dyn-escalation-reason");
  if (!statusEl || !reasonEl) return;

  var isEscalated = statusEl.value === "Escalated";
  var hasReason   = reasonEl.value && reasonEl.value.trim().length > 0;

  if (isEscalated && !hasReason) {
    window.parent.postMessage({
      type:  "BUG_FOUND",
      bugId: "escalation-reason-blank",
    }, "*");

    var OS = window.parent && (window.parent.QA_OS || window.parent.OS);
    if (OS && OS.notify) {
      OS.notify("⚠ Escalation Reason is required when Status is Escalated (AC-4.1).");
    }

    // Visual indicator: highlight the Escalation Reason field
    if (reasonEl) {
      reasonEl.style.borderColor = "#a4262c";
      reasonEl.setAttribute("title", "Required: Escalation Reason must be filled when Status is Escalated (AC-4.1)");
    }
  }
}
```

Call `checkEscalationReason()` at the end of `populateCaseForm()`, and also wire it to
the Status dropdown `change` event so it fires whenever the trainee changes the status:

```javascript
var statusEl = document.getElementById("dyn-status");
if (statusEl) {
  statusEl.addEventListener("change", function() {
    checkEscalationReason();
    // ... existing change handler code (do not remove it) ...
  });
}
```

### 1c — Future date detection (verify/update existing)

The existing future-date check (from C-1) should already cover BUG-C.
Additionally, trigger the check on form load when `populateCaseForm()` runs,
not only on field change — some scenarios pre-load a future date:

```javascript
function checkDateField() {
  var dateField = document.getElementById("dyn-date-opened");
  if (!dateField || !dateField.value) return;

  var selected = new Date(dateField.value);
  var today    = new Date();
  today.setHours(0, 0, 0, 0);

  if (selected > today) {
    window.parent.postMessage({
      type:  "BUG_FOUND",
      bugId: "future-date-allowed",
    }, "*");

    var OS = window.parent && (window.parent.QA_OS || window.parent.OS);
    if (OS && OS.notify) {
      OS.notify("⚠ Date Opened is a future date — this violates AC-3.2.");
    }
  }
}
```

Call `checkDateField()` at the end of `populateCaseForm()`.
Also ensure the date field's `change` event calls `checkDateField()` (keep the existing wiring).

### 1d — Updated `populateCaseForm()` call sequence

The end of `populateCaseForm()` should now call all three checks in order:

```javascript
// After all fields are populated:
applyRole(currentRole);          // applies role restrictions (existing)
checkStatusViolation();          // BUG-A detection
checkEscalationReason();         // BUG-B detection
checkDateField();                // BUG-C detection
```

---

## Part 2: ADO validation enhancements (`apps/ado.html`)

### 2a — Validate AC reference against the active scenario

Currently `validateForm()` only checks that `acRef` is non-empty.
Enhance it to also warn (not block) if the AC reference format does not match `AC-N` or `AC-N.N`:

```javascript
function validateAcRef(acRef) {
  var pattern = /^AC-\d+(\.\d+)?$/i;
  return pattern.test(acRef.trim());
}
```

In `validateForm()`, add a format warning:

```javascript
// After existing required-field checks:
var acRef = getFieldValue("ado-ac-ref").trim();
if (acRef && !validateAcRef(acRef)) {
  errors.push("AC Reference format should be 'AC-N' or 'AC-N.N' (e.g. AC-2.1).");
}
```

This is a soft validation — it adds a message but uses `errors` the same way as other
required-field errors (blocks save until corrected).

### 2b — Show available ACs from the active scenario

When the ADO app boots (`APP_BOOT`), if a `scenarioId` is provided, look up the scenario's
`acceptanceCriteria` array and display the valid AC IDs as a helper near the AC Reference field.

```javascript
function loadScenarioAcHints(scenarioId) {
  var scenarios = (window.parent && window.parent.SCENARIOS) || window.SCENARIOS || {};
  var scenario  = scenarios[scenarioId];
  if (!scenario || !scenario.acceptanceCriteria) return;

  var hints = scenario.acceptanceCriteria.map(function(ac) {
    return ac.id + ": " + ac.text;
  });

  var hintEl = document.getElementById("ado-ac-hints");
  if (!hintEl) return;

  hintEl.innerHTML = "<strong>Available ACs for this scenario:</strong><ul>" +
    hints.map(function(h) { return "<li>" + escapeHtml(h) + "</li>"; }).join("") +
    "</ul>";
  hintEl.style.display = "block";
}
```

Add an AC hints container to the HTML, near the AC Reference field:

```html
<div id="ado-ac-hints"
     style="display:none; background:#f0f6ff; border:1px solid #c7e0f4; border-radius:4px;
            padding:8px 12px; font-size:12px; margin-bottom:10px; color:#004578;">
</div>
```

Wire `loadScenarioAcHints()` in the `APP_BOOT` handler:

```javascript
if (msg.type === "APP_BOOT" && msg.appId === "ado") {
  currentRole = msg.role || "junior";
  applyTheme(msg.theme || "light");
  applyRole(currentRole);
  if (msg.scenarioId) loadScenarioAcHints(msg.scenarioId);  // NEW
}
```

### 2c — Bug history list

Add a collapsible "Filed this session" section below the form that shows all bugs
the trainee has submitted so far. Update it each time `showConfirmation()` is called.

Maintain a session array of filed bugs:

```javascript
var filedBugs = [];  // persists within the app's lifetime

function showConfirmation(title, severity, acRef) {
  // ... existing confirmation code ...

  // Track this bug in session history
  filedBugs.push({ title: title, severity: severity, acRef: acRef, time: getTimeNow() });
  renderBugHistory();
}

function getTimeNow() {
  var d = new Date();
  return d.getHours() + ":" + (d.getMinutes() < 10 ? "0" : "") + d.getMinutes();
}

function renderBugHistory() {
  var histEl = document.getElementById("ado-history");
  if (!histEl || filedBugs.length === 0) return;

  histEl.style.display = "block";
  var items = filedBugs.map(function(b, i) {
    return "<li><strong>" + escapeHtml(b.title) + "</strong> " +
           "<span style='color:#605e5c;font-size:11px;'>" +
           escapeHtml(b.severity) + " · " + escapeHtml(b.acRef) + " · " + b.time +
           "</span></li>";
  });
  histEl.innerHTML =
    "<strong style='font-size:12px;'>Filed this session (" + filedBugs.length + "):</strong>" +
    "<ul style='margin:6px 0 0;padding-left:18px;font-size:12px;'>" + items.join("") + "</ul>";
}

function escapeHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
```

Add the history container near the bottom of the app HTML:

```html
<div id="ado-history"
     style="display:none; margin-top:16px; padding:10px 12px; background:#f8f8f8;
            border:1px solid #edebe9; border-radius:4px; color:#201f1e;">
</div>
```

Update `handleSave()` to pass `severity` and `acRef` to `showConfirmation()`:

```javascript
// In handleSave(), update the showConfirmation call:
showConfirmation(title, severity, acRef);
```

And update the `showConfirmation` signature accordingly.

---

## What NOT to Change

- Do not modify `build.js`, `os.css`, or any `src/` files other than what is explicitly described
- Do not touch `scenarios/case-002.js` — it was created in C-7 and should not be modified here
- Do not touch `apps/teams.html`, `apps/browser.html`, or any other app files
- Do not add CDN links or external dependencies
- Do not rename existing field IDs — read the current field IDs in each app file before writing

---

## Definition of Done

**Dynamics CRM:**
- [ ] `checkStatusViolation()` fires on form load — posts `BUG_FOUND` if Junior role has Escalated/Closed status
- [ ] `checkEscalationReason()` fires on form load and on Status dropdown change — posts `BUG_FOUND` if Status=Escalated and Reason is blank
- [ ] Escalation Reason field border turns red when the violation is detected
- [ ] `checkDateField()` fires on form load in addition to on field change
- [ ] All three checks called at end of `populateCaseForm()`

**ADO:**
- [ ] `validateAcRef()` validates the AC Reference format and blocks save if format is wrong
- [ ] `loadScenarioAcHints()` reads the active scenario's `acceptanceCriteria` and displays them
- [ ] AC hints panel is visible when a scenario with `acceptanceCriteria` is active
- [ ] `filedBugs` session array tracks each filed report
- [ ] Bug history panel renders after the first submission and updates with each subsequent one
- [ ] `showConfirmation()` accepts and logs `severity` and `acRef` in addition to `title`

**Build:**
- [ ] `node build.js` runs without errors
- [ ] Loading `case-002` scenario in the OS shows all three violations detected in Dynamics on boot
- [ ] Filing a bug in ADO with an invalid AC format (e.g. "AC2.1" or "2.1") blocks the save
- [ ] Filing a valid bug updates the session history panel
