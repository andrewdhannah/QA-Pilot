# Sprint — QA-PILOT-PREVENTIVE-RECOMMENDATIONS-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #241 (proposed)
**Lane:** assurance / recommendations
**Type:** Advisory recommendations — preventive assurance guidance
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Phase:** Phase 5 — Predictive Assurance
**Predecessor:** QA-PILOT-PREDICTIVE-RISK-SIGNALS-1 (#240, complete)

---

## 1. Purpose

Convert predictive signals into explainable, evidence-backed advisory recommendations.

**NOT:**
- "do this"
- "block this"
- "create this work"
- "approve this"

**Instead:**
"Given observed evidence, historical patterns, and projected conditions, this action may reduce future risk."

## 2. The Invariant

```
Observation → Qualification → Assessment → Prediction → Recommendation

Each step may reduce uncertainty.
No step may increase authority.
```

## 3. Recommendation Semantics

| Term | Definition | Not |
|------|------------|-----|
| `recommendation` | Suggested attention area | Requirement, finding, or approval |
| `rationale` | Why this recommendation exists | Root cause or diagnosis |
| `evidence_refs` | What data supports this | Proof of necessity |
| `confidence` | How certain the recommendation is | Authority to act |

## 4. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| REC-001 | Recommendations derive from signals | Every recommendation references a predictive signal | ✅ |
| REC-002 | Recommendations are explainable | Every recommendation has rationale and evidence_refs | ✅ |
| REC-003 | No recommendation creates work | Recommendations do not create work packets | ✅ |
| REC-004 | No recommendation creates findings | Recommendations do not create findings | ✅ |
| REC-005 | Stable systems produce no recommendation | qa-pilot: "no_recommendation" for stable state | ✅ |
| REC-006 | Confidence reflects signal maturity | Confidence based on signal confidence | ✅ |
| REC-007 | Advisory boundary preserved | All outputs advisory_only=true | ✅ |
| REC-008 | Existing validators pass | No regressions from #240 baseline | ✅ |

## 5. Guardrails

| Guardrail | Rule |
|-----------|------|
| No manufacturing work | System does not create work from recommendations |
| No authority expansion | Recommendations do not increase authority |
| Explainable | Every recommendation has human-readable rationale |
| Evidence-backed | Every recommendation references data |
| Conservative | Do not recommend without sufficient basis |
| Owner decides | Recommendations inform; Owner authorizes |

## 6. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-PREVENTIVE-RECOMMENDATIONS-1.md` | This sprint document |
| `contracts/assurance/preventive-recommendation-contract.md` | Recommendation contract |
| `docs/schemas/assurance/preventive-recommendation-v1.schema.json` | Recommendation schema |
| `scripts/generate-recommendations.py` | Recommendation engine |
| `data/assurance/preventive-recommendations/` | Recommendation records |

## 7. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #241 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 8. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-PREDICTIVE-RISK-SIGNALS-1 (#240) | ✅ Complete |
| Predictive signals | ✅ Working |
| Historical patterns | ✅ Working |
| Risk engine | ✅ Working |
| Fleet freshness | ✅ Working |
