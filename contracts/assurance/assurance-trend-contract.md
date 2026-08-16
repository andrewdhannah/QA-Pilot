# Assurance Trend Contract

**Sprint:** QA-PILOT-ASSURANCE-TREND-ANALYSIS-1 (#235)
**Status:** ACTIVE — Owner-authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define the trend analysis model for historical interpretation of assurance state.

## 2. Core Distinction

**Observatory answers:** "What is the state?"
**Trend Analysis answers:** "Where is the state moving?"

## 3. Trend Classifications

| Trend | Condition | Meaning |
|-------|-----------|---------|
| `improving` | Current value better than previous | State is getting better |
| `stable` | Current value similar to previous | State is unchanged |
| `degrading` | Current value worse than previous | State is getting worse |
| `insufficient_data` | Not enough history | Cannot determine trend |

## 4. Trend Record Schema

```json
{
  "trend_id": "string",
  "project_id": "string",
  "metric": "string",
  "window_start": "ISO8601",
  "window_end": "ISO8601",
  "previous_value": "number",
  "current_value": "number",
  "direction": "improving | stable | degrading | insufficient_data",
  "confidence": "high | medium | low",
  "delta": "number",
  "delta_pct": "number",
  "evidence_refs": ["string"],
  "advisory_only": true
}
```

## 5. Trend Metrics

### 5.1 Risk Trend

| Aspect | Definition |
|--------|------------|
| Metric | risk_score |
| Improvement | Score decreasing |
| Degradation | Score increasing |
| Stability | Score changing < 5% |

### 5.2 Evidence Coverage Trend

| Aspect | Definition |
|--------|------------|
| Metric | evidence_count |
| Improvement | Count increasing |
| Degradation | Count decreasing |
| Stability | Count unchanged |

### 5.3 Capability Gap Trend

| Aspect | Definition |
|--------|------------|
| Metric | gap_count |
| Improvement | Gaps decreasing |
| Degradation | Gaps increasing |
| Stability | Gaps unchanged |

## 6. Confidence Levels

| Level | Condition | Meaning |
|-------|-----------|---------|
| `high` | >= 3 data points, clear direction | Strong evidence for trend |
| `medium` | 2 data points or moderate signal | Some evidence |
| `low` | 1 data point or weak signal | Limited evidence |

## 7. Missing Data Behavior

When historical data is insufficient:
- Return `insufficient_data` trend
- Do NOT guess or interpolate
- Do NOT fail or error
- Return empty evidence_refs

## 8. Non-Authority Boundary

The trend engine:

| May Do | May Not Do |
|--------|------------|
| Compute trends | Recommend actions |
| Compare values | Assign priorities |
| Report direction | Trigger remediation |
| Show confidence | Create work |
| Reference evidence | Modify state |
