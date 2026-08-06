# QA-PILOT-SOURCE-OF-TRUTH-RECONCILIATION-1

**Sprint:** QA-PILOT-SOURCE-OF-TRUTH-RECONCILIATION-1
**Type:** Source-correction / reconciliation (research + planning)
**Status:** 🔍 Pending — Owner decision required before implementation
**Created:** 2026-07-10
**Agent:** OpenWork (glm-5.2)
**Boundary:** Read-only inspection of both QA Pilot sources. No mutations performed.

---

## 1. Exact Paths Inspected

| # | Path | Role | Access |
|---|------|------|--------|
| 1 | `/Users/andrew/Desktop/OpenWork/QA Pilot` | Complete QA Pilot source | Read-only |
| 2 | `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot` | Incomplete CarbideFrame QA Pilot | Read-only |
| 3 | `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot/docs/schemas/browser-assets/` | CarbideFrame browser training platform | Read-only |
| 4 | `/Users/andrew/Desktop/CarbideFrame/active/librarian/Public/` | Librarian frontend (design reference only) | Not accessed this sprint |

---

## 2. Which Project Is Complete

**The complete project is at `/Users/andrew/Desktop/OpenWork/QA Pilot`.**

It is a fully functional, offline, bilingual (EN/FR) QA onboarding training platform with two integrated halves:

### Academy Half (lesson platform)
- Student login with PBKDF2 password hashing via Web Crypto API
- Multi-course enrollment (4 courses: QA Onboarding, Agile & Scrum, QA Onboarding Advanced, Capstone 2)
- Sequential module/quiz flow with progress tracking
- Course portal, lesson viewer, capstone assessment, certificate generation
- IndexedDB-backed student records, progress, and settings
- Admin dashboard for student management, bug lab, content editor, assignment

### Desktop OS Half (Windows 11-style simulator)
- Boot screen, lock screen, taskbar, start menu
- Draggable/snappable windows, virtual workspaces
- 12 simulated apps: Dynamics 365 CRM, Azure DevOps, Teams, Browser, Outlook, QTube, QApache, Reports, Inspector, Acceptance Criteria, Training, Settings
- 6 scenario files with case state, expected bugs, and AC references
- Scenario scoring engine, health checks, keyboard shortcuts
- Build system (`build.js`) producing self-contained `QASimulator.html`

### Additional subsystems
- QA module (9 files): IndexedDB queries, JSON/MD export, import, page registry, schema, templates, work-item API
- Debug panel (7 files): debug board, filters, import/export, panel, CSS
- Chrome extension: FlightPlan prompt helper
- Desktop launcher scripts (Windows + macOS)
- Clippy guide, PDF library

**Total: 124 files, ~75,000+ lines of code**

---

## 3. Which Project Is Incomplete

**The incomplete project is at `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot`.**

It is a **Python/script-based QA governance framework** (advisory-only) with a **secondary static browser training platform** stored as reference assets under `docs/schemas/browser-assets/`.

### What the CarbideFrame version has:
- A comprehensive Python governance/validator/test framework (~170 scripts, 59 validators, 65 test runners)
- ~50 JSON schemas, hundreds of example fixtures
- A sprint ledger with 155+ sealed sprints
- Custody/receipt/registry-change governance infrastructure
- A **partial** browser training platform with 9 HTML pages, 3 CSS files, 3 JS files (i18n engine + EN/FR dictionaries), 2 favicon assets
- A visual regression harness (72-check)
- Substantial governance documentation (~67 governance docs, ~104 sealed sprint docs)

### What the CarbideFrame version is MISSING (vs. the complete OpenWork project):

#### Missing: Core application logic files (CRITICAL)
| File | Lines | Purpose |
|------|-------|---------|
| `js/db.js` | 969 | IndexedDB gateway — student records, progress, settings, enrollments, certificates. The ONLY file that touches IDB. |
| `js/app.js` | 502 | Global utilities — session management, toast notifications, password hashing, form helpers. |
| `js/pdf-lib.js` | 63 | PDF generation library for certificate export. |
| `js/clippy-guide.js` | 846 | Interactive Clippy-style guide assistant. |

**Impact:** Without `db.js` and `app.js`, the browser platform has **no data persistence, no login, no session management, no quiz scoring, no progress tracking, no certificate generation**. The HTML pages reference these files in their script load order but they don't exist. This is the root cause of the failed visual parity remediation — the agent was styling shells with no underlying application logic.

#### Missing: Course content and quiz data (CRITICAL)
| File | Lines | Purpose |
|------|-------|---------|
| `data/content.js` | 7,055 | Single source of truth — all course definitions, lesson content, quiz questions, bilingual content. 4 courses, 19+ modules, 96+ quiz questions. |
| `data/quiz-questions.js` | 840 | Quiz question bank. |
| `data/assignments.js` | 198 | Student assignment definitions. |
| `data/bug-keys.js` | 106 | Centralized bug key constants for the Bug Lab. |
| `data/progress.js` | 286 | Progress tracking data structures. |
| `data/students.js` | 275 | Student seed/demo data. |

**Impact:** Without `content.js`, the browser platform has **no courses, no lessons, no quizzes, no content to display**. The catalog and course-view pages are empty shells.

#### Missing: Desktop OS simulator (ENTIRE SUBSYSTEM)
| Directory | Files | Lines | Purpose |
|-----------|-------|-------|---------|
| `src/` | 8 | 4,629 | OS core, compositor, workspaces, event bus, keyboard shortcuts, health checks, scoring, custody |
| `apps/` | 16 | ~11,000 | 12 simulated applications (Dynamics, ADO, Teams, Browser, Outlook, QTube, QApache, Reports, Inspector, AC, Training, Settings, Excel, PowerPoint, Word) |
| `scenarios/` | 6 | 963 | Scenario definitions with case state, expected bugs, AC references |
| `os.css` | 1 | 1,474 | All OS styles — Win11 tokens, window chrome, taskbar |
| `os.bundle.js` | 1 | 6,601 | Pre-built OS bundle |
| `QASimulator.html` | 1 | 7,597 | Self-contained single-file build output |
| `build.js` + scripts | 5 | ~500 | Build system, launcher scripts |

**Impact:** The entire Desktop OS simulator — the capstone training environment with simulated work tools — is completely absent from CarbideFrame.

#### Missing: Academy pages
| File | Lines | Purpose |
|------|-------|---------|
| `portal.html` | 3,693 | Course catalog — My Learning + Available Courses (main hub after login) |
| `capstone.html` | 7,807 | Capstone assessment launcher with prerequisite gate |
| `capstone-2.html` | 8,956 | Advanced capstone assessment |
| `capstone-lab.html` | 803 | Capstone lab/practice |
| `simple-login.html` | 546 | Team/class login (alternative to email login) |
| `confirm.html` | 199 | Confirmation page |
| `mock.html` | 1,040 | Mock/simulation page |
| `guide-facilitator.html` | 462 | Facilitator guide |
| `guide-student.html` | 460 | Student guide |
| `ado-lab.html` | 1,316 | Azure DevOps lab |
| `crm-lab.html` | 1,268 | Dynamics CRM lab |
| `QA-Pilot-Session.html` | 270 | Session page |
| `START_Me_Up.html` | 46 | Start page |

**Impact:** The CarbideFrame version has only 9 HTML pages (index, admin, catalog, course-view, certificate, export, identity, import, visual-regression-harness). The complete version has **30 HTML pages**. The CarbideFrame pages are also much smaller — e.g., CarbideFrame `index.html` is 215 lines (a landing/splash page) vs. OpenWork `index.html` at 1,064 lines (a full login page with authentication).

#### Missing: Admin pages
| File | Lines | Purpose |
|------|-------|---------|
| `admin/index.html` | 467 | Admin login |
| `admin/dashboard.html` | 5,065 | Student management and progress overview |
| `admin/bugs.html` | 131 | Bug Lab — toggle intentional defects |
| `admin/editor.html` | 216 | Global content editor |
| `admin/assign.html` | 617 | Manual path assignment per student |
| `admin/simple.html` | 754 | Simple admin panel |

**Impact:** The CarbideFrame version has a single `admin.html` (394 lines) that is a deployment/member management page — completely different from the full admin suite.

#### Missing: QA module
| File | Lines | Purpose |
|------|-------|---------|
| `qa/qa-db.js` | 498 | QA database layer |
| `qa/qa-export-json.js` | 197 | JSON export |
| `qa/qa-export-md.js` | 424 | Markdown export |
| `qa/qa-import-json.js` | 344 | JSON import |
| `qa/qa-page-register.js` | 214 | Page registry |
| `qa/qa-queries.js` | 225 | Query engine |
| `qa/qa-schema.js` | 247 | Schema definitions |
| `qa/qa-templates.js` | 228 | Templates |
| `qa/qa-workitem-api.js` | 366 | Work item API |

**Impact:** The entire QA work-item subsystem is absent.

#### Missing: Debug panel
| File | Lines | Purpose |
|------|-------|---------|
| `debug/` (7 files) | 4,160 | Debug board, filters, import/export, panel, CSS, index |

#### Missing: Chrome extension
| File | Purpose |
|------|---------|
| `chrome-extension/` (3 files) | FlightPlan prompt helper |

#### Missing: Desktop launcher and build tools
| File | Purpose |
|------|---------|
| `build.js`, `build.sh`, `build.bat`, `build.command` | Build system |
| `serve.js` | Local server |
| `launch.bat`, `launch.command` | Launcher scripts |
| `setup_launcher.ps1`, `setup_launcher.sh` | Setup scripts |
| `make_icon_win.py` | Icon generator |
| `desktop/` (9 entries) | Desktop dev templates, dist, videos, tools |

#### Missing: Documentation
| File | Purpose |
|------|---------|
| `README.md` | Project README |
| `ARCHITECTURE.md` | Architecture reference |
| `LOCAL-AI-ARCHITECTURE.md` | Local AI architecture |
| `QA Pilot Docs/` (3 files) | Feature scope, debugger design, scenario LLM prompts |
| `desktop/IMPLEMENTATION-PLAN.md` | Desktop implementation plan |
| `desktop/README.md` | Desktop README |
| `desktop/LICENSE` | License file |
| `package.json` | Node.js package manifest |

---

## 4. Missing Functionality/Assets Summary

| Category | Missing Items | Severity |
|----------|--------------|----------|
| **Core app logic** | `db.js`, `app.js`, `pdf-lib.js`, `clippy-guide.js` | 🔴 CRITICAL — no persistence, no login, no session |
| **Course content** | `content.js` (7,055 lines), `quiz-questions.js`, `assignments.js`, `bug-keys.js`, `progress.js`, `students.js` | 🔴 CRITICAL — no courses, no quizzes, no content |
| **Desktop OS** | Entire `src/`, `apps/`, `scenarios/`, `os.css`, `os.bundle.js`, `QASimulator.html`, build system | 🔴 CRITICAL — entire capstone simulator absent |
| **Academy pages** | `portal.html`, `capstone.html`, `capstone-2.html`, `capstone-lab.html`, `simple-login.html`, `confirm.html`, `mock.html`, `guide-facilitator.html`, `guide-student.html`, `ado-lab.html`, `crm-lab.html`, `QA-Pilot-Session.html`, `START_Me_Up.html` | 🟡 MAJOR — 13 pages missing |
| **Admin suite** | `admin/index.html`, `admin/dashboard.html`, `admin/bugs.html`, `admin/editor.html`, `admin/assign.html`, `admin/simple.html` | 🟡 MAJOR — full admin suite missing |
| **QA module** | 9 files (`qa/qa-*.js`) | 🟡 MAJOR — work-item subsystem absent |
| **Debug panel** | 7 files (`debug/`) | 🟢 MODERATE |
| **Chrome extension** | 3 files | 🟢 LOW |
| **Build/launcher tools** | 10+ files | 🟢 MODERATE — needed for OS rebuilds |
| **Documentation** | `README.md`, `ARCHITECTURE.md`, `LOCAL-AI-ARCHITECTURE.md`, `QA Pilot Docs/`, `desktop/` docs | 🟢 MODERATE |
| **Assets** | `QASimulator.ico`, 4 sprite strip PNGs (QTube videos), `desktop/videos/` | 🟢 LOW |

**Root cause of failed visual parity remediation:** The CarbideFrame browser-assets are a **redesigned shell** — the HTML pages were rebuilt with Librarian-converged visual design (bento workbench, source chips, panel-purpose-labels, no emoji, no gradients), but they were built **without the underlying application logic** (`db.js`, `app.js`, `content.js`, `quiz-questions.js`). The visual parity sprints were styling empty shells that had no data layer, no authentication, no course content, and no quiz engine. No amount of CSS remediation can fix this — the application logic must be present first.

---

## 5. Useful CarbideFrame Work to Preserve

The CarbideFrame QA Pilot has substantial work that does NOT exist in the OpenWork version and should be preserved:

### 5a. Governance framework (UNIQUE — do not lose)
| Asset | Scale | Value |
|-------|-------|-------|
| Python governance scripts (~50 CLIs) | ~15,000 lines | Workbench, broker, MCP handlers, receipt store, packet ingest, evidence intake, test composition, result export, epic regression, pipeline layers, review/decision/owner-action chains, training sim/package/validation, knowledge adapter |
| Python validators (~59 files) | ~12,000 lines | One per governance contract — validates every schema, receipt, custody event, registry change, snapshot, startup surface |
| Shell test runners (~65 files) | ~8,000 lines | One per validator — executable test suite |
| JSON schemas (~50 files) | ~5,000 lines | Formal contracts for every governance surface |
| Example fixtures (~60 dirs) | hundreds of files | Valid/invalid JSON pairs for every contract |
| Sprint ledger | 3,447 lines | 155+ sealed sprints with full provenance |
| Governance docs (~67 files) | ~20,000 lines | Governance contracts, design docs, epic records, sprint records |
| Receipts | ~60 files | Owner decisions, custody receipts, defect records |
| Operational data store (`data/`) | hundreds of JSON files | Receipts, audits, custody, owner-decisions, registry changes, snapshots, evidence, packets, results, test-cases, training packages |

### 5b. Visual design work (PARTIAL VALUE — reapply after migration)
| Asset | Value |
|-------|-------|
| `docs/schemas/browser-assets/css/main.css` (1,203 lines) | Contains Librarian-converged design tokens (warm paper background, bento workbench, source chips, panel-purpose-labels, status-pills, state-badges). This is the visual design language that should be re-applied AFTER the complete application is migrated. |
| `docs/schemas/browser-assets/css/ado-mock.css` (278 lines) | ADO simulation styling — may be newer/better than OpenWork version |
| `docs/schemas/browser-assets/css/dynamics-mock.css` (353 lines) | Dynamics simulation styling — may be newer/better |
| `docs/schemas/browser-assets/i18n/lang-en.js` (405 lines) | English dictionary — has 279 keys vs. OpenWork's 180 keys. The extra 99 keys are from the I18N wiring epic. |
| `docs/schemas/browser-assets/i18n/lang-fr.js` (2,832 lines) | French dictionary — larger than OpenWork's 2,630 lines |
| `docs/schemas/browser-assets/js/i18n.js` (316 lines) | i18n engine — nearly identical to OpenWork's 315 lines |
| Visual regression harness (280 lines) | 72-check design quality harness — unique to CarbideFrame |
| Accessibility remediation | Skip-links, ARIA landmarks, tablist/aria-selected management, form labels — applied across all pages during design quality regression epic |

### 5c. CarbideFrame browser pages (REPLACE structure, preserve design)
The 9 CarbideFrame HTML pages have the Librarian-converged visual design but lack the application logic. They should be used as **design reference** for re-applying the visual language to the complete OpenWork pages after migration.

---

## 6. Recommended Path: Option A

### Recommendation: Option A — Migrate complete QA Pilot into CarbideFrame, then reapply governed Librarian visual design

### Rationale

**Why Option A:**
1. The CarbideFrame browser platform is fundamentally incomplete — it's missing ~60,000 lines of application logic, data, and the entire Desktop OS simulator. Patching (Option B) would mean copying nearly the entire OpenWork project piece by piece, which is more error-prone than a clean migration.
2. The CarbideFrame version has unique governance work (Python framework, 155+ sealed sprints, validators, schemas, custody) that must be preserved. Option C (keep in OpenWork, don't migrate) would leave the governance framework orphaned from the application it governs.
3. Option A gives us the best of both: the complete, functional application from OpenWork + the governance framework from CarbideFrame + the Librarian-converged visual design re-applied as a governed sprint.
4. The visual parity work already done (design tokens, accessibility remediation, i18n expansion) can be re-applied to the migrated pages as a follow-up sprint.

**Why not Option B (patch):**
- Patching would require copying ~100 files from OpenWork into CarbideFrame's `docs/schemas/browser-assets/` structure, which is a non-standard location for a web app. The CarbideFrame browser-assets are nested under `docs/schemas/` as reference assets, not at the project root where a web app would normally live.
- The CarbideFrame pages were redesigned with different HTML structure (bento workbench shell, different page names — `identity.html` vs `simple-login.html`, `catalog.html` vs `portal.html`). Patching would require reconciling two different page architectures file by file.
- The amount of missing code (~60,000 lines) makes patching more work than migrating.

**Why not Option C (keep in OpenWork):**
- The governance framework in CarbideFrame would remain disconnected from the application.
- The Librarian visual design convergence would never happen.
- Two copies of QA Pilot would continue to diverge.

### Migration approach for Option A:
1. Copy the complete OpenWork QA Pilot application files into CarbideFrame at a proper web-app root (e.g., `active/qa-pilot/browser-app/` or restructure `docs/schemas/browser-assets/`).
2. Preserve all CarbideFrame governance framework files (scripts/, docs/, schemas/, fixtures/, receipts/, project-state/, data/).
3. Re-apply the Librarian-converged visual design from the CarbideFrame `main.css` design tokens to the migrated pages.
4. Re-apply the accessibility remediation (skip-links, ARIA landmarks, etc.).
5. Merge the expanded i18n dictionaries (CarbideFrame has 99 extra EN keys).
6. Keep the visual regression harness.

---

## 7. File-by-File Reconciliation Matrix

### Legend
- **COPY** = Copy from OpenWork to CarbideFrame
- **PRESERVE** = Keep CarbideFrame version (unique work)
- **MERGE** = Merge both (CarbideFrame has additions)
- **REPLACE** = Replace CarbideFrame version with OpenWork version
- **NEW** = File only exists in OpenWork (copy in)
- **N/A** = File only exists in CarbideFrame governance (no OpenWork equivalent)

### 7a. Core JavaScript
| File | OpenWork (lines) | CarbideFrame (lines) | Action | Notes |
|------|------------------|---------------------|--------|-------|
| `js/db.js` | 969 | — | **NEW/COPY** | Critical — IndexedDB gateway |
| `js/app.js` | 502 | — | **NEW/COPY** | Critical — session, toast, password hashing |
| `js/i18n.js` | 315 | 316 | **MERGE** | Nearly identical; verify CarbideFrame additions |
| `js/lang-en.js` | 180 | 405 (as `i18n/lang-en.js`) | **MERGE** | CarbideFrame has 99 extra keys from I18N epic |
| `js/lang-fr.js` | 2,630 | 2,832 (as `i18n/lang-fr.js`) | **MERGE** | CarbideFrame has ~200 extra lines |
| `js/pdf-lib.js` | 63 | — | **NEW/COPY** | PDF generation for certificates |
| `js/clippy-guide.js` | 846 | — | **NEW/COPY** | Interactive guide assistant |

### 7b. Data files
| File | OpenWork (lines) | CarbideFrame | Action | Notes |
|------|------------------|-------------|--------|-------|
| `data/content.js` | 7,055 | — | **NEW/COPY** | Critical — all course definitions, lesson content, quizzes |
| `data/quiz-questions.js` | 840 | — | **NEW/COPY** | Quiz question bank |
| `data/assignments.js` | 198 | — | **NEW/COPY** | Student assignments |
| `data/bug-keys.js` | 106 | — | **NEW/COPY** | Bug key constants |
| `data/progress.js` | 286 | — | **NEW/COPY** | Progress tracking |
| `data/students.js` | 275 | — | **NEW/COPY** | Student seed data |

### 7c. CSS
| File | OpenWork (lines) | CarbideFrame (lines) | Action | Notes |
|------|------------------|---------------------|--------|-------|
| `css/main.css` | 933 | 1,203 | **MERGE** | CarbideFrame has Librarian-converged design tokens (+270 lines). Use CarbideFrame as base, add missing OpenWork component styles. |
| `css/ado-mock.css` | 278 | 278 | **COMPARE** | Same line count — verify if identical or CarbideFrame has changes |
| `css/dynamics-mock.css` | 353 | 353 | **COMPARE** | Same line count — verify if identical |
| `os.css` | 1,474 | — | **NEW/COPY** | OS styles — Win11 tokens, window chrome, taskbar |

### 7d. HTML pages — Academy
| File | OpenWork (lines) | CarbideFrame (lines) | Action | Notes |
|------|------------------|---------------------|--------|-------|
| `index.html` | 1,064 | 215 | **REPLACE** | OpenWork is full login page; CarbideFrame is splash/landing. Copy OpenWork, reapply Librarian visual design. |
| `portal.html` | 3,693 | — | **NEW/COPY** | Course catalog — main hub. CarbideFrame `catalog.html` (179 lines) is a minimal replacement. |
| `course-view.html` | 3,261 | 337 | **REPLACE** | OpenWork is full lesson viewer; CarbideFrame is minimal shell. |
| `certificate.html` | 1,211 | 101 | **REPLACE** | OpenWork is full certificate generator; CarbideFrame is minimal. |
| `capstone.html` | 7,807 | — | **NEW/COPY** | Capstone assessment |
| `capstone-2.html` | 8,956 | — | **NEW/COPY** | Advanced capstone |
| `capstone-lab.html` | 803 | — | **NEW/COPY** | Capstone lab |
| `simple-login.html` | 546 | — | **NEW/COPY** | Team/class login |
| `confirm.html` | 199 | — | **NEW/COPY** | Confirmation page |
| `mock.html` | 1,040 | — | **NEW/COPY** | Mock/simulation page |
| `guide-facilitator.html` | 462 | — | **NEW/COPY** | Facilitator guide |
| `guide-student.html` | 460 | — | **NEW/COPY** | Student guide |
| `ado-lab.html` | 1,316 | — | **NEW/COPY** | ADO lab |
| `crm-lab.html` | 1,268 | — | **NEW/COPY** | CRM lab |
| `QA-Pilot-Session.html` | 270 | — | **NEW/COPY** | Session page |
| `START_Me_Up.html` | 46 | — | **NEW/COPY** | Start page |
| `QASimulator.html` | 7,597 | — | **NEW/COPY** | Self-contained OS build output |

### 7e. HTML pages — Admin
| File | OpenWork (lines) | CarbideFrame (lines) | Action | Notes |
|------|------------------|---------------------|--------|-------|
| `admin/index.html` | 467 | — | **NEW/COPY** | Admin login |
| `admin/dashboard.html` | 5,065 | — | **NEW/COPY** | Student management |
| `admin/bugs.html` | 131 | — | **NEW/COPY** | Bug Lab |
| `admin/editor.html` | 216 | — | **NEW/COPY** | Content editor |
| `admin/assign.html` | 617 | — | **NEW/COPY** | Path assignment |
| `admin/simple.html` | 754 | — | **NEW/COPY** | Simple admin |
| `admin.html` (CF) | — | 394 | **PRESERVE as reference** | CarbideFrame deployment page — different purpose, use as design reference |

### 7f. HTML pages — CarbideFrame-only
| File | CarbideFrame (lines) | Action | Notes |
|------|---------------------|--------|-------|
| `identity.html` | 138 | **PRESERVE as reference** | Local learner identity setup — may map to `simple-login.html` |
| `import.html` | 106 | **PRESERVE as reference** | Import team deployment |
| `export.html` | 102 | **PRESERVE as reference** | Export learner results |
| `catalog.html` | 179 | **PRESERVE as reference** | Course catalog — maps to `portal.html` |
| `visual-regression-harness.html` | 280 | **PRESERVE** | 72-check design quality harness — unique to CarbideFrame |

### 7g. Desktop OS source
| Directory | OpenWork files | Lines | Action | Notes |
|-----------|---------------|-------|--------|-------|
| `src/os-core.js` | 1 | 3,279 | **NEW/COPY** | OS engine |
| `src/compositor.js` | 1 | 271 | **NEW/COPY** | Window compositor |
| `src/workspaces.js` | 1 | 151 | **NEW/COPY** | Virtual desktop manager |
| `src/event-bus.js` | 1 | 117 | **NEW/COPY** | Event system |
| `src/keyboard-shortcuts.js` | 1 | 190 | **NEW/COPY** | Keyboard shortcuts |
| `src/health-checks.js` | 1 | 384 | **NEW/COPY** | OS self-diagnostics |
| `src/scoring.js` | 1 | 122 | **NEW/COPY** | Scenario scoring |
| `src/custody/custody.js` | 1 | 115 | **NEW/COPY** | Custody layer |
| `apps/` (16 files) | 16 | ~11,000 | **NEW/COPY** | 12 simulated applications |
| `scenarios/` (6 files) | 6 | 963 | **NEW/COPY** | Scenario definitions |
| `os.bundle.js` | 1 | 6,601 | **NEW/COPY** | Pre-built bundle |
| `os.css` | 1 | 1,474 | **NEW/COPY** | OS styles |
| `build.js` | 1 | ~300 | **NEW/COPY** | Build system |
| `desktop/` (9 entries) | 9 | various | **NEW/COPY** | Desktop dev templates, dist, videos, tools |

### 7h. QA module
| File | OpenWork (lines) | Action | Notes |
|------|------------------|--------|-------|
| `qa/qa-db.js` | 498 | **NEW/COPY** | QA database layer |
| `qa/qa-export-json.js` | 197 | **NEW/COPY** | JSON export |
| `qa/qa-export-md.js` | 424 | **NEW/COPY** | Markdown export |
| `qa/qa-import-json.js` | 344 | **NEW/COPY** | JSON import |
| `qa/qa-page-register.js` | 214 | **NEW/COPY** | Page registry |
| `qa/qa-queries.js` | 225 | **NEW/COPY** | Query engine |
| `qa/qa-schema.js` | 247 | **NEW/COPY** | Schema definitions |
| `qa/qa-templates.js` | 228 | **NEW/COPY** | Templates |
| `qa/qa-workitem-api.js` | 366 | **NEW/COPY** | Work item API |

### 7i. Debug panel
| File | OpenWork (lines) | Action | Notes |
|------|------------------|--------|-------|
| `debug/debug-board.js` | 174 | **NEW/COPY** | |
| `debug/debug-filters.js` | 349 | **NEW/COPY** | |
| `debug/debug-import-export.js` | 730 | **NEW/COPY** | |
| `debug/debug-panel.js` | 636 | **NEW/COPY** | |
| `debug/debug.js` | 489 | **NEW/COPY** | |
| `debug/debug.css` | 1,387 | **NEW/COPY** | |
| `debug/index.html` | 395 | **NEW/COPY** | |
| `debug/local-qa-debugger-prompt-pack.md` | — | **NEW/COPY** | |

### 7j. Chrome extension
| File | Action | Notes |
|------|--------|-------|
| `chrome-extension/manifest.json` | **NEW/COPY** | |
| `chrome-extension/popup.html` | **NEW/COPY** | |
| `chrome-extension/README.md` | **NEW/COPY** | |

### 7k. Build/launcher/config
| File | Action | Notes |
|------|--------|-------|
| `package.json` | **NEW/COPY** | Node.js manifest |
| `build.js` | **NEW/COPY** | Build system |
| `build.sh` | **NEW/COPY** | Build script (macOS) |
| `build.bat` | **NEW/COPY** | Build script (Windows) |
| `build.command` | **NEW/COPY** | Build command (macOS) |
| `serve.js` | **NEW/COPY** | Local server |
| `launch.bat` | **NEW/COPY** | Launcher (Windows) |
| `launch.command` | **NEW/COPY** | Launcher (macOS) |
| `setup_launcher.ps1` | **NEW/COPY** | Setup (Windows) |
| `setup_launcher.sh` | **NEW/COPY** | Setup (macOS) |
| `make_icon_win.py` | **NEW/COPY** | Icon generator |
| `.gitignore` | **COMPARE/MERGE** | Both have .gitignore — merge rules |

### 7l. Assets
| File | Action | Notes |
|------|--------|-------|
| `favicon.png` | **COMPARE** | Both have this — verify if identical |
| `favicon.svg` | **COMPARE** | Both have this — verify if identical |
| `QASimulator.ico` | **NEW/COPY** | Windows icon |
| `desktop/videos/` (4 PNGs) | **NEW/COPY** | QTube sprite strips |

### 7m. Documentation
| File | Action | Notes |
|------|--------|-------|
| `README.md` | **NEW/COPY** | Project README |
| `ARCHITECTURE.md` | **NEW/COPY** | Architecture reference |
| `LOCAL-AI-ARCHITECTURE.md` | **NEW/COPY** | Local AI architecture |
| `QA Pilot Docs/` (3 files) | **NEW/COPY** | Feature scope, debugger design, scenario prompts |
| `desktop/IMPLEMENTATION-PLAN.md` | **NEW/COPY** | Desktop implementation plan |
| `desktop/README.md` | **NEW/COPY** | Desktop README |
| `desktop/LICENSE` | **NEW/COPY** | MIT license |

### 7n. CarbideFrame governance (PRESERVE — no OpenWork equivalent)
| Asset | Action | Notes |
|-------|--------|-------|
| `scripts/` (~170 files) | **PRESERVE** | Python governance framework — unique to CarbideFrame |
| `docs/governance/` (~67 files) | **PRESERVE** | Governance contracts |
| `docs/schemas/*.schema.json` (~50 files) | **PRESERVE** | JSON schemas |
| `docs/examples/` (~60 dirs) | **PRESERVE** | Example fixtures |
| `docs/sprints/` (~104 files) | **PRESERVE** | Sealed sprint records |
| `docs/planning/` (7 files) | **PRESERVE** | Planning docs |
| `fixtures/` | **PRESERVE** | Broker fixtures |
| `project-state/sprint-ledger.json` | **PRESERVE** | Sprint ledger |
| `receipts/` | **PRESERVE** | Owner decisions, custody receipts |
| `reports/` | **PRESERVE** | Status reports |
| `data/` (operational store) | **PRESERVE** | Governance data |
| `config/` | **PRESERVE** | Broker config |
| `PROJECT-IDENTITY.md` | **PRESERVE** | Project identity |
| `PROJECT-PROFILE.json` | **PRESERVE** | Project profile |
| `startup-contract.json` | **PRESERVE** | Startup contract |
| `PROJECT-STARTUP.md` | **PRESERVE** | Startup doc |
| `FEATURE-STATUS.md` | **PRESERVE** | Feature status |
| `SESSION-HANDOFF.md` | **PRESERVE** | Session handoff |
| `STARTUP-STATE.md` | **PRESERVE** | Startup state |

---

## 8. Recommended Implementation Sequence

### Phase 1: Migration Preparation (governed sprint)
1. **Owner decision required:** Authorize Option A migration
2. Create migration sprint: `QA-PILOT-SOURCE-MIGRATION-1`
3. Choose target location for web app within CarbideFrame (recommend `active/qa-pilot/browser-app/` to separate from governance framework)
4. Snapshot current CarbideFrame browser-assets for design reference

### Phase 2: Copy Complete Application (governed sprint)
5. Copy all OpenWork QA Pilot application files to `active/qa-pilot/browser-app/`:
   - `js/` (7 files: app.js, db.js, i18n.js, lang-en.js, lang-fr.js, pdf-lib.js, clippy-guide.js)
   - `data/` (6 files: content.js, quiz-questions.js, assignments.js, bug-keys.js, progress.js, students.js)
   - `css/` (3 files: main.css, ado-mock.css, dynamics-mock.css)
   - `os.css`, `os.bundle.js`
   - All 30 HTML pages (root + admin/ + apps/ + scenarios/)
   - `src/` (8 files), `qa/` (9 files), `debug/` (7 files)
   - `chrome-extension/` (3 files)
   - Build/launcher/config files
   - Assets (favicon, ico, sprite strips)
   - Documentation
6. Verify the copied application opens and runs from `file://`

### Phase 3: Merge i18n Dictionaries (governed sprint)
7. Merge CarbideFrame's expanded `lang-en.js` (405 lines, 279 keys) into the migrated copy
8. Merge CarbideFrame's expanded `lang-fr.js` (2,832 lines) into the migrated copy
9. Verify i18n engine works with merged dictionaries

### Phase 4: Reapply Visual Design (governed sprint)
10. Merge CarbideFrame's `main.css` design tokens (Librarian-converged: warm paper background, bento workbench, source chips, panel-purpose-labels, status-pills, state-badges) into the migrated `main.css`
11. Reapply accessibility remediation (skip-links, ARIA landmarks, tablist, form labels) to migrated pages
12. Copy visual regression harness to migrated app
13. Run visual regression harness against migrated pages

### Phase 5: Validation (governed sprint)
14. Full roundtrip validation: login → portal → course → quiz → capstone → certificate
15. Verify bilingual (EN/FR) toggle works on all pages
16. Verify admin suite: dashboard, bugs, editor, assign
17. Verify Desktop OS: boot, apps, scenarios, scoring
18. Verify QA module: queries, export, import
19. Verify debug panel
20. Run all 59 CarbideFrame validators + 65 test runners (governance framework must remain green)

### Phase 6: Cleanup (governed sprint)
21. Archive old `docs/schemas/browser-assets/` pages (keep as design reference)
22. Update `startup-contract.json` to reflect new web app location
23. Update `FEATURE-STATUS.md` and `SESSION-HANDOFF.md`
24. Update sprint ledger

---

## 9. Validation Results

### Inspection validation
- ✅ Both project paths inspected (read-only, no mutations)
- ✅ Complete file inventory of OpenWork QA Pilot (124 files)
- ✅ Complete file inventory of CarbideFrame QA Pilot browser-assets (17 files)
- ✅ Line counts obtained for all significant files
- ✅ Key entry points read (README, ARCHITECTURE, index.html, startup-contract, SESSION-HANDOFF, FEATURE-STATUS)
- ✅ Missing files identified and categorized by severity
- ✅ CarbideFrame unique work identified and categorized
- ✅ File-by-file reconciliation matrix produced
- ✅ Implementation sequence produced

### Constraints honored
- ✅ No mutations to complete OpenWork QA Pilot source
- ✅ No mutations to CarbideFrame Librarian source
- ✅ No backend, auth, telemetry, external dependencies, or fake-live behavior added
- ✅ No visual parity or styling work performed

---

## 10. Risks

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| R1 | **Path reference breakage** — OpenWork pages use relative paths (`css/main.css`, `js/db.js`). Moving to a subdirectory (`browser-app/`) may break references. | 🟡 MEDIUM | Verify all relative paths work from new location. May need to adjust paths or keep at project root. |
| R2 | **i18n merge conflicts** — CarbideFrame has 99 extra EN keys and ~200 extra FR lines. Merging may produce duplicate keys or conflicts. | 🟡 MEDIUM | Programmatic key-diff comparison before merge. Test all pages in both languages after merge. |
| R3 | **CSS design token conflicts** — CarbideFrame `main.css` (1,203 lines) has Librarian-converged tokens that may conflict with OpenWork component styles (933 lines). | 🟡 MEDIUM | Diff comparison of `:root` custom properties. Merge tokens first, then add missing component styles. |
| R4 | **Governance framework integration** — The migrated web app needs to be recognized by the CarbideFrame governance framework (startup-contract, validators, etc.). | 🟡 MEDIUM | Update `startup-contract.json` `is_web_app` field and verification surfaces. Add web-app validators. |
| R5 | **Data store separation** — CarbideFrame `data/` is the governance operational store (gitignored). OpenWork `data/` is course content (JS files). These must not collide. | 🟡 MEDIUM | Use separate directories: `browser-app/data/` for course content, `data/` for governance store. |
| R6 | **Visual parity epic invalidation** — The in-flight visual parity epic (Sprint 3/5) and paused I18N epic were built on incomplete code. They may need to be re-scoped or abandoned. | 🟢 LOW | Mark epics as superseded by migration. Re-plan visual parity as post-migration sprint. |
| R7 | **Working tree state** — CarbideFrame has 416 changed/untracked files. Migration adds more. | 🟢 LOW | Commit current state before migration. Use governed sprint with custody checkout. |
| R8 | **OpenWork source divergence** — If OpenWork QA Pilot is still being actively developed, the migrated copy will diverge. | 🟢 LOW | Establish CarbideFrame as the new canonical home. Archive OpenWork version or mark as superseded. |

---

## 11. Owner Decision Required Before Implementation

**Decision required:** Authorize Option A (migrate complete QA Pilot from OpenWork into CarbideFrame, then reapply governed Librarian visual design).

**Specific authorizations needed:**

1. **Authorize copy** of all application files from `/Users/andrew/Desktop/OpenWork/QA Pilot` into `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot/` (target subdirectory TBD — recommend `browser-app/`).

2. **Authorize retirement** of the current `docs/schemas/browser-assets/` pages (archive as design reference, do not delete).

3. **Authorize re-scoping** of the in-flight `EPIC-QA-PILOT-LIBRARIAN-VISUAL-PARITY-CORRECTION-1` (Sprint 3/5 complete) — the remaining Sprints 4-5 should be deferred until after migration, then re-planned against the complete codebase.

4. **Authorize re-scoping** of the paused `EPIC-QA-PILOT-I18N-WIRING-1` (5/5 sprints complete, unsealed) — the i18n work should be re-validated against the migrated codebase.

5. **Confirm target location** for the web app within CarbideFrame:
   - Option i: `active/qa-pilot/browser-app/` (separate from governance)
   - Option ii: `active/qa-pilot/` root (merge with governance — may cause path conflicts)
   - Option iii: Other (Owner preference)

6. **Confirm whether OpenWork QA Pilot should be archived** or left as-is after migration.

---

## Summary

The CarbideFrame QA Pilot is a **governance framework with an incomplete browser shell**. The OpenWork QA Pilot is the **complete, functional training platform**. The CarbideFrame browser-assets were redesigned with Librarian visual design but were built without the underlying application logic (`db.js`, `app.js`, `content.js`, and ~60,000 lines of additional code). This is why visual parity remediation failed — the agent was styling empty shells.

**Recommended path: Option A** — migrate the complete OpenWork application into CarbideFrame, preserve the governance framework, then reapply the Librarian visual design as a post-migration governed sprint.

**Hard stop remains in effect:** No further visual parity or styling work until this reconciliation is Owner-approved and the migration is complete.