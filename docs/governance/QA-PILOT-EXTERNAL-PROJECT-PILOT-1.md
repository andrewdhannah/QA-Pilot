# QA Pilot External Project Pilot — QA-PILOT-EXTERNAL-PROJECT-PILOT-1

**Sprint:** QA-PILOT-EXTERNAL-PROJECT-PILOT-1
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review
**Authority:** Advisory only. External pilot proves portability; does not confer authority.

## 1. Purpose

Prove that QA-Pilot works against a project it was not built for. Validate the portability claim by installing and running against a project with different architecture, stack, and governance model.

## 2. Pilot Target: Agent Bridge

| Property | Value |
|---|---|
| Project | Agent Bridge (active/agent-bridge) |
| Type | MCP bridge runtime extension |
| Architecture | Different from Librarian |
| Stack | Node.js/TypeScript extension runtime |
| Governance | Independent governance model |
| Relationship to QA-Pilot | **Not built for, not derived from** |

## 3. Acceptance Gates

| Gate | Status | Evidence |
|---|---|---|
| **EXT-001** | ✅ PASS | Zero Librarian references in installed core contracts and validators |
| **EXT-002** | ✅ PASS | All 4 existing validators execute with --list-rules against external project |
| **EXT-003** | ✅ PASS | Test library validator (7 rules) passes unchanged |
| **EXT-004** | ✅ PASS | Validation package produced with identical format (manifest.json + summary) |
| **EXT-005** | ✅ PASS | Zero new contracts required — no QA-Pilot contracts modified |

## 4. External Validation Package

| Artifact | Location |
|---|---|
| Manifest | `active/agent-bridge/validation-package/manifest.json` |
| Summary | `active/agent-bridge/validation-package/external-project-summary.md` |
| Project adapter | `active/agent-bridge/qa-pilot/project-adapter.json` |

## 5. Files

| File | Description |
|---|---|
| `scripts/qa-pilot-external-pilot.sh` | External project validation pipeline |
| `adapters/project-adapter-agent-bridge.json` | Agent Bridge project adapter (reference) |

## 6. Next

| Track | When |
|---|---|
| QA-PILOT-CONTINUOUS-VALIDATION-PIPELINE-1 | After external pilot proven |
| QA-PILOT-COMPLIANCE-COVERAGE-EXPANSION-1 | After pipeline established |
