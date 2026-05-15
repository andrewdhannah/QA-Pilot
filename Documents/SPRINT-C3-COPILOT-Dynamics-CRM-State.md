# Sprint C-3 — Dynamics CRM State from Scenario
## Copilot Prompt — GitHub repo: andrewdhannah/QA-Pilot

You are working in the QA Pilot repository, inside `desktop/apps/dynamics.html`.
No CDN links, no external imports, no fetch(). File:// safe architecture.
Run `node build.js` from the `desktop/` folder after making changes.

---

## Context

The capstone scenario (`scenarios/capstone-scenario.js`) defines a `crmState`
object that pre-populates the Dynamics case form when the assessment begins.
This sprint wires that data into the Dynamics app so that when the capstone
loads, the student sees a realistic active case rather than an empty form.

The scenario data is available via `window.SCENARIOS["capstone-001"].crmState`
once the OS bundle has loaded. It contains:

```javascript
crmState: {
    caseTitle:    "Customer unable to complete online payment",
    customerName: "Maria Chen",
    caseId:       "CASE-00142",
    priority:     "Medium",
    status:       "Active",
    summary:      "Customer reports payment fails at the final confirmation step. Issue is intermittent but reproducible.",
    product:      "Online Payments Portal",
    assignedTo:   "Junior Investigator"
}
```

The OS shell also sends an `APP_BOOT` message when the app iframe loads:
```javascript
{ type: "APP_BOOT", appId: "dynamics", role: "junior" | "senior", theme: "light" | "dark" }
```

**Sprint C-1 (role-gating) should be complete before this sprint.**
This sprint extends `populateCaseForm()` — it does not replace role-gating.

---

## Deliverable 1: Read Scenario Data in populateCaseForm()

Update or create `populateCaseForm()` to read from `window.SCENARIOS` first,
then fall back to defaults if no scenario is loaded:

```javascript
function populateCaseForm() {
    // Prefer live scenario data if the capstone is active
    var scenario = window.SCENARIOS && window.SCENARIOS["capstone-001"];
    var data     = (scenario && scenario.crmState) || {
        caseTitle:    "Customer unable to complete online payment",
        customerName: "Maria Chen",
        caseId:       "CASE-00142",
        priority:     "Medium",
        status:       "Active",
        summary:      "Customer reports payment fails at the final confirmation step. Issue is intermittent but reproducible.",
        product:      "Online Payments Portal",
        assignedTo:   "Junior Investigator",
        dateOpened:   new Date().toISOString().split("T")[0]
    };

    // Map crmState keys to form field IDs
    // Read the actual field IDs in dynamics.html and update this map to match
    var fieldMap = {
        "dyn-case-title":    data.caseTitle,
        "dyn-customer-name": data.customerName,
        "dyn-case-id":       data.caseId,
        "dyn-priority":      data.priority,
        "dyn-status":        data.status,
        "dyn-summary":       data.summary,
        "dyn-product":       data.product,
        "dyn-assigned-to":   data.assignedTo,
        "dyn-date-opened":   data.dateOpened || new Date().toISOString().split("T")[0]
    };

    Object.keys(fieldMap).forEach(function(id) {
        var el  = document.getElementById(id);
        var val = fieldMap[id];
        if (el && val !== undefined) el.value = val;
    });
}
```

**Before implementing:** read `dynamics.html` and list every `id` attribute on
form inputs, selects, and textareas. Update the `fieldMap` keys above to match
exactly. Do not guess IDs.

---

## Deliverable 2: Case Header Display

Add a read-only case header above the editable form that shows the case metadata.
This mimics the Dynamics 365 case header ribbon — always visible, not editable:

```html
<!-- Case header — populated by JS from scenario crmState -->
<div id="dyn-case-header" style="
    background: #0078d4;
    color: white;
    padding: 12px 16px;
    margin-bottom: 16px;
    border-radius: 4px;
    font-size: 12px;
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
">
    <div>
        <div style="opacity:0.75; font-size:11px;">Case ID</div>
        <div id="dyn-header-case-id" style="font-weight:600;">—</div>
    </div>
    <div>
        <div style="opacity:0.75; font-size:11px;">Customer</div>
        <div id="dyn-header-customer" style="font-weight:600;">—</div>
    </div>
    <div>
        <div style="opacity:0.75; font-size:11px;">Priority</div>
        <div id="dyn-header-priority" style="font-weight:600;">—</div>
    </div>
    <div>
        <div style="opacity:0.75; font-size:11px;">Status</div>
        <div id="dyn-header-status" style="font-weight:600;">—</div>
    </div>
    <div>
        <div style="opacity:0.75; font-size:11px;">Assigned To</div>
        <div id="dyn-header-assigned" style="font-weight:600;">—</div>
    </div>
</div>
```

Populate the header from the same scenario data:

```javascript
function populateCaseHeader(data) {
    var fields = {
        "dyn-header-case-id":   data.caseId,
        "dyn-header-customer":  data.customerName,
        "dyn-header-priority":  data.priority,
        "dyn-header-status":    data.status,
        "dyn-header-assigned":  data.assignedTo
    };
    Object.keys(fields).forEach(function(id) {
        var el = document.getElementById(id);
        if (el && fields[id]) el.textContent = fields[id];
    });
}
```

Call `populateCaseHeader(data)` at the end of `populateCaseForm()`.

---

## Deliverable 3: Status Change Updates Header

When the student changes the Status dropdown, reflect that change in the
case header so it stays in sync:

```javascript
var statusSelect = document.getElementById("dyn-status");
if (statusSelect) {
    statusSelect.addEventListener("change", function() {
        var headerStatus = document.getElementById("dyn-header-status");
        if (headerStatus) headerStatus.textContent = this.value;

        // BUG_FOUND logic from Sprint C-1 goes here (do not remove it)
    });
}
```

---

## What NOT to Change

- Do not remove or replace the role-gating logic from Sprint C-1
- Do not touch `src/os-core.js`
- Do not touch `build.js`
- Do not touch any other app files
- Do not add CDN links or external dependencies

---

## Definition of Done

- [ ] `populateCaseForm()` reads `window.SCENARIOS["capstone-001"].crmState` when available
- [ ] Falls back to hardcoded defaults if no scenario is loaded
- [ ] All form fields are populated on `APP_BOOT`
- [ ] Case header ribbon appears above the form with Case ID, Customer, Priority, Status, Assigned To
- [ ] Changing the Status dropdown updates the header Status display
- [ ] Role-gating from Sprint C-1 still works correctly after this sprint
- [ ] `node build.js` runs without errors
- [ ] Opening Dynamics via dist.html shows the pre-populated case with header ribbon
