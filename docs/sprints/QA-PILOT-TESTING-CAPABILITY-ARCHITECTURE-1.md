# QA-PILOT-TESTING-CAPABILITY-ARCHITECTURE-1 — Testing Capability Architecture

**Type:** assessment / architecture definition
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** architecture
**Boundary:** QA Pilot-local, Librarian advisory boundary
**Librarian impact:** integration interface definition (non-mutating)

---

## Purpose

Define QA Pilot as a reusable project-agnostic testing capability that consumes application structure, requirements, Librarian planning context, governance constraints, and previous evidence to generate test artifacts.

---

## Deliverables

### 1. Input Contract

Define what QA Pilot can consume from three sources:

| Source | Content |
|--------|---------|
| Project Context | Application identity, repository structure, runtime configuration, technology stack, deployment model |
| Librarian Context | Approved requirements, sprint intent, acceptance criteria, known risks, evidence history |
| Application Knowledge | Routes, UI surfaces, modules, APIs, data models, dependencies |

### 2. Test Artifact Model

Define a common base test artifact schema and specializations:

**Base:**
```
TestArtifact
  identity
  source_context
  intent
  classification
  execution_method
  expected_outcome
  evidence_output
  authority_level
```

**Specializations:**
- SecurityTest
- UATScenario
- RegressionTest
- PerformanceTest
- AccessibilityTest
- LanguageTest

### 3. Execution Model

Define the generation and evidence lifecycle:

```
Generate → Validate → Execute → Capture Evidence → Report → Attach to Librarian
```

**Governance boundary:** QA Pilot generates evidence. It does not make acceptance decisions. This preserves the existing advisory-only governance model.

### 4. Librarian Integration Boundary

| Librarian (decision authority) | → | QA Pilot (validation authority) |
|-------------------------------|----|--------------------------------|
| Sprint intent | → | Validation plans |
| Approved scope | → | Execution results |
| Constraints | → | Evidence packages |
| Decision history | → | Observations |

### 5. Capability Roadmap

| Phase | Capability | Rationale |
|-------|------------|-----------|
| 1 | Regression, UAT, Language | Existing evidence chains; concrete patterns from #170–#173 |
| 2 | Accessibility | Static analysis + UI validation |
| 3 | Performance | Requires workload definitions |
| 4 | Security | Highest governance sensitivity; strongest boundaries needed |

---

## Scope

### Included

- Architecture documentation
- Input contract schemas
- Test artifact model
- Execution model
- Librarian integration interface
- Capability roadmap

### Explicit Non-Scope

| Excluded | Reason |
|----------|--------|
| Implementation of any testing capability | Architecture sprint — defines, does not build |
| QASimulator i18n migration | Reclassified as first implementation pilot of language testing capability |
| capstone-2 migration | Deferred to post-architecture implementation |
| Build output consolidation | Deferred |
| Product behavior changes | Architecture only |

---

## Relation to #177

`QA-PILOT-QASIMULATOR-I18N-MIGRATION-1` (ledger #177) is retained as the first implementation candidate after this architecture contract exists. It is reclassified conceptually from "isolated migration" to "language testing capability pilot."

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| CA-1 | Input contract defined |
| CA-2 | Test artifact model defined |
| CA-3 | Execution model defined |
| CA-4 | Librarian integration boundary defined |
| CA-5 | Capability roadmap produced |
| CA-6 | No implementation changes made |
| CA-7 | Evidence produced |

---

**Status:** ✅ AUTHORIZED — Owner-authorized 2026-07-20
**Authorized by:** Andrew Hannah
**Ledger entry:** #178 (authorized)
