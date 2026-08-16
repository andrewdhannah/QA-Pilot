# Librarian-QA-Pilot

**A governed quality assurance framework for AI-assisted product work.**

QA Pilot is a contract-governed assurance subsystem that transforms findings into governed lifecycle decisions through evidence-backed validation, risk prioritization, Owner decision control, and continuous assurance management. It operates as a separate, harness-governed add-on project with its own ledger, receipts, and governance under the Librarian.

> **Boundary:** QA Pilot produces findings, proposals, and evidence. It does not execute work, approve decisions, or confer authority.

---

## Current State

| Field | Value |
|-------|-------|
| **Project** | `qa-pilot` |
| **Phase** | Phase 5 — Predictive Assurance Readiness |
| **Sealed sprints** | 240+ |
| **Latest sealed** | #240 QA-PILOT-PREDICTIVE-RISK-SIGNALS-1 |
| **Active epic** | EPIC-ASSURANCE-CONTRACT-EVOLUTION-1 (COMPLETE) |
| **Authority** | advisory-only — no authority conferred |
| **Governance** | harness_governed, lightweight-custody |

**Architecture milestone:** The governed improvement loop is proven (sprint #220). The system has crossed from "build missing primitives" into "system integration and operationalization."

---

## What QA Pilot Does

### Decision-Support Stack

```
State → Trajectory → Risk → Value of Attention → Human Decision
```

The complete decision-support stack is operational:

| Layer | Capability | Status |
|-------|-----------|--------|
| **Evidence** | Runtime evidence ingestion, qualification, federation | ✅ Complete |
| **Qualification** | Schema, pipeline, execution, review surface, roundtrip | ✅ Complete |
| **Learning** | Regression learning loop, pattern modeling | ✅ Complete |
| **Discovery** | Fleet freshness, capability discovery, observatory | ✅ Complete |
| **Risk** | Risk prioritization, calibration, predictive signals | ✅ Complete |
| **Economics** | Attention value scoring, economic prioritization | ✅ Complete |
| **Planning** | Planning accuracy measurement, LINK integration | ✅ Complete |
| **Predictive** | Predictive readiness, historical patterns, risk signals | ✅ Complete |
| **Preventive** | Preventive recommendations | ⏳ Next |

### Assurance Contracts

27 canonical contracts under `contracts/assurance/` covering:

- **Core:** Evidence state, finding derivation, remediation lifecycle, owner decision boundary, regression lifecycle
- **Qualification:** Continuous qualification, adaptive profiles, qualification baseline
- **Discovery:** Fleet freshness policy, capability discovery, observatory, projection
- **Risk:** Risk prioritization model, predictive risk signals, preventive recommendations
- **Economics:** Economic prioritization, planning accuracy, historical patterns
- **Runtime:** Runtime evidence ingestion, federation, validation
- **Integration:** LINK readiness, cross-system boundary matrix, improvement proposals

### Key Capabilities

- **207 sprint records** with full governance chain
- **194 Python scripts** and **89 shell scripts** for validation, CLI tools, and test runners
- **75 validators** and **83 test runners**
- **Qualification substrate** — 5-sprint closed loop: discover → collect → validate → evaluate → lifecycle → review → status → startup → decision → lineage
- **Multi-project evidence federation** — per-project isolation, canonical identity, adapter contracts
- **Cross-system contracts** — 5-system boundary matrix, 4 formalized contracts

---

## Architecture

```text
QA Pilot Assurance Engine
├── Governance Substrate
│   ├── Ledger & receipts
│   ├── Custody enforcement
│   └── Write-custody controls
├── Evidence Layer
│   ├── MCP evidence intake
│   ├── Runtime evidence ingestion
│   ├── Evidence federation
│   └── Evidence checklists
├── Qualification Layer
│   ├── Qualification schema
│   ├── Evidence pipeline
│   ├── Execution engine
│   ├── Review surface
│   └── Adaptive profiles
├── Learning Layer
│   ├── Regression learning loop
│   ├── Pattern modeling
│   └── Training simulation
├── Discovery Layer
│   ├── Fleet freshness
│   ├── Capability discovery
│   ├── Observatory
│   └── Trend analysis
├── Risk Layer
│   ├── Risk prioritization
│   ├── Risk calibration
│   ├── Predictive signals
│   └── Predictive readiness
├── Economics Layer
│   ├── Attention value scoring
│   ├── Planning accuracy
│   └── Historical patterns
├── Contracts
│   ├── 27 assurance contracts
│   ├── Cross-system boundary matrix
│   └── Improvement proposals
└── LINK Integration
    ├── Planning context adapter
    ├── Assurance projection
    └── LINK readiness interface
```

## Key Surfaces

| Surface | Purpose |
|---------|---------|
| `browser-app/` | Windows 11-style desktop simulator (offline) |
| `contracts/` | 27 canonical assurance contracts + schemas |
| `contracts/assurance/` | Core assurance contracts (evidence, finding, remediation, etc.) |
| `docs/` | Governance, planning, sprints, reports, schemas |
| `docs/decisions/` | Qualification decisions (0001–0017) |
| `docs/epics/` | Epic definitions and status |
| `docs/governance/` | Governance model, architectural invariants, contracts |
| `docs/plans/` | Capability plans and qualification architecture |
| `docs/schemas/` | JSON schemas (assurance, flightplan, governance) |
| `docs/sprints/` | 207 sealed sprint records |
| `evidence/` | Evidence stores and indices |
| `fixtures/` | Validation fixtures (work proposals, scenarios) |
| `qualification/` | Qualification records and profiles |
| `profiles/` | Project validation profiles |
| `receipts/` | Decision resolutions, custody, sprint closeouts |
| `reports/` | E2E test results, governance reports, migration results |
| `scripts/` | 194 Python scripts, 89 shell scripts |
| `test-library/` | Regression, security, accessibility, UAT, AI fixtures |

---

## Governance

QA Pilot operates under the Librarian governance model:

- **Separate ledger** — QA Pilot sprints seal under the QA Pilot ledger
- **Separate receipts** — decision resolutions and custody records are project-local
- **Advisory-only** — QA Pilot may not confer or modify authority
- **Cross-project mutation** requires explicit handoff/custody authorization
- **Canonical contracts** — 27 assurance contracts with 10 universal invariants
- **Write-custody enforcement** — 15 EC rules, 6 decision codes, sprint-allowlisted writes
- **Custody receipt chain** — 12 custody receipts indexed, lifecycle/live/write sources

### Authority Model

| Function | Owner |
|----------|-------|
| Build | Agents/projects |
| Evaluate | QA-Pilot |
| Record truth | Librarian |
| Teach | Training system |
| Accept risk | Owner |

The loop works because the evaluator, recorder, teacher, and authority holder are separated.

---

## Quick Start

```bash
# Open the offline simulator (no server required)
open browser-app/index.html

# Run the validation pipeline
./scripts/qa-pilot-pipeline.sh

# Run a specific E2E test
python3 scripts/e2e-1-librarian-runtime-audit.py

# Run the workbench CLI
python3 scripts/qa_pilot_workbench.py --help

# Qualify runtime evidence
python3 scripts/qualify-runtime-evidence.py

# Generate predictive risk signals
python3 scripts/generate-predictive-signals.py

# Discover fleet freshness
python3 scripts/discover-fleet-freshness.py
```

---

## Documentation

- `FEATURE-STATUS.md` — feature verification status rollup (240+ sprints)
- `SESSION-HANDOFF.md` — session state handoff and epic tracking
- `STARTUP-STATE.md` — current startup state and custody posture
- `docs/governance/` — governance model, contracts, architectural invariants
- `docs/planning/` — epics, capability plans, qualification architecture
- `docs/sprints/` — 207 sealed sprint records
- `docs/schemas/` — JSON schemas for all contracts
- `docs/decisions/` — qualification decisions and design decisions
- `docs/epics/` — epic definitions and phase tracking

---

## License

MIT
