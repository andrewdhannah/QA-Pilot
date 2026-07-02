# QA Pilot ↔ Librarian MCP Custody — Governance

**Sprint:** QA-PILOT-LIBRARIAN-MCP-CUSTODY-PACKET-1
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review (not sealed)
**Authority:** Decision/constraint only. No implementation authorized.

---

## 1. Purpose

Define whether The Librarian may ever broker calls to QA Pilot's own MCP surface, and if so, under what custody conditions, allowed files, forbidden files, evidence requirements, and rollback path. This is a **decision and constraint document** — it does not authorize any implementation.

## 2. Current Default (Option A — Operating Now)

QA Pilot owns its own MCP surface. The Librarian does not own, register, or execute QA Pilot MCP handlers.

| Property | Current Value | Evidence |
|----------|---------------|----------|
| `project_boundary` | `"qa-pilot"` | All sealed handler outputs |
| `cross_project_registration` | `false` | All sealed handler outputs |
| `store_integration` | `"qa_pilot_receipt_store"` | Handler module references |
| Librarian MCPController | Not referenced | HR-1 AST check across 5 sealed sprints |
| QA Pilot handler path | `scripts/qa_pilot_mcp_handlers.py` | File exists, project-local |
| QA Pilot receipt store | `scripts/qa_pilot_receipt_store.py` | File exists, project-local |

## 3. Integration Options

### Option A — Separate MCP / Local Handler Surface (Current)

QA Pilot continues to own and run its own local handler surface. The Librarian does not route, broker, or register QA Pilot tools.

**Pros:** Clean separation, no coupling, no custody overhead.
**Cons:** The Librarian cannot discover or route to QA Pilot tools from the main MCP context.

### Option B — Librarian Brokered Calls (Future Possible Path)

The Librarian may later expose broker tools that route to QA Pilot handlers, but only when custody records prove the QA Pilot project context.

**Pros:** Single MCP entry point for users who switch projects. Custody trail preserved.
**Cons:** Requires broker layer. Adds coupling surface. Requires custody verification at runtime.

### Option C — Native Librarian MCPController Registration (Not Recommended)

The Librarian directly registers QA Pilot tools in its MCPController Swift source.

**Pros:** No broker layer. Tools appear natively.
**Cons:** Highest coupling. QA Pilot loses project independence. Requires modifying Librarian Sources/App. Requires highest custody bar.

## 4. Recommended Outcome

| Decision | Value |
|----------|-------|
| Current operating mode | **Option A** — preserve |
| Next possible design path | **Option B planning only** — may be designed, not implemented |
| Option C authorization | **Not authorized** — requires separate Owner decision even for planning |

## 5. Custody Conditions for Any Future Option B

If the Owner later authorizes Option B implementation, ALL of the following conditions must be met before any broker code is written:

### Identity Conditions (CC-1 through CC-4)

| Rule | Condition |
|------|-----------|
| CC-1 | `active_project_id` must equal `"qa-pilot"` |
| CC-2 | `target_project_id` must equal `"qa-pilot"` |
| CC-3 | The requested tool must belong to a sealed QA Pilot MCP surface sprint |
| CC-4 | The QA Pilot ledger must have the relevant sprint sealed |

### Authority Conditions (CC-5 through CC-7)

| Rule | Condition |
|------|-----------|
| CC-5 | The QA Pilot handler path must be project-local (`active/qa-pilot/scripts/`) |
| CC-6 | The request must carry a custody record proving project context |
| CC-7 | The output must remain advisory/read-only/R1 per the sealed QA Pilot contract |

### Safety Conditions (CC-8 through CC-10)

| Rule | Condition |
|------|-----------|
| CC-8 | The output must not create Owner approval, seal, merge, or production-readiness state |
| CC-9 | All broker calls must produce a receipt or audit evidence |
| CC-10 | A rollback path must be documented before any broker implementation begins |

## 6. Forbidden Actions (Never Authorized by This Packet)

The following actions are **never authorized** by this custody packet, even if Option B is later approved:

1. Merging QA Pilot into The Librarian as a subsystem
2. Registering QA Pilot tools directly in The Librarian MCPController
3. Removing or overriding QA Pilot's `project_boundary` or `cross_project_registration` invariants
4. Allowing QA Pilot handler output to create Owner approval, seal, merge, or production-readiness state
5. Allowing QA Pilot handler output to bypass The Librarian's custody or authority model
6. Deleting or modifying QA Pilot's sealed sprint receipts, governance docs, or schemas to remove project separation

## 7. Required Components for Option B Planning

If the Owner authorizes Option B planning, the following must be designed before any implementation:

- A broker tool schema defining request/response shape with custody fields
- A project-context verification mechanism (e.g., reading `active_project_id` from project selection)
- A custody record schema for each brokered call
- A rollback plan for the broker layer
- Receipt/audit evidence generation for each brokered call
- Validator and test runner for broker behavior before any runtime code

## 8. Non-Goals

- No The Librarian MCPController mutation
- No Sources/App mutation
- No native MCP registration
- No QA Pilot handler behavior changes
- No cross-project call execution
- No broker implementation
- No runtime changes of any kind

## 9. Required Boundaries

1. Do not mutate `active/librarian/` (The Librarian repo)
2. Do not mutate `qa-pilot-v2/` or `QA-PilotV2/` (production QA Pilot repos)
3. Do not alter mainline Owner decision records
4. Do not claim QA approval, sealing, merge authority, or production readiness
5. Do not implement broker tools or runtime changes
6. Do not register QA Pilot tools in The Librarian runtime
7. Do not cross the QA Pilot → The Librarian project boundary
