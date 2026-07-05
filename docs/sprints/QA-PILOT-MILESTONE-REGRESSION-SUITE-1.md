# QA-PILOT-MILESTONE-REGRESSION-SUITE-1 — QA Pilot Milestone Regression Suite

**Type:** Validation / regression hardening
**Lane:** `parallel_planning`
**Boundary:** `qa_pilot_local`
**Librarian impact:** `none`
**Status:** `planned`
**Predecessor:** QA-PILOT-QA-PACKET-INGEST-1 (sealed #17)
**Authorization:** OD-QA-PILOT-QA-PACKET-INGEST-1-SEAL — "Next authorized sprint: QA-PILOT-MILESTONE-REGRESSION-SUITE-1"

---

## Intent

Before building QA-PILOT-LOCAL-TRAINING-SIM-1, prove the ingest chain remains stable under regression. Lock the packet custody invariants, advisory boundary, derived-store behavior, invalid-packet rejection, and no-cross-project-write rule.

## Rationale

The packet ingest sprint (sealed #17) defined schema, validation, CLI, and governance for governed QA export packets. The regression suite locks those behaviors so they survive future changes — ensuring the chain stays stable as training sim and future work build on it.

## Scope

### Allowed

- Regression test runner exercising the full ingest chain
- Tests locking: packet custody invariants, advisory boundary, derived-store behavior, invalid-packet rejection, no-cross-project-write rule
- Integration tests exercising real CLI commands (validate, ingest, list, status, clear)
- Tests validating that invalid packets remain rejected after schema/CLI changes
- Tests validating that stored records retain advisory flags
- Sprint receipt and ledger/status updates

### Forbidden

- Changes to the ingest schema or CLI itself (that was sealed #17)
- Training sim work
- Library changes to how packets are stored
- Any Librarian file mutation
- Any cross-project write

## Acceptance Gates

| Gate | Status |
|------|--------|
| Regression test runner exists | 🔍 Pending |
| Packet custody invariants locked by test | 🔍 Pending |
| Advisory boundary enforced in test | 🔍 Pending |
| Derived-store behavior tested | 🔍 Pending |
| Invalid-packet rejection proven stable | 🔍 Pending |
| No-cross-project-write rule tested | 🔍 Pending |
| Ingest CLI end-to-end integration tested | 🔍 Pending |
| All existing QA Pilot validators still pass | 🔍 Pending |
| No Librarian files modified | 🔍 Pending |

## Boundary Assertion

```json
{
  "project_boundary": "qa-pilot",
  "lane": "parallel_planning",
  "librarian_impact": "none",
  "cross_project_registration": false,
  "runtime_mutation_authorized": false,
  "implementation_authorized": true
}
```
