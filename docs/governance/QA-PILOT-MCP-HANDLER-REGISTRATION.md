# QA Pilot MCP Handler Registration — Governance

**Sprint:** QA-PILOT-MCP-HANDLER-REGISTRATION-1
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review (not sealed)
**Authority:** Advisory only. QA Pilot-owned local handler stubs only — no The Librarian MCP runtime registration.

---

## 1. Purpose

Wire the sealed QA Pilot MCP surface contracts to the sealed QA Pilot receipt store as QA Pilot-owned local handler stubs. These handlers implement the four MCP surface tools (register, get, list, status) by calling the receipt store directly — without registering in The Librarian's MCP runtime, without mutating The Librarian source code, and without crossing the project boundary.

## 2. Handler Architecture

```
MCP Surface Contract (docs/schemas/qa-pilot-mcp-tool.schema.json)
        │
        ▼
QA Pilot Handler Module (scripts/qa_pilot_mcp_handlers.py)
        │
        ├── qa_pilot_receipt_register()  →  Store Register
        ├── qa_pilot_receipt_get()        →  Store Get
        ├── qa_pilot_receipt_list()       →  Store List
        └── qa_pilot_receipt_status()     →  Store Status
        │
        ▼
QA Pilot Receipt Store (scripts/qa_pilot_receipt_store.py)
        │
        ▼
data/receipts/  │  data/receipt-index.json
```

**Key constraint:** Handlers call the QA Pilot receipt store only. They must not call The Librarian runtime, MCPController, or any external service.

## 3. Handler Functions

### `qa_pilot_receipt_register(receipt_data)` — R1 Advisory

| Field | Value |
|-------|-------|
| **Input** | Receipt JSON object |
| **Authority** | R1 advisory mutation |
| **Store call** | `register(receipt_path)` — validates schema, enforces advisory, persists |
| **Output** | `receipt_id`, `stored_path`, `validation_status`, `advisory_only: true`, `advisory_notice` |
| **Non-effects** | Does not approve, seal, merge, or mark production readiness |

### `qa_pilot_receipt_get(receipt_id)` — R0 Read-only

| Field | Value |
|-------|-------|
| **Input** | `receipt_id` (qapr- pattern) |
| **Authority** | R0 read-only |
| **Store call** | `get(receipt_id)` — returns receipt or not_found |
| **Output** | `found`, `receipt` (if found), `advisory_notice` |

### `qa_pilot_receipt_list(limit, offset, filters)` — R0 Read-only

| Field | Value |
|-------|-------|
| **Input** | `limit` (1-100), `offset`, optional `project_id`/`status`/`packet_type` |
| **Authority** | R0 read-only |
| **Store call** | `list_receipts(...)` — applies filters, bounded limit |
| **Output** | `receipts[]`, `total_count`, `limit`, `offset`, `advisory_notice` |

### `qa_pilot_receipt_status()` — R0 Read-only

| Field | Value |
|-------|-------|
| **Input** | None |
| **Authority** | R0 read-only |
| **Store call** | `status()` — counts, breakdowns, last validation |
| **Output** | `status`, `receipt_store` counts, `last_validation`, `advisory_notice` |

## 4. Authority Model (HR-1 through HR-6)

| Rule | Description |
|------|-------------|
| HR-1 | Register handler calls QA Pilot receipt store only (not The Librarian runtime) |
| HR-2 | Register handler returns advisory_only=true |
| HR-3 | Register handler rejects receipts with non-advisory authority |
| HR-4 | Get/list/status handlers are R0 read-only — no store mutation |
| HR-5 | List handler enforces bounded limit (1-100) |
| HR-6 | All handler responses include advisory/read-only boundary statements |

## 5. Cross-Project Boundary

**This sprint explicitly does not cross the QA Pilot → The Librarian project boundary.**

| Allowed | Forbidden |
|---------|-----------|
| Call QA Pilot receipt store functions | Call The Librarian MCPController |
| Read QA Pilot schemas and config | Read or write The Librarian files |
| Create QA Pilot-owned handler stubs | Register handlers in The Librarian runtime |
| Validate against QA Pilot schemas | Mutate The Librarian Swift sources |
| Use QA Pilot data paths | Use The Librarian receipt store |

**Cross-project integration requires a separate Owner-approved custody packet.** This sprint only creates QA Pilot-owned local handler stubs. If future work needs to register these handlers in The Librarian's MCP runtime (e.g., in `Sources/App/Controllers/MCPController.swift`), that requires explicit Owner authorization via a cross-project custody packet.

## 6. Relationship to Existing Components

| Component | Relationship |
|-----------|-------------|
| `docs/schemas/qa-pilot-mcp-tool.schema.json` | Handler input/output follow the MCP surface contracts |
| `scripts/qa_pilot_receipt_store.py` | Handlers call store functions for all operations |
| `docs/schemas/qa-pilot-receipt.schema.json` | Register handler validates receipts via store |
| `scripts/validate-qa-pilot-receipt-store.py` | Handler behavior tested via store validator |
| `scripts/validate-qa-pilot-mcp-surface.py` | Handler contracts validated against MCP surface rules |
| `active/librarian/Sources/App/Controllers/MCPController.swift` | **Not touched** — cross-project boundary |

## 7. Non-Goals

- No The Librarian MCPController registration
- No The Librarian Swift source mutation
- No cross-project custody boundary crossing
- No gRPC, HTTP, or wire protocol implementation
- No automated dispatch, seal, approval, or authority-promotion
- No concurrent access guarantees
- No database backend

## 8. Required Boundaries

1. Do not mutate `active/librarian/` (The Librarian repo)
2. Do not mutate `qa-pilot-v2/` or `QA-PilotV2/` (production QA Pilot repos)
3. Do not alter mainline Owner decision records
4. Do not claim QA approval, sealing, merge authority, or production readiness
5. Handlers must call QA Pilot receipt store only
6. Register must return advisory_only=true
7. Get/list/status must be R0 read-only
8. List must enforce bounded limit 1-100
9. Cross-project registration must be explicitly rejected in validator
