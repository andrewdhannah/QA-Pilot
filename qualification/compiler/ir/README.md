# Qualification Compiler — IR Design

## Overview

The Qualification Intermediate Representation (IR) is the compiler artifact between an epic contract and a generated test suite. It formalizes the pattern proven by the SNA qualification (68 tests, 9 layers) into a reusable, composable transformation.

## Files

| File | Purpose |
|------|---------|
| `qualification-ir.schema.json` | JSON Schema (Draft 2020-12) for the IR |
| `sna-epic-ir.json` | Example IR instance derived from the SNA epic contract |
| `qualification-evidence.schema.json` | JSON Schema for the evidence output format |
| `TRANSFORMATION-RULES.md` | How contract elements map to test families |

## Design Principles

1. **Contract-derived, not implementation-derived.** The IR captures tests derived from the epic contract's invariants, gates, and rules — never from the implementation code.

2. **Provenance-traced.** Every test carries `source_contract_elements` that trace back to the specific contract element it validates. This enables forward tracing (contract → tests) and backward tracing (failed test → contract element at risk).

3. **Composable.** Multiple IRs can be merged via `parent_ir_refs`. The schema supports IRs derived from multiple contract sources.

4. **Schema-validated.** Both the IR and the evidence output use JSON Schema Draft 2020-12. The compiler validates the IR before codegen.

5. **Deterministic.** Given the same contract + same compiler version, the IR is deterministic. The source hash proves which contract version was used.

## IR Structure

```
QualificationIR
├── ir_metadata          # Provenance, versioning, lineage
├── contract_source      # Structured extraction of the epic contract
│   ├── governing_invariant
│   ├── invariants[]     # 6 invariants (INV-1 through INV-6)
│   ├── acceptance_gates[]  # 5 gates (GATE-A through GATE-E)
│   ├── authority_constraints[]
│   ├── lifecycle_rules[]   # Legal and illegal transitions
│   ├── stop_conditions[]
│   ├── evidence_requirements[]
│   ├── scope
│   └── two_layer_defense
├── derivation_plan      # How contract → tests
│   ├── layer_derivations[]   # Exactly 9 layers
│   │   └── test_families[]
│   │       └── test_patterns[]
│   ├── adversarial_rules[]   # 6 attack vectors
│   └── positive_rules[]      # 4 legitimate workflows
└── output_spec          # What the compiled output looks like
    ├── layers[]
    ├── evidence_format
    └── disposition_rules
```

## The 9 Layers

| # | Layer | Question Answered | Source Contract Elements |
|---|-------|-------------------|------------------------|
| 1 | Contract | Does the invariant have unambiguous acceptance criteria? | All invariants, gates |
| 2 | Workflow | Can every supported lifecycle path be exercised? | Legal transitions |
| 3 | Negative | Can any forbidden state be produced? | Illegal transitions |
| 4 | Concurrency | Can races defeat reservation/binding? | Atomicity requirements |
| 5 | Persistence | Can restart/mutation/recovery bypass controls? | Persistence-layer defenses |
| 6 | Interface | Can MCP/API/CLI paths bypass the allocator? | Scope boundaries |
| 7 | Exceptional | Can import/restore/clone/recovery create a violation? | Import classification rules |
| 8 | Evidence | Can QA-Pilot independently prove the observed result? | Evidence requirements |
| 9 | Regression | Does the existing test suite remain clean? | Existing infrastructure |

## Test Pattern Assertion Types

| Type | Semantics |
|------|-----------|
| `element_exists` | Element exists and is accessible |
| `structure_valid` | Element conforms to expected structure |
| `state_transition_allowed` | Transition succeeds |
| `state_transition_rejected` | Transition is rejected (defense working) |
| `contention_exactly_one_winner` | N-way race produces exactly 1 winner |
| `tamper_detected` | File/state manipulation is detected |
| `path_convergence` | All paths converge through the allocator |
| `evidence_produced` | Evidence artifact exists and is well-formed |
| `deterministic_outcome` | Operation produces a predictable result |
| `lifecycle_completes` | Full lifecycle path executes successfully |

## Composability

Multiple IRs can be composed:

```json
{
  "ir_metadata": {
    "ir_id": "IR-COMPOSED-1",
    "parent_ir_refs": ["IR-SNA-EPIC-1", "IR-ANOTHER-CONTRACT-1"]
  }
}
```

The compiler merges `contract_source` elements (deduplicating by ID), concatenates `derivation_plan` arrays, and unions `adversarial_rules` and `positive_rules`.

## Usage

1. **Author an IR** from an epic contract (manual + semi-automated)
2. **Validate** the IR against `qualification-ir.schema.json`
3. **Compile** the IR to a Python test suite via the codegen pass
4. **Execute** the test suite
5. **Emit evidence** conforming to `qualification-evidence.schema.json`
6. **Verify provenance** by walking the `source_contract_elements` chain
