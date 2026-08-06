# QA-PILOT-DEPENDENCY-RISK-CAPABILITY-1 — Dependency Risk Capability

**Type:** implementation / assurance profile
**Status:** ✅ **SEALED — Implementation complete, all gates pass**
**Lane:** implementation
**Boundary:** QA Pilot-local
**Librarian impact:** none
**Dependencies:** #185 (assurance profile architecture), #186 (privacy profile exposed dependency surfaces)
**Consumed by:** #188 (security assurance profile)

---

## Purpose

Implement dependency risk analysis capability using the #185 assurance profile architecture. Discovers application dependencies (libraries, CDNs, external services, scripts), checks version status, identifies known risks, and produces structured evidence for #188 consumption.

---

## Scope

### Included

| # | Area | Action |
|---|------|--------|
| 1 | Dependency inventory | Discover all external dependencies (scripts, CDNs, libraries, packages, services) — deduplicated across sources |
| 2 | Version analysis | Extract version information where available |
| 3 | Risk identification | Outdated/pinned/unversioned dependencies flagged with taxonomy classification |
| 4 | Evidence classification | Findings classified as PASS / OBSERVATION / OWNER_DECISION_REQUIRED |
| 5 | Profile linkage | Output conforms to #185 assurance profile contract schema |
| 6 | #188 handoff | Evidence marked consumable_by: "#188" |

### Non-Scope

- Automatic upgrades
- Vulnerability remediation
- Package replacement
- CVE database integration (future)
- Blocking builds from dependency findings alone
- Treating observations as failures without Owner classification
- Expanding into security assurance controls owned by #188

---

## Implementation

### Script

`scripts/qa_pilot_dependency_risk_capability.py`

- Architecture basis: QA-PILOT-ASSURANCE-PROFILE-ARCHITECTURE-1 (#185)
- Profile: DEPENDENCY-RISK-1 (3 controls: DR-INVENTORY, DR-VERSION, DR-RISK)
- Consumed by: #188 Security Assurance Profile

### Profile Controls

| Control | Description | Evidence Required |
|---------|-------------|------------------|
| DR-INVENTORY | Dependency inventory is complete and categorized | implementation |
| DR-VERSION | Dependency version metadata is available and verifiable | implementation |
| DR-RISK | Dependency risk findings are classified and actionable | implementation, documentation |

### Evidence Output

| Artifact | Path |
|----------|------|
| Dependency evidence (assurance_report format) | `data/dependency-risk-evidence.json` |
| Profile contract (per #185 schema) | `data/dependency-risk-profile-contract.json` |

---

## Results

| Metric | Value |
|--------|-------|
| Dependencies (deduplicated) | 28 |
| Local libraries | 28 |
| CDN dependencies | 0 |
| External services | 0 |
| Overall classification | OBSERVATION |
| Owner action required | No |
| Consumable by #188 | Yes |

### Control Results

| Control | Result |
|---------|--------|
| DR-INVENTORY | ✅ PASS — Inventory complete, all dependencies categorized |
| DR-VERSION | ⚠️ OBSERVATION — 28 unversioned local dependencies |
| DR-RISK | ⚠️ OBSERVATION — 28 findings, all OBSERVATION (unversioned local deps) |

---

## Acceptance Gates

| Gate | Requirement | Result |
|------|-------------|--------|
| DR-1 | Dependency inventory complete — deduplicated across source files | ✅ PASS |
| DR-2 | Dependency evidence has provenance (timestamp, source file, scan method) | ✅ PASS |
| DR-3 | Version analysis is reproducible (same source → same results) | ✅ PASS |
| DR-4 | Findings classification is explicit (PASS / OBSERVATION / OWNER_DECISION_REQUIRED) | ✅ PASS |
| DR-5 | Owner decision boundary preserved — no automated remediation | ✅ PASS |
| DR-6 | No package changes, source modifications, or dependency upgrades made | ✅ PASS |
| DR-7 | Evidence retained for audit (`data/dependency-risk-evidence.json`) | ✅ PASS |
| DR-8 | Output conforms to #185 assurance profile contract schema | ✅ PASS |

**8 PASS, 0 FAIL — All gates pass.**

---

## Constraint Compliance

| Constraint | Status |
|------------|--------|
| No automated dependency remediation | ✅ Preserved |
| No automatic upgrades/version changes | ✅ Preserved |
| No blocking builds solely from dependency findings | ✅ Preserved |
| No treating observations as failures without Owner classification | ✅ Preserved |
| No expanding into security assurance controls owned by #188 | ✅ Preserved |
| Evidence consumable by #188 without migration | ✅ `consumable_by: "#188"` field present |

---

## Core Invariant

```
Risk Finding ≠ Vulnerability Decision ≠ Remediation Authorization ≠ Change Execution
✅ Preserved — capability produces advisory findings only.
```

---

**Status:** ✅ SEALED — Implementation complete, all 8 gates pass
**Ledger entry:** #187 (sealed)
