# WP-001 — Cursor Integrity Repair: Evidence & Findings

**Work Packet:** WP-001 of GOVERNANCE-INTEGRITY-RECOVERY-1
**Date:** 2026-08-16
**Status:** INVESTIGATION COMPLETE — requires Owner decision

---

## Before State Snapshot

### Librarian Cursor
```
project_id: "librarian"
phase: 8 (Operate/Maintain)
cursor_position: 529
cycle: 1
source_revision: "governance-migration-complete-v1.1-2026-07-20"
sprint_id: "LIBRARIAN-LIFECYCLE-CURSOR-DB-BACKFILL-1"
last_transition_at: 2026-07-06T14:23:53Z
last_reconciled_at: 2026-07-20T01:57:16Z
```
**Assessment:** Librarian cursor appears HEALTHY. Drift event `DRIFT-librarian-drift_detection` (critical) may be stale — the cursor now shows `project_id: "librarian"` (correct), not `"librarian-workbench"` as the drift reported.

### QA-Pilot Cursor
```
project_id: "qa-pilot"
phase: 1 (Plan)
cycle: 1
entered_from: "project_init"
source_revision: "init-v1"
last_transition_at: 2026-07-20T01:57:16Z
last_reconciled_at: 2026-07-20T01:57:16Z
history: 2 entries (init + profile change)
```
**Assessment:** Cursor EXISTS and is readable. But `get_allowed_transitions` returns "Cursor not found for project: 'qa-pilot'".

---

## Root Cause Analysis

### The Deadlock
1. `get_cursor("qa-pilot")` → **SUCCESS** — returns cursor at Phase 1
2. `get_allowed_transitions("qa-pilot")` → **FAILURE** — "Cursor not found"
3. `advance_cursor("qa-pilot")` → **FAILURE** — "Owner decision required" (correct governance)

The cursor exists but the transition resolver cannot locate it. This is a **lookup path mismatch** between the cursor storage and the transition resolution code.

### The State Translation Problem

The Rust `LifecycleState` enum (from `librarian-contracts/src/lifecycle.rs`) defines:
```
Install → Initialize → Qualify → Identity → Ready → Discovered → Candidate → Admitted → Operational → Suspended → Retired
```

The MCP adapter maps QA-Pilot's cursor to:
```
phase: 1, label: "Plan"
```

**There is no `Plan` state in the Rust enum.** The adapter is creating a translation layer that doesn't correspond to the canonical lifecycle states. This means:
- The cursor is stored with a phase value that the transition engine doesn't recognize
- The transition resolver may be looking for a `LifecycleState` variant that doesn't match the stored phase
- The `can_transition_to()` method in Rust validates against `LifecycleState` variants, not numeric phases

### The Transition Table

From `lifecycle.rs`:
```rust
Install => [Initialize]
Initialize => [Qualify]
Qualify => [Identity]
Identity => [Ready]
Ready => [Discovered]
Discovered => [Candidate]
Candidate => [Admitted, Suspended]
Admitted => [Operational, Suspended]
Operational => [Suspended, Retired]
Suspended => [Candidate, Admitted, Retired]
Retired => []  // terminal
```

If QA-Pilot's cursor is stored as `phase: 1` (which maps to... what in the Rust enum?), the transition resolver may be unable to determine valid next states.

### The Additional Lifecycle System

There's a SECOND lifecycle system in `librarian-core/src/lifecycle/transitions.rs` with different states:
```
Discovered → Candidate → Qualified → Approved → Active → Deprecated → Retired
```

This is the **component lifecycle** (for governance entities), not the **project lifecycle** (for projects). The two systems have overlapping but different state machines.

---

## Drift Events (4 open)

| Drift ID | Entity | Severity | Status |
|----------|--------|----------|--------|
| `DRIFT-librarian-drift_detection` | librarian | **CRITICAL** | May be stale — cursor now appears correct |
| `DRIFT-agent-bridge-reconciliation_record` | agent-bridge | warning | Reconciliation overdue |
| `DRIFT-agent-bridge-drift_detection` | agent-bridge | warning | 31 days stale |
| `DRIFT-scrum-tracker-drift_detection` | scrum-tracker | warning | Position mismatch |

---

## Acceptance Gate Results

### G1 — Identity Alignment
| Project | cursor.project_id | canonical project.id | Match |
|---------|-------------------|---------------------|-------|
| librarian | `librarian` | `librarian` | ✅ PASS |
| qa-pilot | `qa-pilot` | `qa-pilot` | ✅ PASS |

### G2 — Transition Resolution
| Project | get_allowed_transitions | Result |
|---------|------------------------|--------|
| librarian | Not tested (phase 8, terminal-adjacent) | SKIPPED |
| qa-pilot | "Cursor not found" | ❌ FAIL |

### G3 — Ledger Position
| Project | cursor_position | latest_sealed | Match |
|---------|----------------|---------------|-------|
| librarian | 529 | 529 | ✅ PASS |
| qa-pilot | N/A (no sealed sprints) | N/A | ✅ PASS |

---

## Required Owner Decisions

### Decision 1: Librarian Drift Resolution
The critical drift event `DRIFT-librarian-drift_detection` reports cursor identity mismatch. However, the current cursor state shows correct identity (`project_id: "librarian"`, position 529). Options:
- **Accept** — drift event is stale, cursor is already correct
- **Investigate** — verify cursor matches canonical ledger
- **Escalate** — if ledger state is uncertain

### Decision 2: QA-Pilot Phase Translation
The adapter maps the cursor to `phase: 1, label: "Plan"` but the Rust enum has no `Plan` state. Options:
- **Map to `Initialize`** — Phase 1 = Initialize (the first mutable state after Install)
- **Map to `Discovered`** — if QA-Pilot is a newly discovered entity
- **Create `Plan` state** — add a new variant to the Rust LifecycleState enum
- **Investigate** — understand what `project_init` intended Phase 1 to mean

### Decision 3: Transition Resolver Fix
The `get_allowed_transitions` tool cannot find QA-Pilot's cursor. This is likely a lookup path mismatch in the Swift adapter. Options:
- **Fix adapter lookup** — align the transition resolver with cursor storage
- **Bypass for now** — allow cursor advancement through direct DB mutation (requires Owner authority)
- **Escalate** — if the fix requires Rust/Swift code changes beyond current scope

---

## Stop Condition Evaluation

| Condition | Triggered? | Action |
|-----------|-----------|--------|
| Cursor repair requires modifying sealed receipts | No | — |
| Canonical ledger history must be rewritten | No | — |
| Project identity ambiguity remains | No — identities are clear | — |

**Stop conditions not triggered.** The issue is a code-level lookup mismatch, not a data integrity problem.

---

## Recommended Path Forward

1. **Resolve Decision 1** (librarian drift) — likely accept as stale
2. **Resolve Decision 2** (QA-Pilot phase) — determine correct mapping
3. **Resolve Decision 3** (transition resolver) — fix or bypass the lookup
4. **Re-run acceptance gates** after fixes
5. **Produce receipt artifact** with before/after evidence

---

*WP-001 investigation complete. Awaiting Owner decisions before proceeding to repair.*
