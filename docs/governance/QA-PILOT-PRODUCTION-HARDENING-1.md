# QA Pilot Production Hardening — QA-PILOT-PRODUCTION-HARDENING-1

**Sprint:** QA-PILOT-PRODUCTION-HARDENING-1
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review
**Authority:** Advisory only. Version manifests document capabilities; they do not confer authority.

## 1. Purpose

Convert the completed QA-Pilot architecture into a maintainable, versioned, repeatable product capability. Establish the version manifest, contract registry, compatibility validation, and upgrade path that prevent future drift.

## 2. Architecture

```
QA-Pilot Runtime
    │
    ├── qa-pilot-manifest.json     (version manifest — all artifacts cataloged)
    ├── contracts/                  (schemas + validators)
    ├── capabilities/               (entry points + query surfaces)
    ├── adapters/                   (project adapter template)
    └── test-library/               (versioned test bundles)
            │
            ▼
    validate-qa-pilot-compatibility.py
            │
            ├── Contract integrity
            ├── Capability presence
            ├── Version alignment
            └── Authority invariants
```

## 3. Results

| Metric | Value |
|--------|-------|
| Contracts cataloged | 9 (learning-object, SDK, epic-scenario, receipt, knowledge-adapter, qualification, training, sim, workbench) |
| Capabilities registered | 12 (SDK, epics, lessons, scenarios, qualification, install, knowledge, workbench, broker, receipts, intake, dashboard) |
| Compatibility rules | 10 (PC-1 through PC-10) |
| Compatibility verdict | ✅ PASS — all rules pass |
| Fresh install | 27 files, zero Librarian paths, project adapter: `librarian_independent: True` |

## 4. Acceptance Gates

| Gate | Rule | Status |
|---|---|---|
| Manifest exists | PC-1 | ✅ Pass |
| Version correct | PC-2 | ✅ Pass |
| Contracts on disk | PC-3 | ✅ Pass |
| Validators declared | PC-4 | ✅ Pass |
| Capabilities registered | PC-5 | ✅ Pass |
| No authority claim | PC-6 | ✅ Pass |
| 5+ contracts | PC-7 | ✅ 9 contracts |
| 5+ capabilities | PC-8 | ✅ 12 capabilities |
| Install kit matches | PC-9 | ✅ Pass |
| Schema consistency | PC-10 | ✅ Pass |

## 5. Files

| File | Description |
|---|---|
| `qa-pilot-manifest.json` | Version manifest — contracts, capabilities, dependencies |
| `scripts/validate-qa-pilot-compatibility.py` | 10-rule compatibility validator |
| `docs/governance/QA-PILOT-PRODUCTION-HARDENING-1.md` | This governance document |

## 6. Prevented Drift Scenarios

| Scenario | How Manifest Prevents It |
|---|---|
| Tests newer than contracts | Manifest declares contract versions; validator checks schema existence |
| Adapters expect unsupported schemas | Capabilities declare required contracts; compatibility check fails on mismatch |
| Projects consume incompatible packages | Fresh install kit + manifest ensure dependency alignment |
| Authority claims creep in | PC-6 enforces `no_authority_conferred: true` |
| Orphan artifacts accumulate | PC-10 checks schema directory coverage |

## 7. Upgrade Path

When adding new contracts or capabilities:

1. Add schema to `docs/schemas/`
2. Add entry to `qa-pilot-manifest.json` contracts or capabilities
3. Create validator for new contract
4. Run `validate-qa-pilot-compatibility.py` to confirm registration
5. Regenerate fresh install bundle

## 8. Next

| Phase | Work Order | When |
|---|---|---|
| Operations | QA-PILOT-LIBRARIAN-RELEASE-VALIDATION-1 | After hardening |
| Content | Test library expansion | Parallel |

## 9. QA-Pilot Complete State

```
Phase 1 — Infrastructure Boundary    4 work orders   ✓
Phase 2 — Teaching Capability         5 work orders   ✓
Phase 3 — Qualification               1 work order    ✓
Phase 4 — Portability                 1 work order    ✓
Phase 5 — Production Hardening        1 work order    ✓ ← COMPLETE
─────────────────────────────────────────────────────────
Total: 12 work orders, all sealed
```
