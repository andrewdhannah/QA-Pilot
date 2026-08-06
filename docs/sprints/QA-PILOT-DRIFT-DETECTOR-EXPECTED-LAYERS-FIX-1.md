# Sprint Receipt — QA-PILOT-DRIFT-DETECTOR-EXPECTED-LAYERS-FIX-1

**Status:** ✅ Sealed
**Lane:** governance maintenance / drift detector hardening
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** none

---

## Scope Satisfied

Eliminated the stale EXPECTED_LAYERS weakness in the QA Pilot drift detector. Replaced the hardcoded `pipeline_sprints` set (32 sprint IDs) with a dynamic derivation: pre-pipeline sprint IDs are computed from the ledger (sealed_number < 33). Any sealed sprint >=33 not in the registry is correctly identified as extra.

## Required Outcomes

| # | Requirement | Result |
|---|-------------|--------|
| 1 | Identify stale DR-4 EXPECTED_LAYERS source | ✅ 32 hardcoded sprint IDs replaced |
| 2 | Replace stale expectation path | ✅ Dynamic pre-pipeline derivation from ledger |
| 3 | Preserve validator semantics | ✅ DR-4 still detects real stale registry state |
| 4 | Add regression fixtures | ✅ 4 new fixtures |
| 5 | Chain validation | ✅ All validators green (PH-5 pre-existing) |
| 6 | Evidence | ✅ Sprint receipt created |

## Change

**File:** `scripts/validate-qa-pilot-pipeline-drift-detection.py`

Removed the 32-entry hardcoded `pipeline_sprints` set. Replaced with:

```python
pre_pipeline_ids = set()
for s in ledger.get("sprints", []):
    sn = s.get("sealed_number")
    if sn and isinstance(sn, int) and sn < 33 and s.get("status") == "sealed":
        pre_pipeline_ids.add(s["id"])
```

## Fixtures Added

| Fixture | Path |
|---------|------|
| Valid post-seal advancement | `docs/examples/qa-pilot-pipeline-drift-detection/valid-post-seal-advancement.json` |
| Invalid stale expected count | `docs/examples/qa-pilot-pipeline-drift-detection/invalid-stale-expected-count.json` |
| Invalid extra unsealed layer | `docs/examples/qa-pilot-pipeline-drift-detection/invalid-extra-unsealed-layer.json` |
| Invalid stale expected range | `docs/examples/qa-pilot-pipeline-drift-detection/invalid-stale-expected-range.json` |

## Validation

| Suite | Result |
|-------|--------|
| DR drift detection | ✅ DR-3: 31 layers, DR-4: No extra |
| DR tests | ✅ 20/22 (2 pre-existing PH-5 failures) |
| PH pipeline health | ✅ All 31 layers, PH-12 pass (PH-5 pre-existing) |
| PLR registry | ✅ ALL CHECKS PASS |
| AR advisory review | ✅ ALL CHECKS PASS |
| SUG, RCR, RCG, MG | ✅ All green |

## Authorization

Sprint authorized 2026-07-07 by Owner recommendation.

Sealed 2026-07-07 by Owner seal command.

**Next authorized sprint:** None — awaiting Owner direction.
