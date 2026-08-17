# Sprint — QA-PILOT-WORK-PACKET-INTEGRATION-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #243 (proposed)
**Lane:** assurance / governance
**Type:** Work packet integration — proposal to governed execution
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Phase:** Phase 6 — Governed Improvement Activation
**Predecessor:** QA-PILOT-IMPROVEMENT-PROPOSAL-BRIDGE-1 (#242, complete)

---

## 1. Purpose

Connect accepted improvement proposals to the Librarian work packet boundary while preserving owner authority.

**The narrowest remaining contract between the assurance layer and the governance substrate.**

## 2. The Handoff

```
Accepted Improvement Proposal
            ↓
      Work Packet Creation Request
            ↓
      Librarian Work Packet Service (#546)
            ↓
      Governed Execution
            ↓
      New Evidence
            ↓
      Qualification Loop
```

## 3. Receipt Chain

The complete provenance loop:

```
PR-* Preventive Recommendation
        ↓
IP-* Improvement Proposal
        ↓
OD-* Owner Decision
        ↓
WP-* Work Packet
        ↓
Execution Evidence
        ↓
Future Qualification
```

## 4. Handoff Adapter Rules

The adapter performs only translation:

| May Do | May Not Do |
|--------|------------|
| Translate proposal to request | Dispatch agents |
| Reference evidence | Assign owners |
| Include risk context | Modify lifecycle state |
| Include owner decision | Approve execution |

## 5. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| WP-001 | Accepted proposals only | create-all only processes accepted proposals. Rejected/pending proposals are ignored. | ✅ |
| WP-002 | Rejection isolation | Rejected proposals do not generate requests, no penalty | ✅ |
| WP-003 | Authority preservation | QA-Pilot proposes, Librarian records, Owner authorizes, Agents execute | ✅ |
| WP-004 | Round-trip evidence | Provenance chain: PR → IP → OD → WP → Execution Evidence | ✅ |
| WP-005 | Provenance chain complete | Every request references proposal, recommendation, evidence, owner decision | ✅ |
| WP-006 | Advisory boundary preserved | Requests do not increase authority. advisory_only=true. | ✅ |
| WP-007 | Existing validators pass | No regressions from #242 baseline | ✅ |

## 6. Guardrails

| Guardrail | Rule |
|-----------|------|
| Translation only | Adapter translates, does not act |
| Owner-gated | Only accepted proposals proceed |
| No auto-mutation | System does not create work from proposals |
| Provenance complete | Full traceability through chain |
| Advisory | Work requests are advisory until Owner authorizes |

## 7. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-WORK-PACKET-INTEGRATION-1.md` | This sprint document |
| `contracts/assurance/work-packet-request-contract.md` | Work packet request contract |
| `docs/schemas/assurance/work-packet-request-v1.schema.json` | Request schema |
| `scripts/create-work-packet-request.py` | Handoff adapter |
| `data/assurance/work-packet-requests/` | Request records |

## 8. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #243 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 9. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-IMPROVEMENT-PROPOSAL-BRIDGE-1 (#242) | ✅ Complete |
| Improvement proposals | ✅ Working |
| Librarian Work Packet Service (#546) | ✅ Available |
| Owner decision tracking | ✅ Working |
