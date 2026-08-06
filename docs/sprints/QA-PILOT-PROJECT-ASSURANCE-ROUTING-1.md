# QA-PILOT-PROJECT-ASSURANCE-ROUTING-1 — Multi-Project Assurance Routing

**Type:** assurance / multi-project routing
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** assurance
**Boundary:** QA Pilot-local
**Librarian impact:** integration_interface
**Epic:** EPIC-QA-PILOT-ASSURANCE-OPERATIONS-INTEGRATION-1 (Phase 2)
**Dependencies:** QA-PILOT-OWNER-DASHBOARD-INTEGRATION-1 (#203, sealed)

---

## Purpose

Extend assurance projection from a single project boundary to multiple projects while preserving one canonical assurance model and preventing fragmented truth domains.

**What this sprint does:** Proves that the assurance operating layer is a reusable system capability rather than a QA Pilot-specific implementation.

**What this sprint does not do:** Create project-specific assurance schemas, separate finding lifecycle interpretations, independent risk models, or isolated evidence chains.

---

## Design Invariant

> Multiple projects, one assurance language, separate sources of truth.

The key risk is duplication. Routing must extend the existing model, not fork it.

---

## Acceptance Gates

| Gate | Validation Target | Pass Criteria |
|------|-------------------|---------------|
| PAR-1 | Common assurance contract | Multiple projects consume the same assurance contract structure |
| PAR-2 | Project identity | Project identity remains explicit in all projections |
| PAR-3 | Finding traceability | Findings remain traceable to originating project state |
| PAR-4 | Comparable risk | Risk prioritization remains comparable across projects |
| PAR-5 | Evidence discoverability | Evidence lineage remains project-scoped but globally discoverable |
| PAR-6 | Aggregated dashboard | Owner dashboard can aggregate without merging truth domains |
| PAR-7 | Boundary enforcement | Project boundaries prevent unauthorized cross-project mutation |
| PAR-8 | Missing data visibility | Missing project data is visible, not inferred |

---

## Scope

### In Scope

- Extend assurance store schemas to carry `project_id` identity
- Add multi-project aggregation to Owner Dashboard
- Verify finding routing preserves project association
- Verify risk comparison across projects
- Verify evidence lineage discoverability across project boundaries
- Verify boundary enforcement (no cross-project mutation)

### Non-Scope

- New project onboarding (Librarian, Agent Bridge, Runtime Node)
- Operational calibration (Phase 3, Sprint 205)
- Governance maturity features (Phase 4, Sprint 206)
- Actual cross-project data population
- Modifying other project repositories

---

## Deliverables

| Artifact | Purpose |
|----------|---------|
| Multi-project routing extension to dashboard | Aggregated view across project boundaries |
| Project identity schema update | `project_id` in assurance stores |
| Cross-project validator | PAR-1 through PAR-8 rules |
| Test runner | Multi-project scenario tests |
| Fixtures | Multi-project valid + invalid scenarios |

---

## Sprint Boundary

| Constraint | Value |
|------------|-------|
| Project boundary | QA Pilot-local schemas and scripts |
| Librarian impact | Integration interface (reading project state) |
| Cross-project mutation | none — read-only queries |
| File scope | `scripts/`, `docs/schemas/`, `docs/examples/`, `data/` |

---

**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Authorized by:** Andrew Hannah
**Epic:** EPIC-QA-PILOT-ASSURANCE-OPERATIONS-INTEGRATION-1 (Phase 2)
**Ledger entry:** #204 (status: authorized)
