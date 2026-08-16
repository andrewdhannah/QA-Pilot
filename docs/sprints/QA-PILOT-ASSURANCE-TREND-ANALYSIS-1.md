# Sprint — QA-PILOT-ASSURANCE-TREND-ANALYSIS-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #235 (proposed)
**Lane:** assurance / trends
**Type:** Historical interpretation — temporal assurance analysis
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Phase:** Phase 4 — Operational Intelligence
**Predecessor:** QA-PILOT-ASSURANCE-OBSERVATORY-1 (#234, complete)

---

## 1. Purpose

Add historical interpretation of assurance state without changing qualification, risk, or authority behavior.

The system should identify:
- Improvement
- Degradation
- Stability
- Unresolved persistence
- Emerging risk patterns

while remaining advisory.

## 2. The Distinction

```
Observatory answers:
"What is the state?"

Trend Analysis answers:
"Where is the state moving?"
```

These are different capabilities.

## 3. Trend Model

### 3.1 Trend Classifications

| Trend | Condition | Meaning |
|-------|-----------|---------|
| `improving` | Current better than previous | State is getting better |
| `stable` | Current similar to previous | State is unchanged |
| `degrading` | Current worse than previous | State is getting worse |
| `insufficient_data` | Not enough history | Cannot determine trend |

### 3.2 Trend Record

```json
{
  "trend_id": "TR-001",
  "project_id": "librarian",
  "metric": "risk_score",
  "window_start": "2026-07-16T00:00:00Z",
  "window_end": "2026-08-16T00:00:00Z",
  "previous_value": 32,
  "current_value": 18,
  "direction": "improving",
  "confidence": "high",
  "delta": -14,
  "delta_pct": -43.8,
  "evidence_refs": [],
  "advisory_only": true
}
```

### 3.3 Initial Metrics

| Metric | Source | What It Shows |
|--------|--------|---------------|
| Risk trend | Risk history | Is risk increasing or decreasing? |
| Evidence coverage trend | Fleet freshness | Is coverage improving or degrading? |
| Capability gap trend | Capability discovery | Are gaps being addressed? |

## 4. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| TREND-001 | Historical state can be reconstructed | `analyze-trends.py` queries observatory reports for historical data | ✅ |
| TREND-002 | Trend calculation is deterministic | Same historical data produces same trend (stable with 2 similar data points) | ✅ |
| TREND-003 | Missing history produces insufficient_data | With 1 data point, returns "insufficient_data" | ✅ |
| TREND-004 | Trend records preserve provenance | Every trend has window_start, window_end, evidence_refs | ✅ |
| TREND-005 | No trend output grants authority | Trend is observation, not recommendation. advisory_only=true. | ✅ |
| TREND-006 | Fleet trends aggregate without merging | Each project has independent trends | ✅ |
| TREND-007 | Advisory projection consumed by observatory | Trend data available for observatory consumption | ✅ |
| TREND-008 | Round-trip validation | Trend engine produces correct output for known inputs | ✅ |
| TREND-009 | Existing validators pass | No regressions from #234 baseline | ✅ |

## 5. Guardrails

| Guardrail | Rule |
|-----------|------|
| Observation only | Trend is "where is it moving?" not "what should we do?" |
| No remediation | Trend does not create work |
| No priority assignment | Trend does not rank projects |
| Deterministic | Same inputs → same trends |
| Evidence-backed | Every trend references data |
| Conservative | Do not over-interpret noisy data |

## 6. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-ASSURANCE-TREND-ANALYSIS-1.md` | This sprint document |
| `contracts/assurance/assurance-trend-contract.md` | Trend contract |
| `scripts/analyze-trends.py` | Trend engine |
| `data/assurance/trend-records/` | Trend records |

## 7. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #235 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 8. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-ASSURANCE-OBSERVATORY-1 (#234) | ✅ Complete |
| Observatory reports | ✅ Available |
| Risk assessments | ✅ Available |
| Capability discoveries | ✅ Available |
| Fleet freshness discovery | ✅ Working |
