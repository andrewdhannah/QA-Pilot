# QA Pilot Broker MCP Advisory Surface — Governance

**Sprint:** QA-PILOT-BROKER-MCP-ADVISORY-SURFACE-1
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review (not sealed)
**Authority:** QA Pilot-local advisory surface. No native MCP registration. Advisory-only.

---

## 1. Purpose

Define a QA Pilot-local advisory MCP-style surface for the sealed broker implementation. This surface provides structured command names (`qa_pilot_broker_accept`, `qa_pilot_broker_audit`, etc.) that are **not native MCP registrations** — they are QA Pilot-local CLI adapters that delegate to the sealed broker module.

The surface is advisory-only and forward-direction-only. It does not register tools in The Librarian MCPController, Sources/App, or any runtime.

## 2. Design Principles

| Principle | Rule |
|-----------|------|
| **Delegates to sealed broker** | The surface calls broker functions — it does not duplicate policy |
| **Advisory-only** | All surface outputs carry advisory-only authority |
| **No native registration** | Command names are QA Pilot-local, not MCP registrations |
| **Custody-first** | All commands pass through broker custody checks (CC-1-10) |
| **Audit trail** | Every accepted/rejected command produces or references broker audit evidence |
| **Forward-only** | No reverse broker direction |

## 3. Advisory Surface Commands

| Command | Delegates To | Description |
|---------|-------------|-------------|
| `qa_pilot_broker_accept` | `broker.accept_request()` | Accept and process a broker request |
| `qa_pilot_broker_audit` | `broker.get_audit_receipt()` | Get a broker audit receipt by ID |
| `qa_pilot_broker_list_audit` | `broker.list_audit_receipts()` | List broker audit receipts |
| `qa_pilot_broker_status` | `broker.broker_status()` | Broker status summary |
| `qa_pilot_broker_enable` | `broker.set_broker_enabled(True)` | Enable the broker |
| `qa_pilot_broker_disable` | `broker.set_broker_enabled(False)` | Disable the broker |

## 4. Advisory Surface Response Format

Every command returns a JSON response with these required fields:

| Field | Type | Description |
|-------|------|-------------|
| `surface` | string | `"qa_pilot_broker_advisory_surface"` |
| `command` | string | The command that was executed |
| `project_id` | string | `"qa-pilot"` |
| `authority` | string | `"advisory_only"` |
| `accepted` | boolean | Whether the command was accepted |
| `custody_verified` | boolean | Whether custody checks passed |
| `refusal_code` | string | Refusal code when rejected (e.g. `custody_failed`, `broker_disabled`, `unsupported_command`) |
| `audit_receipt_id` | string | Broker audit receipt ID |
| `broker_commit_or_version` | string | `"qap-broker-v1"` |
| `timestamp` | string | ISO 8601 timestamp |
| `limitations` | string | Advisory limitation notice |

## 5. Refusal Codes

| Code | Meaning |
|------|---------|
| `custody_failed` | One or more CC conditions failed |
| `broker_disabled` | Broker is disabled via config |
| `invalid_project` | project_id is not qa-pilot |
| `unsupported_command` | Unknown surface command |
| `parse_error` | Malformed JSON input |

## 6. Boundaries

- All commands remain inside `active/qa-pilot/`
- No native MCPController registration
- No Sources/App mutation
- No cross-project calls
- No external QA Pilot production repos modified
- No approval, seal, merge, or production-readiness authority
- No broadening of broker authority beyond advisory-only

## 7. Non-Goals

- No native MCP registration
- No Librarian runtime mutation
- No reverse broker direction
- No new custody logic (delegates to sealed broker)
- No production mutation pathways
- No authoritative QA result output
