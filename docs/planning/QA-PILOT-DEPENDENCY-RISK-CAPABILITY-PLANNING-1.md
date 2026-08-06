# QA Pilot Dependency Risk Capability — Planning Definition

**Document:** #187 Planning Definition  
**Status:** ✅ **SEALED — Planning defined, implementation complete, all 8 gates pass**  
**Preceding capability:** #186 Privacy Assurance Profile (✅ sealed)  
**Architecture basis:** #185 Assurance Profile Architecture (✅ sealed)  
**Next capability:** #188 Security Assurance Profile (⏳ proposed)

---

## 1. Purpose

Create a governed capability that inventories software dependencies and produces risk observations without becoming a remediation engine.

This fills the missing evidence layer exposed by #186:

```
Application
    ├── Input/data surface       ← #186 (privacy)
    ├── Browser storage          ← #186 (privacy)
    ├── External services        ← #186 (privacy)
    └── Dependencies             ← #187 (dependency risk) — MISSING LAYER
```

Privacy can identify that a dependency exists. It cannot adequately evaluate the technical risk created by that dependency. #187 fills that gap.

---

## 2. Core Invariant

```
Risk Finding
        ≠
Vulnerability Decision
        ≠
Remediation Authorization
        ≠
Change Execution
```

The capability produces evidence-based risk observations. It does not:
- Upgrade packages
- Modify source
- Replace dependencies
- Create security certifications
- Declare vulnerabilities resolved
- Approve releases

---

## 3. Architecture — Profile Pattern (per #185)

```
Standard / Framework
        ↓
Assurance Profile (with controls)
        ↓
Evidence Collection (dependency inventory)
        ↓
Findings Classification
        ↓
Owner Decision Boundary
```

#187 implements this pattern for the **dependency risk** domain:

### Profile Contract

```json
{
  "profile": "DEPENDENCY-RISK-1",
  "controls": [
    {
      "id": "DR-INVENTORY",
      "capabilities": ["dependency_risk"],
      "evidence_required": ["implementation"],
      "finding_classification_default": "OBSERVATION",
      "escalation_rule": "OWNER_DECISION_REQUIRED (if unversioned or abandoned)"
    },
    {
      "id": "DR-VERSION",
      "capabilities": ["dependency_risk"],
      "evidence_required": ["implementation"],
      "finding_classification_default": "OBSERVATION",
      "escalation_rule": "OWNER_DECISION_REQUIRED (if beyond supported lifecycle)"
    },
    {
      "id": "DR-RISK",
      "capabilities": ["dependency_risk"],
      "evidence_required": ["implementation", "documentation"],
      "finding_classification_default": "OBSERVATION",
      "escalation_rule": "OWNER_DECISION_REQUIRED (if dependency is abandoned or unsupported)"
    }
  ],
  "authority_level": "advisory"
}
```

### Evidence Expectation Model

| Evidence Type | Definition | QA Pilot Action |
|--------------|------------|----------------|
| **inventory** | Inventory of all dependencies (name, version, source, type) | Static analysis — scan source for imports, CDN references, service endpoints |
| **version_analysis** | Version metadata per dependency | Extract version from path, header, or metadata |
| **risk_classification** | Risk observation per dependency | Apply finding taxonomy to version/dependency metadata |

### Finding Taxonomy

| Capability Finding | Profile Finding | When |
|-------------------|----------------|------|
| PASS | PASS | Dependency is versioned, supported, and within lifecycle |
| OBSERVATION | OBSERVATION | Dependency is unversioned but local (pinned to path) |
| OWNER_DECISION_REQUIRED | OWNER_DECISION_REQUIRED | Dependency is beyond lifecycle, abandoned, or externally sourced without provenance |

---

## 4. Scope

### Included

| # | Area | Action |
|---|------|--------|
| 1 | Dependency inventory | Discover all external dependencies (scripts, CDNs, libraries, packages, services) |
| 2 | Version analysis | Extract version information where available |
| 3 | Dependency graph | Direct/transitive classification |
| 4 | Risk identification | Outdated/pinned/unversioned/abandoned dependencies flagged |
| 5 | Evidence classification | Findings classified as PASS / OBSERVATION / OWNER_DECISION_REQUIRED |
| 6 | Evidence output | Machine-readable Dependency Evidence Record |
| 7 | Profile linkage | Output conforms to #185 assurance profile contract schema |

### Explicit Non-Scope

- Automatic upgrades
- Vulnerability remediation
- Package replacement
- CVE database integration (future — requires separate capability)
- Security certification
- Vulnerability declaration
- Release approval
- Compliance certification
- Legal risk acceptance

---

## 5. Evidence Model — Dependency Evidence Record

### Schema

```json
{
  "evidence_id": "DEP-RISK-{date}-{seq}",
  "profile": "DEPENDENCY-RISK-1",
  "generated_at": "ISO8601",
  "overall": "OBSERVATION | OWNER_DECISION_REQUIRED | PASS",
  
  "inventory": {
    "total_dependencies": 127,
    "local_libraries": 127,
    "cdn_dependencies": 0,
    "external_services": 0,
    "dependency_graph": [
      {
        "name": "js/app.js",
        "type": "local_library",
        "version": "unversioned",
        "classification": "direct",
        "sources": ["browser-app/index.html", "browser-app/capstone.html"]
      }
    ]
  },
  
  "version_analysis": [
    {
      "dependency": "js/db.js",
      "version": "unversioned",
      "risk": "OBSERVATION",
      "finding": "Unversioned dependency (pinned to path, no version tracking)"
    }
  ],
  
  "risk_findings": [
    {
      "finding_id": "DR-{seq}",
      "dependency": "js/db.js",
      "finding": "Version is tracked only by file path — no version metadata available",
      "classification": "OBSERVATION"
    }
  ],
  
  "controls": {
    "DR-INVENTORY": "OBSERVATION",
    "DR-VERSION": "OBSERVATION",
    "DR-RISK": "OBSERVATION"
  },
  
  "authority_level": "advisory",
  "owner_action_required": false
}
```

### Evidence Output Rules

- All findings include: dependency name, version or version status, risk classification, finding description
- `overall` is the highest severity across all control findings
- `owner_action_required: true` when any control is OWNER_DECISION_REQUIRED
- Evidence is advisory — QA Pilot does not assert vulnerability status
- Evidence does not contain authentication tokens, credentials, or secrets
- Evidence is append-only — previous evidence is never modified

---

## 6. Finding Classification Rules

| Classification | Definition | Example |
|---------------|------------|---------|
| **PASS** | Dependency is versioned, supported, properly sourced | `lodash@4.17.21` via npm |
| **OBSERVATION** | Dependency is local, unversioned, but functional | `js/db.js` pinned to path |
| **OWNER_DECISION_REQUIRED** | Dependency is beyond lifecycle, abandoned, or externally sourced without provenance | `library-x@1.0.0` — version is beyond supported lifecycle |

### Escalation Rules

- **OBSERVATION** does not escalate — it is informational
- **OWNER_DECISION_REQUIRED** escalates when:
  - Dependency version is beyond documented lifecycle
  - Dependency is known to be abandoned
  - External service has no documented alternative or fallback
  - Dependency is loaded from an untrusted or unverifiable source

---

## 7. Dependency Classification Categories

| Category | Code | Definition | Risk Baseline |
|----------|------|------------|--------------|
| Local library | `local` | Bundled JS/CSS files, project-owned | OBSERVATION (unversioned) |
| CDN dependency | `cdn` | External CDN reference (cdnjs, unpkg, etc.) | OWNER_DECISION_REQUIRED (external, unversioned drift) |
| External service | `service` | API endpoint, third-party service | OWNER_DECISION_REQUIRED (no local control, lifecycle unknown) |
| Package manager | `package` | npm, pip, cargo, etc. managed dependency | PASS/OBSERVATION (versioned, but may drift) |

---

## 8. Acceptance Gates

| Gate | Requirement |
|------|-------------|
| DR-1 | Dependency inventory generated from source scan |
| DR-2 | Dependency evidence has provenance (timestamp, source file, scan method) |
| DR-3 | Version analysis is reproducible (same source → same results) |
| DR-4 | Findings classification is explicit (PASS / OBSERVATION / OWNER_DECISION_REQUIRED) |
| DR-5 | Owner decision boundary preserved — no automated remediation |
| DR-6 | No package changes, source modifications, or dependency upgrades made |
| DR-7 | Evidence retained for audit (as `data/dependency-risk-evidence.json`) |
| DR-8 | Output conforms to #185 assurance profile contract schema |

---

## 9. Integration with #186 and #188

### #186 → #187 Handoff

| #186 Exposed | #187 Fills |
|-------------|-----------|
| Analytics/service inventory (`PRIV-THIRD-PARTY`) | Dependency risk classification for each service |
| Data collection sources (`PRIV-DATA-COLLECTION`) | Version analysis for collection libraries |
| Storage mechanisms (`PRIV-STORAGE`) | Dependency graph for storage libraries |

### #187 → #188 Handoff

| #187 Produces | #188 Consumes |
|--------------|--------------|
| Dependency inventory | Security controls mapping |
| Version risk findings | Vulnerability surface estimation |
| Owner decision findings | Security profile escalation |
| Evidence record | Security assurance evidence input |

### Combined Sequence

```
Privacy Profile (#186)
        +
Dependency Risk (#187)
        +
Existing Security Capability (#183)
        +
Architecture Evidence
        |
        v
Security Assurance Profile (#188)
```

The security profile can then ask better questions:
- What components exist?
- Which dependencies support them?
- What evidence supports their lifecycle?
- What findings require Owner decisions?

---

## 10. Longer-Term Convergence

#187 also contributes to the **Release Readiness Profile**:

```
Accessibility     #181
Performance       #182
Security          #188  (consumes #187)
Privacy           #186  (exposed dependency surface)
Regression        #179
UAT               #180
Dependency Risk   #187
Architecture Evidence
        |
        v
Release Readiness Profile
```

The output chain remains:

```
Evidence → Assessment → Owner Decision
```

not:

```
Evidence → Automatic Release Approval
```

---

## 11. Current Assurance Framework State

| # | Capability | Status |
|---|-----------|--------|
| #185 | Assurance Profile Architecture | ✅ Sealed |
| #186 | Privacy Assurance Profile | ✅ Sealed |
| **#187** | **Dependency Risk Capability** | **⏳ Planning defined — awaiting authorization for implementation** |
| #188 | Security Assurance Profile | ⏳ Proposed |

---

## 12. Next Valid Transition

**Owner authorization to implement #187** using this planning definition as scope.

Implementation must:
- Produce evidence conforming to the Dependency Evidence Record schema
- Conform to #185 assurance profile contract
- Preserve the core invariant (Risk Finding ≠ Vulnerability Decision ≠ Remediation Authorization ≠ Change Execution)
- Leave all packages, source files, and dependencies unchanged

---

*Document: QA-PILOT-DEPENDENCY-RISK-CAPABILITY-PLANNING-1.md*
*Capability: #187 Dependency Risk | Status: Planning Definition Complete*
*Core invariant: Risk Finding ≠ Vulnerability Decision ≠ Remediation Authorization ≠ Change Execution*
