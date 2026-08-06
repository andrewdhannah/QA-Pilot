# QA-PILOT-LEGACY-PAGE-ASSESSMENT-1 — Legacy Page Disposition Assessment

**Type:** assessment / strategy
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** assessment
**Boundary:** QA Pilot-local
**Librarian impact:** none
**Dependencies:** #171 sealed (QA-PILOT-ADMIN-I18N-WIRING-1)

---

## Purpose

Determine the disposition of the 14 legacy pages that are not yet wired to i18n. The output is a classification and strategy recommendation — not implementation.

**Why now:** Active surface i18n wiring is complete. The remaining question is not "how do we wire these pages?" but "which surfaces should be migrated, retained, or retired?"

---

## Scope

### Pages to Assess

| # | Page | Path |
|---|------|------|
| 1 | QA Pilot Session | `browser-app/QA-Pilot-Session.html` |
| 2 | QA Simulator | `browser-app/QASimulator.html` |
| 3 | Start Me Up | `browser-app/START_Me_Up.html` |
| 4 | ADO Lab | `browser-app/ado-lab.html` |
| 5 | Capstone Lab | `browser-app/capstone-lab.html` |
| 6 | Capstone 2 | `browser-app/capstone-2.html` |
| 7 | CRM Lab | `browser-app/crm-lab.html` |
| 8 | Confirm | `browser-app/confirm.html` |
| 9 | Mock | `browser-app/mock.html` |
| 10 | Simple Login | `browser-app/simple-login.html` |
| 11 | Guide: Facilitator | `browser-app/guide-facilitator.html` |
| 12 | Guide: Student | `browser-app/guide-student.html` |
| 13 | Chrome Extension | `browser-app/chrome-extension/popup.html` |
| 14 | Desktop Dist | `browser-app/desktop/dist.html` |

### Assessment Per Page

| Field | Purpose |
|-------|---------|
| Page identity | What the page is and what it does |
| Usage status | Active / unknown / obsolete |
| i18n state | Wired / partial / absent |
| User impact | High / medium / low |
| Migration effort | Estimate (if applicable) |
| Recommendation | Migrate / retain / retire / owner decision required |

### Explicit Non-Scope

This sprint must not:

- Add translation keys
- Modify any page
- Add language toggles
- Refactor templates
- Touch app modules (16 apps/)

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| LA-1 | All 14 legacy pages assessed |
| LA-2 | Usage status determined for each page |
| LA-3 | i18n state documented for each page |
| LA-4 | Recommendation produced for each page |
| LA-5 | No pages modified |
| LA-6 | Evidence produced |

---

## Evidence Contract

This sprint produces exactly:

```
docs/sprints/QA-PILOT-LEGACY-PAGE-ASSESSMENT-1-EVIDENCE.md
```

Containing:
- Per-page assessment table
- Recommendation summary
- Aggregate effort estimate
- Scope compliance confirmation

---

## Expected Output Categories

```
MIGRATE
  planned implementation sprint

RETAIN
  known non-i18n surface

RETIRE
  decommission candidate

OWNER_DECISION_REQUIRED
  needs direction
```

---

## Resulting State

| Phase | Status |
|-------|--------|
| Active surface i18n wiring | ✅ Complete (#170, #171) |
| Legacy page strategy | ✅ Determined (this sprint) |
| App module audit | ⏳ Depends on legacy outcome |

---

**Status:** ✅ AUTHORIZED — Owner-authorized 2026-07-20
**Authorized by:** Andrew Hannah
**Ledger entry:** #172 (authorized)
