# QA Pilot Test Composition — Governance

**Sprint:** QA-PILOT-TEST-COMPOSITION-1
**Boundary:** QA Pilot-local only
**Librarian impact:** none
**Authority:** advisory-only

## Purpose

Convert QA Pilot-local ingested evidence packets into advisory test cases.
Generated tests are QA Pilot-local, advisory-only, and carry evidence provenance.

## Architecture

```
evidence store (data/evidence/)  ──→  test composition  ──→  test-case store (data/test-cases/)
       ↑                                  ↑                           ↑
   EP- packets                     TC rules 1-12                 TC- test_ids
```

## TC Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| TC-1 | Reads only QA Pilot-local evidence records | Evidence store path check |
| TC-2 | Generated tests reference source packet ID | `source_artifact` field required |
| TC-3 | Generated tests include `advisory_only: true` | Compose enforces; validator checks |
| TC-4 | Generated tests validate against `qa-test-case.schema.json` | Schema validation at compose time |
| TC-5 | No approve/seal/start/advance authority verbs | FORBIDDEN_AUTHORITY_VERBS list |
| TC-6 | No source-project mutation paths | `/Sources/`, `/Public/`, `/.librarian/` blocked |
| TC-7 | Malformed evidence is rejected | Required fields check |
| TC-8 | Duplicate composition is deterministic | Skip on test_id collision |
| TC-9 | Cross-project source metadata preserved, not converted to authority | `_source_project_metadata` check |
| TC-10 | Test-case index is QA Pilot-local only | `data/test-cases/` paths only |
| TC-11 | Existing MCP evidence-intake remains green | Validated in test runner |
| TC-12 | Existing custody/startup/architecture regressions remain green | Validated in test runner |

## Forbidden

- Writing to Librarian project files
- Mutating Librarian ledgers, receipts, status surfaces, or startup state
- Creating Librarian receipts
- Approving or sealing any sprint
- Advancing active_sprint
- Treating generated tests as Owner decisions
- Exporting QA results as authority

## Commands

```
compose [--packet-id ID]        Compose test cases from evidence
validate <path>                 Validate evidence or test case file
list [--limit N] [--source-packet ID]  List composed test cases
read <test_id>                  Read a composed test case
status                          Show store status
clear                           Clear all composed test cases
```
