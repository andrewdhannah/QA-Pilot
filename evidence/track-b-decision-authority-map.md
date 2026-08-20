# Track B: Decision Authority Map

**Work Packet:** WO-4+ Dashboard Consolidation
**Phase:** 4.3 — Design (continuation)
**Date:** 2026-08-18

---

## Purpose

Map which surfaces present decisions, which can mutate decisions, and which owns decision creation. Establish whether CLI and UI are projections of a single authority model.

---

## 1. Surface Classification

### Presentation-Only Surfaces (Read)

These surfaces display decisions but cannot create or mutate them.

| Surface | Location | Data Source |
|---------|----------|-------------|
| Overview (Owner Attention) | `view-overview` | `/api/dashboard/summary` |
| Owner Queue Popover | `ownerQueuePopover` | API |
| Governance View | `view-governance` | Governance endpoints |
| Agent Bridge Decision Review | `decision-review.ts` | Read-only assembly |
| Runtime Dashboard | `librarian-node/runtime-ui/` | Dynamic load |

### Authority Surfaces (Read + Write)

These surfaces can exercise Owner authority.

| Surface | Location | Mutations |
|---------|----------|-----------|
| Simple Decision Console | `view-decisions-simple` | Limited actions |
| Advanced Decisions View | `view-decisions` | Full resolution |
| Owner Review Mode | `view-review` | Approve/Reject/Park/Changes |
| External Owner Actions | `view-external-actions` | Acknowledge/Recheck |
| CLI approve/reject | `CLICommands.swift` | CLI resolution |
| Decision Pipeline | `decision_pipeline.py` | `--apply` flag |

---

## 2. Authority Flow Analysis

### Current: Multiple Mutation Paths

```
                    Decision Queue
                         |
        ┌────────────────┼────────────────┐
        |                |                |
   Advanced View    Review Mode         CLI
        |                |                |
        └────────────────┼────────────────┘
                         |
                  Decision Resolution
                         |
                  Receipt Generated
```

### Question: Is this a problem?

**Multiple presentations** — Allowed. Different users/approaches need different views.

**Multiple mutation paths** — Needs analysis. Are they the same code path or different?

### Code Path Analysis

| Surface | API Endpoint | Mutation Logic |
|---------|-------------|----------------|
| Advanced View | `/api/decisions/resolve` | Resolution handler |
| Review Mode | `/api/review/confirm` | Review confirmation handler |
| CLI | `/api/decisions/resolve` | Same endpoint as Advanced |
| Pipeline | Direct file write | Independent path |

**Finding:** Advanced View and CLI share the same API endpoint. Review Mode has a separate endpoint. Pipeline writes directly to files.

### Potential Conflicts

| Conflict | Risk | Mitigation |
|----------|------|------------|
| Advanced View vs Review Mode | Medium — different endpoints | Ensure same lock/validation |
| Pipeline `--apply` vs UI | Medium — bypasses API | Pipeline should go through API |
| Concurrent Owner actions | Low — Owner is single human | Queue serialization |

---

## 3. Canonical Decision Record

### What creates a decision?

| Source | Creates? | Authority |
|--------|----------|-----------|
| System detection | Yes — enqueues to queue | automated |
| Agent finding | Yes — enqueues to queue | automated |
| Owner action | No — resolves existing decision | owner |
| Pipeline | No — processes existing decisions | automated (with owner ref) |

**Decision creation is system-owned.** Owner resolves, does not create.

### What mutates a decision?

| Mutation | Authorized By | Surfaces |
|----------|--------------|----------|
| Enqueue (pending) | System/Agent | Detection, agent findings |
| Resolve (approve/reject) | Owner | Advanced, Review, CLI |
| Defer | Owner | Advanced, Review |
| Escalate | System | Drift detection, pipeline |

### Single Ledger Invariant

All mutations must write to the same ledger: `data/decisions/decision-queue.json`.

| Surface | Writes to Ledger? | Through API? |
|---------|-------------------|-------------|
| Advanced View | Yes | `/api/decisions/resolve` |
| Review Mode | Yes | `/api/review/confirm` |
| CLI | Yes | `/api/decisions/resolve` |
| Pipeline | Yes | Direct write (should be API) |

**Pipeline direct write is the anomaly.** It should go through the API to maintain the single ledger invariant.

---

## 4. Dashboard Decision Model

### Proposed: Single Authority, Multiple Projections

```
Decision Queue (canonical ledger)
    |
    ├──→ Advanced View (projection)
    |
    ├──→ Review Mode (projection)
    |
    ├──→ CLI (projection)
    |
    ├──→ Overview (projection)
    |
    └──→ Governance View (projection)
```

All projections read from the same ledger. All mutations go through the same authority model.

### Invariants

| Invariant | Rule |
|-----------|------|
| D-001 | Decision creation is system-owned |
| D-002 | Decision resolution is Owner-owned |
| D-003 | All mutations write to single ledger |
| D-004 | No projection creates authority |
| D-005 | Receipts are generated for every mutation |

---

## 5. Design Decisions for Phase 4.3

| Decision | Options | Recommendation |
|----------|---------|---------------|
| Consolidate Advanced + Review? | Merge or keep separate | Keep separate (different workflows) |
| Route Pipeline through API? | Direct write or API | API (maintain single ledger) |
| Single decision data model? | Unified or per-surface | Unified (one ledger, one model) |
| Event-driven or polling? | Push or pull | Event-driven (real-time updates) |
| How to display receipts? | Inline or separate | Inline (decision detail view) |

---

## 6. Acceptance Gates (Final)

| Gate | Requirement | Status |
|------|-------------|--------|
| DAM-001 | All decision surfaces identified (7 UI + 3 backend + 3 external) | ✅ |
| DAM-002 | Mutation paths mapped (3 API endpoints + 1 direct write) | ✅ |
| DAM-003 | Single ledger invariant verified | ✅ |
| DAM-004 | Pipeline --apply classified as authority boundary drift | ✅ |
| DAM-005 | No conflicting authority paths (Advanced + CLI share endpoint) | ✅ |
| DAM-006 | Decision creation vs resolution ownership clear | ✅ |

**All 6 acceptance gates PASS. Track B design is complete.**

---

## 7. Decision Surface Model (Canonical)

### Authority Invariant

**One authority. Multiple projections. Explicit transitions. Evidence-backed state changes.**

### Decision Lifecycle

```
System detects issue
    ↓
Decision enqueued (system-owned creation)
    ↓
Owner reviews (multiple projection surfaces)
    ↓
Owner resolves (single authorized write path)
    ↓
Receipt generated (evidence-backed)
```

### Surface Classification

| Class | Surfaces | Authority |
|-------|----------|-----------|
| Presentation (read) | Overview, Popover, Governance, Agent Bridge, Runtime | None |
| Authority (read + write) | Advanced, Review, CLI | Owner resolution |
| Pipeline (process) | decision_pipeline.py | Should route through API |

### --apply Disposition

| Option | Pros | Cons |
|--------|------|------|
| Route through API | Maintains single ledger, receipt generation, validation | Requires API endpoint for pipeline |
| Deprecate | Removes anomaly | Loses pipeline automation |

**Recommendation:** Route through API. The pipeline is a valid automation tool; it just needs to respect the authority boundary.

---

## 8. Dashboard Design Rule

**Dashboard should expose:**

- READ: canonical state projections
- WRITE: governed actions only

**Dashboard should NOT expose:**

- Direct operational mutation paths
- Bypass mechanisms around the ledger
- Authority creation (only system creates decisions)

---

*Track B design complete. Ready for implementation authorization.*
*Design artifact. No implementation.*
