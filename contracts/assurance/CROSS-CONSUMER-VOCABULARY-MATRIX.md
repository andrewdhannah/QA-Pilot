# Cross-Consumer Common Vocabulary Matrix

**Extracted from:** EPIC-ASSURANCE-OPERATIONS-ADOPTION-1 (#207–#210)
**Sprint:** #215 — ASSURANCE-CONTRACT-EVIDENCE-STATE-CONTRACT-FORMALIZATION-1

## Purpose

Prove that all 4 consumer shapes produce a common assurance vocabulary. A concept is "universal" only if it appears in every consumer without modification.

## Concept Matrix

| Concept | QA Pilot | Librarian (#207) | Agent Bridge (#209) | Runtime Node (#210) | Universal? |
|---------|----------|-----------------|---------------------|---------------------|------------|
| **Evidence identity** | EP-* IDs | Receipt IDs | AB-* intake IDs | RN-* receipt IDs | ✅ YES |
| **Evidence timestamp** | Every evidence item | Every receipt | Every artifact | Every qualification record | ✅ YES |
| **Evidence source tracking** | source_project | project identity | project metadata | project + companion repo | ✅ YES |
| **assurance_record** | All 11+ types | 4 receipt types | 4 intake types | 4 record types | ✅ YES |
| **assurance_snapshot** | N/A (none exist) | N/A (none exist) | 3 snapshot types | 5 snapshot types | ✅ Conditional* |
| **Evidence → Finding derivation** | PH-*, DR-*, RD-* | Adapter gaps | Compound identity gap | Artifact/runtime distinction | ✅ YES |
| **Finding → Contract ref** | Each rule has ID | Gap → AD-* gate | Gap → AB-AD-* gate | Finding → RN-AD-* gate | ✅ YES |
| **Recommendation (advisory)** | Recovery diagnostics | ADAPT outcome | Model note | Phase 4 extraction | ✅ YES |
| **Owner decision boundary** | OD-* receipts | Owner seal records | Owner authority model | Owner seal records | ✅ YES |
| **Regression guard** | MR-*, SR-*, CRL-* rules | Via adapter | Via adapter | Via adapter | ✅ YES |
| **Absence = valid info** | Pipeline layer gaps | Missing lifecycle concepts | Missing ledger | Missing loop | ✅ YES |
| **Adapter boundary** | Internal | Librarian adapter | Agent Bridge adapter | Runtime Node adapter | ✅ YES |
| **Compound identity** | Single project | Single project | Multi-component | Single + companion repo | ❌ Partial |
| **Runtime evidence** | None | None | Mixed (3 snapshots) | Mixed (5 snapshots) | ❌ Conditional |

*\*assurance_snapshot is universal as a concept — every consumer COULD produce snapshots. The model must handle both even if a consumer currently produces only records.*

## Universal Invariants

The following 10 invariants survived across ALL 4 consumer shapes:

```
EV-ID-1    Evidence has identity + observation + context
EV-CLASS-1 Evidence is either record or snapshot
EV-REC-1   Records are immutable
EV-SNP-1   Snapshots are transient
EV-SEP-1   Record ≠ snapshot — no cross-mutation
EV-ABS-1   Absence is valid information
EV-GOV-1   Governance concepts map directly
EV-ADP-1   Project-specific mechanics go in adapters
EV-AUTH-1  Authority boundary is invariant
FD-1, FD-2 Findings trace to evidence + contract
```

## Non-Universal Observations

| Observation | Consumers | Classification |
|-------------|-----------|----------------|
| Compound identity | Agent Bridge only | Project topology — not assurance property |
| Runtime evidence | Agent Bridge + Runtime Node | Conditional on project type — model handles via snapshot class |
| Continuous assurance loop | QA Pilot only | Implementation choice — not assurance contract |
| Structured sprint ledger | QA Pilot + Librarian | Format choice — adapter handles |
