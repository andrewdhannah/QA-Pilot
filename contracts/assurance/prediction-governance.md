# Prediction Governance Contract

**Sprint:** QA-PILOT-ASSURANCE-PREDICTIVE-READINESS-1 (#238)
**Status:** ACTIVE — Owner-authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define governance rules for predictive assurance before prediction capability is built.

## 2. Core Invariant

```
Prediction ≠ Decision
Prediction ≠ Finding
Prediction ≠ Required Action
```

## 3. Prediction Semantics

| Term | Definition | Implication |
|------|------------|-------------|
| `prediction` | Statistical likelihood based on history | Not a finding or requirement |
| `confidence` | How certain the prediction is | Not authority to act |
| `risk_signal` | Early warning indicator | Not a confirmed issue |
| `recommendation` | Suggested attention area | Not a required action |

## 4. Prediction Types

| Type | Meaning | Example |
|------|---------|---------|
| `trend_prediction` | Where a metric is heading | "Risk likely to increase" |
| `gap_prediction` | What gaps may emerge | "Evidence coverage may become insufficient" |
| `variance_prediction` | What may deviate from plan | "Effort may exceed estimate" |
| `pattern_prediction` | Recurring patterns | "Projects with this profile tend to have findings" |

## 5. Confidence Levels

| Level | Threshold | Meaning |
|-------|-----------|---------|
| `high` | >= 80% | Strong historical basis |
| `medium` | 50-79% | Moderate historical basis |
| `low` | < 50% | Limited historical basis |
| `insufficient_data` | N/A | Not enough data to predict |

## 6. False Positive/Negative Behavior

### 6.1 False Positive

**Scenario:** Predicted issue, none occurred.

**Handling:**
- Log for model tuning
- No penalty to prediction system
- No wasted Owner attention (prediction was advisory)
- Feed back into model improvement

### 6.2 False Negative

**Scenario:** Missed prediction, issue occurred.

**Handling:**
- Log for model improvement
- No blame attribution
- Analyze what signal was missed
- Feed back into feature engineering

### 6.3 Uncertain Prediction

**Scenario:** Prediction with low confidence.

**Handling:**
- Report with explicit low confidence
- Do not suppress uncertain predictions
- Let Owner decide if uncertainty is acceptable

### 6.4 Contradiction

**Scenario:** Prediction contradicts current evidence.

**Handling:**
- Prefer current evidence over prediction
- Flag contradiction for review
- Prediction may indicate emerging risk not yet in evidence

## 7. Authority Boundary

### 7.1 Predictions May

| Allowed | Example |
|---------|---------|
| Identify likelihood | "70% chance of finding in next qualification" |
| Recommend attention | "Consider reviewing this area" |
| Show confidence | "Confidence: medium" |
| Reference evidence | "Based on 5 historical patterns" |
| Explain basis | "Similar projects had findings" |

### 7.2 Predictions May Not

| Forbidden | Reason |
|-----------|--------|
| Create findings | Prediction is not observation |
| Assign priorities | Owner decides priority |
| Trigger remediation | Prediction is not diagnosis |
| Modify state | Prediction is observation |
| Authorize action | Only Owner authorizes |

## 8. Model Governance

### 8.1 Model Versioning

Every prediction model must be versioned:

```json
{
  "model_id": "string",
  "model_version": "string",
  "trained_at": "ISO8601",
  "training_data_summary": "string",
  "accuracy_metrics": {},
  "advisory_only": true
}
```

### 8.2 Model Change Process

1. New model trained on historical data
2. Accuracy evaluated against holdout set
3. Governance review (Owner approval required)
4. A/B testing period
5. Full deployment

### 8.3 Model Transparency

Every prediction must reference:
- Model version used
- Training data characteristics
- Confidence level
- Known limitations

## 9. Non-Authority Boundary

The prediction system:

| May Do | May Not Do |
|--------|------------|
| Predict likelihood | Diagnose root cause |
| Recommend attention | Assign work |
| Show confidence | Claim certainty |
| Reference history | Extrapolate beyond data |
| Explain predictions | Justify actions |
