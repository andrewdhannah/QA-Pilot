# Human Assurance — Operating Mode Declaration

**Purpose:** Freeze the Human Assurance Profile (#189) as a governed capability. Define its boundaries, ownership, retention rules, and relationship to QA Pilot and the Knowledge System.

**Status:** EFFECTIVE  
**Preceding:** #189 Implementation (✅ sealed, 10 exercises across 5 roles)  
**Architecture invariant:** Human Assessment ≠ Operational Authorization

---

## 1. Capability Status

| Property | Value |
|----------|-------|
| Capability | Human Assurance Profile (#189) |
| Status | **SEALED** |
| Roles | 5 (manager, architect, engineer, auditor, new owner) |
| Exercises | 10 |
| Classification taxonomy | PASS / OBSERVATION / OWNER_DECISION_REQUIRED / ERROR |
| Authority level | Advisory |
| Evidence location | `data/human-assurance/` (separate from system assurance) |
| Consumed by | Operator Capability View (not Release Readiness) |

---

## 2. What #189 Owns

| Domain | Owns | Does Not Own |
|--------|------|-------------|
| Operator understanding | ✅ Evaluates comprehension of governed systems | ❌ Operational authorization |
| Assessment evidence | ✅ Records exercise results with provenance | ❌ System certification |
| Learning paths | ✅ Generates from graph traversal | ❌ Personnel decisions |
| Knowledge gaps | ✅ Identifies areas needing reinforcement | ❌ Performance reviews |
| Role-based curricula | ✅ Defines per-role exercise sets | ❌ Access control |

---

## 3. What #189 Does Not Own

| Activity | Not Owned By #189 | Owned By |
|----------|------------------|----------|
| Granting permissions | ❌ | Owner / Governance process |
| Authorizing changes | ❌ | Owner |
| Certifying system readiness | ❌ | System assurance profiles + Owner |
| Blocking releases | ❌ | Owner |
| Personnel decisions | ❌ | Owner / Management |
| Access control | ❌ | Governance process |
| Modifying knowledge graph | ❌ | Graph maintainer (governance process) |

---

## 4. Assurance Separation (Frozen)

### Architecture

```
System Assurance (#186–#188)        Human Assurance (#189)
         ↓                                   ↓
data/ (system evidence)              data/human-assurance/
         ↓                                   ↓
Release Readiness Profile            Operator Capability View
         ↓                                   ↓
Owner Release Decision               Owner / Governance Decisions
```

### Rules

| Rule | Enforcement |
|------|-------------|
| Human assurance evidence stored in `data/human-assurance/` | Separate directory — never mixed with system evidence |
| Release Readiness does not consume human data | Structural separation — no cross-directory ingestion |
| System release not blocked by human assessment failure | No integration between human evidence and release process |
| System certification not granted by human assessment pass | No integration between human evidence and certification process |

---

## 5. Retention and Visibility Rules

| Property | Rule |
|----------|------|
| What is stored | Role, exercise responses, assessment classification, evidence_refs |
| PII stored | None — role-based identification only. No names, emails, or identifiers |
| Retention period | Same as evidence policy (append-only, indefinite) |
| Who can view individual results | Subject + Owner |
| Who can view aggregated results (by role) | Governance view |
| Modification | Append-only — assessment evidence cannot be modified or deleted |

---

## 6. Relationship to QA Pilot

| Aspect | Relationship |
|--------|-------------|
| Architecture basis | #185 Assurance Profile Architecture |
| Classification taxonomy | Same as #186–#188 (PASS/OBSERVATION/ODR/ERROR) |
| Output format | Same `assurance_report` contract |
| Operating mode | Follows same lifecycle as system assurance profiles |
| **Key difference** | Evaluates human operators, not system components |
| **Key separation** | Evidence stored separately from system assurance |

---

## 7. Relationship to Knowledge System

| Aspect | Relationship |
|--------|-------------|
| Exercise generation | Consumes knowledge graph for learning paths |
| Evidence artifacts | References governed artifacts as assessment material |
| Query layer | Operators use query layer to find evidence during exercises |
| **Boundary** | Assessment results do not modify the knowledge graph |

---

## 8. Future Extension Rules

### Permitted Without Governance Process

- Add new exercises to existing role profiles
- Add new roles following the existing pattern
- Update exercise questions to reflect architecture changes
- Improve evaluation logic
- Add additional evidence references

### Requires Full Governance Process

- Changing the classification taxonomy
- Adding permission-granting capability
- Integrating human assurance with system release process
- Changing retention or visibility rules
- Adding PII collection
- Modifying the authority_level field

---

## 9. Platform Assurance State

| # | Capability | Function | Status |
|---|-----------|----------|--------|
| #185 | Profile Architecture | Framework definition | ✅ Sealed |
| #186 | Privacy Assurance | System privacy posture | ✅ Sealed |
| #187 | Dependency Risk | Supply chain analysis | ✅ Sealed |
| #188 | Security Assurance | System security posture | ✅ Sealed |
| **#189** | **Human Assurance** | **Operator understanding** | **✅ Sealed** |
| — | Release Readiness | Cross-capability aggregation | ✅ Operational |

### The Assurance Stack

```
Artifact
   ↓
Evidence
   ↓
Assessment
   ↓
Classification
   ↓
Owner Visibility
```

Applied to two domains:
- **System State** (system assurance)
- **Human Understanding** (human assurance)

---

## 10. Platform Maturity

```
Construction Mode
    ↓ Evidence creation, capability building
Governance Mode
    ↓ Operating modes, authority boundaries, invariants
Certification Mode
    ↓ Test programs, invariant regression, validation
Knowledge Mode
    ↓ Graph, queries, organizational memory
Assurance Mode
    ↓ System + Human assurance, symmetrical evidence discipline
Stable Platform Operation
    ↓ Routine use, periodic reporting, selective evolution
```

The assurance stack is complete. System assurance evaluates components. Human assurance evaluates operator understanding. Neither replaces Owner judgment.

---

*Document: HUMAN-ASSURANCE-OPERATING-MODE.md*
*Status: EFFECTIVE | #189: Sealed*
*Core invariant: Human Assessment ≠ Operational Authorization*
*The capability evaluates understanding. It does not authorize action.*
*System assurance and human assurance are parallel planes — never merged.*
