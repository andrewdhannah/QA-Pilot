# QA Pilot Fresh Install Kit — QA-PILOT-FRESH-INSTALL-KIT-1

**Purpose:** Package the QA-Pilot teaching and qualification pipeline into a project-neutral deployment model. Any governed project can install QA-Pilot contracts without depending on Librarian paths or assumptions.

## Architecture

```
Fresh Project
    │
    ▼
Install QA-Pilot (bash scripts/qa-pilot-install.sh <target>)
    │
    ├── contracts/        (schemas — learning-object, scenario, SDK)
    ├── validators/        (standalone validation scripts)
    ├── examples/          (valid + invalid fixtures)
    └── project-adapter.json  (configure for your project)
    │
    ▼
Configure Project Adapter
    │
    ├── Set evidence_source to your project's evidence output
    ├── Review governance boundary (advisory_only = true)
    └── Configure adapter type
    │
    ▼
Run Validation Example
    │
    ├── python3 validators/validate-learning-object.py --all
    ├── python3 validators/validate-learning-object.py --list-rules
    └── (all validators pass against project-neutral fixtures)
    │
    ▼
Validation Package (advisory, provenance-tracked)
```

## Installation

```bash
bash scripts/qa-pilot-install.sh /path/to/my-new-project
```

Creates `/path/to/my-new-project/qa-pilot/` with:
- 3 contract schemas
- 3 standalone validators
- 20 example fixtures (across 3 domains)
- Project adapter configuration

## Acceptance Gates

| Gate | Criteria | Status |
|---|---|---|
| **FK-001** | Zero Librarian paths in installed artifacts | ✅ Verified |
| **FK-002** | Validators runnable without Librarian context | ✅ Verified |
| **FK-003** | Example fixtures validate correctly | ✅ Verified |
| **FK-004** | Project adapter is configurable | ✅ project-adapter.json |
| **FK-005** | Results remain advisory-only | ✅ All validators enforce |

## Portable Contract Bundle

| Contract | Schema | Validator | Fixtures |
|---|---|---|---|
| Learning Object v1 | `contracts/learning-object-v1.schema.json` | `validators/validate-learning-object.py` | 6 examples |
| SDK Integration | `contracts/qa-pilot-sdk-integration.schema.json` | `validators/validate-qa-pilot-sdk-integration.py` | 9 examples |
| Epic Scenario Suite | `contracts/qa-pilot-epic-scenario-suite.schema.json` | `validators/validate-qa-pilot-epic-scenario-suite.py` | 5 examples |

## Files

| File | Description |
|---|---|
| `scripts/qa-pilot-install.sh` | Install script — creates project-neutral bundle |
| `docs/QA-PILOT-FRESH-INSTALL-KIT.md` | This documentation |

## QA-Pilot Complete State

```
Phase 1 — Infrastructure Boundary
    QA-PILOT-000                              ✓
    QA-PILOT-SDK-INTEGRATION-1                ✓
    QA-PILOT-EPIC-SCENARIO-SUITES             ✓
    QA-PILOT-CAPABILITY-RECONCILIATION-1      ✓

Phase 2 — Teaching Capability
    QA-PILOT-LEARNING-OBJECT-CONTRACT-1        ✓
    QA-PILOT-EVIDENCE-TO-LESSON-GENERATOR-1   ✓
    QA-PILOT-VISUAL-INTEGRATION-CONTRACT-1    ✓
    QA-PILOT-SCENARIO-ADAPTER-1               ✓

Phase 3 — Qualification
    QA-PILOT-AI-QUALIFICATION-1               ✓

Phase 4 — Portability
    QA-PILOT-FRESH-INSTALL-KIT-1              ✓ ← COMPLETE
```
