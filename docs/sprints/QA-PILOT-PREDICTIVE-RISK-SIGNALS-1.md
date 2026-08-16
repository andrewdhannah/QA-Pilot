# Sprint — QA-PILOT-PREDICTIVE-RISK-SIGNALS-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #240 (proposed)
**Lane:** assurance / predictive
**Type:** Forward-looking risk indicators — predictive signals
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Phase:** Phase 5 — Predictive Assurance Readiness
**Predecessor:** QA-PILOT-HISTORICAL-PATTERN-MODELING-1 (#239, complete)

---

## 1. Purpose

Add forward-looking risk indicators derived from current assurance state, historical patterns, trajectory, and evidence confidence.

**The system answers:** "Given what we know today, what conditions may warrant future attention?"

**NOT:** "What will fail?"

## 2. The Separation

```
Current Risk Assessment          Predictive Risk Signal
        │                                │
        △                                △
  Observed state                  Projected condition
  Evidence-backed                 Pattern-derived
  Point-in-time                   Time-horizon
```

**Keep these separate.** Do not modify existing risk records.

## 3. Signal Model

### 3.1 Signal Record

```json
{
  "signal_id": "PRS-001",
  "project_id": "agent-bridge",
  "generated_at": "2026-08-16T06:00:00Z",
  "current_risk": 42,
  "projected_condition": "increased_attention_possible",
  "time_horizon": "30_days",
  "confidence": "low",
  "basis": [
    "risk_trajectory_increasing",
    "insufficient_pattern_data"
  ],
  "pattern_refs": [],
  "evidence_refs": [],
  "advisory_only": true
}
```

### 3.2 Signal Categories

| Category | Condition | Example |
|----------|-----------|---------|
| `emerging_risk` | Risk trajectory increasing | "Risk trend may increase" |
| `evidence_degradation` | Coverage decreasing | "Evidence freshness declining" |
| `planning_drift` | Repeated estimation variance | "Effort may exceed estimates" |

### 3.3 Confidence Levels

| Level | Condition | Meaning |
|-------|-----------|---------|
| `high` | Multiple patterns, large samples | Strong basis for projection |
| `medium` | Some patterns, moderate samples | Moderate basis |
| `low` | Few patterns, small samples | Limited basis |
| `insufficient` | No patterns or very small samples | Cannot project reliably |

## 4. Prediction Inputs

| Input | Source | Contribution |
|-------|--------|--------------|
| Risk trajectory | Trend analysis (#235) | Direction of risk |
| Pattern evidence | Pattern modeling (#239) | Historical associations |
| Evidence freshness | Fleet freshness (#224) | Confidence modifier |
| Planning variance | Planning accuracy (#229) | Planning risk signal |

## 5. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| PRS-001 | Current risk and projected risk are separate | Predictive signal is distinct object from risk assessment | ✅ |
| PRS-002 | Every signal has evidence references | Signal includes basis and pattern_refs | ✅ |
| PRS-003 | Confidence reflects pattern maturity | Confidence based on pattern confidence level | ✅ |
| PRS-004 | Insufficient patterns reduce confidence | When patterns insufficient, confidence = low | ✅ |
| PRS-005 | Signals cannot create findings | Signals are observation only. advisory_only=true. | ✅ |
| PRS-006 | Signals cannot create work packets | Signals do not create work | ✅ |
| PRS-007 | Signals are explainable | Every signal has human-readable basis | ✅ |
| PRS-008 | Historical replay produces same result | Deterministic signal generation | ✅ |
| PRS-009 | Authority boundary validation passes | No authority expansion | ✅ |
| PRS-010 | Existing validators pass | No regressions from #239 baseline | ✅ |

## 6. Guardrails

| Guardrail | Rule |
|-----------|------|
| Separate from risk | Predictive signals do not modify risk assessment |
| Evidence-backed | Every signal references data |
| Conservative | Default to low confidence when uncertain |
| Explainable | Every signal has human-readable basis |
| No authority expansion | Signals do not create findings or work |
| "No signal" is valid | Correct output may be "no actionable signals" |

## 7. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-PREDICTIVE-RISK-SIGNALS-1.md` | This sprint document |
| `contracts/assurance/predictive-risk-signal-contract.md` | Signal contract |
| `scripts/generate-predictive-signals.py` | Signal engine |
| `data/assurance/predictive-signals/` | Signal records |

## 8. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #240 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 9. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-HISTORICAL-PATTERN-MODELING-1 (#239) | ✅ Complete |
| Trend analysis | ✅ Working |
| Pattern engine | ✅ Working |
| Fleet freshness | ✅ Working |
| Planning accuracy | ✅ Working |
