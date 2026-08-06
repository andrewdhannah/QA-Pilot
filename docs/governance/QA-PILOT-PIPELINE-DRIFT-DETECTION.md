# QA Pilot Pipeline Drift Detection — Governance

**Status:** Agent work complete — pending Owner review
**Sprint:** QA-PILOT-PIPELINE-DRIFT-DETECTION-1
**Boundary:** QA Pilot-local validation/drift-report surfaces only
**Librarian impact:** none
**Authority:** advisory-only

## Purpose

Detect whether QA Pilot pipeline state has diverged across ledger, startup surface, stores, validators, and boundary fields after future edits.

## DR Rules

| Rule | Description |
|------|-------------|
| DR-1 | Ledger/startup sealed-head match |
| DR-2 | Active sprint matches across ledger, profile, status |
| DR-3 | All 6 sealed layers (#33-#38) present |
| DR-4 | No unexpected extra packet layers |
| DR-5 | EP/TC/QR/ERS stores internally consistent |
| DR-6 | Startup surface output not stale |
| DR-7 | PH validator agrees with pipeline state |
| DR-8 | Posture/custody/mutation fields unchanged |
| DR-9 | No authority/promotion/seal claims |
| DR-10 | Report is bounded and advisory-only |

## Usage

```
python3 scripts/validate-qa-pilot-pipeline-drift-detection.py             # live mode
python3 scripts/validate-qa-pilot-pipeline-drift-detection.py --report    # formatted report
python3 scripts/validate-qa-pilot-pipeline-drift-detection.py --fixture <path>  # fixture
```

## Forbidden

- Auto-repairing drift
- Creating a new packet layer
- Mutating Librarian state
- Creating seal, promotion, canonical-truth, or ingest authority
