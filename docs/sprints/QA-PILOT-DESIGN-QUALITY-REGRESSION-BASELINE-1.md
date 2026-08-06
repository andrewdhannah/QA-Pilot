# QA Pilot Design Quality Regression Baseline

**Sprint:** QA-PILOT-DESIGN-QUALITY-REGRESSION-BASELINE-1 (Ledger #143)
**Lane:** design_quality
**Epic:** EPIC-QA-PILOT-DESIGN-QUALITY-REGRESSION-1 (Sprint 1/5)
**Boundary:** qa_pilot_local
**Librarian impact:** none
**Status:** authorized — Owner-approved 2026-07-09 per OD-EPIC-QA-PILOT-DESIGN-QUALITY-REGRESSION-1-AUTHORIZATION
**Dependencies:** None

---

## Purpose

Inventory all 8 QA Pilot browser asset pages. Audit current design-quality posture, accessibility risks, responsive risks, EN/FR i18n risks, and static-browser custody boundaries. Document validation gaps. Do not implement redesigns unless trivial baseline hygiene.

## Scope — Included

1. Inspect all 8 browser asset pages
2. Evaluate design-quality posture (token usage, component class usage, visual consistency)
3. Evaluate accessibility risks (keyboard nav, focus visibility, semantic landmarks, headings, form labels, contrast, status messaging)
4. Evaluate responsive risks (narrow/default/wide viewport behavior)
5. Evaluate EN/FR language risk (toggle rendering, translation coverage)
6. Evaluate custody/static-browser boundaries
7. Document all validation gaps
8. Recommend Sprint 2 scope

## Scope — Excluded

- No redesigns unless trivial baseline hygiene
- No CSS token system changes
- No new features
- No backend
- No auth

## Acceptance Criteria

| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | All 8 pages inspected and inventoried | Page-by-page audit table |
| 2 | Design-quality risks documented | Risk table with severity |
| 3 | Accessibility risks documented | Explicit findings |
| 4 | Responsive risks documented | Explicit findings |
| 5 | EN/FR risks documented | Explicit findings |
| 6 | Custody/static-browser boundaries confirmed | No violations found |
| 7 | Validation gaps documented | Gap list |
| 8 | Sprint 2 recommendations provided | Recommendation section |

## Completion Report

### Pages Inspected (8/8)

| # | Page | File | Size |
|---|------|------|------|
| 1 | Splash/Startup | `index.html` | 9129 bytes |
| 2 | Admin Dashboard | `admin.html` | 370 lines |
| 3 | Learner Identity | `identity.html` | 123 lines |
| 4 | Training Portal | `catalog.html` | 162 lines |
| 5 | Course Runtime | `course-view.html` | 334 lines |
| 6 | Certificate | `certificate.html` | 100 lines |
| 7 | Result Export | `export.html` | 99 lines |
| 8 | Admin Import | `import.html` | 103 lines |

### Current Design-Quality Posture

| Dimension | Status | Details |
|-----------|--------|---------|
| CSS token usage | ✅ Good | All pages use `main.css` design tokens consistently |
| Component classes | ✅ Good | `.panel-purpose-label`, `.view-data-footer`, `.status-pill`, `.view-state-badge`, bento cards all present on pages where applicable |
| Design consistency | ✅ Uniform | All 8 pages share main.css tokens, font stacks, color palette |
| Inline style usage | ⚠️ Moderate | `admin.html`: 40 inline style attributes (mostly layout overrides for bento dashboard); `export.html`/`import.html`: 8 each; `index.html`: 7 |
| Data footers | ✅ Present | All 8 pages have `.view-data-footer` |
| Language toggle | ✅ Fixed | All 8 pages render EN/FR toggle (Defect #1 resolved) |

### Accessibility Risks Found

| # | Risk | Severity | Pages Affected | Description |
|---|------|----------|----------------|-------------|
| A1 | **No semantic landmarks** | High | All 8 | No `<main>`, `<nav>`, `<header>`, `<footer>`, or `role="main"`/`role="banner"` on any page. Screen readers have no way to navigate page regions. |
| A2 | **Tab elements lack ARIA roles** | High | admin.html | 6 admin tab buttons have no `role="tab"` or `role="button"`. Only `onclick` handlers — keyboard nav is degraded. |
| A3 | **Form inputs lack labels** | High | admin.html, index.html, course-view.html | admin.html has 4 inputs with no `<label for="...">`; index.html file input has no label; course-view.html textarea has no visible label. |
| A4 | **No ARIA landmarks or properties** | High | All 8 | Zero `aria-*` attributes across all pages. No `aria-label`, `aria-describedby`, `aria-live` regions. |
| A5 | **Heading hierarchy gaps** | Medium | Several | `index.html`: only 1 heading (h1). `catalog.html`: only 1 heading (h1). `certificate.html`: h1 only. `course-view.html`: dynamic h1 populated by JS. Heading order skips levels on some pages. |
| A6 | **Keyboard navigation limited** | High | All | Mode cards and interactive elements use `onclick` on `<div>` elements without `tabindex` or `role="button"`. Focusable elements are limited to `<button>` and `<input>` elements only. |
| A7 | **Focus visibility not tested** | Medium | All | `:focus-visible` is defined in main.css but many interactive elements are `<div>` with `onclick` — focus management is inconsistent. |
| A8 | **No skip-link** | Medium | All 8 | No skip-to-content link on any page. |
| A9 | **Color contrast not explicitly tested** | Low | All | Token-based colors generally pass (blue `#2563eb` on white) but some hardcoded inline colors should be verified against WCAG AA. |

### Responsive Risks Found

| # | Risk | Severity | Pages Affected | Description |
|---|------|----------|----------------|-------------|
| R1 | **Media queries missing** | Medium | export.html, identity.html, import.html, index.html | These pages lack `@media` queries for responsive breakpoints. Behavior on narrow viewports is untested. |
| R2 | **Narrow viewport untested** | Medium | All | Only admin.html, catalog.html, certificate.html, course-view.html have media queries. No page has been explicitly tested at <768px. |
| R3 | **Wide viewport consistency** | Low | All | `.container` width tokens exist (narrow/wide) but not all pages use them. Some pages use hardcoded `max-width` values. |

### EN/FR Language Risks Found

| # | Risk | Severity | Pages Affected | Description |
|---|------|----------|----------------|-------------|
| L1 | **No `__()` translation calls in text** | Medium | All 8 | All page text is hardcoded in HTML templates. The `__()` translation function exists but is never called for UI text. Language toggle switches `currentLang` but text does not re-render. |
| L2 | **Page text does not re-render on language switch** | Medium | All 8 | The `setLanguage()` function changes `currentLang` but pages do not re-render their text. Only newly rendered content would reflect the language switch. |
| L3 | **No `lang` attribute update on language switch** | Low | All 8 | `document.documentElement.lang` is never updated when language toggles (stays "en"). |

### Custody/Static-Browser Boundary Confirmation

| Check | Result |
|-------|--------|
| No backend dependencies | ✅ Confirmed — all state via localStorage |
| No auth/password fields | ✅ Confirmed — no login forms, no password inputs |
| No install requirements | ✅ Confirmed — all pages open from `file://` |
| No cross-project write | ✅ Confirmed — no Librarian file paths referenced |
| No Librarian mutation | ✅ Confirmed |
| JSON import/export model | ✅ Confirmed — deployment-v1 and result-v1 schemas enforced |
| Local identity model | ✅ Confirmed — identity notes on every page |
| Advisory labeling | ✅ Confirmed — certificates and results marked advisory |

### Validation Gaps

| # | Gap | Priority | Recommended Sprint |
|---|-----|----------|-------------------|
| G1 | No accessibility audit framework exists | High | Sprint 2 (accessibility) |
| G2 | No screen-reader testing done | Medium | Sprint 2 (accessibility) |
| G3 | No responsive viewport testing | High | Sprint 4 (responsive) |
| G4 | No i18n/translation coverage analysis | Medium | Sprint 2 or 4 |
| G5 | No visual regression checklist | Medium | Sprint 3 (visual harness) |
| G6 | No keyboard navigation validation | High | Sprint 2 (accessibility) |

### Recommended Sprint 2 Scope

Based on the audit findings, **Sprint 2 (QA-PILOT-ACCESSIBILITY-REGRESSION-1)** should focus on:

1. **Add semantic landmarks** to all 8 pages (`<main>`, `<header>`, `<footer>`, `<nav>`)
2. **Add ARIA roles** to admin tabs (`role="tab"`, `role="tablist"`, `aria-selected`) and interactive elements (`role="button"`)
3. **Add form labels** to all inputs (`<label for="...">` or `aria-label`)
4. **Add skip-link** to all pages
5. **Improve keyboard navigation** — add `tabindex` and keyboard event handlers to interactive divs
6. **Fix heading hierarchy** — ensure sequential h1→h2→h3 order on every page
7. **Add `aria-live` regions** for dynamic content (deployment preview, results dashboard, exercise feedback)
8. **Add `lang` attribute update** to i18n toggle
9. Update `document.title` on language switch for translated page titles

All changes must preserve static browser behavior and not introduce backend dependencies.

### Files Changed

None. Sprint 1 is an inspection-only sprint. No files were modified.

### Validation Results

| Check | Result |
|-------|--------|
| All 8 pages inspected | ✅ |
| Design-quality risks documented | ✅ 6 categories |
| Accessibility risks documented | ✅ 9 findings (A1-A9) |
| Responsive risks documented | ✅ 3 findings (R1-R3) |
| EN/FR risks documented | ✅ 3 findings (L1-L3) |
| Custody/static-browser boundaries | ✅ Confirmed — no violations |
| Validation gaps documented | ✅ 6 gaps (G1-G6) |
| Sprint 2 recommendation provided | ✅ 9 items |

### Unresolved Issues

None. All findings are documented as risks for remediation in Sprints 2-5.

### Owner Review Posture

| Aspect | Status |
|--------|--------|
| Sprint scope respected | ✅ Inspection only — no page changes |
| No sealed epic files mutated | ✅ Referenced by reference only |
| Sprint 2 not advanced | ✅ Not started — awaiting Owner direction |
| Authority boundaries preserved | ✅ |

## Authorization Reference

- **Decision ID:** `OD-EPIC-QA-PILOT-DESIGN-QUALITY-REGRESSION-1-AUTHORIZATION`
- **Owner:** Andrew Hannah
- **Date:** 2026-07-09
