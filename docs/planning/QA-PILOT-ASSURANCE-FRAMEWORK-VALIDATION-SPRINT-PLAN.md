# QA Pilot Assurance Framework — Validation Sprint Plan

**Type:** Validation exercise — no framework expansion
**Status:** PLANNING ONLY — no implementation authorized
**Preceding gate:** QA Pilot Assurance Framework Operating Mode Declaration (✅ complete)
**Next gate:** Owner authorization → Validation execution

---

## 1. Purpose

Validate that the frozen QA Pilot assurance framework produces useful, trustworthy decision support in practice.

The framework architecture is frozen. The unknown is not whether more controls can be added — it is whether the existing framework produces actionable evidence.

---

## 2. Core Invariant

```
Validation Finding
        ≠
Framework Change
```

Validation produces observations and recommendations. It does **not** authorize architecture changes, capability additions, or profile modifications.

---

## 3. Scope

### Included

- Run all 7 existing capabilities against a representative project/application
- Evaluate evidence discovery, classification consistency, provenance, and freshness
- Assess the Release Readiness Profile output for utility and boundary adherence
- Produce a validation report with findings and recommendations

### Explicitly Excluded

- ❌ New capability implementation
- ❌ New profile creation
- ❌ Architecture changes
- ❌ Classification taxonomy changes
- ❌ Cross-system integration
- ❌ Script modifications
- ❌ Framework expansion of any kind

---

## 4. Validation Target

### Selection Criteria

The target should be:
- A real application or project within the CarbideFrame workspace
- Accessible to QA Pilot's existing capabilities (static analysis-based)
- Representative of the type of project the framework is expected to assess
- Not altered or instrumented for validation purposes

### Proposed Candidates

| Candidate | Location | Rationale |
|-----------|----------|-----------|
| **Librarian browser-app** | `CarbideFrame/active/qa-pilot/browser-app/` | Already the target of existing capabilities — direct applicability |
| **Librarian core governance docs** | `CarbideFrame/docs/governance/` | Tests documentation-focused capabilities |
| **Runtime Node** | `CarbideFrame/librarian-runtime-node/` | Cross-project validation — tests framework generality |

**Primary recommendation:** The existing `browser-app/` target already exercised by #179–#182, privacy (#186), and dependency (#187) capabilities. Running the full framework against it validates the integration chain.

---

## 5. Evaluation Areas

### Area 1 — Evidence Discovery

| Question | Validation Method |
|----------|-----------------|
| Can the framework identify relevant evidence for each capability? | Run each capability script; verify output is non-empty and meaningful |
| Are evidence files produced in the expected locations? | Check `data/*.json` output paths |
| Are there any capabilities that fail to produce evidence on this target? | Report capability failures with error detail |

### Area 2 — Profile Consumption

| Question | Validation Method |
|----------|-----------------|
| Do #186 (Privacy), #187 (Dependency Risk), and #188 (Security) consume available evidence correctly? | Verify each profile's `assurance_report.inputs` or `consumes` field |
| Are evidence references valid (files exist, JSON is parseable)? | Validate each referenced file path |
| Do control_summary/assessments contain meaningful findings? | Review finding text for clarity and actionability |

### Area 3 — Classification Consistency

| Question | Validation Method |
|----------|-----------------|
| Are PASS / OBSERVATION / OWNER_DECISION_REQUIRED classifications consistent across capabilities? | Compare findings that should logically share a classification |
| Are there any false positives (PASS when evidence suggests otherwise)? | Manual review of PASS findings |
| Are there any false negatives (ODR when evidence is unremarkable)? | Manual review of OWNER_DECISION_REQUIRED findings |
| Is the overall profile status consistent with individual control findings? | Verify aggregation logic per #185 inheritance rules |

### Area 4 — Provenance

| Question | Validation Method |
|----------|-----------------|
| Can every finding trace back to its source evidence? | Pick 5 findings per capability; verify `evidence_references` resolve |
| Are evidence_references valid file paths? | Verify file existence for all referenced paths |
| Is the evidence chain reconstructable? | Trace: Release Readiness → Profile → Capability → Evidence file → Raw data |

### Area 5 — Release Readiness Utility

| Question | Validation Method |
|----------|-----------------|
| Does the Release Readiness Profile expose useful gaps? | Review `coverage` missing/stale results |
| Are owner decisions actionable? | Review `owner_decisions` — can the Owner act on these? |
| Does the aggregation avoid making release decisions? | Verify no `ship_approved`, `blocked`, or deployment fields |
| Is evidence freshness tracked correctly? | Check `status` field in `coverage` against file modification timestamps |

### Area 6 — Owner Boundary

| Question | Validation Method |
|----------|-----------------|
| Does the output stop before making decisions? | Verify no decision language in findings |
| Are all findings advisory (`authority_level: advisory`)? | Check every evidence file |
| Is the Owner decision boundary preserved? | Verify no auto-remediation, no auto-approval, no implicit authority |

---

## 6. Deliverables

| # | Deliverable | Contents |
|---|-------------|----------|
| 1 | **Validation Report** | Summary of evaluation areas, findings per area, classification consistency assessment |
| 2 | **Findings Inventory** | Structured list of validation findings with PASS/OBSERVATION/ODR classification |
| 3 | **Framework Improvement Recommendations** | Bounded list of recommendations — no architecture changes unless separately authorized |

### Report Format

```json
{
  "validation": "QA-PILOT-ASSURANCE-FRAMEWORK-VALIDATION-1",
  "target": "browser-app",
  "generated_at": "ISO8601",
  "areas": [
    {
      "area": "Evidence Discovery",
      "status": "PASS",
      "findings": []
    }
  ],
  "overall": "OBSERVATION",
  "recommendations": [
    {
      "recommendation": "Improve X",
      "classification": "OBSERVATION",
      "requires_authorization": false
    }
  ],
  "authority_level": "advisory"
}
```

---

## 7. Acceptance Gates

| Gate | Requirement |
|------|-------------|
| VAL-1 | All 7 capabilities executed against the target |
| VAL-2 | Evidence discovery assessed (non-empty, meaningful output) |
| VAL-3 | Classification consistency evaluated |
| VAL-4 | Provenance verified (findings traceable to source evidence) |
| VAL-5 | Release Readiness utility assessed |
| VAL-6 | Owner boundary confirmed preserved |
| VAL-7 | No framework changes made during validation |
| VAL-8 | Validation report produced |

---

## 8. Change Restriction

During validation, the following are **not permitted**:

- Modifying capability scripts
- Changing evidence file paths
- Altering the Release Readiness Profile
- Adding new capabilities or profiles
- Modifying the classification taxonomy
- Changing the #185 assurance_report schema
- Creating any new evidence files beyond the validation report

If a framework issue is discovered during validation, it is recorded as a finding — not fixed immediately. Fixes require a separate authorized sprint after validation completes.

---

## 9. Current State

| Gate | Status |
|------|--------|
| QA Pilot Operating Mode Declaration | ✅ Complete |
| **Validation Sprint Plan** | **✅ Complete — awaiting authorization** |
| Validation execution | ⏳ Requires Owner authorization |
| Post-validation decision | ⏳ After validation results |

---

## 10. Next Transition

**Owner authorization** to execute the validation sprint.

After authorization, validation produces a report with findings and recommendations. No framework changes occur during validation.

---

*Document: QA-PILOT-ASSURANCE-FRAMEWORK-VALIDATION-SPRINT-PLAN.md*
*Status: Planning Only | Validation Only — no framework expansion*
*Core invariant: Validation Finding ≠ Framework Change*
