# Preventive Recommendation Contract

**Sprint:** QA-PILOT-PREVENTIVE-RECOMMENDATIONS-1 (#241)
**Status:** ACTIVE — Owner-authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define advisory recommendations derived from predictive signals.

## 2. Core Invariant

```
Observation → Qualification → Assessment → Prediction → Recommendation

Each step may reduce uncertainty.
No step may increase authority.
```

## 3. Recommendation Semantics

| Term | Definition | Not |
|------|------------|-----|
| `recommendation` | Suggested attention area | Requirement, finding, or approval |
| `rationale` | Why this recommendation exists | Root cause or diagnosis |
| `evidence_refs` | What data supports this | Proof of necessity |
| `confidence` | How certain the recommendation is | Authority to act |
| `expiration` | When this recommendation expires | Deadline |

## 4. Recommendation Types

| Type | Meaning | Example |
|------|---------|---------|
| `evidence_enhancement` | Consider improving evidence coverage | "Consider adding runtime evidence" |
| `risk_review` | Consider reviewing risk assessment | "Risk trajectory increasing" |
| `planning_adjustment` | Consider adjusting estimates | "Planning variance detected" |
| `no_recommendation` | No action needed | "Current state is stable" |

## 5. Evidence Requirements

Every recommendation must reference:

| Requirement | Meaning |
|-------------|---------|
| Signal reference | Which predictive signal triggered this |
| Pattern references | Which historical patterns support this |
| Evidence references | What data backs this |
| Confidence basis | Why this confidence level |

## 6. Expiration Rules

| Recommendation Type | Default Expiration |
|--------------------|--------------------|
| evidence_enhancement | 90 days |
| risk_review | 30 days |
| planning_adjustment | 60 days |
| no_recommendation | N/A |

## 7. Non-Authority Boundary

Recommendations:

| May Do | May Not Do |
|--------|------------|
| Suggest attention areas | Create work packets |
| Reference evidence | Create findings |
| Show confidence | Assign priorities |
| Explain rationale | Trigger remediation |
| Report expiration | Modify state |
| Recommend review | Authorize action |
