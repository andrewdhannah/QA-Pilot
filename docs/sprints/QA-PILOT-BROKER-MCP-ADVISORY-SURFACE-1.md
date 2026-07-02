# QA-PILOT-BROKER-MCP-ADVISORY-SURFACE-1 — QA Pilot Broker MCP Advisory Surface

**Project:** QA Pilot
**Status:** 🔍 Pending Owner review (not sealed)
**Authority:** QA Pilot-local advisory surface. No native MCP registration. Advisory-only.

**Sprint type:** Implementation sprint.
**Sprint ID:** `QA-PILOT-BROKER-MCP-ADVISORY-SURFACE-1`
**Date:** 2026-07-02
**Branch:** `main`
**Starting HEAD:** `1d703aa`
**Predecessor:** QA-PILOT-BROKER-IMPLEMENTATION-1 (sealed #8)
**Authorization basis:** Owner-approved per OD-QA-PILOT-BROKER-IMPLEMENTATION-1-SEAL.
**Authority:** QA Pilot-local advisory surface. No Librarian mutation. No native MCPController registration. Advisory-only.

---

## Implementation Summary

### Advisory Surface Script

Implemented `scripts/qa_pilot_broker_advisory_surface.py` — a QA Pilot-local advisory MCP-style surface that wraps the sealed broker implementation with 6 commands:

| Commands | Delegates To | Description |
|----------|-------------|-------------|
| `qa_pilot_broker_accept` | broker.accept_request() | Accept and process a broker request |
| `qa_pilot_broker_audit` | broker.get_audit_receipt() | Get a broker audit receipt |
| `qa_pilot_broker_list_audit` | broker.list_audit_receipts() | List broker audit receipts |
| `qa_pilot_broker_status` | broker.broker_status() | Broker status summary |
| `qa_pilot_broker_enable` | broker.set_broker_enabled(True) | Enable the broker |
| `qa_pilot_broker_disable` | broker.set_broker_enabled(False) | Disable the broker |

**These are NOT native MCP registrations** — they are QA Pilot-local CLI adapters.

### Response Format

Every command returns a structured JSON response with all required advisory surface fields: `surface`, `command`, `project_id`, `authority`, `accepted`, `custody_verified`, `refusal_code`, `audit_receipt_id`, `broker_commit_or_version`, `timestamp`, `limitations`.

### Design Properties

| Property | Value |
|----------|-------|
| Delegates to sealed broker | Yes — no policy duplication |
| Advisory-only | All outputs carry authority=advisory_only |
| No native MCP registration | Command names are QA Pilot-local |
| Custody-first | All commands pass through broker CC-1-10 checks |
| Audit trail | Every accepted/rejected command references broker audit evidence |
| Forward-only | No reverse broker direction |

---

## Files Created

| File | Type |
|------|------|
| `scripts/qa_pilot_broker_advisory_surface.py` | Advisory surface adapter script |
| `docs/governance/QA-PILOT-BROKER-MCP-ADVISORY-SURFACE.md` | Governance doc (7 sections) |
| `docs/schemas/qa-pilot-broker-mcp-advisory-surface.schema.json` | Response schema (Draft 2020-12) |
| `fixtures/broker-advisory-surface/valid-accept-register.json` | Valid fixture |
| `fixtures/broker-advisory-surface/valid-audit.json` | Valid fixture |
| `fixtures/broker-advisory-surface/valid-list-audit.json` | Valid fixture |
| `fixtures/broker-advisory-surface/valid-status.json` | Valid fixture |
| `fixtures/broker-advisory-surface/invalid-unsupported-command.json` | Invalid fixture |
| `fixtures/broker-advisory-surface/invalid-missing-custody-accept.json` | Invalid fixture |
| `fixtures/broker-advisory-surface/invalid-wrong-project-accept.json` | Invalid fixture |
| `fixtures/broker-advisory-surface/invalid-cross-project-accept.json` | Invalid fixture |
| `fixtures/broker-advisory-surface/invalid-unsupported-tool-accept.json` | Invalid fixture |
| `fixtures/broker-advisory-surface/invalid-authoritative-claim-accept.json` | Invalid fixture |
| `fixtures/broker-advisory-surface/invalid-disabled-broker-accept.json` | Invalid fixture |
| `fixtures/broker-advisory-surface/invalid-malformed-accept.json` | Invalid fixture |
| `docs/examples/broker-advisory-surface/valid-broker-accept-example.json` | Example response |
| `scripts/validate-qa-pilot-broker-advisory-surface.py` | Validator (19 rules VA-1-19) |
| `scripts/test-qa-pilot-broker-advisory-surface.sh` | Test runner (36 tests) |
| `docs/sprints/QA-PILOT-BROKER-MCP-ADVISORY-SURFACE-1.md` | Sprint receipt |

## Files Modified

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Added sprint #9 (pending_owner_review) |
| `FEATURE-STATUS.md` | Added advisory surface entry |
| `SESSION-HANDOFF.md` | Added advisory surface handoff |

## Validation

| Check | Result |
|-------|--------|
| Advisory surface validator (VA-1-19) | 19/19 pass |
| Advisory surface test runner | **36/36 pass** |
| Implementation test runner | 32/32 pass |
| Plan test runner | 18/18 pass |
| Implementation validator | ALL CHECKS PASS |
| Plan validator | ALL CHECKS PASS |
| Receipt validator | ALL CHECKS PASS |
| MCP surface validator | ALL CHECKS PASS |
| Store validator | ALL CHECKS PASS |
| Handler validator | ALL CHECKS PASS |
| Custody validator | ALL CHECKS PASS |
| Prohibited-zone scan (Librarian repo) | Clean — no new modifications |
| No MCPController registration | Confirmed — only in docstring rejection context |
| No cross-project calls | Confirmed — surface delegates to broker, QA Pilot-local only |
| No external production repo mutation | Confirmed — no QA-PilotV2/ references |

---

## Surface Behavior Verified

| Scenario | Result |
|----------|--------|
| Valid accept (register) | ✅ Accepted |
| Valid accept (get) | ✅ Accepted |
| Valid list-audit | ✅ Accepted |
| Valid status | ✅ Accepted |
| Valid audit lookup | ✅ Accepted |
| Enable/disable commands | ✅ Accepted |
| Unsupported command | ✅ Rejected (argparse validation) |
| Missing custody | ✅ Rejected (custody_failed) |
| Wrong project_id | ✅ Rejected (custody_failed) |
| Cross-project handler | ✅ Rejected (custody_failed) |
| Unsupported tool | ✅ Rejected (custody_failed) |
| Non-advisory authority | ✅ Rejected (custody_failed) |
| Disabled broker | ✅ Rejected (broker_disabled) |
| Malformed input | ✅ Rejected (parse_error) |
| All required response fields present | ✅ Confirmed |
| Authority is advisory_only | ✅ Confirmed |
| Audit receipt ID present for accepted | ✅ Confirmed |
| Refusal code present for rejected | ✅ Confirmed |
| Limitations notice present | ✅ Confirmed |
| No changes outside QA Pilot | ✅ Confirmed |

---

## Next Recommended Sprint

Awaiting Owner review and seal decision for QA-PILOT-BROKER-MCP-ADVISORY-SURFACE-1.
