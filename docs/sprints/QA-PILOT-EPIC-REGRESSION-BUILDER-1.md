# Sprint Report — QA-PILOT-EPIC-REGRESSION-BUILDER-1

## Status: ✅ **Sealed (ledger #36)**

**Type:** Implementation / Epic regression builder
**Lane:** implementation
**Boundary:** QA Pilot-local only
**Librarian impact:** none
**Authorization:** Owner-approved 2026-07-06 per explicit authorization.
**Sealed:** Owner-approved 2026-07-07 per seal qa-pilot sprint QA-PILOT-EPIC-REGRESSION-BUILDER-1.

## Scope Satisfied

Built the Epic-level regression builder that rolls sprint-level evidence (EP-*), test cases (TC-*), and result packets (QR-*) into advisory Epic regression suites conforming to `qa-epic-regression-suite.schema.json`.

### Deliverables

| Delivery | Path | Status |
|----------|------|--------|
| Governance doc | `docs/governance/QA-PILOT-EPIC-REGRESSION-BUILDER.md` | ✅ |
| Epic builder implementation | `scripts/qa_pilot_epic_regression_builder.py` | ✅ 6 commands |
| Validator (ER-1 through ER-13) | `scripts/validate-qa-pilot-epic-regression-builder.py` | ✅ 14 checks pass |
| Test runner (24 tests) | `scripts/test-qa-pilot-epic-regression-builder.sh` | ✅ 24/24 pass |
| Fixtures (4 total) | `docs/examples/qa-pilot-epic-regression-builder/` | ✅ |
| Output store | `data/epic-regression/` + `data/epic-regression/epic-regression-index.json` | ✅ |

### ER Rules Coverage

| Rule | Description | Status |
|------|-------------|--------|
| ER-1 | Builds from QA Pilot-local evidence, tests, results only | ✅ |
| ER-2 | Epic suite references EP evidence packet IDs | ✅ |
| ER-3 | Epic suite references TC test case IDs | ✅ |
| ER-4 | Epic suite references QR result packet IDs | ✅ |
| ER-5 | Suite includes advisory: true | ✅ |
| ER-6 | Suite validates against qa-epic-regression-suite schema | ✅ |
| ER-7 | No authority verbs | ✅ |
| ER-8 | No canonical mutation paths | ✅ |
| ER-9 | Malformed/incomplete inputs rejected | ✅ |
| ER-10 | Duplicate build is deterministic | ✅ |
| ER-11 | Epic index is QA Pilot-local only | ✅ |
| ER-12 | Packet chain (#33-#35) remains green | ✅ |
| ER-13 | Custody/startup/architecture regressions green | ✅ |

### Acceptance Gates

| Gate | Result |
|------|--------|
| Epic regression builder validator: PASS | ✅ 14/14 |
| Existing QA Pilot packet chain validators: PASS | ✅ #33 EM 12/12, #34 TC 13/13 |
| Milestone regression (#18): PASS | ✅ 11/11 |
| Architecture plan (#32): PASS | ✅ 13/13 |
| Startup / authority checks: PASS | ✅ |
| No canonical mutation authority introduced | ✅ |
| No seal authority introduced | ✅ |
| Epic regression output remains advisory-only | ✅ |

## Guardrails Maintained

- Epic regression is an advisory aggregation layer over #33/#34/#35 output
- No automatic promotion, seal, Owner-decision, or Librarian-ingest behavior
- No Librarian project-state modified
- All 13 ER rules enforced at build and validate time

## Sealed

Sealed by Owner 2026-07-07 as ledger #36 per `seal qa-pilot sprint QA-PILOT-EPIC-REGRESSION-BUILDER-1`.

## Next authorized sprint

None — awaiting Owner direction.
