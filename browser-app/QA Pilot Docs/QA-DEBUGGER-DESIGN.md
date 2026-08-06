# QA Debugger — Design Document
## Adapting `local-qa-debugger-prompt-pack.md` to QA-Pilot's Actual Structure

**Date:** 2026-05-22  
**Status:** Design / Evaluation  
**Scope:** MVP sidecar debugger for QA-Pilot  

---

## 1. Executive Summary

The prompt pack specifies a generic static-site debugger. QA-Pilot is **not** a generic static site — it is a multi-layered training platform with:

- A custom IndexedDB layer (`js/db.js`) with 6 object stores
- A desktop OS simulator with 15+ iframe-hosted apps
- Multi-course training with dynamic content loading
- Capstone assessment labs with complex scoring
- Admin dashboard with per-student bug configuration
- A build system (`build.js` / `build.sh`) that bundles for `file://`

**The closest viable implementation** reuses the prompt pack's architectural principles (shared local data layer, structured bug reports, JSON/Markdown export, human-in-the-loop clarification) but adapts every integration point to QA-Pilot's actual pages, storage, and iframe hierarchy.

---

## 2. Gap Analysis: Prompt Pack Assumptions vs. QA-Pilot Reality

| Prompt Pack Assumes | QA-Pilot Reality | Adaptation Required |
|---|---|---|
| `lessons/lesson-01.html` flat structure | `portal.html` → `course-view.html` → iframes; `desktop/dist.html` → `apps/*.html` | Page registration must handle top-level, course-view, capstone, admin, and OS app contexts |
| Generic `localDB` abstraction | `js/db.js` with `qa_onboarding_db` (v2), 6 stores, async Promise API | Extend existing DB with new `debuggerBugs` store **or** create separate `QAPilotDebugger` DB |
| Simple static pages with `<body data-page-id>` | Dynamic content: course-view loads modules via JS; OS apps boot via `APP_BOOT` postMessage | Page registration script must detect context from URL params, parent window, and postMessage data |
| No build step | `build.js` / `build.sh` bundles `os.bundle.js`, `desktop/dist.html`, `capstone-2.html` | Debugger files excluded from bundle; debug site is standalone; widget script optionally injected into bundle output |
| Pages in subfolders use `../qa/` | QA-Pilot has pages at root, `apps/`, `admin/`, `desktop/`, `scenarios/` | Multi-path script inclusion logic |
| One app version | Multiple "apps" inside OS desktop + standalone pages | `app_context` field in page records distinguishes `os-desktop`, `dynamics`, `ado`, `course-view`, etc. |

---

## 3. Storage Integration Strategy

### Option A: Extend Existing DB (Recommended)

Add a new object store `debuggerBugs` to the existing `qa_onboarding_db` by bumping `DB_VERSION` from 2 → 3.

**Pros:**
- Single database = atomic backups, single cleanup path
- Debugger can cross-reference student records (e.g., bug filed by which student)
- Admin dashboard could eventually show debugger data

**Cons:**
- Requires modifying `js/db.js` (touched by many features, high blast radius)
- DB version bump triggers `onupgradeneeded` for all users

**Mitigation:**
- Add store creation defensively (check `contains()` first, as existing pattern does)
- Do NOT remove or modify existing stores
- Add only: `debuggerBugs`, `debuggerPages`, `debuggerSessions`

### Option B: Separate Debugger DB (Safer)

Create `QAPilotDebugger` as a second IndexedDB with its own version.

**Pros:**
- Zero risk to existing `js/db.js`
- Independent versioning
- Can be deleted/cleared without affecting student data

**Cons:**
- Two DBs to manage
- Cannot easily join with student records

### Decision: Option B for MVP, migrate to Option A later

For the MVP, use **Option B** (separate DB) to guarantee zero regression. The `qa-db.js` wrapper can abstract this away — if we later want to migrate to Option A, only `qa-db.js` changes.

**`qa-db.js` wrapper capabilities:**
```javascript
window.QA_DB = {
  capabilities: {
    persistent: true,
    backend: "indexeddb",
    dbName: "QAPilotDebugger",
    warnings: []
  },
  init() { /* opens QAPilotDebugger, creates stores */ },
  getAllBugs() { /* returns Promise<Array> */ },
  createBug(record) { /* saves to debuggerBugs store */ },
  // ... etc
};
```

---

## 4. Page Registration Mapping

### QA-Pilot Page Inventory

| Page | Path | Context Type | Registration Strategy |
|---|---|---|---|
| Login | `index.html` | `standalone` | Direct `<script>` + body data attrs |
| Portal | `portal.html` | `standalone` | Direct `<script>` + body data attrs |
| Course Viewer | `course-view.html` | `training` | Direct `<script>` + reads `?course=` param |
| Capstone 1 | `capstone-lab.html` | `assessment` | Direct `<script>` + body data attrs |
| Capstone 2 | `capstone-2.html` | `assessment` | Direct `<script>` + body data attrs |
| Certificate | `certificate.html` | `standalone` | Direct `<script>` + body data attrs |
| Admin Dashboard | `admin/dashboard.html` | `admin` | Direct `<script>` + `../qa/` paths |
| Admin Bugs | `admin/bugs.html` | `admin` | Direct `<script>` + `../qa/` paths |
| Admin Editor | `admin/editor.html` | `admin` | Direct `<script>` + `../qa/` paths |
| Admin Assign | `admin/assign.html` | `admin` | Direct `<script>` + `../qa/` paths |
| OS Desktop | `desktop/dist.html` | `os-desktop` | **Inside OS iframe** — registration via `os-core.js` or `window.parent` proxy |
| Dynamics | `apps/dynamics.html` | `os-app` | Loaded inside OS iframe; register via `window.parent` or skip |
| ADO | `apps/ado.html` | `os-app` | Loaded inside OS iframe; register via `window.parent` or skip |
| Teams | `apps/teams.html` | `os-app` | Loaded inside OS iframe; register via `window.parent` or skip |
| Browser | `apps/browser.html` | `os-app` | Loaded inside OS iframe; register via `window.parent` or skip |
| Outlook | `apps/qoutlook.html` | `os-app` | Loaded inside OS iframe; register via `window.parent` or skip |
| Training | `apps/training.html` | `os-app` | Loaded inside OS iframe; register via `window.parent` or skip |
| Reports | `apps/reports.html` | `os-app` | Loaded inside OS iframe; register via `window.parent` or skip |

### Practical Decision

**MVP scope:** Register only top-level pages + course-view + capstones + admin pages. **Skip OS iframe apps for MVP** — they are too deeply nested and the prompt pack's widget would be intrusive inside the simulator. A bug in an OS app can be filed from the OS desktop level or from the debugger directly by selecting the app context.

### Page Record Shape (Adapted)

```javascript
{
  which_page: "course-view.html?course=qa-onboarding-advanced",
  page_id: "course-view",
  module_id: "qa-onboarding-advanced",      // from URL param
  page_title: "QA Onboarding Advanced — Course Viewer",
  app_version: "v2.0",                      // from data attr or hardcoded
  session_id: "SESSION-2026-05-22-001",     // from session/caseId
  app_context: "training",                    // standalone | training | assessment | admin | os-desktop
  registered_at: "2026-05-22T00:00:00.000Z"
}
```

---

## 5. Adapted File Structure

The prompt pack suggests `qa/` and `debug/` at project root. This maps cleanly to QA-Pilot:

```text
QA Pilot/
  index.html
  portal.html
  course-view.html
  capstone-lab.html
  capstone-2.html
  certificate.html
  js/
    db.js                          ← existing (DO NOT TOUCH per rules)
    app.js                         ← existing (DO NOT TOUCH per rules)
  data/
    content.js                     ← existing
    bug-keys.js                    ← existing
  admin/
    dashboard.html                 ← add script tags
    bugs.html                      ← add script tags
    editor.html                    ← add script tags
    assign.html                    ← add script tags
  apps/                            ← SKIP for MVP (iframe apps)
  desktop/
    dist.html                      ← add script tags (top-level OS desktop)
  qa/                              ← NEW
    qa-schema.js
    qa-db.js
    qa-page-register.js
    qa-bug-api.js
    qa-export-json.js
    qa-import-json.js
    qa-export-md.js
    qa-bug-widget.js              ← optional, disabled by default
  debug/                           ← NEW
    index.html
    debug.css
    debug.js
    debug-panel.js
    debug-filters.js
    debug-import-export.js
  bug-reports/                     ← NEW
    README.md
```

---

## 6. MVP Build Plan (Adapted for QA-Pilot)

Based on the prompt pack's "Minimal MVP Cut" (Prompts 1, 2, 3, 4, 5, 7, 8, 9, 13, 17) adapted to our reality.

### Phase 1: Foundation (No UI yet)

| Step | File(s) | Task | Integration Point |
|---|---|---|---|
| 1.1 | `js/db.js` (read-only audit) | Confirm IndexedDB shape, version, stores | Audit only |
| 1.2 | `qa/qa-schema.js` | Define `PageRecord`, `BugRecord`, `SessionRecord`, `ExportPayload` shapes with `app_context` field | Standalone |
| 1.3 | `qa/qa-db.js` | Create `QAPilotDebugger` IndexedDB with `debuggerBugs`, `debuggerPages`, `debuggerSessions` stores. Wrap with `window.QA_DB` namespace. Use existing `_get`/`_put`/`_getAll` pattern from `js/db.js` | Standalone |
| 1.4 | `qa/qa-page-register.js` | Auto-detect page path, URL params (`?course=`, `?caseId=`), `document.title`, `data-*` attrs. Write to `debuggerPages`. Set `window.QA_CURRENT_PAGE` | Included in portal, course-view, capstones, admin pages |
| 1.5 | `qa/qa-bug-api.js` | `window.QA_BUGS` namespace. `createFromCurrentPage()` merges `QA_CURRENT_PAGE` + env info + validates. `markNeedsClarification()`, `markReadyForAgent()`, `updateStatus()` | Standalone |

### Phase 2: Debug Site Shell

| Step | File(s) | Task | Notes |
|---|---|---|---|
| 2.1 | `debug/index.html` | Static HTML shell: top bar, left detail panel, right sidebar, filter bar | Loads `../qa/*.js` |
| 2.2 | `debug/debug.css` | Professional styling matching QA-Pilot palette (blue #2563eb, purple #7c3aed, 2px borders) | Reuse existing CSS vars if possible |
| 2.3 | `debug/debug.js` | Init, load data, render sidebar, handle selection | Uses `QA_DB` namespace |
| 2.4 | `debug/debug-panel.js` | Bug detail view, edit form, status actions | Form validation, confirmation dialogs |
| 2.5 | `debug/debug-filters.js` | Filter by status, severity, app_context, which_page, text search | Real-time list update |

### Phase 3: Import / Export

| Step | File(s) | Task | Notes |
|---|---|---|---|
| 3.1 | `qa/qa-export-json.js` | `window.QA_EXPORT_JSON`. Build payload with `schemaVersion: "qa-bug-report-v1"`, project metadata, bugs array. Blob download. | Filename: `qa-bugs-YYYY-MM-DD-HHMM.json` |
| 3.2 | `qa/qa-import-json.js` | `window.QA_IMPORT_JSON`. File picker, parse, validate schemaVersion, merge with dedup logic (preserve newest `updated_at`). Return import summary. | Never auto-overwrite without opt-in |
| 3.3 | `qa/qa-export-md.js` | `window.QA_EXPORT_MD`. Generate agent-ready Markdown with constraints preamble, bug summary table, ready-for-agent section, needs-clarification section, per-bug details with explicit "do not guess" instructions. | This is the handoff artifact for agents like me |
| 3.4 | `debug/debug-import-export.js` | Wire UI buttons to export/import modules. Show success/error messages. | Blob download / file input |

### Phase 4: Clarification Workflow

| Step | File(s) | Task | Notes |
|---|---|---|---|
| 4.1 | `debug/debug-panel.js` | Add action buttons: "Mark Needs Clarification", "Add Question", "Mark Ready for Agent", "Reject Bug", "Verify Fixed" | Updates `QA_DB` and refreshes list |
| 4.2 | `qa/qa-bug-api.js` | Validation rules: if `expected` empty or `steps_to_reproduce` empty → auto-flag `needs_clarification` | Prevent vague bugs from reaching agent |

### Phase 5: Integration & Test

| Step | File(s) | Task | Notes |
|---|---|---|---|
| 5.1 | `index.html`, `portal.html`, `course-view.html`, `capstone-lab.html`, `capstone-2.html`, `certificate.html` | Add `<script src="./qa/qa-schema.js"></script>` etc. before `</body>` | Use correct relative path |
| 5.2 | `admin/dashboard.html`, `admin/bugs.html`, `admin/editor.html`, `admin/assign.html` | Add `<script src="../qa/qa-schema.js"></script>` etc. | `../qa/` from `admin/` subfolder |
| 5.3 | `desktop/dist.html` | Add script tags to OS desktop shell | OS desktop is a top-level page |
| 5.4 | `debug/TEST-PLAN.md` | Manual test plan: file:// open, bug create, edit, export, import, Markdown export, regression check on existing pages | No test framework |
| 5.5 | `bug-reports/README.md` | Explain the folder, the JSON/Markdown workflow, and the human-in-the-loop rule | Documentation |

### Phase 6: Optional Widget (Post-MVP)

| Step | File(s) | Task | Notes |
|---|---|---|---|
| 6.1 | `qa/qa-bug-widget.js` | Floating "Report Bug" button + modal form. Disabled by `window.QA_BUG_WIDGET_DISABLED = true`. | Only on select pages |

---

## 7. Critical Adaptations for QA-Pilot

### 7.1 Build System Exclusion

`build.js` bundles source files into `desktop/dist.html` and `QASimulator.html`. The debugger is **not** part of the OS bundle — it is a standalone sidecar. The `qa/` scripts should:

- **Not** be referenced in `build.js`
- **Not** be bundled into `os.bundle.js`
- Be loaded directly via `<script src="...">` in pages that need them

### 7.2 `js/db.js` Touch Rule

Per `CLAUDE.md`: **"Never touch `js/db.js` or `js/app.js` without explicit instruction"**

For the MVP, we **honor this rule** by using a separate `QAPilotDebugger` IndexedDB. If Andrew later wants unified storage, we can add a `debuggerBugs` store to `qa_onboarding_db` v3 in a dedicated migration session.

### 7.3 Iframe Hierarchy

QA-Pilot has iframes within iframes:

```
portal.html
  → course-view.html (iframe)
    → capstone-lab.html (iframe)
    → capstone-2.html (iframe)

desktop/dist.html
  → apps/dynamics.html (iframe)
  → apps/ado.html (iframe)
  → apps/teams.html (iframe)
```

The prompt pack assumes a flat structure. Our adapted approach:

- **Top-level pages** (portal, course-view, capstone-lab, capstone-2, desktop/dist) register themselves directly
- **Nested iframes** (apps inside desktop) are skipped for MVP — a bug in Teams can be filed by:
  1. Tester notes the app context manually in the debugger
  2. Or: OS desktop registers as `app_context: "os-desktop"` and tester selects `os-app: teams` in the bug form
- **Course-view iframe** (capstone inside course-view) registers as its own page because it loads as a separate HTML document with its own URL

### 7.4 Session ID Strategy

QA-Pilot already has `caseId` (student identifier, e.g., `CASE-00001`). The debugger should reuse this as the session anchor rather than generating a separate session ID:

```javascript
// qa-page-register.js
var sessionId = (window.currentSession && window.currentSession.caseId) 
                || (window.parent && window.parent.currentSession && window.parent.currentSession.caseId)
                || "anonymous-" + Date.now();
```

This links bugs to actual student records if available.

### 7.5 URL Param Awareness

QA-Pilot pages carry state in URL params:
- `course-view.html?course=qa-onboarding-advanced`
- `capstone-2.html?courseId=capstone-2`
- `certificate.html?course=qa-onboarding&confetti=true`
- `admin/dashboard.html?tab=students`

The page registration script must capture these params in `which_page` so bugs are traceable to the exact runtime context.

---

## 8. Expansion Roadmap (Post-MVP)

| Feature | Description | Complexity |
|---|---|---|
| **Console Error Capture** | Auto-catch `window.onerror` and `console.error`, file as bug with stack trace | Low |
| **Screenshot Filename Tracking** | Prompt tester for screenshot filename, store in `evidence` array | Low |
| **OS App Bug Proxy** | `os-core.js` forwards bug reports from iframe apps to top-level debugger store | Medium |
| **Student-linked Bugs** | Cross-reference `caseId` with student record; show student name in debugger | Medium |
| **Bug Templates** | Pre-fill bug forms based on `bug_type` (e.g., "navigation" template) | Low |
| **Course Coverage Map** | Visual map of which pages/modules have filed bugs vs. no bugs | Medium |
| **Agent Fix Status Import** | Import a JSON from an agent that marks bugs as `fixed` with notes | Medium |
| **Admin Dashboard Integration** | Show "Debugger Active" badge, bug count per student in admin UI | High |
| **Capstone Scoring Link** | Link debugger bugs to capstone scoring rubric items | High |
| **Regression Test Link** | Export a list of bugs as a checklist for manual regression testing | Low |

---

## 9. Risk Assessment & Gotchas

| Risk | Likelihood | Mitigation |
|---|---|---|
| Separate DB = bugs not visible to admin dashboard | High | Accept for MVP; future migration to unified DB |
| Script tags break `file://` on some pages | Medium | Test all pages after integration; use relative paths carefully |
| OS iframe apps can't reach parent IndexedDB | Medium | Skip for MVP; document limitation |
| `build.js` accidentally includes qa/ files | Low | Explicitly exclude in build.js logic (or just don't reference them in source) |
| Storage quota exceeded on old machines | Low | In-memory fallback in `qa-db.js` with warning banner |
| Debugger CSS conflicts with QA-Pilot styling | Low | Use `qd-` prefix for all debugger CSS classes; scoped to debug/ pages only |

---

## 10. Decision Required

Before building, Andrew needs to decide:

1. **MVP scope confirmation** — Do we build the full 6-phase plan, or cut further?
2. **Widget inclusion** — Include the optional on-page bug widget in MVP, or defer to Phase 6?
3. **DB strategy** — Stick with separate `QAPilotDebugger` DB (safe), or extend `qa_onboarding_db` (unified but touches `js/db.js`)?
4. **Pages to instrument** — All top-level pages, or start with a subset (e.g., just `portal.html`, `course-view.html`, `capstone-lab.html`)?
5. **Build integration** — Should `build.sh` copy `qa/` and `debug/` to the `desktop/` folder for distribution, or are they developer-only tools?

---

## Appendix A: Example Bug Record for QA-Pilot

```javascript
{
  id: "BUG-2026-05-22-001",
  title: "Capstone 2 scoring ignores ADO bugs with AC-C2-001 format",
  severity: "high",
  status: "ready_for_agent",
  bug_type: "simulation",
  which_page: "capstone-2.html?courseId=capstone-2",
  page_id: "capstone-2",
  module_id: "capstone-2",
  page_title: "Capstone 2 Assessment",
  app_version: "v2.0",
  session_id: "CASE-00001",
  app_context: "assessment",
  observed: "Filing a bug with AC reference 'AC-C2-001-3' in ADO does not count toward capstone score.",
  expected: "AC references matching the SCENARIO_C2 rubric should be recognized by the scoring engine.",
  steps_to_reproduce: [
    "Open capstone-2.html with case-002 scenario",
    "Log into Dynamics and file a bug with AC reference 'AC-C2-001-3'",
    "Submit capstone",
    "Observe score shows 0/8 for this rubric item"
  ],
  environment: {
    browser: "Chrome 136",
    run_mode: "file://",
    viewport: "1440x900",
    os_app: "ado"
  },
  evidence: ["screenshot-ado-ac-ref.png"],
  human_clarification_needed: false,
  clarification_question: "",
  agent_instructions: "Inspect scoreCapstone2() in os-core.js and the AC reference regex in apps/ado.html. Verify the regex handles the 'AC-C2-001-3' format.",
  created_by: "tester",
  created_at: "2026-05-22T10:30:00.000Z",
  updated_at: "2026-05-22T10:30:00.000Z"
}
```

---

## Appendix B: Example Markdown Export Snippet

```markdown
# QA-Pilot Bug Report — Agent Handoff

## Project Constraints
- Must run under `file://`
- No external dependencies
- No server required
- Do not modify `js/db.js` or `js/app.js` without explicit approval
- Prefer isolated fixes; modify shared logic only when proven defective

## Human-in-the-Loop Rule
If expected behavior is unclear, the agent must STOP and mark the bug as NEEDS_CLARIFICATION.  
Do not invent missing requirements. Do not guess.

---

## Ready for Agent (2 bugs)

### BUG-2026-05-22-001 — Capstone 2 scoring ignores ADO bugs with AC-C2-001 format
**Severity:** High | **Status:** Ready for Agent | **Page:** `capstone-2.html?courseId=capstone-2`

#### Observed
Filing a bug with AC reference 'AC-C2-001-3' in ADO does not count toward capstone score.

#### Expected
AC references matching the SCENARIO_C2 rubric should be recognized by the scoring engine.

#### Agent Instructions
Inspect scoreCapstone2() in os-core.js and the AC reference regex in apps/ado.html.

#### Constraints
- No external dependencies.
- No server.
- Must run under `file://`.
- Do not modify unrelated capstone scoring behavior.

---

## Needs Clarification (1 bug)

### BUG-2026-05-22-002 — Course viewer quiz intro missing for module 3
**Severity:** Medium | **Status:** Needs Clarification | **Page:** `course-view.html?course=qa-onboarding-advanced`

**Question for human:** Should every module show its own quiz intro screen, or only modules with quizzes? Module 3 is an overview page with no quiz.
```

---

*End of design document*
