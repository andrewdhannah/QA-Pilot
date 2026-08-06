# #189 Human Assurance Profile — Planning Definition

**Type:** assurance profile / human capability assessment  
**Status:** PLANNING ONLY — no implementation authorized  
**Architecture basis:** #185 Assurance Profile Architecture  
**Consumes:** Knowledge graph, operating modes, evidence artifacts, query layer  
**Next gate:** Impact Analysis → Invariant Review → Owner Authorization → Implementation

---

## 1. Purpose

Evaluate whether an operator can understand and safely navigate a governed system.

### It Answers

> "Has this person demonstrated understanding of the system boundaries, evidence model, and operating procedures?"

### It Does Not Answer

> "Is this person authorized to make decisions?"

Authority remains external:

```
Human Assurance
        ↓
Demonstrated Understanding
        ↓
Owner / Governance Authority
        ↓
Authorization Decision
```

---

## 2. Core Invariants

| Invariant | Statement |
|-----------|----------|
| HA-001 | Human assurance does not grant authority |
| HA-002 | Assessment results require evidence |
| HA-003 | Training completion does not equal operational authorization |
| HA-004 | Knowledge graph remains navigation only |
| HA-005 | Model explanations require evidence paths |
| HA-006 | Assessment failures produce evidence, not remediation |

---

## 3. Inputs

### Knowledge Graph

Provides learning paths, dependency order, artifact importance, custody chains, and invariant relationships.

**Example learning path for Governance Bridge:**
```
Why it exists (Phase 0 Audit)
What it protects (authority boundary)
How it operates (translation layer)
How it fails (node unreachable)
How it is changed (governance process)
```

### Operating Modes

Provide the boundaries to evaluate:

- "Can the operator explain why the bridge cannot create authority?"
- "Can the operator identify when Owner review is required?"
- "Can the operator distinguish observation from failure?"

### Evidence Artifacts

Provide assessment source material:
- Architecture documents
- Certification reports
- Invariant reviews
- Operating declarations
- Recovery guides

### Query Layer

Provides the tool the operator uses to find answers:
- Custody queries (why does this exist?)
- Impact queries (what changes if this changes?)
- Reporting queries (summarize this capability)

---

## 4. Assessment Model

Uses the same QA Pilot pattern:

```
Exercise
    ↓
Response
    ↓
Evaluation
    ↓
Evidence Record
    ↓
Classification
```

### Classification

| Result | Meaning |
|--------|---------|
| PASS | Understanding demonstrated |
| OBSERVATION | Knowledge gap identified |
| OWNER_DECISION_REQUIRED | Requires human judgment |
| ERROR | Assessment evidence unavailable |

**No new taxonomy.** Reuses existing PASS / OBSERVATION / OWNER_DECISION_REQUIRED / ERROR.

---

## 5. Role Profiles

### Manager Assurance

**Evaluates:**
- Can answer: What has been delivered? What is complete? What risks remain?
- Can interpret: Reporting queries, capability inventory, deferred items

**Sample exercise:**
"Generate a status summary for the Windows Runtime Node. Identify its certification state and remaining deferred items."

### Architect Assurance

**Evaluates:**
- Can answer: What changes affect invariants? What boundaries exist? What requires review?
- Can interpret: Impact queries, constraint propagation, change sequences

**Sample exercise:**
"What is affected if AUTH-003 changes? Identify affected systems, protected invariants, and required gates."

### Engineer Assurance

**Evaluates:**
- Can answer: Why does this component exist? Where is its evidence? What contracts does it depend on?
- Can interpret: Custody queries, evidence chains, artifact paths

**Sample exercise:**
"Trace the certification chain for the Governance Bridge. List the evidence artifacts for each step."

### Auditor Assurance

**Evaluates:**
- Can answer: Where is proof? Is evidence complete? Is provenance intact?
- Can interpret: Provenance verification, evidence_refs validation, operating mode compliance

**Sample exercise:**
"Verify the evidence chain for the Runtime Node certification. Identify any degraded provenance steps."

### New Owner Assurance

**Evaluates:**
- Can answer: How do I safely continue? What is frozen? What can change?
- Can interpret: All operating modes, frozen boundaries, governance process

**Sample exercise:**
"A new team member asks whether they can modify the evidence contract. What is the correct governance response?"

---

## 6. Output Contract

```json
{
  "assurance_report": {
    "profile": "human-assurance",
    "profile_name": "Human Assurance Profile",
    "version": "1.0.0",
    "subject": "operator-identifier",
    "role": "technical-lead | manager | architect | engineer | auditor | new-owner",
    "generated_at": "ISO8601",
    "overall": "PASS | OBSERVATION | OWNER_DECISION_REQUIRED",

    "consumes": ["knowledge-graph", "query-layer", "operating-modes"],

    "assessments": [
      {
        "exercise_id": "EX-001",
        "exercise": "trace-runtime-certification",
        "classification": "PASS",
        "finding": "Operator correctly traced certification chain and identified all evidence artifacts.",
        "evidence_refs": ["docs/reports/SPRINT7-FINAL-CERTIFICATION-REPORT.md"]
      }
    ],

    "knowledge_gaps": [],

    "summary": {
      "total_exercises": 5,
      "pass": 4,
      "observation": 1,
      "owner_decision_required": 0,
      "overall": "OBSERVATION"
    },

    "authority_level": "advisory",
    "consumable_by": "governance_view"
  }
}
```

### Critical Field

```json
"authority_level": "advisory"
```

Must remain mandatory. The profile certifies demonstrated understanding — not operational authorization.

---

## 7. Acceptance Gates

| Gate | Requirement |
|------|-------------|
| HA-PLAN-1 | Role profiles defined (manager, architect, engineer, auditor, new owner) |
| HA-PLAN-2 | Assessment model follows existing QA Pilot taxonomy |
| HA-PLAN-3 | Output contract defined with authority_level: advisory |
| HA-PLAN-4 | Invariants documented (HA-001 through HA-006) |
| HA-PLAN-5 | Consumes knowledge graph, not document search |
| HA-PLAN-6 | No permission-granting capability |
| HA-PLAN-7 | Evidence required per assessment (HA-002) |

---

## 8. Success Criteria

The capability succeeds if a new operator can:

1. Navigate the system without tribal knowledge
2. Explain major architectural boundaries
3. Find evidence supporting claims
4. Identify when Owner decisions are required
5. Avoid violating frozen operating modes

### Validation Scenario

Give a new technical lead only the repository and knowledge system. Measure whether they can reach safe operating understanding without direct transfer from the original builder.

This is the organizational continuity test.

---

## 9. Non-Goals

- Granting permissions
- Authorizing changes
- Replacing Owner decisions
- Generating credentials
- Tracking HR training completion
- Automated role promotion
- Access control decisions

---

## 10. Current Assurance Framework State

| # | Capability | Status |
|---|-----------|--------|
| #185 | Assurance Profile Architecture | ✅ Sealed |
| #186 | Privacy Assurance Profile | ✅ Sealed |
| #187 | Dependency Risk Capability | ✅ Sealed |
| #188 | Security Assurance Profile | ✅ Sealed |
| **#189** | **Human Assurance Profile** | **⏳ Planning defined — awaiting authorization** |

---

## 11. Next Transition

**Owner authorization** to proceed with #189 — Human Assurance Profile implementation.

Sequence: Planning → Impact Analysis → Invariant Review → Authorization → Implementation → Certification → Operating Mode

---

*Document: QA-PILOT-189-HUMAN-ASSURANCE-PROFILE-PLAN.md*
*Status: Planning Only | No implementation authorized*
*Core invariant: Human assurance does not grant authority. Assessment results require evidence.*
*The capability evaluates understanding. It does not authorize action.*
