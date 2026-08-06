# QA-PILOT-DEPENDENCY-RISK-PLANNING-DEFINITION.md — #187 Dependency Risk Capability

**Status:** 🔍 Draft (planned — pre-implementation)
**Authority:** Advisory-only. No approval, seal, execution, write, or sprint-start authority conferred.
**Predecessor:** #186 Privacy Assurance Profile

---

## 1. Purpose

Define the evidence model, finding classifications, acceptance gates, and boundary constraints for a governed Dependency Risk Capability before any dependency scanning or integration work begins.

---

## 2. Architecture Position

```
Assurance Framework (#185)
    │
    ├── #186 Privacy Assurance Profile     ✅ Sealed
    │
    ├── #187 Dependency Risk Capability    ⏳ This definition
    │
    ├── #188 Security Assurance Profile    🔜
    │
    └── Release Readiness Profile          🔜
```

**Dependency relation:** #187 fills the dependency evidence gap that #186 privacy profiling cannot evaluate. Privacy can identify that a dependency exists (PRIV-THIRD-PARTY). #187 evaluates the technical risk that dependency creates.

---

## 3. Core Invariant

**Risk Finding ≠ Vulnerability Decision ≠ Remediation Authorization ≠ Change Execution**

| Phase | Actor | Artifact |
|-------|-------|----------|
| Dependency inventory | Automation | Dependency Evidence Record |
| Version analysis | Automation | Version Analysis Record |
| Risk finding classification | Automation | RiskFinding with evidence |
| Owner decision | Owner | Decision receipt |
| Remediation | Owner or authorized agent | Change execution record |

No phase may skip to a later phase without completing the prior phase's artifact.

---

## 4. Evidence Model

### 4.1 Dependency Evidence Record

Each dependency scanned becomes a `DependencyEvidenceRecord` with the following fields:

| Field | Type | Required | Source |
|-------|------|----------|--------|
| `package_name` | string | yes | Manifest parsing |
| `version` | string | yes | Manifest parsing |
| `source` | enum | yes | `npm`, `pypi`, `rubygems`, `homebrew`, `spm`, `cocoapods`, `cargo`, `direct`, `other` |
| `license` | string | conditional | Package metadata |
| `direct_transitive` | enum | yes | `direct`, `transitive` |
| `dependency_graph` | [string] | conditional | Resolved dependency tree |
| `provenance` | string | yes | File path + line number of declaration |
| `evidence_sha` | string | yes | SHA-256 of the resolved dependency record |

### 4.2 Version Analysis Record

| Field | Type | Required | Source |
|-------|------|----------|--------|
| `package_name` | string | yes | Cross-ref with Dependency Evidence Record |
| `current_version` | string | yes | From dependency manifest |
| `latest_version` | string | conditional | Package registry API |
| `release_date` | string | conditional | Package registry metadata |
| `supported_lifecycle` | enum | conditional | `active`, `maintenance`, `end_of_life`, `unknown` |
| `lifecycle_source` | string | conditional | URL or reference for lifecycle status |
| `abandoned` | boolean | yes | Heuristic: no release in >2 years |
| `version_drift_major` | int | yes | Latest major minus current major |
| `version_drift_minor` | int | yes | Latest minor minus current minor |
| `version_drift_patch` | int | yes | Latest patch minus current patch |

### 4.3 Risk Finding Record

| Field | Type | Required | Source |
|-------|------|----------|--------|
| `finding_id` | string | yes | Generated: `DRF-{timestamp}-{seq}` |
| `package_name` | string | yes | Cross-ref |
| `finding_type` | enum | yes | `outdated`, `unsupported`, `abandoned`, `license_conflict`, `transitive_depth`, `duplicate`, `version_pinning` |
| `classification` | enum | yes | `INFORMATIONAL`, `OBSERVATION`, `OWNER_DECISION_REQUIRED` |
| `evidence_refs` | [string] | yes | References to Dependency Evidence + Version Analysis records |
| `rationale` | string (min 10) | yes | Why this finding matters |
| `owner_decision_prompt` | string | conditional | What the Owner must decide (only when classification = OWNER_DECISION_REQUIRED) |
| `created_at` | string | yes | ISO 8601 |

---

## 5. Finding Classifications

| Classification | Meaning | Owner Action |
|---------------|---------|--------------|
| `INFORMATIONAL` | Dependency exists; no risk detected | None required — recorded for audit |
| `OBSERVATION` | Dependency has notable characteristics (old version, deep transitive chain) | Review if relevant to current work |
| `OWNER_DECISION_REQUIRED` | Dependency is unsupported, abandoned, or has blocking characteristics | Owner must decide: accept risk, defer, schedule remediation, or reject |

**Classification boundaries:**

| Condition | Classification |
|-----------|---------------|
| Dependency is on latest minor/patch within supported lifecycle | `INFORMATIONAL` |
| Dependency is >1 major version behind but still in supported lifecycle | `OBSERVATION` |
| Dependency is in maintenance or end-of-life lifecycle | `OWNER_DECISION_REQUIRED` |
| Dependency is abandoned (no release in >2 years) | `OWNER_DECISION_REQUIRED` |
| Dependency has no declared license | `OBSERVATION` |
| Dependency is a transitive duplicate of a direct dependency | `OBSERVATION` |

---

## 6. Acceptance Gates

| Gate ID | Requirement | Verification |
|---------|-------------|--------------|
| DR-1 | Dependency inventory generated from all declared manifests | Script walks known manifest paths; reports coverage gaps |
| DR-2 | Every Dependency Evidence Record has provenance | Record includes file path + line number of declaration |
| DR-3 | Version analysis is reproducible | Same manifest inputs produce same version analysis outputs (version-pinned sources) |
| DR-4 | Finding classification is explicit per §5 table | Classification must be one of the three values; rationale must reference the condition that triggered it |
| DR-5 | Owner decision boundary preserved | No `OWNER_DECISION_REQUIRED` finding is automatically resolved, dismissed, or remediated by automation |
| DR-6 | No automated remediation | No script or pipeline step upgrades, replaces, or removes dependencies |
| DR-7 | Evidence retained for audit | All records written to a timestamped evidence bundle; bundle hash recorded |

---

## 7. Boundary Constraints

### 7.1 In Scope

- Enumerating declared dependencies from manifest files
- Resolving transitive dependency trees where manifest data permits
- Analyzing version recency against package registry data
- Identifying unsupported, abandoned, or lifecycle-expired dependencies
- Producing finding classifications with evidence references
- Recording Owner decisions against findings

### 7.2 Not In Scope

```
✗ Dependency upgrades or version bumps
✗ Package replacement recommendations
✗ Vulnerability database correlation (CVE, OSV, NVD)
✗ Build-time dependency verification
✗ Runtime dependency monitoring
✗ SBOM generation (future capability)
✗ Security certification assertions
✗ Automatic release blocking
```

### 7.3 Explicit Non-Scope Rationale

**Vulnerability correlation is excluded** because it requires a different evidence model (CVE data sources, CVSS scoring, exploitability analysis) and a different authority boundary (security disclosure handling). #187 is a **dependency risk inventory**, not a vulnerability scanner. Vulnerability correlation belongs in #188 Security Assurance Profile, which can consume #187's evidence records as input.

**SBOM generation is excluded** because SPDX/CycloneDX output formats require a different serialization layer and are consumed by different stakeholders (procurement, compliance). #187's evidence model is designed to be transformable into SBOM formats, but the transformation is not the primary capability.

---

## 8. Implementation Sequence

```
Phase 1: Manifests
    │
    ├── Identify all project manifest locations
    │   (Package.swift, package.json, requirements.txt, Podfile, etc.)
    │
    ├── Parse declared dependencies
    │
    └── Generate Dependency Evidence Records
    │
Phase 2: Registry
    │
    ├── Query package registries per source type
    │
    ├── Resolve latest versions and lifecycle status
    │
    └── Generate Version Analysis Records
    │
Phase 3: Classification
    │
    ├── Apply classification rules per §5
    │
    ├── Generate Risk Finding Records
    │
    └── Produce evidence bundle
    │
Phase 4: Owner Surface
    │
    ├── Present findings in reviewable format
    │
    ├── Record Owner decisions
    │
    └── Archive evidence for audit
```

---

## 9. Evidence Bundle Output

Each `#187 Dependency Risk` run produces:

```
dependency-risk-evidence-{timestamp}/
    ├── manifest-inventory.json          # DR-1: all manifests found
    ├── dependency-records.json          # DR-2: per-dependency evidence
    ├── version-analysis.json            # DR-3: per-dependency version analysis
    ├── risk-findings.json               # DR-4: classified findings
    ├── owner-decisions.json             # DR-5: Owner decision records
    ├── evidence.sha256                  # DR-7: bundle integrity hash
    └── profile-contract.json            # Reference to #185 profile architecture
```

---

## 10. Relationship to Existing Capabilities

| Existing | #187 Relationship |
|----------|-------------------|
| #186 PRIV-THIRD-PARTY | Privacy identifies that a dependency exists. #187 evaluates the risk that dependency creates. |
| #183 Security Capability | #187 produces dependency evidence that #188 Security can consume for vulnerability correlation. |
| QA Pilot Evidence Checklist | #187 findings can populate checklist items as evidence sources. |
| Sprint ledger | #187 runs are version-tracked against the sprint state at time of execution. |
