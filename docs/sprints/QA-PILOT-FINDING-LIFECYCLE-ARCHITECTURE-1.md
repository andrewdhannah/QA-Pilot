# QA-PILOT-FINDING-LIFECYCLE-ARCHITECTURE-1 — Finding Lifecycle Management Architecture

**Type:** assessment / architecture definition
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** assurance
**Boundary:** QA Pilot-local (evidence, classification, context) / Owner (decision, risk acceptance, resolution)
**Dependencies:** #198 (model-assisted), Operational Review

---

## Purpose

Introduce controlled lifecycle management for assurance findings without changing the advisory boundary. Closes the gap between evidence generation and resolution.

---

## Deliverables

### Phase 1 — Finding State Model

```
OPEN → ACKNOWLEDGED → ACTION_ASSIGNED → IN_PROGRESS → RESOLVED → VERIFIED
  └→ ACCEPTED_RISK └→ DEFERRED └→ NOT_APPLICABLE
```

### Phase 2 — Owner Acknowledgment Queue

```
Owner Action Queue:
  HIGH ATTENTION: items awaiting acknowledgment
  REVIEW: items assigned or monitoring
  MONITOR: informational only
```

### Phase 3 — Resolution Evidence Binding

```
Change → Evidence → Finding → Risk → Owner Action → Resolution Evidence → Final State
```

### Phase 4 — Escalation Model

| Trigger | Action |
|---------|--------|
| Aging threshold exceeded | Finding promoted to HIGH ATTENTION |
| Repeated same finding | Flag as recurring |
| Unresolved HIGH ATTENTION | Release readiness blocked (advisory) |
| New finding on previously resolved area | Re-open finding |

---

## Scope

### Included

- Finding lifecycle state model
- Owner acknowledgment queue design
- Resolution evidence binding
- Escalation model (advisory only)

### Non-Scope

- Automatic finding closure
- Automatic release blocking
- Owner decision automation
- Multi-project finding routing

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| FL-1 | Finding state model defined |
| FL-2 | Owner acknowledgment queue designed |
| FL-3 | Resolution evidence binding defined |
| FL-4 | Escalation model defined (advisory) |
| FL-5 | No automatic finding closure |
| FL-6 | Evidence produced |

---

**Status:** ✅ AUTHORIZED — Owner-authorized 2026-07-20
**Ledger entry:** #199 (authorized)
