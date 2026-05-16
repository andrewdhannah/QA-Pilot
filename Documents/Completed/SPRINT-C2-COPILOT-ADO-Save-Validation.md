# Sprint C-2 — ADO Form Save + Validation
## Copilot Prompt — GitHub repo: andrewdhannah/QA-Pilot

You are working in the QA Pilot repository, inside `desktop/apps/ado.html`.
No CDN links, no external imports, no fetch(). File:// safe architecture.
Run `node build.js` from the `desktop/` folder after making changes.

---

## Context

The Azure DevOps bug report form (`apps/ado.html`) exists and renders correctly,
but currently does not validate or save. When a student fills in a bug report
and clicks Save/Submit, nothing happens — no feedback, no signal to the OS.

The OS scoring engine (`src/scoring.js`) is listening for `BUG_LOGGED` messages
from app iframes. It expects this shape:

```javascript
window.parent.postMessage({
    type: "BUG_LOGGED",
    data: {
        title:    "string — the bug title",
        severity: "string — e.g. '1 - Critical', '2 - High', '3 - Medium'",
        acRef:    "string — the AC reference, e.g. 'AC-2.1'",
        hasSteps: true   // boolean — true if Steps to Reproduce is not empty
    }
}, "*");
```

The OS also listens for `APP_BOOT` and `ROLE_CHANGE` messages (same as dynamics.html):
```javascript
{ type: "APP_BOOT", appId: "ado", role: "junior" | "senior", theme: "light" | "dark" }
{ type: "ROLE_CHANGE", role: "junior" | "senior" }
```

---

## Deliverable 1: Listen for APP_BOOT and ROLE_CHANGE

Add a message listener to `apps/ado.html`:

```javascript
var currentRole = "junior";

window.addEventListener("message", function(event) {
    var msg = event.data;
    if (!msg || !msg.type) return;

    if (msg.type === "APP_BOOT" && msg.appId === "ado") {
        currentRole = msg.role || "junior";
        applyTheme(msg.theme || "light");
        applyRole(currentRole);
    }

    if (msg.type === "ROLE_CHANGE") {
        currentRole = msg.role || "junior";
        applyRole(currentRole);
    }
});
```

---

## Deliverable 2: Form Validation

Implement `validateForm()` before allowing a save. All four fields are required:

```javascript
function validateForm() {
    var errors = [];

    var title    = getFieldValue("ado-title");
    var severity = getFieldValue("ado-severity");
    var acRef    = getFieldValue("ado-ac-ref");
    var steps    = getFieldValue("ado-steps");

    if (!title.trim())    errors.push("Title is required.");
    if (!severity.trim()) errors.push("Severity is required.");
    if (!acRef.trim())    errors.push("AC Reference is required.");
    if (!steps.trim())    errors.push("Steps to Reproduce is required.");

    return errors;   // Empty array = valid
}

function getFieldValue(id) {
    var el = document.getElementById(id);
    return el ? el.value : "";
}
```

**Read the existing field IDs in `ado.html` before writing this function
and match them exactly. Do not rename existing IDs.**

---

## Deliverable 3: Save Handler + BUG_LOGGED Signal

Wire the Save/Submit button to validate and then post the `BUG_LOGGED` message:

```javascript
function handleSave() {
    var errors = validateForm();

    // Show validation errors if any
    var errorEl = document.getElementById("ado-errors");
    if (errors.length > 0) {
        if (errorEl) {
            errorEl.textContent = errors.join(" ");
            errorEl.style.display = "block";
        }
        return;   // Do not proceed
    }

    // Clear any previous errors
    if (errorEl) errorEl.style.display = "none";

    // Read field values
    var title    = getFieldValue("ado-title").trim();
    var severity = getFieldValue("ado-severity").trim();
    var acRef    = getFieldValue("ado-ac-ref").trim();
    var steps    = getFieldValue("ado-steps").trim();

    // Post BUG_LOGGED to the OS scoring engine
    window.parent.postMessage({
        type: "BUG_LOGGED",
        data: {
            title:    title,
            severity: severity,
            acRef:    acRef,
            hasSteps: steps.length > 0
        }
    }, "*");

    // Notify the OS (shows in Notification Centre)
    var OS = window.parent && (window.parent.QA_OS || window.parent.OS);
    if (OS && OS.notify) {
        OS.notify("📋 Bug report filed: " + title);
    }

    // Show confirmation state in the form
    showConfirmation(title);
}
```

---

## Deliverable 4: Confirmation State

After a successful save, show a confirmation message inside the app and
offer a "File Another" button to reset the form:

```javascript
function showConfirmation(title) {
    var form    = document.getElementById("ado-form");
    var confirm = document.getElementById("ado-confirm");

    if (form)    form.style.display    = "none";
    if (confirm) confirm.style.display = "block";

    var confirmedTitle = document.getElementById("ado-confirmed-title");
    if (confirmedTitle) confirmedTitle.textContent = title;
}

function resetForm() {
    var form    = document.getElementById("ado-form");
    var confirm = document.getElementById("ado-confirm");

    if (form)    { form.style.display = "block"; form.reset(); }
    if (confirm) confirm.style.display = "none";
}
```

Add a confirmation panel to the HTML (hidden by default):
```html
<div id="ado-confirm" style="display:none; padding:24px; text-align:center;">
    <div style="font-size:32px; margin-bottom:12px;">✓</div>
    <div style="font-size:15px; font-weight:600; margin-bottom:8px;">Bug Report Filed</div>
    <div id="ado-confirmed-title" style="font-size:13px; color:#605e5c; margin-bottom:20px;"></div>
    <button onclick="resetForm()" style="padding:8px 20px; background:#0078d4; color:white;
        border:none; border-radius:4px; cursor:pointer; font-size:13px;">
        File Another Report
    </button>
</div>
```

Add an error display element near the save button:
```html
<div id="ado-errors" style="display:none; color:#a4262c; font-size:12px;
     margin-bottom:8px; padding:6px 10px; background:#fde7e9;
     border-radius:4px; border:1px solid #f1707b;"></div>
```

---

## Deliverable 5: Role-Based Severity Options

Senior Investigators can set higher-severity bugs. Apply role gating to the
Severity dropdown so Junior investigators see an appropriate range:

```javascript
function applyRole(role) {
    // Both roles can file bugs — no hard restrictions, just a notice
    var roleNotice = document.getElementById("ado-role-notice");
    if (roleNotice) {
        roleNotice.style.display = role === "junior" ? "block" : "none";
    }
}
```

Add a subtle notice for Juniors (hidden for Senior):
```html
<div id="ado-role-notice" style="display:none; background:#f0f6ff;
     border:1px solid #c7e0f4; border-radius:4px; padding:8px 12px;
     font-size:12px; margin-bottom:12px; color:#004578;">
    Junior Investigator — Log all bugs you find. A Senior will review and triage.
</div>
```

---

## Wiring the Save Button

Find the existing Save/Submit button in `ado.html` and wire it to `handleSave()`.
If no button exists, add one:

```html
<button type="button" onclick="handleSave()"
    style="padding:8px 20px; background:#0078d4; color:white;
           border:none; border-radius:4px; cursor:pointer; font-size:13px;">
    File Bug Report
</button>
```

---

## What NOT to Change

- Do not touch `src/os-core.js`
- Do not touch `build.js`
- Do not touch any other app files
- Do not add CDN links or external dependencies
- Do not rename existing field IDs — read the file and match them

---

## Definition of Done

- [ ] `APP_BOOT` and `ROLE_CHANGE` messages are handled
- [ ] `validateForm()` returns errors if Title, Severity, AC Reference, or Steps are empty
- [ ] Validation errors are displayed inline near the save button
- [ ] On valid save, `BUG_LOGGED` is posted to `window.parent` with `{ title, severity, acRef, hasSteps }`
- [ ] OS Notification Centre shows "Bug report filed: [title]" after save
- [ ] Confirmation panel appears after save, form is hidden
- [ ] "File Another Report" button resets the form
- [ ] Junior role notice is shown for Junior, hidden for Senior
- [ ] `node build.js` runs without errors
- [ ] Filing a report via dist.html shows confirmation and a notification in the OS taskbar
