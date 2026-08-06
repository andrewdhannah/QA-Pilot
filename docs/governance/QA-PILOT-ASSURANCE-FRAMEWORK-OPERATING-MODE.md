# QA Pilot Assurance Framework — Operating Mode Declaration

**Purpose:** Freeze the assurance framework architecture after completion of the Release Readiness Profile. Define evidence ownership, profile extension rules, capability addition criteria, and the boundary between framework maintenance and new development.

**Status:** EFFECTIVE — supersedes all informal framework extension patterns.

---

## 1. Framework Architecture (Frozen)

The following architecture is frozen as of 2026-07-20. No modification to the layered structure without an Owner-authorized amendment.

```
Discovery Phase
       ↓
Assessment Profiles (#185)
       ↓
Individual Capabilities (#179–#188)
       ↓
Evidence Classification (PASS / OBSERVATION / OWNER_DECISION_REQUIRED)
       ↓
Release Readiness Profile (aggregation — composition only)
       ↓
Owner Review
       ↓
Release Decision (Owner-owned — not automated)
```

### Frozen Components

| Component | Classification | Amendment Required? |
|-----------|---------------|-------------------|
| Layer sequence (Discovery → Assessment → Capabilities → Classification → Aggregation → Owner → Decision) | Structural | Yes — Owner-authoriZed amendment |
| #185 assurance_report schema | Contract | Yes — Owner-authoriZed amendment |
| PASS / OBSERVATION / OWNER_DECISION_REQUIRED taxonomy | Contract | Yes — Owner-authoriZed amendment |
| Release Readiness as composition-only (no decision authority) | Invariant | Yes — requires full invariant review |
| evidence_references / provenance chain | Contract | Yes — Owner-authoriZed amendment |

### Non-Frozen (Maintenance Permitted)

- Script optimizations (performance, error handling) that do not change output schema
- Evidence file path updates (if capability script changes output location)
- Timestamp format improvements
- Bug fixes in evidence loading or classification extraction

---

## 2. Evidence Ownership

| Evidence | Producer | Owner | Update Authority |
|----------|----------|-------|-----------------|
| `data/regression-evidence.json` | #179 Regression | QA Pilot capability | Capability manager |
| `data/uat-evidence.json` | #180 UAT | QA Pilot capability | Capability manager |
| `data/accessibility-evidence.json` | #181 Accessibility | QA Pilot capability | Capability manager |
| `data/performance-baseline.json` | #182 Performance | QA Pilot capability | Capability manager |
| `data/privacy-assurance-evidence.json` | #186 Privacy | QA Pilot assurance profile | Profile owner |
| `data/dependency-risk-evidence.json` | #187 Dependency Risk | QA Pilot assurance profile | Profile owner |
| `data/dependency-risk-profile-contract.json` | #187 | QA Pilot assurance profile | Profile owner |
| `data/security-assurance-evidence.json` | #188 Security | QA Pilot assurance profile | Profile owner |
| `data/security-assurance-profile-contract.json` | #188 | QA Pilot assurance profile | Profile owner |
| `data/release-readiness-evidence.json` | Release Readiness | QA Pilot composition | Composition owner |

### Evidence Update Rules

1. Each evidence file is produced exclusively by its owning capability script
2. No script writes to evidence files it does not own
3. The Release Readiness Profile reads evidence files — it never writes to input files
4. Evidence files are JSON — no format migration without Owner authorization

---

## 3. Profile Extension Rules

### Adding a New Control to an Existing Profile

Permitted if:
- The control fits within the existing profile's scope (standards, input sources)
- The control uses the existing classification taxonomy
- The control does not introduce new authority
- The control does not require input from outside the profile's existing capability dependencies

**Authority:** QA Pilot capability owner. Notify via sprint ledger entry.

### Adding a New Profile (e.g., #189, SOC2 Compliance Profile)

Requires:
1. Planning definition (scope, input sources, non-goals, acceptance gates)
2. Invariant review (authority boundary, classification preservation, no certification claims)
3. Owner authorization
4. Implementation within authorized scope
5. Release Readiness Profile updated to include the new input
6. Framework amendment recorded in this document

**Authority:** Owner authorization required.

### Adding a New Capability (e.g., new scanner, new evidence type)

Requires:
1. Dependency analysis (which profiles would consume this capability?)
2. Planning definition
3. Invariant review
4. Owner authorization
5. All consuming profiles updated

**Authority:** Owner authorization required.

---

## 4. Capability Addition Criteria

New capabilities should be evaluated against:

| Criteria | Required? | Notes |
|----------|-----------|-------|
| Addresses a gap in the existing evidence chain | Yes | If existing capabilities already cover this area, surface the gap as a profile improvement, not a new capability |
| Has at least one consuming profile | Yes | Standalone capabilities with no downstream consumer should be proposed, not implemented |
| Preserves the classification taxonomy | Yes | No new classification levels |
| Preserves the authority boundary | Yes | Evidence generation only — no decision authority |
| Has defined acceptance gates | Yes | Minimum 5 gates including provenance, classification, and authority boundary |
| Evidence output conforms to #185 | Yes | Must produce `assurance_report` format if consumed by Release Readiness |
| No compliance certification | Yes | QA Pilot produces evidence — not certification |

### Discouraged Patterns

- **Capability for capability's sake** — adding a capability because it's expected (e.g., "every QA framework has a performance capability") without a clear evidence gap
- **Profile without consumer** — creating a profile that nothing consumes
- **Cross-system expansion** — extending QA Pilot into Librarian territory without a cross-system proposal
- **Certification creep** — profiles producing compliance claims rather than evidence

---

## 5. Maintenance vs. New Development Boundary

| Activity | Classification | Authority |
|----------|---------------|-----------|
| Bug fix in evidence loading | Maintenance | Capability owner |
| Performance optimization of existing script | Maintenance | Capability owner |
| Update evidence file path | Maintenance | Capability owner |
| Improve error message clarity | Maintenance | Capability owner |
| Add new classification taxonomy value | **New development** | Owner authorization |
| Add new control to existing profile | **New development** | Owner authorization |
| Add new profile | **New development** | Owner authorization + invariant review |
| Add new capability | **New development** | Owner authorization + invariant review |
| Add new evidence output format | **New development** | Owner authorization |
| Modify Release Readiness aggregation logic | **New development** | Owner authorization + invariant review |
| Cross-system integration (QA Pilot → Librarian) | **New development** | Separate cross-system proposal |

---

## 6. Current Capability Registry

| # | Capability | Type | Evidence | Status |
|---|-----------|------|----------|--------|
| #179 | Regression | Test capability | `regression-evidence.json` | ✅ Sealed |
| #180 | UAT | Test capability | `uat-evidence.json` | ✅ Sealed |
| #181 | Accessibility | Test capability | `accessibility-evidence.json` | ✅ Sealed |
| #182 | Performance | Test capability | `performance-baseline.json` | ✅ Sealed |
| #183 | Security Capability | Capability (existing) | `security-compliance-evidence.json` | ✅ Existing |
| #185 | Assurance Profile Architecture | Architecture | (definition only) | ✅ Sealed |
| #186 | Privacy Assurance | Assurance profile | `privacy-assurance-evidence.json` | ✅ Sealed |
| #187 | Dependency Risk | Assurance profile | `dependency-risk-evidence.json` | ✅ Sealed |
| #188 | Security Assurance | Assurance profile | `security-assurance-evidence.json` | ✅ Sealed |
| — | Release Readiness Profile | Composition layer | `release-readiness-evidence.json` | ✅ Sealed |

### Capability Dependency Graph

```
#185 (architecture)
 ├── #186 (privacy) — consumes #183
 ├── #187 (dependency) — standalone
 ├── #188 (security) — consumes #186, #187
 ├── #179 (regression)
 ├── #180 (UAT)
 ├── #181 (accessibility)
 ├── #182 (performance)
 │
 └── Release Readiness Profile — consumes all #179–#188
```

---

## 7. Profile-to-Capability Mapping

| Profile | Capabilities Consumed | Standards |
|---------|----------------------|-----------|
| #186 Privacy Assurance | #183, #179, #180, #181, #182 (via artifact ingestion) | GDPR, PIPEDA, Apple Privacy |
| #187 Dependency Risk | (standalone — static analysis) | DEPENDENCY-RISK-FRAMEWORK-1 |
| #188 Security Assurance | #186, #187, #183 (direct scan) | SOC2 Security, OWASP |
| Release Readiness | #179, #180, #181, #182, #186, #187, #188 | (aggregation — no standards) |

---

## 8. Known Framework Limitations

| Limitation | Impact | Recommended Action |
|-----------|--------|-------------------|
| #179–#182 use legacy evidence format (no #185 assurance_report) | Cannot extract structured PASS/OBSERVATION status — derived as OBSERVATION by proxy | Consider migrating to #185 format if deeper integration is needed |
| #183 Security Capability exists but is not a formal #185 profile | Not consumed by current profiles | Could be converted to a #185 profile if security assurance needs expansion |
| No formal regression test for framework outputs | Evidence format changes may silently break the Release Readiness Profile | Add a structural validation gate for each capability script |
| Evidence timestamps are not standardized across all capabilities | Freshness classification may be approximate for older-format capabilities | Standardization deferred — no current requirement |

---

## 9. Governance Rules

1. **No profile may assert compliance** — all profiles have `authority_level: advisory`
2. **No capability may create a new classification level** — PASS / OBSERVATION / OWNER_DECISION_REQUIRED is frozen
3. **No script may write to evidence files it does not own** — the Release Readiness script reads only
4. **No profile may make release decisions** — the release decision is Owner-owned
5. **No capability may auto-remediate** — findings are evidence, not actions
6. **No evidence gap may be silently assumed PASS** — missing evidence must be reported as MISSING
7. **All new profiles require an invariant review** before Owner authorization
8. **The Release Readiness Profile is the sole composition layer** — no other aggregation surface should be created without Owner authorization and an amendment to this document

---

## 10. Amendment Process

Amendments to this operating mode require:
1. A written proposal describing the change and its rationale
2. Impact analysis on frozen components, evidence ownership, and profile extension rules
3. Invariant review (if authority boundary or classification taxonomy is affected)
4. Owner authorization
5. Update to this document with amendment recorded

---

*Document: QA-PILOT-ASSURANCE-FRAMEWORK-OPERATING-MODE.md*
*Status: EFFECTIVE | Frozen: 2026-07-20*
*Authority: Advisory — all profiles produce evidence, not decisions*
