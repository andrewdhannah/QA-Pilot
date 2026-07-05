# PROJECT-STARTUP-SYSTEM-SEPARATION-1 — Startup System Separation

**Type:** Governance / startup architecture
**Mode:** Contract-based delegation — generic harness selects project, project declares shape
**Predecessor:** `start qa-pilot` blocker report (2026-07-02)

---

## Summary

Separated generic startup harness authority from project-specific startup contracts so any selected project can declare its own identity, state, checks, verification surfaces, and context sources without inheriting assumptions from The Librarian, QA Pilot, or any single local layout.

## What Changed

### System Boundary Architecture

Created `docs/startup/` with:
- **`project-startup-contract-schema.json`** — Draft 2020-12 JSON schema defining the minimum startup contract for any project (contract_schema, project_id, project_name, identity_source, startup_state_file, startup_checks_script, is_web_app, verification_surfaces, required_files, forbidden_terms_in_generic, context_sources)
- **`STARTUP-BOUNDARY-ARCHITECTURE.md`** — Classification system (SYSTEM_GENERIC / PROJECT_SPECIFIC / PROJECT_PROFILE / DERIVED_REPORT), contract-based delegation flow, validation rules

### Generic Harness Updates (SYSTEM_GENERIC)

| File | Change |
|------|--------|
| `SessionStartup/AGENT-START.md` | Level 2 root verification now contract-driven — reads project's `startup-contract.json` `required_files` field. Project selector protocol (§13) added. Hardcoded `Public/` checks and `active/librarian` path removed. |
| `docs/rules/ACTIVE-REPO-ROOT-RULE.md` | Level 2 verification now contract-based. Web app and script/tool projects distinguished by contract `is_web_app` field. Hardcoded `Public/index.html` removed. |
| `CLAUDE.md` (workspace root) | Startup protocol steps updated — Step 3 now includes project selector, Step 5/6/7 use contract-declared paths. |

### QA Pilot Project Files (PROJECT_SPECIFIC)

| File | Change |
|------|--------|
| `active/qa-pilot/startup-contract.json` | **New.** Declares QA Pilot shape: identity_source = PROJECT-IDENTITY.md, is_web_app = false, required_files = 5 project files, forbidden_terms_in_generic = Librarian-specific terms |
| `active/qa-pilot/PROJECT-STARTUP.md` | **New.** QA Pilot identity, MCP context, project-specific rules, delegation to PROJECT-IDENTITY.md |
| `active/qa-pilot/scripts/run-startup-checks.sh` | **New.** QA Pilot-local startup checks — verifies project files exist, sprint ledger readable, known validators/test runners present. No Public/ checks, no Swift build, no web app assumptions. Generates `active/qa-pilot/STARTUP-STATE.md`. |
| `active/qa-pilot/STARTUP-STATE.md` | **New.** Project-local generated state (written by startup checks) |
| `active/qa-pilot/reports/qa-pilot-startup-blocker-report.md` | (Existing) — Documents the original 5 blockers that motivated this sprint |

### Librarian Project Files (PROJECT_SPECIFIC)

| File | Change |
|------|--------|
| `active/librarian/startup-contract.json` | **New.** Declares Librarian shape: is_web_app = true, required_files = 7 (including Public/*), forbidden_terms_in_generic = Librarian-specific check paths |
| `active/librarian/PROJECT-STARTUP.md` | Project selector protocol § removed (now generic in AGENT-START.md §13), replaced with reference to AGENT-START.md §13 |
| `active/librarian/scripts/run-startup-checks.sh` | Now writes to project-local `active/librarian/STARTUP-STATE.md`. Project name dynamically resolved from pointer file or startup contract. Legacy copy to SessionStartup/ for backward compatibility. |

### Validation

| File | Change |
|------|--------|
| `SessionStartup/validate-startup-boundary.py` | **New.** Checks that SYSTEM_GENERIC files contain no project-specific forbidden terms from any project's contract |

## Verification

### Boundary Validation

```
Startup Boundary Validator
Projects with contracts: librarian, qa-pilot
✅ All generic startup files are clean of project-specific assumptions.
Files checked: CLAUDE.md, AGENT-START.md, ACTIVE-REPO-ROOT-RULE.md, PROJECT-HARNESS-STARTUP-PROTOCOL.md
```

### QA Pilot Proof

```
QA Pilot startup checks complete.
Operating mode: managed
Project: QA Pilot
MCP: reachable (via Librarian)
Working tree: clean (except intentional sprint files)
No Public/ checks evaluated — no web app assumptions
No active/librarian paths in startup checks
No sprint-3 assumption
Startup file: active/qa-pilot/STARTUP-STATE.md
```

### Librarian Preservation

```
Librarian startup checks complete.
Operating mode: managed
Project: The Librarian
MCP: reachable
Startup file: active/librarian/STARTUP-STATE.md
```

## Files Changed

```
Created:
  docs/startup/project-startup-contract-schema.json
  docs/startup/STARTUP-BOUNDARY-ARCHITECTURE.md
  SessionStartup/validate-startup-boundary.py
  active/qa-pilot/startup-contract.json
  active/qa-pilot/PROJECT-STARTUP.md
  active/qa-pilot/scripts/run-startup-checks.sh
  active/qa-pilot/STARTUP-STATE.md
  active/librarian/startup-contract.json
  active/qa-pilot/docs/sprints/PROJECT-STARTUP-SYSTEM-SEPARATION-1.md

Modified:
  SessionStartup/AGENT-START.md (root verification, startup state path, §13 added)
  docs/rules/ACTIVE-REPO-ROOT-RULE.md (generic Level 2, removed hardcoded checks)
  CLAUDE.md (updated startup protocol)
  active/librarian/PROJECT-STARTUP.md (removed project selector to AGENT-START.md)
  active/librarian/scripts/run-startup-checks.sh (project-local state, dynamic project name)
  active/qa-pilot/PROJECT-PROFILE.json (no change needed — already has required fields)
  .librarian/current-project.json (pointer switched to qa-pilot for proof)
```

## Acceptance Gates

| Gate | Status |
|------|--------|
| Generic files contain no hardcoded Librarian shape | ✅ |
| Generic files contain no hardcoded QA Pilot shape | ✅ |
| Generic startup loads project contract before running checks | ✅ |
| `start qa-pilot` completes cleanly (no Public/ checks, no active/librarian paths) | ✅ |
| `start librarian` still completes cleanly (web app checks preserved via contract) | ✅ |
| Boundary validator passes | ✅ |
| QA Pilot checks pass | ✅ |
| Librarian checks pass | ✅ |
