# QA-PILOT-LIBRARIAN-MCP-CUSTODY-PACKET-1 — QA Pilot ↔ Librarian MCP Custody

**Project:** QA Pilot
**Status:** ✅ **Sealed (ledger #6)** — Owner-approved 2026-07-02 per OD-QA-PILOT-LIBRARIAN-MCP-CUSTODY-PACKET-1-SEAL
**Authority:** Decision/constraint only. No implementation authorized.

**Sprint type:** Decision / custody constraint sprint.
**Sprint ID:** `QA-PILOT-LIBRARIAN-MCP-CUSTODY-PACKET-1`
**Date:** 2026-07-02
**Branch:** `main`
**Starting HEAD:** `14e80ea`
**Predecessor:** QA-PILOT-MCP-HANDLER-REGISTRATION-1 (sealed #5)
**Authorization basis:** Owner-approved per OD-QA-PILOT-MCP-HANDLER-REGISTRATION-1-SEAL — "Create a cross-project custody packet authorizing, constraining, or rejecting future integration of QA Pilot local handler stubs into The Librarian MCP runtime."
**Authority:** Decision/constraint only. No runtime implementation, no project boundary crossing.

---

## Decision Outcome

| Decision | Value |
|----------|-------|
| Current operating mode | **Option A — Separate MCP (preserved)** |
| Next authorized path | **Option B planning only** |
| Option C authorization | **Not authorized** |

## Options Modeled

### Option A — Separate MCP / Local Handler Surface (Current ✅)
QA Pilot owns and runs its own local handler surface. The Librarian does not route, broker, or register QA Pilot tools. This is the current operating mode and remains the default.

### Option B — Librarian Brokered Calls (Planning Only)
The Librarian may later expose broker tools that route to QA Pilot handlers, but only when custody records prove QA Pilot project context. **Planning is authorized. Implementation is not.**

### Option C — Native Librarian MCPController Registration (Not Authorized)
QA Pilot tools registered directly in The Librarian MCPController. Highest coupling. **Not authorized for planning or implementation.**

## Custody Conditions (CC-1 through CC-10)

Any future Option B implementation must satisfy all 10 conditions:

**Identity (CC-1-4):**
- `active_project_id == "qa-pilot"`
- `target_project_id == "qa-pilot"`
- Requested tool belongs to sealed QA Pilot MCP surface
- QA Pilot ledger has relevant sprint sealed

**Authority (CC-5-7):**
- Handler path is project-local (`active/qa-pilot/scripts/`)
- Request carries custody record proving project context
- Output remains advisory/read-only/R1 per sealed contract

**Safety (CC-8-10):**
- Output must not create Owner approval, seal, merge, or production-readiness state
- All broker calls produce receipt/audit evidence
- Rollback path documented before implementation

## Forbidden Actions (Never Authorized by This Packet)
1. Merging QA Pilot into The Librarian as subsystem
2. Registering QA Pilot tools directly in Librarian MCPController
3. Removing `project_boundary` or `cross_project_registration` invariants
4. Allowing handler output to create approval/seal/merge state
5. Allowing handler output to bypass Librarian custody model
6. Deleting or modifying sealed QA Pilot sprint documents

## Files Created

### `docs/governance/QA-PILOT-LIBRARIAN-MCP-CUSTODY.md`
Full governance document (9 sections): purpose, current default, integration options (A/B/C), recommended outcome, custody conditions (CC-1-10), forbidden actions, required components for Option B planning, non-goals, required boundaries.

### `docs/schemas/qa-pilot-librarian-mcp-custody.schema.json`
Draft 2020-12 schema for custody packets. Enforces:
- `decision_mode: "decision_only"`
- `current_operating_mode: "option_a_separate_mcp"`
- `project_boundary_assertion: "qa-pilot"`
- `cross_project_registration_assertion: false`

### `docs/examples/qa-pilot-librarian-mcp-custody/` (6 fixture files)

| File | Type | Description |
|------|------|-------------|
| `valid-option-a-current.json` | Valid | Current operating mode, decision only, Option B planning |
| `valid-option-b-planning-only.json` | Valid | Option B as possible future path, no implementation |
| `valid-decision-only-invariants.json` | Valid | Strict Option A, no planning authorized |
| `invalid-native-registration-authorized.json` | Invalid | Claims implementation_authorized for Option C |
| `invalid-missing-project-context.json` | Invalid | project_boundary=librarian, cross_project_registration=true |
| `invalid-cross-project-registration.json` | Invalid | Same violations plus implementation_authorized |

### `scripts/validate-qa-pilot-librarian-mcp-custody.py`
Python validator with 8 rules (CD-1 through CD-8):
- CD-1-3: Schema-enforced decision constraints
- CD-4: project_boundary_assertion is 'qa-pilot'
- CD-5: cross_project_registration_assertion is false
- CD-6: custody_conditions has all sections
- CD-7: forbidden_actions is non-empty
- CD-8: No Librarian runtime references in custody docs

### `scripts/test-qa-pilot-librarian-mcp-custody.sh`
Test runner with 14 tests:
1. Validator exists
2. --list-rules works
3. Valid fixtures all pass (3/3)
4. Invalid fixtures all fail (3/3)
5. Governance doc exists
6. Schema valid JSON
7. CD-8: No Librarian runtime refs
8. All 6 fixture files exist
9-12. All 4 existing validators still pass (regression)
13. No valid fixture claims implementation authority
14. Prohibited-zone scan clean

## Validation Results

### Custody Validator
```
$ python3 scripts/validate-qa-pilot-librarian-mcp-custody.py
  ✅ valid-decision-only-invariants.json — 8/8 checks pass
  ✅ valid-option-a-current.json — 8/8 checks pass
  ✅ valid-option-b-planning-only.json — 8/8 checks pass
  ✅ CD-8: No Librarian runtime references
  ✅ ALL CHECKS PASS

--include-invalid:
  ❌ invalid-cross-project-registration.json — 4/8 checks pass (4 expected failures)
  ❌ invalid-missing-project-context.json — 4/8 checks pass (4 expected failures)
  ❌ invalid-native-registration-authorized.json — 5/8 checks pass (3 expected failures)
  Valid fixtures:   3/3 passed
  Invalid fixtures: 3/3 rejected
  ✅ ALL CHECKS PASS
```

### Test Runner
```
14/14 passed. All tests pass. ✅
```

### Existing Validators (Regression)
```
Receipt validator:   ✅ ALL CHECKS PASS
MCP surface:         ✅ ALL CHECKS PASS
Store validator:     ✅ ALL CHECKS PASS
Handler validator:   ✅ ALL CHECKS PASS
```

### Prohibited-Zone Scan
```
The Librarian repo: not modified by this sprint
The Librarian MCPController: not mutated
Runtime MCP handlers: not registered
Cross-project integration: not performed
External QA Pilot production repos: not touched
Result: CLEAN
```

## Architecture Invariants Preserved

| Invariant | Status | Evidence |
|-----------|--------|----------|
| `project_boundary: "qa-pilot"` | ✅ Preserved | CD-4: all fixtures + schema enforce |
| `cross_project_registration: false` | ✅ Preserved | CD-5: all fixtures + schema enforce |
| No Librarian MCPController refs | ✅ Preserved | CD-8: text scan clean |
| QA Pilot owns its MCP surface | ✅ Preserved | Governance doc §2 |
| No implementation authorized | ✅ Preserved | CD-1: decision_mode=decision_only |

## Acceptance Gates

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 1 | Custody governance doc exists | **Pass** | 9 sections — Option A/B/C, CC-1-10, forbidden actions |
| 2 | Custody packet schema exists | **Pass** | Draft 2020-12, enforces decision_only, qa-pilot boundary |
| 3 | 3 valid fixtures pass | **Pass** | All 8/8 checks pass |
| 4 | 3 invalid fixtures fail | **Pass** | All rejected on expected rules |
| 5 | CC-1-10 documented | **Pass** | Identity, authority, safety conditions |
| 6 | Option A preserved as default | **Pass** | Governance doc §2: operating mode is Option A |
| 7 | Option B planning only (no implementation) | **Pass** | CD-3: authorized_next_path is planning-only |
| 8 | Option C not authorized | **Pass** | Invalid fixture catches this |
| 9 | All 4 existing validators pass | **Pass** | Receipt, MCP surface, store, handler — all still pass |
| 10 | No Librarian runtime references | **Pass** | CD-8: text scan clean |
| 11 | Prohibited-zone scan clean | **Pass** | No Librarian files modified |
| 12 | Closeout exists, pending Owner review | **Pass** | This document |

## Closeout Receipt

This sprint is closed (agent work complete) by the existence of:

1. 1 custody decision governance document (9 sections)
2. 1 custody packet schema (Draft 2020-12)
3. 6 fixture files (3 valid, 3 invalid)
4. 1 custody validator (8 rules CD-1-8)
5. 1 custody test runner (14/14 passing, 4 regression guards)
6. QA Pilot sprint ledger entry #6
7. Updated FEATURE-STATUS.md and SESSION-HANDOFF.md
8. This closeout receipt

**This sprint does not:**
- Seal itself or any other sprint
- Claim Owner approval of any kind
- Mutate The Librarian repo
- Register or implement any runtime MCP handlers
- Mutate The Librarian MCPController or Swift sources
- Cross the QA Pilot → The Librarian project boundary
- Authorize Option B or C implementation
- Change QA Pilot handler behavior

**This sprint does:**
- Define the custody conditions for any future Librarian brokering of QA Pilot tools
- Preserve QA Pilot's project_boundary and cross_project_registration invariants
- Model Option A (current), Option B (planning only), and Option C (not authorized)
- Recommend Option A as current operating mode, Option B planning as next possible path
- Document 10 custody conditions (CC-1-10) for any future Option B implementation
- Preserve all 4 existing QA Pilot validators and test runners

**Status: ✅ Sealed (ledger #6) — Owner-approved 2026-07-02 per OD-QA-PILOT-LIBRARIAN-MCP-CUSTODY-PACKET-1-SEAL**
