# QA Pilot Pipeline Recovery Diagnostics — Governance

**Status:** Agent work complete — pending Owner review
**Sprint:** QA-PILOT-PIPELINE-RECOVERY-DIAGNOSTICS-1
**Boundary:** QA Pilot-local diagnostic/report surfaces only
**Librarian impact:** none
**Authority:** advisory-only

## Purpose

Classify drift failures by affected layer, identify likely cause, and present bounded Owner-facing recovery options. Diagnostic-only — does not auto-repair.

## Usage

```
python3 scripts/qa_pilot_pipeline_recovery_diagnostics.py                # JSON output
python3 scripts/qa_pilot_pipeline_recovery_diagnostics.py --report       # Formatted report
python3 scripts/qa_pilot_pipeline_recovery_diagnostics.py --fixture <p>  # Fixture mode
```

## Forbidden

- Auto-repairing drift
- Mutating canonical state
- Creating a new packet layer
- Creating seal, promotion, canonical-truth, or ingesting authority
- Mutating Librarian state
