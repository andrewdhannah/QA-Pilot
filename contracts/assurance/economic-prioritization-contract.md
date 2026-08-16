# Economic Prioritization Contract

**Sprint:** QA-PILOT-ASSURANCE-ECONOMICS-LAYER-1 (#237)
**Status:** ACTIVE — Owner-authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define the advisory resource prioritization model for attention value scoring.

## 2. Core Question

**Given limited attention and resources, which areas provide the highest expected value for review?**

## 3. Attention Value Model

### 3.1 Formula

```
Attention Value =
Risk Exposure
    × Change Frequency
    × Authority Impact
    × Confidence
    ÷ Estimated Effort
```

### 3.2 Component Definitions

| Component | Range | Source | Meaning |
|-----------|-------|--------|---------|
| Risk Exposure | 0-100 | Risk engine | What could matter? |
| Change Frequency | 0.5-2.0 | Runtime evidence, history | How often does this change? |
| Authority Impact | 1.0-4.0 | Authority scope | What is at stake? |
| Confidence | 0.4-1.0 | Evidence quality | How certain are we? |
| Estimated Effort | 0.5-10.0 | Planning accuracy | How much work to review? |

### 3.3 Component Ranges

**Risk Exposure (0-100):**
- From existing risk engine
- Higher = more potential issues

**Change Frequency (0.5-2.0):**
- 0.5: Rarely changes (stable)
- 1.0: Average change frequency
- 2.0: Frequently changes (active)

**Authority Impact (1.0-4.0):**
- 1.0: Observation-only (low impact)
- 2.0: Recommendation scope (medium impact)
- 3.0: Mutation capability (high impact)
- 4.0: Critical governance (critical impact)

**Confidence (0.4-1.0):**
- 0.4: Low confidence (missing evidence)
- 0.7: Medium confidence (partial evidence)
- 1.0: High confidence (full evidence)

**Estimated Effort (0.5-10.0):**
- 0.5: Minimal effort (< 1 hour)
- 2.0: Low effort (1 day)
- 5.0: Medium effort (1 week)
- 10.0: High effort (1 month)

### 3.4 Attention Value Interpretation

| Score Range | Level | Meaning |
|-------------|-------|---------|
| 0-20 | Low | Low priority for review |
| 21-50 | Medium | Worth reviewing when time permits |
| 51-80 | High | Should be reviewed soon |
| 81-100 | Critical | Immediate review recommended |

## 4. Non-Authority Boundary

The economics engine:

| May Do | May Not Do |
|--------|------------|
| Compute attention scores | Create work packets |
| Rank projects by value | Assign priorities |
| Recommend review order | Authorize actions |
| Explain scoring | Modify state |
| Reference evidence | Create false evidence |

## 5. Explainability Requirement

Every attention value score must include:

```json
{
  "attention_score": 65,
  "attention_level": "high",
  "components": {
    "risk_exposure": 62,
    "change_frequency": 1.5,
    "authority_impact": 2.0,
    "confidence": 0.7,
    "estimated_effort": 2.0
  },
  "contributing_factors": [
    "capability gaps detected",
    "missing runtime evidence",
    "recent change activity"
  ],
  "evidence_refs": ["RA-001", "CD-001"],
  "advisory_only": true
}
```
