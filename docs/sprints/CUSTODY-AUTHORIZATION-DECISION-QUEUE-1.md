# CUSTODY-AUTHORIZATION-DECISION-QUEUE-1 — Custody Authorization Decision Queue

**Status:** 🔍 Active (sprint #31)
**Type:** Governance / decision queue
**Lane:** parallel_planning
**Boundary:** QA Pilot-local only
**Librarian impact:** none
**Input dependencies:** CUSTODY-STARTUP-REGRESSION-LOCK-1 (#30, sealed)

---

## Sprint Purpose

Add a governed Owner decision queue for custody-related startup findings, so startup can surface custody posture findings as explicit Owner decision candidates without allowing startup to approve, seal, mutate, or execute anything.

## Scope

**Allowed:**
- `docs/governance/CUSTODY-AUTHORIZATION-DECISION-QUEUE.md`
- `docs/schemas/custody-authorization-decision-queue.schema.json`
- `scripts/validate-custody-authorization-decision-queue.py`
- `scripts/test-custody-authorization-decision-queue.sh`
- `docs/examples/custody-authorization-decision-queue/` (16 fixtures)
- `docs/sprints/CUSTODY-AUTHORIZATION-DECISION-QUEUE-1.md`
- `project-state/sprint-ledger.json` (add sprint #31 entry)
- `FEATURE-STATUS.md` (add sprint status)
- `SESSION-HANDOFF.md` (update handoff)

**Nothing else.** No changes to #23–#30 sealed contracts, no startup-contract.json changes, no generic harness changes, no Librarian files.

## Rules Covered (12 CDQ rules)

| Rule | Assertion | Type |
|------|-----------|------|
| CDQ-1 | `advisory` must be `true` | Positive |
| CDQ-2 | `owner_required` must be `true` | Positive |
| CDQ-3 | No approve/seal/execute/write controls | Negative |
| CDQ-4 | No index mutation claim | Negative |
| CDQ-5 | No receipt creation claim | Negative |
| CDQ-6 | No sprint advancement claim | Negative |
| CDQ-7 | `source` must be `"startup_report"` | Positive |
| CDQ-8 | Cross-project entries require `owner_authorized: true` | Negative |
| CDQ-9 | Status must be `pending` on creation (post-creation: `owner_reviewed`/`deferred`) | Positive |
| CDQ-10 | `owner_decision` must be `null` on creation | Positive |
| CDQ-11 | `finding_type` must be from allowed set | Positive |
| CDQ-12 | `custody_context.contract_id` must reference valid sealed contract if present | Positive |

## Test Results

```
Test suite: 20/20 pass, 0 failed

Group 1 — Fixture validation:    16/16 pass (5 positive + 11 negative)
Group 2 — External regression:    4/4  pass (startup regression 15/15,
                                   parity matrix 13/13, existing validators 15/15,
                                   CRL lock #30 7/7 live)
```

## Hard Boundaries Enforced

- No Librarian files modified
- No custody receipts mutated
- No custody indexes mutated (#27)
- No custody surfaces altered (#28, #29)
- No startup-contract.json or generic harness changes
- No approval/seal/execute/write/sprint-start authority
- No cross-project mutation without explicit Owner authorization

## Next

Owner direction.
