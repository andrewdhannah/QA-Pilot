# QA-PILOT-ORIGINAL-FRONTEND-PARITY-AUDIT-1 — Frontend Parity Audit

**Generated:** 2026-07-09
**Status:** complete_pending_owner_review
**Purpose:** Compare new browser assets against original QA Pilot frontend and identify what must be ported, reused, or redesigned.

---

## Executive Finding

The new browser assets (ledger #111–#124) established a **correct workflow architecture** (no-backend, JSON custody, local identity, deployment/result roundtrip) but replaced the **original QA Pilot product design** with a minimal greenfield UI. The original frontend — 1,064-line splash, 5,065-line admin dashboard, 3,693-line portal, 3,261-line course runtime, 933-line CSS framework, 969-line DB layer — was not ported, reused, or adapted.

**Sealed workflow = functional. Frontend = replaced, not migrated.**

---

## 1. Splash / Landing Page

| Aspect | Original (`index.html`) | New (`index.html`) | Gap |
|--------|------------------------|-------------------|-----|
| Lines of code | **1,064** (35.7KB) | 303 (10.8KB) | −72% |
| Login/auth flow | Full login/create-account (151 refs) | Anti-login (no account system) | Intentional — governance change |
| Course catalog entry | Course listing, placement survey, path auto-healer | 3 mode buttons (Solo, Import, Admin) | Different paradigm |
| Visual design | Full CSS framework (`css/main.css` 933 lines) | Inline styles (~80 lines) | **Major — no design parity** |
| Brand assets | `favicon.png`, `favicon.svg` | None | **Missing** |
| i18n support | 6 language files (2,630 lines French) | None | **Missing** |
| UX patterns | Topbar, username display, sign-out | Minimal card layout | **Major parity gap** |

**Verdict: Workflow preserved. Design completely replaced.**

---

## 2. Admin Console

| Aspect | Original (`admin/` 6 files) | New (`admin.html`) | Gap |
|--------|---------------------------|-------------------|-----|
| Dashboard | **`dashboard.html` — 5,065 lines, 214KB** | Single page, ~347 lines | **−93% — original had full admin suite** |
| Course assignment | `assign.html` — 617 lines, 28KB | Inline tab, ~50 lines of UI | Reduced |
| Content editor | `editor.html` — 216 lines, 8KB | Not present | **Missing** |
| Bug lab | `bugs.html` — 131 lines, 6KB | Not present | **Missing** (legacy concept) |
| Admin nav | Tabbed interface, full admin navigation | 4-tab minimal layout | Simplified |
| Data management | Full IndexedDB CRUD, search/filter/sort/batch | localStorage basic state | Reduced |

**Verdict: Admin suite was 6 files / ~300KB. New version is 1 file / 15KB. No design parity.**

---

## 3. Learner Portal

| Aspect | Original (`portal.html`) | New (`identity.html` + `catalog.html`) | Gap |
|--------|-------------------------|----------------------------------------|-----|
| Portal size | **3,693 lines, 141KB** | 86 + 71 = 157 lines | **−96%** |
| Course catalog | Full course grid with cards, descriptions, enrollment | Simple list of assigned packages | Reduced |
| Enrollment flow | Click to enroll, progress tracking, resume | Identity selection from deployment JSON | Different model |
| Certificate | `certificate.html` — print-to-PDF, score ring, breakdown | Not present | **Missing** |
| Search/filter | Text search, filter pills, sort, batch actions | None | **Missing** |
| Progress display | Per-course progress bars, completion status | Basic percentage | Reduced |
| Placement survey | Survey → path auto-healer | Not present | **Missing** (legacy concept) |

**Verdict: Portal was a full product experience. New version is a minimal assignment list.**

---

## 4. Course Runtime

| Aspect | Original (`course-view.html`) | New (`course-view.html`) | Gap |
|--------|------------------------------|-------------------------|-----|
| Runtime size | **3,261 lines, 121KB** | 153 lines, 7.8KB | **−95%** |
| Lesson structure | Chaptered lessons, sidebar, resume, time tracking | Linear section navigation | Reduced |
| Quiz engine | 230 quiz/question references | **0 quiz references** | **Missing entirely** |
| Scoring | Score tracking, pass/fail, results | None | **Missing** |
| Section types | Text, quiz, code exercise, reference, diagram | Text only | Reduced |
| Progress tracking | Per-lesson completion, 15s read gate, resume | Per-section checkbox | Reduced |

**Verdict: Original had a full interactive learning runtime with quizzes, scoring, and progress. New version is a text reader.**

---

## 5. Quiz / Testing Flow

| Aspect | Original | New | Gap |
|--------|----------|-----|-----|
| Quiz mechanics | Multiple choice, score tracking, correct/incorrect feedback | **Not implemented** | **Entirely missing** |
| Question types | Quiz, bug-lab scenarios, validation exercises | None | **Missing** |
| Scoring engine | `evaluateSubmission()`, result modals | None | **Missing** |
| Exercises | Per-section exercises in course packs | Present in schema but **not rendered** in UI | **Missing in runtime** |

**Verdict: Quiz/testing is the largest functional gap. The entire interactive learning layer was not carried forward.**

---

## 6. Navigation & Visual Language

| Aspect | Original | New | Gap |
|--------|----------|-----|-----|
| CSS framework | `main.css` — 933 lines, 29KB (design tokens, theme, layout) | Inline `<style>` — ~80 lines | **No design system** |
| Theme | Light/dark theme support, fidelity modes | Single dark theme | Reduced |
| Layout | Topbar, sidebar, content area | Simple stacked card layout | Simplified |
| Icons | Favicon, SVG icons | Unicode emoji only | Reduced |
| Responsive | Full responsive layout | Basic mobile-friendly | Reduced |
| i18n | 6 language files | None | **Missing** |
| Build pipeline | `build.js` — inlines all JS/HTML into `dist.html` | No build step | Different approach |

**Verdict: The entire visual design language from the original was not preserved.**

---

## 7. File Structure Comparison

| Original V1 Files | New Browser Assets | Status |
|-------------------|-------------------|--------|
| `index.html` (1,064 lines) | `index.html` (303 lines) | ❌ Replaced, not ported |
| `admin/dashboard.html` (5,065 lines) | `admin.html` (347 lines, combined) | ❌ Replaced, not ported |
| `admin/assign.html` (617 lines) | (merged into admin.html) | ⚠️ Reduced |
| `admin/editor.html` (216 lines) | — | ❌ Not migrated |
| `admin/bugs.html` (131 lines) | — | ❌ Not migrated |
| `portal.html` (3,693 lines) | `identity.html` + `catalog.html` (157 lines combined) | ❌ Replaced, not ported |
| `course-view.html` (3,261 lines) | `course-view.html` (153 lines) | ❌ Replaced, quiz layer missing |
| `certificate.html` (1,100+ lines) | — | ❌ Not migrated |
| `css/main.css` (933 lines) | Inline styles | ❌ Replaced |
| `js/db.js` (969 lines) | Inline localStorage | ❌ Replaced |
| `js/app.js` (502 lines) | — | ❌ Not migrated |
| i18n (6 files, ~3,800 lines) | — | ❌ Not migrated |
| `favicon.*` (2 files) | — | ❌ Not migrated |

---

## 8. Reusable Components Identified

| Component | Original Path | Lines | Reusable? | Notes |
|-----------|--------------|-------|-----------|-------|
| CSS design tokens | `css/main.css` | 933 | **Yes** | Full design system with theme variables |
| DB layer | `js/db.js` | 969 | **Partially** | IndexedDB logic could be adapted to localStorage |
| Course runtime shell | `course-view.html` | 3,261 | **Partially** | Lesson rendering structure reusable, auth parts need stripping |
| Portal catalog | `portal.html` | 3,693 | **Partially** | Course card layout, enrollment flow reusable |
| Admin dashboard | `admin/dashboard.html` | 5,065 | **Partially** | Tab layout, data tables, filter patterns reusable |
| i18n framework | `js/i18n.js`, `lang-*.js` | ~3,800 | **Yes** | Separated from auth, reusable language system |
| Build pipeline | `build.js` | ~400 | **Partially** | Inlining logic reusable but static hosting reduces need |
| Favicon/brand | `favicon.png`, `favicon.svg` | — | **Yes** | Direct port |

---

## 9. Migration Plan

### Phase 0: Asset Port (No-Design-Change)

| Sprint | Scope | Source |
|--------|-------|--------|
| QA-PILOT-ORIGINAL-ASSET-INVENTORY-1 | Copy CSS, favicon, i18n files. No behavior change | `css/main.css`, `favicon.*`, `i18n.js`, `lang-*.js` |

### Phase 1: Design Port (Visual Parity)

| Sprint | Scope | Source → Target |
|--------|-------|-----------------|
| QA-PILOT-ADMIN-CONSOLE-DESIGN-PORT-1 | Port original admin layout, tabs, tables to new admin.html | `admin/dashboard.html`, `admin/assign.html` → `admin.html` |
| QA-PILOT-LEARNER-PORTAL-DESIGN-PORT-1 | Port original portal course grid, cards, enrollment | `portal.html` → `catalog.html` + `identity.html` |
| QA-PILOT-COURSE-RUNTIME-DESIGN-PORT-1 | Port original lesson layout, sidebar, progress | `course-view.html` → `course-view.html` |

### Phase 2: Functional Port (Feature Parity)

| Sprint | Scope | Source → Target |
|--------|-------|-----------------|
| QA-PILOT-QUIZ-FLOW-PORT-1 | Port quiz engine, scoring, feedback | `course-view.html` (quiz sections) → `course-view.html` |
| QA-PILOT-CERTIFICATE-PORT-1 | Port certificate generation | `certificate.html` → new file |
| QA-PILOT-I18N-PORT-1 | Wire i18n framework into browser assets | `i18n.js`, `lang-*.js` → all HTML pages |

### Phase 3: Integration & Baseline

| Sprint | Scope |
|--------|-------|
| QA-PILOT-BROWSER-WORKFLOW-INTEGRATION-1 | Merge ported design with sealed workflow (deployment JSON, local identity, result export) |
| QA-PILOT-ORIGINAL-FRONTEND-OPERATIONAL-BASELINE-1 | Lock migrated system with design parity checklist |

---

## 10. Key Rule for Future Implementation

> **The goal is design/product migration, not greenfield replacement.**
>
> Before creating any new HTML/CSS/JS, agent must check the original QA Pilot frontend at `Desktop/openwork/QA Pilot/` for a reusable component, layout, or pattern. Any replacement UI must be justified with file-level evidence showing why the original component cannot be reused under the browser-only governance model.
