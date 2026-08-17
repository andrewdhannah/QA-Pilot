# Sprint — QA-PILOT-CLOSED-LOOP-OPTIMIZATION-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #245 (proposed)
**Lane:** assurance / optimization
**Type:** Closed-loop optimization — learning from outcomes
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Phase:** Phase 6 — Governed Improvement Activation
**Predecessor:** QA-PILOT-IMPROVEMENT-OUTCOME-MEASUREMENT-1 (#244, complete)

---

## 1. Purpose

Convert measured improvement outcomes into durable learning signals that improve future planning and qualification decisions, without allowing the learning system to directly alter governance authority or policy.

**This is the last architecture-building sprint before a deliberate phase review.**

## 2. The Closed Loop

```
Problem
   ↓
Assurance
   ↓
Recommendation
   ↓
Owner Decision
   ↓
Work Packet
   ↓
Execution
   ↓
Post-change Evidence
   ↓
Outcome Measurement
   ↓
Learning Signal
   ↓
Future Planning / Qualification
```

## 3. The Critical Distinction

**Do NOT make this:** "Outcomes automatically tune QA-Pilot."

**Make this:** "Outcomes produce evidence-backed optimization signals that future decision systems may consume."

```
Outcome
  ↓
Learning Signal
  ↓
  ├── Planning Insight
  ├── Qualification Insight
  ├── Risk Calibration Signal
  └── Recommendation Effectiveness Signal
          ↓
     Future Decision Context
```

**NOT:**
```
Outcome
  ↓
Automatic policy mutation
  ↓
New qualification rules
  ↓
New authority
```

## 4. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| CL-001 | Closed-loop contract defined | `contracts/assurance/closed-loop-optimization-contract.md` — learning categories, effectiveness signals, confidence rules | ✅ |
| CL-002 | Deterministic learning generation | Same outcome produces same learning signal | ✅ |
| CL-003 | Outcome-aware learning semantics | Different outcomes produce different signals (improved→effective, unchanged→not_effective, etc.) | ✅ |
| CL-004 | Planning consumption | Learning signals available for planning context | ✅ |
| CL-005 | Qualification consumption | Learning signals available for qualification context | ✅ |
| CL-006 | Effectiveness measurement | effectiveness command shows recommendation effectiveness breakdown | ✅ |
| CL-007 | Negative learning preserved | unchanged outcome produces "not_effective" signal with "observation" confidence | ✅ |
| CL-008 | Authority isolation | Learning signals do not modify governance, risk, qualification, permissions. advisory_only=true. | ✅ |
| CL-009 | Provenance round-trip | Signal references outcome_id, proposal_id, recommendation_id | ✅ |
| CL-010 | Sparse-data behavior | 1 outcome = "observation" confidence, 2-4 = "emerging_pattern", etc. | ✅ |
| CL-011 | Existing validators pass | No regressions from #244 baseline | ✅ |

## 5. Learning Confidence Rules

| Outcomes | Confidence | Meaning |
|----------|------------|---------|
| 1 | observation | Single data point |
| 2-4 | emerging_pattern | Early pattern |
| 5-9 | developing_pattern | Moderate evidence |
| >= 10 | established_pattern | Strong evidence |

## 6. Guardrails

| Guardrail | Rule |
|-----------|------|
| Learning is evidence | Signals are observations, not policies |
| No auto-tuning | Learning does not modify governance |
| Confidence reflects data | Sparse data = low confidence |
| Negative outcomes learn too | All outcomes produce signals |
| Provenance complete | Full traceability |
| Conservative | Don't over-interpret limited data |

## 7. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-CLOSED-LOOP-OPTIMIZATION-1.md` | This sprint document |
| `contracts/assurance/closed-loop-optimization-contract.md` | Closed-loop contract |
| `docs/schemas/assurance/learning-signal-v1.schema.json` | Learning signal schema |
| `scripts/generate-learning-signals.py` | Learning engine |
| `data/assurance/learning-signals/` | Learning signal records |

## 8. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #245 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 9. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-IMPROVEMENT-OUTCOME-MEASUREMENT-1 (#244) | ✅ Complete |
| Improvement outcomes | ✅ Available |
| Preventive recommendations | ✅ Available |
| Improvement proposals | ✅ Available |
| Risk engine | ✅ Working |
| Planning accuracy | ✅ Working |
