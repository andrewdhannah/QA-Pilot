# Assurance Remediation Contract

**Extracted from:** EPIC-ASSURANCE-OPERATIONS-ADOPTION-1 (#207–#210)
**Sprint:** #215 — ASSURANCE-CONTRACT-EVIDENCE-STATE-CONTRACT-FORMALIZATION-1
**Status:** DRAFT — 🔍 Pending Owner review

---

## 1. Purpose

Define the lifecycle of an assurance finding from detection through remediation verification. The remediation contract ensures that every response to a finding preserves the evidence chain and maintains the QA Pilot ≠ Authority invariant.

## 2. Remediation Lifecycle

```
Finding
  |
  v
Proposal (advisory) ────┐
  |                      |
  v                      |
Owner Decision           |
  |                      |
  +---- Authorized ------+--- Execution (Librarian)
  |                      |
  +---- Deferred --------+--- Parked with reason
  |                      |
  +---- Rejected --------+--- Closed with rationale
  |                      |
  v                      v
Verification          Evidence
  |                    Archive
  v
Regression Guard
```

### 2.1 Lifecycle States

| State | Description | Owner Action Required? |
|-------|-------------|----------------------|
| `detected` | Finding identified, proposal generated | No |
| `proposed` | Recommendation submitted for Owner review | Yes |
| `authorized` | Owner approved remediation | Yes |
| `deferred` | Owner deferred remediation | Yes |
| `rejected` | Owner declined remediation | Yes |
| `in_progress` | Remediation being executed (Librarian side) | No (monitoring) |
| `verified` | Remediation verified by assurance engine | No |
| `regression_guard` | Permanent regression guard installed | No |
| `closed` | Lifecycle complete | No |

## 3. Remediation Object

```
AssuranceRemediation {
    remediation_id: string,
    finding_ref: string,              // Reference to originating finding
    evidence_refs: string[],          // Evidence supporting remediation
    proposal: {                       // Advisory recommendation
        description: string,
        approach: string,
        effort_estimate: string,
        risk_if_not_done: string
    },
    owner_decision: {                 // Populated after Owner acts
        decision: "authorized" | "deferred" | "rejected",
        rationale: string,
        decided_at: ISO8601,
        decided_by: "owner"
    },
    state: "detected" | "proposed" | "authorized" | "deferred" |
           "rejected" | "in_progress" | "verified" | "regression_guard" | "closed",
    verification: {
        verified_at: ISO8601?,
        verifier: string?,
        evidence_ref: string?,             // Link to verification evidence
        result: "pass" | "fail" | "partial"?
    },
    regression_guard_ref: string?     // Link to regression contract if installed
}
```

## 4. Remediation Rules

| Rule ID | Rule | Enforcement |
|---------|------|-------------|
| RM-1 | Every remediation MUST trace to exactly one finding | Schema validation |
| RM-2 | Every remediation MUST trace to at least one evidence item | Schema validation |
| RM-3 | A remediation proposal MUST be advisory-only (`owner_decision_required: true`) | Schema validation |
| RM-4 | No remediation MAY advance past `proposed` without an Owner decision | State machine rule |
| RM-5 | An Owner decision of `deferred` or `rejected` MUST include a rationale | Schema validation |
| RM-6 | Verification MUST produce evidence (cannot be self-verified by remediator) | Contract rule |
| RM-7 | A `regression_guard` state means the fix is encoded as a permanent assurance test | Contract rule |
| RM-8 | QA Pilot MAY propose, classify severity, and recommend. QA Pilot MUST NOT execute | Authority rule |

## 5. Evidence Provenance for Remediation

Every remediation decision must maintain the chain:

```
Original Evidence
    |
    v
Finding (derived from evidence + contract)
    |
    v
Proposal (derived from finding)
    |
    v
Owner Decision (recorded as evidence)
    |
    v
Execution (Librarian side — separate custody)
    |
    v
Verification Evidence (new evidence — feeds back into loop)
```

## 6. Prohibited Patterns

| Pattern | Risk | Rule |
|---------|------|------|
| Remediation starts without Owner decision | Authority bypass | RM-4 |
| Finding → Execution without Proposal | Skip advisory layer | RM-3 |
| QA Pilot self-verifies its own remediation | Circular verification | RM-6 |
| Remediation closes without regression guard | Lost institutional memory | RM-7 |
| Evidence chain truncated | Loss of provenance | RM-1, RM-2 |
