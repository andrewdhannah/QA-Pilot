# QA-PILOT-SECURITY-COMPLIANCE-CAPABILITY-ARCHITECTURE-1 — Evidence

**Produced by:** #183
**Date:** 2026-07-20
**Status:** Architecture document — defines Security, Privacy & Compliance capability

---

## 1. Security Input Contract

### Consumable Sources

| Source | What QA Pilot Reads |
|--------|-------------------|
| Application structure | File inventory, routes, endpoints, UI surfaces |
| Dependency inventory | Bundled libraries, script tags, package.json |
| Configuration surfaces | settings files, env vars, inline config |
| Authentication/authorization flows | Login forms, session stores, role definitions |
| Data flows | Form submissions, data exports, storage patterns |
| Librarian Context | Sprint intent, known risks, evidence history, ownership, change provenance |

### What QA Pilot Does Not Consume

- Production credentials
- Live API keys
- Customer data
- Private keys

---

## 2. Compliance Profile Model

### Design

```
compliance_profile:
  name: string
  frameworks:
    - reference: string (e.g. "GDPR")
      controls:
        - id: string
          description: string
          validation_type: enum(dependency, config, static_analysis, evidence_review)

profiles_supported:
  - EU_SECURITY_PRIVACY_BASELINE (GDPR, NIS2, EU_Cybersecurity_Act, OWASP_ASVS)
  - SOC2
  - PIPEDA
  - ISO27001
  - QE_25
```

**Key rule:** QA Pilot validates controls and produces evidence. QA Pilot does not decide compliance. The profile model is additive — new frameworks can be added as profile packs without changing the capability core.

---

## 3. Finding Artifact Model

### Schema Extension

```
finding:
  identity:            UUID
  domain:              enum(security, privacy, compliance)
  framework:           string (e.g. "GDPR", "SOC2")
  control_reference:   string (e.g. "GDPR-17", "SOC2-CC6")
  affected_surface:    string (file, route, config, component)
  evidence:            string (what was observed)
  classification:
    - PASS
    - OBSERVATION
    - GAP
    - OWNER_DECISION_REQUIRED
  confidence:          enum(high, medium, low)
  recommended_owner_action: string (informational only)
```

### Boundary Rules

| QA Pilot Says | QA Pilot Does Not Say |
|--------------|----------------------|
| "Control evidence not found" | "Organization is non-compliant" |
| "This pattern matches known vulnerability" | "This must be fixed immediately" |
| "GDPR Article 17: deletion workflow not detected" | "Company is GDPR non-compliant" |
| "Dependency X has known CVE" | "Deploy this now" |

---

## 4. Execution Model

### Security-Specific Stages

```
Generate     ──  Profile selection, control mapping
Validate     ──  Schema compliance, control applicability
Execute      ──  Dependency scan, config review, auth inspection,
                 secret exposure check, pattern detection
Capture      ──  Finding with evidence + context
Classify     ──  PASS / OBSERVATION / GAP / OWNER_DECISION_REQUIRED
Output       ──  Evidence package + control coverage matrix
```

### Security Validation Types (Layers 1-3)

| Layer | Type | Method |
|-------|------|--------|
| 1 | Dependency analysis | Static file scan |
| 1 | Secrets exposure | Pattern matching |
| 1 | Insecure configuration | Config file review |
| 1 | Auth flow inspection | Form + session analysis |
| 2 | Personal data inventory | Form field + data model scan |
| 2 | Consent mechanisms | UI toggle detection |
| 2 | Data export/deletion | Workflow analysis |
| 3 | Access control evidence | Role/perm configuration |
| 3 | Change traceability | Git history + evidence chain |
| 3 | Audit trail | Logging pattern detection |

---

## 5. Librarian Boundary

| QA Pilot (Validation) | Librarian (Governance) | Owner (Decision) |
|----------------------|----------------------|-----------------|
| Detects | Evaluates context | Accepts risk |
| Measures | Tracks decision history | Authorizes remediation |
| Records evidence | Maintains accountability chain | Decides priority |
| Classifies findings | Maps to requirements | |

---

## 6. Capability Roadmap

| Phase | Sprint | Scope |
|-------|--------|-------|
| 4A | #183 (this) | Security, Privacy & Compliance capability architecture |
| 4B | Next | Security validation implementation (Layer 1: deps, config, secrets, auth) |
| 4C | Next+1 | Compliance profile framework (profile engine + control mapping) |
| 4D | Next+2+ | Framework packs: GDPR, SOC2, PIPEDA, QE-25, ISO27001 |

---

## Acceptance Gates

| Gate | Result |
|------|--------|
| SEC-ARCH-1 | PASS — Security input contract defined (6 sources, 5 non-sources) |
| SEC-ARCH-2 | PASS — Compliance profile model defined with profile design + 5 supported profiles |
| SEC-ARCH-3 | PASS — Finding artifact schema defined (domain/framework/control/classification/confidence) |
| SEC-ARCH-4 | PASS — Execution model defined with 3 validation layers (technical, privacy, governance) |
| SEC-ARCH-5 | PASS — Librarian boundary preserved (detect/classify/report only) |
| SEC-ARCH-6 | PASS — Implementation roadmap produced (4A→4B→4C→4D) |
| SEC-ARCH-7 | PASS — Evidence artifact produced (this document) |

**7 PASS, 0 FAIL**

---

**Classification:** Advisory architecture definition — does not authorize implementation.
