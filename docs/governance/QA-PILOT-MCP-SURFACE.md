# QA Pilot MCP Surface — Governance

**Sprint:** QA-PILOT-MCP-SURFACE-1 (Lane B)
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review (not sealed)
**Authority:** Advisory only. Tool stubs only — no runtime MCP registration, no The Librarian MCP mutation.

---

## 1. Purpose

Define the QA Pilot MCP tool surface for production receipt workflows. This sprint creates the contract definitions, input/output schemas, authority boundaries, and validation infrastructure for four MCP tools that will later be registered as actual MCP tools in a follow-up implementation sprint.

All tools are defined as **stubs/contracts** under the QA Pilot project boundary. They describe what the tools do, what authority they have, and how they validate input/output — without registering any runtime MCP handlers.

## 2. Tool Inventory

### Tool 1: `qa_pilot_receipt_register`

| Field | Value |
|-------|-------|
| **Tool name** | `qa_pilot_receipt_register` |
| **Purpose** | Register a QA Pilot production receipt as advisory evidence |
| **Authority** | R1 — advisory mutation only |
| **Input** | `receipt` — a QA Pilot production receipt object (validates against `qa-pilot-receipt.schema.json`) |
| **Output** | Registered receipt ID, status, timestamp, advisory confirmation |
| **Non-effects** | Does not approve, seal, merge, or mark production readiness |
| **R0 boundary** | Mutates receipt store only. Does not seal sprints, approve work, or grant authority. |
| **Input schema** | `qa-pilot-mcp-tool.schema.json` (receipt_register sub-schema) |

**Validation rules:**
- R-1: Input receipt must be valid against QA Pilot production receipt schema
- R-2: Input receipt `authority` must be `advisory`
- R-3: Input receipt must include `non_approval_statement` (≥20 chars)
- R-4: Output must include `advisory_only` confirmation
- R-5: Must not output any field claiming approval, seal, merge, or production readiness

### Tool 2: `qa_pilot_receipt_get`

| Field | Value |
|-------|-------|
| **Tool name** | `qa_pilot_receipt_get` |
| **Purpose** | Retrieve a QA Pilot receipt by receipt_id |
| **Authority** | R0 — read-only |
| **Input** | `receipt_id` — canonical QA Pilot receipt identifier (pattern `qapr-\d{8}-\d{3,}`) |
| **Output** | Full receipt object if found, or not_found error |
| **Non-effects** | Does not mutate any state |
| **R0 boundary** | Pure read. No mutation, no authority change, no state change. |

**Validation rules:**
- G-1: `receipt_id` must match `qapr-\d{8}-\d{3,}` pattern
- G-2: Output must not contain authority claims
- G-3: Tool must not mutate any state

### Tool 3: `qa_pilot_receipt_list`

| Field | Value |
|-------|-------|
| **Tool name** | `qa_pilot_receipt_list` |
| **Purpose** | List bounded QA Pilot receipts with filters |
| **Authority** | R0 — read-only |
| **Input** | `project_id` (optional), `status` (optional), `packet_type` (optional), `limit` (required, 1-100), `offset` (optional, default 0) |
| **Output** | Bounded list of receipts, total count, advisory notice |
| **Non-effects** | Does not mutate any state |
| **R0 boundary** | Pure read. Must reject unbounded listings. |

**Validation rules:**
- L-1: `limit` must be an integer between 1 and 100 (inclusive)
- L-2: If `limit` is absent, tool must reject with `unbounded_listing_rejected`
- L-3: `offset` must be >= 0 if provided
- L-4: Output must include `advisory_notice` warning of non-authoritative nature
- L-5: Output must not include any approval/seal/merge/production-ready claims

### Tool 4: `qa_pilot_receipt_status`

| Field | Value |
|-------|-------|
| **Tool name** | `qa_pilot_receipt_status` |
| **Purpose** | Summarize QA Pilot receipt store and validation status |
| **Authority** | R0 — read-only/status-only |
| **Input** | None (status is global to QA Pilot project) |
| **Output** | Receipt counts, last validation timestamp, last validation result, store integrity |
| **Non-effects** | Does not mutate any state |
| **R0 boundary** | Status-only. Must not mutate, approve, seal, or claim authority. |

**Validation rules:**
- S-1: Input must be empty (no parameters)
- S-2: Output must be read-only status fields only
- S-3: Must not claim any approval, seal, merge, or production-readiness authority
- S-4: Must not contain action fields (register, update, delete, seal, approve)

## 3. Authority Model

| Tool | Authority Level | Classification |
|------|----------------|----------------|
| `qa_pilot_receipt_register` | R1 | Advisory mutation — receipt store append only |
| `qa_pilot_receipt_get` | R0 | Read-only query |
| `qa_pilot_receipt_list` | R0 | Read-only list |
| `qa_pilot_receipt_status` | R0 | Read-only status |

### Authority Principles (MP-1 through MP-4)

| Rule | Description |
|------|-------------|
| MP-1 | Register tools must classify submitted receipts as advisory evidence only |
| MP-2 | Query/list/status tools must be read-only |
| MP-3 | No MCP tool may claim or imply approval, seal, merge, or production-readiness authority |
| MP-4 | All tool outputs must include advisory/read-only boundary statements |

## 4. Non-Effects

All QA Pilot MCP tool stubs defined in this sprint:

- Do not register runtime MCP handlers
- Do not mutate The Librarian MCP controller code
- Do not implement Swift services
- Do not grant real MCP dispatch access
- Do not seal sprints, approve work, or promote authority
- Do not interact with external QA Pilot production repos (`qa-pilot-v2`, `QA-PilotV2`)
- Do not read from or write to The Librarian ledger, status surfaces, or governance docs

## 5. Input/Output Contracts

See `docs/schemas/qa-pilot-mcp-tool.schema.json` for the full Draft 2020-12 JSON Schema defining all four tool input/output shapes, including:
- `receipt_register_input` / `receipt_register_output`
- `receipt_get_input` / `receipt_get_output`
- `receipt_list_input` / `receipt_list_output`
- `receipt_status_input` / `receipt_status_output`

## 6. Relationship to Existing Components

| Component | Relationship |
|-----------|-------------|
| `docs/schemas/qa-pilot-receipt.schema.json` | Register tool validates receipts against this schema |
| `docs/governance/QA-PILOT-RECEIPT.md` | Authority model derives from production receipt governance |
| `scripts/validate-qa-pilot-receipt.py` | Register tool reuses PR-2, PR-3, PR-10, PR-11 authority checks |
| `docs/examples/qa-pilot-receipt/` | Register tool accepts these production receipt fixtures as input |

## 7. Non-Goals

- No runtime MCP handler registration
- No The Librarian MCP controller mutation
- No Swift service implementation
- No real receipt store implementation
- No gRPC, HTTP transport, or wire protocol definition
- No automated dispatch, seal, approval, or authority-promotion workflow
- No cross-project MCP invocation
- No integration with Librarian's node-registry receipt store

## 8. Required Boundaries

1. Do not mutate `active/librarian/` (The Librarian repo)
2. Do not mutate `qa-pilot-v2/` or `QA-PilotV2/` (production QA Pilot repos)
3. Do not alter mainline Owner decision records
4. Do not claim QA approval, sealing, merge authority, or production readiness
5. All tool contracts must enforce advisory/read-only authority levels
6. Register tools must classify receipts as advisory evidence only
7. List tools must reject unbounded listing
8. Tools must not imply runtime MCP registration capability
