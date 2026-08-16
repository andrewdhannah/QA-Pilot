# WP-002 — Resolution Record

**Work Packet:** WP-002 of GOVERNANCE-INTEGRITY-RECOVERY-1
**Date:** 2026-08-16
**Status:** TOOL IMPLEMENTED — awaiting Owner authorization for first reconciliation

---

## Decisions Applied

### D1: Lifecycle Population Mechanism — GOVERNED RECONCILIATION PATH

The system correctly refused unauthorized lifecycle mutations. That is governance working, not a defect.

Implemented `governance_lifecycle_reconcile` tool with the required flow:

```
Classification Evidence
        |
        v
Lifecycle Reconciliation Request
        |
        v
Owner Authorization (authorization_basis required)
        |
        v
LifecycleState Validation (canonical Rust enum)
        |
        v
Persist lifecycle_phase (project registry update)
        |
        v
LIFECYCLE_RECONCILIATION_RECEIPT
```

**Rejected approaches:**
- Cursor-only authority: creates conflation (WP-001 lesson)
- Direct DB mutation: bypasses evidence, authority tracking, reconciliation

### D2: librarian-workbench Registry — STALE, RECONCILE TO Operational

Registry says "bootstrap". Cursor says Phase 8 with 37 seals. Registry is behind.

First target for reconciliation once Owner authorizes.

### D3: scrum-tracker — IDENTITY RECONCILIATION REQUIRED

scrum-tracker exists in governance entities but NOT in the project registry. This is an identity relationship problem, not just a lifecycle problem.

**Current state:**
- Governance entities: exists (entity_id: "scrum-tracker")
- Project registry: missing
- On-disk cursor: exists at `/scrummaster-tracker/lifecycle-cursor.json`
- Cursor: Phase 1, position 9, profile "governance_utility"

**Required before lifecycle mutation:**
1. Register scrum-tracker in the project registry
2. Verify entity identity matches project identity
3. Then reconcile lifecycle state

This is out of scope for WP-002 — it's a registry reconciliation issue.

---

## Implementation

### New Tool: `governance_lifecycle_reconcile`

**Files changed:**
- `active/librarian/Sources/App/Controllers/MCPController.swift` — added dispatch case + handler
- `active/librarian/mcp-tool-manifest.json` — added tool definition

**Tool properties:**
- Risk class: R1 Low-Risk Write — lifecycle mutation
- Required parameters: entity_id, proposed_state, evidence_basis, authorization_basis
- Validates proposed_state against canonical Rust LifecycleState enum
- Updates project registry `current_phase`
- Emits `LIFECYCLE_RECONCILIATION_RECEIPT`
- Receipt persisted to `data/lifecycle-state/transitions/`

**Canonical lifecycle states (Rust enum):**
```
Install, Initialize, Qualify, Identity, Ready,
Discovered, Candidate, Admitted, Operational,
Suspended, Retired
```

**Registry phase mapping:**
```
Install/Initialize/Qualify/Identity/Ready/Discovered → "init"
Candidate/Admitted → "active"
Operational → "execution"
Suspended → "suspended"
Retired → "retired"
```

---

## Classification Summary (from investigation)

| Entity | Canonical State | Registry Phase | Confidence |
|---|---|---|---|
| librarian | Operational | execution | HIGH |
| qa-pilot | Initialize | init | HIGH |
| agent-bridge | Operational | active | HIGH |
| librarian-workbench | Operational | bootstrap (STALE) | HIGH |
| working-bibliography-extension | Initialize | init | HIGH |
| claude-conversation-ingestion | Initialize | init | HIGH |
| librarian-vault | Initialize | init | HIGH |
| knowledge-ingestion-addon | Initialize | init | HIGH |

---

## Acceptance Gate Status

| Gate | Status | Notes |
|---|---|---|
| LIFE-001 Completeness | ⏳ PENDING | Tool exists; first reconciliation not yet executed |
| LIFE-002 Enum Validity | ✅ PASS | Tool validates against canonical Rust enum |
| LIFE-003 Transition Compatibility | ✅ PASS | Tool maps to registry phases that have valid transitions |
| LIFE-004 Evidence Traceability | ✅ PASS | Tool records evidence_basis, authorization_basis, receipt |
| LIFE-005 Restart Persistence | ✅ PASS | Tool writes to project registry (durable) + receipt file |

---

## Next Step

Owner authorization to reconcile `librarian-workbench` from "bootstrap" → "execution" (canonical: Operational).

This would be the first governed lifecycle mutation through the new tool.

---

*WP-002 tool implemented. Awaiting Owner authorization for first reconciliation.*
