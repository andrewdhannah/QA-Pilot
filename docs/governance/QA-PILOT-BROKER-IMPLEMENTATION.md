# QA Pilot Option B Broker Implementation — Governance

**Sprint:** QA-PILOT-BROKER-IMPLEMENTATION-1
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review (not sealed)
**Authority:** QA Pilot-local broker implementation. No Librarian mutation. No native MCPController registration. Advisory-only.

---

## 1. Purpose

Implement the Option B broker layer in QA Pilot space only, according to the sealed QA-PILOT-BROKER-PLAN-1 governance. The broker accepts incoming request intents, verifies custody conditions (CC-1 through CC-10), routes to QA Pilot handlers, produces advisory-only output, and generates audit receipts for every call.

## 2. Implementation Model

### 2.1 Architecture

```
Broker Request (JSON)
  │
  ▼
librarian_broker_qa_pilot.py
  │
  ├── 1. Disable flag check ─────────► If disabled → structured refusal + audit
  ├── 2. Custody verification (CC-1–10) ──► If fails → structured refusal + audit
  ├── 3. Project boundary check ─────► Must be qa-pilot
  ├── 4. Tool authority check ───────► R0 or R1 only
  ├── 5. Route to QA Pilot handler ──► scripts/qa_pilot_mcp_handlers.py
  ├── 6. Advisory enforcement ───────► Verify output is advisory-only
  └── 7. Audit receipt ──────────────► data/audit/broker/<receipt_id>.json
       └── Return advisory output
```

### 2.2 Key Properties

| Property | Value |
|----------|-------|
| Broker is local to QA Pilot | Yes — no Librarian dependency at runtime |
| Handlers remain QA Pilot-owned | Yes — broker calls existing handlers |
| Custody verification | CC-1 through CC-10 |
| Output authority | advisory-only |
| Audit trail | Per-call broker audit receipts |
| Disable mechanism | BROKER_ENABLED config flag |
| Cross-project calls | Not executed |
| Native MCPController registration | Not present |

## 3. Implementation Boundaries

### 3.1 Allowed

- Create and modify files under `scripts/librarian_broker_qa_pilot.py`
- Create broker audit receipts in `data/audit/broker/`
- Create implementation governance docs, schema, fixtures, examples, validators, test runners
- Call existing QA Pilot handler module (`scripts/qa_pilot_mcp_handlers.py`)
- Call existing QA Pilot receipt store module (`scripts/qa_pilot_receipt_store.py`)

### 3.2 Forbidden

- Mutate The Librarian repo (`active/librarian/`)
- Touch The Librarian MCPController, Sources/App, runtime, MCP enforcement
- Register native MCP tools
- Execute cross-project calls
- Broaden authority beyond the sealed broker plan
- Implement production mutation pathways
- Mutate external QA Pilot production repos (`QA-PilotV2/`, `qa-pilot-v2/`)

## 4. Broker Request Format

Every broker call accepts a JSON request object with the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `broker_version` | string | Yes | Must be `"qap-broker-v1"` |
| `request_id` | string | Yes | Unique request identifier |
| `project_id` | string | Yes | Must equal `"qa-pilot"` |
| `tool` | string | Yes | QA Pilot MCP tool name |
| `params` | object | Yes | Tool-specific parameters |
| `custody_record` | object | Yes | Custody verification record |
| `timestamp` | string | Yes | ISO 8601 timestamp |

### Custody Record Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `project_context` | string | Yes | Must be `"qa-pilot"` |
| `target_project` | string | Yes | Must be `"qa-pilot"` |
| `tool_name` | string | Yes | Tool being requested |
| `handler_path` | string | Yes | Project-local handler path |
| `authority_claimed` | string | Yes | Must be `"advisory"` or `"read_only"` |
| `session_id` | string | No | Session identifier if available |

## 5. Broker Response Format

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `broker_version` | string | Yes | `"qap-broker-v1"` |
| `request_id` | string | Yes | Echo of request ID |
| `output` | object | No | Handler output (if accepted) |
| `authority` | string | Yes | `"advisory_only"` |
| `project_boundary` | string | Yes | `"qa-pilot"` |
| `custody_verified` | boolean | Yes | Whether custody passed |
| `custody_conditions_checked` | array | Yes | List of CC conditions checked |
| `audit_receipt_id` | string | Yes | Audit receipt ID for this call |
| `accepted` | boolean | Yes | Whether request was accepted |
| `error` | string | No | Error message if rejected |
| `timestamp` | string | Yes | ISO 8601 response timestamp |

## 6. Audit Receipt Format

Per the sealed plan §5, every broker call produces an audit receipt at `data/audit/broker/<receipt_id>.json`:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `receipt_type` | string | Yes | `"broker_audit"` |
| `request_id` | string | Yes | Matches broker request ID |
| `tool` | string | Yes | QA Pilot MCP tool called |
| `project_id` | string | Yes | `"qa-pilot"` |
| `custody_verified` | boolean | Yes | Whether custody passed |
| `custody_conditions_checked` | array | Yes | List of CC conditions verified |
| `output_authority` | string | Yes | `"advisory_only"` |
| `timestamp` | string | Yes | ISO 8601 timestamp |
| `duration_ms` | number | No | Call duration |
| `outcome` | string | Yes | `"success"` or `"failure"` |
| `error` | string | No | Error detail if outcome is failure |

## 7. Disable Mechanism

The broker checks a disable flag before processing any request. Set `BROKER_ENABLED=false` in the config file at `config/broker-config.json`. When disabled, all requests receive a structured refusal with audit evidence. This allows immediate disablement while a full rollback is prepared.

## 8. Rollback Plan

Per the sealed plan §7, rollback requires:
1. Delete or revert all implementation-created files
2. Archive or delete broker audit records
3. Set disable flag or remove
4. Reset project context surfaces to Option A
5. Run post-rollback validation (all validators pass, prohibited-zone clean)

## 9. Authority Constraints

- All broker outputs are `advisory_only` (CC-7, CC-8)
- No broker output creates Owner approval, seal, merge, or production-readiness state
- All broker calls produce audit evidence (CC-9)
- Broker does not execute cross-project calls
- Broker does not register native MCPController tools
- Broker does not mutate The Librarian runtime

## 10. Non-Goals

- No Librarian MCPController mutation
- No Sources/App mutation
- No runtime MCP enforcement changes
- No native MCP registration
- No cross-project call execution
- No reverse broker direction
- No production QA Pilot repo modification
- No authority expansion beyond sealed plan
