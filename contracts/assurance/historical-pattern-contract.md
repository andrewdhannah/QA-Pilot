# Historical Pattern Contract

**Sprint:** QA-PILOT-HISTORICAL-PATTERN-MODELING-1 (#239)
**Status:** ACTIVE — Owner-authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define the pattern model for identifying repeatable relationships in assurance history.

## 2. Core Question

**What patterns have historically preceded certain assurance outcomes?**

## 3. Pattern Semantics

| Term | Definition | Not |
|------|------------|-----|
| `pattern` | Recurring relationship in historical data | Prediction, finding, or requirement |
| `observation` | What was observed in the data | Diagnosis or root cause |
| `association` | What outcomes co-occur with this pattern | Causation |
| `confidence` | How strong the pattern is | Certainty |

## 4. Pattern Record Schema

```json
{
  "pattern_id": "string",
  "pattern_name": "string",
  "pattern_category": "evidence | planning | capability",
  "observations": ["string"],
  "historical_outcome": "string",
  "sample_size": "integer",
  "positive_cases": "integer",
  "confidence": "high | medium | low | insufficient",
  "observation_window": "string",
  "contradictions": "integer",
  "evidence_refs": ["string"],
  "explanation": "string",
  "advisory_only": true
}
```

## 5. Pattern Categories

### 5.1 Evidence Patterns

| Pattern | Observations | Associated Outcome |
|---------|--------------|-------------------|
| Stale Runtime Evidence | evidence_freshness = stale | Higher probability of qualification findings |
| Missing Provenance | provenance_incomplete | Higher probability of authority boundary issues |
| Low Evidence Coverage | coverage < partial | Higher probability of capability gaps |

### 5.2 Planning Patterns

| Pattern | Observations | Associated Outcome |
|---------|--------------|-------------------|
| Large Estimation Variance | planning_variance > 50% | Planning adjustment signal |
| Repeated Underestimation | consistent_underestimation | Future estimates should be adjusted |
| Runtime Change Overrun | runtime_changes + underestimation | Higher effort for runtime work |

### 5.3 Capability Patterns

| Pattern | Observations | Associated Outcome |
|---------|--------------|-------------------|
| Activation Without Evidence | capability_active + no_evidence | Coverage gap discovery |
| Rapid Capability Growth | capabilities_added > 3_in_30_days | Evidence coverage may lag |
| Authority Scope Expansion | scope_increased | May need requalification |

## 6. Confidence Rules

| Rule | Condition | Action |
|------|-----------|--------|
| Minimum sample | sample_size < 3 | Set confidence = insufficient |
| Contradiction penalty | contradictions > 0 | Reduce confidence by one level |
| High confidence | sample_size >= 10, contradictions = 0 | confidence = high |
| Medium confidence | sample_size >= 5 | confidence = medium |
| Low confidence | sample_size >= 3 | confidence = low |

## 7. Non-Authority Boundary

The pattern engine:

| May Do | May Not Do |
|--------|------------|
| Identify patterns | Create findings |
| Show associations | Claim causation |
| Reference evidence | Create work packets |
| Explain patterns | Assign priorities |
| Report confidence | Trigger remediation |
