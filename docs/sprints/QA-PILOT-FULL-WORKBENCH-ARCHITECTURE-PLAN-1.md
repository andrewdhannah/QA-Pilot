# QA-PILOT-FULL-WORKBENCH-ARCHITECTURE-PLAN-1 — QA Pilot Full Workbench Architecture Plan

**Status:** 🔍 Active (sprint #32)
**Type:** Planning / architecture definition
**Lane:** planning
**Boundary:** QA Pilot-local only
**Librarian impact:** none
**Prior sealed head:** #31 CUSTODY-AUTHORIZATION-DECISION-QUEUE-1
**Proposed ledger:** #32
**Input dependencies:** CUSTODY-AUTHORIZATION-DECISION-QUEUE-1 (#31, sealed)

---

## Sprint Purpose

Fully define QA Pilot as the dedicated QA workbench for The Librarian ecosystem. Create a complete architecture plan covering MCP surface, evidence intake, DB design, test composition, epic regression, simulator/help surface, result export, and phased implementation roadmap.

## Scope

**Allowed:**
- `docs/governance/QA-PILOT-FULL-WORKBENCH-ARCHITECTURE.md`
- `docs/governance/QA-PILOT-MCP-SURFACE.md`
- `docs/governance/QA-PILOT-DB-DESIGN.md`
- `docs/governance/QA-PILOT-SIMULATOR-HELP-SURFACE.md`
- `docs/governance/QA-PILOT-WORKBENCH-ROADMAP.md`
- `docs/schemas/qa-evidence-packet.schema.json`
- `docs/schemas/qa-result-packet.schema.json`
- `docs/schemas/qa-test-case.schema.json`
- `docs/schemas/qa-epic-regression-suite.schema.json`
- `docs/schemas/qa-learning-record.schema.json`
- `scripts/validate-qa-pilot-full-workbench-architecture-plan.py`
- `docs/sprints/QA-PILOT-FULL-WORKBENCH-ARCHITECTURE-PLAN-1.md`
- `project-state/sprint-ledger.json` (add sprint #32 entry)
- `FEATURE-STATUS.md` (add sprint status)
- `SESSION-HANDOFF.md` (update handoff)

**Nothing else.** No changes to #23–#31 sealed contracts, no startup-contract.json changes, no generic harness changes, no Librarian files.

## Deliverables

| # | Deliverable | Path |
|---|-------------|------|
| 1 | Architecture doc | `docs/governance/QA-PILOT-FULL-WORKBENCH-ARCHITECTURE.md` |
| 2 | MCP surface doc | `docs/governance/QA-PILOT-MCP-SURFACE.md` |
| 3 | DB design doc | `docs/governance/QA-PILOT-DB-DESIGN.md` |
| 4 | Simulator/help doc | `docs/governance/QA-PILOT-SIMULATOR-HELP-SURFACE.md` |
| 5 | Roadmap doc | `docs/governance/QA-PILOT-WORKBENCH-ROADMAP.md` |
| 6 | Evidence packet schema | `docs/schemas/qa-evidence-packet.schema.json` |
| 7 | QA result packet schema | `docs/schemas/qa-result-packet.schema.json` |
| 8 | Test case schema | `docs/schemas/qa-test-case.schema.json` |
| 9 | Epic regression suite schema | `docs/schemas/qa-epic-regression-suite.schema.json` |
| 10 | Learning record schema | `docs/schemas/qa-learning-record.schema.json` |
| 11 | Plan validator | `scripts/validate-qa-pilot-full-workbench-architecture-plan.py` |

## Validation Results

```
Validator: 12/12 AP rules pass, 0 failed

AP-1:  Architecture doc exists                          ✅
AP-2:  All 12 required sections present                 ✅
AP-3:  All 5 schemas valid JSON Schema                  ✅
AP-4:  MCP doc defines all 12 tools                     ✅
AP-5:  DB doc defines all 11 entities                   ✅
AP-6:  Simulator/help doc exists                        ✅
AP-7:  Roadmap doc defines all 8 phases                 ✅
AP-8:  All docs state no Librarian authority            ✅
AP-9:  Sprint receipt exists                            ✅
AP-10: Receipt references #31 head and #32 proposed     ✅
AP-11: No approve/seal/execute/write authority           ✅
AP-12: Existing regressions green                       ✅
```

## Hard Boundaries Enforced

- No Librarian files modified
- No custody receipts mutated
- No custody indexes or surfaces altered
- No startup-contract.json or generic harness changes
- No approval/seal/execute/write/sprint-start authority created
- No cross-project mutation without explicit Owner authorization

## Next

Planning sprint — no implementation authorized. Recommended first implementation sprint: QA-PILOT-MCP-EVIDENCE-INTAKE-1.
