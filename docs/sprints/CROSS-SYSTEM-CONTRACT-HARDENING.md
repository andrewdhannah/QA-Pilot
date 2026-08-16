# Sprint — Cross-System Contract Hardening

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #236 (proposed)
**Lane:** assurance / contracts
**Type:** Interface hardening — cross-system contract formalization
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Phase:** Phase 4 — Operational Intelligence
**Predecessor:** QA-PILOT-ASSURANCE-TREND-ANALYSIS-1 (#235, complete)

---

## 1. Purpose

Define exactly what each subsystem may provide, consume, and never assume.

**The goal is not "connect everything."**
The goal is: **Define exactly what each subsystem may provide, consume, and never assume.**

## 2. The Risk

The current risk is no longer missing components. It is **boundary erosion between systems**.

Cross-System Contract Hardening prevents accidental role expansion.

## 3. Contract Boundary Matrix

| System | Produces | Consumes | Cannot Do |
|--------|----------|----------|-----------|
| Librarian Core | governance state, receipts, findings | evidence, declarations | execute agent actions |
| FlightPlan | runtime observations | runtime context | classify authority |
| QA-Pilot | assurance evidence, validation results | project state | approve capability changes |
| LINK | advisory projections | assessments, signals | create decisions |
| Agents | proposed actions, artifacts | contracts, capabilities | modify governance state |

## 4. Contracts to Formalize

### 4.1 Evidence Exchange Contract

**Question:** How does an external system submit evidence without becoming a governance actor?

Defines:
- Producer identity
- Evidence class
- Timestamps
- Provenance
- Authority semantics
- Validation requirements

### 4.2 Capability Consumption Contract

**Question:** How does an agent discover and use a capability safely?

Defines:
- Registry lookup
- Authority boundary
- Documentation references
- Evidence references
- Health status interpretation

### 4.3 Qualification Consumption Contract

**Question:** How should downstream systems interpret qualification state?

Critical distinctions:
- `QUALIFIED` ≠ `AUTHORIZED TO CHANGE`
- `DEGRADED` ≠ `DISABLED`
- `REVIEW_REQUIRED` ≠ `FAILED`

### 4.4 Decision Ownership Contract

**Question:** Where does human authority enter?

Defines:
- System: detects, explains, routes
- Owner: accepts, rejects, modifies, approves

## 5. Acceptance Criteria

A clean agent receiving the cross-system contracts should answer:

1. What systems exist?
2. What does each system own?
3. What evidence can each system produce?
4. What authority does each system lack?
5. How does information flow?
6. Where does a human decision occur?

**Without repository exploration.**

## 6. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| CSH-001 | Contract boundary matrix created | `contracts/cross-system-boundary-matrix.md` — 5 systems defined with produces/consumes/cannot_do | ✅ |
| CSH-002 | Evidence Exchange Contract formalized | `contracts/cross-system-evidence-exchange.md` — producer identity, evidence class, provenance, authority semantics | ✅ |
| CSH-003 | Capability Consumption Contract formalized | `contracts/cross-system-capability-consumption.md` — registry lookup, authority boundary, health interpretation | ✅ |
| CSH-004 | Qualification Consumption Contract formalized | `contracts/cross-system-qualification-consumption.md` — critical distinctions, state semantics, interpretation rules | ✅ |
| CSH-005 | Decision Ownership Contract formalized | `contracts/cross-system-decision-ownership.md` — system detect/explain/route, Owner accept/reject/modify/approve | ✅ |
| CSH-006 | 6-question test passes | Agent can answer all 6 questions from contracts alone | ✅ |
| CSH-007 | Existing contracts unchanged | No modification to existing internal contracts | ✅ |
| CSH-008 | Existing validators pass | No regressions from #235 baseline | ✅ |

## 7. Guardrails

| Guardrail | Rule |
|-----------|------|
| Interfaces only | Contracts define boundaries, not implementations |
| No new capabilities | This sprint hardens, not builds |
| No authority expansion | Contracts preserve existing authority model |
| Read-only over existing | No modification to existing contracts |
| Deterministic | Same contracts → same interpretations |

## 8. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/CROSS-SYSTEM-CONTRACT-HARDENING.md` | This sprint document |
| `contracts/cross-system-boundary-matrix.md` | System boundary matrix |
| `contracts/cross-system-evidence-exchange.md` | Evidence exchange contract |
| `contracts/cross-system-capability-consumption.md` | Capability consumption contract |
| `contracts/cross-system-qualification-consumption.md` | Qualification consumption contract |
| `contracts/cross-system-decision-ownership.md` | Decision ownership contract |

## 9. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #236 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 10. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-ASSURANCE-TREND-ANALYSIS-1 (#235) | ✅ Complete |
| All existing contracts | ✅ Exist |
| Cross-system understanding | ✅ Mature |
