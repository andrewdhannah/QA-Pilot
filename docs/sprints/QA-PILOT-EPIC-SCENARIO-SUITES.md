# QA-PILOT-EPIC-SCENARIO-SUITES — Sprint Doc

**Project:** QA Pilot
**Type:** composition validation
**Boundary:** QA Pilot-local (consumes SDK — read-only)
**Librarian impact:** none
**Status:** 🔍 Pending Owner review
**Authority:** advisory-only

---

## Sprint Goal

Transform QA-Pilot from a governed evidence consumer into a system-level composition verifier. Produce reusable epic validation scenarios targeting the Evidence Plane.

## Sprint Scope

1. Create `scripts/qa_pilot_epic_scenario_suite.py` — scenario evaluation engine
2. Create 5 built-in scenario definitions (Evidence Plane target)
3. Create `docs/schemas/qa-pilot-epic-scenario-suite.schema.json` — schema
4. Create `docs/governance/QA-PILOT-EPIC-SCENARIO-SUITES.md` — governance doc
5. Create `scripts/validate-qa-pilot-epic-scenario-suite.py` — validator
6. Create `scripts/test-qa-pilot-epic-scenario-suite.sh` — test runner
7. Create `docs/examples/qa-pilot-epic-scenario-suite/` — fixtures
8. Run all 5 scenarios against live Evidence Plane data
9. Produce completion report

## Scenarios

| ID | Type | What It Validates |
|----|------|-------------------|
| EP-EP-001 | complete_epic | All OE layers present, findings valid, graph topological, provenance tracked, no mutation |
| EP-MISS-001 | missing_artifact | Absent evidence detected and classified with project/category |
| EP-CONF-001 | conflicting_sources | Conflicts have resolver_class in authority block |
| EP-PROV-001 | broken_provenance | Stale/absent links identified in provenance chain |
| EP-BOUND-001 | mutation_boundary | All 5 SDK queries enforce no_mutation_path=True |

## Acceptance Gates (built-in scenario output)

| Gate | Criteria |
|------|----------|
| Complete Evidence Plane | All OE layers recognized, composition validates |
| Missing artifact | Structured learning failure produced for absent evidence |
| Conflicting sources | Authority resolution outcome explained |
| Broken provenance | Broken link identified |
| Mutation boundary | Boundary enforcement confirmed |

## Verification

- All 5 scenarios PASS against live Evidence Plane data
- Learning artifacts generated for every scenario
- Reusable pattern documented for future epics
