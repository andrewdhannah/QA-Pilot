# QA-PILOT-BROKER-PLAN-1 — QA Pilot Option B Broker Plan

**Project:** QA Pilot
**Status:** ✅ **Sealed (ledger #7)** — Owner-approved 2026-07-02 per OD-QA-PILOT-BROKER-PLAN-1-SEAL
**Authority:** Planning/design only. No implementation authorized.

**Sprint type:** Planning / design sprint.
**Sprint ID:** `QA-PILOT-BROKER-PLAN-1`
**Date:** 2026-07-02
**Branch:** `main`
**Starting HEAD:** `056dc68`
**Predecessor:** QA-PILOT-LIBRARIAN-MCP-CUSTODY-PACKET-1 (sealed #6)
**Authorization basis:** Owner-approved per OD-QA-PILOT-LIBRARIAN-MCP-CUSTODY-PACKET-1-SEAL — "Option B planning only — may be designed, not implemented."
**Authority:** Planning/design only. No runtime implementation, no Librarian mutation, no cross-project calls, no native MCPController registration.

---

## Planning Outcome

| Decision | Value |
|----------|-------|
| Current operating mode | **Option A — Separate MCP (preserved)** |
| Option B broker model | **Defined (planning-only)** |
| Option C authorization | **Not authorized — reaffirmed** |
| Broker architecture | Librarian routes to QA Pilot handlers — does not absorb them |

## Broker Model Defined

The broker model follows these principles:
- **Librarian broker is optional and future-only.**
- **QA Pilot MCP surface remains QA Pilot-owned.**
- **Broker routes to QA Pilot handlers — does not absorb them.**
- **Forward direction only** (Librarian → QA Pilot). Reverse direction is out of scope.
- **Custody-first:** Every brokered call must carry a custody record (CC-6).

### Architecture

```
The Librarian → Broker (future) → custody check → route to QA Pilot handler → advisory output + audit receipt
```

## Planned Broker Tools

| Tool | Authority | Purpose |
|------|-----------|---------|
| `planned_librarian_broker_qa_pilot_receipt_register` | R1 (advisory) | Register QA Pilot receipt via broker |
| `planned_librarian_broker_qa_pilot_receipt_get` | R0 (read-only) | Retrieve QA Pilot receipt |
| `planned_librarian_broker_qa_pilot_receipt_list` | R0 (read-only) | List QA Pilot receipts |
| `planned_librarian_broker_qa_pilot_receipt_status` | R0 (read-only) | QA Pilot receipt store status |

All planned tools:
- Require custody verification
- Are marked as `planned` (not implemented)
- Use the prefix `planned_librarian_broker_qa_pilot_`

## Custody Checks (CC-1 through CC-10)

All 10 custody conditions from QA-PILOT-LIBRARIAN-MCP-CUSTODY-PACKET-1 are mapped with verification mechanisms:

**Identity (CC-1-4):** Verify project_id matches qa-pilot, tool in sealed surface, ledger sealed.
**Authority (CC-5-7):** Verify handler path is project-local, request carries custody record, output is advisory-only.
**Safety (CC-8-10):** Verify no approval/seal/merge from output, all calls produce audit evidence, rollback path exists.

## Audit Receipt Requirements

- Receipt type: `broker_audit`
- Required fields: receipt_type, request_id, tool, project_id, custody_verified, custody_conditions_checked, output_authority, timestamp, outcome
- Storage: `data/audit/broker/`
- Retention: Indefinite

## Future Mutation Envelope

| Category | Scope |
|----------|-------|
| **Allowed** | Broker implementation scripts, audit store, implementation governance docs, implementation fixtures, implementation examples |
| **Forbidden** | Librarian Sources/, Public/, project-state/, receipts/, .librarian/; QA Pilot handler/store modules |
| **Runtime mutation** | Not authorized by this sprint |
| **Implementation** | Not authorized by this sprint |

## Rollback Requirements

Before any broker implementation, a rollback plan must document:
- Files to revert (implementation scripts, audit data, docs)
- Audit cleanup (archive or delete broker audit records)
- Disable mechanism (BROKER_ENABLED=false config flag)
- Project context reset (ledger, status surfaces → Option A)
- Post-rollback validation (validators pass, prohibited-zone clean)

## Option C Reaffirmation

Option C (native Librarian MCPController registration) remains **not authorized for planning or implementation**. This sprint does not design, reference, or authorize any direct registration of QA Pilot tools in The Librarian runtime.

---

## Files Created

| File | Type |
|------|------|
| `docs/governance/QA-PILOT-BROKER-PLAN.md` | Broker planning governance doc (10 sections) |
| `docs/schemas/qa-pilot-broker-plan.schema.json` | Broker plan schema (Draft 2020-12) |
| `docs/examples/qa-pilot-broker-plan/valid-option-b-broker-plan.json` | Valid fixture — full Option B planning artifact |
| `docs/examples/qa-pilot-broker-plan/valid-read-only-broker-plan.json` | Valid fixture — read-only planning review |
| `docs/examples/qa-pilot-broker-plan/invalid-implementation-authorized.json` | Invalid fixture — implementation_authorized = true |
| `docs/examples/qa-pilot-broker-plan/invalid-native-registration.json` | Invalid fixture — option_c_authorized = true |
| `docs/examples/qa-pilot-broker-plan/invalid-missing-custody-record.json` | Invalid fixture — missing authority section |
| `docs/examples/qa-pilot-broker-plan/invalid-unbounded-list.json` | Invalid fixture — unbounded allowed_files pattern |
| `scripts/validate-qa-pilot-broker-plan.py` | Broker plan validator (24 rules BP-1-24) |
| `scripts/test-qa-pilot-broker-plan.sh` | Broker plan test runner (18 tests) |
| `docs/sprints/QA-PILOT-BROKER-PLAN-1.md` | Sprint receipt (this file) |

## Validation

| Check | Result |
|-------|--------|
| Broker plan validator (valid fixtures) | 2/2 pass (24/24 checks each) |
| Broker plan validator (invalid fixtures) | 4/4 rejected |
| Broker plan test runner | 18/18 pass |
| Existing receipt validator | Still passes |
| Existing MCP surface validator | Still passes |
| Existing receipt store validator | Still passes |
| Existing handler validator | Still passes |
| Existing custody validator | Still passes |
| BP-24 (Librarian runtime reference scan) | Clean |
| Prohibited-zone scan (Librarian repo) | Clean — no new modifications |
| PROJECT-PROFILE.json | Valid (13 fields) |
| QA Pilot ledger | Valid JSON, unchanged |

**All validations pass.** This sprint is planning-only and pending Owner review.

---

## Next Recommended Sprint

**QA-PILOT-BROKER-IMPLEMENTATION-1** — Implement the Option B broker layer in QA Pilot space (scripts, audit store, validation). Requires:
1. Owner approval of this broker plan
2. Documented rollback plan (CC-10)
3. Owner decision to authorize implementation
