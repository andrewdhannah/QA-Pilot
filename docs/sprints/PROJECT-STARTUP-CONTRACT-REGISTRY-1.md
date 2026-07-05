# PROJECT-STARTUP-CONTRACT-REGISTRY-1 — Startup Contract Registry Selection

**Type:** Governance / registration hardening
**Mode:** Registry-backed project selection — pointer requests, registry resolves, contract validates
**Predecessor:** PROJECT-STARTUP-CONTRACT-NEGATIVE-FIXTURES-1 (sealed #13)

---

## Summary

Moved project startup selection onto a registry-backed path. The pointer requests a project by id. The registry resolves the project. The startup contract validates the project. No project-local files are trusted before registry resolution succeeds.

## System Invariant

```text
The pointer may request a project.
The registry must resolve the project.
The startup contract must validate the project.
Only then may project-local checks run.

The pointer is not authority by itself. It is an input to registry resolution.
No fallback project is selected after registry failure.
```

## What Changed

### Registry Selection Validator

| File | Purpose |
|------|---------|
| `SessionStartup/validate-startup-registry-selection.py` | Validates registry-backed selection flow: pointer validation, registry loading, project resolution, startup contract agreement, path confinement. Supports live mode and fixture mode. |

### Fixtures Added (docs/examples/startup-registry/)

| Fixture | Type | Rejection Reason |
|---------|------|------------------|
| `valid-registry-qa-pilot.json` | Valid | Schema-compliant QA Pilot registry entry |
| `valid-registry-librarian.json` | Valid | Schema-compliant Librarian registry entry |
| `valid-current-project-qa-pilot.json` | Valid | Pointer with valid qa-pilot project id |
| `valid-current-project-librarian.json` | Valid | Pointer with valid librarian project id |
| `invalid-pointer-unknown-project.json` | Invalid | Project id not found in registry |
| `invalid-pointer-path-instead-of-project-id.json` | Invalid | Pointer contains filesystem path instead of project id |
| `invalid-registry-duplicate-project-id.json` | Invalid | Registry has duplicate project_id entries |
| `invalid-registry-missing-repo-path.json` | Invalid | Registry entry missing repo_path |
| `invalid-registry-missing-startup-contract.json` | Invalid | Registry entry has null startup_contract |
| `invalid-registry-project-id-contract-mismatch.json` | Invalid | Registry project_id does not match startup contract project_id |
| `invalid-registry-project-root-escape.json` | Invalid | Registry repo_path escapes workspace root |
| `invalid-registry-startup-contract-escape.json` | Invalid | Startup contract path escapes project root via `../` |
| `invalid-registry-cross-project-root.json` | Invalid | Registry maps qa-pilot to librarian's repo path (project id mismatch in contract) |
| `invalid-registry-malformed-json.json` | Invalid | Registry is not valid JSON |
| `fixture-contract-mismatch.json` | (supporting) | Fixture contract with wrong project_id for mismatch test |

### Live Registry Updated

| File | Change |
|------|--------|
| `active/librarian/project-state/project-index.json` | Added `startup_contract` field to librarian and qa-pilot entries |

### Documentation Updated

| File | Change |
|------|--------|
| `SessionStartup/AGENT-START.md` §13 | Rewritten project selector protocol — registry-backed resolution with invariant, validation rules, fail-closed behavior |
| `docs/startup/STARTUP-BOUNDARY-ARCHITECTURE.md` | Updated delegation flow to include registry selection. Added registry validation section. Added FIXTURE classification category. |

## Verification

### Registry Selection (Live)

```
✅ All registry selection checks pass
Pointer: .librarian/current-project.json → qa-pilot
Registry: project-index.json → QA Pilot
Repo path: active/qa-pilot
```

### Registry Selection (Fixtures)

```
Valid fixtures:   4 passed, 0 failed
Invalid fixtures: 10 rejected as expected, 0 unexpectedly passed
```

### Full Suite

| Validator | Result |
|-----------|--------|
| Boundary validator | ✅ PASS |
| Contract fixture validator | ✅ 2/2 valid pass, 10/10 invalid rejected |
| Registry selection (QA Pilot live) | ✅ PASS |
| Registry selection (Librarian live) | ✅ PASS |
| QA Pilot startup checks | ✅ managed |
| Librarian startup checks | ✅ managed |

## Rejection Classes Proved (Registry Selection)

| Invalid Registry/Pointer | Rejection Reason |
|---|---|
| Unknown project in pointer | `project_id not found in registry` |
| Path instead of project id | `active_project_id contains path separator` |
| Duplicate project_id in registry | `Duplicate project_id 'X' at entries 0 and 1` |
| Missing repo_path in entry | `missing or empty required field: repo_path` |
| Null startup_contract | `startup_contract is empty/null — required for project selection` |
| Project ID mismatch | `registry project_id 'X' does not match startup contract project_id 'Y'` |
| repo_path escapes workspace | `resolves outside workspace root` |
| Contract path escapes project | `startup_contract path escapes via ../` |
| Malformed registry JSON | `is not valid JSON` |

## Files Changed

```
Created:
  docs/examples/startup-registry/valid-registry-qa-pilot.json
  docs/examples/startup-registry/valid-registry-librarian.json
  docs/examples/startup-registry/valid-current-project-qa-pilot.json
  docs/examples/startup-registry/valid-current-project-librarian.json
  docs/examples/startup-registry/invalid-pointer-unknown-project.json
  docs/examples/startup-registry/invalid-pointer-path-instead-of-project-id.json
  docs/examples/startup-registry/invalid-registry-duplicate-project-id.json
  docs/examples/startup-registry/invalid-registry-missing-repo-path.json
  docs/examples/startup-registry/invalid-registry-missing-startup-contract.json
  docs/examples/startup-registry/invalid-registry-project-id-contract-mismatch.json
  docs/examples/startup-registry/invalid-registry-project-root-escape.json
  docs/examples/startup-registry/invalid-registry-startup-contract-escape.json
  docs/examples/startup-registry/invalid-registry-cross-project-root.json
  docs/examples/startup-registry/invalid-registry-malformed-json.json
  docs/examples/startup-registry/fixture-contract-mismatch.json
  SessionStartup/validate-startup-registry-selection.py
  active/qa-pilot/docs/sprints/PROJECT-STARTUP-CONTRACT-REGISTRY-1.md

Modified:
  active/librarian/project-state/project-index.json (startup_contract field added)
  SessionStartup/AGENT-START.md §13 (registry-backed selection protocol)
  docs/startup/STARTUP-BOUNDARY-ARCHITECTURE.md (registry selection flow, validation)
```

## Acceptance Gates

| Gate | Status |
|------|--------|
| Pointer resolves through registry | ✅ |
| Unknown pointer project id rejected | ✅ |
| Pointer cannot specify filesystem path | ✅ |
| Registry duplicate ids rejected | ✅ |
| Missing selected registry entry rejected | ✅ |
| Missing repo_path rejected | ✅ |
| Missing startup_contract rejected | ✅ |
| Registry/contract project-id mismatch rejected | ✅ |
| Path escape through registry rejected | ✅ |
| Cross-project root mapping rejected | ✅ |
| No fallback project after failure | ✅ |
| Live QA Pilot selection passes | ✅ |
| Live Librarian selection passes | ✅ |
| Existing contract negative fixtures still pass | ✅ |
| Existing boundary validator still passes | ✅ |
| QA Pilot startup still passes | ✅ |
| Librarian startup still passes | ✅ |
