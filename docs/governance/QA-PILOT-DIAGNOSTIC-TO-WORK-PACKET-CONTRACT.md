# QA Pilot Diagnostic-to-Work-Packet Contract

**Purpose:** Transform validation findings into actionable, governed repair work packets. Close the loop between detection and authorized remediation.

## Architecture

```
QA-Pilot Validation
    │
    │ "Something violated a contract"
    ▼
Diagnostic Report (DIAG-*)
    │
    │ severity, expected, actual, constraints, evidence refs
    ▼
Work Queue Item (QA-*-*)
    │
    │ OPEN → TRIAGED → APPROVED → IN_PROGRESS → FIXED → VERIFIED → CLOSED
    │                                          ↓ rejected → REJECTED
    ▼
Librarian Work Packet (WP-QA-*)
    │
    │ authorized scope, constraints, required validation
    ▼
Agent / Human Execution
    │
    ▼
Validation Re-run
    │
    ▼
Queue Item Closed / Reopened
```

## Work Queue Lifecycle

```
OPEN ──→ TRIAGED ──→ APPROVED ──→ IN_PROGRESS ──→ FIXED ──→ VERIFIED ──→ CLOSED
  │          │            │              │              │           │
  └─→ REJECTED (any state)
```

| Status | Meaning | Who |
|---|---|---|
| OPEN | Issue detected, awaiting triage | QA-Pilot / automated |
| TRIAGED | Reviewed and categorized | Team / human |
| APPROVED | Authorized for work | Owner / reviewer |
| IN_PROGRESS | Work underway | Agent / developer |
| FIXED | Repair submitted | Agent / developer |
| VERIFIED | Validation re-ran, issue resolved | QA-Pilot / automated |
| CLOSED | Human confirmed closure | Owner / reviewer |
| REJECTED | Determined not actionable | Team / human |

## Three-Layer Schema

| Schema | Purpose | Key Fields |
|---|---|---|
| `qa-diagnostic-report.schema.json` | What QA-Pilot produces from failures | report_id, test_id, failure.expected, failure.actual, constraints |
| `qa-work-queue-item.schema.json` | What lives in the queue | item_id, status, diagnostic_ref, severity, domain, assigned_to, resolution |
| `qa-work-packet.schema.json` | What the agent receives to execute | packet_id, queue_item_ref, authority, constraints, verification_required |

## CLI Commands

| Command | Purpose |
|---|---|
| `diagnose <tid> <dom> <exp> <act>` | Create diagnostic report from validation failure |
| `create <diag-path>` | Create queue item from diagnostic report |
| `transition <item-id> <status>` | Transition item through lifecycle |
| `list [status]` | List queue items (optionally filtered by status) |
| `show <item-id>` | Show item details |
| `status` | Queue status summary |

## Results

| Metric | Value |
|--------|-------|
| Schemas created | 3 (diagnostic report, queue item, work packet) |
| Queue lifecycle states | 8 (OPEN → CLOSED + REJECTED) |
| CLI commands | 6 |
| Test runner | 10/10 pass |
| Full lifecycle proven | ✅ OPEN → TRIAGED → APPROVED → IN_PROGRESS → FIXED → VERIFIED → CLOSED |

## Files

| File | Description |
|---|---|
| `docs/schemas/qa-diagnostic-report.schema.json` | Diagnostic report schema |
| `docs/schemas/qa-work-queue-item.schema.json` | Work queue item schema |
| `docs/schemas/qa-work-packet.schema.json` | Work packet schema |
| `scripts/qa_pilot_work_queue.py` | Queue management CLI |
| `scripts/test-qa-pilot-work-queue.sh` | 10/10 tests passing |
| `docs/governance/QA-PILOT-DIAGNOSTIC-TO-WORK-PACKET-CONTRACT.md` | This contract document |
| `data/diagnostics/` | Diagnostic report store |
| `data/work-queue/` | Queue item store (with index.json) |

## Key Invariants

| Invariant | Enforced By |
|---|---|
| QA-Pilot diagnoses, does not authorize | Diagnostic report has `no_authority_conferred: true` |
| Queue items are advisory | Queue item has `no_authority_conferred: true` |
| Work packets require authority grant | `authority.authorized_by` required in work packet schema |
| Full lifecycle traceability | Queue item references diagnostic; work packet references queue item |
| Human closes, never automation | VERIFIED is automated, CLOSED requires human |
