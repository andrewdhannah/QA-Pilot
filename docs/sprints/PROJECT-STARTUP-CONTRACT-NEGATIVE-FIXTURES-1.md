# PROJECT-STARTUP-CONTRACT-NEGATIVE-FIXTURES-1 — Startup Contract Negative Fixtures

**Type:** Validation / negative fixture coverage
**Mode:** Deterministic rejection of invalid project startup contracts
**Predecessor:** PROJECT-STARTUP-SYSTEM-SEPARATION-1 (sealed #12)

---

## Summary

Added 12 startup contract fixtures (2 valid + 10 invalid) and a fixture validator proving that invalid project startup contracts are rejected before startup proceeds. The harness fails closed — no fallback to Librarian assumptions, no cross-project leakage.

## What Changed

### Fixtures Added (docs/examples/startup-contracts/)

| Fixture | Type | Rejection Reason |
|---------|------|------------------|
| `valid-qa-pilot-startup-contract.json` | Valid | Schema-compliant QA Pilot contract |
| `valid-librarian-startup-contract.json` | Valid | Schema-compliant Librarian contract |
| `invalid-missing-identity-doc.json` | Invalid | identity_source file not found on disk |
| `invalid-missing-startup-check-script.json` | Invalid | startup_checks_script file not found on disk |
| `invalid-check-script-outside-project-root.json` | Invalid | startup_checks_script escapes project root via `../` |
| `invalid-required-file-outside-project-root.json` | Invalid | required_files item escapes project root via `../` |
| `invalid-undeclared-verification-surface.json` | Invalid | Schema violation (wrong types for is_web_app, verification_surfaces) |
| `invalid-project-id-mismatch.json` | Invalid | Contract project_id does not match selected project |
| `invalid-cross-project-startup-state.json` | Invalid | startup_state_file escapes project root via `../` |
| `invalid-web-files-required-for-non-web-project.json` | Invalid | Non-web-app project requires Public/ files |
| `invalid-forbidden-generic-assumption.json` | Invalid | Non-Librarian project has empty forbidden_terms_in_generic |
| `invalid-schema-missing-required-field.json` | Invalid | Schema violation (missing required identity_source) |

### Validator Added

| File | Purpose |
|------|---------|
| `SessionStartup/validate-startup-contract-fixtures.py` | Runs 7 check categories on each fixture: schema compliance, schema version, project ID match, path confinement, file existence, web-app semantic, forbidden-terms semantic |

### Validation Rules Proven

| Check | Proved By |
|-------|-----------|
| Schema-compliant contracts accepted | 2 valid fixtures pass |
| Missing identity doc rejected | `invalid-missing-identity-doc.json` |
| Missing check script rejected | `invalid-missing-startup-check-script.json` |
| Path escape rejected before execution | `invalid-check-script-outside-project-root.json`, `invalid-required-file-outside-project-root.json`, `invalid-cross-project-startup-state.json` |
| Project ID mismatch rejected | `invalid-project-id-mismatch.json` |
| Wrong field types rejected | `invalid-undeclared-verification-surface.json` |
| Missing required fields rejected | `invalid-schema-missing-required-field.json` |
| Non-web-app web files rejected | `invalid-web-files-required-for-non-web-project.json` |
| Empty boundary guard rejected | `invalid-forbidden-generic-assumption.json` |

## Verification

### Fixture Validator

```
Valid fixtures:   2 passed, 0 failed
Invalid fixtures: 10 rejected as expected, 0 unexpectedly passed
✅ ALL FIXTURES VALIDATE AS EXPECTED
```

### Boundary Validator

```
✅ All generic startup files are clean of project-specific assumptions.
Files checked: CLAUDE.md, AGENT-START.md, ACTIVE-REPO-ROOT-RULE.md, PROJECT-HARNESS-STARTUP-PROTOCOL.md
```

### QA Pilot Startup

```
QA Pilot startup checks complete.
Operating mode: managed
MCP: reachable (via Librarian)
```

### Librarian Startup

```
Librarian startup checks complete.
Operating mode: managed
MCP: reachable
```

## Files Changed

```
Created:
  docs/examples/startup-contracts/valid-qa-pilot-startup-contract.json
  docs/examples/startup-contracts/valid-librarian-startup-contract.json
  docs/examples/startup-contracts/invalid-missing-identity-doc.json
  docs/examples/startup-contracts/invalid-missing-startup-check-script.json
  docs/examples/startup-contracts/invalid-check-script-outside-project-root.json
  docs/examples/startup-contracts/invalid-required-file-outside-project-root.json
  docs/examples/startup-contracts/invalid-undeclared-verification-surface.json
  docs/examples/startup-contracts/invalid-project-id-mismatch.json
  docs/examples/startup-contracts/invalid-cross-project-startup-state.json
  docs/examples/startup-contracts/invalid-web-files-required-for-non-web-project.json
  docs/examples/startup-contracts/invalid-forbidden-generic-assumption.json
  docs/examples/startup-contracts/invalid-schema-missing-required-field.json
  SessionStartup/validate-startup-contract-fixtures.py
  active/qa-pilot/docs/sprints/PROJECT-STARTUP-CONTRACT-NEGATIVE-FIXTURES-1.md

No existing files modified.
```

## Acceptance Gates

| Gate | Status |
|------|--------|
| Valid QA Pilot contract fixture passes | ✅ |
| Valid Librarian contract fixture passes | ✅ |
| All 10 invalid fixtures fail with expected reason | ✅ |
| Validator exits nonzero if invalid fixture passes | ✅ |
| Validator exits nonzero if valid fixture fails | ✅ |
| Cross-project paths rejected before execution | ✅ |
| Missing startup check scripts rejected before execution | ✅ |
| Project ID mismatch rejected | ✅ |
| Generic boundary files remain clean | ✅ |
| QA Pilot startup still passes | ✅ |
| Librarian startup still passes | ✅ |
| No registry or pointer behavior changed | ✅ |
