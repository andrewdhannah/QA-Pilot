# QA-PILOT-APP-SURFACE-GAP-AUDIT-1 — App Surface Gap Audit

**Generated:** 2026-07-08
**Epic:** EPIC-QA-PILOT-APP-SURFACE-MIGRATION-1
**Status:** complete_pending_owner_review

---

## 1. Source Inventory

| Source | Location | Type | State |
|--------|----------|------|-------|
| V1 (QA-Pilot) | `Desktop/openwork/QA Pilot/` | Vanilla JS web app | Complete, file-safe, IndexedDB |
| V1.5 (QA-PilotV1_5) | `Desktop/OW Old Folder/QA-PilotV1_5/` | Vanilla JS web app | Transitional, near-identical to V1 |
| V2 (qa-pilot-v2) | `Desktop/openwork/QA-PilotV2/`, `Desktop/CarbideFrame/qa-pilot/` | Vanilla JS course platform | Complete, JSON course packs |
| Current governed | `Desktop/CarbideFrame/active/qa-pilot/` | Python/script pipeline | 109 sealed sprints, no app UI |

## 2. Existing Review Document Summary

The reconciliation report (`docs/planning/QA-PILOT-TRAINING-SYSTEM-RECONCILIATION-PLAN-1.md`, sealed #93) already inventories all generations and classifies 23 capabilities. This audit uses that as the starting index and adds file-level verification.

## 3. Feature Matrix (V1 + V2 + Current)

### Admin Panel

| Version | Status | Evidence |
|---------|--------|----------|
| **V1** | ✅ Complete | `admin/index.html` (14KB), `admin/dashboard.html` (214KB), `admin/assign.html` (28KB), `admin/editor.html` (8KB), `admin/bugs.html` (6KB) — full admin suite with dashboard, course assignment, content editor, bug lab |
| **V1.5** | ✅ Complete | Same files as V1, minor diffs in build pipeline |
| **V2** | ✅ Complete | `platform/admin.html` (300 lines) — course management: import, validate, preview, enable, search, filter, sort, batch actions |
| **Current** | ❌ Absent | No admin UI — current is a Python validation pipeline with no web interface |

**Verdict: Complete in V1/V2. Absent in current. Candidate for redesign with governed auth.**

### Group Login

| Version | Status | Evidence |
|---------|--------|----------|
| **V1** | ✅ Complete | `index.html` has 140 login/auth references. Login/create-account flow with IndexedDB student records |
| **V1.5** | ✅ Complete | Same as V1 |
| **V2** | ✅ Complete | Portal enrollment flow via `platform/portal.html` |
| **Current** | ❌ Absent | No authentication mechanism — governed by Librarian project selection, not user accounts |

**Verdict: Complete in V1/V2. Absent in current. Governance model eliminates need for app-level login.**

### Student Portal

| Version | Status | Evidence |
|---------|--------|----------|
| **V1** | ✅ Complete | `portal.html` — 140KB, 3,693 lines. Course catalog with enrollment |
| **V1.5** | ✅ Complete | Same as V1 |
| **V2** | ✅ Complete | `platform/portal.html` — renders enabled course packs, enrollment-to-runtime path |
| **Current** | ❌ Absent | No student-facing portal |

**Verdict: Complete in V1/V2. Absent in current.**

### Course Assignment

| Version | Status | Evidence |
|---------|--------|----------|
| **V1** | ✅ Complete | `admin/assign.html` — 28KB assignment management UI |
| **V1.5** | ✅ Complete | Same |
| **V2** | ✅ Complete | Admin course management includes enable/disable/archive workflows |
| **Current** | ❌ Absent | No course assignment capability |

**Verdict: Complete in V1/V2. Absent in current.**

### Progress Tracking

| Version | Status | Evidence |
|---------|--------|----------|
| **V1** | ✅ Complete | `js/db.js` — 254 references to progress/enroll/student/score/quiz. IndexedDB `QAPilotDB` with full student progress, quiz results, settings |
| **V1.5** | ✅ Complete | Same |
| **V2** | ✅ Complete | `platform/js/db.js` — 193 references. IndexedDB `course_packs` store, enrollment and progress tracking |
| **Current** | ❌ Absent | No progress tracking — current tracks validation evidence, not student progress |

**Verdict: Complete in V1/V2. Absent in current. Different domain (student vs. validation).**

### Quiz/Runtime Flow

| Version | Status | Evidence |
|--------|--------|----------|
| **V1** | ✅ Complete | `course-view.html` — 120KB, 3,261 lines, 529 references to lesson/chapter/module/quiz/question. Full runtime with quizzes, chapter navigation, sidebar, resume, time tracking |
| **V1.5** | ✅ Complete | Same |
| **V2** | ✅ Complete | `platform/course-view.html` — runtime loader adapts V2 pack to runtime shape. Modules, chapters, quizzes |
| **Current** | ❌ Absent | No runtime — current is not a training delivery platform |

**Verdict: Complete in V1/V2. Absent in current. Core candidate for training system adoption.**

### Course Pack Management

| Version | Status | Evidence |
|---------|--------|----------|
| **V1** | ⚠️ Partial | Lessons embedded in HTML, not JSON course packs |
| **V1.5** | ⚠️ Partial | Same |
| **V2** | ✅ Complete | `course-packs/` — 12 JSON course packs, `course-pack-v1` schema, admin import/validate/preview/enable workflow |
| **Current** | ✅ Training packs | Training Package Generator produces `training-pack-v1` schema — 1 pilot pack (TP-LIBRARIAN-PILOT-1) |

**Verdict: V2 has the mature course pack system. Current training system adopted the concept with governed extensions.**

### Legacy Migration/Converter Tools

| Version | Status | Evidence |
|---------|--------|----------|
| **V1** | ❌ None | No converter |
| **V1.5** | ❌ None | No converter |
| **V2** | ✅ Complete | `scripts/convert-legacy-courses.html`, `scripts/convert-v1_5-to-course-pack-v1.html` — converts V1/V1.5 content to course-pack-v1. 12 packs converted |
| **Current** | ✅ Training packs | Existing training schema (`training-content-v1`) with governance extensions |

**Verdict: V2 converter exists. Would need adaptation for training-content-v1 schema.**

## 4. Current Governed QA Pilot Comparison

| Feature | V1/V2 Status | Current QA Pilot | Gap |
|---------|-------------|-----------------|-----|
| Admin panel | ✅ Complete | ❌ Absent | **MISSING** — needs governed redesign |
| Group login | ✅ Complete | ❌ N/A | N/A — governance model replaces app login |
| Student portal | ✅ Complete | ❌ Absent | **MISSING** — candidate for training system expansion |
| Course assignment | ✅ Complete | ❌ Absent | **MISSING** — candidate for learning paths |
| Progress tracking | ✅ Complete | ❌ Absent | **MISSING** — different domain (student vs validation) |
| Quiz/runtime flow | ✅ Complete | ❌ Absent | **MISSING** — training package generator creates material, no delivery runtime |
| Course pack mgmt | ✅ Complete | ✅ Training packs | **PARTIAL** — training packs exist, course pack management UI does not |
| Legacy converter | ✅ Complete | ⚠️ Partial | **ADAPT** — V2 converter exists, needs retargeting to training-content-v1 |

## 5. Migration Backlog (Prioritized)

| Priority | Feature | Complexity | Depends On | Notes |
|----------|---------|-----------|------------|-------|
| **P0** | Course/runtime delivery | High | Training generator exists | Runtime to render generated training packs — bridges Training System to end users |
| **P1** | Course pack management UI | Medium | Existing V2 admin | Adapt V2 admin to governed context (import, validate, preview, enable training packs) |
| **P2** | Admin panel (governed) | High | P1 | Redesign admin with governance-aware auth (Owner-only actions gated) |
| **P3** | Student portal | Medium | P1 | Port V2 portal to governed training pack model |
| **P4** | Progress tracking | Medium | P3 | Adapt V2 progress tracking for governed training context |
| **P5** | Quiz/runtime enhancement | Medium | P0 | Enhance training content model with interactive quiz types |
| **P6** | Legacy converter retarget | Low | — | Adapt V2 converter from course-pack-v1 to training-content-v1 |
| **N/A** | Group login | — | — | Not applicable — governance model replaces app-level auth |

## 6. Recommended Sprint Sequence

| Sprint | Focus | Effort |
|--------|-------|--------|
| APP-SURFACE-RUNTIME-DELIVERY-1 | Training pack runtime rendering (course-view equivalent for training-content-v1) | High |
| APP-SURFACE-COURSE-MANAGEMENT-1 | Admin course pack management UI (import/validate/enable) | Medium |
| APP-SURFACE-PORTAL-1 | Student/trainee portal with catalog and enrollment | Medium |
| APP-SURFACE-PROGRESS-1 | Progress tracking for governed training | Medium |
| APP-SURFACE-QUIZ-ENHANCEMENT-1 | Interactive quiz types in training content model | Medium |
| APP-SURFACE-CONVERTER-1 | Legacy converter retargeting | Low |

## 7. Authority Boundaries (Migration)

- Training runtime renders advisory content only — no seal/approve/merge
- Admin actions (enable/disable packs) require Owner authorization
- Student progress is local tracking only — no cross-project visibility
- No Librarian mutation from any migrated app surface
- All migrated surfaces retain advisory-only posture
