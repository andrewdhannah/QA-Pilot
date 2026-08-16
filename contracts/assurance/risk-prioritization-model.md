# Risk Prioritization Model Contract

**Sprint:** QA-PILOT-RISK-PRIORITIZATION-1 (#225)
**Status:** ACTIVE — Authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define the advisory risk ranking model that determines where human or agent attention should be directed. This model does NOT determine what must be changed — that remains Owner authority.

## 2. Core Principle

Risk prioritization answers: **"Where should a human or agent look first?"**
It does NOT answer: **"What must be changed?"**

| Allowed | Forbidden |
|---------|-----------|
| Risk score with explanation | Required action |
| Attention recommendation | Autonomous remediation |
| Driver identification | Finding closure |
| Evidence provenance | Owner decisions |

## 3. Risk Score Formula

```
Risk Priority Score
    =
Impact Weight
    × Confidence Weight
    × Freshness Factor
    × Historical Pattern Factor
```

### 3.1 Impact Weight

Derived from authority scope:

| Authority Scope | Impact Weight | Meaning |
|-----------------|---------------|---------|
| `inform-only` | 1.0 | Low impact — observation only |
| `recommendation` | 2.0 | Medium impact — recommendations can influence |
| `mutation_capability` | 3.0 | High impact — can make changes |
| `canonical_state` | 4.0 | Critical impact — affects canonical state |

### 3.2 Confidence Weight

Derived from evidence quality:

| Evidence Quality | Confidence Weight | Meaning |
|------------------|-------------------|---------|
| Qualified evidence | 1.0 | High confidence — evidence is validated |
| Partial evidence | 0.7 | Medium confidence — some validation |
| Unknown | 0.4 | Low confidence — cannot validate |

### 3.3 Freshness Factor

Represents uncertainty, not quality:

| Freshness State | Factor | Meaning |
|-----------------|--------|---------|
| `current` | 1.0 | Evidence is recent — low uncertainty |
| `aging` | 1.2 | Evidence is getting old — moderate uncertainty |
| `stale` | 1.5 | Evidence is outdated — high uncertainty |
| `unknown` | 2.0 | Cannot determine freshness — maximum uncertainty |

**Rule:** Higher factor = more attention needed. Stale evidence needs more attention not because it's bad, but because we don't know if it's still valid.

### 3.4 Historical Pattern Factor

Uses the learning loop:

| Pattern | Factor | Meaning |
|---------|--------|---------|
| No findings | 1.0 | Clean history |
| Repeated findings | 1.5 | Pattern detected — needs attention |
| Unresolved findings | 2.0 | Open issues — needs immediate attention |

## 4. Risk Bands

| Score Range | Band | Meaning |
|-------------|------|---------|
| 0 – 20 | `healthy` | No attention needed |
| 21 – 50 | `monitor` | Watch for changes |
| 51 – 80 | `attention_required` | Human should review |
| 81 – 100 | `urgent` | Immediate attention needed |

## 5. Risk Assessment Output

```json
{
  "project_id": "librarian",
  "assessment_id": "RA-20260816-001",
  "assessed_at": "2026-08-16T04:15:00Z",
  "risk_score": 72,
  "risk_band": "attention_required",
  "factors": {
    "impact_weight": 2.0,
    "confidence_weight": 0.7,
    "freshness_factor": 1.2,
    "historical_pattern_factor": 1.5,
    "raw_score": 2.52,
    "normalized_score": 72
  },
  "drivers": [
    "missing_security_coverage",
    "repeated_runtime_findings"
  ],
  "evidence_refs": [
    "QR-001",
    "FP-004"
  ],
  "recommendations": [
    "Consider adding security evidence coverage"
  ],
  "advisory_only": true,
  "authority_boundary": {
    "can_dispatch": false,
    "can_remediate": false,
    "can_close_findings": false,
    "can_decide": false
  }
}
```

## 6. Explanation Requirement

Every risk assessment must include an explanation that answers: "Why is this project ranked higher?"

The explanation consists of:
1. **Drivers**: Specific factors contributing to the score
2. **Evidence refs**: Which evidence records support the assessment
3. **Factor breakdown**: How each factor contributed to the final score

Example explanation:
```
Risk Score: 72 (attention_required)

Drivers:
  - missing_security_coverage: No security evidence found
  - repeated_runtime_findings: 2 runtime findings in last 30 days

Factor Breakdown:
  - Impact: 2.0 (recommendation scope)
  - Confidence: 0.7 (partial evidence)
  - Freshness: 1.2 (aging evidence)
  - Historical: 1.5 (repeated findings)
  - Raw: 2.0 × 0.7 × 1.2 × 1.5 = 2.52
  - Normalized: 72/100

Evidence:
  - QR-001: Qualification record (2026-08-15)
  - FP-004: Finding pattern (2026-08-14)
```

## 7. Determinism Requirement

The risk engine must be deterministic:

```
assess(project_state) → risk_assessment
assess(project_state) → risk_assessment  (same input, same output)
```

No randomness, no time-dependent scoring, no external state dependencies.

## 8. LINK Readiness Interface

Future LINK integration will consume:

```python
def get_project_risk_state(project_id: str) -> dict:
    """
    Returns risk state for a project.
    
    Returns:
        {
            "risk_score": int,
            "risk_band": "healthy" | "monitor" | "attention_required" | "urgent",
            "drivers": ["string"],
            "recommendations": ["string"],
            "last_assessment": "ISO8601"
        }
    """
    pass

def get_fleet_risk_state() -> dict:
    """
    Returns risk state for all governed projects.
    
    Returns:
        {
            "generated_at": "ISO8601",
            "total_projects": int,
            "by_band": {
                "healthy": int,
                "monitor": int,
                "attention_required": int,
                "urgent": int
            },
            "attention_needed": [
                {
                    "project_id": "string",
                    "risk_score": int,
                    "risk_band": "string",
                    "drivers": ["string"]
                }
            ]
        }
    """
    pass
```

## 9. Non-Authority Boundary

The risk engine MUST NOT:

| Forbidden Action | Reason |
|------------------|--------|
| Dispatch tasks | Owner decides what to do |
| Remediate findings | Owner authorizes remediation |
| Close findings | Owner verifies resolution |
| Make Owner decisions | Owner authority is absolute |
| Schedule work | Owner or agent decides timing |
| Modify evidence | Evidence is append-only |
| Create work packets | Work packets require authorization |
