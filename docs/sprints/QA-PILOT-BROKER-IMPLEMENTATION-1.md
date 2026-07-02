# QA-PILOT-BROKER-IMPLEMENTATION-1 — QA Pilot Option B Broker Implementation

**Project:** QA Pilot
**Status:** 🔍 Pending Owner review (not sealed)
**Authority:** QA Pilot-local broker implementation. No Librarian mutation. Advisory-only.

**Sprint type:** Implementation sprint.
**Sprint ID:** `QA-PILOT-BROKER-IMPLEMENTATION-1`
**Date:** 2026-07-02
**Branch:** `main`
**Starting HEAD:** `ded4af2`
**Predecessor:** QA-PILOT-BROKER-PLAN-1 (sealed #7)
**Authorization basis:** Owner-approved per OD-QA-PILOT-BROKER-PLAN-1-SEAL — "Implement the Option B broker layer in QA Pilot space only, using the sealed broker plan."
**Authority:** QA Pilot-local broker implementation. Advisory-only. No Librarian mutation. No native MCPController registration.

---

## Implementation Summary

### Broker Module

Implemented `scripts/librarian_broker_qa_pilot.py` — a QA Pilot-local broker that:

1. **Disable flag check** — Reads `config/broker-config.json` for `broker_enabled` flag. When disabled, returns structured refusal with audit.
2. **Custody verification (CC-1 through CC-10)** — Verifies all 10 custody conditions:
   - Identity (CC-1-4): project_id, target_project, tool in sealed surface, ledger sealed
   - Authority (CC-5-7): project-local handler path, custody record present, advisory/read-only authority claim
   - Safety (CC-8-10): no approval state from output, audit evidence generated, rollback path documented
3. **Project boundary check** — Rejects non-qa-pilot project_ids
4. **Tool routing** — Routes to existing QA Pilot handler module (`scripts/qa_pilot_mcp_handlers.py`) for register, get, list, status
5. **Advisory enforcement** — Wraps all output as advisory-only; overrides any approval/seal/merge/production flags
6. **Audit receipt generation** — Creates broker audit receipt at `data/audit/broker/<id>.json` for every call (accepted or rejected)

### Plan Compliance

| Requirement | Status |
|-------------|--------|
| Broker routes to QA Pilot handlers, not absorb | ✅ Routes to qa_pilot_mcp_handlers.py |
| Custody verification (CC-1-10) | ✅ All 10 conditions enforced |
| Advisory-only output (CC-7) | ✅ authority = "advisory_only" enforced |
| No approval/seal/merge (CC-8) | ✅ Override mechanism for output flags |
| Audit evidence per call (CC-9) | ✅ Audit receipt for every call |
| Rollback path documented (CC-10) | ✅ Implementation governance doc §8 |
| Disable flag mechanism | ✅ config/broker-config.json with enable/disable CLI |
| No Librarian mutation | ✅ Verified — no changes to active/librarian/ |
| No MCPController registration | ✅ Verified — no native MCP references in broker module |
| No cross-project calls | ✅ Verified — broker is QA Pilot-local only |
| Forward direction only | ✅ No reverse broker direction |

---

## Files Created

| File | Type |
|------|------|
| `scripts/librarian_broker_qa_pilot.py` | Broker implementation module |
| `docs/governance/QA-PILOT-BROKER-IMPLEMENTATION.md` | Implementation governance doc (10 sections) |
| `docs/schemas/qa-pilot-broker-implementation.schema.json` | Broker request schema (Draft 2020-12) |
| `fixtures/broker-implementation/valid-advisory-register-request.json` | Valid fixture — register |
| `fixtures/broker-implementation/valid-advisory-get-request.json` | Valid fixture — get |
| `fixtures/broker-implementation/valid-advisory-list-request.json` | Valid fixture — list |
| `fixtures/broker-implementation/valid-advisory-status-request.json` | Valid fixture — status |
| `fixtures/broker-implementation/invalid-missing-custody.json` | Invalid fixture — no custody_record |
| `fixtures/broker-implementation/invalid-wrong-project.json` | Invalid fixture — wrong project_id |
| `fixtures/broker-implementation/invalid-unsupported-tool.json` | Invalid fixture — tool not in sealed surface |
| `fixtures/broker-implementation/invalid-cross-project-handler.json` | Invalid fixture — Librarian handler path |
| `fixtures/broker-implementation/invalid-authoritative-claim.json` | Invalid fixture — non-advisory authority |
| `fixtures/broker-implementation/invalid-broker-disabled.json` | Invalid fixture — broker disabled test |
| `docs/examples/broker-implementation/valid-request-example.json` | Broker request example |
| `scripts/validate-qa-pilot-broker-implementation.py` | Implementation validator (20 rules BI-1-20) |
| `scripts/test-qa-pilot-broker-implementation.sh` | Implementation test runner (32 tests) |
| `docs/sprints/QA-PILOT-BROKER-IMPLEMENTATION-1.md` | Sprint receipt (this file) |

## Files Modified

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Added sprint #8 (pending_owner_review) |
| `FEATURE-STATUS.md` | Added QA-PILOT-BROKER-IMPLEMENTATION-1 entry |
| `SESSION-HANDOFF.md` | Added implementation sprint handoff |

## New Directories

| Directory | Purpose |
|-----------|---------|
| `data/audit/broker/` | Broker audit receipt storage |
| `config/` | Broker configuration (broker-config.json) |

## Validation

| Check | Result |
|-------|--------|
| Implementation validator (BI-1-20) | 20/20 pass |
| Implementation test runner | **32/32 pass** |
| Existing plan validator | Still passes |
| Existing plan test runner | 18/18 pass |
| Existing receipt validator | Still passes |
| Existing MCP surface validator | Still passes |
| Existing receipt store validator | Still passes |
| Existing handler validator | Still passes |
| Existing custody validator | Still passes |
| Prohibited-zone scan (Librarian repo) | Clean — no new modifications |
| No MCPController registration | Confirmed — broker docstring only (rejection context) |
| No cross-project calls | Confirmed — broker is QA Pilot-local only |
| No external production repo mutation | Confirmed — no QA-PilotV2/ references |

---

## Broker Behavior Verified

| Scenario | Result |
|----------|--------|
| Valid advisory register request | Accepted — custody verified, audit created |
| Valid advisory get request (read-only) | Accepted — custody verified, audit created |
| Valid advisory list request (read-only) | Accepted — custody verified, audit created |
| Valid advisory status request (read-only) | Accepted — custody verified, audit created |
| Missing custody record | Rejected — structured refusal, audit created |
| Wrong project_id | Rejected — custody CC-1 fails, audit created |
| Unsupported tool | Rejected — custody CC-3 fails, audit created |
| Cross-project handler path | Rejected — custody CC-5 fails, audit created |
| Non-advisory authority claim | Rejected — custody CC-7 fails, audit created |
| Broker disabled | Rejected — structured refusal, audit created |
| Audit receipt for accepted request | Created with custody_conditions_checked containing CC-1..CC-10 |
| Audit receipt for rejected request | Created with custody_verified=false |

---

## Next Recommended Sprint

Awaiting Owner review and seal decision for QA-PILOT-BROKER-IMPLEMENTATION-1.
