# EPIC-QA-PILOT-I18N-WIRING-1 — I18N Wiring

**Status:** ✅ Complete — all 5 sprints complete 2026-07-09. Awaiting Owner seal decision.
**Decision ID:** `OD-EPIC-QA-PILOT-I18N-WIRING-1-AUTHORIZATION`
**Receipt:** `receipts/decision-resolutions/od-epic-qa-pilot-i18n-wiring-1-authorization.json`
**Authorization type:** Bounded continuation (5 sprints)

## Purpose

Resolve the carried-forward I18N limitation: the EN/FR toggle changes language state and reloads, but page text remains hardcoded because visible UI strings are not wired through the existing `__()` translation function.

## Sprint Sequence

| # | Sprint | Purpose |
|---|--------|---------|
| 1 | QA-PILOT-I18N-WIRING-BASELINE-1 | Inventory hardcoded text, map dictionaries, produce wiring plan |
| 2 | QA-PILOT-I18N-CORE-DICTIONARY-1 | Extend/normalize translation dictionary |
| 3 | QA-PILOT-I18N-PAGE-WIRING-1 | Wire text through `__()` across all pages |
| 4 | QA-PILOT-I18N-RERENDER-AND-STATE-1 | Verify switch updates text, fix rerender |
| 5 | QA-PILOT-I18N-ROUNDTRIP-VALIDATION-1 | Validate EN/FR rendering, final report |

## Authority Boundaries

- No backend, auth, accounts, telemetry, publication, cross-project writes
- No sealed epic mutation
- No fake-live status
- Preserve layout, accessibility, existing behavior
