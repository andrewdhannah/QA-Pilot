# QA-PILOT-RECEIPT-STORE-1 — QA Pilot Receipt Store

**Project:** QA Pilot
**Status:** ✅ **Sealed (ledger #4)** — Owner-approved 2026-07-02 per OD-QA-PILOT-RECEIPT-STORE-1-SEAL
**Authority:** Advisory only. Local receipt store — no runtime MCP registration, no The Librarian mutation.

**Sprint type:** QA Pilot Receipt Store implementation.
**Sprint ID:** `QA-PILOT-RECEIPT-STORE-1`
**Date:** 2026-07-02
**Branch:** `main`
**Starting HEAD:** `add8b02`
**Predecessor:** QA-PILOT-MCP-SURFACE-1 (sealed #3)
**Authorization basis:** Owner-approved per OD-QA-PILOT-MCP-SURFACE-1-SEAL — "Next authorized sprint: QA-PILOT-RECEIPT-STORE-1. Scope: Implement a QA Pilot-owned local receipt store for production receipt registration/query/status, using the sealed receipt schema and MCP surface contracts."
**Authority:** Advisory only. Local file-based store only — no runtime MCP registration.

---

## Objective

Implement a QA Pilot-owned local receipt store for production receipt registration, query, listing, and status support, using the sealed QA Pilot receipt schema and MCP surface contracts.

## Store Operations Implemented

| Operation | Authority | CLI Usage |
|-----------|-----------|-----------|
| Register | R1 advisory | `python3 scripts/qa_pilot_receipt_store.py register <receipt.json>` |
| Get | R0 read-only | `python3 scripts/qa_pilot_receipt_store.py get <receipt_id>` |
| List | R0 read-only | `python3 scripts/qa_pilot_receipt_store.py list --limit N` |
| Status | R0 read-only | `python3 scripts/qa_pilot_receipt_store.py status` |

## Files Created

### `docs/governance/QA-PILOT-RECEIPT-STORE.md`
Governance document (10 sections): purpose, store architecture, register behavior, get/list/status behavior, authority model (RS-1 through RS-6), relationship to existing components, non-goals, required boundaries.

### `docs/schemas/qa-pilot-receipt-store.schema.json`
Draft 2020-12 schema for the receipt store index and status files. Defines `store_index` and `store_status` sub-schemas.

### `scripts/qa_pilot_receipt_store.py`
The core receipt store module. CLI interface with four commands:
- `register` — validates receipt against `qa-pilot-receipt.schema.json`, enforces advisory-only authority, persists to `data/receipts/{receipt_id}.json`, updates index
- `get` — looks up receipt by ID, returns receipt or not_found
- `list` — applies optional filters (project_id, status, packet_type), bounded limit (1-100), returns summaries
- `status` — counts receipts, reports by_status/by_packet_type breakdowns, last registration, advisory notice

### `docs/examples/qa-pilot-receipt-store/` (8 fixture files)

| File | Type | Description |
|------|------|-------------|
| `valid-register-request.json` | Valid | Advisory receipt with full schema, expected to register successfully |
| `valid-get-request.json` | Valid | Get request for registered receipt ID, expects found=true |
| `valid-list-request.json` | Valid | List request with bounded limit=50 |
| `valid-status-request.json` | Valid | Status request with empty input |
| `invalid-register-authority-claim.json` | Invalid | authority='authoritative', non_approval_statement too short |
| `invalid-list-unbounded.json` | Invalid | limit=0 (outside 1-100) |
| `invalid-get-missing-id.json` | Invalid | receipt_id doesn't match qapr- pattern |
| `invalid-register-duplicate.json` | Invalid | Same receipt_id as valid-register-request, expects duplicate rejection |

### `scripts/validate-qa-pilot-receipt-store.py`
Python validator with 6 business rules (RS-1 through RS-6):
- RS-1: Register validates receipt schema before persisting
- RS-2: Register rejects receipts where authority != 'advisory'
- RS-3: Register enforces non_approval_statement >= 20 chars
- RS-4: Get/list/status are read-only (AST check)
- RS-5: List rejects unbounded (limit outside 1-100)
- RS-6: All store responses include advisory boundary statements

### `scripts/test-qa-pilot-receipt-store.sh`
Bash test runner with 14 tests:
1. Store script exists
2. Store validator passes
3. Register a valid receipt
4. Get registered receipt
5. List receipts
6. Status reports
7. Register rejects authority claim
8. List rejects unbounded
9. Get includes advisory_notice
10. Existing receipt validator still passes (regression)
11. Existing receipt test runner still passes (regression)
12. Existing MCP surface validator still passes (regression)
13. Existing MCP surface test runner still passes (regression)
14. Store index is valid JSON

## Validation Results

### Receipt Store Validator
```
$ python3 scripts/validate-qa-pilot-receipt-store.py
  ✅ RS-1: Register validates receipt schema
  ✅ RS-2: Register rejects authority claims
  ✅ RS-3: Non-approval statement enforcement
  ✅ RS-4: Get/list/status are read-only (AST check)
  ✅ RS-5: List rejects unbounded
  ✅ RS-6: Advisory boundary in responses
  ✅ ALL CHECKS PASS
```

### Receipt Store Test Runner
```
$ bash scripts/test-qa-pilot-receipt-store.sh
Tests: 14 total
Pass:  14
Fail:  0
Result: 14/14 passed. All tests pass. ✅
```

### Existing QA Pilot Receipt Validator (Regression)
```
✅ ALL CHECKS PASS
```

### Existing QA Pilot MCP Surface Validator (Regression)
```
✅ ALL CHECKS PASS
```

### Prohibited-Zone Scan
```
The Librarian repo: not modified by this sprint
The Librarian status surfaces: not modified
The Librarian runtime/MCP enforcement: not mutated
External QA Pilot production repos: not touched
Result: CLEAN
```

### Store Index Format
```
{
  "store_version": "qap-store-v1",
  "last_updated": "...",
  "receipts": {
    "qapr-20260702-101": {
      "receipt_id": "qapr-20260702-101",
      "packet_type": "QAProductionReceipt",
      "status": "completed",
      "authority": "advisory",
      "project_id": "qa-pilot",
      "sprint_id": "QA-PILOT-RECEIPT-STORE-1",
      "stored_at": "...",
      "stored_path": "data/receipts/qapr-20260702-101.json",
      "content_hash": "sha256:..."
    }
  },
  "advisory_notice": "This receipt store is advisory-only..."
}
```

## Authority Boundary Confirmation

This sprint:
- ✅ **Does not** seal itself or claim Owner approval
- ✅ **Does not** mutate The Librarian repo
- ✅ **Does not** mutate QA Pilot production repositories (`qa-pilot-v2` or `QA-PilotV2`)
- ✅ **Does not** register runtime MCP handlers
- ✅ **Does not** mutate The Librarian MCP controller or runtime
- ✅ Register classifies receipts as advisory evidence only
- ✅ Get/list/status are read-only with advisory_notice
- ✅ List rejects unbounded (limit 1-100 required)
- ✅ All store responses include advisory boundary statements

## Acceptance Gates

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 1 | Receipt store governance doc exists | **Pass** | `docs/governance/QA-PILOT-RECEIPT-STORE.md` — 10 sections |
| 2 | Receipt store schema exists | **Pass** | `docs/schemas/qa-pilot-receipt-store.schema.json` — Draft 2020-12 |
| 3 | Receipt store script/module exists | **Pass** | `scripts/qa_pilot_receipt_store.py` — register/get/list/status CLI |
| 4 | Register behavior works | **Pass** | Test 3: register succeeded |
| 5 | Get behavior works | **Pass** | Test 4: found registered receipt |
| 6 | List behavior works with bounded limits | **Pass** | Test 5: returned 1 receipt |
| 7 | Status behavior works | **Pass** | Test 6: reports 1 receipt |
| 8 | Store rejects authority claims | **Pass** | Test 7: rejected authority-claim receipt |
| 9 | Store preserves advisory-only semantics | **Pass** | RS-2/RS-3 checks; advisory_notice in all responses |
| 10 | Existing receipt validation still passes | **Pass** | Test 10: receipt validator still passes |
| 11 | Existing MCP surface validation still passes | **Pass** | Tests 12-13: MCP validator/test runner still pass |
| 12 | Test runner passes | **Pass** | 14/14 pass |
| 13 | QA Pilot ledger remains project-local | **Pass** | Ledger #4 added (pending); only QA Pilot files touched |
| 14 | The Librarian repo remains untouched | **Pass** | Prohibited-zone scan: CLEAN |
| 15 | Closeout receipt exists and states pending Owner review | **Pass** | This document |

## Unresolved Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| No database backend — file-based store only | Low | Acceptable for QA Pilot's current scope |
| No concurrent access guarantees | Low | QA Pilot is single-agent/single-user at this stage |
| jsonschema dependency optional (falls back to structural check) | Low | Install jsonschema for full schema validation |
| Store not wired to runtime MCP handlers | Medium | Deferred to MCP handler integration sprint |

## Closeout Receipt

This sprint is closed (agent work complete) by the existence of:

1. 1 receipt store governance document (10 sections)
2. 1 receipt store schema (Draft 2020-12)
3. 1 receipt store Python module (4 operations: register, get, list, status)
4. 8 fixture files (4 valid, 4 invalid)
5. 1 store validator (6 rules RS-1-6)
6. 1 store test runner (14/14 passing, 4 regression guards)
7. QA Pilot sprint ledger entry #4
8. Updated FEATURE-STATUS.md and SESSION-HANDOFF.md
9. This closeout receipt

**This sprint does not:**
- Seal itself or any other sprint
- Claim Owner approval of any kind
- Mutate The Librarian repo
- Register runtime MCP handlers
- Mutate The Librarian MCP controller or runtime implementation
- Mutate production QA Pilot repos (`qa-pilot-v2`, `QA-PilotV2`)

**This sprint does:**
- Implement a QA Pilot-owned local receipt store
- Support receipt registration with schema validation and advisory enforcement
- Support receipt retrieval by receipt_id
- Support bounded receipt listing with optional filters
- Support receipt store status summary
- Enforce advisory-only authority on all store operations
- Preserve all existing QA Pilot validators and test runners

**Status: ✅ Sealed (ledger #4) — Owner-approved 2026-07-02 per OD-QA-PILOT-RECEIPT-STORE-1-SEAL**
