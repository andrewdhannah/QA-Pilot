# QA-PILOT-SIMPLE-LOGIN-I18N-MIGRATION-1 — Simple Login I18N Migration

**Type:** implementation / i18n wiring
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** implementation
**Boundary:** QA Pilot-local
**Librarian impact:** none
**Dependencies:** #172 sealed (legacy assessment identified simple-login.html as highest-value MIGRATE candidate)

---

## Purpose

Wire `simple-login.html` to i18n. This is the highest-value migration candidate from the legacy assessment: an active authentication surface already connected to db.js/app.js, user-facing, and relatively contained.

---

## Scope

### Included

| Area | Action |
|------|--------|
| Language toggle | Add container to page |
| i18n scripts | Load i18n.js, lang-en.js, lang-fr.js |
| initI18n() | Initialize before other scripts |
| Translation function | Wire hardcoded strings to `__('key')` |
| Keys | Add new login keys to lang-en.js and lang-fr.js |

### Explicit Non-Scope

This sprint must not:

- Modify QASimulator.html or capstone-2.html
- Resolve the QASimulator/desktop duplicate question
- Modify app modules
- Change authentication logic
- Redesign the login UI

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| SL-1 | simple-login.html wired to i18n |
| SL-2 | Language toggle functional |
| SL-3 | EN/FR parity maintained |
| SL-4 | Existing login behavior preserved |
| SL-5 | No unrelated pages modified |
| SL-6 | Evidence produced |

---

## Evidence Contract

This sprint produces exactly:

```
docs/sprints/QA-PILOT-SIMPLE-LOGIN-I18N-MIGRATION-1-EVIDENCE.md
```

---

**Status:** ✅ AUTHORIZED — Owner-authorized 2026-07-20
**Authorized by:** Andrew Hannah
**Ledger entry:** #173 (authorized)
