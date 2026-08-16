# Multi-Type Assurance — E2E-10 through E2E-13 Plan

**Date:** 2026-08-11
**Status:** E2E-10 COMPLETE, E2E-11 through E2E-13 PLANNED
**Source:** Architectural discussion

---

## Objective

Prove that QA-Pilot can derive, construct, execute, and reproduce multiple assurance dimensions from multiple source classes using the same compilation pipeline — without target-specific logic or test-type-specific runners.

---

## E2E-10: Multi-Source Assurance Derivation ✅ COMPLETE

**Status:** 15/15 gates PASS
**Completed:** 2026-08-11

### Results

```
Sources discovered:     1,328 across 5 classes
Requirements derived:   5,138
Dimensions:             REGRESSION (19), CONTRACT (1), BOUNDARY (806),
                        NEGATIVE (2,447), STATE_TRANSITION (2,332)
Capability resolution:  5,138 executable, 0 CAPABILITY_MISSING
```

### Output

- `scripts/e2e-10-multi-source-derivation.py` — Multi-source derivation engine
- `reports/e2e-10-multi-source-derivation-result.json` — Gate results manifest
- `reports/e2e-10-derived-requirements.json` — 5,138 normalized requirements with provenance

---

## E2E-11: Multi-Type Construction

**Input:** Derived requirements from E2E-10
**Output:** Constructed test artifacts for each dimension

### Acceptance Gates

| Gate | Requirement |
|---|---|
| E11-1 | All requirements have corresponding artifacts |
| E11-2 | Artifacts conform to test-definition schema |
| E11-3 | Each artifact declares its assurance_dimensions |
| E11-4 | Provenance preserved (source → requirement → artifact) |
| E11-5 | Artifacts frozen with hash |
| E11-6 | Same construction pipeline as E2E-5 (no new paths) |

---

## E2E-12: Multi-Type Execution

**Input:** Frozen test artifacts from E2E-11
**Output:** Execution results across all dimensions

### Acceptance Gates

| Gate | Requirement |
|---|---|
| E12-1 | All executable artifacts executed |
| E12-2 | Results classified by assurance dimension |
| E12-3 | PASS/FAIL reflects observation, not assertion |
| E12-4 | Evidence produced for every executed test |
| E12-5 | Artifact integrity verified |
| E12-6 | Same execution pipeline as E2E-6 (no new runners) |

---

## E2E-13: Multi-Type Reproducibility

**Input:** Frozen artifacts from E2E-11
**Output:** Structural and observational reproducibility

### Acceptance Gates

| Gate | Requirement |
|---|---|
| E13-1 | Two runs produce identical structural results |
| E13-2 | Two runs produce identical observational results |
| E13-3 | Any divergences attributed to target/environment |
| E13-4 | Provenance spine complete |

---

## Final Output: Assurance Corpus v2

```
ASSURANCE CORPUS v2
├── Multi-source requirements
│   ├── Historical claims → REGRESSION
│   ├── Schemas → CONTRACT
│   ├── Invariants → BOUNDARY
│   ├── Failure semantics → NEGATIVE
│   └── Lifecycle → STATE_TRANSITION
├── Multi-dimension test artifacts
├── Multi-dimension execution results
├── Multi-dimension evidence
├── Reproducibility record
└── Assurance profile
```

---

## Future: Extended Source Classes

The Ground Truth and Startup Contract evolution plans introduce two additional source classes for future E2E derivation:

| Source Class | Material | Derived Dimension | Status |
|---|---|---|---|
| Ground Truth records | Operational knowledge, environment facts | STATE_TRANSITION, REGRESSION | Planned |
| Startup prerequisites | Service requirements, runtime requirements | BOUNDARY, NEGATIVE | Planned |

These extend the same pipeline — no new engine paths required.

---

## Constraints

1. **No new capabilities** — use existing SCRIPT_EXECUTION, SCHEMA_VALIDATION, MCP_API_INTERACTION, BROWSER_INTERACTION
2. **No engine modification** — dimensions are properties of requirements, not modes in the engine
3. **Same contracts** — use existing testing-node-contract, target-adapter-contract, evidence-contract
4. **Same authority boundary** — QA-Pilot observes, does not decide
5. **No test-type-specific runners** — one pipeline for all dimensions

---

## Success Criterion

E2E-10 through E2E-13 succeed if:

> QA-Pilot can derive materially different assurance requirements from multiple authoritative source classes using the same compilation pipeline, without target-specific logic or test-type-specific execution paths.

---

*Plan — captured from architectural discussion.*
