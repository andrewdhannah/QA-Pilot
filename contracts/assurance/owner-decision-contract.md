# Assurance Owner Decision Contract

**Extracted from:** EPIC-ASSURANCE-OPERATIONS-ADOPTION-1 (#207–#210)
**Sprint:** #215 — ASSURANCE-CONTRACT-EVIDENCE-STATE-CONTRACT-FORMALIZATION-1
**Status:** DRAFT — 🔍 Pending Owner review

---

## 1. Purpose

Formalize the governance invariant that survived across all 4 consumer adoption shapes:

> **QA Pilot = Observe, Measure, Classify, Recommend**
> **Librarian = Authorize, Dispatch, Record Custody**
> **Owner = Decide**

This is not a preference. It is an invariant confirmed by every adoption baseline.

## 2. Authority Boundary (Cross-Consumer Invariant)

| Layer | QA Pilot | Librarian | Owner |
|-------|----------|-----------|-------|
| Observe system state | ✅ YES | ❌ NO | ❌ NO |
| Measure against criteria | ✅ YES | ❌ NO | ❌ NO |
| Classify severity | ✅ YES | ❌ NO | ❌ NO |
| Propose remediation | ✅ YES | ❌ NO | ❌ NO |
| Escalate to Owner | ✅ YES | ❌ NO | ❌ NO |
| Authorize execution | ❌ NO | ✅ YES* | ✅ YES |
| Dispatch work | ❌ NO | ✅ YES* | ✅ YES |
| Record custody | ❌ NO | ✅ YES | ❌ NO |
| Accept risk | ❌ NO | ❌ NO | ✅ YES |
| Set priority | ❌ NO | ❌ NO | ✅ YES |
| Override any decision | ❌ NO | ❌ NO | ✅ YES |

*Librarian acts on Owner authorization

## 3. Owner Decision Object

```
OwnerDecision {
    decision_id: string,
    finding_ref: string | null,           // Optional — decision may be standalone
    remediation_ref: string | null,       // Required for remediation decisions
    decision_type: "accept_risk" | "authorize_remediation" |
                   "defer_remediation" | "reject_finding" |
                   "set_priority" | "promote_canonical" |
                   "direct_new_work" | "close",
    rationale: string,                    // REQUIRED — Owner's reasoning
    decided_at: ISO8601,
    decided_by: "owner",
    evidence_consumed: {                  // What evidence informed this decision
        records: string[],                // assurance_record references
        snapshots: string[],              // assurance_snapshot references
        classification: "record_only" | "snapshot_only" | "both"
    },
    decision_boundary: string             // What this decision does NOT authorize
}
```

### 3.1 Decision-Type Evidence Requirements

| Decision Type | Requires Record | Requires Snapshot | Notes |
|---------------|----------------|-------------------|-------|
| `accept_risk` | ✅ Yes | Optional | Risk acceptance needs historical basis |
| `authorize_remediation` | ✅ Yes | ✅ Yes | Both historical proof and current state needed |
| `defer_remediation` | ✅ Yes | Optional | Deferral uses finding evidence |
| `reject_finding` | ✅ Yes | Optional | Rejection must reference evidence |
| `set_priority` | Optional | Optional | Priority is a governance decision |
| `promote_canonical` | ✅ Yes | Optional | Canonical promotion uses migration receipts |
| `direct_new_work` | Optional | Optional | New work may not need existing evidence |
| `close` | ✅ Yes | Optional | Closure must reference final evidence |

## 4. What QA Pilot MUST NOT Do

The following are mechanically enforced by the assurance contract:

| Action | Contract Rule | Enforcement Mechanism |
|--------|---------------|----------------------|
| Authorize work execution | OD-AUTH-1 | Schema validation — no `authorization` field in QA Pilot output |
| Dispatch work packets | OD-DISP-1 | QA Pilot output schema excludes `dispatch` fields |
| Override an Owner decision | OD-OVR-1 | QA Pilot finding for a closed item MUST reference the closure decision |
| Auto-accept risk | OD-RISK-1 | Risk decisions require explicit Owner action |
| Self-seal its own sprints | OD-SEAL-1 | Seal authority requires Owner confirmation |
| Promote to canonical | OD-CAN-1 | Canonical promotion is an Owner decision |
| Set cross-project priority | OD-PRI-1 | Priority is Owner governance, not QA Pilot assessment |
| Escalate outside Owner visibility | OD-ESC-1 | All escalations visible in Owner dashboard |

## 5. Owner Decision Validation Rules

| Rule ID | Rule | Enforcement |
|---------|------|-------------|
| OD-1 | Every decision MUST have a `decision_type` | Schema validation |
| OD-2 | Every decision MUST have a `rationale` (minimum 1 character) | Schema validation |
| OD-3 | Every decision MUST specify `evidence_consumed.classification` | Schema validation |
| OD-4 | `authorize_remediation` decisions MUST reference both records and snapshots | Schema validation |
| OD-5 | Every decision MUST include `decision_boundary` describing what it does NOT authorize | Schema validation |
| OD-6 | QA Pilot output MUST NOT contain `authorization` or `dispatch` fields | Negative schema test |
| OD-7 | QA Pilot output MUST NOT contain `owner_decision` fields with `decided_by: "qa_pilot"` | Negative schema test |
| OD-8 | A finding classified as `closed` MUST reference an Owner decision or be self-invalidating | Schema validation |
| OD-9 | QA Pilot MUST flag every pending Owner decision in the startup surface | Startup surface rule |

## 6. Decision Boundary Examples

| Scenario | QA Pilot Produces | QA Pilot Does NOT Produce |
|----------|-------------------|--------------------------|
| Finding: analytics drift | Finding + recommendation + Owner flag | Priority assignment, disable command |
| Finding: insecure patterns | Severity classification + evidence chain | Remediation timeline, work dispatch |
| Finding: unversioned deps | Dependency inventory + gap assessment | Dependency policy, pinning decision |
| Request: canonical promotion | Migration evidence + status report | Canonical promotion decision |
| Request: sprint seal | Acceptance gate summary | Seal authority |
