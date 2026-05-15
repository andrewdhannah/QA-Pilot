# Sprint C-1 — Dynamics Role-Gating
## Copilot Prompt — GitHub repo: andrewdhannah/QA-Pilot

You are working in the QA Pilot repository, inside `desktop/apps/dynamics.html`.
No CDN links, no external imports, no fetch(). File:// safe architecture.
Run `node build.js` from the `desktop/` folder after making changes.

---

## Context

The OS shell (`src/os-core.js`) sends two postMessage events to every app iframe:

**APP_BOOT** — fired once when the iframe loads:
```javascript
{ type: "APP_BOOT", appId: "dynamics", role: "junior" | "senior", theme: "light" | "dark" }
```

**ROLE_CHANGE** — fired when the user switches role via the Start menu:
```javascript
{ type: "ROLE_CHANGE", role: "junior" | "senior" }
```

The Dynamics app already has a case investigation form with fields including:
- Status dropdown (Active, Pending, Closed, Escalated)
- Escalation Reason
- Assigned To
- Date Opened (with a date picker)

The OS role system distinguishes Junior Investigator from Senior Investigator.
Junior investigators should not be able to close or escalate cases — that is a
Senior action. This mirrors real-world QA workflows where juniors investigate
and seniors approve escalations.

The Dynamics app also needs to report discovered bugs back to the OS for scoring.
When a student encounters a deliberate bug in the CRM form, the app should post
a `BUG_FOUND` message so the scoring engine can track it.

---

## Deliverable 1: Listen for APP_BOOT and ROLE_CHANGE

In `apps/dynamics.html`, add a `window.addEventListener("message", ...)` block
that handles both message types.

```javascript
window.addEventListener("message", function(event) {
    var msg = event.data;
    if (!msg || !msg.type) return;

    if (msg.type === "APP_BOOT" && msg.appId === "dynamics") {
        applyRole(msg.role || "junior");
        applyTheme(msg.theme || "light");
        populateCaseForm();   // Load default/scenario case data into fields
    }

    if (msg.type === "ROLE_CHANGE") {
        applyRole(msg.role || "junior");
    }
});
```

---

## Deliverable 2: applyRole(role)

Implement `applyRole(role)` to show/hide or lock fields based on the role.

**Junior Investigator restrictions:**
- Status dropdown: remove or disable "Closed" and "Escalated" options
- Escalation Reason field: set `disabled = true` and add visual indicator (greyed out)
- Assigned To field: set `readonly = true` (junior can see but not reassign)

**Senior Investigator — full access:**
- All Status options available
- Escalation Reason enabled
- Assigned To editable

```javascript
function applyRole(role) {
    var statusSelect    = document.getElementById("dyn-status");
    var escalationField = document.getElementById("dyn-escalation-reason");
    var assignedField   = document.getElementById("dyn-assigned-to");
    var roleNotice      = document.getElementById("dyn-role-notice");

    if (role === "junior") {
        // Remove restricted options from Status dropdown
        if (statusSelect) {
            ["Closed", "Escalated"].forEach(function(val) {
                var opt = statusSelect.querySelector('option[value="' + val + '"]');
                if (opt) opt.remove();
            });
        }
        if (escalationField) {
            escalationField.disabled = true;
            escalationField.title    = "Escalation requires Senior Investigator role";
        }
        if (assignedField)   assignedField.readOnly = true;
        if (roleNotice)      roleNotice.style.display = "block";

    } else {
        // Senior — restore full access
        if (statusSelect && !statusSelect.querySelector('option[value="Closed"]')) {
            var closedOpt = document.createElement("option");
            closedOpt.value       = "Closed";
            closedOpt.textContent = "Closed";
            statusSelect.appendChild(closedOpt);
        }
        if (statusSelect && !statusSelect.querySelector('option[value="Escalated"]')) {
            var escOpt = document.createElement("option");
            escOpt.value       = "Escalated";
            escOpt.textContent = "Escalated";
            statusSelect.appendChild(escOpt);
        }
        if (escalationField) {
            escalationField.disabled = false;
            escalationField.title    = "";
        }
        if (assignedField)   assignedField.readOnly = false;
        if (roleNotice)      roleNotice.style.display = "none";
    }
}
```

Add a role notice banner near the top of the form (hidden by default):
```html
<div id="dyn-role-notice" style="display:none; background:#fff4ce; border:1px solid #f0c000;
     border-radius:4px; padding:8px 12px; font-size:12px; margin-bottom:12px; color:#6b4c00;">
    Junior Investigator — Status changes to Closed or Escalated require a Senior Investigator.
</div>
```

---

## Deliverable 3: BUG_FOUND Reporting

The capstone scenario has two deliberate bugs the student should discover:

1. **`status-junior-close`** — A Junior should not be able to set Status to Closed,
   but the unpatched form allows it. When the applyRole() logic removes the
   "Closed" option for juniors, this is the bug the student discovers.
   Report it when a Junior user *attempts* to set Status to Closed:

```javascript
// On Status change, if junior tries to pick Closed or Escalated
if (statusSelect) {
    statusSelect.addEventListener("change", function() {
        var OS = window.parent && (window.parent.QA_OS || window.parent.OS);
        if (currentRole === "junior" &&
            (this.value === "Closed" || this.value === "Escalated")) {
            if (OS && OS.notify) OS.notify("⚠ Status restricted for Junior role.");
            // Post BUG_FOUND so the scoring engine tracks this discovery
            window.parent.postMessage({ type: "BUG_FOUND", bugId: "status-junior-close" }, "*");
        }
    });
}
```

2. **`future-date-allowed`** — The Date Opened field should not accept future dates,
   but currently it does. When the student enters a future date, report it:

```javascript
var dateField = document.getElementById("dyn-date-opened");
if (dateField) {
    dateField.addEventListener("change", function() {
        var selected = new Date(this.value);
        var today    = new Date();
        today.setHours(0, 0, 0, 0);
        if (selected > today) {
            window.parent.postMessage({ type: "BUG_FOUND", bugId: "future-date-allowed" }, "*");
            var OS = window.parent && (window.parent.QA_OS || window.parent.OS);
            if (OS && OS.notify) OS.notify("⚠ Future date entered in Date Opened field.");
        }
    });
}
```

---

## Deliverable 4: populateCaseForm()

When `APP_BOOT` fires, populate the case form with default data so it looks like
a real active case. If a capstone scenario is loaded, use its `crmState` instead.

```javascript
function populateCaseForm() {
    // Try to get scenario data first
    var scenario  = window.SCENARIOS && window.SCENARIOS["capstone-001"];
    var crmState  = scenario && scenario.crmState;

    var defaults = {
        caseTitle:    "Customer unable to complete online payment",
        customerName: "Maria Chen",
        caseId:       "CASE-00142",
        priority:     "Medium",
        status:       "Active",
        summary:      "Customer reports payment fails at the final confirmation step.",
        product:      "Online Payments Portal",
        assignedTo:   "Junior Investigator",
        dateOpened:   new Date().toISOString().split("T")[0]
    };

    var data = crmState || defaults;

    // Set each field by ID — adjust IDs to match what already exists in dynamics.html
    setField("dyn-case-title",    data.caseTitle);
    setField("dyn-customer-name", data.customerName);
    setField("dyn-case-id",       data.caseId);
    setField("dyn-priority",      data.priority);
    setField("dyn-status",        data.status);
    setField("dyn-summary",       data.summary);
    setField("dyn-product",       data.product);
    setField("dyn-assigned-to",   data.assignedTo);
    setField("dyn-date-opened",   data.dateOpened || defaults.dateOpened);
}

function setField(id, value) {
    var el = document.getElementById(id);
    if (!el || value === undefined) return;
    if (el.tagName === "SELECT") {
        el.value = value;
    } else {
        el.value = value;
    }
}
```

**Important:** Read the existing field IDs in `dynamics.html` before writing this
function and match them exactly. Do not rename existing IDs.

---

## What NOT to Change

- Do not touch `src/os-core.js`
- Do not touch `build.js`
- Do not touch any other app files
- Do not add CDN links or external dependencies
- Do not change field IDs that already exist — only add the missing ones

---

## Definition of Done

- [ ] `window.addEventListener("message", ...)` handles both `APP_BOOT` and `ROLE_CHANGE`
- [ ] `applyRole("junior")` disables Escalation Reason and removes Closed/Escalated from Status
- [ ] `applyRole("senior")` restores full access
- [ ] Role notice banner is visible for Junior, hidden for Senior
- [ ] Status `change` event posts `BUG_FOUND` with bugId `status-junior-close` when Junior tries restricted status
- [ ] Date field `change` event posts `BUG_FOUND` with bugId `future-date-allowed` for future dates
- [ ] `populateCaseForm()` populates all fields from scenario data or defaults on `APP_BOOT`
- [ ] `node build.js` runs without errors
- [ ] Opening dynamics.html via dist.html shows the populated form and role restrictions apply immediately
