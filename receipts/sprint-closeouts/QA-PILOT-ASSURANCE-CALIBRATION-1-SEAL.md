# Sprint Seal — QA-PILOT-ASSURANCE-CALIBRATION-1

**Ledger:** #205
**Sealed:** 2026-07-20
**Epic:** EPIC-QA-PILOT-ASSURANCE-OPERATIONS-INTEGRATION-1 (Phase 3)

---

## Seal Record

Operational calibration complete and sealed. Produced a measurable operating baseline across all 6 calibration areas. The distinction between calibration findings (observations about operating behavior) and corrective actions (future improvements) is preserved. Assurance state unchanged — no governed lifecycle changes occurred during calibration.

## Acceptance

| Gate | Result |
|------|--------|
| CAL-1: Baseline operational metrics | ✅ PASS |
| CAL-2: False-positive categories identified | ✅ PASS |
| CAL-3: Stale-state causes classified | ✅ PASS |
| CAL-4: Owner queue quality measured | ✅ PASS |
| CAL-5: Evidence freshness thresholds validated | ✅ PASS |
| CAL-6: Projection accuracy verified | ✅ PASS |
| CAL-7: Calibration changes preserve invariants | ✅ PASS |
| CAL-8: No new authority paths introduced | ✅ PASS |

## Baseline Measurements

| Area | Finding |
|------|---------|
| False positives | 100% of 17 findings unacknowledged — no Owner feedback loop |
| Stale evidence | 15.4% stale (>300m), mean age 136m |
| Decision queue | 0 decisions recorded — no Owner engagement pattern |
| Evidence freshness | 8 fresh, 3 aging, 2 stale across 13 files |
| Projection accuracy | ✅ Dashboard/source match verified |
| Owner interaction | No interaction data captured yet |

## Deliverable

- `scripts/qa_pilot_assurance_calibration.py` — Calibration measurement script

## Next

Sprint 206 — QA-PILOT-ASSURANCE-GOVERNANCE-MATURITY-1 (Phase 4) — institutionalize the operating model.
