# GOVERNANCE-INTEGRITY-RECOVERY-1

**Work Order ID:** GIR-001
**Project:** qa-pilot
**Agent:** openwork-claude (mimo-v2.5)
**Created:** 2026-08-16T04:40Z
**Status:** planned
**Authority Scope:** restricted

---

## Objective

Restore operational trust in the governance substrate by repairing state integrity, establishing lifecycle truth, enforcing capability entry controls, and exposing a unified governance health assessment surface.

## Scope Boundary

### Included
- Cursor integrity repair
- Lifecycle state population
- Capability loading enforcement
- Governance health aggregation

### Excluded
- GCE-006 implementation
- Disposition Pipeline
- FlightPlan velocity
- Calibration loop
- Semantic search
- New capability onboarding

## Execution Order

```
WP-001 Cursor Integrity Repair
        |
        v
WP-002 Lifecycle State Population
        |
        v
WP-003 Capability Loading Gate
        |
        v
WP-004 Governance Health Endpoint
```

## Evidence Required Per Work Packet
- Implementation evidence
- Test evidence
- Before/after state snapshot
- Acceptance gate results
- Receipt artifact

## Completion Definition

Governance Integrity Recovery is complete when:
- [ ] Current truth pointer is correct
- [ ] Governance entities have lifecycle truth
- [ ] Unqualified capabilities cannot enter execution
- [ ] Governance state is observable through one endpoint

---

## WP-001 — Cursor Integrity Repair

### Purpose
Restore canonical project position and transition resolution.

### Problem Statement
Current failures:
1. Librarian cursor references incorrect project identity (`librarian-workbench` instead of `librarian`)
2. QA-Pilot cursor exists but `get_allowed_transitions` cannot locate it
3. Governance decisions may execute against incorrect context

### Work
1. Reconcile cursor project identifiers
2. Validate ledger references
3. Repair sprint position references
4. Confirm transition resolver lookup paths

### Acceptance Gates

**G1 — Identity Alignment**
- `cursor.project_id == canonical project.id` for: `librarian`, `qa-pilot`

**G2 — Transition Resolution**
- `get_allowed_transitions(cursor)` returns valid transitions
- No lookup failures, adapter errors, or empty invalid state

**G3 — Ledger Position**
- Cursor position matches latest sealed sprint and canonical ledger marker

### Stop Conditions
Stop immediately if:
- Cursor repair requires modifying sealed receipts
- Canonical ledger history must be rewritten
- Project identity ambiguity remains

### Evidence
- [ ] Before snapshot: cursor state for librarian and qa-pilot
- [ ] After snapshot: cursor state after repair
- [ ] Transition resolution test results
- [ ] Ledger position verification

---

## WP-002 — Lifecycle State Population

### Purpose
Restore governance visibility.

### Problem Statement
Eight governance entities have `lifecycle_phase = NULL`. This prevents lifecycle-based reasoning — the system cannot answer "is it active?", "is it reviewable?", "is it complete?", "is it blocked?"

### Lifecycle Enum

```
PROPOSED
REGISTERED
QUALIFIED
ACTIVE
SUSPENDED
DEPRECATED
RETIRED
```

### Work
1. Define canonical lifecycle enum
2. Map existing entities to appropriate lifecycle states
3. Migrate records
4. Enforce enum validation on future writes

### Acceptance Gates

**G1 — Completeness**
- `COUNT(lifecycle_phase IS NULL) = 0`

**G2 — Validity**
- Every value exists in approved lifecycle enum

**G3 — Persistence**
- Restart system
- Verify lifecycle state survives

### Stop Conditions
Stop if:
- Entity cannot be classified without invention
- Migration requires guessing authority state

Those cases route to Owner Decision Queue.

### Evidence
- [ ] Before snapshot: entity lifecycle states
- [ ] Mapping decisions for each entity
- [ ] After snapshot: populated lifecycle states
- [ ] Enum validation test results
- [ ] Persistence test after restart

---

## WP-003 — Capability Loading Gate

### Purpose
Prevent unreviewed capability execution.

### Problem Statement
Current flow:
```
Capability Registry → Load
```

Missing qualification boundary. 18 unreviewed capabilities are freely loadable.

### Required Flow
```
Capability Request
        |
        v
Capability Gate
        |
        +---- Approved → Load
        |
        +---- Unreviewed → Block
        |
        +---- Unknown → Reject
```

### Work
1. Implement capability gate check before loading
2. Block capabilities with status != `qualified` or `reviewed`
3. Produce allow/deny evidence for every decision

### Acceptance Gates

**G1 — Unreviewed Block**
- Given: `capability.status = unreviewed`
- Expected: `LOAD = DENIED`

**G2 — Approved Path**
- Given: `capability.status = qualified`
- Expected: `LOAD = ALLOWED`

**G3 — Evidence**
- Every allow/deny decision produces:
  - capability identity
  - decision
  - reason
  - timestamp
  - authority context

### Stop Conditions
Stop if:
- Gate requires bypass exceptions without owner authority model
- Existing agents depend on silent loading behavior

### Evidence
- [ ] Gate implementation code
- [ ] Test: unreviewed capability blocked
- [ ] Test: qualified capability allowed
- [ ] Test: unknown capability rejected
- [ ] Evidence record for each test decision

---

## WP-004 — Governance Health Endpoint

### Purpose
Provide single-call governance assessment.

### Problem Statement
Current health assessment requires 8+ independent queries. Creates friction, inconsistent interpretation, and operator overhead.

### Proposed Surface

```json
{
  "cursor": { "status": "healthy|degraded|blocked", "details": {} },
  "lifecycle": { "status": "healthy|degraded|blocked", "details": {} },
  "capabilities": { "status": "healthy|degraded|blocked", "details": {} },
  "knowledge": { "status": "healthy|degraded|blocked", "details": {} },
  "extensions": { "status": "healthy|degraded|blocked", "details": {} },
  "authority": { "status": "healthy|degraded|blocked", "details": {} }
}
```

### Work
1. Aggregate cursor health, lifecycle completeness, capability enforcement state, extension registration status, knowledge substrate status, authority posture into one call
2. Distinguish healthy / degraded / blocked / unknown
3. No silent failure

### Acceptance Gates

**G1 — Single Invocation**
- One request returns complete governance state

**G2 — Component Coverage**
- Must include: cursor health, lifecycle completeness, capability enforcement state, extension registration status, knowledge substrate status

**G3 — Degraded Visibility**
- Endpoint must distinguish: healthy, degraded, blocked, unknown
- No silent failure

### Stop Conditions
Stop if:
- Aggregation requires runtime introspection not available through MCP
- Health check itself introduces performance regression

### Evidence
- [ ] Health endpoint implementation
- [ ] Test: returns full governance state
- [ ] Test: correctly reports degraded components
- [ ] Response time benchmark (< 100ms)
