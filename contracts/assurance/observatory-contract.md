# Observatory Contract

**Sprint:** QA-PILOT-ASSURANCE-OBSERVATORY-1 (#234)
**Status:** ACTIVE — Owner-authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define the observatory that aggregates assurance ecosystem outputs into human-decidable project health views.

## 2. Core Principle

The observatory converts raw assurance data into governed ecosystem awareness.

**Before:** QA-Pilot evaluates systems
**After:** QA-Pilot provides governed ecosystem awareness

## 3. Project Health Model

### 3.1 Health States

| State | Condition | Meaning |
|-------|-----------|---------|
| `healthy` | All checks pass, low risk, good coverage | No attention needed |
| `monitor` | Minor gaps or aging evidence | Watch for changes |
| `attention_needed` | Significant gaps, high risk, or stale evidence | Human should review |
| `critical` | Multiple critical findings or authority issues | Immediate attention |

### 3.2 Health Components

| Component | Source | Weight |
|-----------|--------|--------|
| Evidence Coverage | Fleet freshness | High |
| Qualification State | Qualification history | High |
| Risk Band | Risk engine | High |
| Capability Gaps | Capability discovery | Medium |
| Planning Accuracy | Planning accuracy measurement | Low |

## 4. Trend Analysis

### 4.1 Trend Types

| Trend | Calculation | Meaning |
|-------|-------------|---------|
| `improving` | Recent values better than historical | State is getting better |
| `stable` | Recent values similar to historical | State is unchanged |
| `degrading` | Recent values worse than historical | State is getting worse |

### 4.2 Trend Windows

| Window | Period | Purpose |
|--------|--------|---------|
| Short-term | 7 days | Recent changes |
| Medium-term | 30 days | Monthly trend |
| Long-term | 90 days | Quarterly trend |

## 5. Observatory Output

```json
{
  "observatory_id": "string",
  "generated_at": "ISO8601",
  "fleet_summary": {
    "total_projects": "int",
    "health_distribution": {
      "healthy": "int",
      "monitor": "int",
      "attention_needed": "int",
      "critical": "int"
    },
    "overall_status": "string"
  },
  "projects": [
    {
      "project_id": "string",
      "health": "string",
      "health_rationale": "string",
      "evidence_coverage": "string",
      "qualification_state": "string",
      "risk_band": "string",
      "risk_score": "int",
      "capability_gaps": "int",
      "planning_accuracy": "string",
      "recommended_attention": "string"
    }
  ],
  "trends": {
    "risk_trend": "string",
    "freshness_trend": "string",
    "coverage_trend": "string"
  },
  "attention_needed": [
    {
      "project_id": "string",
      "reason": "string",
      "priority": "string"
    }
  ],
  "advisory_only": true
}
```

## 6. Non-Authority Boundary

The observatory:

| May Do | May Not Do |
|--------|------------|
| Aggregate state | Modify assurance state |
| Display trends | Trigger remediation |
| Recommend attention | Create work packets |
| Explain health | Close findings |
| Generate reports | Authorize actions |
