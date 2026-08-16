# Sprint — QA-PILOT-RISK-PRIORITIZATION-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #225 (proposed)
**Lane:** assurance / prioritization
**Type:** Advisory risk ranking model — deterministic, explainable, evidence-backed
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Predecessor:** QA-PILOT-FLEET-FRESHNESS-DISCOVERY-1 (#224, complete)

---

## 1. Purpose

Create an advisory risk ranking model over existing assurance observations.

Risk prioritization answers: **"Where should a human or agent look first?"**
It does NOT answer: **"What must be changed?"**

That remains Owner authority.

## 2. The Danger

At this stage, the danger is accidentally turning QA-Pilot from an evaluator into an authority system. Risk prioritization must remain advisory:

| Allowed | Forbidden |
|---------|-----------|
| "This project needs attention" | "This project must be fixed" |
| "Missing security coverage" | "Run security scan now" |
| "Repeated findings detected" | "Escalate to Owner" |
| Risk score with explanation | Autonomous action |

## 3. Risk Model

### 3.1 Score Formula

```
Risk Priority Score
    =
Impact Weight
    × Confidence Weight
    × Freshness Factor
    × Historical Pattern Factor
```

### 3.2 Impact Weight

Derived from authority scope:

| Authority Scope | Impact Weight | Meaning |
|-----------------|---------------|---------|
| `inform-only` | 1.0 | Low impact — observation only |
| `recommendation` | 2.0 | Medium impact — recommendations can influence |
| `mutation_capability` | 3.0 | High impact — can make changes |
| `canonical_state` | 4.0 | Critical impact — affects canonical state |

### 3.3 Confidence Weight

Derived from evidence quality:

| Evidence Quality | Confidence Weight | Meaning |
|------------------|-------------------|---------|
| Qualified evidence | 1.0 | High confidence — evidence is validated |
| Partial evidence | 0.7 | Medium confidence — some validation |
| Unknown | 0.4 | Low confidence — cannot validate |

### 3.4 Freshness Factor

Represents uncertainty, not quality:

| Freshness State | Factor | Meaning |
|-----------------|--------|---------|
| `current` | 1.0 | Evidence is recent — low uncertainty |
| `aging` | 1.2 | Evidence is getting old — moderate uncertainty |
| `stale` | 1.5 | Evidence is outdated — high uncertainty |
| `unknown` | 2.0 | Cannot determine freshness — maximum uncertainty |

**Rule:** Higher factor = more attention needed. Stale evidence needs more attention not because it's bad, but because we don't know if it's still valid.

### 3.5 Historical Pattern Factor

Uses the learning loop:

| Pattern | Factor | Meaning |
|---------|--------|---------|
| No findings | 1.0 | Clean history |
| Repeated findings | 1.5 | Pattern detected — needs attention |
| Unresolved findings | 2.0 | Open issues — needs immediate attention |

### 3.6 Risk Bands

| Score Range | Band | Meaning |
|-------------|------|---------|
| 0 – 20 | `healthy` | No attention needed |
| 21 – 50 | `monitor` | Watch for changes |
| 51 – 80 | `attention_required` | Human should review |
| 81 – 100 | `urgent` | Immediate attention needed |

## 4. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| RISK-001 | Risk calculation is deterministic | `scripts/prioritize-risk.py` — same evidence produces same score. Verified by running fleet assessment twice. | ✅ |
| RISK-002 | Every score has evidence provenance | Risk assessment includes factors breakdown, drivers, and evidence_refs. Explain command provides full reasoning. | ✅ |
| RISK-003 | Risk ≠ failure | High risk means "needs attention," not "failed." Output explicitly states: "This is an advisory ranking only." | ✅ |
| RISK-004 | Authority boundary preserved | No dispatch, remediation, finding closure, or owner decisions. authority_boundary field explicitly set to all false. | ✅ |
| RISK-005 | Historical findings feed correctly | Historical pattern factor connects qualification results to risk score. | ✅ |
| RISK-006 | Multi-project validation | QA-Pilot (10/100, healthy) and Librarian (10/100, healthy) assessed independently. No cross-project contamination. | ✅ |
| RISK-007 | CAG activation | Capability activated through: implemented + validated + evidence-backed + registered + projected + discoverable + authority-bounded | ✅ |
| RISK-008 | LINK readiness | `get_project_risk_state()` and `get_fleet_risk_state()` interfaces defined in risk model contract. No LINK integration. | ✅ |
| RISK-009 | Existing validators pass | No regressions from #224 baseline | ✅ |

## 5. Guardrails

| Guardrail | Rule |
|-----------|------|
| Advisory ranking only | Risk scores inform attention, they do not mandate action |
| Deterministic | Same inputs → same outputs, always |
| Explainable | Every score has drivers and evidence refs |
| Evidence-backed | Risk assessment references specific evidence records |
| No authority escalation | Risk engine does not dispatch, remediate, or decide |
| Historical findings are inputs | Learning loop feeds risk model, not the other way around |

## 6. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-RISK-PRIORITIZATION-1.md` | This sprint document |
| `contracts/assurance/risk-prioritization-model.md` | Risk model contract |
| `contracts/assurance/risk-prioritization-link-readiness.md` | LINK readiness interface for risk |
| `scripts/prioritize-risk.py` | Risk engine |
| `data/runtime-evidence/risk-assessments.json` | Risk assessment results |

## 7. Files to Modify

| File | Change |
|------|--------|
| `data/runtime-evidence/discovery-projection.json` | Extend with risk_band and attention_reasons |
| `project-state/sprint-ledger.json` | Add entry #225 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 8. Sequencing After This Sprint

```
#221 Capture          ✅
#222 Qualification    ✅
#223 Federation       ✅
#224 Freshness        ✅
#225 Risk Priority    ← THIS SPRINT
#226 ???              (continuous qualification OR LINK integration)
```

## 9. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-FLEET-FRESHNESS-DISCOVERY-1 (#224) | ✅ Complete |
| Fleet freshness discovery engine | ✅ Working |
| Discovery projection | ✅ Exists |
| Qualification results | ✅ Available |
| Learning loop | ✅ Exists (#220) |
