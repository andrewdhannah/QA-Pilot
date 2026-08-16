# Sprint — QA-PILOT-ASSURANCE-OBSERVATORY-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #234 (proposed)
**Lane:** assurance / observatory
**Type:** Decision surface — assurance ecosystem awareness
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Phase:** Phase 4 — Operational Intelligence
**Predecessor:** QA-PILOT-CAPABILITY-DISCOVERY-1 (#233, complete)

---

## 1. Purpose

Create the decision surface that consumes the assurance ecosystem outputs.

**The natural consumer of everything built through #221–#233.**

Converts raw assurance data into human-decidable project health views.

## 2. The Transition

Before this sprint:
- QA-Pilot evaluates systems

After this sprint:
- QA-Pilot provides governed ecosystem awareness

## 3. Observatory Architecture

```
Assurance Ecosystem Outputs
          │
          △
    ┌─────┴─────┐
    │           │
    ▼           ▼
Qualification Risk
    │           │
    ▼           △
Capability Discovery
    │           │
    △           │
Planning Accuracy
    │           │
    △           │
Freshness State
    │           │
    └─────┬─────┘
          │
          △
    Observatory
          │
          △
    Project Health
          │
          ├── Evidence Coverage
          ├── Qualification State
          ├── Risk Trend
          ├── Capability Gaps
          ├── Planning Accuracy
          └── Recommended Attention
```

## 4. Observatory Output

```json
{
  "observatory_id": "OBS-20260816",
  "generated_at": "2026-08-16T05:15:00Z",
  "fleet_summary": {
    "total_projects": 3,
    "health_distribution": {
      "healthy": 2,
      "attention_needed": 1,
      "critical": 0
    },
    "overall_status": "operational"
  },
  "projects": [
    {
      "project_id": "qa-pilot",
      "health": "healthy",
      "evidence_coverage": "minimal",
      "qualification_state": "pass",
      "risk_band": "healthy",
      "risk_score": 10,
      "capability_gaps": 0,
      "planning_accuracy": "no_data",
      "recommended_attention": "none"
    }
  ],
  "trends": {
    "risk_trend": "stable",
    "freshness_trend": "stable",
    "coverage_trend": "stable"
  },
  "attention_needed": [],
  "advisory_only": true
}
```

## 5. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| OBS-001 | Aggregate assurance state from all onboarded projects | `observe-assurance.py fleet` aggregates 3 projects | ✅ |
| OBS-002 | Show qualification freshness | Each project shows qualification state (pass/finding/untested) | ✅ |
| OBS-003 | Show risk trends | Fleet-wide trend computation available | ✅ |
| OBS-004 | Show capability gaps | agent-bridge shows 2 capability gaps from discovery | ✅ |
| OBS-005 | Show planning accuracy trends | Planning accuracy field included (no_data for now) | ✅ |
| OBS-006 | Preserve advisory-only boundary | Output is observation and recommendation. advisory_only=true. | ✅ |
| OBS-007 | Generate explainable projections | Every health assessment includes health_rationale | ✅ |
| OBS-008 | Existing validators pass | No regressions from #233 baseline | ✅ |

## 6. Guardrails

| Guardrail | Rule |
|-----------|------|
| Advisory only | Observatory observes; it does not decide |
| Read-only | No mutation of assurance state |
| Explainable | Every health assessment has rationale |
| Deterministic | Same inputs → same observatory output |
| Conservative | Do not over-report attention needs |

## 7. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-ASSURANCE-OBSERVATORY-1.md` | This sprint document |
| `contracts/assurance/observatory-contract.md` | Observatory contract |
| `scripts/observe-assurance.py` | Observatory engine |
| `data/assurance/observatory-reports/` | Observatory reports |

## 8. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #234 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 9. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-CAPABILITY-DISCOVERY-1 (#233) | ✅ Complete |
| All assurance engine components | ✅ Working |
| Fleet freshness discovery | ✅ Working |
| Risk engine | ✅ Working |
| Planning accuracy measurement | ✅ Working |
| Capability discovery | ✅ Working |
