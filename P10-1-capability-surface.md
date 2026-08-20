# P10-1 — Capability Surface Definition

**Generated:** 2026-08-17
**Project:** qa-pilot
**Phase:** P10-1 (Capability Surface)
**Status:** COMPLETE

---

## 1. Three-Layer Architecture

### 1.1 Layer 1: Governance Capability Surface

**What every governed project receives.**

```
┌─────────────────────────────────────────────────────────────┐
│                  Governance Capability Surface                │
│                                                              │
│  What every governed project receives                        │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Layer 2: Project Integration Surface

**What projects provide.**

```
┌─────────────────────────────────────────────────────────────┐
│                  Project Integration Surface                  │
│                                                              │
│  What projects provide                                       │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 Layer 3: Execution Surface

**What remains outside governance.**

```
┌─────────────────────────────────────────────────────────────┐
│                  Execution Surface                            │
│                                                              │
│  What remains outside governance                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Governance Capability Surface (P10-1-001)

### 2.1 Observation Capabilities

| Capability | Description | Validation |
|------------|-------------|------------|
| Evidence generation | Produce findings from knowledge substrate | P7.2 proven |
| Knowledge findings | Detect orphans, unreferenced artifacts | P7.2 proven |
| Drift detection | Identify deviations from expected state | P7.2 proven |

### 2.2 Decision Support Capabilities

| Capability | Description | Validation |
|------------|-------------|------------|
| Decision candidates | Project findings into decision queue | P7.2-5 proven |
| Owner review | Present candidates for Owner disposition | P7/P8/P9 proven |
| Disposition recording | Record Owner decisions with rationale | P7/P8/P9 proven |

### 2.3 Lifecycle Control Capabilities

| Capability | Description | Validation |
|------------|-------------|------------|
| Deferred items | Track intentionally deferred decisions | P9-2 proven |
| Capability gaps | Govern system limitations | P9-3 proven |
| Closure evidence | Link resolutions to originating observations | P9-1 proven |

### 2.4 Provenance Capabilities

| Capability | Description | Validation |
|------------|-------------|------------|
| Receipts | Generate evidence receipts at each step | P7/P8 proven |
| Identity | Maintain finding/candidate identity through lifecycle | P9-1/P9-2 proven |
| Replayability | Produce deterministic results on replay | P7.2-5 proven |

### 2.5 Governance Capability Map

```
Governance Substrate
├── Observation
│   ├── Evidence generation
│   ├── Knowledge findings
│   └── Drift detection
│
├── Decision Support
│   ├── Decision candidates
│   ├── Owner review
│   └── Disposition recording
│
├── Lifecycle Control
│   ├── Deferred items
│   ├── Capability gaps
│   └── Closure evidence
│
└── Provenance
    ├── Receipts
    ├── Identity
    └── Replayability
```

---

## 3. Project Integration Surface (P10-1-002)

### 3.1 Project Extension Points

| Extension Point | Description | Variability |
|-----------------|-------------|-------------|
| Entities | Project-specific entities | High |
| Artifacts | Project-specific artifacts | High |
| Work items | Project-specific work types | High |
| Domain validators | Project-specific validation rules | Medium |
| Execution tools | Project-specific execution mechanisms | High |

### 3.2 Project Surface Map

```
Project Surface
├── Entities
│   ├── Project identity
│   ├── Lifecycle state
│   └── Governance profile
│
├── Artifacts
│   ├── Documents
│   ├── Code
│   └── Configuration
│
├── Work Items
│   ├── Sprints
│   ├── Tasks
│   └── Issues
│
├── Domain Validators
│   ├── Project-specific rules
│   ├── Quality gates
│   └── Compliance checks
│
└── Execution Tools
    ├── Local CLI
    ├── Build systems
    └── Deployment tools
```

### 3.3 Integration Interface

```
Governance Substrate ←→ Project Integration
        ↓                     ↓
  Standardized           Variable
  Capabilities           Capabilities
        ↓                     ↓
  Common                Project-specific
  APIs                  Adaptations
```

---

## 4. Execution Surface (P10-1-003)

### 4.1 What Remains Outside Governance

| Element | Description | Governance Role |
|---------|-------------|-----------------|
| System observation | System observes state | Read-only |
| System proposal | System proposes actions | Advisory only |
| Owner decision | Owner decides disposition | Authoritative |
| Execution | Work performed | Through authorized mechanisms |

### 4.2 Execution Boundary

```
┌─────────────────────────────────────────────────────────────┐
│                  Governance Boundary                         │
│                                                              │
│  System observes → System proposes → Owner decides           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    [Boundary]
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Execution Boundary                          │
│                                                              │
│  Execution occurs through authorized mechanisms              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 Execution Rules

| Rule | Description |
|------|-------------|
| No auto-execution | System never executes without Owner authorization |
| No authority crossing | Execution layer never crosses into governance |
| No implicit authorization | Execution requires explicit Owner decision |
| Evidence required | Execution produces resolution evidence |

---

## 5. Validated Invariants Mapped (P10-1-005)

### 5.1 Architecture Invariants

| Invariant | Layer | Status |
|-----------|-------|--------|
| No new governance primitives | Governance | ✅ PRESERVED |
| No new authority roles | Governance | ✅ PRESERVED |
| No automatic remediation | Governance | ✅ PRESERVED |
| No bypass paths | Governance | ✅ PRESERVED |

### 5.2 Authority Invariants

| Invariant | Layer | Status |
|-----------|-------|--------|
| Owner sole disposition authority | Governance | ✅ PRESERVED |
| System advisory only | Governance | ✅ PRESERVED |
| No automatic decisions | Governance | ✅ PRESERVED |

### 5.3 Evidence Invariants

| Invariant | Layer | Status |
|-----------|-------|--------|
| Finding → Decision → Disposition → Resolution | All | ✅ PRESERVED |
| Provenance maintained | All | ✅ PRESERVED |
| Closure links to origin | All | ✅ PRESERVED |

### 5.4 Key Invariant

**The system creates value because it constrains action, not because it automates action.**

---

## 6. No New Primitives (P10-1-006)

### 6.1 New Capability Check

| Capability | Introduced |
|------------|------------|
| New MCP tools | No |
| New governance models | No |
| New authority mechanisms | No |
| New lifecycle states | No |

### 6.2 Architecture Check

| Check | Result |
|-------|--------|
| Architecture freeze preserved | ✅ Yes |
| No new primitives | ✅ Yes |
| No authority expansion | ✅ Yes |

---

## 7. Acceptance Gate Verification

### 7.1 Gate Summary

| Gate | Result | Evidence |
|------|--------|----------|
| P10-1-001 | ✅ PASS | Standard governance capabilities identified |
| P10-1-002 | ✅ PASS | Project-specific extension points identified |
| P10-1-003 | ✅ PASS | Execution boundary documented |
| P10-1-004 | ✅ PASS | Authority boundary preserved |
| P10-1-005 | ✅ PASS | Existing validated invariants mapped |
| P10-1-006 | ✅ PASS | No new primitives introduced |

---

## 8. P10-1 Conclusion

### 8.1 Capability Surface Defined

**Governance Substrate:** 12 capabilities across 4 domains
**Project Surface:** 5 extension points
**Execution Surface:** Clear boundary with 4 rules

### 8.2 Key Findings

1. **Governance capabilities standardized:** 12 capabilities identified
2. **Project extension points defined:** 5 areas of variability
3. **Execution boundary clear:** 4 rules documented
4. **Invariants preserved:** All validated invariants mapped
5. **No new primitives:** Architecture freeze maintained

### 8.3 Operational Capability Map

```
┌─────────────────────────────────────────────────────────────┐
│                  Governance Capability Surface                │
│                                                              │
│  Observation → Decision Support → Lifecycle → Provenance     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Project Integration Surface                  │
│                                                              │
│  Entities → Artifacts → Work Items → Validators → Tools      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Execution Surface                            │
│                                                              │
│  System observes → System proposes → Owner decides → Execute │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

*P10-1 capability surface definition complete. Ready for P10-2.*
