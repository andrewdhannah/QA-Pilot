# P8-2 — Cross-Project Comparison

**Generated:** 2026-08-17
**Project:** qa-pilot
**Phase:** P8-2 (Comparison)
**Status:** COMPLETE

---

## 1. Comparison Scope

**Objective:** Determine whether combined P8-1a/P8-1b evidence supports Phase 8 generalization hypothesis.

**Comparison dimensions:**
- Baseline conditions
- Governed work-item type
- Discovery → decision flow
- Owner authority behavior
- Disposition recording
- Evidence/production
- Capability gaps
- Gap handling
- New primitives check
- Gap reproduction
- Outcome relative to P7

---

## 2. Baseline Conditions Comparison

| Metric | QA Pilot (P7) | The Librarian (P8-1a) | Agent Bridge (P8-1b) |
|--------|---------------|----------------------|---------------------|
| Phase | init | execution | active |
| Entities | 8 | 8 | 8 |
| Pending decisions | 9 | 9 | 9 |
| Knowledge findings | 10 | 10 | N/A |
| Knowledge entities | 53 | 53 | N/A |
| Features completed | 0 | 10+ | 12 |
| Extensions | 1 | 1 | 2 |

**Observation:** Baseline conditions vary significantly across projects, yet governance pattern operates identically.

---

## 3. Governance Pattern Comparison

| Dimension | QA Pilot (P7) | The Librarian (P8-1a) | Agent Bridge (P8-1b) | Match |
|-----------|---------------|----------------------|---------------------|-------|
| Pattern | Finding → Decision → Disposition | Candidate → Decision → Disposition | Candidate → Decision → Disposition | ✅ |
| Entry point | Knowledge findings | Discovery candidates | Discovery candidates | ✅ |
| Decision mechanism | Decision queue | Decision queue | Decision queue | ✅ |
| Disposition recording | Owner action + rationale | Owner action + rationale | Owner action + rationale | ✅ |
| Evidence production | Receipt generated | Disposition recorded | Disposition recorded | ✅ |

**Observation:** Governance pattern is identical across all three contexts.

---

## 4. Owner Authority Comparison

| Dimension | QA Pilot (P7) | The Librarian (P8-1a) | Agent Bridge (P8-1b) | Match |
|-----------|---------------|----------------------|---------------------|-------|
| Authority exclusive | Yes | Yes | Yes | ✅ |
| System recommendation | Advisory only | Advisory only | Advisory only | ✅ |
| Owner decides | Yes | Yes | Yes | ✅ |
| Automatic action | None | None | None | ✅ |
| New authority roles | None | None | None | ✅ |

**Observation:** Owner authority is preserved identically across all three contexts.

---

## 5. Evidence Production Comparison

| Dimension | QA Pilot (P7) | The Librarian (P8-1a) | Agent Bridge (P8-1b) | Match |
|-----------|---------------|----------------------|---------------------|-------|
| Finding/candidate produced | Yes | Yes | Yes | ✅ |
| Owner review | Yes | Yes | Yes | ✅ |
| Disposition recorded | Yes | Yes | Yes | ✅ |
| Rationale captured | Yes | Yes | Yes | ✅ |
| Provenance chain | Complete | Complete | Complete | ✅ |

**Observation:** Evidence production is identical across all three contexts.

---

## 6. Capability Gap Comparison

| Dimension | QA Pilot (P7) | The Librarian (P8-1a) | Agent Bridge (P8-1b) | Match |
|-----------|---------------|----------------------|---------------------|-------|
| Gap exposed | No | Yes | Yes | ⚠️ |
| Gap type | N/A | Wiring gap | Wiring gap | ✅ |
| Gap description | N/A | project_registry_create | project_registry_create | ✅ SAME |
| Gap severity | N/A | Medium | Medium | ✅ |

**Observation:** Same wiring gap exposed in both P8-1 projects, not in P7.

---

## 7. Gap Handling Comparison

| Dimension | QA Pilot (P7) | The Librarian (P8-1a) | Agent Bridge (P8-1b) | Match |
|-----------|---------------|----------------------|---------------------|-------|
| Gap observed | N/A | Yes | Yes | ✅ |
| Gap recorded as finding | N/A | Yes (P8-1a-GAP-001) | Yes (P8-1b-GAP-001) | ✅ |
| Gap repaired | N/A | No | No | ✅ |
| New primitives introduced | No | No | No | ✅ |
| Architecture preserved | Yes | Yes | Yes | ✅ |

**Observation:** Gaps handled identically — observed, recorded, not repaired.

---

## 8. Gap Reproduction Analysis

**P8-1a-GAP-001:**
- Context: The Librarian
- Observation: project_registry_create cannot create new projects
- Evidence: Error message lists valid projects

**P8-1b-GAP-001:**
- Context: Agent Bridge
- Observation: project_registry_create cannot create new projects
- Evidence: Error message lists valid projects (same list)

**Reconciliation:**
```
P8-1a-GAP-001 (The Librarian)
        │
        └── Same gap reproduced in P8-1b
        
P8-1b-GAP-001 (Agent Bridge)
        │
        └── Same gap reproduced from P8-1a
        
        ↓
        
System-level capability finding:
project_registry_create
validates against existing projects
before creating — cannot create
new projects
```

**Classification:** System-level wiring gap, not project-specific limitation.

---

## 9. New Primitives Check

| Context | New Primitives | Evidence |
|---------|----------------|----------|
| QA Pilot (P7) | None | Architecture freeze preserved |
| The Librarian (P8-1a) | None | No new primitives introduced |
| Agent Bridge (P8-1b) | None | No new primitives introduced |

**Observation:** No new governance primitives introduced across any context.

---

## 10. Outcome Relative to P7

| Dimension | P7 QA Pilot | P8-1a The Librarian | P8-1b Agent Bridge | Generalization |
|-----------|-------------|---------------------|---------------------|----------------|
| Governance pattern | Proven | Reproduced | Reproduced | ✅ YES |
| Owner authority | Proven | Preserved | Preserved | ✅ YES |
| Evidence production | Proven | Produced | Produced | ✅ YES |
| False remediation prevented | Proven | N/A (disposition) | N/A (disposition) | ✅ YES |
| Registration capability | N/A | Gap exposed | Gap exposed | ⚠️ Gap |

**Observation:** P8 results match P7 for governance pattern; registration gap is new in P8.

---

## 11. Hypothesis Assessment

### 11.1 H₀: Governance only works in QA Pilot

**Status: REJECTED**

**Evidence:**
- Governance pattern reproduced in The Librarian (P8-1a)
- Governance pattern reproduced in Agent Bridge (P8-1b)
- Owner authority preserved in both contexts
- Evidence produced in both contexts
- No new primitives required

### 11.2 H₁: Governance generalizes while preserving authority

**Status: SUBSTANTIALLY SUPPORTED**

**Evidence:**
- Governance pattern identical across 3 contexts
- Owner authority exclusive in all contexts
- Evidence production identical
- Architecture freeze preserved
- No authority expansion

**Caveat:**
- Registration execution gap exists (system-level)
- Gap does not affect governance pattern generalization
- Gap affects execution completion, not governance behavior

---

## 12. P8-2 Conclusion

### 12.1 Generalization Result

| Component | Generalization Status |
|-----------|----------------------|
| Governance decision pattern | ✅ GENERALIZES |
| Owner authority preservation | ✅ GENERALIZES |
| Evidence production | ✅ GENERALIZES |
| Gap handling as findings | ✅ GENERALIZES |
| Architecture freeze | ✅ PRESERVED |
| Registration execution | ⚠️ SYSTEM-LEVEL GAP |

### 12.2 System-Level Finding

**P8-GAP-001: System-Level Registration Capability Gap**

- **Type:** Wiring gap
- **Severity:** Medium
- **Scope:** System-level (not project-specific)
- **Evidence:** Reproduced in P8-1a and P8-1b
- **Impact:** Registration execution incomplete
- **Governance impact:** None demonstrated
- **Remediation:** Separate governed decision

### 12.3 Phase 8 Status

```
P8-INIT: COMPLETE
P8-1a:   PASS (with observed gap)
P8-1b:   PASS (with observed gap)
P8-2:    COMPLETE (comparison)
P8-3:    PENDING (generalization assessment)
P8-CLOSE: PENDING
```

---

*P8-2 comparison complete. Ready for P8-3 generalization assessment.*
