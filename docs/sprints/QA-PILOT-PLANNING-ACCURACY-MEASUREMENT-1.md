# Sprint — QA-PILOT-PLANNING-ACCURACY-MEASUREMENT-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #229 (proposed)
**Lane:** assurance / optimization
**Type:** Measurement foundation — planning accuracy feedback loop
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Epic:** EPIC-QA-PILOT-ASSURANCE-OPTIMIZATION-1
**Predecessor:** QA-PILOT-ASSURANCE-ROUNDTRIP-VALIDATION-1 (#228, complete)

---

## 1. Purpose

Measure whether assurance context improves planning decisions.

The assurance engine now knows:
- What happened
- What evidence exists
- What risk exists
- What should be considered

What it does NOT yet know:
- **"Did our assurance improve the result?"**

This sprint closes the final learning loop.

## 2. The Missing Signal

```
Current:

Assurance State
      ↓
LINK Context
      ↓
Human Decision


What is missing:

Human Decision
      ↓
Actual Outcome
      ↓
Compare Prediction vs Reality
```

## 3. Planning Accuracy Model

### 3.1 Planning Intent Record

```json
{
  "intent_id": "PI-001",
  "project_id": "librarian",
  "planned_at": "2026-08-16T05:00:00Z",
  "planning_context": {
    "assurance_state": "operational",
    "risk_band": "monitor",
    "coverage": "partial",
    "freshness": "current"
  },
  "estimates": {
    "complexity": "low",
    "effort_days": 3,
    "risk_level": "low",
    "expected_findings": 0
  },
  "decision_rationale": "Existing security coverage is partial. Risk band is monitor."
}
```

### 3.2 Execution Outcome Record

```json
{
  "outcome_id": "EO-001",
  "intent_id": "PI-001",
  "executed_at": "2026-08-16T05:05:00Z",
  "actual": {
    "complexity": "medium",
    "effort_days": 5,
    "findings": 2,
    "severity_breakdown": {
      "medium": 1,
      "low": 1
    }
  },
  "assurance_impact": {
    "qualification_findings": 1,
    "risk_band_changed": false,
    "evidence_gaps_discovered": ["security_controls"]
  }
}
```

### 3.3 Variance Analysis

```json
{
  "variance_id": "VA-001",
  "intent_id": "PI-001",
  "outcome_id": "EO-001",
  "analysis": {
    "effort_variance": {
      "estimated": 3,
      "actual": 5,
      "variance_pct": 66.7,
      "direction": "over"
    },
    "findings_variance": {
      "estimated": 0,
      "actual": 2,
      "variance": 2,
      "direction": "more_than_expected"
    },
    "root_cause": "Insufficient assurance context before planning"
  },
  "learning_signal": {
    "type": "planning_gap",
    "description": "Security qualification coverage was partial, leading to unexpected findings",
    "recommendation": "Include security qualification gate in planning checklist"
  }
}
```

## 4. Feedback Loop

```
Planning Intent
      ↓
Execution
      ↓
Outcome
      ↓
Variance Analysis
      ↓
Learning Signal
      ↓
LINK Context Enhancement
      ↓
Better Planning Decisions
```

## 5. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| PA-001 | Planning intent record schema defined | `docs/schemas/assurance/planning-intent-v1.schema.json` — 8 fields, advisory_only const | ✅ |
| PA-002 | Execution outcome record schema defined | `docs/schemas/assurance/execution-outcome-v1.schema.json` — 7 fields, advisory_only const | ✅ |
| PA-003 | Variance analysis model implemented | `scripts/measure-planning-accuracy.py` — effort variance, findings variance, complexity variance, root cause, learning signal | ✅ |
| PA-004 | Learning signal generation | System produces learning signals (planning_gap, coverage_gap, freshness_gap, risk_miscalibration, assurance_benefit) | ✅ |
| PA-005 | LINK context enhancement | Learning signals generated and stored for future LINK consumption | ✅ |
| PA-006 | Deterministic measurement | Same intent + outcome → same variance analysis | ✅ |
| PA-007 | Authority boundary preserved | Measurement does not create work, close findings, or approve actions. advisory_only=true on all records. | ✅ |
| PA-008 | Existing validators pass | No regressions from #228 baseline | ✅ |

## 6. Guardrails

| Guardrail | Rule |
|-----------|------|
| Measurement only | No action creation from variance analysis |
| Learning signal | Output is recommendation, not instruction |
| No authority escalation | Variance analysis does not authorize remediation |
| Deterministic | Same inputs → same outputs |
| Evidence-backed | Variance analysis references specific records |

## 7. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-PLANNING-ACCURACY-MEASUREMENT-1.md` | This sprint document |
| `docs/schemas/assurance/planning-intent-v1.schema.json` | Planning intent record schema |
| `docs/schemas/assurance/execution-outcome-v1.schema.json` | Execution outcome record schema |
| `contracts/assurance/planning-accuracy-contract.md` | Planning accuracy model contract |
| `scripts/measure-planning-accuracy.py` | Measurement engine |
| `data/assurance/planning-intents/` | Planning intent records |
| `data/assurance/execution-outcomes/` | Execution outcome records |
| `data/assurance/variance-analyses/` | Variance analysis results |
| `data/assurance/learning-signals/` | Learning signals |

## 8. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #229 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 9. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-ASSURANCE-ROUNDTRIP-VALIDATION-1 (#228) | ✅ Complete |
| LINK query surface | ✅ Working |
| Risk engine | ✅ Working |
| Continuous qualification | ✅ Working |
