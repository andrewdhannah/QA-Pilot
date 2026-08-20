# Track B: Decision Surface Baseline Inventory

**Work Packet:** WO-4+ Dashboard Consolidation
**Phase:** 4.3 — Decision Surface
**Status:** IN PROGRESS
**Date:** 2026-08-18
**Agent:** OpenWork-Claude (mimo-v2.5)

---

## 1. Current Decision Surfaces

### Web UI (7 surfaces in Public/index.html)

| Surface | ID | Actionable | Shows Authority | Data Source |
|---------|-----|------------|-----------------|-------------|
| Simple Decision Console | `view-decisions-simple` | Limited | Yes | `/api/decisions/queue` |
| Advanced Decisions View | `view-decisions` | Full | Yes | `/api/decisions/queue` + `/api/decisions/lookup` |
| Owner Review Mode | `view-review` | Full | Yes | `/api/decisions/queue` + `/api/review/panel` |
| External Owner Actions | `view-external-actions` | Yes | Yes | Live OAR API |
| Overview (Owner Attention) | `view-overview` | Read-only | Yes | `/api/dashboard/summary` + `/api/decisions/queue` |
| Owner Queue Popover | `ownerQueuePopover` | Read-only | Yes | API |
| Governance View | `view-governance` | Read-only | Yes | Governance endpoints |

### Backend Data (3 layers)

| Layer | Location | Format | Count |
|-------|----------|--------|-------|
| Decision Queue | `data/decisions/decision-queue.json` | JSON | 19 items |
| Resolution Receipts | `receipts/decision-resolutions/` | JSON | 276 files |
| Pipeline Receipts | `receipts/pipeline/` | JSON | 30+ files |

### Swift Models (4 surfaces)

| Surface | File | Role |
|---------|------|------|
| OwnerActionTypes | `OwnerActionTypes.swift` | Data contract for Owner decisions |
| ProjectWorkModels | `ProjectWorkModels.swift` | Persisted Owner decision records |
| ContextCapsule | `ContextCapsuleContracts.swift` | Decision references in context |
| CLI Commands | `CLICommands.swift` | Decision queue CLI |

### External Systems (3 surfaces)

| Surface | Location | Role |
|---------|----------|------|
| Agent Bridge Decision Review | `agent-bridge/server/src/decision-review.ts` | Read-only decision assembly |
| Decision Pipeline | `governance-implementations/decision_pipeline.py` | 6-stage pipeline |
| Runtime Dashboard | `librarian-node/runtime-ui/views/dashboard.html` | Read-only governance tab |

---

## 2. Duplicate Authority Analysis

### Surfaces that ALLOW Owner action (actionable):

1. Simple Decision Console — limited actions
2. Advanced Decisions View — full resolution workflow
3. Owner Review Mode — approve/reject/park/changes
4. External Owner Actions — acknowledge/recheck
5. CLI approve/reject commands
6. Decision Pipeline (with `--apply`)

### Surfaces that are READ-ONLY (display only):

1. Overview (Owner Attention)
2. Owner Queue Popover
3. Governance View
7. Agent Bridge Decision Review
8. Runtime Dashboard

### Potential duplication:

| Overlap | Surfaces | Risk |
|---------|----------|------|
| Decision queue displayed in 4+ places | Simple, Advanced, Review, Overview | Low — same data, different views |
| Owner action available in 3+ places | Advanced, Review, CLI | Medium — authority exercised through multiple paths |
| Pipeline has its own resolution path | Pipeline `--apply` vs UI resolution | Medium — two code paths for same authority |

---

## 3. Canonical Display Mapping

### Decision States → Display

| Decision State | Displayed In | Action Available |
|---------------|-------------|-----------------|
| pending | Simple, Advanced, Review, Overview, Popover | Approve/Reject/Park |
| approved | Advanced (resolved), Receipts | None (completed) |
| rejected | Advanced (resolved), Receipts | None (completed) |
| deferred | Advanced, Review | Resume |
| external_required | External Actions | Acknowledge/Recheck |

### Authority Flow → Display

| Authority Step | Display | Code Path |
|---------------|---------|-----------|
| System detects issue | Governance View | Detection → Queue |
| System recommends | Advanced (LINK advisory) | Advisory panel |
| Owner reviews | Owner Review Mode | Review workflow |
| Owner decides | Advanced/Review/CLI | Resolution recording |
| Receipt generated | Receipts directory | Pipeline stage 5 |

---

## 4. Presentation Boundaries

### What the dashboard SHOULD display:

- Pending decision count
- Decision severity breakdown
- Owner attention queue
- Decision resolution history
- Authority status (who decided, when)
- Governance health metrics

### What the dashboard SHOULD NOT do:

- Create new authority paths
- Allow decisions without explicit Owner action
- Bypass the decision queue
- Auto-resolve pending decisions
- Modify decision ownership

### The invariant:

**Presentation does not create authority.**
The dashboard shows what needs Owner attention. It does not decide.

---

## 5. Design Questions for Phase 4.3

| Question | Current State | Design Decision Needed |
|----------|--------------|----------------------|
| How many surfaces show decisions? | 7+ | Consolidate or maintain separate views? |
| Where can Owner exercise authority? | 3+ code paths | Single authority surface or multiple? |
| How are receipts displayed? | Separate directory | Inline in dashboard or separate view? |
| What is the canonical decision data model? | Multiple schemas | Unify or maintain per-system schemas? |
| How does the dashboard consume governed state? | Direct API calls | Event-driven or polling? |

---

*Design in progress. Baseline inventory complete.*
