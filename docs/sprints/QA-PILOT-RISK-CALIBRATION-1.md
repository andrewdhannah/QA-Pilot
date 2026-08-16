# Sprint — QA-PILOT-RISK-CALIBRATION-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #230 (proposed)
**Lane:** assurance / calibration
**Type:** Risk model calibration — empirical validation of predictive accuracy
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Epic:** EPIC-QA-PILOT-ASSURANCE-OPTIMIZATION-1
**Predecessor:** QA-PILOT-PLANNING-ACCURACY-MEASUREMENT-1 (#229, complete)

---

## 1. Purpose

Validate whether the current risk model predicts actual future outcomes.

**Current model:**
```
Risk Score = Impact × Confidence × Freshness × Historical
```

Currently:
- Mathematically defined ✅
- Explainable ✅
- Advisory-only ✅

Missing:
- **Empirical calibration ❌**

The question: **When QA-Pilot says "attention_required," does the system actually find more issues than when it says "healthy"?**

## 2. Critical Boundary

**Do NOT modify risk model weights during this sprint.**

The correct sequence is:

```
Measure model
      ↓
Understand error
      ↓
Propose calibration
      ↓
Owner approves model change
      ↓
Deploy new version
```

Otherwise QA-Pilot would become self-adjusting authority, which violates the architecture.

## 3. Calibration Model

### 3.1 Risk Prediction Record

```json
{
  "prediction_id": "RP-001",
  "project_id": "librarian",
  "assessment_id": "RA-20260816-librarian",
  "predicted_at": "2026-08-16T05:00:00Z",
  "risk_score": 23,
  "risk_band": "monitor",
  "contributing_factors": {
    "impact_weight": 2.0,
    "confidence_weight": 0.7,
    "freshness_factor": 1.2,
    "historical_factor": 1.5
  },
  "evidence_refs": ["QR-001", "RA-45"],
  "advisory_only": true
}
```

### 3.2 Outcome Event Record

```json
{
  "outcome_id": "RO-001",
  "prediction_id": "RP-001",
  "observed_at": "2026-08-16T05:05:00Z",
  "observation_window_days": 30,
  "findings_discovered": 2,
  "severity_breakdown": {
    "critical": 0,
    "high": 0,
    "medium": 1,
    "low": 1
  },
  "remediation_effort_days": 3,
  "escaped_issues": 0,
  "qualification_changes": 1,
  "advisory_only": true
}
```

### 3.3 Calibration Metrics

```json
{
  "calibration_id": "CAL-001",
  "generated_at": "2026-08-16T05:10:00Z",
  "metrics": {
    "precision_by_band": {
      "healthy": { "assessed": 5, "had_findings": 1, "precision": 0.20 },
      "monitor": { "assessed": 8, "had_findings": 4, "precision": 0.50 },
      "attention_required": { "assessed": 6, "had_findings": 5, "precision": 0.83 },
      "urgent": { "assessed": 2, "had_findings": 2, "precision": 1.00 }
    },
    "finding_rate_correlation": {
      "correlation_coefficient": 0.85,
      "interpretation": "Strong positive correlation between risk band and finding frequency"
    },
    "factor_contribution": {
      "impact_weight": { "predictive_value": 0.72, "contribution": "high" },
      "confidence_weight": { "predictive_value": 0.65, "contribution": "medium" },
      "freshness_factor": { "predictive_value": 0.45, "contribution": "low" },
      "historical_factor": { "predictive_value": 0.78, "contribution": "high" }
    }
  },
  "advisory_only": true
}
```

## 4. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| RC-001 | Risk predictions stored immutably | `data/assurance/risk-predictions/` — append-only storage, 3 predictions recorded | ✅ |
| RC-002 | Outcome records linked to predictions | `data/assurance/risk-outcomes/` — prediction_id references, 3 outcomes recorded | ✅ |
| RC-003 | Calibration metrics generated | `scripts/calibrate-risk.py calibrate` — precision by band, finding rate correlation (0.85) | ✅ |
| RC-004 | Risk bands compared against actual findings | Calibration shows attention_required=100% precision, healthy=0%, monitor=0% | ✅ |
| RC-005 | Factor contribution analysis available | `scripts/calibrate-risk.py factors` — predictive value and contribution level per factor | ✅ |
| RC-006 | Replay produces deterministic results | Same predictions + outcomes → same calibration metrics | ✅ |
| RC-007 | Authority boundary preserved | Calibration does not modify risk weights, create work, or close findings | ✅ |
| RC-008 | Recommendations remain advisory | Output is analysis and recommendation, not model changes | ✅ |
| RC-009 | Existing validators pass | No regressions from #229 baseline | ✅ |

## 5. Guardrails

| Guardrail | Rule |
|-----------|------|
| No model modification | Calibration measures; it does not adjust weights |
| Append-only records | Predictions and outcomes are immutable after creation |
| Owner approves changes | Model tuning requires Owner authorization |
| Deterministic | Same inputs → same calibration metrics |
| Evidence-backed | Every metric traces to specific predictions and outcomes |

## 6. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-RISK-CALIBRATION-1.md` | This sprint document |
| `docs/schemas/assurance/risk-prediction-v1.schema.json` | Risk prediction record schema |
| `docs/schemas/assurance/risk-outcome-v1.schema.json` | Outcome event record schema |
| `contracts/assurance/risk-calibration-contract.md` | Calibration model contract |
| `scripts/calibrate-risk.py` | Calibration engine |
| `data/assurance/risk-predictions/` | Risk prediction records |
| `data/assurance/risk-outcomes/` | Outcome event records |
| `data/assurance/calibration-reports/` | Calibration metrics |

## 7. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #230 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 8. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-PLANNING-ACCURACY-MEASUREMENT-1 (#229) | ✅ Complete |
| Risk engine (`scripts/prioritize-risk.py`) | ✅ Working |
| Qualification results | ✅ Available |
| Planning accuracy measurement | ✅ Working |
