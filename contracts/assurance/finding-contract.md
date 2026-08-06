# Assurance Finding Derivation Contract

**Extracted from:** EPIC-ASSURANCE-OPERATIONS-ADOPTION-1 (#207–#210)
**Sprint:** #215 — ASSURANCE-CONTRACT-EVIDENCE-STATE-CONTRACT-FORMALIZATION-1
**Status:** DRAFT — 🔍 Pending Owner review

---

## 1. Purpose

Formalize the transformation from evidence to finding. These three layers MUST remain distinct:

| Layer | Meaning | Example |
|-------|---------|---------|
| **Evidence** | What was observed | "Dependency manifest contains 127 local unversioned references" |
| **Finding** | Evaluation against a contract | "Dependency provenance assurance failure" |
| **Recommendation** | Proposed response (NON-authoritative) | "Consider establishing dependency provenance policy" |

## 2. Finding Derivation Model

```
Evidence
    +
Contract criteria
    |
    v
Finding
    |
    +--- classification (pass/advisory/fail)
    +--- severity (if applicable)
    +--- contract_ref (link to violated contract)
    |
    v
Recommendation (advisory only)
```

### 2.1 Finding Object

```
AssuranceFinding {
    finding_id: string,
    source: string,                    // Evidence source reference
    severity: "info" | "advisory" | "violation",
    evidence_refs: string[],           // Evidence IDs that support this finding
    contract_ref: string,              // Contract rule that was evaluated
    classification: "pass" | "advisory" | "fail",
    derived_at: ISO8601,
    derivation_chain: [                // Transparent chain of reasoning
        { step: string, evidence: string }
    ],
    recommendation: {                  // Advisory only — see §4
        description: string,
        proposed_action: string,
        owner_decision_required: boolean
    }
}
```

## 3. Three-Layer Separation (Cross-Consumer Invariant)

Every adoption baseline confirmed the same pattern. The three layers MUST NOT be conflated:

| Consumer | Evidence | Finding | Recommendation | Pattern Confirmed |
|----------|----------|---------|----------------|-------------------|
| QA Pilot | EP-* packets | Pipeline health (PH-*) | Recovery diagnostics | #207 |
| Librarian | Receipts, ledger | Adapter mapping gaps | Adapter creation | #207 |
| Agent Bridge | Intake receipts | Compound identity gap | Model note | #209 |
| Runtime Node | Health snapshots | Artifact/runtime distinction | Phase 4 extraction | #210 |

### 3.1 Prohibited Conflations

| Conflation | Risk | Contract Rule |
|------------|------|---------------|
| Evidence described as a finding | Analysis bias — observation becomes judgment before evaluation | FD-1 |
| Finding described as evidence | Circular reasoning — finding used as proof of itself | FD-2 |
| Recommendation described as a finding | Action bias — proposed fix treated as root cause | FD-3 |
| Finding implies authorization | Authority escalation — finding treated as dispatch command | FD-4 |
| Severity set without contract ref | Unbounded classification — severity floating without normative basis | FD-5 |

## 4. The Recommendation Layer MUST Remain Non-Authoritative

### 4.1 Allowed (QA Pilot)

| Action | Authority |
|--------|-----------|
| Detect a contract violation | ✅ YES — core function |
| Classify severity | ✅ YES — advisory only |
| Recommend remediation | ✅ YES — advisory only |
| Present evidence chain | ✅ YES — core function |
| Flag for Owner decision | ✅ YES — core function |

### 4.2 NOT Allowed (QA Pilot)

| Action | Authority |
|--------|-----------|
| Select remediation priority | ❌ NO — Owner decision |
| Approve risk acceptance | ❌ NO — Owner decision |
| Dispatch work | ❌ NO — Librarian authority |
| Override Owner decision | ❌ NO — never |
| Authorize any execution | ❌ NO — never |
| Escalate without Owner visibility | ❌ NO — all escalations visible |

### 4.3 Finding Derivation Rules

| Rule ID | Rule | Enforcement |
|---------|------|-------------|
| FD-1 | Every finding MUST reference exactly one or more evidence items | Schema validation |
| FD-2 | Every finding MUST reference at least one contract rule | Schema validation |
| FD-3 | Recommendation MUST be labeled `advisory_only: true` | Schema validation |
| FD-4 | Finding MUST NOT contain execution or dispatch instructions | Negative schema test |
| FD-5 | Severity WITHOUT contract_ref is invalid | Schema validation |
| FD-6 | A finding may not reference another finding as its primary evidence | Negative schema test |
| FD-7 | Evidence, findings, and recommendations must be independently reviewable | Design requirement |
| FD-8 | Absence of evidence is a valid finding (not a failure) | Contract rule |
