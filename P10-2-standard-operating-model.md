# P10-2 — Standard Operating Model

**Generated:** 2026-08-17
**Project:** qa-pilot
**Phase:** P10-2 (Operating Model)
**Status:** COMPLETE

---

## 1. Standard Operating Lifecycle (P10-2-001)

### 1.1 Eight-Step Lifecycle

```
Observation
    ↓
Classification
    ↓
Decision Candidate
    ↓
Owner Review
    ↓
Disposition
    ↓
Execution (if authorized)
    ↓
Evidence
    ↓
Closure
```

### 1.2 Step Definitions

| Step | Action | Actor | Output |
|------|--------|-------|--------|
| 1. Observation | System detects anomaly or state | System | Finding |
| 2. Classification | Finding classified by type and severity | System | Classified finding |
| 3. Decision Candidate | Finding projected into decision queue | System | Decision candidate |
| 4. Owner Review | Owner reviews candidate with context | Owner | Informed decision |
| 5. Disposition | Owner decides action | Owner | Disposition recorded |
| 6. Execution | Work performed if authorized | Execution layer | Work completed |
| 7. Evidence | Resolution evidence produced | System | Resolution receipt |
| 8. Closure | Finding closed with evidence chain | System | Closure receipt |

### 1.3 Lifecycle Invariants

| Invariant | Enforcement |
|-----------|-------------|
| Owner decides at step 5 | Mandatory — no bypass |
| Evidence produced at steps 7-8 | Mandatory — no closure without evidence |
| Execution requires authorization | Mandatory — no auto-execution |
| Identity maintained throughout | Mandatory — no identity loss |

---

## 2. Roles and Responsibilities (P10-2-002)

### 2.1 System Role

| Responsibility | Boundary |
|----------------|----------|
| Observe | Read-only observation of state |
| Classify | Automated classification of findings |
| Recommend | Advisory suggestions, not decisions |
| Record | Record Owner decisions and evidence |
| Track | Maintain lifecycle state |

**System DOES NOT:**
- Decide
- Authorize
- Execute without permission
- Remediate automatically

### 2.2 Owner Role

| Responsibility | Boundary |
|----------------|----------|
| Review | Examine findings and candidates |
| Decide | Choose disposition |
| Authorize | Approve execution |
| Accept Risk | Acknowledge limitations |
| Close | Confirm resolution |

**Owner DOES NOT:**
- Execute directly (through governance)
- Bypass evidence requirements
- Skip disposition recording

### 2.3 Execution Role

| Responsibility | Boundary |
|----------------|----------|
| Perform | Execute authorized work |
| Report | Produce completion evidence |
| Escalate | Surface issues to governance |

**Execution DOES NOT:**
- Initiate governance actions
- Cross into authority boundary
- Skip evidence production

### 2.4 RACI Matrix

| Activity | System | Owner | Execution |
|----------|--------|-------|-----------|
| Observation | R/A | I | I |
| Classification | R/A | I | I |
| Decision Candidate | R/A | I | I |
| Owner Review | I | R/A | I |
| Disposition | C | R/A | I |
| Execution | I | A | R |
| Evidence | R/A | I | C |
| Closure | R/A | A | C |

R = Responsible, A = Accountable, C = Consulted, I = Informed

---

## 3. Entry and Exit Conditions (P10-2-003)

### 3.1 Entry Conditions

| Condition | Requirement |
|-----------|-------------|
| Observation occurred | System detected anomaly or state |
| Finding created | Evidence artifact produced |
| Classification complete | Finding type and severity assigned |
| Decision candidate projected | Finding in decision queue |

### 3.2 Exit Conditions

| Condition | Requirement |
|-----------|-------------|
| Owner disposition recorded | Decision made with rationale |
| Execution completed (if authorized) | Work performed |
| Resolution evidence produced | Evidence artifact created |
| Closure receipt recorded | Closure linked to origin |

### 3.3 Lifecycle Entry/Exit Rules

| Rule | Description |
|------|-------------|
| No entry without observation | Lifecycle starts with evidence |
| No exit without closure | Lifecycle ends with evidence |
| No skip steps | All steps must be traversed |
| No reverse without evidence | Reversal requires new evidence |

---

## 4. Escalation Boundaries (P10-2-004)

### 4.1 Escalation Triggers

| Trigger | Escalation Path |
|---------|-----------------|
| Finding severity critical | Immediate Owner review |
| Capability gap identified | Gap lifecycle (P9-3 pattern) |
| Authority boundary threatened | Stop and flag |
| Evidence chain broken | Stop and flag |

### 4.2 Escalation Rules

| Rule | Description |
|------|-------------|
| No auto-escalation | System flags, Owner decides |
| Escalation produces evidence | All escalations recorded |
| Escalation preserves authority | Owner remains decision authority |

### 4.3 Stop Conditions

| Condition | Action |
|-----------|--------|
| Authority breach detected | Halt, flag, await Owner |
| Evidence fabrication detected | Halt, flag, await Owner |
| Architecture violation detected | Halt, flag, await Owner |

---

## 5. Evidence Requirements (P10-2-005)

### 5.1 Required Evidence at Each Step

| Step | Required Evidence |
|------|-------------------|
| Observation | Finding artifact |
| Classification | Classification metadata |
| Decision Candidate | Queue entry with provenance |
| Owner Review | Review timestamp |
| Disposition | Decision record with rationale |
| Execution | Authorization record |
| Evidence | Resolution receipt |
| Closure | Closure receipt linked to origin |

### 5.2 Evidence Retention Rules

| Rule | Description |
|------|-------------|
| Retain all evidence | No evidence deletion |
| Link to origin | Every evidence links to finding |
| Maintain identity | Finding identity preserved |
| Support replay | Evidence supports deterministic replay |

### 5.3 Evidence Quality Criteria

| Criterion | Requirement |
|-----------|-------------|
| Completeness | All steps have evidence |
| Accuracy | Evidence matches reality |
| Timeliness | Evidence produced at step time |
| Provenance | Evidence links to origin |

---

## 6. Project-Specific Variation Boundaries (P10-2-006)

### 6.1 What Can Vary

| Dimension | Variation Allowed |
|-----------|-------------------|
| Finding types | Project-specific finding types |
| Classification rules | Project-specific severity rules |
| Disposition options | Project-specific dispositions |
| Execution tools | Project-specific execution |
| Evidence formats | Project-specific formats |

### 6.2 What Cannot Vary

| Dimension | Variation Prohibited |
|-----------|----------------------|
| Owner authority | Must remain exclusive |
| Evidence requirements | Must produce evidence |
| Lifecycle steps | Must traverse all steps |
| Identity preservation | Must maintain identity |
| Closure requirements | Must link to origin |

### 6.3 Variation Boundary Rules

| Rule | Description |
|------|-------------|
| Variations documented | All variations must be documented |
| Variations tested | Variations must be validated |
| Variations preserve invariants | Variations cannot violate invariants |

---

## 7. No Authority Expansion (P10-2-007)

### 7.1 Authority Invariants

| Invariant | Status |
|-----------|--------|
| Owner remains sole disposition authority | ✅ PRESERVED |
| System remains advisory | ✅ PRESERVED |
| No automatic decisions | ✅ PRESERVED |
| No authority crossing | ✅ PRESERVED |

### 7.2 Operating Model Constraints

| Constraint | Enforcement |
|------------|-------------|
| No automatic remediation | System proposes, Owner decides |
| No autonomous approval | Owner approves all actions |
| No mandatory workflow enforcement | Workflows are guidance, not enforcement |
| No replacement of project processes | Governance augments, not replaces |

---

## 8. Acceptance Gate Verification

### 8.1 Gate Summary

| Gate | Result | Evidence |
|------|--------|----------|
| P10-2-001 | ✅ PASS | Standard operating lifecycle defined |
| P10-2-002 | ✅ PASS | Roles and responsibilities documented |
| P10-2-003 | ✅ PASS | Entry and exit conditions defined |
| P10-2-004 | ✅ PASS | Escalation boundaries defined |
| P10-2-005 | ✅ PASS | Evidence requirements defined |
| P10-2-006 | ✅ PASS | Project-specific variation boundaries documented |
| P10-2-007 | ✅ PASS | No authority expansion introduced |

---

## 9. P10-2 Conclusion

### 9.1 Operating Model Defined

**Eight-step lifecycle** with clear roles, responsibilities, and evidence requirements.

**Four roles:** System, Owner, Execution, Governance

**Entry/exit conditions** documented for each step.

**Escalation boundaries** defined with stop conditions.

**Evidence requirements** specified for each step.

**Project variations** allowed within invariant boundaries.

### 9.2 Key Operating Principles

1. **Owner decides** — System proposes, Owner decides
2. **Evidence required** — No closure without evidence
3. **Identity preserved** — Finding identity maintained throughout
4. **No auto-execution** — Execution requires authorization
5. **Variations allowed** — Within invariant boundaries

### 9.3 Operating Model Summary

```
┌─────────────────────────────────────────────────────────────┐
│                  Standard Operating Model                    │
│                                                              │
│  Observation → Classification → Decision Candidate → Review  │
│       ↓                                                      │
│  Disposition → Execution → Evidence → Closure                │
│                                                              │
│  System: Observe, Classify, Recommend, Record, Track         │
│  Owner: Review, Decide, Authorize, Accept Risk, Close        │
│  Execution: Perform, Report, Escalate                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

*P10-2 standard operating model complete. Ready for P10-3.*
