# Qualification Compiler — Transformation Rules

**IR Schema:** `qualification-ir.schema.json`
**IR Instance:** `sna-epic-ir.json`
**Derived from:** SNA qualification suite (`qa-pilot-sna-independent-qualification.py`)

---

## 1. Transformation Pipeline

```
EPIC CONTRACT (JSON)
       │
       ▼
┌─────────────────────┐
│  EXTRACTION PASS    │  Parse contract → ContractSource
│  (schema-validated) │  Map free-text → structured elements
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  DERIVATION PASS    │  ContractSource → DerivationPlan
│  (rule-driven)      │  Each contract element → test families
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  CODEGEN PASS       │  DerivationPlan → Python test suite
│  (template-based)   │  Test patterns → pytest functions
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  EVIDENCE PASS      │  Test results → QualificationResult
│  (deterministic)    │  Structured evidence output
└─────────────────────┘
```

## 2. Extraction Rules

### 2.1 Contract → ContractSource

| Contract Field | IR Field | Transform |
|----------------|----------|-----------|
| `governing_invariant` | `contract_source.governing_invariant.statement` | Direct copy |
| `governing_invariant` | `contract_source.governing_invariant.testable_form` | Manual predicate translation (required at IR authoring time) |
| `invariants[N]` | `contract_source.invariants[N]` | Each gets `invariant_id`, `statement`, `testable_form`, `violation_shape`, `defense_layers` |
| `acceptance_gates[N]` | `contract_source.acceptance_gates[N]` | Each gets `gate_id`, `statement`, `testable_form`, `evidence_sources` |
| `stop_conditions[N]` | `contract_source.stop_conditions[N]` | Each gets `condition_id`, `predicate`, `severity`, `message` |
| `scope` | `contract_source.scope` | Direct copy |
| `two_layer_defense` | `contract_source.two_layer_defense` | Direct copy |

### 2.2 Derived Elements

| Derived Field | Source | Rule |
|---------------|--------|------|
| `lifecycle_rules` | Contract sprints + invariant analysis | Each state transition becomes a rule with `from_state`, `to_state`, `condition`, `is_legal` |
| `authority_constraints` | `scope.forbidden` + audit findings | Each forbidden item becomes a constraint with `boundary_type` |
| `evidence_requirements` | Contract acceptance criteria + QA-Pilot pattern | Each acceptance gate maps to evidence requirements |

## 3. Derivation Rules

### 3.1 Layer 1 (Contract) — Structural Validation

**Source elements:** All invariants, all gates

**Rule:** For each contract element, generate a test that asserts the element exists, is well-formed, and has unambiguous acceptance criteria.

```
FOR EACH invariant IN contract_source.invariants:
  EMIT TestPattern {
    pattern_id: "C-{seq}",
    assertion_type: "element_exists" | "structure_valid",
    assertion: "{element}.exists ∧ {element}.has_testable_form"
  }
```

**Concrete mapping from SNA:**
- 6 invariants → C-004 (count check)
- 5 gates → C-005 (count check)
- Governing invariant → C-002 (exists)
- Stop conditions → C-007 (exists)
- Two-layer defense → C-009 (both layers documented)

### 3.2 Layer 2 (Workflow) — Happy Path Exercise

**Source elements:** Invariants with `defense_layers: ["application"]`, lifecycle rules with `is_legal: true`

**Rule:** For each legal lifecycle transition, generate a test that exercises the full path.

```
FOR EACH rule IN lifecycle_rules WHERE rule.is_legal == true:
  EMIT TestFamily {
    family_id: "WF-{transition_name}",
    source_contract_elements: [rule.rule_id, related_invariants],
    test_patterns: [
      { exercise path through rule },
      { verify binding/provenance },
      { verify edge case (release, re-reserve) }
    ]
  }
```

**Concrete mapping from SNA:**
- LR-1 (RESERVE) + LR-2 (BIND) → W-001 (create sprint)
- LR-3 (BUILD) → W-002 (can_build check)
- INV-3 (binding) → W-003 (verify binding)
- INV-3 → W-004 (provenance export)
- LR-6 (RELEASE) → W-005 (release and re-reserve)
- INV-1 → W-006 (committed number rejection)

### 3.3 Layer 3 (Negative) — Forbidden State Fabrication

**Source elements:** Invariants with `violation_shape`, lifecycle rules with `is_legal: false`

**Rule:** For each forbidden transition, generate a test that ATTEMPTS the forbidden operation and asserts rejection.

```
FOR EACH rule IN lifecycle_rules WHERE rule.is_legal == false:
  EMIT TestPattern {
    pattern_id: "N-{seq}",
    assertion_type: "state_transition_rejected",
    assertion: "¬{rule.condition}"
  }
```

**Concrete mapping from SNA:**
- LR-7 (build without reservation) → N-001
- LR-11 (duplicate reservation) → N-006
- INV-3 (wrong sprint binding) → N-003, N-007
- LR-9 (seal without reservation) → N-004
- LR-10 (seal with released) → N-005
- INV-1 (expiry) → N-008

### 3.4 Layer 4 (Concurrency) — Race Condition Tests

**Source elements:** GATE-B (contention produces exactly one winner), INV-1 (atomic reservation)

**Rule:** For each contention point, generate N-way race tests with barrier synchronization.

```
FOR EACH contention_point IN contract_source WHERE atomicity_required:
  FOR EACH concurrency_level IN [2, 10]:
    EMIT TestPattern {
      pattern_id: "CC-{seq}",
      assertion_type: "contention_exactly_one_winner",
      assertion: "barrier_sync({level}) ∧ {operation} → |{success}| == 1"
    }
```

**Concrete mapping from SNA:**
- GATE-B → CC-001 (2-way race for same number)
- GATE-B → CC-002 (10-way race for same number)
- INV-1 → CC-003 (concurrent bind)

### 3.5 Layer 5 (Persistence) — File-Level Defense Tests

**Source elements:** INV-5 (persistence enforces uniqueness), GATE-D (bypass rejected at persistence)

**Rule:** For each persistence-layer defense, generate tests that manipulate the store file directly.

```
FOR EACH persistence_defense IN INV-5.defense_layers:
  EMIT TestFamily {
    test_patterns: [
      { tamper with JSON → allocator detects },
      { delete store → allocator handles gracefully },
      { corrupt JSON → allocator raises or recovers },
      { concurrent writes → atomicity preserved },
      { seal reads from persisted state }
    ]
  }
```

**Concrete mapping from SNA:**
- INV-5 → P-001 (JSON injection)
- INV-5 → P-002 (file deletion)
- INV-5 → P-003 (corrupt JSON)
- GATE-B + INV-5 → P-004 (concurrent writes)
- INV-4 + INV-5 → P-005 (seal against persisted state)

### 3.6 Layer 6 (Interface) — Code Path Audit

**Source elements:** INV-2 (no alternate mechanisms), GATE-A (all paths use allocator)

**Rule:** For each external interface surface (MCP, CLI, import), verify convergence through allocator.

```
FOR EACH interface_surface IN [MCP, CLI, IMPORT, REPAIR]:
  EMIT TestPattern {
    pattern_id: "I-{seq}",
    assertion_type: "path_convergence",
    assertion: "{surface} → calls(sprint_number_allocator)"
  }
```

**Concrete mapping from SNA:**
- GATE-A → I-001 (SNA-9 audit exists)
- GATE-A → I-002 (CLI verified)
- INV-2 → I-003 (import verified)
- INV-2 → I-004 (zero UNKNOWN paths)
- INV-2 → I-005 (all adjacent files reference allocator)

### 3.7 Layer 7 (Exceptional) — Import/Restore/Clone/Recovery

**Source elements:** INV-6 (import distinguishes historical vs new)

**Rule:** For each import classification, generate tests that verify correct behavior.

```
FOR EACH import_type IN [historical_restore, clone_as_new, import_as_new, recovery]:
  EMIT TestPattern {
    pattern_id: "E-{seq}",
    assertion_type: "deterministic_outcome",
    assertion: "classify_import({type}).requires_allocation == {expected}"
  }
```

**Concrete mapping from SNA:**
- INV-6 → E-001 (historical restore)
- INV-6 → E-002 (clone-as-new requires allocation)
- INV-6 → E-003 (clone rejects source reuse)
- INV-6 → E-004 (recovery preserves identity)
- INV-6 → E-005 (import-as-new requires allocation)
- INV-6 → E-006 (clone validation)

### 3.8 Layer 8 (Evidence) — Independent Proof Generation

**Source elements:** All evidence_requirements

**Rule:** For each evidence requirement, generate a test that asserts the evidence artifact exists and is well-formed.

```
FOR EACH req IN contract_source.evidence_requirements:
  EMIT TestPattern {
    pattern_id: "EV-{seq}",
    assertion_type: "evidence_produced",
    assertion: "{req.claim} ∧ evidence.{req.method}"
  }
```

### 3.9 Layer 9 (Regression) — Existing Infrastructure Check

**Source elements:** Contract sprints, acceptance gates

**Rule:** For each expected artifact (test runner, store file, governance implementation), assert existence.

```
FOR EACH expected_artifact IN contract_artifacts:
  EMIT TestPattern {
    pattern_id: "R-{seq}",
    assertion_type: "element_exists",
    assertion: "{artifact}.exists"
  }
```

## 4. Adversarial Derivation Rules

**Source:** Critical adversarial test pattern from SNA qualification

**Rule:** For each attack vector, the IR specifies:
1. What the attacker attempts
2. Which contract element is targeted
3. What the expected outcome should be
4. What severity applies if the attack succeeds

```
FOR EACH attack IN adversarial_surface:
  EMIT AdversarialRule {
    attack_vector: attack.description,
    contract_target: attack.invariant_id,
    expected_outcome: "rejected" | "detected" | "no_violation",
    severity_if_pass: severity_for(attack.invariant_id),
    test_pattern: { specific assertion }
  }
```

**Severity mapping:**
- INV-1 (atomic reservation) → critical
- INV-3 (binding integrity) → critical
- INV-4 (seal prerequisites) → critical
- INV-5 (persistence uniqueness) → medium (file-access boundary)

## 5. Positive Derivation Rules

**Source:** Positive workflow tests from SNA qualification

**Rule:** For each legitimate workflow, ensure it still completes successfully. This prevents the system from "passing" by making sprint creation unusable.

```
FOR EACH workflow IN legitimate_workflows:
  EMIT PositiveRule {
    lifecycle_path: workflow.states,
    expected_outcome: "completes" | "preserved" | "new_identity",
    test_pattern: { full lifecycle assertion }
  }
```

## 6. Provenance Traceability

Every test in the generated suite MUST carry a `source_contract_elements` field that traces back to the contract. The traceability chain:

```
Test ID (e.g. W-001)
    ↓ derived_from
TestPattern (in IR)
    ↓ source_contract_elements
Contract Elements (e.g. INV-1, LR-1, GATE-C)
    ↓ from
Epic Contract (e.g. EPIC-SPRINT-NUMBER-ALLOCATION-GOVERNANCE-1)
```

This allows:
- **Forward tracing:** Contract element → which tests validate it
- **Backward tracing:** Failed test → which contract element is at risk
- **Impact analysis:** Changed contract element → which tests need regeneration
