# QA Pilot Security Qualification — Implementation Roadmap

**Sprint:** QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1
**Status:** Planning — defines the sequence of implementation sprints that follow this planning sprint
**Note:** This roadmap describes what *could* be built. No implementation is authorized by this document.

---

## 0. Dependency Chain

This roadmap is the implementation sequence for the security qualification domain. It depends on the architecture defined in `QA-PILOT-QUALIFICATION-ARCHITECTURE.md` and the taxonomy defined in `QA-PILOT-SECURITY-TAXONOMY.md`.

The roadmap sequence is ordered such that each sprint produces contracts consumed by the next. No sprint assumes implementation that does not yet exist.

---

## 1. Sprint Inventory

### Series A: Foundation (4 sprints)

---

#### A1 — QA-PILOT-QUALIFICATION-PROFILE-SCHEMA-1

**Objective:** Extend the Node Profile schema with the qualification manifest.

| Attribute | Value |
|-----------|-------|
| **Owner** | Librarian (schema change) / QA Pilot (validation) |
| **Contracts introduced** | Qualification profile extension to Node Profile schema |
| **State machine** | None — profile is configuration |
| **Database changes** | Node Profile schema extended with `qualification_profile` block |
| **API changes** | Node Registry read endpoints expose qualification_profile |
| **UI impact** | None |
| **Tests required** | Valid/invalid qualification profile fixtures; schema validation tests |
| **Dependencies** | Node Registry schema (existing) |
| **Acceptance gates** | |
| QP-PROFILE-1 | Qualification profile extension defined as Draft 2020-12 schema |
| QP-PROFILE-2 | Domain, level, release_gate, exceptions fields validated |
| QP-PROFILE-3 | Inheritance rules documented |
| QP-PROFILE-4 | Override rules documented and validated |
| QP-PROFILE-5 | Validator created with 10 business rules |
| QP-PROFILE-6 | Test runner 10/10 passes |

---

#### A2 — QA-PILOT-QUALIFICATION-RECEIPT-1

**Objective:** Implement the qualification receipt as an extension of the existing Evidence Receipt.

| Attribute | Value |
|-----------|-------|
| **Owner** | QA Pilot (receipt schema + validator) |
| **Contracts introduced** | Qualification receipt schema (inherits Evidence Receipt) |
| **State machine** | None — receipts are append-only |
| **Database changes** | Qualification receipt type added to receipt store |
| **API changes** | None |
| **UI impact** | None |
| **Tests required** | Valid/invalid qualification receipt fixtures; inheritance validation |
| **Dependencies** | Evidence Receipt schema (existing) |
| **Acceptance gates** | |
| QP-RCPT-1 | Qualification receipt schema extends Evidence Receipt (validated) |
| QP-RCPT-2 | All Evidence Receipt fields inherited without modification |
| QP-RCPT-3 | Qualification-specific fields (domain, test_class, component_refs, etc.) defined |
| QP-RCPT-4 | Validator created with 10 business rules |
| QP-RCPT-5 | Test runner 10/10 passes |
| QP-RCPT-6 | No parallel receipt system created |

---

#### A3 — QA-PILOT-QUALIFICATION-TEST-IDENTITY-1

**Objective:** Implement the stable test identity model with versioned revisions.

| Attribute | Value |
|-----------|-------|
| **Owner** | QA Pilot |
| **Contracts introduced** | Test identity schema, revision lifecycle, invalidation rules |
| **State machine** | ACTIVE → STALE (component changed) → RETIRED (component removed) |
| **Database changes** | Test identity registry (QA Pilot-local, not Node Registry) |
| **API changes** | None |
| **UI impact** | None |
| **Tests required** | Identity creation, revision bump, staleness detection, retirement validation |
| **Dependencies** | None |
| **Acceptance gates** | |
| QP-ID-1 | Test identity schema defined (base_id, revision, component_ref, status) |
| QP-ID-2 | Revision lifecycle defined (increment rules, component version binding) |
| QP-ID-3 | Invalidation rules defined (component removed → retired) |
| QP-ID-4 | Receipt lineage linking defined (identity → receipt chain) |
| QP-ID-5 | Validator created with 8 business rules |
| QP-ID-6 | Test runner 8/8 passes |

---

#### A4 — QA-PILOT-QUALIFICATION-COVERAGE-ENGINE-1

**Objective:** Implement the coverage analysis engine that produces gap reports.

| Attribute | Value |
|-----------|-------|
| **Owner** | QA Pilot |
| **Contracts introduced** | Coverage calculation rules (from coverage model doc) |
| **State machine** | None — stateless calculation |
| **Database changes** | None |
| **API changes** | Coverage report output format |
| **UI impact** | None |
| **Tests required** | Per-component score, per-domain score, aggregate score, gap detection (6 types) |
| **Dependencies** | A1 (qualification profile), A2 (receipts), A3 (test identity) |
| **Acceptance gates** | |
| QP-COV-1 | Interface coverage calculation validated |
| QP-COV-2 | Authority coverage calculation validated |
| QP-COV-3 | Domain coverage calculation validated |
| QP-COV-4 | Change coverage calculation validated |
| QP-COV-5 | All 6 gap types detected and reported correctly |
| QP-COV-6 | Coverage level inheritance rules enforced |
| QP-COV-7 | Edge case handling validated |
| QP-COV-8 | Test runner 15/15 passes |

---

### Series B: Security Test Generation (3 sprints)

---

#### B1 — QA-PILOT-SECURITY-GENERATOR-STRUCTURAL-1

**Objective:** Implement the structural security test generator — enumerates interfaces and produces basic existence/auth tests.

| Attribute | Value |
|-----------|-------|
| **Owner** | QA Pilot |
| **Contracts introduced** | Structural test generation rules |
| **State machine** | None — generator is stateless |
| **Database changes** | None |
| **API changes** | None |
| **UI impact** | None |
| **Tests required** | Test generation from route metadata, authority model, schema required fields |
| **Dependencies** | A3 (test identity), A4 (coverage engine) |
| **Acceptance gates** | |
| QP-STRUCT-1 | Generator reads component metadata and produces structural tests |
| QP-STRUCT-2 | Authentication tests generated for all authority_boundary endpoints |
| QP-STRUCT-3 | Route enumeration covers all registered interfaces |
| QP-STRUCT-4 | Test identities generated with correct base_id pattern |
| QP-STRUCT-5 | Generator respects component version boundaries |
| QP-STRUCT-6 | Test runner 12/12 passes |

---

#### B2 — QA-PILOT-SECURITY-GENERATOR-ADVERSARIAL-1

**Objective:** Implement the adversarial security test generator — applies template suites based on component classification.

| Attribute | Value |
|-----------|-------|
| **Owner** | QA Pilot |
| **Contracts introduced** | Adversarial test generation rules, classification-to-template mapping |
| **State machine** | None — generator is stateless |
| **Database changes** | None |
| **API changes** | None |
| **UI impact** | None |
| **Tests required** | Template selection by classification, adversarial test generation per category |
| **Dependencies** | B1 (structural generator), QA-PILOT-SECURITY-TAXONOMY.md (§3 mapping) |
| **Acceptance gates** | |
| QP-ADV-1 | Classification-to-template mapping implemented for all 10 classifications |
| QP-ADV-2 | Adversarial tests generated for authority_boundary components |
| QP-ADV-3 | AI Governance adversarial tests generated for AI-facing components |
| QP-ADV-4 | Template parameterization works (routes, methods, expected status) |
| QP-ADV-5 | Test runner 15/15 passes |

---

#### B3 — QA-PILOT-SECURITY-GENERATOR-BEHAVIORAL-1

**Objective:** Implement the behavioral test generator — derives tests from contracts, schemas, and state machines.

| Attribute | Value |
|-----------|-------|
| **Owner** | QA Pilot |
| **Contracts introduced** | Behavioral test generation rules |
| **State machine** | None — generator is stateless |
| **Database changes** | None |
| **API changes** | None |
| **UI impact** | None |
| **Tests required** | Schema-derived tests (missing required field, wrong type, boundary values) |
| **Dependencies** | A3 (test identity), B1 (structural generator) |
| **Acceptance gates** | |
| QP-BEH-1 | Schema required fields produce rejection tests |
| QP-BEH-2 | State machine transitions produce valid/invalid transition tests |
| QP-BEH-3 | Dependency inventory produces scanning/validation tests |
| QP-BEH-4 | Behavioral tests include code location references |
| QP-BEH-5 | Test runner 12/12 passes |

---

### Series C: Execution and Integration (3 sprints)

---

#### C1 — QA-PILOT-QUALIFICATION-EXECUTION-HARNESS-1

**Objective:** Implement the qualification execution harness that runs generated tests and produces receipts.

| Attribute | Value |
|-----------|-------|
| **Owner** | QA Pilot |
| **Contracts introduced** | Execution harness contract, qualification artifact store schema |
| **State machine** | IDLE → GENERATING → EXECUTING → AGGREGATING → REPORTED |
| **Database changes** | Qualification artifact store (QA Pilot-local) |
| **API changes** | Qualification execution trigger |
| **UI impact** | None |
| **Tests required** | End-to-end execution flow, receipt generation, artifact storage |
| **Dependencies** | A2 (receipts), A3 (test identity), B1-B3 (generators) |
| **Acceptance gates** | |
| QP-EXEC-1 | Execution harness runs structural → behavioral → adversarial sequence |
| QP-EXEC-2 | Receipt generated for each executed test |
| QP-EXEC-3 | Aggregate qualification receipt produced per component |
| QP-EXEC-4 | Artifacts stored in qualification artifact store |
| QP-EXEC-5 | Test runner 12/12 passes |

---

#### C2 — QA-PILOT-QUALIFICATION-PUSH-EVENT-1

**Objective:** Implement the push event integration between Librarian and QA Pilot.

| Attribute | Value |
|-----------|-------|
| **Owner** | Librarian (event publisher) / QA Pilot (event consumer) |
| **Contracts introduced** | Push event schema, scope definition |
| **State machine** | None (event is stateless trigger) |
| **Database changes** | None |
| **API changes** | Librarian event publisher MCP tool; QA Pilot event consumer endpoint |
| **UI impact** | None |
| **Tests required** | Event publication, event consumption, scope filtering, trigger execution |
| **Dependencies** | C1 (execution harness) |
| **Acceptance gates** | |
| QP-PUSH-1 | SPRINT_SEALED event published with changed_targets and qualification_required |
| QP-PUSH-2 | QA Pilot consumes event and triggers targeted qualification |
| QP-PUSH-3 | Scope filtering works (only changed targets re-qualified) |
| QP-PUSH-4 | Receipt returned to Librarian and evidence chain updated |
| QP-PUSH-5 | Test runner 10/10 passes |

---

#### C3 — QA-PILOT-QUALIFICATION-COVERAGE-FEEDBACK-1

**Objective:** Implement the coverage gap feedback loop — detect, report, and track coverage improvements across sprints.

| Attribute | Value |
|-----------|-------|
| **Owner** | QA Pilot |
| **Contracts introduced** | Coverage trend report format |
| **State machine** | None (trend reporting is read-only) |
| **Database changes** | Coverage history table (QA Pilot-local) |
| **API changes** | Coverage trend query endpoint |
| **UI impact** | Dashboard coverage card (read-only) |
| **Tests required** | Trend calculation, improvement detection, regression alerting |
| **Dependencies** | A4 (coverage engine), C2 (push event) |
| **Acceptance gates** | |
| QP-FEED-1 | Coverage trends tracked across sprint boundaries |
| QP-FEED-2 | Coverage improvement detected and reported |
| QP-FEED-3 | Coverage regression detected and alerted |
| QP-FEED-4 | Coverage trend report format defined |
| QP-FEED-5 | Test runner 10/10 passes |

---

## 2. Complete Dependency Graph

```
A1 (Profile Schema) ──────┐
                          │
A2 (Receipt) ─────────────┤
                          │
A3 (Test Identity) ───────┤
                          │
A4 (Coverage Engine) ◄────┘
        │
        ├──────────────────────────┐
        │                          │
B1 (Structural Gen)         B2 (Adversarial Gen)
        │                          │
        ├──────────────────────────┘
        │
B3 (Behavioral Gen)
        │
        └──────────────────────────┐
                                   │
C1 (Execution Harness) ◄──────────┘
        │
C2 (Push Event)
        │
C3 (Coverage Feedback)
```

---

## 3. Optional / Future Sprints

These are not in the critical path and may be deferred or skipped:

| Sprint | Purpose | Dependency |
|--------|---------|------------|
| QA-PILOT-SECURITY-DOMAIN-TEST-CATALOG-1 | Define process for maintaining human-authored domain tests | B3 |
| QA-PILOT-QUALIFICATION-UI-SURFACE-1 | Dashboard coverage visualization | C3 |
| QA-PILOT-QUALIFICATION-MATERIALIZE-1 | Authorized test materialization to target repos | C1 (requires separate Owner authorization) |
| QA-PILOT-SECURITY-FUZZ-INTEGRATION-1 | Fuzz testing integration | B2 |

---

## 4. Implementation Ordering Rules

1. **Foundation before generation.** Series A must complete before Series B begins. The identity, receipt, and coverage models are prerequisites for any test generation.
2. **Generation before execution.** Series B must complete before Series C begins. The execution harness runs generators.
3. **Push before feedback.** C2 (push event) should precede C3 (coverage feedback) because feedback requires deterministic triggers.
4. **Parallel within series.** Within Series A, A2 (receipt) and A3 (identity) can proceed in parallel. Within Series B, B1 (structural) and B2 (adversarial) can proceed in parallel since they consume different input types.

---

## 5. Estimation Notes

| Series | Sprints | Dependencies | Owner Supervision |
|--------|---------|--------------|-------------------|
| A — Foundation | 4 | Existing Node Registry, Evidence Receipt | OWNER_SUPERVISED (new contracts) |
| B — Generation | 3 | Series A | DELEGATED_DISPATCH (mechanical) |
| C — Execution | 3 | Series B | DELEGATED_DISPATCH (mechanical) |
| **Total** | **10** | | |

Series A requires Owner supervision because it introduces new contracts (qualification profile, receipt extension, identity model). Series B and C are mechanical implementations of defined contracts and can use delegated dispatch.

---

*Implementation roadmap for QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1. Planning only. No implementation authority conferred.*
