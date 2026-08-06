# QA-PILOT-GOVERNANCE-VALIDATOR-REPAIR-1 — Governance Validator Repair

**Type:** infrastructure / evidence integrity
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** governance
**Boundary:** QA Pilot-local
**Librarian impact:** none
**Dependencies:** DWR-005 sealed (identity baseline closed)

---

## Purpose

Restore governance validator execution. The baseline audit (ledger #166) identified 17 validators with execution issues (exit codes 1 or 2). These are dependency/configuration issues, not runtime defects. Repairing them restores validation confidence before product-surface reassessment.

**Why this is first:** If visual parity or I18N work produces evidence while validators are partially broken, future reviewers may have to question whether failures are product issues or validation environment issues.

---

## Scope

### Included

| # | Area | Action |
|---|------|--------|
| 1 | Failing validators | Investigate root cause, fix dependency/configuration issues |
| 2 | Rerun validation suite | Execute all validators, record pass/fail |
| 3 | Validation confidence | Confirm restored validator execution |

### Explicit Non-Scope

This sprint must not:

- Modify product behavior
- Change governance contracts
- Alter migration history
- Modify canonical decision records
- Expand to feature work

---

## Failing Validators (From Baseline Audit #166)

| # | Validator | Exit Code | Category |
|---|-----------|-----------|----------|
| 1 | validate-qa-pilot-action-handoff-intake.py | 2 | Workbench chain |
| 2 | validate-qa-pilot-handoff-review-outcome.py | 2 | Workbench chain |
| 3 | validate-qa-pilot-owner-action-packet-export.py | 2 | Workbench chain |
| 4 | validate-qa-pilot-owner-action-packet.py | 2 | Workbench chain |
| 5 | validate-qa-pilot-owner-action-readiness.py | 2 | Workbench chain |
| 6 | validate-qa-pilot-pipeline-health-regression.py | 1 | Pipeline health |
| 7 | validate-qa-pilot-pipeline-layer-registry.py | 1 | Pipeline layer registry |
| 8 | validate-qa-pilot-qualification.py | 2 | Qualification chain |
| 9 | validate-qa-pilot-registry-change-receipt-backfill.py | 1 | Registry receipts |
| 10 | validate-qa-pilot-review-decision-receipt.py | 2 | Review chain |
| 11 | validate-qa-pilot-review-decision-summary.py | 2 | Review chain |
| 12 | validate-qa-pilot-review-depth-thresholds-decision-packet-startup-surface.py | 2 | Review depth |
| 13 | validate-qa-pilot-review-depth-thresholds-decision-packet.py | 2 | Review depth |
| 14 | validate-qa-pilot-review-depth-thresholds.py | 2 | Review depth |
| 15 | validate-qa-pilot-seal-authority-gate.py | 2 | Seal authority |
| 16 | validate-qa-pilot-startup-surface-regression-snapshot.py | 1 | Startup surface |
| 17 | validate-qa-pilot-workbench.py | 2 | Workbench |

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| VR-1 | Root cause identified for each failing validator |
| VR-2 | Fixes applied (dependency/config changes only) |
| VR-3 | All 17 previously failing validators now execute |
| VR-4 | Validation suite rerun with updated results |
| VR-5 | No product behavior changes introduced |
| VR-6 | Evidence produced |

---

## Evidence Contract

This sprint produces exactly:

```
docs/sprints/QA-PILOT-GOVERNANCE-VALIDATOR-REPAIR-1-EVIDENCE.md
```

The evidence document contains:

| # | Section | Purpose |
|---|---------|---------|
| 1 | Root cause analysis | Why each validator failed |
| 2 | Fixes applied | What was changed |
| 3 | Rerun results | Updated pass/fail status |
| 4 | Validation confidence | Assessment of restored validator execution |
| 5 | Scope compliance | Confirmation of non-scope adherence |

---

## Sprint Boundary

| Constraint | Value |
|------------|-------|
| Project boundary | QA Pilot-local |
| Librarian mutation | none |
| Cross-project mutation | none |
| File scope | `scripts/validate-*.py`, `scripts/test-*.sh`, dependencies |
| Write scope | Validator fixes, evidence document |
| Read-only scope | All governance metadata |

---

**Status:** ✅ AUTHORIZED — Owner-authorized 2026-07-20
**Authorized by:** Andrew Hannah
**Ledger entry:** #168 (authorized)
