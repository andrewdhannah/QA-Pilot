# QA-Pilot Assurance Compiler — Architecture Vision

**Date:** 2026-08-11
**Status:** DIRECTIONAL (not sealed implementation law)
**Source:** E2E-1 through E2E-9 session + architectural discussion

---

## Architectural Thesis

> QA-Pilot is an assurance compiler, not a collection of test-type implementations.

It derives assurance requirements from authoritative sources, compiles them into executable artifacts, and preserves evidence — without embedding target-specific logic or test-type-specific execution paths.

---

## The Five Stages

```
1. DISCOVER
   Find authoritative assurance sources
          │
          ▼
2. DERIVE
   Convert source material into normalized
   assurance requirements
          │
          ▼
3. CONSTRUCT
   Compile requirements into executable
   test artifacts using qualified capabilities
          │
          ▼
4. EXECUTE
   Run frozen artifacts against a target
          │
          ▼
5. PRESERVE
   Produce evidence + provenance + results
```

Governance projection sits after observation, not inside the testing engine.

---

## Source Model

| Source Class | Example | Derived Assurance Class |
|---|---|---|
| Historical sealed claims | Sprint ledger, acceptance criteria | Regression |
| JSON schemas / contracts | API schemas, data contracts | Contract |
| Governance invariants | Authority boundaries, custody rules | Boundary |
| Failure semantics | Error handling, rejection behavior | Negative |
| Lifecycle definitions | State machines, cursor transitions | State transition |
| Runtime-observable behavior | MCP endpoints, API surfaces | Integration |

---

## Compilation Pipeline

```
AUTHORITATIVE SOURCES
        │
        ▼
Source Discovery
        │
        ▼
Claim / Property Extraction
        │
        ▼
Test Requirement
        │
        ▼
Requirement Classification
        │
        ▼
Capability Resolution
        │
        ▼
Target Adapter Resolution
        │
        ▼
Test Construction
        │
        ▼
Frozen Test Artifact
        │
        ▼
Execution
        │
        ▼
Observation
        │
        ▼
Evidence
        │
        ▼
Governance Projection
```

---

## Test Type as Derived Metadata

A requirement carries assurance dimensions, not a single test type:

```yaml
requirement:
  id: "REQ-001"
  source:
    kind: CONTRACT
    reference: "schema/execution-receipt.schema.json"
  property: "Receipt must contain integrity_hash field"
  assurance_dimensions:
    - CONTRACT
    - BOUNDARY
  required_capabilities:
    - SCHEMA_VALIDATION
  target_adapter: "cli"
  provenance:
    extracted_from: "execution-receipt.schema.json"
    extracted_at: "2026-08-11T00:00:00Z"
```

This prevents the future engine from becoming:

```python
# DON'T DO THIS
if test_type == "boundary":
    ...
elif test_type == "regression":
    ...
elif test_type == "negative":
    ...
```

---

## Capability Principle

> A new assurance requirement does not justify a new engine path. It first attempts resolution through the existing Capability Registry. A new capability is introduced only when an actual requirement cannot be satisfied by an existing qualified capability.

```
New assurance requirement
        │
        ▼
Existing capability?
    ┌───┴───┐
   YES     NO
    │       │
    ▼       ▼
  use     CAPABILITY_MISSING
 existing    │
 capability  ▼
          qualify capability
               │
               ▼
          qualify adapter
               │
               ▼
          test target
```

---

## Authority Invariant

```
QA-Pilot discovers.
QA-Pilot derives.
QA-Pilot constructs.
QA-Pilot executes.
QA-Pilot observes.
QA-Pilot preserves evidence.

QA-Pilot does NOT decide what the observation means
for the target's governance state.
```

---

## The Invariant Chain

```
SOURCE
  ≠ REQUIREMENT
  ≠ TEST
  ≠ EXECUTION
  ≠ RESULT
  ≠ DISPOSITION
```

And:

```
QA-Pilot may derive an assurance requirement from a source,
but derivation does not establish the truth of the source.

Execution does not establish the correctness of the requirement.

Observation does not establish governance disposition.
```

Each arrow is independently auditable.

---

## Corpus Model

```
Target
  ↓
Assurance Profile
  ├── discoverable properties
  ├── executable requirements
  ├── capability gaps
  └── generated assurance corpus
```

The corpus retains:

```
SOURCE CLAIM
    ≠
DERIVED REQUIREMENT
    ≠
TEST ARTIFACT
    ≠
OBSERVATION
    ≠
GOVERNANCE DISPOSITION
```

---

## What E2E-1 Through E2E-9 Proved

| E2E | Claim Proved |
|-----|--------------|
| E2E-1 → E2E-3 | Modality independence (MCP, browser, CLI) |
| E2E-4 → E2E-8 | Historical assurance reconstruction |
| E2E-9 | Target independence (externally originated) |
| Classification pilot | Self-discovery of derivation defects |

## What E2E-10 Through E2E-13 Will Prove

| E2E | Claim to Prove |
|-----|----------------|
| E2E-10 | Multi-source derivation without target-specific logic |
| E2E-11 | Multi-type construction through same pipeline |
| E2E-12 | Multi-type execution without test-type-specific runners |
| E2E-13 | Multi-type reproducibility |

---

## The Stronger Claim

```
                  QA-PILOT
                      │
             ASSURANCE COMPILER
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
   Librarian       Openwork       Project X
       │              │              │
       ├─ historical  ├─ contracts  ├─ contracts
       ├─ contracts   ├─ boundaries ├─ runtime
       ├─ boundaries  ├─ negative   └─ history
       └─ lifecycle   └─ runtime
              │
              ▼
       NORMALIZED ASSURANCE
          REQUIREMENTS
              │
              ▼
       SAME QA-PILOT ENGINE
```

Not "QA-Pilot can test different targets" but "QA-Pilot can compile assurance from different source classes using the same pipeline."

---

## Relationship to Other Contracts

| Document | Scope | Status |
|---|---|---|
| Testing Node Contract | What QA-Pilot is allowed to do and own | SEALED |
| Target Adapter Contract | How QA-Pilot couples to a target | ESTABLISHED |
| Capability Registry | What QA-Pilot is currently qualified to do | VALIDATED |
| **This document** | **What the system is being built toward** | **DIRECTIONAL** |

---

## What This Document Is NOT

- This is not sealed implementation law
- This is not a specification that must be followed exactly
- This is an architectural direction that guides development
- The testing node contract remains the normative boundary
- New capabilities are added only when actual requirements demand them

---

*Architecture vision — directional, not normative.*
