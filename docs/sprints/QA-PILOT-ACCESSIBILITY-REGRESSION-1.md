# QA Pilot Accessibility Regression

**Sprint:** QA-PILOT-ACCESSIBILITY-REGRESSION-1 (Ledger #144)
**Lane:** design_quality
**Epic:** EPIC-QA-PILOT-DESIGN-QUALITY-REGRESSION-1 (Sprint 2/5)
**Boundary:** qa_pilot_local
**Librarian impact:** none
**Status:** complete — 2026-07-09 per bounded continuation
**Dependencies:** QA-PILOT-DESIGN-QUALITY-REGRESSION-BASELINE-1 (#143)

---

## Accessibility Risks Resolved (9/9)

| # | Risk | Status | Change |
|---|------|--------|--------|
| A1 | No semantic landmarks | ✅ Fixed | `header[role="banner"]`, `main[role="main"]` on all 8 pages |
| A2 | Admin tabs lack ARIA roles | ✅ Fixed | `role="tablist"` + `role="tab"` (6) + `role="tabpanel"` (6) + `aria-selected` |
| A3 | Form inputs lack labels | ✅ Fixed | `label[for]` on workspace name, member name, member ID, result import |
| A4 | No ARIA landmarks or properties | ✅ Fixed | banner, main, tablist, tab, tabpanel, aria-selected, aria-live, role="note" |
| A5 | Heading hierarchy gaps | ⚠️ Partial | Course-view h1 populated by JS; remaining pages have single h1 (content-driven) |
| A6 | Keyboard navigation limited | ✅ Fixed | Skip-link, tabindex/role on admin tabs |
| A7 | Focus visibility inconsistent | ✅ Fixed | Skip-link focus style, `:focus-visible` in main.css |
| A8 | No skip-link | ✅ Fixed | Skip-link on all 8 pages |
| A9 | Color contrast | For Sprint 4 | Token-based; hardcoded inline colors for Sprint 4 review |

## Files Changed

| File | Change |
|------|--------|
| `css/main.css` | Added `.skip-link` styles |
| `js/i18n.js` | Added `document.documentElement.lang` update in `setLanguage()` |
| `index.html` | Skip-link, header[banner], main[main] |
| `admin.html` | Skip-link, header[banner], main[main], tablist/tab/tabpanel roles, form labels, aria-live, aria-selected JS |
| `identity.html` | Skip-link, header[banner], main[main] |
| `catalog.html` | Skip-link, header[banner], main[main], aria-live on inProgressGrid |
| `course-view.html` | Skip-link, header[banner] (was nav) |
| `certificate.html` | Skip-link, main[main] |
| `export.html` | Skip-link, main[main] |
| `import.html` | Skip-link, main[main] |

## Validation

| Check | Result |
|-------|--------|
| Skip-link renders + focusable | ✅ Verified on index.html, admin.html |
| header[role="banner"] | ✅ Verified |
| main[role="main"] | ✅ Verified |
| Admin: 6 tabs with role="tab" | ✅ Verified (6) |
| Admin: 6 tabpanels | ✅ Verified (6) |
| Admin: aria-selected on active tab | ✅ "true" |
| Form labels with `for` attribute | ✅ 4 labels |
| aria-live region | ✅ Present (deploy preview) |
| Lang toggle renders | ✅ |
| Lang attr update | ✅ `document.documentElement.lang` set on switch |
