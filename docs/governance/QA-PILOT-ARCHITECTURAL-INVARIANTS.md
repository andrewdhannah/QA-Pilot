# QA-Pilot Architectural Invariants

**Date:** 2026-08-11
**Status:** FROZEN
**Source:** E2E-1 through E2E-9 session

---

## Permanent Invariants

These invariants are frozen and must not be violated by any future QA-Pilot development.

### 1. Authority Boundary

```
QA-Pilot may discover that its test was wrong.
QA-Pilot may correct its testing machinery.
QA-Pilot does not rewrite the target's result to make the target pass.
```

### 2. Result Semantics

```
FAIL ≠ governance verdict
constructed test ≠ executed test
observed result ≠ governance disposition
structural freeze ≠ semantic freeze
claimed capability ≠ qualified capability
```

### 3. Evidence Chain

```
Historical Claim
      ↓ independent extraction
Requirement
      ↓ agent construction
Test
      ↓ runner
Execution
      ↓ observation
Result
      ↓ evidence preservation
Evidence
      ↓ Owner/governance interpretation
Disposition
```

No stage may manufacture the authority of the next stage.

### 4. Capability Bounding

```
Requirement
     ↓
Required capability
     ↓
Qualified?
 ┌───┴───┐
 NO     YES
 │       │
CAPABILITY  execute
_MISSING     │
             ▼
        observation
             │
             ▼
          result
```

The test generator should never silently downgrade a requirement because it lacks a capability.

### 5. Test Type as Property

```
Test type is a property of the derived requirement, not a special mode in the engine.
```

### 6. Assurance Source Independence

```
QA-Pilot does not inherit target authority merely because it tests the target.
The target remains the target.
The governing system remains the governing system.
QA-Pilot remains the testing node.
```

### 7. Reproducibility

```
Structural reproducibility: same artifacts produce same structure
Observational reproducibility: same artifacts produce same observations
Divergences: attributed to target/environment, not silently absorbed
```

### 8. Evidence Preservation

```
Original results preserved unchanged.
Dispositions added as additive layer.
Defective results preserved as evidence.
No silent overwrites.
```

---

## Derived Rules

### From E2E-1: Finding Disposition

```
A finding is an observation, not a governance verdict.
Classification adds disposition, does not alter result.
UNRESOLVED is a valid first-class outcome.
```

### From E2E-4: Historical Assurance

```
Historical assurance is not timeless assurance.
Requirements derived from sealed history may not apply to current behavior.
The assurance pipeline must distinguish source fact from source interpretation.
```

### From E2E-8: Corpus Integrity

```
307 PASS ≠ "Librarian has 307 independently proven requirements"
307 PASS = "307 currently executable assertions passed after QA-Pilot's reconstruction was corrected"
```

### From E2E-9: Portability

```
QA-Pilot has demonstrated target portability across materially different targets
and modalities without testing-engine modification.
```

---

## Capability Registry Invariant

```
New testing modality
        ↓
Required capability
        ↓
Skill discovery
        ↓
Capability qualification
        ↓
Adapter qualification
        ↓
Tests can use it
```

Adding a capability is a governed qualification process, not a simple flag toggle.

---

## Assurance Compiler Invariants

### 9. Source ≠ Requirement ≠ Test ≠ Execution ≠ Result ≠ Disposition

```
SOURCE
  ≠ REQUIREMENT
  ≠ TEST
  ≠ EXECUTION
  ≠ RESULT
  ≠ DISPOSITION
```

Each arrow is independently auditable.

### 10. Derivation Does Not Establish Truth

```
QA-Pilot may derive an assurance requirement from a source,
but derivation does not establish the truth of the source.

Execution does not establish the correctness of the requirement.

Observation does not establish governance disposition.
```

### 11. Dimensions Are Properties, Not Engine Modes

```
Assurance dimensions (REGRESSION, CONTRACT, BOUNDARY, etc.)
are properties of the derived requirement, not special modes
in the execution engine.
```

### 12. Capability Principle

```
A new assurance requirement does not justify a new engine path.
It first attempts resolution through the existing Capability Registry.
A new capability is introduced only when an actual requirement
cannot be satisfied by an existing qualified capability.
```

---

## The Assurance Compiler Model

```
QA-Pilot is a substrate-agnostic assurance compiler capable of
deriving, constructing, executing, and preserving evidence for
independently testable properties of governed or external systems.
```

---

*Invariants frozen — violations require explicit Owner decision.*
