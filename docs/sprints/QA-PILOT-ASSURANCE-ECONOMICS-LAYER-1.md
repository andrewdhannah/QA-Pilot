# Sprint — QA-PILOT-ASSURANCE-ECONOMICS-LAYER-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #237 (proposed)
**Lane:** assurance / economics
**Type:** Advisory resource prioritization — attention value scoring
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Phase:** Phase 4 — Operational Intelligence
**Predecessor:** CROSS-SYSTEM-CONTRACT-HARDENING (#236, complete)

---

## 1. Purpose

Introduce advisory resource prioritization by combining existing assurance signals into an attention value score.

**Given limited attention and resources, which areas provide the highest expected value for review?**

NOT: "What must be changed?" — that remains Owner authority.

## 2. The Model

```
Attention Value =
Risk Exposure
    × Change Frequency
    × Authority Impact
    × Confidence
    ÷ Estimated Effort
```

### 2.1 Components

| Component | Source | Meaning |
|-----------|--------|---------|
| Risk Exposure | Risk calibration (#230) | What could matter? |
| Change Frequency | Runtime evidence, sprint history | How often does this change? |
| Authority Impact | Declared authority scope | What is at stake? |
| Confidence | Evidence quality | How certain are we? |
| Estimated Effort | Planning accuracy | How much work to review? |

### 2.2 Scoring Logic

Higher attention value = more valuable to review first.

**Important:** Highest risk ≠ always first action.

Example:
| Item | Risk | Effort | Attention Value |
|------|------|--------|-----------------|
| A | High (80) | 20 days | Medium |
| B | Medium (50) | 2 hours | High |

The system recommends where review time may have the most leverage.

## 3. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| ECON-001 | Score calculation deterministic | Same inputs produce same attention value | ✅ |
| ECON-002 | All inputs trace to evidence | Every component has source and evidence_refs | ✅ |
| ECON-003 | Missing evidence lowers confidence | agent-bridge: no_evidence → confidence 0.4 | ✅ |
| ECON-004 | Recommendations remain advisory | advisory_only=true on all outputs | ✅ |
| ECON-005 | No work packets created automatically | Economics does not create work | ✅ |
| ECON-006 | No lifecycle mutation possible | Economics does not modify state | ✅ |
| ECON-007 | Explainability report generated | explain command shows full component breakdown | ✅ |
| ECON-008 | Round-trip validation | Economics produces correct output for known inputs | ✅ |
| ECON-009 | Existing validators pass | No regressions from #236 baseline | ✅ |

## 4. Guardrails

| Guardrail | Rule |
|-----------|------|
| Advisory only | Economics recommends; Owner decides |
| Evidence-backed | Every score traces to evidence |
| Deterministic | Same inputs → same score |
| Explainable | Every score has component breakdown |
| No automation | Economics does not create work or modify state |

## 5. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-ASSURANCE-ECONOMICS-LAYER-1.md` | This sprint document |
| `contracts/assurance/economic-prioritization-contract.md` | Economics contract |
| `scripts/prioritize-economics.py` | Economics engine |
| `data/assurance/economics-reports/` | Economics reports |

## 6. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #237 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 7. Dependencies

| Dependency | Status |
|------------|--------|
| CROSS-SYSTEM-CONTRACT-HARDENING (#236) | ✅ Complete |
| Risk engine | ✅ Working |
| Risk calibration | ✅ Working |
| Planning accuracy | ✅ Working |
| Fleet freshness | ✅ Working |
