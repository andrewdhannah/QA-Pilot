# GPI-001 — Runtime Qualification Activation

**Sprint ID:** GPI-001
**Project:** qa-pilot
**Phase:** Phase 7 — Adoption & Empirical Validation (P7.1 Cross-Project Trial)
**Status:** PLANNED — awaiting Owner authorization
**Date:** 2026-08-17
**Authority Scope:** restricted

---

## Objective

Activate runtime qualification against the canonical five-dimensional governance state. Prove that qualification can observe, evaluate, and record results while preserving the independence of qualification, lifecycle, health, execution policy, and entity type.

**This is not qualification architecture expansion.** It bridges the existing qualification substrate to the canonical state model established by LVC-001.

## Governing Question

Can runtime qualification operate against the canonical five-dimensional governance state while preserving the independence of qualification, lifecycle, health, and execution policy?

## Critical Boundary

```
Qualification
     │
     ├── observes canonical state
     ├── evaluates qualification evidence
     ├── produces qualification result
     └── records evidence/receipt
            │
            X
     must NOT mutate:
       lifecycle_state
       health_state
       execution_policy
       entity_type
```

The qualification engine produces a **qualification result** — it does not advance lifecycle, change health assessment, alter execution permission, or reclassify entities. Those remain under their respective authority sources.

---

## Audit Evidence (Current State)

### Existing Qualification Infrastructure

| Component | Path | What It Does |
|-----------|------|-------------|
| Qualification Execution Engine | `scripts/qa_pilot_qualification_execution.py` | Evaluates QR records, produces qualification results |
| Qualification Evidence Pipeline | `scripts/qa_pilot_qualification_evidence_pipeline.py` | Ingests evidence into QR records |
| Qualification Review Surface | `scripts/qa_pilot_qualification_review_surface.py` | Owner review of qualification results |
| Qualification Compiler | `qualification/compiler/qualification_compiler.py` | IR → test suite generation |

### Current Qualification State

The qualification engine operates on QR records with its own internal lifecycle:

```
QR Record
├── lifecycle_state: proposed → in_progress → completed
├── qualification_level: unqualified → spot_checked → peer_reviewed → audited
├── overall_score: 0.0–1.0
└── sub_dimension_scores: schema, freshness, diversity, authority, provenance
```

**Key gap:** The qualification engine does NOT read from the canonical five-dimensional governance state. It evaluates QR records in isolation, without awareness of the entity's lifecycle_state, health_state, execution_policy, or entity_type in the registry.

### What GPI-001 Bridges

```
Before GPI-001:

Registry (canonical state)          Qualification Engine
├── entity_type                      ├── QR records (internal)
├── lifecycle_state                  ├── internal lifecycle
├── qualification_state              ├── qualification levels
├── health_state                     └── evaluation results
└── execution_policy
        │                                    │
        └──── NOT CONNECTED ────────────────┘


After GPI-001:

Registry (canonical state)          Qualification Engine
├── entity_type ◄──── reads ────────┤
├── lifecycle_state ◄── context ────┤
├── qualification_state ◄─ updates ─┤── QR records (internal)
├── health_state ◄─── context ──────┤── evaluation results
└── execution_policy ◄─ context ────┘── receipts
        │                                    │
        └──── BOUND (read-only) ────────────┘
```

---

## Scope

### In Scope

1. Bind qualification execution to canonical governance state (read-only)
2. Update qualification_state in registry based on qualification results
3. Produce qualification receipts referencing canonical state
4. Enforce authority boundary: qualification must not mutate other dimensions
5. Verify existing qualification behavior unchanged
6. Prove replay determinism

### Out of Scope

- New qualification rules or QR- rule changes
- Lifecycle state transitions triggered by qualification
- Health state changes triggered by qualification
- Execution policy changes triggered by qualification
- Entity reclassification triggered by qualification
- Qualification compiler changes
- New assurance primitives

---

## Work Packets

### WP-GPI-001 — Qualification-to-Canonical Binding

**Purpose:** Connect the qualification execution engine to the canonical governance state registry.

**Deliverables:**
- Registry reader module: `scripts/governance_state_reader.py`
- Reads all 5 dimensions from `project-index-v2.json`
- Provides entity governance context to qualification engine
- Read-only — no write path through this module

**Acceptance Gates:**
- GPI-001-A: Qualification engine can read canonical state for any entity
- GPI-001-B: Reader returns all 5 dimensions independently

### WP-GPI-002 — Runtime Qualification Execution

**Purpose:** Execute qualification against entities with canonical state awareness.

**Deliverables:**
- Updated qualification execution: reads canonical state as evaluation context
- Qualification evaluates evidence against entity's qualification_state
- Result includes canonical state snapshot at evaluation time
- No mutation of non-qualification dimensions

**Acceptance Gates:**
- GPI-001-C: Qualification executes with canonical state as context
- GPI-001-D: Qualification result includes canonical state snapshot
- GPI-001-E: Existing QR- rule evaluation produces identical results

### WP-GPI-003 — Authority Boundary Enforcement

**Purpose:** Ensure qualification cannot mutate lifecycle, health, execution, or entity_type.

**Deliverables:**
- Authority boundary validator: `scripts/validate-qualification-authority.py`
- Pre-commit check: qualification receipt cannot contain mutations to non-qualification dimensions
- Post-execution check: registry state unchanged except qualification_state
- Test fixtures (valid + invalid)

**Acceptance Gates:**
- GPI-001-F: Qualification cannot mutate lifecycle_state
- GPI-001-G: Qualification cannot mutate health_state
- GPI-001-H: Qualification cannot mutate execution_policy
- GPI-001-I: Qualification cannot mutate entity_type
- GPI-001-J: Registry state unchanged after qualification (except qualification_state)

### WP-GPI-004 — Evidence and Receipt Generation

**Purpose:** Produce qualification receipts that reference canonical state.

**Deliverables:**
- Qualification receipt schema: includes canonical state snapshot
- Receipt references entity_id, all 5 dimensions at evaluation time
- Receipt includes qualification result (level, score, assessment)
- Receipt is append-only evidence, not a mutation command

**Acceptance Gates:**
- GPI-001-K: Qualification receipt includes canonical state snapshot
- GPI-001-L: Receipt is evidence, not mutation command

### WP-GPI-005 — Regression and Replay Verification

**Purpose:** Prove existing qualification behavior unchanged and replay is deterministic.

**Deliverables:**
- Regression test: existing qualification results unchanged
- Replay test: same inputs produce same qualification results
- State comparison: before/after qualification, only qualification_state changed

**Acceptance Gates:**
- GPI-001-M: Existing qualification results reproduce identically
- GPI-001-N: Replay produces same classification from same inputs
- GPI-001-O: Only qualification_state changes during qualification

---

## Acceptance Gates (Summary)

| Gate | Question | Work Packet |
|------|----------|-------------|
| GPI-001-A | Qualification engine can read canonical state for any entity | WP-GPI-001 |
| GPI-001-B | Reader returns all 5 dimensions independently | WP-GPI-001 |
| GPI-001-C | Qualification executes with canonical state as context | WP-GPI-002 |
| GPI-001-D | Qualification result includes canonical state snapshot | WP-GPI-002 |
| GPI-001-E | Existing QR- rule evaluation produces identical results | WP-GPI-002 |
| GPI-001-F | Qualification cannot mutate lifecycle_state | WP-GPI-003 |
| GPI-001-G | Qualification cannot mutate health_state | WP-GPI-003 |
| GPI-001-H | Qualification cannot mutate execution_policy | WP-GPI-003 |
| GPI-001-I | Qualification cannot mutate entity_type | WP-GPI-003 |
| GPI-001-J | Registry state unchanged after qualification (except qualification_state) | WP-GPI-003 |
| GPI-001-K | Qualification receipt includes canonical state snapshot | WP-GPI-004 |
| GPI-001-L | Receipt is evidence, not mutation command | WP-GPI-004 |
| GPI-001-M | Existing qualification results reproduce identically | WP-GPI-005 |
| GPI-001-N | Replay produces same classification from same inputs | WP-GPI-005 |
| GPI-001-O | Only qualification_state changes during qualification | WP-GPI-005 |

**15 gates total.**

---

## Completion Criterion

Runtime qualification operates against the canonical five-dimensional governance state. Qualification results reference canonical state. Authority boundaries are enforced. Existing behavior is preserved. The qualification system is now a consumer of the canonical model, not an isolated subsystem.

---

## Dependency Chain

```
GIR-001 (complete) ✅
        ↓
LVC-001 (complete) ✅
        ↓
WP-003B (complete) ✅
        ↓
GPI-001 (this sprint) ← YOU ARE HERE
        ↓
P7.1 Cross-Project Trial continues
```

---

## Architecture Freeze Compliance

| Check | Status |
|-------|--------|
| New assurance primitives? | No — binding existing qualification to canonical state |
| New governance authority? | No — qualification remains advisory |
| New lifecycle states? | No — using canonical enum from LVC-001 |
| Routing changes? | No — data model binding only |
| Qualification authority expansion? | No — qualification cannot mutate other dimensions |

---

## Authorization Posture

```
GPI-001
Status: READY FOR AUTHORIZATION

WP-GPI-001  Qualification-to-Canonical Binding
WP-GPI-002  Runtime Qualification Execution
WP-GPI-003  Authority Boundary Enforcement
WP-GPI-004  Evidence and Receipt Generation
WP-GPI-005  Regression and Replay Verification

Acceptance Gates: A–O (15 gates)
New Authority: NONE
New Assurance Primitives: NONE
Authority Boundary: PRESERVED (qualification cannot mutate other dimensions)
Architecture Freeze: PRESERVED
```
