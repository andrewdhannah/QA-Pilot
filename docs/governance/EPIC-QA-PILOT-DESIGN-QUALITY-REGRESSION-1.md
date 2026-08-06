# EPIC-QA-PILOT-DESIGN-QUALITY-REGRESSION-1 — Design Quality Regression

**Status:** ✅ Sealed — Owner-approved 2026-07-09 per OD-EPIC-QA-PILOT-DESIGN-QUALITY-REGRESSION-1-BATCH-SEAL
**Decision ID:** `OD-EPIC-QA-PILOT-DESIGN-QUALITY-REGRESSION-1-AUTHORIZATION`
**Receipt:** `receipts/decision-resolutions/od-epic-qa-pilot-design-quality-regression-1-authorization.json`
**Authorization type:** Bounded continuation (5 sprints)
**Prior epic:** EPIC-QA-PILOT-DESIGN-LANGUAGE-REFRESH-1 (sealed #136-#142)

---

## Purpose

Perform a bounded post-refresh quality pass for the sealed QA Pilot design-language refresh. Verify visual consistency, accessibility, responsive behavior, EN/FR language behavior, and static-browser custody boundaries across the QA Pilot browser asset pages.

## Sprint Sequence

| # | Sprint | Purpose |
|---|--------|---------|
| 1 | QA-PILOT-DESIGN-QUALITY-REGRESSION-BASELINE-1 | Inventory all pages, audit design/accessibility/responsive/i18n/custody gaps |
| 2 | QA-PILOT-ACCESSIBILITY-REGRESSION-1 | Validate and remediate keyboard nav, focus, semantics, contrast, lang toggle accessibility |
| 3 | QA-PILOT-VISUAL-REGRESSION-HARNESS-1 | Create repeatable visual/page-state validation checklist/harness |
| 4 | QA-PILOT-RESPONSIVE-I18N-REGRESSION-1 | Validate viewport + EN/FR behavior. Remediate regressions |
| 5 | QA-PILOT-DESIGN-QUALITY-ROUNDTRIP-VALIDATION-1 | Final whole-epic validation and completion report |

## Authority Boundaries

- Do not reopen or mutate the sealed design-language epic except by reference.
- Do not add backend requirements, auth, passwords, accounts, telemetry, publication workflows, or cross-project writes.
- Do not introduce fake-live status.
- Do not remove existing functionality unless a defect requires it and the change is documented.
- Do not seal any sprint or the epic without explicit Owner decision.

## Stop Conditions

- Scope exceeded
- Backend/install/auth required
- Cross-project write required
- Librarian canonical file mutation required
- Sealed epic files mutated instead of referenced
