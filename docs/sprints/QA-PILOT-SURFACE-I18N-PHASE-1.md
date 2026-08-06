# QA-PILOT-SURFACE-I18N-PHASE-1 — Combined Surface I18N Migration (Phase 1)

**Type:** implementation / i18n migration
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** implementation
**Boundary:** QA Pilot-local
**Librarian impact:** none
**Dependencies:** #175 sealed; Owner decisions on QASimulator, capstone-2, desktop, START_Me_Up

---

## Purpose

Begin i18n migration for the combined QASimulator/capstone-2 surface. Due to the shared 16-module dependency (confirmed by #175), these two surfaces must be migrated together.

**Phase 1 scope:** Wire QASimulator.html (canonical surface) to i18n. capstone-2 migration and app module wiring deferred to Phase 2.

---

## Scope

### Included

| Area | Action |
|------|--------|
| QASimulator.html | Add i18n scripts, language toggle, initI18n call |
| QASimulator strings | Wire hardcoded user-facing strings to `__('key')` |
| Keys | Add ~30 new keys to lang-en.js and lang-fr.js |

### Explicit Non-Scope

| Excluded | Reason |
|----------|--------|
| capstone-2 migration | Phase 2 |
| App module i18n wiring | Depends on surface migration completion |
| Desktop distribution | Already consolidated |
| Chrome extension | Deferred |

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| SI-1 | QASimulator.html wired to i18n |
| SI-2 | Language toggle functional |
| SI-3 | EN/FR parity maintained |
| SI-4 | Existing behavior preserved |
| SI-5 | No unrelated surfaces modified |
| SI-6 | Evidence produced |

---

**Status:** ✅ AUTHORIZED — Owner-authorized 2026-07-20
**Ledger entry:** #176 (authorized)
