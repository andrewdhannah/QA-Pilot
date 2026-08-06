# QA Pilot Work Proposal Contract — Governance

**Status:** 🔍 Pending Owner review
**Authority:** Governance documentation only. QA Pilot is a separate add-on project with its own ledger.
**Sprint:** QA-PILOT-LIBRARIAN-WORK-QUEUE-INTEGRATION-1

---

## 1. Purpose

Define the governed contract for QA-Pilot work proposals — advisory repair proposals produced from diagnostic findings. The proposal is the bridge between QA-Pilot's detection/explanation capability and the Librarian's work execution system.

## 2. Authority Model

```
QA-Pilot detects     →  Diagnostic Report
QA-Pilot explains    →  Work Queue Item
QA-Pilot proposes    →  Work Proposal (this contract)
                         ↓
Human reviews         →  Owner decision
Librarian drafts      →  project_work_packet_draft
Owner authorizes       →  project_work_packet_authorize
Librarian dispatches  →  project_work_packet_dispatch
Agent executes        →  work result
QA-Pilot verifies     →  verification rerun
Owner closes          →  owner decision
```

**Key invariant:** QA-Pilot produces proposals. It does not:
- Call Librarian work packet MCP tools
- Create work packets
- Authorize, dispatch, or execute anything
- Confer execution permission or mutation authority

## 3. Proposal Schema

See `docs/schemas/qa-work-proposal.schema.json` for the canonical schema.

### Required Fields

| Field | Type | Source |
|-------|------|--------|
| `proposal_id` | string (WP-QA-* pattern) | Compiler-generated |
| `source_diagnostic_id` | string (DIAG-* pattern) | Diagnostic report |
| `source_test_id` | string | Diagnostic report |
| `failure_summary` | object | Diagnostic report |
| `severity` | enum | Diagnostic report |
| `affected_domain` | enum | Diagnostic report |
| `suggested_objective` | string | Compiler-generated |
| `constraints` | object | Diagnostic report |
| `verification_requirements` | object | Compiler-generated |
| `compliance_mappings` | object | Compiler-generated |
| `limitations` | object | Fixed (advisory-only) |
| `provenance` | object | Compiler-generated |

### Forbidden Fields

The following fields must NOT exist in any work proposal:

| Forbidden Field | Reason |
|-----------------|--------|
| `owner_approval` | Proposals do not approve — the Owner approves separately |
| `execution_permission` | Proposals do not permit execution — the Librarian authorizes |
| `mutation_authority` | Proposals do not confer mutation authority — the Librarian governs mutation |

## 4. Provenance Chain

Every proposal must preserve the full diagnostic → proposal trace:

```
Diagnostic Report (DIAG-*)
    ├── report_id      → source_diagnostic_id
    ├── test_id        → source_test_id
    ├── severity       → severity
    ├── domain         → affected_domain
    ├── failure        → failure_summary
    ├── constraints    → constraints
    └── provenance
        ├── detected_by    → provenance.detected_by
        ├── validation_run  → provenance.validation_run
        └── pipeline_run   → provenance.pipeline_run
```

## 5. Status Mapping (Observational Only)

QA-Pilot does not control Librarian states. The status mapping is observational — it describes what the Librarian state *would be* if the proposal were consumed:

| QA-Pilot Proposal Status | Librarian Equivalent |
|--------------------------|---------------------|
| OPEN | proposal_created |
| REVIEW_REQUIRED | owner_review |
| APPROVED | packet_authorized |
| EXECUTING | agent_active |
| VERIFIED | validation_passed |
| CLOSED | owner_closed |

## 6. Boundary Invariants

1. The proposal schema must not contain execution authority fields
2. The compiler must not call Librarian MCP tools
3. The compiler must not write outside QA-Pilot paths
4. The proposal must preserve the full provenance chain
5. The proposal must contain concrete verification requirements
6. The proposal is advisory-only — it confers no authority

## 7. Relationship to Existing Contracts

| Contract | Relationship |
|----------|-------------|
| qa-diagnostic-report.schema.json | Source — proposals are compiled from diagnostic reports |
| qa-work-queue-item.schema.json | Predecessor — queue items organize detected issues; proposals convert them to repair candidates |
| qa-work-packet.schema.json | Successor (Librarian-owned) — proposals may be consumed to create work packets |
| QA-PILOT-PROJECT-GOVERNANCE.md | Boundary — defines forbidden cross-project paths |

## 8. Non-Goals

- No Librarian work packet creation
- No Librarian MCP tool calls
- No execution authority
- No mutation authority
- No automatic proposal-to-packet conversion
- No regression learning loop (deferred to QA-PILOT-REGRESSION-LEARNING-LOOP-1)
- No operational dashboard (deferred until proposal lifecycle exists)
