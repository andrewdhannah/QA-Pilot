# Closed-Loop Optimization Contract

**Sprint:** QA-PILOT-CLOSED-LOOP-OPTIMIZATION-1 (#245)
**Status:** ACTIVE — Owner-authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define how improvement outcomes produce learning signals for future planning and qualification.

## 2. Core Principle

**Learning signals are evidence-backed optimization inputs, not governance policies.**

## 3. Learning Signal Record

```json
{
  "signal_id": "LS-001",
  "outcome_id": "IO-001",
  "proposal_id": "IP-001",
  "recommendation_id": "PR-001",
  "project_id": "agent-bridge",
  "generated_at": "2026-08-16T07:15:00Z",
  "outcome_classification": "unchanged",
  "intervention_type": "evidence_enhancement",
  "baseline_state": {"metric": "evidence_coverage", "value": "none"},
  "post_change_state": {"metric": "evidence_coverage", "value": "none"},
  "measured_delta": "none → none",
  "confidence": "observation",
  "learning_category": "planning_insight",
  "learning_content": "Evidence enhancement intervention produced no observed change under current conditions.",
  "effectiveness_signal": "not_effective",
  "measurement_quality": "measurable",
  "applicable_context": {
    "project_id": "agent-bridge",
    "capability": "runtime_evidence",
    "conditions": "no_prior_evidence"
  },
  "evidence_refs": ["IO-001", "CD-001"],
  "advisory_only": true
}
```

## 4. Learning Categories

| Category | Meaning | Consumption |
|----------|---------|-------------|
| `planning_insight` | What we learned about planning | Future estimates |
| `qualification_insight` | What we learned about qualification | Future qualification |
| `risk_calibration_signal` | What we learned about risk | Risk model tuning |
| `recommendation_effectiveness` | How well recommendations work | Future recommendations |

## 5. Effectiveness Measurement

| Outcome | Effectiveness Signal |
|---------|---------------------|
| `improved` | effective |
| `unchanged` | not_effective |
| `degraded` | harmful |
| `inconclusive` | unknown |
| `not_measurable` | measurement_gap |

## 6. Learning Confidence

| Historical Outcomes | Confidence | Meaning |
|---------------------|------------|---------|
| 1 | observation | Single data point |
| 2-4 | emerging_pattern | Early pattern |
| 5-9 | developing_pattern | Moderate evidence |
| >= 10 | established_pattern | Strong evidence |

## 7. Non-Authority Boundary

Learning signals:

| May Do | May Not Do |
|--------|------------|
| Produce insights | Modify governance |
| Inform planning | Create work |
| Inform qualification | Change risk weights |
| Measure effectiveness | Approve proposals |
| Reference evidence | Close findings |
| Build history | Modify authority |
