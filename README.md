# Librarian-QA-Pilot

**A governed quality assurance framework for AI-assisted product work.**

QA Pilot is a fully offline QA onboarding training platform with a Windows 11-style desktop simulator — no server, no install, open `index.html` from `file://` and go. It provides structured QA lanes, evidence collection, manual verification scripts, readiness assessments, and a governed workbench for routing findings into bounded action.

> **Boundary:** QA Pilot produces findings, proposals, and evidence. It does not execute work, approve decisions, or confer authority.

---

## What QA Pilot does

QA Pilot is a separate, harness-governed add-on project with its own ledger, receipts, and governance. The Librarian provides the governance/custody infrastructure; QA Pilot retains implementation authority for its own QA surfaces.

The platform includes:

- **Fully offline browser app** — Windows 11-style desktop simulator, opens from `file://`
- **Diagnostic reports** — structured QA findings from governed evidence
- **Work proposals** — governed bridge from findings to bounded action (no execution authority)
- **Learning objects** — schema-validated lessons from QA evidence (v1)
- **Qualification framework** — review depth thresholds, decision receipts, action packets, handoff intakes, readiness posture
- **Assurance contracts** — canonical contract set extracted from adoption baselines
- **Test library** — regression, security, accessibility, UAT, and AI-behavior fixtures
- **Training system** — content model, package generator, validation engine, MCP surface

---

## Status

- **Project:** `qa-pilot`
- **Thesis:** A governed quality assurance framework for AI-assisted product work
- **Owner:** Andrew Hannah
- **Type:** add_on (harness_governed)
- **Profile:** lightweight-custody
- **Manifest:** `qa-pilot-manifest.json` (v1.3.0)
- **Authority:** advisory-only — no authority conferred

---

## Architecture

```text
QA Pilot Workbench
  ├── Diagnostic report intake
  ├── Risk-based review depth
  ├── Decision receipts (Owner)
  ├── Action packets
  ├── Handoff intake / review outcome
  ├── Owner action readiness
  └── Result packet export
```

## Key Surfaces

| Surface | Purpose |
|---------|---------|
| `browser-app/` | Fully offline Windows 11-style desktop simulator |
| `contracts/` | Canonical QA contracts and schemas |
| `docs/` | Governance, planning, sprints, reports, schemas |
| `fixtures/` | Validation fixtures (work proposals, scenarios) |
| `profiles/` | Project validation profiles |
| `receipts/` | Decision resolutions, custody, sprint closeouts |
| `scripts/` | Validators, CLI tools, test runners |
| `test-library/` | Regression / security / accessibility / UAT / AI fixtures |

## Governance

QA Pilot operates under the Librarian governance model:

- **Separate ledger** — QA Pilot sprints seal under the QA Pilot ledger
- **Separate receipts** — decision resolutions and custody records are project-local
- **Advisory-only** — QA Pilot may not confer or modify authority
- **Cross-project mutation** requires explicit handoff/custody authorization
- **Canonical contracts** — 5 assurance contracts with 10 universal invariants

## Quick Start

```bash
# Open the offline simulator (no server required)
open browser-app/index.html

# Run the validation pipeline
./scripts/qa-pilot-pipeline.sh

# Validate a learning object
python3 scripts/validate-learning-object.py fixtures/... 

# Run the workbench CLI
python3 scripts/qa_pilot_workbench.py --help
```

## Documentation

- `docs/governance/` — governance model, contracts, decision receipts
- `docs/planning/` — epics, capability plans, qualification architecture
- `docs/sprints/` — sealed sprint records
- `docs/schemas/` — JSON schemas for all contracts
- `FEATURE-STATUS.md` — feature verification status rollup
- `SESSION-HANDOFF.md` — session state handoff

---

## License

MIT
