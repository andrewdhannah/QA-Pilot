# QA-PILOT-OWNER-DASHBOARD-INTEGRATION-1 — Owner Dashboard Integration

**Type:** assurance / operational visibility surface
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** assurance
**Boundary:** QA Pilot-local
**Librarian impact:** none
**Epic:** EPIC-QA-PILOT-ASSURANCE-OPERATIONS-INTEGRATION-1 (Phase 1)
**Dependencies:** QA-PILOT-CANONICAL-ASSURANCE-BASELINE-RECONCILIATION-1 (#201, sealed), QA-PILOT-ASSURANCE-LAYER-REGISTRY-RECONCILIATION-1 (#202, sealed)

---

## Purpose

Expose the operational assurance state through an Owner-facing governance surface using authoritative lifecycle, risk, evidence, and readiness data. This is the point where QA Pilot begins demonstrating the operational value of the assurance layer rather than proving its internal correctness.

**What this sprint does:** Build a governance dashboard that surfaces what is known, what is validated, what requires attention, and what requires Owner action — all traced to authoritative source artifacts.

**What this sprint does not do:** Auto-resolve findings, infer approval, hide uncertainty, modify lifecycle states, approve releases, or replace Owner decision authority.

---

## Design Invariant

> The dashboard is a **projection layer**, not a decision engine.

This is the critical architectural boundary. The dashboard reads from authoritative stores (finding lifecycle, risk prioritization, evidence pipeline, release readiness profiles) and presents their state. It does not mutate them.

Every displayed state must trace to a source artifact. Provenance is not optional.

---

## Acceptance Gates

| Gate | Validation Target | Pass Criteria |
|------|-------------------|---------------|
| AG-1 | Dashboard data source | Registry-backed, not fixture-derived — all data reads from live stores |
| AG-2 | Lifecycle visibility | Findings progress through all lifecycle states visible (open → acknowledged → resolved → closed) |
| AG-3 | Risk visibility | Prioritized risks map to current evidence — risk state shown with evidence references |
| AG-4 | Evidence freshness | Stale/new evidence states visible — evidence age indicators displayed |
| AG-5 | Owner queue | Decisions requiring Owner action surfaced — queue entries shown with status |
| AG-6 | Release readiness | Assurance state reflected accurately — readiness profile summary shown |
| AG-7 | Provenance | Every displayed state traces to source artifacts — each element has a source reference |
| AG-8 | No mutation | Dashboard does not write to any lifecycle, evidence, risk, or decision store — verified by enforcement |
| AG-9 | No inference | Dashboard does not approve, reject, or infer Owner decisions — no decision verbs in output |
| AG-10 | Sparse slot handling | Dashboard correctly handles sparse registry slots — gaps shown as gaps, not errors |

---

## Scope

### Dashboard Sections

| Section | Data Source | Purpose |
|---------|-------------|---------|
| Lifecycle state | Finding lifecycle store (#199-#200) | Show findings by state across all lifecycle stages |
| Risk map | Risk prioritization (#193), dependency risk (#187) | Show prioritized risks with evidence references |
| Evidence freshness | Evidence pipeline, lineage (#192) | Show evidence age indicators, stale/new tags |
| Owner decision queue | Owner action readiness, decision receipts | Surface items needing Owner attention |
| Release readiness | Release readiness profile (#189) | Summary of assurance state relative to release criteria |
| Registry health | Pipeline layer registry (#202) | Show layer coverage with sparse slot awareness |

### Non-Scope

- Multi-project routing (Phase 2, Sprint 204)
- Operational calibration (Phase 3, Sprint 205)
- Governance maturity features (Phase 4, Sprint 206)
- Finding lifecycle mutation
- Automated release gating
- Cross-project evidence routing

---

## Deliverables

| Artifact | Location | Purpose |
|----------|----------|---------|
| Dashboard script/module | `scripts/qa_pilot_owner_dashboard.py` | CLI-based dashboard with text and JSON output modes |
| Dashboard validator | `scripts/validate-qa-pilot-owner-dashboard.py` | Validates dashboard output correctness (DG-1 through DG-10) |
| Dashboard schema | `docs/schemas/qa-pilot-owner-dashboard.schema.json` | Schema for dashboard JSON output |
| Test runner | `scripts/test-qa-pilot-owner-dashboard.sh` | Test suite for dashboard functionality |
| Sprint doc | This file | Sprint record |

---

## Sprint Boundary

| Constraint | Value |
|------------|-------|
| Project boundary | QA Pilot-local |
| Librarian mutation | none |
| Cross-project mutation | none |
| File scope | `scripts/`, `docs/schemas/`, `data/` (read-only for source stores) |
| Read-only scope | Finding lifecycle, evidence pipeline, risk store, decision receipts, release readiness profile, pipeline layer registry |
| Write scope | Dashboard script, validator, schema, test runner, sprint doc |

---

**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Authorized by:** Andrew Hannah
**Epic:** EPIC-QA-PILOT-ASSURANCE-OPERATIONS-INTEGRATION-1 (Phase 1)
**Ledger entry:** #203 (status: authorized)
