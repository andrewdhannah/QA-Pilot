# QA Pilot Librarian Consumption Specification

**Status:** 🔍 Pending Owner review
**Authority:** Interface contract specification. Not an integration dependency.
**Sprint:** QA-PILOT-LIBRARIAN-WORK-QUEUE-INTEGRATION-1

---

## 1. Purpose

Document the future handoff from QA-Pilot work proposals to Librarian work packets. This is an **interface contract** — it specifies how the Librarian *may* consume QA-Pilot proposals. It is not a runtime dependency. The Librarian dispatch bridge must reach operational status before this handoff can be exercised end-to-end.

## 2. Current State

| System | Status |
|--------|--------|
| QA-Pilot diagnostic reports | ✅ Operational (qa-diagnostic-report.schema.json) |
| QA-Pilot work queue items | ✅ Operational (qa-work-queue-item.schema.json) |
| QA-Pilot work proposals | ✅ This sprint — contract and compiler |
| Librarian MCP tool surface | ✅ Routable (draft, authorize, get, list, bridge_status) |
| Librarian work packet draft | ⚠️ Tool exists but service unavailable (work_packet_service_available: false) |
| Librarian work packet authorize | ⚠️ Tool exists but service unavailable |
| Librarian work packet dispatch | ❌ Not available (bridge status: degraded) |
| Librarian work packet intake | ❌ Not available (0 intakes ever recorded) |
| Librarian work packet verification | ❌ Not available |
| Librarian work packet closure | ❌ Not available |

### MCP Diagnostic Trail (2026-07-24)

During QA-PILOT-LIBRARIAN-WORK-QUEUE-INTEGRATION-1 authorization, the Librarian work packet MCP tools were probed:

```
project_work_packet_bridge_status →
  work_packet_service_available: false
  selected_project_available: false
  selected_project_id: null
  bridge_status: degraded
  available_tools: [draft, authorize, get, list, bridge_status]
  limitations: [
    "No worker dispatch — authorization only",
    "No model/node assignment",
    "No verification execution",
    "No application or closure",
    "Packets stored as JSON files — DB not written by this service"
  ]
```

The MCP tool *surface* exists and is routable. The *backing service* is not operational. This is the contract-first approach: the interface was created ahead of the operational capability.

**This diagnostic trail is QA-Pilot evidence.** The missing Librarian operational layer is now documented with a concrete failure signal, not a guess. This is exactly the type of finding the QA-Pilot OBD2 loop is designed to catch.

### Dependency: LIBRARIAN-WORK-PACKET-SERVICE-ACTIVATION-1

The end-to-end loop requires a Librarian-owned sprint to activate the DB-backed work packet lifecycle:

```
project_work_packet_draft    → activate backing service
project_work_packet_authorize → activate backing service
project_work_packet_dispatch  → implement (does not exist)
project_work_result_intake    → implement (does not exist)
project_work_result_verify    → implement (does not exist)
project_work_packet_closure   → implement (does not exist)
```

This sprint is not yet created. When it is, it may use QA-Pilot proposal fixtures (from this sprint) as test inputs for the first real work packet lifecycle exercise.

**Conclusion:** The QA-Pilot side is complete and can seal independently (Tier 1). The end-to-end loop requires LIBRARIAN-WORK-PACKET-SERVICE-ACTIVATION-1 to complete first.

## 3. Handoff Flow

```
QA-Pilot Work Proposal (qa-work-proposal.schema.json)
      │
      │  ← advisory-only, no authority conferred
      │
      ▼
Human Review (Owner)
      │
      │  Owner reads proposal, decides whether to proceed
      │
      ▼
Librarian project_work_packet_draft
      │
      │  Owner or Librarian creates a work packet draft
      │  from the proposal content
      │
      ▼
project_work_packet_authorize
      │
      │  Owner authorizes the work packet
      │
      ▼
project_work_packet_dispatch
      │
      │  Librarian dispatches to agent
      │
      ▼
Agent Execution
      │
      │  Agent executes within authorized scope
      │
      ▼
project_work_result_intake
      │
      │  Agent submits work result
      │
      ▼
project_work_result_verify
      │
      │  Verification runs (may include QA-Pilot rerun)
      │
      ▼
Owner Decision
      │
      │  Owner approves or rejects
      │
      ▼
Closure
```

## 4. Field Mapping

When the Owner or Librarian converts a QA-Pilot proposal to a work packet draft, the following mapping is suggested:

| QA-Pilot Proposal Field | Librarian Work Packet Field |
|------------------------|---------------------------|
| `suggested_objective` | `scope` (first item) |
| `source_diagnostic_id` | `work_id` provenance reference |
| `constraints.must_not_modify` | `forbidden_paths` |
| `constraints.required_validation` | `validators_required` |
| `verification_requirements.rerun_tests` | `evidence_required` (test_output) |
| `verification_requirements.pass_criteria` | `acceptance_gates` (pass_criteria) |
| `affected_domain` | `work_type` mapping |
| `severity` | `agent_role` priority context |

## 5. Status Mapping (Observational)

QA-Pilot does not control Librarian states. This mapping is observational only:

| QA-Pilot Proposal Status | Librarian Equivalent | Who Transitions |
|--------------------------|---------------------|-----------------|
| OPEN | proposal_created | QA-Pilot (compiler) |
| REVIEW_REQUIRED | owner_review | QA-Pilot (advisory) |
| APPROVED | packet_authorized | Owner (via Librarian) |
| EXECUTING | agent_active | Librarian (dispatch) |
| VERIFIED | validation_passed | Librarian (verification) |
| CLOSED | owner_closed | Owner (decision) |

## 6. Authority Boundary

- QA-Pilot creates the proposal (OPEN)
- QA-Pilot marks the proposal as REVIEW_REQUIRED (advisory)
- The Owner reviews and decides
- The Librarian creates and authorizes the work packet
- The Librarian dispatches
- The Agent executes
- The Librarian verifies
- The Owner closes

**QA-Pilot never transitions the proposal beyond REVIEW_REQUIRED.** All subsequent states are observational — QA-Pilot may *report* them but may not *set* them.

## 7. Tier 2 Gates (Blocked)

The following acceptance gates are explicitly blocked until the Librarian dispatch bridge is operational:

| Gate | Requirement | Blocker |
|------|-------------|---------|
| WQI-005 | Librarian converts proposal into work packet | Librarian dispatch bridge not operational |
| WQI-006 | End-to-end dispatch → verification → closure completes | Librarian dispatch bridge not operational |

These gates are documented in the sprint acceptance criteria as Tier 2 — they cannot pass until the Librarian infrastructure advances. The sprint can seal with Tier 1 gates passing and Tier 2 gates documented as blocked.

## 8. Future Unblocking

When the Librarian dispatch bridge reaches operational status:

1. WQI-005 can be tested by converting a QA-Pilot proposal to a work packet draft
2. WQI-006 can be tested by running the full dispatch → intake → verification → closure chain
3. The operational dashboard (deferred) can be built to visualize the full lifecycle

Until then, the QA-Pilot side is complete: the contract, compiler, validator, and test runner are all QA-Pilot-local and can be validated independently.
