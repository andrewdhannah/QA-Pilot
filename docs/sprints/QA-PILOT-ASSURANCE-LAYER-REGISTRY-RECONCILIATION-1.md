# QA-PILOT-ASSURANCE-LAYER-REGISTRY-RECONCILIATION-1 — Asset Layer Registry Reconciliation

**Type:** data reconciliation / baseline maintenance
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** assurance
**Boundary:** QA Pilot-local
**Librarian impact:** none
**Epic:** EPIC-QA-PILOT-ASSURANCE-OPERATIONS-INTEGRATION-1
**Dependencies:** QA-PILOT-CANONICAL-ASSURANCE-BASELINE-RECONCILIATION-1 (#201, sealed)

---

## Purpose

Reconcile the pipeline layer registry and related health baselines before the Owner Dashboard surface is built. The dashboard is a projection surface — it must not compensate for stale source-of-truth data.

**What this sprint does:** Extends the pipeline layer registry to cover all sealed sprints through #200, regenerates the health expected-layers projection, and ensures that downstream dashboards and surfaces render accurate operational state.

**What this sprint does not do:** Build the Owner Dashboard, add new assurance capabilities, modify the finding lifecycle, or change any sealed evidence.

---

## Background

Sprint 201 identified two stale baseline data items:

| Item | Issue | Location |
|------|-------|----------|
| Pipeline layer registry | Registry stops at slot 73; 100+ sealed sprints (slots 74–200) unregistered | `data/pipeline-layer-registry/registry.json` |
| Pipeline health expected layers | Derived from stale registry — regenerated after registry update | `scripts/validate-qa-pilot-pipeline-health-regression.py` |

These are data maintenance gaps from the rapid capability build-out (#166–#200). No code defects, no assurance regressions — but the dashboard should not launch until the source layer map is complete.

---

## Scope

### Registry Reconciliation (Primary)

Extend `data/pipeline-layer-registry/registry.json` to include all sealed sprints from slot 74 through slot 200. Each layer entry requires:

| Field | Source |
|-------|--------|
| `slot` | Sprint's `sealed_number` from sprint ledger |
| `sprint_id` | Sprint ID from ledger |
| `sprint_title` | Sprint title from ledger |
| `layer_type` | Classified by sprint `area` or `lane` (pipeline, validation, governance, assurance, planning, etc.) |
| `status` | `sealed` |
| `advisory` | `true` |
| `custody` | `qa-pilot-local` |
| `librarian_mutation` | `false` |

### Health Baseline Regeneration (Derivative)

Update the expected-layers projection consumed by `validate-qa-pilot-pipeline-health-regression.py` (PH-12 check) so it reflects the complete layer set through slot 200.

### Verification

| Check | Pass Criteria |
|-------|--------------|
| PLR-16 | Registry covers all sealed slots through #200; no missing slot gaps |
| PH-12 | No unexpected extra sealed layers reported |
| Pipeline health regression | ALL PIPELINE HEALTH CHECKS PASS |
| Pipeline layer registry | Registry validates with no failures |
| All existing validators | Zero regressions introduced |

---

## Deliverables

| Artifact | Location | Purpose |
|----------|----------|---------|
| Updated pipeline layer registry | `data/pipeline-layer-registry/registry.json` | Complete layer coverage through slot 200 |
| Health expected layers updated | (within validator script or companion data file) | PH-12 check operates against complete data |
| Registry reconciliation report | Sprint doc (this file) | Record of changes made |

---

## Acceptance Gates

| Gate | Description | Pass Criteria |
|------|-------------|---------------|
| AG-1 | Registry extends through slot 200 | All sealed sprints #33–#200 have registry entries |
| AG-2 | No slot gaps | Slot numbers are contiguous with no missing values |
| AG-3 | Layer types correctly classified | Each entry's `layer_type` matches sprint area/lane |
| AG-4 | Health baseline regenerated | PH-12 reports no unexpected layers |
| AG-5 | All existing validators pass | No regressions introduced by data changes |
| AG-6 | No stale baseline warnings | Pipeline health regression reports ALL CHECKS PASS |
| AG-7 | No dashboard surface created | Forbidden scope verified |
| AG-8 | Registry schema valid | Registry JSON parses and passes PLR validation |

---

## Non-Goals

- Build the Owner Dashboard surface (Sprint 203)
- Add new assurance capabilities
- Modify existing sealed sprint evidence
- Change the finding lifecycle
- Implement cross-project routing
- Run operational calibration

---

## Sprint Boundary

| Constraint | Value |
|------------|-------|
| Project boundary | QA Pilot-local |
| Librarian mutation | none |
| Cross-project mutation | none |
| File scope | `data/pipeline-layer-registry/`, `scripts/validate-qa-pilot-pipeline-health-regression.py` |
| Read-only scope | All sealed sprint evidence, sprint ledger |
| Write scope | Pipeline layer registry, health baseline data, sprint doc |

---

**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Authorized by:** Andrew Hannah
**Epic:** EPIC-QA-PILOT-ASSURANCE-OPERATIONS-INTEGRATION-1
**Ledger entry:** #202 (status: authorized)
