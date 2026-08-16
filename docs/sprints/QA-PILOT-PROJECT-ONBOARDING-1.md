# Sprint — QA-PILOT-PROJECT-ONBOARDING-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #232 (proposed)
**Lane:** assurance / federation
**Type:** Federation maturity — repeatable project onboarding
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Epic:** EPIC-QA-PILOT-ASSURANCE-OPTIMIZATION-1
**Predecessor:** QA-PILOT-ADAPTIVE-QUALIFICATION-1 (#231, complete)

---

## 1. Purpose

Make a new governed project able to enter the assurance ecosystem through a repeatable adapter path.

The architecture already has:
- Runtime evidence federation (#223)
- Project identity schema (#223)
- Freshness discovery (#224)
- LINK projection (#227)
- Adaptive profiles (#231)

The missing capability is the **onboarding contract**.

## 2. Onboarding Architecture

```
New Project
      │
      △
Project Assurance Adapter
      │
      ├── Identity Registration
      ├── Evidence Source Declaration
      ├── Capability Discovery
      ├── Qualification Profile Mapping
      ├── Freshness Policy Binding
      └── LINK Projection Registration
      │
      △
Governed Assurance Participant
```

## 3. Onboarding State Model

```
registered
      │
      △
evidence_connected
      │
      △
qualification_ready
      │
      △
assurance_active
```

A project can exist without being fully qualified. The state model distinguishes partial onboarding from full assurance participation.

## 4. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| PO-001 | Project identity contract validated | `onboard-project.py onboard` validates project_id, project_instance, identity_source | ✅ |
| PO-002 | Evidence sources registered | Evidence domains declared and project directories created | ✅ |
| PO-003 | Provenance chain verified | Provenance fields checked on existing evidence | ✅ |
| PO-004 | Qualification profiles mapped | Default profiles assigned based on artifact types (4 profiles available) | ✅ |
| PO-005 | Freshness policy assigned | Freshness windows configured (60min records, 15min snapshots) | ✅ |
| PO-006 | LINK projection generated | Project metadata created for LINK visibility | ✅ |
| PO-007 | Project isolation verified | No cross-project references detected | ✅ |
| PO-008 | Onboarding receipt created | Append-only onboarding record in `data/assurance/onboarding-records/` | ✅ |
| PO-009 | Existing project state unchanged | Onboarding only adds new project, does not modify existing | ✅ |
| PO-010 | Replay produces deterministic onboarding state | Same inputs → same onboarding result | ✅ |
| PO-011 | Existing validators pass | No regressions from #231 baseline | ✅ |

## 5. Guardrails

| Guardrail | Rule |
|-----------|------|
| Repeatable path | Same onboarding process for all projects |
| Isolation preserved | No cross-project contamination |
| No automatic approval | Onboarding does not approve capabilities |
| No centralized authority | Projects retain authority over their evidence |
| No cross-project mutation | Onboarding is additive only |
| Advisory | Onboarding status is recommendation, not authorization |

## 6. What This Sprint Does NOT Create

- Automatic project approval
- Automatic capability activation
- Centralized project authority
- Cross-project mutation
- Automatic remediation

Those remain outside QA-Pilot.

## 7. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-PROJECT-ONBOARDING-1.md` | This sprint document |
| `contracts/assurance/project-onboarding-contract.md` | Onboarding contract |
| `scripts/onboard-project.py` | Onboarding engine |
| `data/assurance/onboarding-records/` | Onboarding receipts |

## 8. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #232 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 9. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-ADAPTIVE-QUALIFICATION-1 (#231) | ✅ Complete |
| Federation engine | ✅ Working |
| Project identity schema | ✅ Exists |
| Fleet freshness discovery | ✅ Working |
| LINK query surface | ✅ Working |
| Adaptive qualification profiles | ✅ Working |
