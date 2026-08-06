# CUSTODY-AUTHORIZATION-DECISION-QUEUE.md — Custody Authorization Decision Queue

**Status:** 🔍 Active (sprint #31)
**Authority:** Read-only-to-startup, Owner-governed decision queue for custody posture findings surfaced during startup. Queue entries are advisory and pending Owner action only. No entry may count as approval, seal, execution, sprint start, or custody mutation.
**Sprint:** CUSTODY-AUTHORIZATION-DECISION-QUEUE-1

---

## 1. Purpose

Add a governed Owner decision queue for custody-related startup findings, allowing startup to surface custody posture findings as explicit Owner decision candidates without allowing startup to approve, seal, mutate, or execute anything.

## 2. Data Flow

```
Startup (#29) → Custody Posture Report → Decision Queue (this sprint) → Owner Review → Owner Decision
     ↑                    ↑                          ↑                         ↑
  read-only           advisory only           pending action          explicit authorization
```

| Layer | Component | Authority |
|-------|-----------|-----------|
| Startup report | `custody-surface-startup-integration.py` (#29) | Read-only posture |
| Regression lock | `CRL rules` (#30) | Read-only lock |
| Decision queue | This sprint | Advisory queue only |
| Owner decision | Owner decision receipt | Authoritative |

## 3. Queue Entry Schema

Each queue entry has the following structure:

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `entry_id` | string | yes | Unique, deterministic format: `CDQ-<timestamp>-<sequence>` |
| `queued_at` | string (ISO 8601) | yes | When the entry was created |
| `status` | string | yes | One of: `pending`, `owner_reviewed`, `deferred` |
| `source` | string | yes | Must be `"startup_report"` |
| `finding_type` | string | yes | One of: `degraded_custody`, `missing_receipt`, `stale_index`, `violation_detected`, `review_item`, `cross_project_reference` |
| `description` | string | yes | Human-readable finding description (1-500 chars) |
| `custody_context` | object | yes | Reference to the specific custody finding including contract_id, receipt_count, detail |
| `advisory` | boolean | yes | Must be `true` — queue entries are always advisory |
| `owner_required` | boolean | yes | Must be `true` — Owner decision required |
| `owner_decision` | string or null | no | Must be `null` on creation; one of `accept`, `reject`, `defer` after Owner review |
| `owner_decided_at` | string or null | no | Timestamp when Owner made decision |
| `cross_project` | boolean | no | If `true`, must include `owner_authorized: true` |
| `owner_authorized` | boolean | no | If `cross_project` is `true`, must be `true` |

## 4. Invariants (CDQ rules)

| Rule | Assertion | Type |
|------|-----------|------|
| CDQ-1 | Queue entry must have `advisory: true` | Positive |
| CDQ-2 | Queue entry must have `owner_required: true` | Positive |
| CDQ-3 | Queue entry must have no approve/seal/execute/write controls | Negative |
| CDQ-4 | Queue entry must not claim to mutate custody index | Negative |
| CDQ-5 | Queue entry must not claim to create custody receipt | Negative |
| CDQ-6 | Queue entry must not claim to advance active sprint | Negative |
| CDQ-7 | Queue entry `source` must be `"startup_report"` only | Positive |
| CDQ-8 | Cross-project entries rejected unless `owner_authorized: true` | Negative |
| CDQ-9 | Queue entry `status` must be `"pending"` on creation | Positive |
| CDQ-10 | `owner_decision` must be `null` on creation | Positive |
| CDQ-11 | `finding_type` must be from allowed set | Positive |
| CDQ-12 | `custody_context.contract_id` must reference a valid sealed contract if present | Positive |

## 5. Positive Fixtures

| Fixture | Rule | Description |
|---------|------|-------------|
| `queue-pending-degraded-custody.json` | CDQ-1,2,7,9,10,11 | Normal degraded custody finding, status pending |
| `queue-pending-missing-receipt.json` | CDQ-1,2,7,9,10,11 | Missing receipt finding, status pending |
| `queue-pending-stale-index.json` | CDQ-1,2,7,9,10,11 | Stale index finding, status pending |
| `queue-owner-reviewed-accepted.json` | CDQ-1,2,7,10,11 | Owner reviewed and accepted |
| `queue-cross-project-authorized.json` | CDQ-8 | Cross-project entry with owner_authorized: true |

## 6. Negative Fixtures

| Fixture | Rule | Description |
|---------|------|-------------|
| `queue-advisory-false.json` | CDQ-1 | `advisory: false` — rejected |
| `queue-owner-required-false.json` | CDQ-2 | `owner_required: false` — rejected |
| `queue-claims-approve-control.json` | CDQ-3 | Claims approve or seal control — rejected |
| `queue-claims-index-mutate.json` | CDQ-4 | Claims to mutate custody index — rejected |
| `queue-claims-receipt-create.json` | CDQ-5 | Claims to create custody receipt — rejected |
| `queue-claims-sprint-advance.json` | CDQ-6 | Claims to advance active sprint — rejected |
| `queue-source-not-startup.json` | CDQ-7 | Source is not "startup_report" — rejected |
| `queue-cross-project-unauthorized.json` | CDQ-8 | Cross-project without owner_authorized — rejected |
| `queue-status-not-pending.json` | CDQ-9 | Status is not "pending" on creation — rejected |
| `queue-owner-decision-not-null.json` | CDQ-10 | owner_decision set on creation — rejected |

## 7. Non-Goals

- No startup approval, seal, execution, or write authority
- No custody receipt creation
- No custody index mutation
- No custody surface mutation
- No active sprint advancement
- No cross-project mutation without explicit Owner authorization
- No bypass of GLOBAL-STARTUP-INTENT-AUTHORIZATION-CONTRACT-1

## 8. Boundary Invariants

1. Queue entries are advisory-only (`advisory: true`)
2. Queue entries require Owner decision before any state change
3. Queue entries do not create, mutate, or approve custody state
4. Cross-project entries require explicit `owner_authorized: true`
5. `finding_type` is restricted to the allowed set
6. `status` must be `pending` on creation; transitions only via Owner decision
7. All #23–#30 regression rules remain green
