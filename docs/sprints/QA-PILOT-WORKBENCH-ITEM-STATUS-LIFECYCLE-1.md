# Sprint Receipt — QA-PILOT-WORKBENCH-ITEM-STATUS-LIFECYCLE-1

**Ledger #68**
**Lane:** governance
**Type:** substantive capability / workbench lifecycle
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** none
**Input dependencies:** QA-PILOT-WORKBENCH-ITEM-EVIDENCE-LINKING-1 (#67, sealed)

---

## Goal

Add a governed QA workbench item status lifecycle on top of the existing item model and evidence-linking layer. Support bounded local QA states without granting Owner approval, sprint seal authority, verification authority, or Librarian mutation.

## Deliverables

### Schema
- Updated `docs/schemas/qa-workbench-item.schema.json`:
  - 7 allowed statuses: `draft`, `open`, `triaged`, `evidence_attached`, `needs_review`, `deferred`, `resolved_locally`
  - New `lifecycle_history` array with append-only entries (8 fields each)

### CLI Commands (8 new)
- `status <item-id>` — show current status and allowed transitions
- `transition <item-id> <to-status> --reason REASON` — governed transition
- `history <item-id>` — show append-only lifecycle history
- `reopen <item-id> --reason REASON` — reopen resolved/deferred item
- `validate-transition <item-id> <to-status>` — read-only check
- Extended `create` — auto-adds initial lifecycle entry
- Extended `triage` — uses lifecycle transition internally
- Extended `list` — filter by status

### Allowed Transitions
```
draft → open
open → triaged
triaged → evidence_attached
evidence_attached → needs_review
needs_review → deferred | resolved_locally
deferred → open
resolved_locally → open (reopen with reason, min 10 chars)
```

### Lifecycle History Fields
- `from_status`, `to_status`, `transition_reason` (required, min 3 chars)
- `actor` (optional), `timestamp`, `evidence_refs` (optional)
- `advisory_only: true` (const)

### Validator Rules (lifecycle)
- **WL-1**: Lifecycle entries must have valid status values
- **WL-2**: `advisory_only: true` on each history entry
- **WL-3**: `transition_reason` required (min 3 chars)
- **WL-4**: Transition reasons must not claim approval/verification/seal/defect-acceptance
- **WL-5**: `resolved_locally` must not claim Owner approval
- **WL-6**: Final history entry `to_status` must match item status
- **WL-7**: History must maintain chronological chain (no gaps)

### Fixtures (14 new, 33 total)
- 8 valid lifecycle fixtures (draft, open, triaged, evidence_attached, needs_review, deferred, resolved_locally, reopened)
- 6 invalid lifecycle fixtures (unsupported status, missing reason, claiming approval, claiming verification, history gap, registry state in transition)

### Authority Boundaries Preserved
- `resolved_locally` does not mean Owner-approved
- `triaged` does not mean defect accepted
- `evidence_attached` does not mean verified
- `needs_review` does not force Owner action
- No status transition seals, approves, verifies, or mutates governance state

## Validation
- Test runner: **23/23 pass**
- Fixture validation: **33/33 pass** (17 valid + 16 invalid)
- Pipeline Health: ✅ ALL CHECKS PASS
- Pipeline Drift: ✅ NO DRIFT DETECTED
- PLR: ✅ ALL CHECKS PASS
- SRS: ✅ ALL SNAPSHOT CHECKS PASS

## Evidence
- Sprint receipt: `docs/sprints/QA-PILOT-WORKBENCH-ITEM-STATUS-LIFECYCLE-1.md`
- Updated schema: `docs/schemas/qa-workbench-item.schema.json`
- CLI: `scripts/qa_pilot_workbench.py`
- Validator: `scripts/validate-qa-pilot-workbench.py`
- Test results: `scripts/test-qa-pilot-workbench.sh (23/23 pass)`
- Fixtures: `docs/examples/qa-pilot-workbench/ (33 fixtures, 33/33 pass)`
- RCR receipt: `data/registry-change-receipts/RCR-ADD-LAYER-068.json`
- SUG receipt: `data/snapshot-update-gate-receipts/SUG-REFRESH-068.json`
