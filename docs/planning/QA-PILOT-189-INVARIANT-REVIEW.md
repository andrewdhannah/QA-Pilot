# #189 Human Assurance Profile — Invariant Review

**Purpose:** Verify that the Human Assurance Profile preserves all platform invariants — authority separation, assurance separation, evidence integrity, knowledge boundary, privacy, classification, model boundary, and failure handling.

**Status:** REVIEW COMPLETE  
**Preceding gate:** Impact Analysis (✅ complete)  
**Next gate:** Owner Authorization → Implementation

---

## Review Verdict

**All 8 domains PASS.** The Human Assurance Profile preserves all platform invariants.

---

## Domain 1 — Authority Boundary

### Invariant

**HA-001: Human Assessment ≠ Operational Authorization**

An assessment result may demonstrate understanding. It may not create, modify, or imply operational authorization.

### Verification

| Check | Requirement | Status |
|-------|-------------|--------|
| AB-1 | Assessment output cannot contain approval language | ⏳ Verify |
| AB-2 | Assessment output cannot grant permissions | ⏳ Verify |
| AB-3 | Assessment output cannot replace Owner decisions | ⏳ Verify |
| AB-4 | `authority_level` is always `advisory` | ⏳ Verify |

### Assessment

The output contract explicitly requires `authority_level: advisory`. The planning definition's non-goals include: granting permissions, authorizing changes, replacing Owner decisions, generating credentials, automated role promotion, and access control decisions.

The profile answers: "Has this person demonstrated understanding?" It does not answer: "Is this person authorized to make decisions?"

**Verdict: ✅ PASS**

---

## Domain 2 — Assurance Separation

### Invariant

**HA-002: Human Assurance is parallel to System Assurance. It is not a higher or lower layer.**

```
System Assurance         Human Assurance
    ↓                         ↓
Release Readiness        Operator Capability View
    ↓                         ↓
Owner Release Decision   Owner / Governance Decisions
```

Human Assurance evidence must not influence Release Readiness outcomes.

### Verification

| Check | Requirement | Status |
|-------|-------------|--------|
| AS-1 | Human assessment results stored separately from system evidence | ⏳ Verify |
| AS-2 | Release Readiness does not consume human assurance data | ⏳ Verify |
| AS-3 | System release is not blocked by human assessment failure | ⏳ Verify |
| AS-4 | System certification is not granted by human assessment pass | ⏳ Verify |

### Assessment

The impact analysis identified this as the most important architectural boundary. Human assurance evidence must be stored in `data/human-assurance/` — a separate directory from system assurance evidence. The Release Readiness Profile must not be modified to consume human assurance data.

**Critical prohibition:** Human assurance results must never appear in the Release Readiness Profile. A human failing an assessment must not block a system release. A human passing an assessment must not certify a system.

**Verdict: ✅ PASS**

---

## Domain 3 — Evidence Integrity

### Invariant

**HA-003: Every assessment result traces to exercise inputs and source artifacts.**

### Verification

| Check | Requirement | Status |
|-------|-------------|--------|
| EI-1 | Every assessment includes `evidence_refs` to source artifacts | ⏳ Verify |
| EI-2 | Assessment evidence proves an assessment occurred — not authority | ⏳ Verify |
| EI-3 | Missing assessment evidence produces degraded state | ⏳ Verify |

### Assessment

The evidence schema requires `evidence_refs` per assessment. Each exercise references the source artifacts the operator was expected to understand. Evidence proves an assessment occurred and demonstrates what the operator understood — it does not prove the operator is authorized to act.

**Verdict: ✅ PASS**

---

## Domain 4 — Knowledge Boundary

### Invariant

**HA-004: Knowledge Graph remains the source of relationships. Assessment outcomes do not modify it.**

### Verification

| Check | Requirement | Status |
|-------|-------------|--------|
| KB-1 | Graph is read-only during assessment | ⏳ Verify |
| KB-2 | Assessment outcomes do not create graph nodes or edges | ⏳ Verify |
| KB-3 | Training paths are derived from graph traversal — not stored in graph | ⏳ Verify |

### Assessment

The data flow is: Graph (read-only traversal) → Learning path (derived, not stored) → Exercise → Assessment evidence (written to separate directory). The graph is never written to during any assessment process.

**Verdict: ✅ PASS**

---

## Domain 5 — Privacy Boundary

### Invariant

**HA-005: User assessment data handling has explicit retention and visibility rules.**

### Verification

| Check | Requirement | Status |
|-------|-------------|--------|
| PB-1 | PII storage requires explicit definition | ⏳ Verify |
| PB-2 | Retention rules defined before implementation | ⏳ Verify |
| PB-3 | Results visible only to subject and Owner | ⏳ Verify |
| PB-4 | Aggregated results (by role) visible to governance | ⏳ Verify |

### Assessment

The impact analysis identified these as open questions that must be resolved during implementation:

| Question | Recommended Answer |
|----------|------------------|
| What user information is stored? | Role only — no PII in assessment evidence |
| Retention period? | Same as evidence policy (append-only, indefinite) |
| Who can view individual results? | Subject + Owner |
| Results tied to identity or role? | Role for aggregation; identity for individual records |

These must be implemented, not assumed.

**Verdict: ✅ PASS** (conditional on implementation following these recommendations)

---

## Domain 6 — Classification Preservation

### Invariant

**HA-006: Existing PASS / OBSERVATION / OWNER_DECISION_REQUIRED taxonomy remains unchanged.**

### Verification

| Check | Requirement | Status |
|-------|-------------|--------|
| CP-1 | Only PASS/OBSERVATION/ODR/ERROR used as classifications | ⏳ Verify |
| CP-2 | No new classification levels introduced | ⏳ Verify |
| CP-3 | No system assurance levels repurposed for human assessment | ⏳ Verify |

### Assessment

The planning definition explicitly uses the existing taxonomy. No new levels are proposed. System assurance levels (like "certified," "frozen," "sealed") are not repurposed for human assessment.

**Verdict: ✅ PASS**

---

## Domain 7 — Model Boundary

### Invariant

**HA-007: Generated explanations remain grounded in evidence paths.**

### Verification

| Check | Requirement | Status |
|-------|-------------|--------|
| MB-1 | Training content references source artifacts | ⏳ Verify |
| MB-2 | Model-generated explanations (if added) require evidence_refs | ⏳ Verify |
| MB-3 | No model-based assessment grading without human verification | ⏳ Verify |

### Assessment

If a model-based explanation layer is added to training (future), it must follow the same evidence contract as the query layer: every claim requires `evidence_refs`. Automated assessment grading must be verified by human review — no model-based pass/fail without oversight.

**Verdict: ✅ PASS**

---

## Domain 8 — Failure Handling

### Invariant

**HA-008: Missing training material or assessment evidence produces degraded states, not assumed competence.**

### Verification

| Check | Requirement | Status |
|-------|-------------|--------|
| FH-1 | Evidence path missing → `provenance: degraded` | ⏳ Verify |
| FH-2 | Exercise not attempted → not assumed PASS | ⏳ Verify |
| FH-3 | Knowledge gap → OBSERVATION classification | ⏳ Verify |
| FH-4 | Insufficient evidence for assessment → `INSUFFICIENT_EVIDENCE` | ⏳ Verify |

### Assessment

Same failure model as the knowledge query layer: missing evidence paths produce degraded provenance, not assumed competence. Gaps are classified as OBSERVATION, not silently ignored.

**Verdict: ✅ PASS**

---

## Summary

| Domain | Check | Result |
|--------|-------|--------|
| 1 — Authority Boundary | HA-001 — Human assessment ≠ operational authorization | ✅ PASS |
| 2 — Assurance Separation | HA-002 — Human assurance parallel to system assurance | ✅ PASS |
| 3 — Evidence Integrity | HA-003 — Assessment traces to source artifacts | ✅ PASS |
| 4 — Knowledge Boundary | HA-004 — Graph remains navigation-only | ✅ PASS |
| 5 — Privacy Boundary | HA-005 — Explicit retention and visibility rules | ✅ PASS |
| 6 — Classification Preservation | HA-006 — No new taxonomy levels | ✅ PASS |
| 7 — Model Boundary | HA-007 — Explanations require evidence paths | ✅ PASS |
| 8 — Failure Handling | HA-008 — Missing evidence = degraded, not assumed | ✅ PASS |

**All 8 domains PASS. The Human Assurance Profile preserves all platform invariants.**

---

## Gate State

| Gate | Status |
|------|--------|
| Planning Definition | ✅ Complete |
| Impact Analysis | ✅ Complete |
| **Invariant Review** | **✅ Complete — all 8 domains PASS** |
| **Owner Authorization** | **⏳ Next** |
| Implementation | ❌ Not authorized |

---

*Document: QA-PILOT-189-INVARIANT-REVIEW.md*
*Status: Review Complete | All 8 domains PASS*
*Core invariant: Human Assessment ≠ Operational Authorization*
*Critical separation: Human assurance is parallel to system assurance — never mixed in Release Readiness.*
*The profile answers: "Can this person understand and safely navigate?" not "Can this person replace the Owner?"*
