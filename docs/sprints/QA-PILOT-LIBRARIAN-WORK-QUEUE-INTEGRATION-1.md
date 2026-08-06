# QA-PILOT-LIBRARIAN-WORK-QUEUE-INTEGRATION-1 — Work Queue Integration

**Type:** operational integration
**Status:** ✅ **SEALED — Owner-sealed 2026-07-24**
**Lane:** operational
**Boundary:** QA Pilot-local
**Librarian impact:** contract_interface (interface contract only — no integration dependency)
**Epic:** EPIC-ASSURANCE-CONTRACT-EVOLUTION-1 (Phase 4 follow-on)
**Dependencies:** ASSURANCE-CONTRACT-EVIDENCE-FRESHNESS-SEMANTICS-1 (#213, sealed)
**Critical-path dependency:** LIBRARIAN-WORK-PACKET-SERVICE-ACTIVATION-1 (not yet created — Librarian-owned sprint to activate the DB-backed work packet dispatch/intake/verification/closure lifecycle)

---

## MCP Diagnostic Trail

During authorization of this sprint, the Librarian work packet MCP tools were probed:

```
project_work_packet_bridge_status →
  work_packet_service_available: false
  selected_project_available: false
  selected_project_id: null
  bridge_status: degraded
```

The MCP tool *surface* exists (draft, authorize, get, list, bridge_status are routable), but the *backing service* is not operational. The tool correctly rejected the request because the backend capability is unavailable.

**This is fail-closed behavior.** The interface failed closed instead of pretending capability existed. The alternative would have been worse: MCP reports "draft succeeded" with no durable intake, ambiguous authorization state, broken execution lineage, and fictional governance receipts. Instead, the system produced `bridge_status: degraded` and `work_packet_service_available: false` — a valid operational state.

This is not a bug. It is the contract-first approach: the MCP interface was created ahead of the operational backing service. The contract exists before the capability.

This diagnostic trail is itself QA-Pilot evidence: the missing Librarian operational layer is now documented with a concrete failure signal, not a guess. This incident is captured as a regression asset via WQI-008.

## Sprint Sequencing

The recommended order for closing the end-to-end loop:

1. **QA-PILOT-LIBRARIAN-WORK-QUEUE-INTEGRATION-1** (this sprint — QA-Pilot side)
   - Proposal contract, compiler, validator, test runner
   - Tier 1 gates pass (QA-Pilot-owned)
   - Tier 2 gates blocked (require Librarian service)

2. **LIBRARIAN-WORK-PACKET-SERVICE-ACTIVATION-1** (Librarian side — not yet created)
   - Activate DB-backed work packet service
   - Implement dispatch/intake/verification/closure path
   - Exercise first real work packet lifecycle
   - May use QA-Pilot proposal fixtures as test inputs

3. **QA-PILOT-REGRESSION-LEARNING-LOOP-1** (QA-Pilot side — deferred)
   - Verified fixes become reusable regression tests
   - Requires the end-to-end loop to be operational

This sprint can seal independently (Tier 1). The end-to-end loop requires sprint 2. The feedback loop requires both.

## Purpose

Create the governed bridge from QA-Pilot diagnostic findings to Librarian-compatible work proposals while maintaining strict authority separation.

QA-Pilot detects, explains, and proposes. The Librarian governs, authorizes, and dispatches. Agents execute. Humans decide.

This sprint fills the missing capability: the governed transition from "problem identified" to "approved work candidate" without crossing the authority boundary.

## Architecture

```
QA-Pilot Pipeline
      │
      ▼
Diagnostic Report (qa-diagnostic-report.schema.json)
      │
      ▼
QA-Pilot Work Proposal Compiler
      │
      ▼
QA-Pilot Work Proposal (qa-work-proposal.schema.json)
      │
      │  ← advisory-only, no authority conferred
      │
      ▼
Human Review (Owner)
      │
      ▼
Librarian project_work_packet_draft
      │
      ▼
Authorize → Dispatch → Execute → Verify → Close
```

**Key invariant:** QA-Pilot produces proposals. It does not call Librarian work packet MCP tools. It does not create work packets. It does not authorize, dispatch, or execute anything.

## Scope

### 1. Work Proposal Contract

Create `docs/schemas/qa-work-proposal.schema.json` — a proposal containing:

| Field | Source | Purpose |
|-------|--------|---------|
| `proposal_id` | Generated | Unique identifier (WP-QA-* pattern) |
| `source_diagnostic_id` | Diagnostic report | Provenance link to DIAG-* report |
| `source_test_id` | Diagnostic report | Provenance link to failing test |
| `failure_summary` | Diagnostic report | Expected/actual/reproduction context |
| `severity` | Diagnostic report | LOW/MEDIUM/HIGH/CRITICAL |
| `affected_domain` | Diagnostic report | regression/security/uat/etc. |
| `suggested_objective` | Compiler-generated | Advisory work objective |
| `constraints` | Diagnostic report | must_not_modify + required_validation |
| `verification_requirements` | Compiler-generated | rerun_tests + pass_criteria |
| `compliance_mappings` | Compiler-generated | Field mapping + status mapping |
| `limitations` | Fixed | advisory_only, no_execution_authority, no_mutation_authority |
| `provenance` | Compiler-generated | Full diagnostic → proposal trace |

**Forbidden fields** (must NOT exist in the proposal):
- `owner_approval` — the proposal does not approve anything
- `execution_permission` — the proposal does not permit execution
- `mutation_authority` — the proposal does not confer mutation authority

### 2. Diagnostic → Proposal Compiler

Create `scripts/qa_pilot_work_proposal_compiler.py`:

- **Input:** Diagnostic report (JSON conforming to qa-diagnostic-report.schema.json)
- **Output:** Work proposal (JSON conforming to qa-work-proposal.schema.json)
- **Rules:**
  - Deterministic — same input always produces same output
  - No Librarian MCP calls
  - No filesystem mutation outside QA-Pilot
  - Preserves provenance chain (diagnostic_id, test_id, detected_by, validation_run, pipeline_run)
  - Generates proposal_id from diagnostic domain + sequence
  - Maps diagnostic fields to proposal fields per the contract

### 3. Librarian Consumption Specification

Create `docs/governance/QA-PILOT-LIBRARIAN-CONSUMPTION-SPECIFICATION.md`:

Documents the future handoff as an **interface contract**, not an integration dependency:

```
QA-Pilot Proposal
      ↓
Human Review (Owner)
      ↓
Librarian project_work_packet_draft
      ↓
Authorize
      ↓
Dispatch
      ↓
Execute
      ↓
Verify
      ↓
Close
```

This is a specification of how the Librarian *may* consume QA-Pilot proposals. It is not a runtime dependency. The Librarian dispatch bridge must reach operational status before this handoff can be exercised end-to-end.

### 4. Status Mapping

Observational mapping only — QA-Pilot does not control Librarian states:

| QA-Pilot Proposal Status | Librarian Equivalent (observational) |
|--------------------------|--------------------------------------|
| OPEN | proposal_created |
| REVIEW_REQUIRED | owner_review |
| APPROVED | packet_authorized |
| EXECUTING | agent_active |
| VERIFIED | validation_passed |
| CLOSED | owner_closed |

## Acceptance Gates

### Tier 1 — QA-Pilot owned (can pass now)

| Gate | Requirement | Pass Criteria |
|------|-------------|---------------|
| WQI-001 | Diagnostic creates proposal | Compiler accepts diagnostic report input and emits proposal conforming to qa-work-proposal.schema.json |
| WQI-002 | Proposal preserves provenance | Every proposal contains valid source_diagnostic_id and source_test_id referencing real diagnostic/test artifacts |
| WQI-003 | Proposal validates against schema | Validator accepts all valid fixtures and rejects all invalid fixtures with clear rule violations |
| WQI-004 | Proposal contains verification requirements | No proposal with empty or missing verification_requirements passes validation |
| WQI-007 | QA-Pilot cannot mutate Librarian state | Forbidden-path scan clean, no Librarian MCP tool calls in any script, no execution authority fields in schema |
| WQI-008 | Fail-closed invariant | Missing work packet service must produce a diagnostic state and must not silently downgrade governance. Regression gate from MCP outage diagnostic trail 2026-07-24. |

### Tier 2 — Future dependency (explicitly blocked)

| Gate | Requirement | Pass Criteria |
|------|-------------|---------------|
| WQI-005 | Librarian converts proposal into work packet | BLOCKED — requires Librarian dispatch bridge operational. Documented as interface contract in consumption specification. |
| WQI-006 | End-to-end dispatch → verification → closure completes | BLOCKED — requires Librarian dispatch bridge operational. Documented as interface contract in consumption specification. |

## Deferred

### Regression Learning Loop → QA-PILOT-REGRESSION-LEARNING-LOOP-1

The fix → regression feedback loop introduces a new feedback authority:

```
Fix completed
    ↓
Should this become a permanent test?
```

That deserves its own contract and is deferred to a separate sprint.

### Operational Dashboard

Deferred until the proposal lifecycle exists. A dashboard visualizing incomplete state has no value.

## Authority Boundary

This sprint is within QA-Pilot's `harness_governed` boundary:

- Creates only QA-Pilot-local artifacts (schemas, scripts, fixtures, validators, governance docs)
- Does not call `project_work_packet_draft` or any Librarian work packet MCP tool
- Does not mutate any Librarian path (per QA-PILOT-PROJECT-GOVERNANCE.md §4)
- The proposal format is a QA-Pilot-owned contract that the Librarian *may* consume but is not required to

## Verification

- Validator: `scripts/validate-qa-pilot-work-proposal.py` (WQI rules)
- Test runner: `scripts/test-qa-pilot-work-proposal.sh`
- Fixtures: `fixtures/work-proposal/` (valid + invalid)
- Existing delegation validator: `scripts/validate-qa-pilot-delegation.py` must remain green

---

**Authorized by:** Andrew Hannah, 2026-07-24
**Authorization scope:** Proposal artifact, not work packet. QA-Pilot-local execution. Tier 1/Tier 2 acceptance split. Librarian dispatch dependency documented, not embedded.

**Sealed by:** Andrew Hannah, 2026-07-24
**Sealed as:** Ledger #214
**Seal note:** Tier 1 gates 6/6 PASS (WQI-001 through WQI-004, WQI-007, WQI-008). WQI-008 established fail-closed regression coverage for unavailable execution capability. Tier 2 gates (WQI-005, WQI-006) remain blocked by LIBRARIAN-WORK-PACKET-SERVICE-ACTIVATION-1. Blocking condition is external dependency, not implementation failure. 19/19 tests pass. No Librarian paths mutated. No execution authority in schema. No Librarian MCP tool calls in compiler.
