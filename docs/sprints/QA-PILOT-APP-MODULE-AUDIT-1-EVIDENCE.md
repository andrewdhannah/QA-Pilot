# QA-PILOT-APP-MODULE-AUDIT-1-EVIDENCE.md

**Produced by:** QA-PILOT-APP-MODULE-AUDIT-1 (ledger #175)
**Date:** 2026-07-20
**Classification:** Advisory assessment evidence — does not authorize implementation

---

## Acceptance Gate Results

| Gate | Result | Assessment |
|------|--------|------------|
| AMA-1 | PASS | All 16 modules inventoried |
| AMA-2 | PASS | Module ownership documented |
| AMA-3 | PASS | Surface dependencies mapped |
| AMA-4 | PASS | Active/inactive classification produced |
| AMA-5 | PASS | Recommendations generated |
| AMA-6 | PASS | No implementation changes made |
| AMA-7 | PASS | Evidence produced (this document) |

**7 PASS, 0 FAIL**

---

## Per-Module Inventory

| # | Module | Size | Lines | Type | i18n | Form | Content.js | Recommendation |
|---|--------|------|-------|------|------|------|------------|---------------|
| 1 | `_stub.html` | 1.5KB | 55 | Placeholder | No | No | No | RETAIN (template) |
| 2 | `ac.html` | 17KB | 415 | Bug simulation | No | Yes | Yes | RETAIN |
| 3 | `ado.html` | 60KB | 1,439 | Bug simulation | No | Yes | Yes | RETAIN |
| 4 | `browser.html` | 35KB | 748 | Training browser | No | No | Yes | RETAIN |
| 5 | `dynamics.html` | 115KB | 2,534 | CRM simulation | No | Yes | Yes | RETAIN |
| 6 | `excel.html` | 10KB | 226 | Bug simulation | No | Yes | Yes | RETAIN |
| 7 | `inspector.html` | 9KB | 268 | Scenario tool | No | No | No | RETAIN |
| 8 | `powerpoint.html` | 7KB | 169 | Bug simulation | No | No | Yes | RETAIN |
| 9 | `qapache.html` | 3KB | 0* | Sim app stub | No | No | No | RETAIN (stub) |
| 10 | `qoutlook.html` | 53KB | 1,282 | Bug simulation | No | Yes | Yes | RETAIN |
| 11 | `qtube.html` | 4KB | 0* | Sim app stub | No | No | No | RETAIN (stub) |
| 12 | `reports.html` | 20KB | 565 | Reporting | Yes | No | Yes | RETAIN |
| 13 | `settings.html` | 26KB | 595 | Settings simulation | No | Yes | Yes | RETAIN |
| 14 | `teams.html` | 87KB | 1,951 | Collaboration sim | No | Yes | Yes | RETAIN |
| 15 | `training.html` | 47KB | 1,085 | Training mode | No | No | Yes | RETAIN |
| 16 | `word.html` | 7KB | 148 | Bug simulation | No | Yes | Yes | RETAIN |

*\* qapache.html and qtube.html show 0 lines due to single-line file structure (minified/inline)*

---

## Critical Finding: Shared Ownership

**All 16 modules are loaded by both QASimulator AND capstone-2.** There is no module that is unique to a single surface.

| Surface | Modules Referenced |
|---------|-------------------|
| QASimulator.html | All 16 |
| capstone-2.html | All 16 |
| content.js (course definitions) | 10 modules (ac, ado, browser, dynamics, excel, reports, settings, teams, training, word) |

**Implication:** Any module-level change (i18n wiring, refactoring, retirement) affects both QASimulator AND capstone-2 simultaneously. Module work cannot be sequenced independently of surface migration planning.

---

## Module Classification

| Category | Count | Modules |
|----------|-------|---------|
| RETAIN | 14 | All active simulation/training modules |
| RETAIN (stub/placeholder) | 2 | `_stub.html`, `qapache.html`, `qtube.html` |
| RETIRE | 0 | No modules recommended for retirement |
| MIGRATE | 0 | Module migration depends on surface migration decision |

### Classification Rationale

**RETAIN (13 + 1 stub):** All modules are actively referenced by both QASimulator and capstone-2. They are functional simulation/training components with content.js integration. No module is orphaned or decayed.

**Retire candidate `_stub.html`:** Placeholder template (55 lines). No functional value. Can be removed when convenient — low priority.

---

## i18n State

| State | Count | Modules |
|-------|-------|---------|
| Wired (`__()` calls) | 1 | reports.html |
| Absent | 15 | All others |

**Finding:** Only `reports.html` has i18n integration. All other modules use hardcoded English strings inside inline HTML. Module i18n wiring is a significant effort that should be planned as part of the broader surface migration.

---

## Surface Dependency Map

```
                    QASimulator.html
                    capstone-2.html
                           |
          +----------------+----------------+
          |                |                |
     apps/ac.html    apps/ado.html    apps/browser.html
     apps/ac.html    apps/dynamics...   (all 16)
          |                |                |
          +----------------+----------------+
                           |
                    content.js (10 modules)
                    course-view.html
                    portal.html
```

No module has a single-surface owner. All modules are shared infrastructure.

---

## Recommendation Summary

| Recommendation | Count | Notes |
|---------------|-------|-------|
| RETAIN | 16 | All modules are active shared components |
| RETIRE | 0 | No modules are orphaned |
| MIGRATE | 0 | Module migration deferred to surface migration |
| OWNER DECISION | 0 | No module-level decisions needed |

---

## Scope Compliance

| Check | Result |
|-------|--------|
| Modules refactored | None |
| i18n changes | None |
| UI changes | None |
| QASimulator/capstone migration | None |

**Scope classification:** Assessment only. No implementation changes.

---

## Post-Audit Sequence

```
#175 (this sprint)
        |
        v
Complete surface + module inventory
        |
        v
Owner decisions on:
  - capstone-2 migration
  - QASimulator i18n path
  - desktop/distribution pathway
  - Chrome extension
```

---

**Produced by:** QA-PILOT-APP-MODULE-AUDIT-1 (ledger #175)
**Classification:** Advisory assessment evidence — does not authorize implementation.
