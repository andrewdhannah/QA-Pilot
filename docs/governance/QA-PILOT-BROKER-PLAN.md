# QA Pilot Option B Broker Plan — Governance

**Sprint:** QA-PILOT-BROKER-PLAN-1
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review (not sealed)
**Authority:** Planning/design only. No implementation authorized.

---

## 1. Purpose

Define a planning-only model for Option B: a future Librarian-brokered call path to QA Pilot's own MCP surface. This document designs the broker model, request/response shape, custody verification requirements, audit receipt requirements, rollback requirements, and future mutation envelope — without implementing broker tools, mutating The Librarian runtime, or registering native MCPController tools.

**This sprint is planning-only.** All artifacts are design documents, not implementation code. Option A (Separate MCP) remains the current operating mode. Option B implementation requires a later Owner-approved sprint.

---

## 2. Broker Model

### 2.1 Design Principles

| Principle | Rule |
|-----------|------|
| **Librarian broker is optional** | The broker is a future, optional layer. QA Pilot MCP surface remains QA Pilot-owned. |
| **QA Pilot surface is QA Pilot-owned** | The broker must route to QA Pilot handlers, not absorb them. QA Pilot retains handler ownership. |
| **No runtime mutation** | This sprint designs the broker model. It does not add broker code to any runtime. |
| **Custody-first** | Every brokered call must carry a custody record proving project context (CC-6). |
| **No cross-project call execution** | The broker plans routes. It does not execute cross-project calls. |
| **No native MCPController registration** | Option C remains rejected (CC-3 override). |

### 2.2 Broker Architecture (Planned)

```
┌─────────────────────────────┐     ┌──────────────────────────────┐
│  The Librarian MCP Context  │     │     QA Pilot Project Space    │
│                             │     │                              │
│  project_get_profile() ─────┼────>│  QA Pilot's own MCP surface  │
│  project_get_cursor()       │     │  (Option A — operating now)  │
│  project_assemble_context() │     │                              │
│                             │     │  qa_pilot_receipt_register   │
│  ┌───────────────────┐      │     │  qa_pilot_receipt_get        │
│  │ Broker (future)   │──────┼────>│  qa_pilot_receipt_list       │
│  │ ─ route to handler│      │     │  qa_pilot_receipt_status     │
│  │ ─ custody check   │      │     │                              │
│  │ ─ audit receipt   │      │     │  QA Pilot Receipt Store      │
│  │ ─ advisory output │      │     │  QA Pilot Handler Module     │
│  └───────────────────┘      │     └──────────────────────────────┘
└─────────────────────────────┘
```

**Key properties:**
- The broker does not own or reimplement QA Pilot handlers.
- The broker verifies custody, routes to QA Pilot's project-local handler path, and records audit evidence.
- QA Pilot remains an independent project with its own MCP surface, ledger, and governance.

### 2.3 Forward vs. Reverse Broker Direction

| Direction | Description | Authority |
|-----------|-------------|-----------|
| **Forward** (Librarian → QA Pilot) | The Librarian discovers and routes a call to QA Pilot's MCP surface under custody guard. | Planning-only this sprint. Requires future Owner-approved implementation sprint. |
| **Reverse** (QA Pilot → Librarian) | QA Pilot calls back into The Librarian for custody or context verification. | Out of scope. Requires separate Owner decision even for planning. |

This sprint defines **forward broker planning only**.

---

## 3. Planned Broker Tool Shapes (Planning Artifacts Only)

The following broker tool shapes are defined as **planning artifacts**. They represent what a future implementation might look like. They are not registered, imported, or executable.

### 3.1 Broker Tool Schemas

| Planned Tool | Authority | Purpose | Custody Required |
|---|---|---|---|
| `planned_librarian_broker_qa_pilot_receipt_register` | R1 (advisory mutation) | Register a QA Pilot receipt via broker | Yes |
| `planned_librarian_broker_qa_pilot_receipt_get` | R0 (read-only) | Retrieve a QA Pilot receipt | Yes |
| `planned_librarian_broker_qa_pilot_receipt_list` | R0 (read-only) | List QA Pilot receipts | Yes |
| `planned_librarian_broker_qa_pilot_receipt_status` | R0 (read-only) | QA Pilot receipt store status | Yes |

### 3.2 Common Broker Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `project_id` | string | Yes | Must equal `"qa-pilot"` |
| `tool` | string | Yes | The QA Pilot MCP tool name |
| `params` | object | Yes | Tool-specific parameters |
| `custody_record` | object | Yes | Custody verification record |
| `request_id` | string | Yes | Unique request identifier |
| `timestamp` | string | Yes | ISO 8601 timestamp |

### 3.3 Common Broker Response Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `output` | object | Yes | Handler output (advisory/read-only/R1) |
| `authority` | string | Yes | Must be `"advisory_only"` |
| `project_boundary` | string | Yes | Must be `"qa-pilot"` |
| `custody_verified` | boolean | Yes | Whether custody check passed |
| `audit_receipt_id` | string | Yes | Audit receipt ID for this call |
| `error` | string | No | Error message if call failed |

### 3.4 Authority Constraints

- All broker outputs must remain advisory/read-only/R1 per the sealed QA Pilot contract (CC-7).
- No broker output may create Owner approval, seal, merge, or production-readiness state (CC-8).
- Broker outputs carry no approval, seal, merge, or production-readiness authority (CC-8).

---

## 4. Custody Verification Requirements (CC-1 through CC-10)

### 4.1 Identity Conditions

| CC | Condition | Broker Verification Mechanism |
|----|-----------|-------------------------------|
| CC-1 | `active_project_id` must equal `"qa-pilot"` | Check `project_id` field in broker request |
| CC-2 | `target_project_id` must equal `"qa-pilot"` | Check `project_id` field matches target |
| CC-3 | Requested tool belongs to sealed QA Pilot MCP surface | Verify tool name against known sealed surface list |
| CC-4 | QA Pilot ledger contains required sealed sprint evidence | Check sprint-ledger.json for relevant sealed sprint |

### 4.2 Authority Conditions

| CC | Condition | Broker Verification Mechanism |
|----|-----------|-------------------------------|
| CC-5 | QA Pilot handler path is project-local | Verify handler resolves under `active/qa-pilot/scripts/` |
| CC-6 | Request carries a custody record proving project context | Require `custody_record` in request with project context fields |
| CC-7 | Output remains advisory/read-only/R1 | Verify `authority` in response is `"advisory_only"` |

### 4.3 Safety Conditions

| CC | Condition | Broker Verification Mechanism |
|----|-----------|-------------------------------|
| CC-8 | Output does not create Owner approval, seal, merge, or production-readiness state | Verify response has no approval/seal/merge/production flags |
| CC-9 | All broker calls produce audit evidence | Generate audit receipt for every broker call |
| CC-10 | Rollback path documented before any broker implementation | Verify rollback-plan.md exists before implementation |

### 4.4 Implementation-Readiness Gate

None of the custody conditions above are enforced by runtime code in this sprint. They are **planning requirements** that a future implementation sprint must satisfy before going live.

---

## 5. Audit Receipt Requirements

Every future broker call **must** produce an audit receipt (CC-9). This section defines the requirements:

### 5.1 Audit Receipt Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `receipt_type` | string | Yes | `"broker_audit"` |
| `request_id` | string | Yes | Matches the broker request ID |
| `tool` | string | Yes | The QA Pilot MCP tool called |
| `project_id` | string | Yes | `"qa-pilot"` |
| `custody_verified` | boolean | Yes | Whether custody passed |
| `custody_conditions_checked` | array | Yes | List of CC conditions verified |
| `output_authority` | string | Yes | `"advisory_only"` |
| `timestamp` | string | Yes | ISO 8601 |
| `duration_ms` | number | No | Call duration if measured |
| `outcome` | string | Yes | `"success"` or `"failure"` |
| `error` | string | No | Error detail if outcome is failure |

### 5.2 Storage Location

Broker audit receipts would be stored in a dedicated broker audit directory (e.g., `data/audit/broker/`) to keep them separate from QA Pilot's production receipt store.

### 5.3 Retention

Broker audit receipts are retained indefinitely as part of the project's audit trail. No automatic expiry.

---

## 6. Future Mutation Envelope

This section defines the exact scope of files a future broker implementation sprint may touch.

### 6.1 Allowed Files (Implementation)

| Path Pattern | Purpose | Authority |
|---|---|---|
| `docs/governance/QA-PILOT-BROKER-IMPLEMENTATION.md` | Implementation governance | Update |
| `docs/schemas/qa-pilot-broker-implementation.schema.json` | Implementation schema | Update |
| `scripts/librarian_broker_qa_pilot.py` | Broker implementation module | Create |
| `fixtures/broker-implementation/` | Broker implementation fixtures | Create |
| `scripts/validate-broker-implementation.py` | Broker validator | Create |
| `scripts/test-broker-implementation.sh` | Broker test runner | Create |
| `data/audit/broker/` | Broker audit store | Create |
| `docs/examples/broker-implementation/` | Broker examples | Create |

### 6.2 Forbidden Files (Implementation)

| Path Pattern | Reason |
|---|---|
| `**/active/librarian/Sources/**` | Librarian runtime mutation — not authorized |
| `**/active/librarian/Public/**` | Librarian web surface — not authorized |
| `**/active/librarian/project-state/**` | Librarian state — not authorized |
| `**/active/librarian/receipts/**` | Librarian receipts — not authorized |
| `**/active/librarian/.librarian/**` | Librarian config — not authorized |
| `**/QA-PilotV2/**` | External QA Pilot production repo — out of scope |
| `scripts/qa_pilot_mcp_handlers.py` | QA Pilot handler module — already sealed, not to be mutated by broker |
| `scripts/qa_pilot_receipt_store.py` | QA Pilot receipt store — already sealed, not to be mutated by broker |

### 6.3 Runtime Mutation Prohibition

**Runtime mutation remains unauthorized by this sprint.** No runtime code, MCP handler registration, or live context assembly changes are permitted. The future implementation sprint must also not mutate The Librarian runtime, MCP enforcement, or MCPController sources.

### 6.4 Implementation Authorization Gate

This sprint does not authorize implementation. A future Owner-approved sprint with a documented rollback plan (CC-10) is required before any broker code is written.

---

## 7. Rollback Requirements

Before any future broker implementation, a rollback plan must be documented (CC-10). This section defines the minimum rollback requirements:

### 7.1 Files to Revert

| File Pattern | Revert Action |
|---|---|
| `scripts/librarian_broker_qa_pilot.py` | Delete (never existed before implementation) |
| `data/audit/broker/` | Delete any audit records (or archive) |
| `docs/governance/QA-PILOT-BROKER-IMPLEMENTATION.md` | Delete |
| `docs/schemas/qa-pilot-broker-implementation.schema.json` | Delete |
| Any other implementation-created files under `docs/examples/broker-implementation/` | Delete |

### 7.2 Receipt and Audit Cleanup

| Artifact | Cleanup Action |
|---|---|
| QA Pilot ledger entries for broker implementation | Sealed sprints remain; add `reverted: true` field |
| Broker audit records | Archive to `data/audit/broker/archive/` |
| Broker-related status entries in FEATURE-STATUS.md | Revert to pre-implementation state |

### 7.3 Disable Mechanism

Any broker implementation must include a disable flag or mechanism (e.g., `BROKER_ENABLED=false` in a config file) that can be set without deleting code. This allows immediate disablement of the broker path while a full rollback is prepared.

### 7.4 Project Context Reset

After rollback, project context (ledger, status surfaces, session handoff) must be updated to reflect that the broker implementation has been reverted and the project is back to Option A (Separate MCP).

### 7.5 Post-Rollback Validation

| Check | Expected |
|---|---|
| Existing QA Pilot validators still pass | All pass |
| Prohibited-zone scan | Clean — no Librarian changes |
| Broker disable flag | Set to `false` or removed |
| No broker script files | `scripts/librarian_broker_*.py` absent |
| No broker audit data | `data/audit/broker/` empty (or archived) |
| FEATURE-STATUS.md | Reflects Option A, not broker |

---

## 8. Option C Reaffirmation

**Option C (native Librarian MCPController registration) is not authorized for planning or implementation.** This sprint does not design, reference, or authorize any direct registration of QA Pilot tools in The Librarian's MCPController Swift source. All planned broker tools route through a separate broker layer, not through native MCPController registration.

---

## 9. Non-Goals

- No broker tool implementation (no executable handler code)
- No The Librarian MCPController mutation
- No Sources/App mutation
- No native MCP registration
- No QA Pilot handler behavior changes
- No cross-project call execution
- No runtime changes of any kind
- No reverse broker direction (QA Pilot → Librarian) planning
- No external QA Pilot production repo modification

## 10. Required Boundaries

1. Do not mutate `active/librarian/` (The Librarian repo)
2. Do not mutate `qa-pilot-v2/` or `QA-PilotV2/` (production QA Pilot repos)
3. Do not alter mainline Owner decision records
4. Do not claim QA approval, sealing, merge authority, or production readiness
5. Do not implement broker tools or runtime changes — this is a planning-only sprint
6. Do not register QA Pilot tools in The Librarian runtime
7. Do not cross the QA Pilot → The Librarian project boundary
