# QA Pilot Design Language Baseline

**Sprint:** QA-PILOT-DESIGN-LANGUAGE-BASELINE-1 (Ledger #136)
**Lane:** design_refresh
**Epic:** EPIC-QA-PILOT-DESIGN-LANGUAGE-REFRESH-1 (Sprint 1/7)
**Boundary:** qa_pilot_local
**Librarian impact:** none
**Status:** authorized — Owner-approved 2026-07-09 per OD-EPIC-QA-PILOT-DESIGN-LANGUAGE-REFRESH-1-AUTHORIZATION
**Dependencies:** QA-PILOT-MIGRATED-FRONTEND-ROUNDTRIP-VALIDATION-1 (#135, complete)

---

## Purpose

Create the design-language baseline for the full epic. Before any pages are redesigned, establish the rules, reference points, and constraints.

## Scope — Included

1. Compare all 8 QA Pilot browser assets against the current Librarian dashboard design language
2. Document Librarian design tokens to inherit:
   - Bento card hierarchy (elevation levels, attention/standard/flat cards)
   - Status/readiness strip with pill indicators
   - Spacing scale, typography, radii, density system
   - Motion (entrance, stagger, pulse)
   - Light-theme palette (warm neutrals, blue accent)
3. Define QA Pilot-specific design rules:
   - Academy/training product identity retained
   - Light-theme native (no dark theme)
   - Browser-only constraints (no server rendering, no build step)
   - JSON custody model visually reinforced
4. Produce page-by-page redesign rules for each of the 8 pages
5. **Fix Defect #1 (medium):** `renderLangToggle()` called with element instead of string ID — fix call sites on all 8 pages so the EN/FR toggle renders
6. **Fix Defect #2 (low):** `export.html` and `import.html` missing "QA Pilot Academy" title branding and favicon references

## Scope — Excluded

- No page redesigns (deferred to sprints 2-6)
- No CSS token system changes (deferred to sprint 2)
- No new features
- No backend
- No auth
- No Librarian mutation

## Acceptance Criteria

| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | Design baseline document covers all 8 pages vs Librarian reference | Comparison table per page |
| 2 | Shared design rules defined | Documented in baseline doc |
| 3 | QA Pilot-specific rules defined | Documented constraints |
| 4 | Page-by-page redesign rules documented | Redesign rules per page |
| 5 | Defect #1 fixed (lang toggle renders on all pages) | `renderLangToggle('lang-toggle-container')` on all pages |
| 6 | Defect #2 fixed (export/import branding) | Titles say "QA Pilot Academy" + favicon added |
| 7 | All existing workflow steps unaffected | Quick spot-check of admin and learner flows |
| 8 | No backend/auth/install/Librarian mutation introduced | Verified |

## Completion Report

### Deliverables

| # | Deliverable | Status |
|---|-------------|--------|
| 1 | Design baseline document comparing all 8 pages vs Librarian | ✅ `docs/governance/QA-PILOT-DESIGN-LANGUAGE-BASELINE.md` |
| 2 | Librarian design tokens to inherit | ✅ Documented in baseline §2 |
| 3 | QA Pilot-specific design rules | ✅ Documented in baseline §3 (identity, browser, light-theme, layout) |
| 4 | Page-by-page redesign rules for all 8 pages | ✅ Documented in baseline §4 |
| 5 | Components to add vs keep (Librarian vs QA Pilot) | ✅ Documented in baseline §5-6 |
| 6 | Sprint sequence guidance for Sprints 2-7 | ✅ Documented in baseline §7 |

### Defect Remediation

| Defect | Before | After | Status |
|--------|--------|-------|--------|
| #1: EN/FR toggle never renders | `renderLangToggle(element)` — all 8 pages | `renderLangToggle('lang-toggle-container')` — all 8 pages | ✅ Fixed |
| #2: export/import missing Academy branding | `<title>QA Pilot — Export/Import Results</title>`, no favicon | `<title>QA Pilot Academy — Export/Import Results</title>`, `<link rel="icon" href="favicon.svg">` | ✅ Fixed |

### Changed Files (10 files)

| File | Change | Type |
|------|--------|------|
| `docs/schemas/browser-assets/index.html` | renderLangToggle: element → string ID | Defect fix |
| `docs/schemas/browser-assets/admin.html` | renderLangToggle: element → string ID | Defect fix |
| `docs/schemas/browser-assets/catalog.html` | renderLangToggle: element → string ID | Defect fix |
| `docs/schemas/browser-assets/certificate.html` | renderLangToggle: element → string ID | Defect fix |
| `docs/schemas/browser-assets/course-view.html` | renderLangToggle: element → string ID | Defect fix |
| `docs/schemas/browser-assets/identity.html` | renderLangToggle: element → string ID | Defect fix |
| `docs/schemas/browser-assets/export.html` | renderLangToggle fix + Academy title + favicon | Defect fix |
| `docs/schemas/browser-assets/import.html` | renderLangToggle fix + Academy title + favicon | Defect fix |
| `docs/governance/QA-PILOT-DESIGN-LANGUAGE-BASELINE.md` | Created — design baseline | New file |
| `docs/sprints/QA-PILOT-DESIGN-LANGUAGE-BASELINE-1.md` | Updated — completion report | Update |

### Validation

| Check | Result |
|-------|--------|
| renderLangToggle('lang-toggle-container') on all 8 pages | ✅ All 8 use string ID, no element refs |
| QA Pilot Academy title on all 8 pages | ✅ All 8 present |
| Favicon on all 8 pages | ✅ All 8 present |
| main.css on all 8 pages | ✅ All 8 present |
| No dark theme colors introduced | ✅ None |
| No backend/auth/install introduced | ✅ None |
| No Librarian mutation | ✅ None |
| No cross-project write | ✅ None |

### Unresolved Issues

None. Both defects from Sprint #135 are resolved. Sprint 2 (`QA-PILOT-DESIGN-TOKEN-AND-SHELL-REFRESH-1`) is ready to begin when authorized.

### Owner Review Posture

| Aspect | Status |
|--------|--------|
| Sprint scope respected | ✅ Baseline only — no page redesigns, no CSS changes |
| Defect remediation within scope | ✅ Both defects repaired as baseline hygiene |
| Sprint 2 not advanced | ✅ Not started — awaiting authorization |
| Not sealed | ✅ Not sealed — epic remains in progress |

## Authorization Reference

- **Decision ID:** `OD-EPIC-QA-PILOT-DESIGN-LANGUAGE-REFRESH-1-AUTHORIZATION`
- **Owner:** Andrew Hannah
- **Date:** 2026-07-09
- **Receipt:** `receipts/decision-resolutions/od-epic-qa-pilot-design-language-refresh-1-authorization.json`
