# QA-PILOT-TRAINING-SYSTEM-RECONCILIATION-PLAN-1 — Reconciliation Report

**Generated:** 2026-07-08
**Sprint:** QA-PILOT-TRAINING-SYSTEM-RECONCILIATION-PLAN-1 (Sprint 1/11)
**Epic:** EPIC-QA-PILOT-TRAINING-SYSTEM-1
**Status:** complete_pending_owner_review

---

## 1. Generation Inventory

Five generations of QA Pilot were identified across local filesystems and GitHub repositories:

| Gen | ID | GitHub | Local Path | Era | Language | Type |
|-----|----|--------|-----------|-----|----------|------|
| **V1** | QA-Pilot | `andrewdhannah/QA-Pilot` | `Desktop/openwork/QA Pilot/` | Pre-2026-05 | Vanilla JS | Web app (academy + OS sim) |
| **V1.5** | QA-PilotV1_5 | `andrewdhannah/QA-PilotV1_5` | `Desktop/OW Old Folder/QA-PilotV1_5/` | 2026-05 | Vanilla JS | Web app (transitional) |
| **V2** | qa-pilot-v2 | `andrewdhannah/qa-pilot-v2` | `Desktop/openwork/QA-PilotV2/` + `Desktop/CarbideFrame/qa-pilot/` | 2026-05–06 | Vanilla JS | Course platform (JSON course packs) |
| **Current** | active/qa-pilot | — | `Desktop/CarbideFrame/active/qa-pilot/` | 2026-07 | Python/scripts | Governed QA validation pipeline |
| **Bridge** | (cross-project) | — | `active/librarian` (packet export) | 2026-07 | Python/Swift | Cross-project QA packet bridge |

---

## 2. Feature Lineage Map

### 2.1 Training & Onboarding Capabilities

```
V1 Academy ─────────────────────────────────────────────────────────┐
  ├── Lessons 1-4 (chaptered, quizzes, progress, resume)          │
  ├── Course viewer (course.html, course-view.html)                │
  ├── Placement survey & path auto-healer                          │
  ├── Admin suite (dashboard, assign, editor, bug lab)             │
  ├── Capstone host shell + unlock gate                            │
  ├── Certificate page (print-to-PDF)                              │
  └── Multi-course architecture (portal, catalog, enrollment)       │
                                                                    │
V1.5 Transitional ─────────────────────────────────────────────────┤
  └── Same architecture as V1, minor fixes                          │
                                                                    │
V2 Course Platform ────────────────────────────────────────────────┤
  ├── Course packs as JSON (course-pack-v1 schema)                  │
  ├── IndexedDB storage (db.js)                                     │
  ├── Admin UI: import, validate, preview, enable courses           │
  ├── Admin UI: search, filter, sort, batch actions                 │
  ├── Legacy V1.5 → course-pack-v1 converter                        │
  ├── Student portal: catalog, enrollment, progress                 │
  ├── Runtime: modules, chapters, quizzes                           │
  ├── Completion certificate                                        │
  └── 12 shipped course packs (QA onboarding, Agile, Scrum, etc.)   │
                                                                    │
Current Governed ───────────────────────────────────────────────────┤
  └── (No training/onboarding capabilities — shifted to QA          │
       validation pipeline)                                         │
                                                                    │
EPIC TARGET ────────────────────────────────────────────────────────┘
  Knowledge adapter → Training gen → Validation → Packages
```

### 2.2 OS Simulator & Scenario Capabilities (V1 Only)

```
V1 Desktop (OS Simulator)
├── Windows 11 shell (lock screen, taskbar, desktop, themes)
├── Window manager (drag, snap, minimize, maximize, z-stack)
├── Start menu, Task View, Notification Centre, Quick Settings
├── Apps: Dynamics CRM, ADO, AC Panel, Settings
├── Capstone scenario engine (stage gates, scoring)
│   ├── Dynamics capstone wiring (bug triggers, BUG_FOUND events)
│   ├── ADO capstone wiring (bug logging, validation)
│   └── Scoring engine (evaluateSubmission, result modal)
├── Build pipeline (node build.js → dist.html)
├── Chrome extension (sprint prompt helper)
└── Workspaces (IDB-backed window layout persistence)

V2: (No OS simulator — dropped in V2 redesign)
Current: (No OS simulator — out of scope)
```

### 2.3 QA Validation Capabilities (Current Only)

```
Current Governed QA Pilot
├── Evidence checklists & linker (EC-*, EL-* rules)
├── Review packets & review intake
├── Broker system (plan, implementation, audit, MCP surface)
├── Custody framework (receipt index, lifecycle, live custody)
├── MCP handler registration & call-loop guard
├── Pipeline: layer registry, drift detection, health regression
├── Risk-based review depth (4 modes: none/light/standard/heavy)
├── Decision packets & startup surfaces
├── QA packet ingest (Librarian → QA Pilot bridge)
├── Milestone regression suite
├── Local training simulation (advisory-only)
├── Receipt store & registry change receipts
├── Owner decision/review receipts & startup surfaces
├── Snapshot update gate, seal authority gate, RCR closeout gate
└── Full workbench architecture (action handoff, export, review)
```

---

## 3. Capability Comparison Matrix

| Capability Area | V1 | V1.5 | V2 | Current | Epic Target | Classification |
|---|---|---|---|---|---|---|
| **Course/lesson runtime** | ✅ Full | ✅ Full | ✅ Full | ❌ | ✅ | **keep** (adapt from V2) |
| **Quiz engine** | ✅ Basic | ✅ Basic | ✅ Basic | ❌ | ✅ | **keep** (redesign as validation exercise) |
| **Progress tracking** | ✅ IDB | ✅ IDB | ✅ IDB | ❌ | ✅ | **keep** (adopt V2 approach) |
| **Student portal/catalog** | ✅ Basic | ✅ Basic | ✅ Full | ❌ | ✅ | **redesign** (for governed context) |
| **Admin course management** | ✅ Basic | ✅ Basic | ✅ Full | ❌ | ✅ | **redesign** (for governed context) |
| **JSON course packs** | ❌ | ❌ | ✅ Full | ❌ | ✅ | **keep** (V2 schema as foundation) |
| **Legacy content converter** | ❌ | ❌ | ✅ P4 | ❌ | ✅ | **keep** (reuse for V1→V3 migration) |
| **OS Simulator / Win11 shell** | ✅ Full | ✅ Full | ❌ | ❌ | ❌ | **retire** (separate concern) |
| **Capstone/scenario engine** | ✅ Full | ✅ Full | ❌ | ❌ | ❌ | **retire** (separate concern) |
| **Scoring engine** | ✅ Basic | ✅ Basic | ❌ | ❌ | ⚠️ | **defer** (post-epic) |
| **Certificate generation** | ✅ Print | ✅ Print | ✅ Basic | ❌ | ✅ | **redesign** (governed format) |
| **Chrome extension** | ✅ Sprint tool | ✅ | ❌ | ❌ | ❌ | **retire** (separate concern) |
| **Evidence checklists** | ❌ | ❌ | ❌ | ✅ Full | — | **keep** (existing) |
| **Review packets/intake** | ❌ | ❌ | ❌ | ✅ Full | — | **keep** (existing) |
| **Broker/MCP system** | ❌ | ❌ | ❌ | ✅ Full | — | **keep** (existing) |
| **Custody framework** | ❌ | ❌ | ❌ | ✅ Full | — | **keep** (existing) |
| **Risk-based review depth** | ❌ | ❌ | ❌ | ✅ Full | — | **keep** (existing) |
| **Training simulation** | ❌ | ❌ | ❌ | ✅ Basic | ✅ Expand | **keep** (expand from existing) |
| **Cross-project bridge** | ❌ | ❌ | ❌ | ✅ Full | — | **keep** (existing) |
| **Knowledge adapter** | ❌ | ❌ | ❌ | ❌ | ✅ Target | **new** (epic deliverable) |
| **Training package generator** | ❌ | ❌ | ❌ | ❌ | ✅ Target | **new** (epic deliverable) |
| **Training validation engine** | ❌ | ❌ | ❌ | ❌ | ✅ Target | **new** (epic deliverable) |
| **Learning paths** | ❌ | ❌ | ❌ | ❌ | ✅ Target | **new** (epic deliverable) |
| **Project training export** | ❌ | ❌ | ❌ | ❌ | ✅ Target | **new** (epic deliverable) |
| **Onboarding/help generation** | ❌ | ❌ | ❌ | ❌ | ✅ Target | **new** (epic deliverable) |

---

## 4. Classification Summary

### Keep (9)
Retain existing capability in the successor training system:

| Capability | Source | Rationale |
|------------|--------|-----------|
| Course/lesson runtime | V2 | Proven architecture, file-safe, JSON-driven |
| Quiz engine | V1/V2 | Core learning interaction, needs minor redesign |
| Progress tracking | V2 | IDB-based, works well, adopt as-is |
| JSON course packs | V2 | Schema-driven authoring, AI-friendly format |
| Legacy content converter | V2 | P4 converter works, reuse for V1→V3 migration |
| Training simulation | Current | Already exists (QA-PILOT-LOCAL-TRAINING-SIM-1), expand |
| Evidence/review pipeline | Current | Core governed QA Pilot, not replaced |
| Custody/broker framework | Current | Core governed QA Pilot, not replaced |
| Cross-project packet bridge | Current | Librarian ↔ QA Pilot pipeline, not replaced |

### Redesign (4)
Needs rework before inclusion in the successor:

| Capability | Source | What Changes |
|------------|--------|-------------|
| Student portal/catalog | V2 | Needs governance-aware authorization model |
| Admin course management | V2 | Needs governance-aware workflow (Owner approval gates) |
| Certificate generation | V1/V2 | Needs governed format with source lineage |
| Training artifact schemas | V2 | Course-pack-v1 schema needs adaptation for governed context (source refs, audience, validation status, ownership) |

### Retire (3)
Separate concern, not part of the training system:

| Capability | Source | Rationale |
|------------|--------|-----------|
| OS Simulator / Win11 shell | V1 | Standalone desktop simulation — out of scope for governed training |
| Capstone/scenario engine | V1 | Tied to OS simulator — out of scope |
| Chrome extension | V1 | Developer tooling — separate from training delivery |

### Defer (1)
Valid but out of scope for this epic:

| Capability | Source | When |
|------------|--------|------|
| Scoring/evaluation engine | V1 | Post-epic — after learning paths and validation are stable |

---

## 5. Architecture Recommendation

### Recommended Approach: Hybrid Adoption

The successor training system should **adopt V2's JSON course-pack model** as the foundational content format, wrapped in the **current governed QA Pilot's authority and validation framework**.

```
                  Knowledge Sources
           (Librarian canonical docs, schemas, governance)
                        │
                        ▼
           ┌─────────────────────────┐
           │   Knowledge Adapter     │  ← Sprint 3
           │  (read-only, provenance)│
           └─────────┬───────────────┘
                     │
                     ▼
           ┌─────────────────────────┐
           │   Training Content Model │  ← Sprint 4
           │  (schemas + validators)  │
           └─────────┬───────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌────────────┐ ┌──────────┐ ┌──────────┐
│  Package   │ │Validation│ │ Learning │ ← Sprints 5-8
│  Generator │ │  Engine  │ │  Paths   │
└────────────┘ └──────────┘ └──────────┘
        │            │            │
        └────────────┼────────────┘
                     ▼
           ┌─────────────────────────┐
           │   Training Packages      │  ← Sprint 9
           │  (governed, provenance)  │
           └─────────┬───────────────┘
                     │
                     ▼
           ┌─────────────────────────┐
           │   New Project           │
           │   Onboarding / Help     │
           └─────────────────────────┘
```

### Key Architectural Decisions

1. **Content format**: Adopt V2's course-pack-v1 JSON schema as the base, extending it with governance fields (source references, intended audience, validation status, ownership state, authority posture)

2. **Storage**: Use QA Pilot's existing `data/packets/` derived store pattern (from the ingest bridge), not V2's IndexedDB — keeping everything file-based and governed

3. **Authority**: Every training artifact is advisory until Owner-approved. No auto-publication. Model mirrors the existing QA Pilot advisory-only posture

4. **Source lineage**: Every artifact must answer "What Librarian sources created this?" — enforced at the schema/validator level, matching the pattern established in QA-PILOT-QA-PACKET-INGEST-1

5. **Validation**: Training fails validation deterministically — matching the QA-PILOT-MILESTONE-REGRESSION-SUITE-1 pattern

6. **Training sim expansion**: Build on QA-PILOT-LOCAL-TRAINING-SIM-1's existing foundation (scenario libraries, exercises, evaluation, completion evidence)

7. **No V1 OS simulator**: The OS simulator/scenario/capstone system is a separate product concern and is not included in this epic

---

## 6. Sprint Sequence (Restated)

| Phase | # | Sprint | Classification |
|-------|---|--------|----------------|
| **Reconciliation & Architecture** | 1 | QA-PILOT-TRAINING-SYSTEM-RECONCILIATION-PLAN-1 | ✅ Complete |
| | 2 | QA-PILOT-TRAINING-SYSTEM-ARCHITECTURE-1 | Awaiting authorization |
| **Knowledge Connection** | 3 | QA-PILOT-LIBRARIAN-KNOWLEDGE-ADAPTER-1 | Not started |
| | 4 | QA-PILOT-TRAINING-CONTENT-MODEL-1 | Not started |
| **Training Generation** | 5 | QA-PILOT-TRAINING-PACKAGE-GENERATOR-1 | Not started |
| | 6 | QA-PILOT-TRAINING-VALIDATION-ENGINE-1 | Not started |
| **Learning Experience** | 7 | QA-PILOT-LEARNING-PATHS-1 | Not started |
| | 8 | QA-PILOT-TRAINING-SIMULATION-EXPANSION-1 | Not started |
| **Project Bootstrap** | 9 | QA-PILOT-PROJECT-TRAINING-PACKAGE-EXPORT-1 | Not started |
| | 10 | QA-PILOT-TRAINING-SYSTEM-MCP-SURFACE-1 | Not started |
| **Operational Baseline** | 11 | QA-PILOT-TRAINING-SYSTEM-OPERATIONAL-BASELINE-1 | Not started |
