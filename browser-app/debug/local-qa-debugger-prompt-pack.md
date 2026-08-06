# Local QA Debugger Prompt Pack

**Project:** Static `file://` QA Debugger / Bug Reporter  
**Target environment:** Local-only website, no install, no server, no build step, no external dependencies  
**Primary output:** A sidecar debug site that reads/writes the same local app data layer, files structured bugs, exports/imports JSON, and exports agent-ready Markdown  
**Date:** 2026-05-22  

---

## 0. Core Concept

Build a static local QA debugger that sits inside the same project folder as the main training website.

The debugger must not depend on unrestricted filesystem access. Under `file://`, browser JavaScript cannot safely scan or mutate arbitrary project files. Instead, the main app must self-report its page/session/runtime metadata into a shared local data layer. The debugger then becomes a second local UI over that structured app state.

The system should work like this:

```text
Main Site
  → registers page metadata
  → records session/progress/runtime state
  → allows bug filing from current page
  → writes structured records into shared localDB abstraction

Debug Site
  → reads the same localDB abstraction
  → displays pages, sessions, bugs, and clarification status
  → imports bug JSON from another tester/developer
  → exports bug JSON
  → exports agent-ready Markdown

Developer / Local Agent
  → imports JSON or reads Markdown
  → fixes clear bugs
  → asks the human-in-the-middle for clarification when unclear
```

The app owns the runtime truth.  
The debugger is another local UI over that truth.  
The export file is the transfer artifact.  
The human remains the authority when expected behavior is unclear.

---

## 1. Non-Negotiable Constraints

Use these constraints in every implementation step.

```text
- Must run from file://
- Must not require a local server
- Must not require npm, Node, Python, Electron, Tauri, Docker, or browser extensions
- Must not use external CDN resources
- Must not require internet access
- Must be plain HTML, CSS, and JavaScript
- Must preserve the existing project structure
- Must not break current app behavior
- Must degrade safely if browser storage is unavailable
- JSON export is the durable source of transfer between machines
- Markdown export is the durable handoff format for agentic AI
- Unclear bugs must be marked NEEDS_CLARIFICATION, not guessed at
```

---

## 2. Desired Folder Structure

Ask the agent to create or adapt toward this structure.

```text
project/
  index.html
  lessons/
    lesson-01.html
    lesson-02.html
    lesson-03.html
  assets/
    css/
    js/

  qa/
    qa-db.js
    qa-schema.js
    qa-page-register.js
    qa-bug-api.js
    qa-export-json.js
    qa-export-md.js
    qa-import-json.js

  debug/
    index.html
    debug.css
    debug.js
    debug-panel.js
    debug-filters.js
    debug-import-export.js

  bug-reports/
    README.md
```

If the existing project has a different folder layout, preserve it. Add the QA/debug files in the least invasive location.

---

# Prompt 1 — Audit the Existing Storage Layer

## Purpose

Determine how the current project stores local data and where to attach the debugger without breaking existing behavior.

## Prompt

```text
You are auditing a static local website that must run under file:// with no server, no install, no dependencies, and no build process.

Task:
Review the current project structure and identify the existing localDB/storage layer.

Find:
1. Where localDB is defined.
2. How records are created, updated, read, and deleted.
3. Whether the storage is backed by IndexedDB, localStorage, an in-memory object, a JSON-like abstraction, or another browser-accessible mechanism.
4. Whether the storage is available to multiple HTML pages in the project.
5. Whether the debugger can safely import the same storage wrapper.
6. Any assumptions that would fail under file://.

Do not modify code yet.

Output:
- A short audit report.
- The exact files that define or use storage.
- The safest integration point for the QA debugger.
- Any risks.
- A recommended minimal implementation path.

Constraints:
- Do not add dependencies.
- Do not require a server.
- Do not convert the app to a framework.
- Do not assume unrestricted filesystem access.
```

---

# Prompt 2 — Define the QA Schema

## Purpose

Add a stable schema for page metadata, bug reports, sessions, exports, and clarification records.

## Prompt

```text
Create or update a plain JavaScript schema file for the local QA debugger.

Target file:
qa/qa-schema.js

Requirements:
Define schema objects or schema documentation for:

1. Page records
2. Bug records
3. Session records
4. Export records
5. Clarification records

The schema must include a which_page field that anchors a bug to the source page.

Use this page metadata shape:

{
  which_page: "lessons/lesson-02.html",
  page_id: "lesson-02",
  module_id: "crm-basics",
  page_title: "CRM Navigation Basics",
  app_version: "v0.4",
  session_id: "SESSION-2026-05-22-001"
}

Use this bug shape:

{
  id: "BUG-2026-05-22-001",
  title: "Next button does not advance from Lesson 02",
  severity: "high",
  status: "new",
  bug_type: "navigation",
  which_page: "lessons/lesson-02.html",
  page_id: "lesson-02",
  module_id: "crm-basics",
  page_title: "CRM Navigation Basics",
  observed: "Clicking the Next button does nothing.",
  expected: "The user should advance to Lesson 03.",
  steps_to_reproduce: [
    "Open lessons/lesson-02.html",
    "Complete the lesson quiz",
    "Click the Next button"
  ],
  environment: {
    browser: "Chrome",
    run_mode: "file://",
    viewport: "1440x900"
  },
  evidence: [],
  human_clarification_needed: false,
  clarification_question: "",
  agent_instructions: "Inspect the navigation handler. Verify the target path exists before modifying shared logic.",
  created_by: "tester",
  created_at: "2026-05-22T00:00:00.000Z",
  updated_at: "2026-05-22T00:00:00.000Z"
}

Allowed severities:
- blocker
- high
- medium
- low
- note

Allowed statuses:
- new
- triaged
- needs_clarification
- ready_for_agent
- in_progress
- fixed
- verified
- rejected

Allowed bug types:
- navigation
- content
- layout
- data
- quiz
- simulation
- accessibility
- performance
- console_error
- other

Export the schema in a browser-safe way. Avoid ES modules if the current project does not already use them. Prefer attaching a namespace to window, such as window.QA_SCHEMA.

Constraints:
- Plain JavaScript only.
- No dependencies.
- Must run under file://.
- Must not break existing app code.
```

---

# Prompt 3 — Create the Shared QA DB Wrapper

## Purpose

Expose a stable API that both the main website and the debug site can use.

## Prompt

```text
Create a browser-safe shared QA database wrapper.

Target file:
qa/qa-db.js

The wrapper must work under file:// and must not require a server.

Use the existing project localDB if one already exists. If the project already has a storage wrapper, adapt this file as a thin compatibility layer over it.

Required namespace:
window.QA_DB

Required methods:
- init()
- getAllPages()
- getPage(which_page)
- registerPage(pageRecord)
- getAllBugs()
- getBug(id)
- createBug(bugRecord)
- updateBug(id, patch)
- deleteBug(id)
- importBugs(bugsArray, options)
- exportState()
- getCurrentSession()
- registerSession(sessionRecord)

Data groups:
- pages
- bugs
- sessions
- exports
- clarifications

Important:
The durable transfer format is exported JSON, not silent filesystem writes.

Storage priority:
1. Existing project localDB if available.
2. IndexedDB if already used by the project.
3. localStorage fallback if acceptable in the current project.
4. In-memory fallback with clear warning state.

The wrapper must expose a capability report:

QA_DB.capabilities = {
  persistent: true or false,
  backend: "existing-localdb" | "indexeddb" | "localstorage" | "memory",
  warnings: []
}

Add defensive error handling. The app must continue functioning even if storage is unavailable.

Constraints:
- Plain JavaScript only.
- No external dependencies.
- No server.
- No filesystem assumptions.
- Must work from file://.
- Must not rewrite the existing storage architecture unless absolutely necessary.
```

---

# Prompt 4 — Register Page Metadata From the Main Site

## Purpose

Make the app self-report page identity and runtime context so the debugger does not need to scan files.

## Prompt

```text
Create a page registration script.

Target file:
qa/qa-page-register.js

Purpose:
Every page in the main site should register its identity into QA_DB when loaded.

Required behavior:
1. Detect the current page path.
2. Detect document.title.
3. Read optional metadata from body data attributes:
   - data-page-id
   - data-module-id
   - data-lesson-id
   - data-app-version
4. Create a session_id if one does not exist.
5. Register a page record into QA_DB.
6. Store the current page record as window.QA_CURRENT_PAGE.

Example body markup:
<body
  data-page-id="lesson-02"
  data-module-id="crm-basics"
  data-lesson-id="lesson-02"
  data-app-version="v0.4"
>

Example output:
{
  which_page: "lessons/lesson-02.html",
  page_id: "lesson-02",
  module_id: "crm-basics",
  lesson_id: "lesson-02",
  page_title: "CRM Navigation Basics",
  app_version: "v0.4",
  session_id: "SESSION-2026-05-22-001",
  registered_at: "2026-05-22T00:00:00.000Z"
}

Path handling:
- Use a stable relative path where possible.
- Avoid absolute machine-specific paths.
- Do not store private local filesystem paths.
- If only location.pathname is available, normalize it to the project-relative path if feasible.

Constraints:
- Plain JavaScript only.
- Must not require page-specific custom code.
- Must not break pages that lack data attributes.
- Must run safely under file://.
```

---

# Prompt 5 — Add Bug Creation API

## Purpose

Allow the main site and debugger to create structured bug reports.

## Prompt

```text
Create a bug API layer.

Target file:
qa/qa-bug-api.js

Required namespace:
window.QA_BUGS

Required methods:
- createFromCurrentPage(input)
- validateBug(input)
- normalizeBug(input)
- markNeedsClarification(id, question)
- markReadyForAgent(id, instructions)
- updateStatus(id, status)
- getEnvironmentInfo()

createFromCurrentPage(input) should:
1. Read window.QA_CURRENT_PAGE if available.
2. Merge page metadata into the bug record.
3. Add browser environment info.
4. Validate required fields.
5. Save through QA_DB.createBug().
6. Return the saved bug.

Required fields:
- title
- severity
- observed
- expected
- steps_to_reproduce
- which_page

If expected behavior is unclear, the bug must be allowed but marked:
status: "needs_clarification"
human_clarification_needed: true

Environment info:
- browser user agent
- viewport width/height
- run mode: file:// or http(s)
- timestamp
- page title
- current URL without exposing private filesystem details where possible

Constraints:
- No dependencies.
- No server.
- No filesystem writes.
- Must work under file://.
- Must not guess expected behavior if missing.
```

---

# Prompt 6 — Build the Debug Site Shell

## Purpose

Create the sidecar local debug website.

## Prompt

```text
Create a static debug website.

Target files:
debug/index.html
debug/debug.css
debug/debug.js

The debug site must load the shared QA files:
../qa/qa-schema.js
../qa/qa-db.js
../qa/qa-bug-api.js
../qa/qa-export-json.js
../qa/qa-import-json.js
../qa/qa-export-md.js

Layout:
- Left/main area: selected bug details, forms, import/export controls
- Right sidebar: structured bug list
- Top bar: project/debugger title and storage capability status
- Filter area: status, severity, page, type
- Empty state: explain that no bugs are loaded yet

Right sidebar bug list:
- Group by status or page
- Show severity
- Show title
- Show which_page
- Show clarification badge if needed

Bug detail panel:
- ID
- title
- severity
- status
- bug_type
- which_page
- observed
- expected
- steps_to_reproduce
- agent_instructions
- clarification_question
- created_at
- updated_at

Actions:
- Create bug
- Edit selected bug
- Delete selected bug
- Mark needs clarification
- Mark ready for agent
- Export JSON
- Import JSON
- Export Markdown

Constraints:
- Plain HTML/CSS/JS only.
- No external CSS frameworks.
- No CDN.
- No build tools.
- Must open directly from file://.
- Must not assume it can read project files.
```

---

# Prompt 7 — Create JSON Export

## Purpose

Make JSON the durable transfer artifact between tester and developer.

## Prompt

```text
Create the JSON export module.

Target file:
qa/qa-export-json.js

Required namespace:
window.QA_EXPORT_JSON

Required methods:
- buildExportPayload(options)
- downloadJSON(filename, payload)
- exportAllBugs()
- exportFilteredBugs(filter)

Payload format:
{
  schemaVersion: "qa-bug-report-v1",
  exportedAt: "2026-05-22T00:00:00.000Z",
  project: {
    name: "QA Onboarding Training Platform",
    version: "v0.4",
    runMode: "file://"
  },
  source: {
    generatedBy: "Local QA Debugger",
    storageBackend: "existing-localdb",
    persistent: true
  },
  bugs: [],
  pages: [],
  sessions: []
}

downloadJSON should create a Blob and trigger a browser download.

Filename format:
qa-bugs-YYYY-MM-DD-HHMM.json

Constraints:
- No filesystem writes.
- Use browser download only.
- Must work under file://.
- No dependencies.
```

---

# Prompt 8 — Create JSON Import

## Purpose

Allow a developer to import bug reports from another local copy.

## Prompt

```text
Create the JSON import module.

Target file:
qa/qa-import-json.js

Required namespace:
window.QA_IMPORT_JSON

Required methods:
- parseImportedFile(file)
- validatePayload(payload)
- importPayload(payload, options)
- mergeBugs(existingBugs, importedBugs, options)

Import behavior:
- User selects JSON file manually with <input type="file">
- Parse JSON safely
- Validate schemaVersion
- Validate bugs array
- Merge bugs into QA_DB
- Avoid duplicate IDs
- If duplicate ID exists, preserve the newest updated_at unless options.overwrite is true
- Return import summary

Import summary:
{
  imported: 0,
  skipped: 0,
  updated: 0,
  errors: []
}

Constraints:
- No silent filesystem reads.
- No dependencies.
- Must work from file://.
- Must not erase existing bugs unless explicitly requested.
```

---

# Prompt 9 — Create Agent-Ready Markdown Export

## Purpose

Generate a Markdown handoff that can be fed to a local coding agent.

## Prompt

```text
Create the Markdown export module.

Target file:
qa/qa-export-md.js

Required namespace:
window.QA_EXPORT_MD

Required methods:
- buildMarkdown(payloadOrBugs, options)
- downloadMarkdown(filename, markdown)
- exportAllBugsMarkdown()
- exportReadyForAgentMarkdown()
- exportNeedsClarificationMarkdown()

The Markdown must be structured for an agentic AI working under strict project constraints.

Required Markdown sections:
1. Title
2. Project constraints
3. Human-in-the-loop rule
4. Bug summary table
5. Bugs ready for agent
6. Bugs needing clarification
7. Bugs not ready for work
8. Per-bug details
9. Explicit instructions not to guess unclear behavior

Required language:
- If expected behavior is unclear, mark NEEDS_CLARIFICATION.
- Do not invent missing requirements.
- Do not add dependencies.
- Do not require a server.
- Do not break file:// execution.
- Prefer isolated fixes.
- Modify shared logic only when the bug proves the shared logic is defective.

Example per-bug format:

## BUG-2026-05-22-001 — Next button does not advance from Lesson 02

Severity: High  
Status: Ready for Agent  
Page: `lessons/lesson-02.html`  
Type: Navigation  

### Observed
Clicking the Next button does nothing.

### Expected
The user should advance to Lesson 03.

### Steps to Reproduce
1. Open `lessons/lesson-02.html`
2. Complete the lesson quiz
3. Click the Next button

### Agent Instructions
Inspect the navigation handler for `lesson-02.html`. Verify that the target path exists before modifying shared navigation logic.

### Constraints
- No external dependencies.
- No server.
- Must run under `file://`.
- Do not modify unrelated lesson behavior.

Constraints:
- Plain JavaScript only.
- Browser download using Blob.
- No filesystem writes.
- Must work under file://.
```

---

# Prompt 10 — Add Optional On-Page Bug Button

## Purpose

Let testers file bugs from the page they are testing.

## Prompt

```text
Add an optional on-page bug filing widget.

Target file:
qa/qa-bug-widget.js

Purpose:
When included on a page, this widget adds a small "Report Bug" button that opens a local modal form.

Required behavior:
- Button should be unobtrusive.
- Modal form should collect:
  - title
  - severity
  - bug_type
  - observed
  - expected
  - steps_to_reproduce
  - agent_instructions
  - human_clarification_needed
  - clarification_question
- On submit, call QA_BUGS.createFromCurrentPage().
- Show success/failure message.
- Do not block normal page behavior.
- Allow the widget to be disabled by setting:
  window.QA_BUG_WIDGET_DISABLED = true

Constraints:
- No dependencies.
- No external CSS.
- Must work under file://.
- Must not break existing page layout.
- Must be optional.
```

---

# Prompt 11 — Integrate Scripts Safely Into Existing Pages

## Purpose

Wire the QA layer into the main site without breaking working pages.

## Prompt

```text
Integrate the QA scripts into the existing static site.

Task:
Add these scripts to main pages in the safest location, preferably before closing </body>:

<script src="./qa/qa-schema.js"></script>
<script src="./qa/qa-db.js"></script>
<script src="./qa/qa-page-register.js"></script>
<script src="./qa/qa-bug-api.js"></script>

If a page is inside a subfolder, adjust relative paths correctly:

<script src="../qa/qa-schema.js"></script>
<script src="../qa/qa-db.js"></script>
<script src="../qa/qa-page-register.js"></script>
<script src="../qa/qa-bug-api.js"></script>

Optional widget:
<script src="./qa/qa-bug-widget.js"></script>

Add body data attributes where useful:
<body
  data-page-id="lesson-02"
  data-module-id="crm-basics"
  data-lesson-id="lesson-02"
  data-app-version="v0.4"
>

Rules:
- Do not rewrite pages unnecessarily.
- Do not change existing lesson logic.
- Do not change existing CSS unless needed for the optional widget.
- Use correct relative paths.
- If unsure about a page, skip it and report it.
- Preserve file:// compatibility.
```

---

# Prompt 12 — Build Debug Filters and Right Sidebar

## Purpose

Make the debugger useful as a triage console.

## Prompt

```text
Implement the debug sidebar and filters.

Target files:
debug/debug-panel.js
debug/debug-filters.js
debug/debug.js

Required filters:
- status
- severity
- bug_type
- which_page
- text search

Required group modes:
- group by status
- group by page
- group by severity
- flat list

Each bug row should show:
- severity
- status
- title
- which_page
- clarification badge if human_clarification_needed is true

Selection behavior:
- Clicking a bug opens its full details in the main panel.
- Editing a bug updates QA_DB.
- Deleting a bug asks for confirmation.
- Status changes update the list immediately.

Constraints:
- No dependencies.
- Keep DOM code simple.
- Must run under file://.
```

---

# Prompt 13 — Add Human-in-the-Loop Clarification Workflow

## Purpose

Prevent agents from guessing ambiguous intent.

## Prompt

```text
Implement the clarification workflow.

Requirements:
A bug can be marked as needing clarification when:
- expected behavior is empty
- reproduction steps are missing
- observed behavior is vague
- the fix would require a product/design decision
- the report conflicts with existing app behavior
- the agent instructions are unclear

Add UI actions:
- Mark Needs Clarification
- Add Clarification Question
- Mark Ready for Agent
- Reject Bug
- Verify Fixed

When marked needs clarification:
status = "needs_clarification"
human_clarification_needed = true
clarification_question = user-provided question

When marked ready:
status = "ready_for_agent"
human_clarification_needed = false

Markdown export must separate:
- Ready for Agent
- Needs Clarification
- Not Ready

Never include needs-clarification bugs in the "fix now" section.

Constraints:
- No guessing missing expected behavior.
- No hidden assumptions.
- Human remains final authority.
```

---

# Prompt 14 — Add Import/Export UI Wiring

## Purpose

Connect the JSON and Markdown modules to the debugger UI.

## Prompt

```text
Wire import/export controls in debug/index.html and debug/debug-import-export.js.

Required controls:
- Export All Bugs as JSON
- Export Filtered Bugs as JSON
- Import Bugs from JSON
- Export All Bugs as Markdown
- Export Ready-for-Agent Bugs as Markdown
- Export Needs-Clarification Bugs as Markdown

Import flow:
1. User clicks Import JSON.
2. Browser file picker opens.
3. User selects JSON.
4. App validates payload.
5. App merges bugs.
6. App displays import summary.
7. Sidebar refreshes.

Export flow:
1. User clicks export.
2. App builds payload or Markdown.
3. App triggers Blob download.
4. App shows success message.

Constraints:
- No silent reads/writes.
- No server.
- No dependencies.
- Must work under file://.
```

---

# Prompt 15 — Create a Manual Test Plan

## Purpose

Verify the debugger under the real constraints.

## Prompt

```text
Create a manual test plan for the local QA debugger.

Target file:
debug/TEST-PLAN.md

Include tests for:

1. Opening debug/index.html directly from file://
2. Opening main site pages directly from file://
3. Page metadata registration
4. Bug creation from debugger
5. Bug creation from optional page widget
6. Bug editing
7. Bug deletion
8. Status changes
9. Needs clarification workflow
10. Ready for agent workflow
11. JSON export
12. JSON import into a fresh copy
13. Markdown export
14. Browser storage unavailable fallback
15. Relative path correctness from nested lesson pages
16. No dependency/no server verification
17. Regression check that existing training pages still work

For each test include:
- Test name
- Steps
- Expected result
- Pass/fail checkbox
- Notes

Constraints:
- Manual testing only.
- No test framework.
- No install.
```

---

# Prompt 16 — Create Developer Handoff Documentation

## Purpose

Document how the system works for future agents and developers.

## Prompt

```text
Create documentation for the local QA debugger.

Target file:
debug/README.md

Include:

1. What this debugger is
2. Why it exists
3. Why it does not scan the filesystem
4. How it works under file://
5. How page metadata is registered
6. How bugs are stored
7. How JSON export/import works
8. How Markdown handoff works
9. How the human-in-the-loop clarification workflow works
10. How to add the bug widget to a page
11. How to remove/disable the bug widget
12. Known browser limitations
13. Troubleshooting
14. Future improvements

Important wording:
The debugger does not bypass file:// restrictions by being in the same folder. It works because the main app and debugger use the same structured local data layer.

Constraints:
- Be clear and direct.
- Do not claim unrestricted filesystem access.
- Do not require a server.
```

---

# Prompt 17 — Final Integration Review

## Purpose

Have the agent inspect its own work before handing control back to the human.

## Prompt

```text
Review the completed local QA debugger implementation.

Check:

Architecture:
- Does the debugger run from file://?
- Does it avoid unrestricted filesystem assumptions?
- Does it use the shared localDB wrapper?
- Does JSON export act as the durable transfer format?
- Does Markdown export act as the agent handoff format?

Schema:
- Are page records implemented?
- Are bug records implemented?
- Is which_page present and populated?
- Are statuses and severities constrained?
- Is needs clarification represented clearly?

UI:
- Does debug/index.html load?
- Does the right sidebar show structured bugs?
- Can bugs be filtered?
- Can bugs be edited?
- Can bugs be imported/exported?

Safety:
- Are unclear bugs marked NEEDS_CLARIFICATION?
- Does the agent handoff tell agents not to guess?
- Are shared logic changes discouraged unless proven necessary?
- Are existing site pages preserved?

Constraints:
- No dependencies added.
- No server required.
- No build step added.
- No external CDN.
- No internet required.

Output:
- Summary of what was implemented.
- Files changed.
- Known limitations.
- Manual tests performed.
- Any items requiring human decision.
```

---

# Recommended Build Order

Use the prompts in this order:

```text
1. Audit storage layer
2. Define QA schema
3. Create QA DB wrapper
4. Register page metadata
5. Add bug creation API
6. Build debug site shell
7. Add JSON export
8. Add JSON import
9. Add Markdown export
10. Add optional page bug widget
11. Integrate scripts into pages
12. Build sidebar and filters
13. Add clarification workflow
14. Wire import/export UI
15. Create manual test plan
16. Create README
17. Final integration review
```

---

# Minimal MVP Cut

If you want the smallest working version first, use only these prompts:

```text
1. Audit storage layer
2. Define QA schema
3. Create QA DB wrapper
4. Register page metadata
5. Build debug site shell
7. Add JSON export
8. Add JSON import
9. Add Markdown export
13. Add clarification workflow
17. Final integration review
```

Skip the optional on-page widget until the debugger UI is stable.

---

# MVP Acceptance Criteria

The MVP is complete when:

```text
- debug/index.html opens directly from file://
- The debugger can create a bug manually
- The bug includes which_page
- Bugs persist through the existing localDB layer or safe fallback
- Bugs appear in a right-side structured list
- Bugs can be marked needs_clarification
- Bugs can be marked ready_for_agent
- Bugs export to JSON
- JSON can be imported into another copy
- Bugs export to agent-ready Markdown
- The Markdown tells the agent not to guess unclear behavior
- Existing site pages still work
```

---

# Future Upgrade Ideas

Keep these out of MVP unless the base system is stable.

```text
- Console error capture
- Screenshot filename tracking
- DOM element selector capture
- Viewport/device preset capture
- Repro session timeline
- Bug deduplication
- Bug templates by type
- Agent fix status import
- Patch review checklist
- Local changelog export
- QA run summaries
- Test case linkage
- Lesson/module coverage map
```

---

# Design Principle

The debugger should not be a fake server, a filesystem crawler, or an installable app.

It should be a static local QA console over structured app truth.

```text
App state in localDB
  → Debugger UI
  → JSON artifact
  → Markdown agent handoff
  → Human clarification gate
  → Fix
  → Verify
```
