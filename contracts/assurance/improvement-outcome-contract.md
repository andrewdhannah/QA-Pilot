# Improvement Outcome Contract

**Sprint:** QA-PILOT-IMPROVEMENT-OUTCOME-MEASUREMENT-1 (#244)
**Status:** ACTIVE — Owner-authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define how intervention outcomes are measured and recorded.

## 2. Core Principle

**Outcome measures what changed. It does not declare success or failure.**

## 3. Outcome Classifications

| Classification | Condition | Meaning |
|----------------|-----------|---------|
| `improved` | Measured metric moved in intended direction | Learning opportunity |
| `unchanged` | Measured metric did not change | May need different approach |
| `degraded` | Measured metric moved in wrong direction | Requires investigation |
| `inconclusive` | Insufficient evidence to determine | More evidence needed |
| `not_measurable` | No clear measurement criteria | Measurement design gap |

## 4. Outcome Record

```json
{
  "outcome_id": "IO-001",
  "proposal_id": "IP-001",
  "work_packet_id": "WP-001",
  "project_id": "agent-bridge",
  "measured_at": "2026-08-16T07:00:00Z",
  "baseline": {
    "metric": "evidence_coverage",
    "value": "none",
    "evidence_ref": "CD-001",
    "captured_at": "2026-08-16T05:00:00Z"
  },
  "post_change": {
    "metric": "evidence_coverage",
    "value": "minimal",
    "evidence_ref": "RE-001",
    "captured_at": "2026-08-16T06:45:00Z"
  },
  "comparison": {
    "direction": "improved",
    "confidence": "medium",
    "delta": "none → minimal"
  },
  "measurement_criteria": "Evidence coverage increased from none to minimal",
  "provenance_chain": {
    "recommendation_id": "PR-001",
    "proposal_id": "IP-001",
    "owner_decision": "accepted",
    "work_packet_id": "WP-001"
  },
  "advisory_only": true
}
```

## 5. Measurement Rules

| Rule | Requirement |
|------|-------------|
| Baseline required | Every outcome must reference pre-intervention state |
| Post-change required | Every outcome must reference post-intervention evidence |
| Deterministic comparison | Compare declared metrics, not agent assertion |
| Negative preservation | Degraded outcomes are valid and must be recorded |
| Inconclusive valid | Insufficient evidence produces "inconclusive" |

## 6. Non-Authority Boundary

Outcome measurement:

| May Do | May Not Do |
|--------|------------|
| Measure condition change | Close findings |
| Record baseline and post-change | Modify risk models |
| Compare metrics | Change qualification policy |
| Classify direction | Approve interventions |
| Reference evidence | Seal work |
| Feed learning | Auto-remediate |
