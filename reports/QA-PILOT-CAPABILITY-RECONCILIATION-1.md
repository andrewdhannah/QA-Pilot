# QA-PILOT-CAPABILITY-RECONCILIATION-1

**Purpose:** Inventory the existing QA-Pilot V1.5 implementation and map its capabilities onto the new governed evidence model.

**Source:** `/Users/andrew/Desktop/OpenWork/QA Pilot/` (V1.5)
**Target:** `/Users/andrew/Desktop/CarbideFrame/active/qa-pilot/` (V2, SDK-governed)
**Status:** 🔍 Pending Owner review

---

## 1. V1.5 Architecture Overview

V1.5 is a fully functional, self-contained QA training platform with a **simulated Win11 desktop OS** that runs scenario-based assessments. It has no governance wrapper, no Librarian integration, and assumes total authority over its state.

### Three Major Layers

```
LAYER 1: ACADEMY (course platform)
├── index.html              — Login / account creation
├── portal.html              — Course catalog
├── course-view.html         — Lesson player with modules, quizzes, progress
├── certificate.html         — Score display, breakdown, print
├── data/content.js          — Course definitions (7055 lines, JS globals)
├── data/quiz-questions.js   — Quiz banks (841 lines, structured objects)
├── data/bug-keys.js         — Bug ID constants (106 lines)
├── data/students.js         — Student data model
├── data/progress.js         — Progress tracking model
├── data/assignments.js      — Assignment data model
├── js/db.js                 — IndexedDB wrapper (qa_onboarding_db, 6 stores)
├── js/app.js                — UI app logic
├── js/i18n.js               — Internationalization
├── js/lang-en.js / lang-fr.js
└── css/main.css             — Design tokens and layout

LAYER 2: DESKTOP OS SIMULATOR
├── QASimulator.html         — OS shell entry
├── src/os-core.js           — OS engine (APPS registry, window management, scenarios, scoring)
├── src/compositor.js        — Window state, focus, layouts, snap
├── src/event-bus.js         — Internal pub/sub
├── src/workspaces.js        — IDB-backed window layout persistence
├── src/scoring.js           — Capstone assessment scoring engine (122 lines)
├── src/health-checks.js     — System health monitoring
├── src/keyboard-shortcuts.js
├── os.css                   — OS chrome styling
├── apps/dynamics.html       — Dynamics 365 CRM simulator
├── apps/ado.html            — Azure DevOps bug report simulator
├── apps/teams.html          — Microsoft Teams chat simulator
├── apps/qoutlook.html       — Email client simulator
├── apps/browser.html        — QA Browser with internal pages (QTube, QApache)
└── os.bundle.js             — Build output (never edit directly)

LAYER 3: SCENARIOS & ASSESSMENTS
├── scenarios/capstone-scenario.js     — Capstone #1: Payment Processing
├── scenarios/capstone-scenario-2.js   — Capstone #2: Sprint G
├── scenarios/scenarios-case-001.js    — Training case #1
├── scenarios/case-002.js              — Training case #2
├── scenarios/scenario-case-003.js     — Training case #3
├── scenarios/scenarios-bug-001.js     — Bug hunting exercise
├── src/scoring.js                     — Evaluation engine (pure function)
├── admin/                             — Admin dashboard, bug lab, enrollment mgmt
├── data/bug-keys.js                   — Centralized bug ID registry
├── chrome-extension/                  — Browser extension for bug logging
├── qa/                                — QA debugger (qa-db.js, qa-schema.js)
└── debug/                             — Debug landing page
```

### Runtime Model

- **Language:** Vanilla JavaScript (no transpilation, no build-time transforms)
- **Runtime:** Browser only — `file://` safe. No server required.
- **Frameworks:** None. No React, Vue, Angular, or any runtime dependency.
- **Build:** `node build.js` inlines all source into single-file distribution
- **Data:** IndexedDB (`qa_onboarding_db`) + localStorage for OS state
- **Deploy:** SharePoint, USB drive, OneNote, or direct `file://`

---

## 2. Capability Inventory — What V1.5 Has That V2 Does Not

| Capability | V1.5 Status | V2 Status | Preserve? | Migration Strategy |
|---|---|---|---|---|
| **Course platform** (lessons, modules, quizzes, progress) | ✅ Full | ✅ Full (migrated to course-pack-v1) | YES — already migrated | Already done via P4 converter |
| **Quiz question bank** (structured questions with explanations) | ✅ 841 lines | ✅ In course-pack-v1 JSON | YES — already migrated | Already done |
| **Bug key registry** (centralized bug constants) | ✅ 106 lines | ✅ In platform/data/bug-keys.js | YES — already copied | Already done |
| **Student management** (accounts, roles, enrollments) | ✅ Full | ✅ Partial (enrollments exist) | YES | Migrate student data model to SDK-governed |
| **Progress tracking** (per-student, per-course) | ✅ Full | ✅ course_progress store | YES | Already migrated schema |
| **Certificate generation** (score ring, breakdown, print) | ✅ Full | ✅ certificate.html exists | YES | Already migrated |
| **Desktop OS simulator** (Win11-style with window management) | ✅ Full | ❌ Missing | EVALUATE | OS simulator is context for capstone scenarios. Assess if needed for training. |
| **Dynamics CRM simulator** (mock CRM with bugs) | ✅ Full | ❌ Missing | EVALUATE | Capstone scenario context. Could be replaced or hosted separately. |
| **Azure DevOps simulator** (mock ADO for bug reports) | ✅ Full | ❌ Missing | EVALUATE | Same as Dynamics |
| **Teams chat simulator** (scenario narrative delivery) | ✅ Full | ❌ Missing | EVALUATE | Narrative delivery — could be simplified to text |
| **QOutlook email client** | ✅ Full | ❌ Missing | LOW | Easter egg. Not core to training. |
| **Capstone scoring engine** (scoring.js — 122 lines) | ✅ Pure function | ❌ Missing | HIGH | **Reusable as-is** — pure function, no side effects, reads window.SCENARIOS |
| **Scenario definitions** (6 scenario files with bugs, CRM state, teams threads) | ✅ Full | ❌ Missing | HIGH | **Reusable with adapter** — define scenarios against governed evidence |
| **Clippy guide** (on-screen help avatar) | ✅ js/clippy-guide.js | ❌ Missing | LOW | Fun but not essential |
| **Health checks** (src/health-checks.js) | ✅ | ❌ Missing | LOW | Replaced by Librarian health checks |
| **Workspace persistence** (src/workspaces.js) | ✅ | ❌ Missing | LOW | Browser-based, not governance-relevant |
| **Admin dashboard** (course mgmt, bug lab, enrollment) | ✅ admin/ | ✅ Partial (admin.html exists) | YES — partial | Already has course import UI. Expand for teaching layer. |
| **QA Debugger** (qa/, debug/) | ✅ | ❌ Missing | LOW | Internal dev tool, not relevant to governed teaching |
| **Chrome extension** (bug logging helper) | ✅ | ❌ Missing | EVALUATE | Could be useful for real-world training |

---

## 3. Governance Boundary Analysis

### V1.5 Governance Violations (relative to V2 model)

| Violation | Location | Risk | Remediation |
|---|---|---|---|
| Reads/writes IndexedDB freely without governance | `js/db.js`, `src/os-core.js` | MEDIUM | V2 already has separate DB (`qa_pilot_v2`). Data migration needed for student records. |
| Assumes `file://` authority over all state | Throughout | LOW | OK for client — but must not confuse local state with governed evidence. |
| No provenance for training artifacts | `data/content.js`, `data/quiz-questions.js` | MEDIUM | Course packs in V2 add version/source, but no provenance chain back to Librarian. |
| No evidence schema on quiz content | `data/quiz-questions.js` | MEDIUM | Questions are static data. For governed teaching, questions should reference SDK findings. |
| Hardcoded admin credentials | `README.md` (QAAdmin2026) | LOW | Outdated. Not in V2. |
| Scenario data assumes local knowledge | `scenarios/*.js` | MEDIUM | Scenarios reference hardcoded bugs. Target: scenario definitions derive from SDK findings. |
| Scoring engine is pure but uncoupled | `src/scoring.js` | LOW | Scoring logic is reusable — just needs governed scenario input. |

### Confirmed Non-Violations

- V1.5 does NOT write to Librarian state ✅
- V1.5 does NOT create authority records ✅
- V1.5 does NOT maintain duplicate evidence stores (it maintains student data, which is separate) ✅
- V1.5 does NOT claim authority over project governance ✅

---

## 4. Reusable Assets — What to Preserve

### Tier 1: Directly Reusable (pure logic, no side effects)

| Asset | Path | Lines | Notes |
|---|---|---|---|
| **Scoring engine** | `src/scoring.js` | 122 | Pure function. Takes scenarioId, bugsFound, bugsLogged → {score, passed}. No dependencies. |
| **Bug key registry** | `data/bug-keys.js` | 106 | Constants only. Already in V2. |
| **Quiz question bank** | `data/quiz-questions.js` | 841 | Static data. Already migrated to course-pack-v1 JSON. |
| **Course content** | `data/content.js` | 7055 | Already migrated to JSON course packs via P4 converter. |
| **i18n system** | `js/i18n.js`, `js/lang-*.js` | ~600 | Already in V2. |

### Tier 2: Reusable With Adapter (depends on old input format)

| Asset | Path | Lines | Adapter Needed |
|---|---|---|---|
| **Scenario definitions** | `scenarios/*.js` | ~500 total | Currently read from `window.SCENARIOS`. Needs adapter to inject SDK evidence findings. |
| **Scoring HTML/CSS** | `capstone.html`, `os.css` | ~400 | Scoring UI is embedded in OS. Needs extraction. |
| **Certificate display** | `certificate.html` | ~200 | Already in V2. May need scoring data from new pipeline. |

### Tier 3: Context/Experience (reusable design, not logic)

| Asset | Notes |
|---|---|
| **Dynamics CRM simulator** | The mock CRM is where students practice finding bugs. Valuable for hands-on training. Could be hosted as a standalone HTML page gated behind SDK. |
| **Azure DevOps simulator** | Same as Dynamics. Bug report entry point. |
| **Teams chat simulator** | Narrative delivery — could be simplified to text or kept as-is. |
| **Training workflow** (Portal → Course → Lesson → Quiz → Capstone) | The progression model is sound. Already preserved in V2's academy layer. |

---

## 5. Learning Object Contract — Proposed Mapping

The missing layer is the **learning object** — a governed artifact that connects Librarian evidence to teaching/testing/certification.

### Current (V1.5) Model

```
Project knowledge (manual)
        ↓
Course content (content.js)
        ↓
Lessons & quizzes
        ↓
Capstone scenario (hardcoded bugs)
        ↓
Scoring (evaluateSubmission)
        ↓
Certificate
```

### Target (V2 + SDK) Model

```
Librarian governed evidence  ←─ SDK
        ↓
Learning Object
        ├── source_epic         (which epic this teaches)
        ├── source_findings     (findings that inspired this lesson)
        ├── source_provenance   (evidence provenance context)
        ├── lesson              (explanatory content)
        ├── quiz                (assessment questions with explanations)
        ├── exercise            (scenario-based exercise)
        └── certification       (evaluation criteria)
        │
        ├──→ Human onboarding
        ├──→ AI context/training
        └──→ Qualification tests
```

### Example: A finding becomes a lesson

```json
{
  "learning_object_id": "LO-EV-GOV-002",
  "source_finding": "F-0001",
  "source_code": "EV-GOV-002",
  "title": "Lifecycle Cursor Freshness",
  "type": "lesson",
  "prerequisite_knowledge": ["governance", "lifecycle"],
  "content": "A lifecycle cursor tracks project phase...",
  "quiz": [
    {
      "question": "What does a stale cursor mean?",
      "answer": "The project has not been reconciled within the freshness threshold",
      "explanation": "Staleness means the project's lifecycle state is uncertain..."
    }
  ],
  "exercise": {
    "scenario": "You find a project with a stale cursor...",
    "expected_action": "Identify the staleness, check last reconciliation time..."
  },
  "provenance": {
    "source_artifact": "F-0001 in latest-evaluation.json",
    "generated_by": "evidence-plane-evaluator-v1",
    "generated_at": "2026-07-24T02:04:56Z"
  }
}
```

---

## 6. The OBD2 Analogy — Complete

```
Librarian (diagnostic computer)        QA-Pilot (training technician)
──────────────────────────────          ─────────────────────────────────
OE-001 sensor readings                 Explain what each reading means
OE-002 fault codes                     Create exercises around each code
OE-003 system relationships            Test understanding of component links
OE-004 authority resolution            Teach why one source wins over another
OE-005 runtime lineage                 Walk through the chain from code to output
OE-006 projection provenance           Verify surface matches source

Capstone scenario:                     "Here is a diagnostic readout. Find the problems.
                                        Report them correctly. Get certified."
```

---

## 7. Migration Boundary Document

### What Changes

| Current (V1.5 path) | Target (governed path) | When |
|---|---|---|
| Scenarios hardcode bug definitions | Scenarios consume SDK findings | Teaching layer build |
| Scoring reads window.SCENARIOS | Scoring reads governed scenario input | Reuse as-is with adapter |
| Course content in JS globals | Course content in JSON course packs | ✅ Already done |
| Quiz questions in JS | Quiz questions in course-pack JSON | ✅ Already done |
| Student state in IndexedDB | Student state in governed data model | Reconciliation sprint |
| OS simulator manages all state | OS simulator is a sandboxed experience layer | No change needed — not governance-relevant |

### What Stays

- Scoring engine (pure function) — **keep as-is**
- Scenario definitions (adapted, not rewritten)
- Training progression model
- Certificate generation
- Admin dashboard (expand for teaching layer)
- Dynamics/ADO/Teams simulators (if desired — they are sandboxed experience, not authority)

### What Goes Away

- Hardcoded content.js globals → replaced by course-pack JSON ✅
- Uncontrolled IndexedDB access → V2's qa_pilot_v2 with governed schema
- file:// authority assumption → SDK-governed evidence consumption

---

## 8. Recommended Implementation Sequence

```
Phase 2A — Teaching Layer Foundation
─────────────────────────────────────
1. Learning Object schema (contract connecting SDK evidence → teaching artifacts)
2. Learning Object generator (transforms findings into lessons + quizzes)
3. Scenario adapter (reads SDK findings, populates scenario format for scoring engine)

Phase 2B — Capability Integration
─────────────────────────────────────
4. Scoring engine integration (adapter for governed scenario data)
5. Exercise generator (scenario-based exercises from evidence patterns)

Phase 2C — AI Qualification  
─────────────────────────────────────
6. AI qualification tests (can AI interpret governed evidence?)
7. Certification engine (evidence-backed cert, not local-test-only)
```

---

## 9. Key Findings Summary

| Finding | Severity | Action |
|---|---|---|
| V1.5 already has the teaching/testing/certification engine | POSITIVE — not a rebuild | Inventory and adapt |
| Scoring.js is a pure function — directly reusable | REUSABLE | Keep as-is, wrap adapter |
| Scenario definitions are the main migration target | MIGRATION NEEDED | Redefine to consume SDK findings |
| Course platform already migrated to course-pack-v1 | ✅ COMPLETE | No action needed |
| No governance violations in V1.5 teaching logic | CLEAN | Confirms separation |
| Learning object contract is the missing piece | NEW | Define schema for Phase 2A |
| OBD2 analogy is architecturally complete | CONFIRMED | Use as reference model |

---

*This report was produced by a governed agent. All status markers are 🔍 Pending Owner verification. No authority is conferred by this report.*
