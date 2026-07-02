# QA-PILOT-MCP-SURFACE-1 — QA Pilot MCP Surface (Lane B)

**Project:** QA Pilot
**Status:** 🔍 Pending Owner review (not sealed)
**Authority:** Advisory only. Tool stubs/contracts only — no runtime MCP registration.

**Sprint type:** QA Pilot Lane B — MCP tool stub contracts and validation.
**Sprint ID:** `QA-PILOT-MCP-SURFACE-1`
**Date:** 2026-07-02
**Branch:** `main`
**Starting HEAD:** `ea20417`
**Predecessor:** QA-PILOT-PRODUCTION-LANE-A-1 (sealed #2)
**Authorization basis:** Owner-approved per OD-QA-PILOT-PRODUCTION-LANE-A-1-SEAL — "Next authorized sprint: QA-PILOT-MCP-SURFACE-1. Scope: Implement QA Pilot MCP tool stubs for production receipt registration, query, and status surfaces under the QA Pilot project boundary."
**Authority:** Advisory only. Tool stubs only — no runtime MCP registration, no The Librarian MCP mutation.

---

## Objective

Define QA Pilot MCP tool stubs for production receipt registration, receipt query, and receipt status surfaces under the QA Pilot project boundary. Create contracts, schemas, fixtures, validator, and test infrastructure for four tools that will later be registered as actual MCP tools.

## MCP Tools Defined

| Tool | Authority | Purpose |
|------|-----------|---------|
| `qa_pilot_receipt_register` | R1 (advisory mutation) | Register a QA Pilot production receipt as advisory evidence |
| `qa_pilot_receipt_get` | R0 (read-only) | Retrieve a QA Pilot receipt by receipt_id |
| `qa_pilot_receipt_list` | R0 (read-only) | List bounded QA Pilot receipts with filters |
| `qa_pilot_receipt_status` | R0 (read-only) | Summarize QA Pilot receipt store and validation status |

## Files Created

### `docs/governance/QA-PILOT-MCP-SURFACE.md`
Governance document (8 sections): purpose, tool inventory (4 tools with input/output tables), authority model (MP-1 through MP-4), non-effects, input/output contract reference, relationship to existing components, non-goals, required boundaries.

### `docs/schemas/qa-pilot-mcp-tool.schema.json`
Draft 2020-12 schema defining all four tool input/output contracts:
- `receipt_register_input` / `receipt_register_output`
- `receipt_get_input` / `receipt_get_output`
- `receipt_list_input` / `receipt_list_output`
- `receipt_status_input` / `receipt_status_output`

### `docs/examples/qa-pilot-mcp-surface/` (8 fixture files)

| File | Type | Tool | Description |
|------|------|------|-------------|
| `valid-receipt-register.json` | Valid | Register | Advisory receipt register with full input/output, advisory_only=true, non_effects |
| `valid-receipt-get.json` | Valid | Get | Read-only receipt query with advisory_notice |
| `valid-receipt-list.json` | Valid | List | Bounded list (limit=50) with advisory_notice |
| `valid-receipt-status.json` | Valid | Status | Empty input, status-only read-only output with advisory_notice |
| `invalid-register-authority-claim.json` | Invalid | Register | authority='authoritative', output claims approved_and_sealed, advisory_only=false |
| `invalid-list-unbounded.json` | Invalid | List | limit=0 (violates 1-100 range) |
| `invalid-get-missing-receipt-id.json` | Invalid | Get | Empty receipt_id |
| `invalid-status-mutating-authority.json` | Invalid | Status | Non-empty input (action='seal_all_pending'), output claims sealed/approved |

### `scripts/validate-qa-pilot-mcp-surface.py`
Python validator with 13 business rules:
- MP-1: Register tools classify as advisory evidence only
- MP-2: Query/list/status tools are R0 read-only
- MP-3: No authority claims in output
- MP-4: Advisory/read-only boundary statements present
- R-1: Register input receipt authority='advisory'
- R-2: Register output advisory_only=true
- R-3: Register output non_effects advisory language
- G-1: Get input receipt_id pattern
- G-2: Get output advisory_notice
- L-1: List input limit 1-100
- L-2: List output advisory_notice
- S-1: Status input empty
- S-2: Status output no seal/approve

### `scripts/test-qa-pilot-mcp-surface.sh`
Bash test runner with 14 tests:
1. Validator exists
2. --list-rules works
3. Valid fixtures all pass (4/4)
4. Invalid fixtures correctly rejected (4/4)
5. --all mode passes
6. --all --include-invalid detects failures
7. Non-existent file fails
8. AST meta-check (no authority-granting code)
9. Schema file exists and is valid JSON
10. Governance doc exists
11. PROJECT-PROFILE.json has required fields
12. Sprint ledger valid
13. Existing receipt validator still passes (regression guard)
14. Existing receipt test runner still passes (regression guard)

## Validation Results

### MCP Surface Validator
```
$ python3 scripts/validate-qa-pilot-mcp-surface.py
  ✅ valid-receipt-get.json — 13/13 checks pass
  ✅ valid-receipt-list.json — 13/13 checks pass
  ✅ valid-receipt-register.json — 13/13 checks pass
  ✅ valid-receipt-status.json — 13/13 checks pass
  ✅ ALL CHECKS PASS

$ python3 scripts/validate-qa-pilot-mcp-surface.py --include-invalid
  ❌ invalid-get-missing-receipt-id.json — 12/13 checks pass
       FAIL G-1: G-1: get input receipt_id is empty
  ❌ invalid-list-unbounded.json — 12/13 checks pass
       FAIL L-1: L-1: list input limit must be 1-100, got 0
  ❌ invalid-register-authority-claim.json — 7/13 checks pass
       FAIL MP-1, MP-2, MP-4, R-1, R-2, R-3
  ❌ invalid-status-mutating-authority.json — 11/13 checks pass
       FAIL S-1, S-2
  Valid fixtures:   4/4 passed (all pass)
  Invalid fixtures: 4/4 rejected (all rejected)
```

### Test Runner
```
$ bash scripts/test-qa-pilot-mcp-surface.sh
Tests: 14 total
Pass:  14
Fail:  0
Result: 14/14 passed. All tests pass. ✅
```

### Existing Receipt Validator (Regression)
```
$ python3 scripts/validate-qa-pilot-receipt.py
✅ ALL CHECKS PASS
```

### Prohibited-Zone Scan
```
The Librarian repo: not modified by this sprint
The Librarian HEAD: abeea3e (seal: SPRINT-PACKET-BRIDGE-1 at ledger #227)
  — external commit, not from this sprint
Pre-existing modifications: none
New untracked files: none
Result: CLEAN — no The Librarian files modified by this sprint.
```

### AST Meta-Check
```
✅ Validator contains no authority-granting code
```

## Authority Boundary Confirmation

This sprint:
- ✅ **Does not** seal itself or claim Owner approval
- ✅ **Does not** mutate The Librarian repo
- ✅ **Does not** mutate QA Pilot production repositories (`qa-pilot-v2` or `QA-PilotV2`)
- ✅ **Does not** register runtime MCP handlers
- ✅ **Does not** mutate The Librarian MCP controller or runtime
- ✅ **Does not** alter mainline sprint authority or Owner decision records
- ✅ All tool contracts enforce advisory/read-only authority levels
- ✅ Register tool classifies receipts as advisory evidence only
- ✅ Query/list/status tools are R0 read-only
- ✅ List tool rejects unbounded listing
- ✅ Invalid fixtures claiming authority are correctly rejected
- ✅ AST meta-check confirms no authority-granting code

## Acceptance Gates

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 1 | MCP surface governance doc exists | **Pass** | `docs/governance/QA-PILOT-MCP-SURFACE.md` — 8 sections |
| 2 | MCP tool schema/contract exists | **Pass** | `docs/schemas/qa-pilot-mcp-tool.schema.json` — Draft 2020-12, 4 tool sub-schemas |
| 3 | Four required tool stubs represented | **Pass** | register (R1), get (R0), list (R0), status (R0) |
| 4 | Valid fixtures exist for all four tools | **Pass** | 4 valid fixtures, one per tool |
| 5 | Invalid fixtures cover authority claims, missing identifiers, unbounded list, mutating status | **Pass** | 4 invalid fixtures covering each violation |
| 6 | Validator enforces advisory/read-only boundaries | **Pass** | MP-1-4 + R/G/L/S rules, all enforced |
| 7 | Test runner passes | **Pass** | 14/14 pass |
| 8 | Existing QA Pilot production receipt validation still passes | **Pass** | Receipt validator and test runner both pass |
| 9 | QA Pilot ledger remains project-local | **Pass** | Ledger #3 added (pending); only QA Pilot files touched |
| 10 | The Librarian repo remains untouched | **Pass** | Prohibited-zone scan: CLEAN |
| 11 | Closeout receipt exists and states pending Owner review | **Pass** | This document |

## Unresolved Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| MCP tool stubs not yet registered as runtime MCP handlers | Medium | Deferred to runtime implementation sprint |
| No receipt store implementation — tools define contracts only | Medium | Deferred to receipt store implementation sprint |
| No cross-project MCP invocation defined | Low | Future QA Pilot integration sprint |
| No gRPC/HTTP transport layer defined | Low | Tools are stubs/contracts only at this stage |

## Closeout Receipt

This sprint is closed (agent work complete) by the existence of:

1. 1 MCP surface governance document (8 sections)
2. 1 MCP tool contract schema (Draft 2020-12, 4 tool sub-schemas)
3. 8 fixture files (4 valid, 4 invalid) covering all four tools
4. 1 validator (13 rules: MP-1-4 + R-1-3 + G-1-2 + L-1-2 + S-1-2)
5. 1 test runner (14/14 passing, including regression guards for existing receipt validation)
6. QA Pilot sprint ledger entry #3
7. Updated FEATURE-STATUS.md and SESSION-HANDOFF.md
8. This closeout receipt

**This sprint does not:**
- Seal itself or any other sprint
- Claim Owner approval of any kind
- Mutate The Librarian repo
- Register runtime MCP handlers
- Mutate The Librarian MCP controller or runtime implementation
- Mutate production QA Pilot repos (`qa-pilot-v2`, `QA-PilotV2`)

**This sprint does:**
- Define QA Pilot MCP tool stubs for production receipt workflows
- Define input/output contracts for all four tools
- Enforce advisory/read-only authority boundaries
- Require bounded listing (limit 1-100, required)
- Require advisory notice in all query/list/status outputs
- Classify register tool as advisory mutation only with non_approval checks
- Preserve existing QA Pilot production receipt validation

**Status: 🔍 Pending Owner review (not sealed)**
