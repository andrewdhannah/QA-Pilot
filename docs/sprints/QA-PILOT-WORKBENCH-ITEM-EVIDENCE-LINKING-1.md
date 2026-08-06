# Sprint Receipt — QA-PILOT-WORKBENCH-ITEM-EVIDENCE-LINKING-1

**Ledger #67**
**Lane:** governance
**Type:** substantive capability / workbench evidence layer
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** none
**Input dependencies:** QA-PILOT-WORKBENCH-CAPABILITY-FOUNDATION-1 (#66, sealed)

---

## Goal

Extend QA workbench items so they can attach, validate, list, and summarize structured evidence references against QA Pilot-local evidence stores without claiming verification, approval, seal authority, or Librarian mutation.

## Deliverables

### Evidence Link Schema
- `docs/schemas/qa-workbench-evidence-link.schema.json` — 12 fields, 6 required
- Inline `evidence_links` array added to `docs/schemas/qa-workbench-item.schema.json`

### CLI Operations (8 new commands)
- `attach` — Attach a structured evidence link (JSON file) to an existing QA item
- `detach` — Detach an evidence link by ID from a QA item
- `list-refs` — List all evidence links on a QA item
- `validate-refs` — Validate all evidence links on a QA item
- `summarize` — Summarize evidence posture for a QA item
- `list` extended with `--evidence-type` filter

### Validator Rules Extended
- **WB-9**: evidence links must validate individually against schema
- **WB-10**: evidence link `attachment_reason` must not claim authority
- **WB-11**: evidence links must not reference Librarian paths
- **WB-12**: evidence links must not carry registry/RCR/SRS state fields
- **EL-1**: No duplicate `evidence_link_id` values on same item
- **EL-2**: `advisory_only` must be `true` on every link
- **EL-3**: `custody` must be `qa-pilot-local` on every link
- **EL-4**: `authority_note` must match standard disclaimer
- **EL-5**: `evidence_type` must be a supported value

### Fixtures (10 new)
- 5 valid:
  - `valid-qa-item-one-evidence-link.json` — item with one evidence link
  - `valid-qa-item-multiple-evidence-links.json` — item with 3 evidence links
  - `valid-qa-item-validator-output-link.json` — item linking validator output
  - `valid-qa-item-arp-link.json` — item linking ARP packet
  - `valid-qa-item-train-sim-link.json` — item linking training sim result
- 5 invalid:
  - `invalid-missing-evidence-link-id.json` — link missing required ID
  - `invalid-external-custody.json` — link claiming Librarian custody
  - `invalid-authority-claiming-evidence-note.json` — link claiming authority
  - `invalid-evidence-ref-mutates-registry.json` — link with registry state
  - `invalid-unsupported-evidence-type.json` — link with invalid type

### Authority Boundaries Preserved
- Evidence attachment does not prove defect validity
- Evidence attachment does not imply Owner approval
- Evidence attachment does not seal, verify, or close a QA item
- No registry/RCR/SRS/SUG mutation beyond standard post-seal maintenance
- All links enforce `advisory_only: true`, `custody: qa-pilot-local`

## Validation
- Test runner: **16/16 pass**
- Fixture validation: **19/19 pass** (9 valid + 10 invalid)
- Pipeline Health: **ALL CHECKS PASS**
- Pipeline Drift: **NO DRIFT DETECTED**
- PLR: **ALL CHECKS PASS**
- SRS: **ALL SNAPSHOT CHECKS PASS**

## Evidence
- Sprint receipt: `docs/sprints/QA-PILOT-WORKBENCH-ITEM-EVIDENCE-LINKING-1.md`
- Evidence link schema: `docs/schemas/qa-workbench-evidence-link.schema.json`
- Extended CLI: `scripts/qa_pilot_workbench.py`
- Extended validator: `scripts/validate-qa-pilot-workbench.py`
- Test results: `scripts/test-qa-pilot-workbench.sh (16/16 pass)`
- Fixtures: `docs/examples/qa-pilot-workbench/ (19 fixtures, 19/19 pass)`
- RCR receipt: `data/registry-change-receipts/RCR-ADD-LAYER-067.json`
- SUG receipt: `data/snapshot-update-gate-receipts/SUG-REFRESH-067.json`
