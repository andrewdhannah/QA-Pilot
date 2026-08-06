# #189 Human Assurance Profile — Impact Analysis

**Purpose:** Assess the impact of adding a Human Assurance Profile that evaluates operator understanding of governed systems. Assessment only — no implementation authorized.

**Status:** ASSESSMENT COMPLETE  
**Preceding gate:** #189 Planning Definition (✅ complete)  
**Next gate:** Invariant Review → Owner Authorization → Implementation

---

## 1. Authority Boundary Impact

### Invariant

```
Human Assurance Result ≠ Operational Authorization
```

### Verification

| Check | Risk | Mitigation |
|-------|------|------------|
| Output implies approval | Profile could say "Approved operator" instead of "Understanding demonstrated" | **Output contract requires:** classification = PASS/OBSERVATION/ODR only; no "approved," "authorized," or "certified" labels |
| Output grants permissions | Profile results could feed into an access control system | **Explicit non-goal:** no permission-granting capability; no integration with access control |
| Output replaces Owner decision | Manager could treat PASS as "operator is authorized to decide" | **Operating mode declaration** will define: Understanding ≠ Authorization |

### Output Language Rules

| Permitted | Not Permitted |
|-----------|---------------|
| "Understanding demonstrated" | "Approved operator" |
| "Knowledge gap identified" | "Authorized to modify production" |
| "Additional review recommended" | "Certified decision maker" |
| "Assessment evidence recorded" | "Operator granted authority" |

### Boundary: PASS

The planning definition explicitly separates human assurance from authorization. The output contract requires `authority_level: advisory`. No language in the profile implies approval, certification, or permission.

---

## 2. Knowledge Graph Impact

### Invariant

```
Knowledge Graph → Learning Path → Exercise → Assessment Evidence
Assessment Result → (does not modify) → Knowledge Graph
```

### Verification

| Check | Assessment |
|--------|------------|
| Graph remains navigation-only | Assessment results are not stored in the graph — they are evidence files |
| Training paths reference artifacts | Learning paths are traversals of existing graph edges — no new node types |
| No training artifact becomes evidence authority | Training materials reference source artifacts — they do not replace them |
| Graph relationships not altered by outcomes | Assessment evidence is written to `data/human-assurance/` — not to graph nodes or edges |

### Data Flow

```
Knowledge Graph (read-only traversal)
    ↓
Learning path generated (derived — not stored in graph)
    ↓
Operator follows path (external)
    ↓
Assessment executed (read -> evaluate -> write evidence)
    ↓
Assessment evidence stored (`data/human-assurance/`)
```

The graph is never written to by the assessment process.

### Boundary: PASS

---

## 3. Evidence Model Impact

### Invariant

Assessment evidence proves an assessment occurred. It does not prove authority.

### Evidence Schema

```json
{
  "assessment_type": "human_assurance",
  "exercise_id": "EX-001",
  "subject": "operator-identifier",
  "role": "technical-lead",
  "classification": "PASS | OBSERVATION | OWNER_DECISION_REQUIRED",
  "finding": "Description of demonstrated understanding or gap",
  "evidence_refs": [
    "path/to/referenced/artifact.md"
  ],
  "authority_level": "advisory"
}
```

### Contract Compliance

| Requirement | Status |
|-------------|--------|
| Follows existing classification taxonomy | ✅ PASS/OBSERVATION/ODR — no new levels |
| Includes evidence_refs | ✅ Required per assessment |
| authority_level: advisory | ✅ Hardcoded |
| Does not create new evidence class | ✅ Uses existing assurance_report format |
| Does not assert authority | ✅ No permission or approval fields |

### Boundary: PASS

---

## 4. QA Pilot Framework Impact

### Verification

| Check | Assessment |
|--------|------------|
| #189 consumes existing knowledge, not document search | ✅ Learning paths generated from graph traversal |
| #189 follows existing taxonomy | ✅ PASS/OBSERVATION/ODR — no new levels |
| Release Readiness does not interpret human assurance as system readiness | ⚠️ **Requires explicit separation:** Human assurance results must be kept separate from system assurance in Release Readiness aggregation |
| Existing profile contracts unchanged | ✅ No modification to #185 schema, #186, #187, or #188 |

### System vs Human Assurance Separation

| Profile | Evaluates | Consumed By |
|---------|-----------|-------------|
| #186 Privacy | Application privacy posture | Release Readiness |
| #187 Dependency Risk | Software supply chain | Release Readiness |
| #188 Security | Application security posture | Release Readiness |
| **#189 Human** | **Operator understanding** | **Governance view (separate from Release Readiness)** |

**Critical separation:** Human assurance results must not be mixed with system assurance results in the Release Readiness Profile. A human failing an assessment must not block a system release. A human passing an assessment must not certify a system.

### Boundary: PASS (with conditional)

**Condition:** Human assurance evidence must be stored separately from system assurance evidence and consumed by a separate governance view, not by the Release Readiness Profile.

---

## 5. Privacy and Security Considerations

### Data Governance Questions

| Question | Recommended Approach | Status |
|----------|---------------------|--------|
| What user information is stored? | Role, exercise responses, assessment evidence — no PII | ⏳ To be confirmed during implementation |
| How long are assessment records retained? | Same retention as other evidence (append-only) | ⏳ To be confirmed |
| Who can view individual results? | Owner and subject only | ⏳ To be confirmed |
| Are results tied to identity or role? | Tied to role for anonymized aggregation; tied to identity for individual capability records | ⏳ To be confirmed |

### Requirements

- No PII stored without explicit consent
- Assessment evidence is append-only — no modification or deletion
- Individual results visible only to the subject and Owner
- Aggregated results (by role) are governance-visible

### Boundary: PASS (with documentation requirements)

---

## 6. Success Measurement

### Assessment Criteria

| Capability | Measurement | Evidence |
|-----------|-------------|----------|
| Finds system purpose | Exercise: trace custody chain | Exercise result classification |
| Understands invariants | Exercise: explain what AUTH-003 protects | Exercise + referenced artifact |
| Locates certification proof | Exercise: find Sprint 7 evidence | Exercise + resolved evidence_refs |
| Identifies change process | Exercise: describe governance sequence | Exercise + operating mode reference |
| Knows Owner decision points | Exercise: identify ODR-classified findings | Exercise + Release Readiness reference |

### Validation Scenario

Give a new technical lead only:
- Repository
- Knowledge system access (graph + query layer)
- Documentation (governance, architecture, operations)
- Query interface

Measure:
- Time to first correct query
- Number of incorrect assumptions
- Questions answerable without human assistance
- Understanding of frozen vs changeable boundaries

---

## 7. Summary

| Assessment Area | Result |
|----------------|--------|
| Authority boundary | ✅ PASS — Human assurance ≠ operational authorization. Output contract prevents approval/certification language. |
| Knowledge graph impact | ✅ PASS — Read-only traversal. Assessment evidence stored separately. |
| Evidence model impact | ✅ PASS — Existing taxonomy. No new evidence classes. |
| QA Pilot framework impact | ⚠️ PASS (conditional) — Human assurance must be separated from system assurance in Release Readiness. |
| Privacy/security considerations | ⏹ Identified — implementation must define retention, visibility, and PII rules. |
| Success measurement | ✅ Defined — traceable to exercise results and evidence_refs. |

---

## 8. Gate State

| Gate | Status |
|------|--------|
| Planning Definition | ✅ Complete |
| **Impact Analysis** | **✅ Complete** |
| **Invariant Review** | **⏳ Next** |
| Owner Authorization | ⏳ After invariant review |
| Implementation | ❌ Not authorized |

---

*Document: QA-PILOT-189-IMPACT-ANALYSIS.md*
*Status: Assessment Complete | No implementation authorized*
*Key finding: Human assurance results must be separated from system assurance in Release Readiness.*
*Core invariant: Human Assurance Result ≠ Operational Authorization.*
