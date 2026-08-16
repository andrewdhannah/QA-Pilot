# Sprint — QA-PILOT-IMPROVEMENT-PROPOSAL-BRIDGE-1

**Status:** ✅ Authorized — Owner-authorized 2026-08-16
**Ledger:** #242 (proposed)
**Lane:** assurance / governance
**Type:** Improvement proposal bridge — recommendation to governed work
**Boundary:** QA Pilot-local advisory surface only
**Librarian impact:** contract_interface
**Phase:** Phase 6 — Governed Improvement Activation
**Predecessor:** QA-PILOT-PREVENTIVE-RECOMMENDATIONS-1 (#241, complete)

---

## 1. Purpose

Create the narrow bridge between recommendation artifacts and governed work proposals.

**NOT:**
- Creating work
- Dispatching agents
- Approving remediation
- Changing risk state

**Only:**
Transform an assurance recommendation into an owner-reviewable proposal.

## 2. The Governance Boundary

```
QA-Pilot
  │
  │ Preventive Recommendation (advisory)
  │
  △
Owner Review Queue
  │
  │ accepted / rejected / deferred
  │
  △
Work Proposal
  │
  △
Librarian Work Packet Service (#546)
  │
  △
Execution
  │
  △
Evidence
  │
  △
Future Qualification
```

## 3. Critical Gates

### Gate 1 — Recommendation Provenance

Every proposal must answer:
- Why was this proposed?
- Which evidence supports it?
- Which prediction produced it?

### Gate 2 — No Automatic Mutation

Direct creation is prohibited:

```
Recommendation
      X
Work Packet
```

Required path:

```
Recommendation
      ↓
Owner Review
      ↓
Work Proposal
      ↓
Work Packet
```

### Gate 3 — Rejection is Valid

A mature governance loop must support:

```
Recommendation
      ↓
Owner Review
      ↓
Rejected
```

Without creating a finding, failure, or system penalty.

### Gate 4 — Accepted Proposal Handoff

Only after owner acceptance:

```
Improvement Proposal
      ↓
Authorized Work Proposal
      ↓
Librarian Work Packet
```

## 4. Acceptance Gates

| Gate | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| BRIDGE-001 | Recommendation provenance traceable | Every proposal references recommendation, evidence, risk_context, economic_context | ✅ |
| BRIDGE-002 | No automatic mutation | Recommendations do not directly create work packets | ✅ |
| BRIDGE-003 | Rejection is valid | Owner can reject without system penalty | ✅ |
| BRIDGE-004 | Accepted proposal handoff works | Accepted proposal shows "Ready for work packet creation" | ✅ |
| BRIDGE-005 | Owner decision state tracked | Proposals track pending_owner_review/accepted/rejected/deferred | ✅ |
| BRIDGE-006 | Advisory boundary preserved | Proposals do not increase authority. advisory_only=true. | ✅ |
| BRIDGE-007 | Existing validators pass | No regressions from #241 baseline | ✅ |

## 5. Guardrails

| Guardrail | Rule |
|-----------|------|
| Bridge only | Converts recommendations to proposals, not work |
| Owner-gated | All state changes require Owner decision |
| No auto-mutation | System cannot create work from recommendations |
| Rejection valid | Owner can reject without penalty |
| Provenance complete | Full traceability from recommendation to proposal |
| Advisory | Proposals are advisory until Owner accepts |

## 6. Files to Create

| File | Purpose |
|------|---------|
| `docs/sprints/QA-PILOT-IMPROVEMENT-PROPOSAL-BRIDGE-1.md` | This sprint document |
| `contracts/assurance/improvement-proposal-contract.md` | Proposal contract |
| `docs/schemas/assurance/improvement-proposal-v1.schema.json` | Proposal schema |
| `scripts/generate-proposals.py` | Proposal generator |
| `data/assurance/improvement-proposals/` | Proposal records |

## 7. Files to Modify

| File | Change |
|------|--------|
| `project-state/sprint-ledger.json` | Add entry #242 |
| `FEATURE-STATUS.md` | Add sprint status entry |
| `SESSION-HANDOFF.md` | Update authorized work |

## 8. Dependencies

| Dependency | Status |
|------------|--------|
| QA-PILOT-PREVENTIVE-RECOMMENDATIONS-1 (#241) | ✅ Complete |
| Preventive recommendations | ✅ Working |
| Risk engine | ✅ Working |
| Economics engine | ✅ Working |
| Librarian Work Packet Service (#546) | ✅ Available |
