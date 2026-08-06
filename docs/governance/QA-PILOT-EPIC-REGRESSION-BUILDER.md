# QA Pilot Epic Regression Builder — Governance

**Status:** Agent work complete — pending Owner review
**Sprint:** QA-PILOT-EPIC-REGRESSION-BUILDER-1
**Boundary:** QA Pilot-local only
**Librarian impact:** none
**Authority:** advisory-only

## Purpose

Roll sprint-level evidence (EP-*), test cases (TC-*), and result packets (QR-*) into Epic-level advisory regression suites conforming to `qa-epic-regression-suite.schema.json`.

## Architecture

```
evidence (data/evidence/) ──┐
test cases (data/test-cases/) ├──→ epic build ──→ epic regression store
result packets (data/result/  ┘   ER-1..13        (data/epic-regression/)
                                                  ERS- suites
```

## ER Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| ER-1 | Builds from QA Pilot-local evidence, tests, results only | Path confinement |
| ER-2 | Epic suite references source EP evidence packet IDs | `provenance.evidence_packets` |
| ER-3 | Epic suite references source TC test case IDs | `tests[]` array |
| ER-4 | Epic suite references source QR result packet IDs | `provenance.result_packets` |
| ER-5 | Suite includes `advisory: true` | Schema const |
| ER-6 | Suite validates against `qa-epic-regression-suite` schema | Schema validation |
| ER-7 | No authority verbs | FORBIDDEN_AUTHORITY_VERBS |
| ER-8 | No canonical mutation paths | Path block list |
| ER-9 | Malformed/incomplete inputs rejected | Pre-build validation |
| ER-10 | Duplicate build is deterministic | Unique suite per input |
| ER-11 | Epic index is QA Pilot-local only | `data/epic-regression/` |
| ER-12 | Packet chain (#33-#35) remains green | Validated |
| ER-13 | Custody/startup/architecture regressions green | Validated |

## Commands

```
build <epic_id> [--sprint-ids S1 S2 ...]   Build Epic regression suite
validate <path>                              Validate an Epic suite file
list [--limit N]                             List built Epic suites
read <suite_id>                              Read a built Epic suite
status                                       Show store status
clear                                        Clear all Epic suites
```

## Forbidden

- Collapsing Epic regression into a canonical truth source
- Automatic promotion, seal, Owner-decision, or Librarian-ingest behavior
- Modifying Librarian project-state
- Any authority mutation
