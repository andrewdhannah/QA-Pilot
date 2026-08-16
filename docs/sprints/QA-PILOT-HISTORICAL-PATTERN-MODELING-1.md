# Sprint — QA-PILOT-HISTORICAL-PATTERN-MODELING-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #239 (proposed)
**Lane:** assurance / patterns
**Type:** Historical pattern identification — explainable assurance patterns
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Phase:** Phase 5 — Predictive Assurance Readiness
**Predecessor:** QA-PILOT-ASSURANCE-PREDICTIVE-READINESS-1 (#238, complete)

---

## 1. Purpose

Identify repeatable relationships in existing assurance history without creating predictive decisions.

**The sprint answers:** "What patterns have historically preceded certain assurance outcomes?"

**NOT:** "What will happen and what should be done?"

## 2. The Design Constraint

Avoid creating a "model" too early. The current ecosystem advantage is explainability.

**Prefer:**
```
Observed: 8 similar cases
Outcome: 5 produced evidence findings
Confidence: Medium
```

**Over:**
```
Model predicts 73% failure probability
```

The first is auditable. The second introduces an opaque authority surface.

## 3. Pattern Model

### 3.1 Pattern Record

```json
{
  "pattern_id": "PAT-001",
  "pattern_name": "Capability Evidence Gap",
  "observations": [
    "runtime_evidence_gap",
    "high_change_frequency"
  ],
  "historical_outcome": "qualification_finding",
  "sample_size": 8,
  "positive_cases": 5,
  "confidence": "medium",
  "observation_window": "2026-01-01 to 2026-08-16",
  "evidence_refs": [],
  "advisory_only": true
}
```

### 3.2 Confidence Calculation

| Sample Size | Confidence |
|-------------|------------|
| >= 10 | High |
| 5-9 | Medium |
| 3-4 | Low |
| < 3 | Insufficient |

### 3.3 Pattern Categories

| Category | Examples | Source |
|----------|----------|--------|
| Evidence patterns | Stale evidence → findings | Fleet freshness, qualification |
| Planning patterns | Estimation variance → adjustment | Planning accuracy |
| Capability patterns | Activation without evidence → gaps | Capability discovery |

## 4. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| PATTERN-001 | Patterns derive only from existing evidence | Every pattern references qualification history, planning data, or capability discoveries | ✅ |
| PATTERN-002 | Minimum sample size enforced | Patterns with < 3 observations flagged as "insufficient" confidence | ✅ |
| PATTERN-003 | Correlation is not represented as causation | Output uses "associated with" language, not "causes" | ✅ |
| PATTERN-004 | Contradictory evidence lowers confidence | Confidence calculation includes contradiction penalty | ✅ |
| PATTERN-005 | Pattern output cannot create findings | Patterns are observation only. advisory_only=true. | ✅ |
| PATTERN-006 | Pattern output cannot create work packets | Patterns do not create work | ✅ |
| PATTERN-007 | Pattern provenance is replayable | Same data produces same patterns | ✅ |
| PATTERN-008 | Round-trip validation passes | Pattern engine produces correct output | ✅ |
| PATTERN-009 | Existing validators pass | No regressions from #238 baseline | ✅ |

## 5. Guardrails

| Guardrail | Rule |
|-----------|------|
| Explainable | Every pattern has human-readable explanation |
| Evidence-backed | Every pattern references specific data |
| No causation claims | Correlation only |
| No authority expansion | Patterns do not create findings or work |
| Conservative | Do not over-interpret limited data |
| Auditable | Full provenance for every pattern |

## 6. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-HISTORICAL-PATTERN-MODELING-1.md` | This sprint document |
| `contracts/assurance/historical-pattern-contract.md` | Pattern model contract |
| `scripts/discover-patterns.py` | Pattern engine |
| `data/assurance/historical-patterns/` | Pattern records |

## 7. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #239 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 8. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-ASSURANCE-PREDICTIVE-READINESS-1 (#238) | ✅ Complete |
| Qualification history | ✅ Available |
| Planning accuracy | ✅ Working |
| Capability discovery | ✅ Working |
| Fleet freshness | ✅ Working |
