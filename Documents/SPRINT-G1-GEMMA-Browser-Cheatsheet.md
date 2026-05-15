# Sprint G-1 — Browser Home Page + QA Cheat Sheet
## Gemma Build Prompt

Read GEMMA-STYLE-GUIDE.md before writing any code.
The OS build (node build.js) must be working before this sprint.

---

## Context

This is the QA Pilot training platform.
Stack: pure HTML/CSS/JS, no frameworks, no CDN links. File:// safe architecture.
All content inside `desktop/apps/browser.html` must be self-contained.

The QA Browser (`apps/browser.html`) is a tabbed Edge-style browser that runs
inside the OS desktop simulator. It already works — tabs open and close, the
address bar accepts routes, and content renders via `srcdoc` iframes.

The browser's content system uses a function called `buildContentForRoute(route, title)`.
Routes are internal strings, not real URLs. Currently the home page shows a
generic placeholder. This sprint replaces it with real training content.

The browser uses `srcdoc` to render pages — this means all content returned by
`buildContentForRoute()` must be a self-contained HTML string with no external
links, no `<link>` tags, no `<script src="...">` tags.

---

## What to Build

### Deliverable 1: Improve `buildContentForRoute("home")`

Replace the existing home route content with a QA Pilot welcome page that opens
automatically when the browser app launches. The page should include:

- A header: "QA Pilot — Quick Reference"
- A workflow section: numbered steps showing the trainee workflow
- An app guide section: what each OS app is for
- A keyboard tips section: useful shortcuts

All content must be returned as a plain HTML string from `buildContentForRoute()`.
Use only inline styles — no external CSS.

**Workflow steps to include:**
1. Sign in and unlock the OS desktop
2. Open the Dynamics CRM case from your desktop icon
3. Open the AC Panel to review what the system should do
4. Compare the CRM case against the AC — look for anything that doesn't match
5. Open Azure DevOps for each bug you find and file a complete report
6. When done, click "Submit for Certification" in the taskbar

**App descriptions to include:**

| App | Purpose |
|-----|---------|
| Dynamics CRM | View and investigate the active support case |
| AC Panel | Review the Acceptance Criteria — what correct behaviour looks like |
| Azure DevOps | File a bug report for each defect you find |
| Browser | This app — reference material and guidelines |
| Training | Starts the capstone assessment with your scenario brief |

**Keyboard tip to include:**
- Double-click a desktop icon to open an app
- Click the Windows logo (taskbar) to open the Start menu
- Click Submit in the taskbar when you are finished

---

### Deliverable 2: Add `buildContentForRoute("docs/qa-guidelines")`

Add a new route case that returns a QA guidelines reference page. This is a
second tab that opens alongside Home when the browser launches.

The page should include:

**Section 1: What is a Bug Report?**
A valid ADO bug report requires:
- Title: a clear, one-line description of the defect (not "it doesn't work")
- Severity: 1 = Critical, 2 = High, 3 = Medium, 4 = Low
- AC Reference: the specific acceptance criteria the defect violates (e.g. AC-2.1)
- Steps to Reproduce: numbered steps that reliably reproduce the issue

**Section 2: Severity Guide**
- Severity 1 — Critical: system crash, data loss, security issue, blocks all users
- Severity 2 — High: major feature broken, no workaround, affects most users
- Severity 3 — Medium: feature partially broken, workaround exists
- Severity 4 — Low: cosmetic issue, minor inconvenience

**Section 3: Good vs Bad Bug Titles**
- Bad: "Status is broken"
- Good: "Junior Investigator can set case Status to Closed — AC-2.1 violation"
- Bad: "Date field issue"
- Good: "Date Opened field accepts future dates — should be blocked per AC-3.2"

---

### Deliverable 3: Open Two Tabs on Launch

Modify the `APP_BOOT` handler in `browser.html` so that when the browser first
opens (no saved tabs), it creates two default tabs instead of one:

```javascript
if (!state.tabs || !state.tabs.length) {
    createTab({ title: "Home",          route: "home" });
    createTab({ title: "QA Guidelines", route: "docs/qa-guidelines" });
    // Set Home as the active tab
    if (state.tabs.length > 0) state.activeTabId = state.tabs[0].id;
}
```

---

## Style Guide for srcdoc Content

All HTML strings returned by `buildContentForRoute()` must follow this pattern:

```javascript
return (
    "<!doctype html><html><head><meta charset='UTF-8'>" +
    "<title>[Page Title]</title>" +
    "<style>" +
    "body { font-family: Segoe UI, system-ui, sans-serif; font-size: 13px;" +
    "       padding: 20px 24px; background: #faf9f8; color: #201f1e;" +
    "       line-height: 1.6; max-width: 720px; }" +
    "h1   { font-size: 17px; font-weight: 600; margin: 0 0 16px; color: #0078d4; }" +
    "h2   { font-size: 14px; font-weight: 600; margin: 20px 0 8px; color: #201f1e; }" +
    "p    { margin: 0 0 10px; }" +
    "ol, ul { margin: 0 0 12px; padding-left: 20px; }" +
    "li   { margin-bottom: 4px; }" +
    "table { border-collapse: collapse; width: 100%; margin-bottom: 12px; }" +
    "th   { background: #edebe9; text-align: left; padding: 6px 10px;" +
    "       font-size: 12px; font-weight: 600; }" +
    "td   { padding: 6px 10px; border-bottom: 1px solid #edebe9; font-size: 12px; }" +
    "code { background: #edebe9; padding: 1px 5px; border-radius: 3px;" +
    "       font-family: Consolas, monospace; font-size: 12px; }" +
    ".tip { background: #f0f6ff; border-left: 3px solid #0078d4;" +
    "       padding: 8px 12px; border-radius: 0 4px 4px 0; margin-bottom: 12px; }" +
    "</style>" +
    "</head><body>" +
    // ... page content here ...
    "</body></html>"
);
```

Do not use template literals (backticks) — use string concatenation with `+`.
The content runs inside an srcdoc iframe and must be HTML-escaped where needed.

---

## What NOT to Change

- Do not change the tab system logic (createTab, closeTab, setActiveTab)
- Do not change the address bar or navigation button behaviour
- Do not change state persistence logic
- Do not add CDN links or external dependencies
- Do not add `<link>` or `<script src="...">` tags inside srcdoc content strings
- Do not touch any other app files

---

## After This Sprint

Run `node build.js` from the `desktop/` folder.
Open `dist.html`, unlock the OS, double-click the Browser icon.
Confirm: two tabs open (Home and QA Guidelines), content displays correctly,
both tabs can be switched, a third tab can be opened via the + button.

---

## Definition of Done

- [ ] `buildContentForRoute("home")` returns a full HTML string with workflow, app guide, and keyboard tips
- [ ] `buildContentForRoute("docs/qa-guidelines")` returns a full HTML string with bug report guide, severity levels, and good/bad title examples
- [ ] `APP_BOOT` opens two default tabs: "Home" and "QA Guidelines"
- [ ] Home tab is active on launch
- [ ] All content uses inline styles only — no external CSS or JS
- [ ] All HTML strings use string concatenation, not template literals
- [ ] `node build.js` runs without errors
- [ ] Browser app opens cleanly in dist.html with both tabs visible
