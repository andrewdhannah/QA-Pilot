# PROJECT-STARTUP.md — QA Pilot

**This file provides project-specific startup context for agents working on QA Pilot.**
**QA Pilot is a harness_governed add-on project — see PROJECT-IDENTITY.md for full identity, boundaries, and authority.**

---

## Delegation

QA Pilot's project identity and governance are defined in:

- **Identity:** `PROJECT-IDENTITY.md` (project_id, thesis, owner, boundaries)
- **Profile:** `PROJECT-PROFILE.json` (repo_path, workspace_path, sandbox_boundary, allowed_mutation_paths, forbidden_cross_project_paths)
- **Status:** `FEATURE-STATUS.md`, `SESSION-HANDOFF.md`, `project-state/sprint-ledger.json`
- **Governance:** `docs/governance/QA-PILOT-PROJECT-GOVERNANCE.md`

## Project Identity

| Field | Value |
|-------|-------|
| `project_id` | `qa-pilot` |
| `project_name` | QA Pilot |
| `profile_id` | `lightweight-custody` |
| `owner` | Andrew Hannah |
| `thesis` | A governed quality assurance framework for AI-assisted product work, providing structured QA lanes, evidence collection, manual verification scripts, and readiness assessments. |

## MCP Context Acquisition

QA Pilot uses the generic startup protocol defined in `SessionStartup/AGENT-START.md` §13 (project selector) and `docs/rules/PROJECT-HARNESS-STARTUP-PROTOCOL.md`.

## QA Pilot-Specific Rules

### Paths
- **Read/write:** `{{active_project_root}}/`
- **Read-only (historical):** `{{historical_root}}/`
- **Do not edit:** `{{historical_root}}/` unless explicitly authorized

### Allowed Mutation Paths
- `docs/`, `scripts/`, `fixtures/`, `project-state/`, `receipts/`
- `PROJECT-IDENTITY.md`, `PROJECT-PROFILE.json`, `FEATURE-STATUS.md`, `SESSION-HANDOFF.md`

### Forbidden Cross-Project Paths
- See `PROJECT-PROFILE.json` `forbidden_cross_project_paths` for the full list

### Agent Authority
- Authority level: `advisory-only`
- No agent may self-verify work or mark it `✅ Verified`
- All agent work is `🔍 Pending` until Owner reviews
- QA Pilot is a separate add-on project — must not mutate The Librarian repo
- See `PROJECT-IDENTITY.md` for the complete boundary rules
