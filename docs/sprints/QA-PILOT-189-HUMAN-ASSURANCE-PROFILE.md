# QA-PILOT-189-HUMAN-ASSURANCE-PROFILE — Human Assurance Profile

**Type:** assurance profile / human capability assessment  
**Status:** ✅ **SEALED — Implementation complete, all invariants preserved**  
**Lane:** assurance  
**Boundary:** QA Pilot-local, knowledge consumption layer  
**Consumes:** Knowledge graph, governance graph, operating mode declarations  
**Stored separately from:** System assurance evidence (Release Readiness)

---

## Purpose

Evaluate whether an operator can understand and safely navigate a governed system.

It answers: "Has this person demonstrated understanding of the system boundaries, evidence model, and operating procedures?"

It does not answer: "Is this person authorized to make decisions?"

---

## Implementation

**Script:** `scripts/qa_pilot_human_assurance_profile.py`

### Role Profiles

| Role | Exercises | Knowledge Areas |
|------|-----------|----------------|
| Manager | 2 | System status, capability inventory |
| Architect | 2 | Impact analysis, boundary understanding |
| Engineer | 2 | Custody tracing, evidence discovery |
| Auditor | 2 | Provenance verification, compliance check |
| New Owner | 2 | Governance understanding, decision boundary |

### Assessment Model

```
Exercise (generated from graph)
    ↓
Operator response
    ↓
Evaluation against key concepts
    ↓
Classification (PASS / OBSERVATION / ODR / ERROR)
    ↓
Evidence record with evidence_refs
```

---

## Invariant Compliance

| Invariant | Status | Verification |
|-----------|--------|-------------|
| HA-001 — Assessment ≠ Authorization | ✅ Preserved | `authority_level: advisory` — no authority language |
| HA-002 — Parallel to system assurance | ✅ Preserved | Evidence in `data/human-assurance/` — not in Release Readiness |
| HA-003 — Evidence traces to source | ✅ Preserved | Every exercise has evidence_refs |
| HA-004 — Graph navigation-only | ✅ Preserved | Graph is read-only during assessment |
| HA-005 — Retention and visibility | ✅ Preserved | Role-based, no PII in assessment evidence |
| HA-006 — No new taxonomy | ✅ Preserved | Uses PASS/OBSERVATION/ODR/ERROR |
| HA-007 — Explanations require evidence | ✅ Preserved | Training references source artifacts |
| HA-008 — Missing evidence = degraded | ✅ Preserved | Unresolvable evidence produces ERROR |

### Assurance Separation Verified

| Check | Result |
|-------|--------|
| Human evidence in separate directory | ✅ `data/human-assurance/` |
| Release Readiness does not consume human data | ✅ Confirmed — no contamination |
| Consumable by operator-capability-view | ✅ Not by Release Readiness |

---

## Results

| Metric | Value |
|--------|-------|
| Roles defined | 5 |
| Total exercises | 10 |
| Learning paths | 5 (one per role) |
| Evidence stored in | `data/human-assurance/` (separate from system assurance) |
| Core invariant | ✅ Preserved |

---

## Assurance Framework State

| # | Capability | Status |
|---|-----------|--------|
| #185 | Assurance Profile Architecture | ✅ Sealed |
| #186 | Privacy Assurance Profile | ✅ Sealed |
| #187 | Dependency Risk Capability | ✅ Sealed |
| #188 | Security Assurance Profile | ✅ Sealed |
| **#189** | **Human Assurance Profile** | **✅ Sealed** |

---

*Sprint: QA-PILOT-189-HUMAN-ASSURANCE-PROFILE | Status: Sealed*
*Core invariant: Human Assessment ≠ Operational Authorization*
*The capability evaluates understanding. It does not authorize action.*
*Human assurance is parallel to system assurance — never mixed in Release Readiness.*
