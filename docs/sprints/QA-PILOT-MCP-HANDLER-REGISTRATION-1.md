# QA-PILOT-MCP-HANDLER-REGISTRATION-1 — QA Pilot MCP Handler Registration

**Project:** QA Pilot
**Status:** 🔍 Pending Owner review (not sealed)
**Authority:** Advisory only. QA Pilot-owned local handler stubs — no The Librarian MCP runtime registration.

**Sprint type:** QA Pilot MCP Handler Registration.
**Sprint ID:** `QA-PILOT-MCP-HANDLER-REGISTRATION-1`
**Date:** 2026-07-02
**Branch:** `main`
**Starting HEAD:** `23ffe13`
**Predecessor:** QA-PILOT-RECEIPT-STORE-1 (sealed #4)
**Authorization basis:** Owner-approved per OD-QA-PILOT-RECEIPT-STORE-1-SEAL — "Wire the sealed QA Pilot MCP surface contracts to the sealed QA Pilot receipt store as QA Pilot-owned runtime handler stubs or local project handlers."
**Authority:** Advisory only. Handlers stay within QA Pilot project boundary.

---

## Objective

Wire the sealed QA Pilot MCP surface contracts to the sealed QA Pilot receipt store as QA Pilot-owned local handler stubs. These handlers implement the four MCP surface tools by calling the receipt store directly — without registering in The Librarian runtime, without mutating The Librarian source code.

## Handler Functions Implemented

| Function | Authority | Store Integration | CLI |
|----------|-----------|-------------------|-----|
| `handle_register(receipt_path)` | R1 advisory | Calls `store.register()` | `register <path>` |
| `handle_get(receipt_id)` | R0 read-only | Calls `store.get()` | `get <id>` |
| `handle_list(limit, offset, filters)` | R0 read-only | Calls `store.list_receipts()` | `list --limit N` |
| `handle_status()` | R0 read-only | Calls `store.status()` | `status` |

## Files Created

### `docs/governance/QA-PILOT-MCP-HANDLER-REGISTRATION.md`
Governance document (8 sections): handler architecture, handler function specs, authority model (HR-1-6), cross-project boundary rules, relationship to existing components, non-goals, required boundaries.

### `docs/schemas/qa-pilot-mcp-handler.schema.json`
Draft 2020-12 schema for QA Pilot handler registration. Enforces `project_boundary: qa-pilot`, `store_integration: qa_pilot_receipt_store`, `cross_project_registration: false`.

### `scripts/qa_pilot_mcp_handlers.py`
QA Pilot-owned local handler module. Wraps each receipt store function with handler-level metadata:
- `project_boundary: "qa-pilot"`
- `store_integration: "qa_pilot_receipt_store"`
- `cross_project_registration: false`
- `advisory_notice` in all responses

### `docs/examples/qa-pilot-mcp-handler/` (8 fixture files)

| File | Type | Description |
|------|------|-------------|
| `valid-handler-register.json` | Valid | Register handler with advisory receipt, project_boundary, store_integration |
| `valid-handler-get.json` | Valid | Get handler with valid receipt_id |
| `valid-handler-list.json` | Valid | List handler with bounded limit=50 |
| `valid-handler-status.json` | Valid | Status handler with empty input |
| `invalid-handler-authority-claim.json` | Invalid | Receipt authority='authoritative' |
| `invalid-handler-unbounded-list.json` | Invalid | List limit=0 |
| `invalid-handler-cross-project-registration.json` | Invalid | project_boundary='librarian', cross_project_registration=true |
| `invalid-handler-mutating-status.json` | Invalid | Status with non-empty input (action='seal_all') |

### `scripts/validate-qa-pilot-mcp-handler.py`
Python validator with 6 business rules (HR-1 through HR-6):
- HR-1: Register handler calls QA Pilot receipt store only (AST check — no Librarian runtime refs)
- HR-2: Register handler returns advisory_only=true (runtime test)
- HR-3: Register handler rejects non-advisory authority (delegates to store)
- HR-4: Get/list/status are R0 read-only (AST check — no store mutation calls)
- HR-5: List handler enforces bounded limit (1-100)
- HR-6: All handler responses include advisory boundary statements

### `scripts/test-qa-pilot-mcp-handler.sh`
Bash test runner with 14 tests:
1. Handler script exists
2. Handler validator passes
3. Handler register works (calls store)
4. Register returns advisory_only=true
5. Register includes project_boundary=qa-pilot
6. Handler get works
7. Handler list works
8. Handler status works
9. Handler rejects authority claim
10. Handler list rejects unbounded
11. Handler responses include advisory_notice
12. Handler includes cross_project_registration=false
13. All 3 existing validators still pass (regression)
14. All 3 existing test runners still pass (regression)

## Validation Results

### Handler Validator
```
$ python3 scripts/validate-qa-pilot-mcp-handler.py
  ✅ HR-1: Handler calls QA Pilot receipt store only
  ✅ HR-2: Register returns advisory_only=true (runtime test)
  ✅ HR-3: Register rejects non-advisory authority
  ✅ HR-4: Get/list/status are R0 read-only (AST check)
  ✅ HR-5: List enforces bounded limit 1-100
  ✅ HR-6: Advisory boundary in responses
  ✅ ALL CHECKS PASS
```

### Handler Test Runner
```
$ bash scripts/test-qa-pilot-mcp-handler.sh
Tests: 14 total
Pass:  14
Fail:  0
Result: 14/14 passed. All tests pass. ✅
```

### Existing Validators (Regression)
```
Receipt validator:   ✅ ALL CHECKS PASS
MCP surface validator: ✅ ALL CHECKS PASS
Store validator:     ✅ ALL CHECKS PASS
Receipt test:        ✅ 14/14 pass
MCP surface test:   ✅ 14/14 pass
Store test:         ✅ 14/14 pass
```

### Prohibited-Zone Scan
```
The Librarian repo: not modified by this sprint
The Librarian HEAD: 7f455a3
The Librarian MCPController: not touched
The Librarian runtime: not mutated
External QA Pilot production repos: not touched
Result: CLEAN
```

## Cross-Project Boundary Confirmation

| Constraint | Status | Evidence |
|------------|--------|----------|
| Handlers call QA Pilot receipt store only | ✅ Pass | HR-1: no Librarian runtime refs |
| Handlers include project_boundary=qa-pilot | ✅ Pass | All handler outputs include this field |
| Handlers include store_integration name | ✅ Pass | All handler outputs reference qa_pilot_receipt_store |
| cross_project_registration is false | ✅ Pass | All handler outputs include this field |
| No Librarian MCPController references | ✅ Pass | HR-1 AST check: code is clean |
| No Librarian Swift source mutation | ✅ Pass | Prohibited-zone scan: CLEAN |
| Invalid cross-project fixture exists | ✅ Pass | 8th fixture tests this case |

## Acceptance Gates

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 1 | Handler governance doc exists | **Pass** | `docs/governance/QA-PILOT-MCP-HANDLER-REGISTRATION.md` — 8 sections |
| 2 | Handler schema/contract exists | **Pass** | `docs/schemas/qa-pilot-mcp-handler.schema.json` — Draft 2020-12 |
| 3 | QA Pilot handler module exists | **Pass** | `scripts/qa_pilot_mcp_handlers.py` — 4 handler functions |
| 4 | Four required handler functions | **Pass** | register, get, list, status |
| 5 | Handlers call QA Pilot receipt store only | **Pass** | HR-1 AST check; all handlers import and use store |
| 6 | Register remains R1 advisory | **Pass** | HR-2: runtime test confirms advisory_only=true |
| 7 | Get/list/status remain R0 read-only | **Pass** | HR-4 AST check: no store mutation calls |
| 8 | List remains bounded 1-100 | **Pass** | HR-5: limit validation; test rejects unbounded |
| 9 | Cross-project registration explicitly rejected | **Pass** | All outputs include cross_project_registration=false |
| 10 | Existing receipt validation still passes | **Pass** | Regression: validator + test runner both pass |
| 11 | Existing MCP surface validation still passes | **Pass** | Regression: validator + test runner both pass |
| 12 | Existing receipt store validation still passes | **Pass** | Regression: validator + test runner both pass |
| 13 | New handler test runner passes | **Pass** | 14/14 pass |
| 14 | QA Pilot ledger remains project-local | **Pass** | Ledger #5 added (pending); only QA Pilot files touched |
| 15 | The Librarian repo remains untouched | **Pass** | Prohibited-zone scan: CLEAN |
| 16 | Closeout receipt exists, states pending Owner review | **Pass** | This document |

## Unresolved Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Handlers are local stubs only — not registered in Librarian MCP runtime | Medium | Requires separate cross-project custody packet for Librarian integration |
| No gRPC/HTTP transport layer | Low | Out of scope for handler stub sprint |
| Store uses file-based persistence (no DB) | Low | Acceptable for current QA Pilot scope |
| Concurrent access not guaranteed | Low | Single-agent/single-user at this stage |

## Closeout Receipt

This sprint is closed (agent work complete) by the existence of:

1. 1 handler governance document (8 sections)
2. 1 handler schema (Draft 2020-12)
3. 1 handler module with 4 functions wrapping the receipt store
4. 8 fixture files (4 valid, 4 invalid) including cross-project boundary test
5. 1 handler validator (6 rules HR-1-6)
6. 1 handler test runner (14/14 passing, 7 regression guards)
7. QA Pilot sprint ledger entry #5
8. Updated FEATURE-STATUS.md and SESSION-HANDOFF.md
9. This closeout receipt

**This sprint does not:**
- Seal itself or any other sprint
- Claim Owner approval of any kind
- Mutate The Librarian repo
- Register handlers in The Librarian MCP runtime
- Mutate The Librarian MCPController or Swift sources
- Cross the QA Pilot → The Librarian project boundary
- Mutate production QA Pilot repos (`qa-pilot-v2`, `QA-PilotV2`)

**This sprint does:**
- Create QA Pilot-owned handler stubs wrapping the receipt store
- Wire all four MCP surface contracts to the receipt store
- Enforce project_boundary=qa-pilot across all handlers
- Enforce cross_project_registration=false across all handlers
- Preserve all existing QA Pilot validators and test runners (6/6 regression guards)

**Status: 🔍 Pending Owner review (not sealed)**
