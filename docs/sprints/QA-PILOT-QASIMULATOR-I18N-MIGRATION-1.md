# QA-PILOT-QASIMULATOR-I18N-MIGRATION-1 — QASimulator Source-Level I18N Migration

**Type:** implementation / i18n migration
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** implementation
**Boundary:** QA Pilot-local
**Librarian impact:** none
**Dependencies:** #176 sealed (build provenance validated — Outcome A: active pipeline)

---

## Purpose

Wire i18n into QASimulator.html at the source level. Modify `src/` files and `build.js`, then regenerate the bundle. No direct edits to the generated HTML.

---

## Scope

### Included

| # | Area | Action |
|---|------|--------|
| 1 | `build.js` | Add i18n.js, lang-en.js, lang-fr.js to bundle head section |
| 2 | `src/os-core.js` | Add `initI18n()`, `renderLangToggle()` calls |
| 3 | Source strings | Wire identifiable user-facing strings to `__('key')` |
| 4 | `js/lang-en.js`, `js/lang-fr.js` | Add QASimulator keys |
| 5 | Rebuild | `node build.js` — verify output matches expectations |

### Explicit Non-Scope

| Excluded | Reason |
|----------|--------|
| Direct edits to QASimulator.html | Bundle artifact — modifies build pipeline instead |
| capstone-2 migration | Separate track |
| Build output consolidation | Separate future sprint |
| Chrom extension | Lifecycle decision deferred |
| Desktop distribution | Build output dependency — future sprint |

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| QI18N-1 | Source-level strings identified |
| QI18N-2 | EN/FR keys added |
| QI18N-3 | Build regeneration succeeds |
| QI18N-4 | Generated QASimulator output verified |
| QI18N-5 | No manual bundle modifications |
| QI18N-6 | Shared modules regression checked |
| QI18N-7 | Evidence produced |

---

**Status:** ✅ AUTHORIZED — Owner-authorized 2026-07-20
**Authorized by:** Andrew Hannah
**Ledger entry:** #177 (authorized)
