# QA Pilot Pipeline Health Regression — Governance

**Status:** Agent work complete — pending Owner review
**Sprint:** QA-PILOT-PIPELINE-HEALTH-REGRESSION-1
**Boundary:** QA Pilot-local validation/regression surfaces only
**Librarian impact:** none
**Authority:** advisory-only

## Purpose

Add a whole-pipeline health regression harness that validates the sealed five-layer QA Pilot chain as one coherent advisory system:
#33 EP evidence → #34 TC tests → #35 QR results → #36 ERS suites → #37 startup surface

## PH Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| PH-1 | Pipeline has 5 sealed layers (#33-#37) | Ledger scan |
| PH-2 | Layer order is EP → TC → QR → ERS → surface | Sealed number comparison |
| PH-3 | Each layer references correct sprint ID | Ledger resolution |
| PH-4 | Each layer is advisory-only | Profile boundary check |
| PH-5 | All data stores accessible | Store index reads |
| PH-6 | Custody remains qa-pilot-local | Profile check |
| PH-7 | Librarian mutation authority is NONE | active_sprint null check |
| PH-8 | Startup surface agrees with ledger | Surface vs ledger comparison |
| PH-9 | No stale sealed-head claims | Max sealed ≤ #37 |
| PH-10 | No authority/promotion/seal claims | Field-level scan |
| PH-11 | Layer dependencies satisfied (order) | Sealed number monotonicity |
| PH-12 | No sixth packet layer exists | Sealed sprint whitelist |

## Usage

```
python3 scripts/validate-qa-pilot-pipeline-health-regression.py          # live mode
python3 scripts/validate-qa-pilot-pipeline-health-regression.py --fixture <path>  # fixture mode
```
