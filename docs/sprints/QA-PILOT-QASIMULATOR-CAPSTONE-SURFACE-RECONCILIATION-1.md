# QA-PILOT-QASIMULATOR-CAPSTONE-SURFACE-RECONCILIATION-1 — QASimulator/Capstone Surface Reconciliation

**Type:** assessment / surface reconciliation
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** assessment
**Boundary:** QA Pilot-local
**Librarian impact:** none
**Dependencies:** #173 sealed (QA-PILOT-SIMPLE-LOGIN-I18N-MIGRATION-1)

---

## Purpose

Resolve the ownership and artifact identity of the three large legacy surfaces identified in #172: QASimulator.html, desktop/dist.html, and capstone-2.html. Determine whether they are duplicates, build artifacts, or distinct active surfaces.

**Why now:** The legacy assessment revealed that QASimulator.html and desktop/dist.html are nearly identical in size (813KB each), suggesting a potential duplicate or build-artifact relationship. Resolving this before the App Module Audit ensures the module audit has a stable surface inventory.

---

## Scope

### Surfaces to Reconcile

| Page | Size | Assessment #172 Recommendation |
|------|------|-------------------------------|
| QASimulator.html | 813KB | MIGRATE candidate |
| desktop/dist.html | 814KB | OWNER_DECISION_REQUIRED |
| capstone-2.html | 914KB | MIGRATE candidate |

### Included

| # | Area | Action |
|---|------|--------|
| 1 | File comparison | Compare QASimulator.html vs desktop/dist.html for identity/duplicate detection |
| 2 | Runtime ownership | Determine which files are user-facing vs build artifacts |
| 3 | Source relationship | Identify build pipeline or generation relationship |
| 4 | Usage status | Document whether surfaces are actively used |
| 5 | Recommendation | Produce classification for each surface |

### Output Classification

| Classification | Meaning |
|---------------|---------|
| RETAIN | Current state is intentional |
| CONSOLIDATE | Duplicate exists; choose canonical copy |
| MIGRATE | Active surface requires modernization |
| RETIRE | No active purpose |
| OWNER DECISION REQUIRED | Product/distribution choice |

### Explicit Non-Scope

This sprint must not:

- Modify any of the three surfaces
- Perform migration work
- Add i18n wiring
- Refactor code
- Change build pipeline
- Make ownership decisions

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| QR-1 | QASimulator and capstone files compared |
| QR-2 | Runtime ownership determined |
| QR-3 | Source/build artifact relationship identified |
| QR-4 | User-facing usage status documented |
| QR-5 | Migration/retain/retire recommendation produced |
| QR-6 | Evidence artifact produced |
| QR-7 | No implementation changes made |

---

## Evidence Contract

This sprint produces exactly:

```
docs/sprints/QA-PILOT-QASIMULATOR-CAPSTONE-SURFACE-RECONCILIATION-1-EVIDENCE.md
```

Containing:
- Per-surface comparison results
- Duplicate/build-artifact determination
- Ownership and usage analysis
- Recommendation per surface

---

## Resulting Dependency

```
This sprint
        |
        v
Surface inventory clarity
        |
        v
App Module Audit (stable surface map)
```

---

**Status:** ✅ AUTHORIZED — Owner-authorized 2026-07-20
**Authorized by:** Andrew Hannah
**Ledger entry:** #174 (authorized)
