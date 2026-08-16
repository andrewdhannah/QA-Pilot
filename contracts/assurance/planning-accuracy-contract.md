# Planning Accuracy Contract

**Sprint:** QA-PILOT-PLANNING-ACCURACY-MEASUREMENT-1 (#229)
**Status:** ACTIVE — Authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define the planning accuracy measurement model. Measure whether assurance context improves planning decisions by comparing predicted vs actual outcomes.

## 2. Core Principle

The system now knows:
- What happened
- What evidence exists
- What risk exists
- What should be considered

The next capability:
- **"Did our assurance improve the result?"**

## 3. Planning Accuracy Model

### 3.1 Measurement Flow

```
Planning Intent (prediction)
      ↓
Execution
      ↓
Actual Outcome
      ↓
Variance Analysis
      ↓
Learning Signal
      ↓
LINK Context Enhancement
```

### 3.2 Variance Metrics

| Metric | Formula | Meaning |
|--------|---------|---------|
| Effort Variance | `(actual - estimated) / estimated * 100` | How much effort differed from plan |
| Findings Variance | `actual_findings - expected_findings` | How many more/fewer findings than expected |
| Complexity Variance | `actual_complexity - planned_complexity` | How complexity compared to estimate |
| Risk Variance | `actual_risk - predicted_risk` | How risk compared to prediction |

### 3.3 Learning Signal Types

| Signal Type | Trigger | Meaning |
|-------------|---------|---------|
| `planning_gap` | Effort variance > 50% | Planning did not account for actual complexity |
| `coverage_gap` | Unexpected findings | Evidence coverage was insufficient |
| `freshness_gap` | Stale evidence led to wrong prediction | Evidence freshness affected accuracy |
| `risk_miscalibration` | Risk band significantly wrong | Risk model needs tuning |
| `assurance_benefit` | Assurance context prevented issues | Assurance context improved outcome |

### 3.4 Feedback Loop

Learning signals feed back into planning context:

```
Before planning:
  "Security qualification coverage is partial"
  + 
  "Historical variance: +66% effort for partial coverage projects"
  ↓
  Better-informed planning decision
```

## 4. Variance Analysis Output

```json
{
  "variance_id": "VA-001",
  "intent_id": "PI-001",
  "outcome_id": "EO-001",
  "project_id": "librarian",
  "analyzed_at": "2026-08-16T05:10:00Z",
  "variance": {
    "effort": {
      "estimated": 3,
      "actual": 5,
      "variance_pct": 66.7,
      "direction": "over"
    },
    "findings": {
      "expected": 0,
      "actual": 2,
      "variance": 2,
      "direction": "more_than_expected"
    },
    "complexity": {
      "planned": "low",
      "actual": "medium",
      "direction": "underestimated"
    }
  },
  "root_cause": "Insufficient security qualification coverage",
  "learning_signal": {
    "type": "coverage_gap",
    "description": "Security qualification coverage was partial, leading to unexpected findings",
    "recommendation": "Include security qualification gate in planning checklist for partial coverage projects",
    "confidence": "medium"
  },
  "advisory_only": true
}
```

## 5. Acceptance Criteria

### 5.1 Deterministic

Same planning intent + same outcome → same variance analysis

### 5.2 Evidence-backed

Every learning signal traces to:
- Planning intent record
- Execution outcome record
- Specific variance metrics

### 5.3 Advisory

Learning signals are recommendations:
- "Include security qualification gate"
- Not: "Require security qualification"

### 5.4 Authority Boundary

The measurement engine:

| May Do | May Not Do |
|--------|------------|
| Record planning intents | Create work packets |
| Record execution outcomes | Assign owners |
| Compute variance | Close findings |
| Generate learning signals | Approve remediation |
| Enhance planning context | Make planning decisions |

## 6. Integration with Existing Systems

### 6.1 LINK Integration

Learning signals feed into `get_planning_context()`:

```python
def get_planning_context(project_id: str) -> dict:
    # Existing context
    context = {
        "coverage": "partial",
        "risk_band": "monitor",
        ...
    }
    
    # Add learning signals
    signals = get_learning_signals(project_id)
    if signals:
        context["historical_learning"] = signals
    
    return context
```

### 6.2 Risk Integration

Variance patterns feed into risk model:

```
Repeated planning gaps → Higher uncertainty weight
Consistent underestimation → Higher complexity factor
```

### 6.3 Continuous Qualification Integration

Learning signals can trigger requalification:

```
Coverage gap detected → Requalify affected profiles
```
