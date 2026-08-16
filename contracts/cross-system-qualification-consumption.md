# Cross-System Qualification Consumption Contract

**Sprint:** Cross-System Contract Hardening (#236)
**Status:** ACTIVE — Owner-authorized 2026-08-16

---

## 1. Purpose

Define how downstream systems interpret qualification state.

## 2. Question

**How should downstream systems interpret qualification state?**

## 3. Critical Distinctions

### 3.1 QUALIFIED ≠ AUTHORIZED TO CHANGE

| Statement | Meaning | Implication |
|-----------|---------|-------------|
| `QUALIFIED` | Evidence meets qualification criteria | Artifact is acceptable as-is |
| `AUTHORIZED TO CHANGE` | Owner approved modification | Different concept entirely |

**Rule:** Qualification is informational. Authorization requires Owner decision.

### 3.2 DEGRADED ≠ DISABLED

| Statement | Meaning | Implication |
|-----------|---------|-------------|
| `DEGRADED` | Some criteria not met | Functionality reduced but operational |
| `DISABLED` | Capability not available | Cannot be used |

**Rule:** Degraded state indicates reduced assurance, not operational failure.

### 3.3 REVIEW_REQUIRED ≠ FAILED

| Statement | Meaning | Implication |
|-----------|---------|-------------|
| `REVIEW_REQUIRED` | Human judgment needed | Pending Owner review |
| `FAILED` | Criteria not met | Definitive negative result |

**Rule:** Review required is a procedural state, not a quality judgment.

## 4. Qualification State Semantics

### 4.1 Valid States

| State | Meaning | Downstream Action |
|-------|---------|-------------------|
| `QUALIFIED` | All criteria met | May proceed (within authority) |
| `CONDITIONALLY_QUALIFIED` | Criteria met with conditions | Proceed with conditions |
| `REVIEW_REQUIRED` | Human judgment needed | Await Owner decision |
| `NOT_QUALIFIED` | Criteria not met | Do not proceed |
| `UNTESTED` | No qualification performed | Qualify before proceeding |

### 4.2 State Transitions

```
UNTESTED → QUALIFIED (if criteria met)
UNTESTED → NOT_QUALIFIED (if criteria not met)
UNTESTED → REVIEW_REQUIRED (if human judgment needed)

QUALIFIED → REVIEW_REQUIRED (if evidence changes)
NOT_QUALIFIED → REVIEW_REQUIRED (if remediation applied)

REVIEW_REQUIRED → QUALIFIED (Owner approves)
REVIEW_REQUIRED → NOT_QUALIFIED (Owner rejects)
```

## 5. Interpretation Rules

| Rule | Requirement |
|------|-------------|
| No implicit authorization | Qualification never implies authority to change |
| State is point-in-time | Qualification valid at time of assessment |
| Evidence changes require requalification | New evidence invalidates prior qualification |
| Owner disposition required | Final decision requires Owner action |

## 6. Downstream System Obligations

| System | Obligation |
|--------|------------|
| LINK | Display qualification state; do not act on it |
| Agents | Await qualification before proposing actions |
| FlightPlan | Report evidence; do not interpret qualification |
| Librarian | Record qualification; do not modify based on it |

## 7. Non-Authority Boundary

Qualification consumption:

| May Do | May Not Do |
|--------|------------|
| Display qualification state | Auto-approve actions |
| Interpret state semantics | Modify qualification |
| Reference qualification | Create false qualification |
| Await Owner disposition | Bypass Owner review |
