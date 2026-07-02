# QA Pilot Receipt Store — Governance

**Sprint:** QA-PILOT-RECEIPT-STORE-1
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review (not sealed)
**Authority:** Advisory only. Local receipt store only — no runtime MCP registration, no The Librarian mutation.

---

## 1. Purpose

Implement a QA Pilot-owned local receipt store for production receipt registration, query, listing, and status support. The store uses the sealed QA Pilot receipt schema (`docs/schemas/qa-pilot-receipt.schema.json`) and respects the MCP surface contracts defined in the previous sprint (Lane B). All operations enforce advisory-only authority.

## 2. Store Architecture

### Data Paths

| Path | Purpose |
|------|---------|
| `data/receipts/{receipt_id}.json` | Individual receipt storage |
| `data/receipt-index.json` | Index of all stored receipts with metadata |
| `data/receipt-store-status.json` | Auto-generated store status summary |

### Store Operations

| Operation | Authority | Description |
|-----------|-----------|-------------|
| Register | R1 advisory | Validate and persist a QA Pilot receipt |
| Get | R0 read-only | Retrieve a receipt by receipt_id |
| List | R0 read-only | List receipts with bounded pagination |
| Status | R0 read-only | Summarize receipt store health |

## 3. Register Behavior

**Input:** A QA Pilot production receipt JSON object.

**Validation:**
1. Receipt must parse as valid JSON
2. Receipt must validate against `qa-pilot-receipt.schema.json` (Draft 2020-12)
3. Receipt `authority` must be `advisory`
4. Receipt must include `non_approval_statement` (≥20 characters)
5. Receipt `receipt_id` must match `qapr-\d{8}-\d{3,}` pattern
6. Receipt must not already exist in store (duplicate check by receipt_id)

**Output:** `receipt_id`, `stored_path`, `validation_status`, `advisory_only: true`, `non_effects`, `registered_at`

**Non-effects:** Does not approve, seal, merge, or mark production readiness.

## 4. Get Behavior

**Input:** `receipt_id` (string, pattern `qapr-\d{8}-\d{3,}`).

**Behavior:**
1. Look up receipt_id in store index
2. If found, read and return the full receipt JSON
3. If not found, return `not_found` with appropriate message

**Output:** `found: bool`, `receipt` (if found), `advisory_notice`

## 5. List Behavior

**Input:** Optional `project_id`, `status`, `packet_type` filters. Required `limit` (1-100). Optional `offset` (default 0).

**Behavior:**
1. Start with all receipts from index
2. Apply optional filters (project_id, status, packet_type)
3. Apply offset
4. Apply limit (must be 1-100, reject otherwise)
5. Return bounded list of receipt summaries

**Output:** `receipts[]`, `total_count`, `limit`, `offset`, `advisory_notice`

## 6. Status Behavior

**Input:** None (empty object).

**Output:** `status` (healthy/degraded/unavailable), `receipt_store` (total_receipts, by_status, by_packet_type), `last_registration` (if any), `last_validation`, `advisory_notice`

## 7. Authority Model

| Operation | Level | Classification |
|-----------|-------|----------------|
| Register | R1 | Advisory mutation — receipt store append only |
| Get | R0 | Read-only query |
| List | R0 | Read-only list |
| Status | R0 | Read-only status |

### Authority Rules (RS-1 through RS-6)

| Rule | Description |
|------|-------------|
| RS-1 | Register must validate receipt schema before persisting |
| RS-2 | Register must reject receipts where authority != 'advisory' |
| RS-3 | Register must reject receipts with non_approval_statement < 20 chars |
| RS-4 | Get/list/status are read-only — must not mutate store |
| RS-5 | List must reject unbounded requests (limit outside 1-100) |
| RS-6 | All store responses must include advisory boundary statements |

## 8. Relationship to Existing Components

| Component | Relationship |
|-----------|-------------|
| `docs/schemas/qa-pilot-receipt.schema.json` | Register validates receipts against this schema |
| `docs/governance/QA-PILOT-RECEIPT.md` | Authority model derives from production receipt governance |
| `docs/governance/QA-PILOT-MCP-SURFACE.md` | Store implements the MCP surface contracts as local operations |
| `docs/schemas/qa-pilot-mcp-tool.schema.json` | Store input/output shapes follow MCP tool contracts |
| `scripts/validate-qa-pilot-receipt.py` | Store reuses PR-2, PR-3 authority checks |
| `scripts/validate-qa-pilot-mcp-surface.py` | Store respects MP-1 through MP-4 authority principles |

## 9. Non-Goals

- No runtime MCP handler registration
- No The Librarian repo mutation
- No The Librarian MCP controller or runtime mutation
- No automated dispatch, seal, approval, or authority-promotion
- No cross-project MCP invocation
- No gRPC, HTTP, or wire protocol implementation
- No database backend — file-based store only
- No concurrent access guarantees

## 10. Required Boundaries

1. Do not mutate `active/librarian/` (The Librarian repo)
2. Do not mutate `qa-pilot-v2/` or `QA-PilotV2/` (production QA Pilot repos)
3. Do not alter mainline Owner decision records
4. Do not claim QA approval, sealing, merge authority, or production readiness
5. All store operations must enforce advisory/read-only authority levels
6. Register must classify receipts as advisory evidence only
7. List must reject unbounded listing
8. Store must not register runtime MCP handlers
9. Store must not imply Librarian-level custody or enforcement
