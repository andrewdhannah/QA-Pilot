# QA Pilot Test Library Expansion — QA-PILOT-TEST-LIBRARY-EXPANSION-1

**Sprint:** QA-PILOT-TEST-LIBRARY-EXPANSION-1
**Project:** QA Pilot
**Status:** 🔍 Pending Owner review
**Authority:** Advisory only. Test results report status; they do not confer authority.

## 1. Purpose

Convert existing project knowledge — sealed work orders, acceptance gates, authority invariants, and evidence plane contracts — into reusable governed test definitions. Expand the test library from seed to initial coverage.

## 2. Test Library Structure

```
test-library/
├── test-library-index.json        (manifest — domain counts, schema refs)
├── regression/                    (3 tests)
│   ├── REG-001-cursor-freshness.json
│   ├── REG-002-acceptance-gate-completeness.json
│   └── REG-003-composition-graph-topology.json
├── security/                      (4 tests)
│   ├── SEC-001-mutation-path-absence.json
│   ├── SEC-002-learning-object-no-evidence.json
│   ├── SEC-003-certification-no-seal-authority.json
│   └── SEC-004-scoring-no-state-mutation.json
├── uat/                           (0 — future)
├── accessibility/                 (0 — future)
├── performance/                   (0 — future)
├── ai/                            (0 — future)
└── compliance/                    (0 — future)
```

## 3. Test Definitions

| ID | Domain | Source | What It Validates |
|---|---|---|---|
| REG-001 | regression | OE-001 evidence freshness | Cursor staleness detection |
| REG-002 | regression | AG-PREP/AG-COPY gates | Sealed work order acceptance gate completeness |
| REG-003 | regression | OE-003 composition graph | Graph topology integrity |
| SEC-001 | security | QPSDK-005 | SDK mutation path absence |
| SEC-002 | security | LO-001 | Learning objects don't embed evidence |
| SEC-003 | security | LO-005, VIS-005 | No seal authority in certification |
| SEC-004 | security | QA-PILOT-SCENARIO-ADAPTER-1 | Scoring is pure function, no side effects |

## 4. Results

| Metric | Value |
|--------|-------|
| Test definitions created | 7 |
| Domains populated | 2 (regression, security) |
| Domains seeded (0 tests) | 5 (uat, accessibility, performance, ai, compliance) |
| Test library validator rules | 7 (TL-1 through TL-7) |
| Validator result | ✅ All 7 rules pass |
| Source contracts | 4 (SDK, learning-object, epic-scenario, scenario-adapter) |

## 5. Validation Rules (TL-1 through TL-7)

| Rule | Check | Status |
|---|---|---|
| TL-1 | Library index exists | ✅ |
| TL-2 | Test files match index counts | ✅ |
| TL-3 | Test IDs have correct domain prefix | ✅ |
| TL-4 | All tests have required fields | ✅ |
| TL-5 | advisory_only=True on all tests | ✅ |
| TL-6 | no_seal_authority=True on all tests | ✅ |
| TL-7 | All test files are valid JSON | ✅ |

## 6. Expansion Priority

| Pri | Domain | Next Steps |
|---|---|---|
| 1 | Regression | Add tests from each new sealed sprint's acceptance gates |
| 2 | Security | Add permission escalation and provenance manipulation tests |
| 3 | UAT | Model user journeys — portal, course, capstone, certification |
| 4 | Accessibility | WCAG 2.1 AA patterns for academy surfaces |
| 5 | Performance | Startup time, SDK query latency, validator throughput |
| 6 | AI | Multi-model benchmarks, refusal patterns, instruction following |
| 7 | Compliance | SOC 2, PIPEDA, EU AI Act evidence maping |

## 7. Files

| File | Description |
|---|---|
| `test-library/test-library-index.json` | Library manifest |
| `test-library/regression/REG-*.json` | 3 regression test definitions |
| `test-library/security/SEC-*.json` | 4 security test definitions |
| `docs/schemas/qa-test-definition.schema.json` | Test definition schema |
| `scripts/validate-qa-pilot-test-library.py` | 7-rule library validator |
| `docs/governance/QA-PILOT-TEST-LIBRARY-EXPANSION-1.md` | This governance document |
