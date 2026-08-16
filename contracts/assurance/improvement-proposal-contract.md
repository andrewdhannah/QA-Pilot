# Improvement Proposal Contract

**Sprint:** QA-PILOT-IMPROVEMENT-PROPOSAL-BRIDGE-1 (#242)
**Status:** ACTIVE — Owner-authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define the bridge between preventive recommendations and governed work proposals.

## 2. Core Invariant

```
Recommendation → Owner Review → Work Proposal → Work Packet

Direct creation is prohibited.
Owner decision is required at every state change.
```

## 3. Proposal States

| State | Meaning | Next States |
|-------|---------|-------------|
| `pending_owner_review` | Awaiting Owner decision | accepted, rejected, deferred |
| `accepted` | Owner approved | Ready for work packet creation |
| `rejected` | Owner declined | Terminal state |
| `deferred` | Owner postponed | pending_owner_review (re-review) |
| `converted` | Became work packet | Terminal state |

## 4. Proposal Record

```json
{
  "proposal_id": "IP-001",
  "project_id": "agent-bridge",
  "created_at": "2026-08-16T06:15:00Z",
  "recommendation_refs": ["PR-001"],
  "evidence_refs": ["CD-001"],
  "risk_context": {
    "current_risk": 42,
    "risk_band": "monitor"
  },
  "economic_context": {
    "attention_score": 35,
    "attention_level": "medium"
  },
  "expected_outcome": "Improved evidence coverage reducing future qualification findings",
  "status": "pending_owner_review",
  "owner_decision": null,
  "owner_rationale": null,
  "work_packet_id": null,
  "advisory_only": true
}
```

## 5. Owner Decision Rules

| Decision | Effect | System Action |
|----------|--------|---------------|
| `accepted` | Proposal approved for work | Ready for work packet creation |
| `rejected` | Proposal declined | No further action |
| `deferred` | Proposal postponed | Return to pending_owner_review |

## 6. Non-Authority Boundary

Proposals:

| May Do | May Not Do |
|--------|------------|
| Package recommendations | Create work packets |
| Track owner decisions | Dispatch agents |
| Reference evidence | Approve remediation |
| Show context | Modify risk state |
| Wait for decision | Auto-convert to work |
