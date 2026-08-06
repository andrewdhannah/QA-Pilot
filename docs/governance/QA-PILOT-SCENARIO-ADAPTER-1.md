# QA Pilot Scenario Adapter — QA-PILOT-SCENARIO-ADAPTER-1

**Sprint:** QA-PILOT-SCENARIO-ADAPTER-1
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review
**Authority:** Advisory only. Evaluates understanding, not system correctness.

## 1. Purpose

Bridge the governed Learning Object pipeline to the V1.5 testing and certification engine (`scoring.js`). Reconnect the recovered testing capability to the governed evidence architecture.

## 2. Architecture

```
SDK Findings
      ↓
Learning Object (exercise + certification criteria)
      ↓
Scenario Adapter
      ├── evaluate() — V1.5 scoring logic (pure function)
      ├── evaluate-from-lo() — scoring from learning objects
      └── scoring with provenance metadata
      ↓
Validation Result (advisory, provenance-tracked)
```

## 3. End-to-End Pipeline

```
Evidence Plane finding (F-0001, EV-GOV-002)
      ↓
Learning Object (LO-EV-GOV-002-0001)
      │  exercise.scenario_id = "cursor-freshness-scenario"
      │  certification.passing_score = 80
      ▼
Scenario Adapter
      │  evaluate_from_lo(lo_id, bugs_found, bugs_logged)
      │  → { score, percentage, passed, missed_bugs, summary }
      ▼
Validation Result
      │  provenance: advisory, no_authority_conferred
      │  certification_criteria: from learning object
```

## 4. Results

| Metric | Value |
|--------|-------|
| V1.5 scenarios adapted | 5 (capstone-001, capstone-002, case-002, scenario-case-003, scenarios-bug-001) |
| Learning objects supported | All generated LOs (via `evaluate-from-lo`) |
| Scoring model | Port of `scoring.js` — pure function, no side effects |
| Maximum score per bug | 3 (1 found + 1 complete report + 1 correct AC ref) |
| Test runner | 10/10 pass ✅ |

## 5. Files

| File | Description |
|---|---|
| `scripts/qa_pilot_scenario_adapter.py` | Adapter — list, load, evaluate, evaluate-from-lo |
| `scripts/test-qa-pilot-scenario-adapter.sh` | 10 tests |
| `docs/governance/QA-PILOT-SCENARIO-ADAPTER-1.md` | This governance document |

## 6. Next

| Phase | Work Order |
|---|---|
| Phase 3 | QA-PILOT-AI-QUALIFICATION-1 |
