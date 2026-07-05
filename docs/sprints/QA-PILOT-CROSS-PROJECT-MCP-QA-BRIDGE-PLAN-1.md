# QA-PILOT-CROSS-PROJECT-MCP-QA-BRIDGE-PLAN-1 — Cross-Project QA / Training MCP Bridge Plan

**Type:** Planning / architecture sprint
**Lane:** `parallel_planning`
**Boundary:** `qa_pilot_local`
**Librarian impact:** `none`
**Status:** `planned`
**Design authority:** Owner Andrew Hannah — design direction DD-PROJECT-SANDBOX-MODEL-1 (2026-07-05)

---

## Intent

Define a governed MCP packet exchange so QA Pilot can consume Librarian project-state, planning claims, fixtures, and document snapshots for QA regression, help-doc generation, and local training simulation — without crossing authority boundaries.

MCP is the transport. Librarian remains authority. QA Pilot becomes the QA/training consumer. `/local` hosts simulated training based on the same structures.

---

## Architecture Overview

### Project Authority Ownership

| Project | Owns |
|---------|------|
| **Librarian** | Librarian DB, Librarian ledger, Librarian receipts, Librarian startup authority, Librarian MCP surface |
| **QA Pilot** | QA Pilot DB, QA Pilot ledger, QA Pilot receipts, QA Pilot startup authority, QA Pilot derived store |
| **Training Sim /local** | Local simulated/derived store only — never canonical authority |

### Cross-Project Packet Flow

```
Librarian DB
  |
  | governed MCP export packet
  v
QA Pilot inbound store
  |
  | ingested as advisory/derived copy
  v
QA Pilot local derived DB
  |
  | generated training packets
  v
/local/training-sim store (simulated only)
```

### Core Invariant

No cross-project write authority. Allowed:

1. Librarian exports packet
2. QA Pilot imports packet
3. QA Pilot generates QA result
4. QA Pilot submits proposal/report
5. Owner approves applying something to Librarian
6. Librarian records the accepted decision in Librarian DB/ledger

Not allowed:
- QA Pilot writes Librarian DB
- QA Pilot seals Librarian sprints
- QA Pilot changes Librarian roadmap
- QA Pilot promotes training sim results into authority
- Direct cross-project DB access (packet-gated only)

---

## Proposed MCP Tool Surface

### Librarian Export Tools (read-only / bounded export)

| Tool | Purpose |
|------|---------|
| `librarian_qa_claims_export` | Export testable claim registry |
| `librarian_qa_fixture_packet_export` | Export fixture packs for QA |
| `librarian_project_state_packet_get` | Get current canonical project-state packet |
| `librarian_milestone_regression_packet_get` | Get milestone regression data |
| `librarian_training_packet_export` | Export training/help-doc sources |
| `librarian_document_snapshot_get` | Get planning doc snapshots |

### QA Pilot Submit Tools (proposal-only / governed)

| Tool | Purpose |
|------|---------|
| `qa_pilot_regression_result_submit` | Submit QA regression results |
| `qa_pilot_claim_gap_report_submit` | Report claim gaps found during QA |
| `qa_pilot_training_doc_candidate_submit` | Propose training/help-doc candidates |
| `qa_pilot_fixture_recommendation_submit` | Propose new fixtures from QA findings |

### QA Pilot Ingest Packet Types

- Planning doc snapshots
- Testable claim registry
- Fixture packs
- Current canonical project-state packet
- Milestone regression packet
- Training/help-doc source packet
- Compact context packet for simulation

---

## Packet Custody Schema

Every cross-project packet must include these fields:

```json
{
  "packet_type": "qa_claim_registry | project_state | milestone_regression | training_source",
  "source_project": "librarian",
  "consumer_project": "qa-pilot",
  "authority_status": "authoritative_export | advisory_copy | training_simulated",
  "generated_at": "ISO-8601",
  "source_db_revision": "<string>",
  "source_packet_hash": "<sha256>",
  "source_docs": ["<path>", ...],
  "allowed_use": [
    "qa_regression",
    "training_doc_generation",
    "simulation"
  ],
  "forbidden_use": [
    "direct_librarian_mutation",
    "owner_decision_substitution",
    "authority_promotion"
  ],
  "owner_decision_required_for_apply": true
}
```

---

## Project Sandbox Model

Every new governed project gets its own sandbox at creation time.

### Minimum Sandbox Contents

```
/projects/<project-id>/
  project.db
  project-ledger.json
  receipts/
  fixtures/
  validators/
  reports/
  docs/
  startup/
    project_startup_authority
    STARTUP-COMPACT.md
  packets/
    inbound/
    outbound/
  local/
    simulations/
    derived/
```

### Onboarding Creates

- project ID
- project profile
- project DB
- project ledger
- receipt store
- startup authority record
- canonical project-state packet
- compact startup summary
- fixture directory
- validator directory
- packet exchange directories
- boundary declaration
- Owner authority declaration

### Core Rule

> A project sandbox is authoritative only for itself.

QA Pilot can own QA Pilot state. Librarian can own Librarian state. A training sim can own simulated state. None directly writes another project's authority store.

---

## Training Sim Local Structure

```
/local/training-sim/
  packets/
    project-state/
    milestone-regression/
    planning-claims/
    fixtures/
    help-doc-sources/
  scenarios/
    startup-authority/
    readiness-gate/
    seal-review/
    milestone-regression/
    owner-action-required/
  runs/
    run-*.json
  reports/
    training-report-*.md
```

The training sim uses the same structures as real project state (canonical project-state packet, startup authority, readiness gate, claim registry, fixture registry, Owner action choices, result receipts) but is clearly labeled `training_simulated` — not real authority.

---

## Sprint Breakdown (5-Sprint Sequence)

### 1. QA-PILOT-CROSS-PROJECT-MCP-QA-BRIDGE-PLAN-1 ← **this sprint**

Planning only. Defines:
- Allowed packet types
- Request/response schema
- Custody fields
- Read/export tools
- Submit/proposal tools
- Forbidden direct mutation
- QA Pilot local derived-store rules
- Training Sim packet rules

### 2. LIBRARIAN-QA-PACKET-EXPORT-1

Librarian-side implementation. Adds bounded export surfaces:
- `project-state packet`
- `planning-claim packet`
- `fixture packet`
- `milestone-regression packet`
- `document snapshot packet`

No QA Pilot mutation.

### 3. QA-PILOT-QA-PACKET-INGEST-1

QA Pilot-side implementation. Imports Librarian QA packets into QA Pilot-local derived storage.
Validates:
- Source project
- Packet hash
- `generated_at`
- `authority_source`
- Custody provenance
- Read-only/advisory status

### 4. QA-PILOT-MILESTONE-REGRESSION-SUITE-1

Runs regression against imported packets. Outputs:
- Pass/fail report
- Claim gaps
- Fixture gaps
- Unresolved Owner questions
- Proposed fixes

### 5. QA-PILOT-LOCAL-TRAINING-SIM-1

Builds `/local/training-sim` from imported packets. Outputs:
- Help-doc drafts
- Training scenarios
- Simulated Owner/agent workflows
- Evaluation receipts
- MCP packet custody fields

---

## What This Sprint May Produce

✅ QA Pilot planning docs
✅ QA Pilot-local bridge model
✅ QA packet schema drafts
✅ Proposed MCP tool contracts (design only)
✅ Local training sim plan
✅ Future QA Pilot implementation sprint briefs

## What This Sprint Must NOT Produce

❌ Librarian code changes
❌ Librarian DB writes
❌ Librarian MCP registration
❌ Librarian roadmap mutation
❌ Librarian seal/status changes
❌ Cross-project authority
❌ Any implementation code

## Boundary Assertion

```json
{
  "project_boundary": "qa-pilot",
  "lane": "parallel_planning",
  "librarian_impact": "none",
  "cross_project_registration": false,
  "runtime_mutation_authorized": false,
  "implementation_authorized": false
}
```

## Acceptance Gates

| Gate | Status |
|------|--------|
| Packet custody schema drafted | 🔍 Pending |
| Librarian export tools defined | 🔍 Pending |
| QA Pilot submit tools defined | 🔍 Pending |
| Packet type registry enumerated | 🔍 Pending |
| Cross-project protocol flow documented | 🔍 Pending |
| Training sim /local structure defined | 🔍 Pending |
| Sandbox onboarding model described | 🔍 Pending |
| Sprint breakdown sequenced | 🔍 Pending |
| Boundary rules enumerated and scoped | 🔍 Pending |
| No Librarian files referenced in mutation paths | 🔍 Pending |
| QA Pilot startup checks pass | 🔍 Pending |

## Design Authority References

- **Receipt:** `receipts/decision-resolutions/dd-project-sandbox-model-1.json`
- **Design direction:** Owner Andrew Hannah, 2026-07-05
- **Preceding work:** QA-PILOT-BROKER-AUDIT-STORE-HARDEN-1 (sealed #15)
- **Parallel with:** LIBRARIAN-DB-STARTUP-AUTHORITY-1, LIBRARIAN-READINESS-GATE-CANONICAL-1 (Librarian lane)
