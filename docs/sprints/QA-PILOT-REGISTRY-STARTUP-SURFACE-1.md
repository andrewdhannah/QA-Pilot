# Sprint Receipt — QA-PILOT-REGISTRY-STARTUP-SURFACE-1

**Status:** ✅ Sealed
**Type:** Governance / registry startup surface contract
**Lane:** governance
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** none

---

## Scope Satisfied

Added registry-aware pipeline posture reporting to the QA Pilot startup surface. The surface now presents a `Registry Posture` section in both text and JSON output, showing the governed layer registry state, PH-12/DR-3/DR-4/PLR/SR-8 alignment status, and a blocked/degraded/ready classification.

No subprocess validator calls — posture is determined directly from the registry data file and ledger, avoiding circular subprocess dependencies with the PH/DR/SR validators.

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| Updated startup surface | `scripts/qa_pilot_pipeline_startup_surface.py` | ✅ Registry Posture section, RSS rules |
| Updated valid fixture | `docs/examples/qa-pilot-epic-regression-startup-surface/valid-pipeline-report.json` | ✅ |
| Updated invalid fixtures | `docs/examples/qa-pilot-epic-regression-startup-surface/invalid-*.json` | ✅ |
| New fixture (clean) | `docs/examples/qa-pilot-registry-startup-surface/valid-clean-registry.json` | ✅ |
| New fixture (degraded) | `docs/examples/qa-pilot-registry-startup-surface/invalid-degraded-drift.json` | ✅ |
| New fixture (blocked) | `docs/examples/qa-pilot-registry-startup-surface/invalid-blocked-authority-claim.json` | ✅ |
| Test runner | `scripts/test-qa-pilot-registry-startup-surface.sh` | ✅ 20/20 pass |

## Changes to `qa_pilot_pipeline_startup_surface.py`

- Added `LAYER_REGISTRY_PATH` constant
- Added `gather_registry_posture()` — reads registry data and ledger, determines alignment without subprocess calls
- `gather_state()` now includes `registry_posture` in state dict
- `format_report()` shows `Registry Posture` section with layer count, latest layer, PH/DR/PLR/SR status icons, and classification
- `cmd_status()` shows registry layer count and classification
- JSON output includes `registry_posture` under `pipeline`
- Added 10 `RSS-*` validation rules (RSS-1 through RSS-10) for registry posture
- `validate_report()` validates registry posture fields

## Registry Posture Fields

| Field | Source | Description |
|-------|--------|-------------|
| `registry_layer_count` | Registry file | Number of sealed layers in registry |
| `latest_registry_layer` | Registry file | Latest layer (slot + sprint ID) |
| `registry_latest_matches_ledger` | Ledger | Whether registry latest matches ledger latest sealed head |
| `ph_12_status` | Inferred | pass if registry >= 16 layers, else fail |
| `dr_3_4_status` | Inferred | pass if registry matches ledger, else degraded |
| `plr_status` | Inferred | pass if registry has layers |
| `sr_8_status` | Inferred | pass if registry is healthy |
| `classification` | Computed | ready / degraded / blocked |

## Validation

| Suite | Result |
|-------|--------|
| Registry startup surface tests | ✅ 20/20 pass |
| Layer registry (PLR) | ✅ ALL CHECKS PASS |
| Legacy startup surface validator | ✅ ALL CHECKS PASS |
| MCP call loop guard | ✅ ALL CHECKS PASS |
| No Librarian files modified | ✅ |

## Authorization

Sprint authorized 2026-07-07 by Owner: "I authorize QA Pilot sprint QA-PILOT-REGISTRY-STARTUP-SURFACE-1."

Sealed 2026-07-07 by Owner: "I approve and seal QA Pilot sprint QA-PILOT-REGISTRY-STARTUP-SURFACE-1 as ledger #50."

**Next authorized sprint:** None — awaiting Owner direction.
