# QA-PILOT-ADMIN-I18N-WIRING-1 — Admin Page I18N Wiring

**Type:** implementation / i18n wiring
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** implementation
**Boundary:** QA Pilot-local
**Librarian impact:** none
**Dependencies:** #170 sealed (QA-PILOT-CORE-I18N-WIRING-1)

---

## Purpose

Complete i18n wiring for the remaining admin surfaces: `assign.html`, `bugs.html`, `editor.html`, `simple.html`. These are active admin pages that were not included in the core sprint (#170).

---

## Scope

### Pages In Scope

| Page | Estimated Strings | Notes |
|------|-------------------|-------|
| `assign.html` | ~6 | Navigation labels, form fields, buttons |
| `bugs.html` | ~6 | Bug form labels, filter text |
| `editor.html` | ~4 | Editor interface labels |
| `simple.html` | ~4 | Simplified dashboard labels |

### What This Sprint Does

- Add ~20 new keys to lang-en.js and lang-fr.js
- Wire hardcoded strings to `__('key')` calls
- Add language toggle to each admin page
- Add i18n script loading to each admin page
- Validate EN/FR parity

### Explicit Non-Scope

| Excluded | Reason |
|----------|--------|
| Legacy 14-page assessment | Separate lifecycle (assessment, not implementation) |
| App module audit | Separate lifecycle |
| Translation architecture changes | Out of scope |
| UI redesign | Out of scope |

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| ADMIN-I18N-1 | All identified admin strings replaced |
| ADMIN-I18N-2 | EN/FR parity maintained |
| ADMIN-I18N-3 | Existing admin behavior preserved |
| ADMIN-I18N-4 | Language toggle verified on each admin page |
| ADMIN-I18N-5 | No legacy pages modified |
| ADMIN-I18N-6 | Evidence produced |

---

## Evidence Contract

This sprint produces exactly:

```
docs/sprints/QA-PILOT-ADMIN-I18N-WIRING-1-EVIDENCE.md
```

Containing:
- Keys added per page
- Language toggle verification
- EN/FR parity check
- Scope compliance confirmation

---

## Resulting State

| Layer | After Core (#170) | After Admin |
|-------|-------------------|-------------|
| Core pages | ✅ i18n wired | ✅ i18n wired |
| Admin pages | ⚠️ dashboard only | ✅ all 5 admin pages |
| All active pages | ~60% i18n coverage | ~80% i18n coverage |
| Legacy pages (14) | ❌ Not touched | ❌ Not touched |

---

## Ledger

**Status:** ✅ AUTHORIZED — Owner-authorized 2026-07-20
**Authorized by:** Andrew Hannah
**Ledger entry:** #171 (authorized)
