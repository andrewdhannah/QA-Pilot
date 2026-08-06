# QA-PILOT-APP-MODULE-AUDIT-1 — Application Module Ownership Audit

**Type:** assessment / module inventory
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** assessment
**Boundary:** QA Pilot-local
**Librarian impact:** none
**Dependencies:** #174 sealed (surface reconciliation complete)

---

## Purpose

Inventory and classify the 16 application modules under `apps/`. Determine ownership, surface dependencies, and active/inactive status. The output is a stable module map for future planning.

**Why now:** Surface ownership is resolved (#174). The module audit can now operate on a stable surface inventory rather than assumptions.

---

## Scope

### Modules to Assess

| # | Module | Path |
|---|--------|------|
| 1 | AC | `browser-app/apps/ac.html` |
| 2 | ADO | `browser-app/apps/ado.html` |
| 3 | Browser | `browser-app/apps/browser.html` |
| 4 | Dynamics | `browser-app/apps/dynamics.html` |
| 5 | Excel | `browser-app/apps/excel.html` |
| 6 | Inspector | `browser-app/apps/inspector.html` |
| 7 | PowerPoint | `browser-app/apps/powerpoint.html` |
| 8 | QApache | `browser-app/apps/qapache.html` |
| 9 | QOutlook | `browser-app/apps/qoutlook.html` |
| 10 | QTube | `browser-app/apps/qtube.html` |
| 11 | Reports | `browser-app/apps/reports.html` |
| 12 | Settings | `browser-app/apps/settings.html` |
| 13 | Teams | `browser-app/apps/teams.html` |
| 14 | Training | `browser-app/apps/training.html` |
| 15 | Word | `browser-app/apps/word.html` |
| 16 | Stub | `browser-app/apps/_stub.html` |

### Assessment Per Module

| Field | Purpose |
|-------|---------|
| Module identity | What the module does |
| Ownership | Surface it belongs to (QASimulator/desktop, capstone-2, both) |
| Dependencies | External scripts, inline content |
| Active status | Used / legacy / placeholder |
| i18n state | Wired / partial / absent |
| Coupling risks | Shared dependencies with other surfaces |
| Recommendation | Retain / migrate / retire |

### Explicit Non-Scope

This sprint must not:

- Refactor any module
- Add i18n changes
- Modify module behavior
- Change UI
- Migrate QASimulator or capstone
- Make ownership decisions

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| AMA-1 | All 16 modules inventoried |
| AMA-2 | Module ownership documented |
| AMA-3 | Surface dependencies mapped |
| AMA-4 | Active/inactive classification produced |
| AMA-5 | Recommendations generated |
| AMA-6 | No implementation changes made |
| AMA-7 | Evidence produced |

---

## Evidence Contract

This sprint produces exactly:

```
docs/sprints/QA-PILOT-APP-MODULE-AUDIT-1-EVIDENCE.md
```

Containing:
- Per-module inventory table
- Ownership and dependency mapping
- Active/inactive classification
- Retain/migrate/retire recommendations

---

## Resulting Dependency

```
#174 Surface Reconciliation
        |
        v
#175 App Module Audit (this sprint)
        |
        v
Complete surface + module inventory
        |
        v
Migration planning decisions
```

---

**Status:** ✅ AUTHORIZED — Owner-authorized 2026-07-20
**Authorized by:** Andrew Hannah
**Ledger entry:** #175 (authorized)
