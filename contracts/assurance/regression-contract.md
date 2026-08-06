# Assurance Regression Contract

**Extracted from:** EPIC-ASSURANCE-OPERATIONS-ADOPTION-1 (#207–#210)
**Sprint:** #215 — ASSURANCE-CONTRACT-EVIDENCE-STATE-CONTRACT-FORMALIZATION-1
**Status:** DRAFT — 🔍 Pending Owner review

---

## 1. Purpose

Define the regression guard contract that converts verified remediations into permanent, machine-checkable assurance tests. This contract ensures that institutional knowledge is not lost after a fix is applied.

## 2. Regression Guard Lifecycle

```
Finding
    |
    v
Remediation Authorized (Owner decision)
    |
    v
Fix Applied (Librarian execution)
    |
    v
Verification (Assurance engine)
    |
    v
Regression Guard Created
    |
    v
Future Assurance Run
    |
    +--- If pass: continue
    +--- If fail: new finding (contract violation)
```

## 3. Regression Guard Object

```
RegressionGuard {
    guard_id: string,
    finding_ref: string,                  // Originating finding
    remediation_ref: string,              // Remediation that produced this guard
    evidence_refs: string[],              // Evidence chain
    contract_ref: string,                 // Assurance contract rule being guarded
    guard_type: "schema" | "validator" | "test" | "fixture" | "contract",
    guard_location: string,               // Path to guard artifact
    installed_at: ISO8601,
    invariant: string,                    // Human-readable: "What must remain true"
    test_command: string,                 // Machine-checkable: how to verify
    last_verified: ISO8601?,
    verification_result: "pass" | "fail" | "not_run"?
}
```

## 4. Regression Guard Types

| Type | Description | Example |
|------|-------------|---------|
| `schema` | Schema validation rule | "evidence_class must be present" |
| `validator` | Deterministic validation script | `validate-*-evidence-class.py` |
| `test` | Automated test case | "Record freshness does not degrade on re-validation" |
| `fixture` | Test fixture for expected behavior | Valid evidence fixture with known classification |
| `contract` | Governance contract entry | This document — contract text |

## 5. Regression Guard Rules

| Rule ID | Rule | Enforcement |
|---------|------|-------------|
| RG-1 | Every regression guard MUST trace to exactly one finding | Schema validation |
| RG-2 | Every regression guard MUST trace to at least one evidence item | Schema validation |
| RG-3 | A regression guard MUST be machine-checkable (testable by script or validator) | Contract rule |
| RG-4 | A regression guard MUST NOT produce false positives across any known valid system state | Test validation |
| RG-5 | A regression guard MUST be installed by the assurance engine, not by the remediator | Authority rule |
| RG-6 | A regression guard failure MUST produce a new finding (not auto-remediate) | Contract rule |
| RG-7 | Regression guards persist across sprint boundaries | Design requirement |
| RG-8 | Every closed remediation SHOULD produce a regression guard or document why not | Best practice |

## 6. The Valuable Artifact

The valuable artifact for institutional memory is:

> **Assurance Contract Violation**
> +
> **Accepted Remediation**
> +
> **Permanent Regression Guard**

Not "a test failed." Not "a finding was closed." The combined artifact of all three layers.

## 7. Cross-Consumer Regression Pattern

The adoption baselines confirmed that every consumer benefits from the same regression model:

| Consumer | Would Guard Against | Guard Form |
|----------|-------------------|------------|
| QA Pilot | Evidence class misclassification | Validator rule |
| Librarian | Evidence freshness conflation | Dashboard projection test |
| Agent Bridge | Snapshot accidentally stored as record | Schema validation |
| Runtime Node | Health check overwriting qualification | Write-path separation test |

## 8. Prohibited Patterns

| Pattern | Risk | Rule |
|---------|------|------|
| Self-verified remediation (no second party) | Circular verification | RG-5 |
| Regression guard without testable command | Orphaned rule — unenforceable | RG-3 |
| Auto-remediation on guard failure | Infinite fix loop | RG-6 |
| Regression guard removed without new finding | Silent gap | Contract review |
| Guard created before remediation verified | False positive on first run | Lifecycle rule |
