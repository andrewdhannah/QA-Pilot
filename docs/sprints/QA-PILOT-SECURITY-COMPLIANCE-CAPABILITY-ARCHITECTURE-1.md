# QA-PILOT-SECURITY-COMPLIANCE-CAPABILITY-ARCHITECTURE-1 — Security, Privacy & Compliance Capability Architecture

**Type:** assessment / architecture definition
**Status:** ✅ **AUTHORIZED — Owner-authorized 2026-07-20**
**Lane:** architecture
**Boundary:** QA Pilot-local, Librarian advisory boundary
**Dependencies:** #182 sealed, Phase 3 Review complete

---

## Purpose

Define a standards-aware security, privacy, and compliance validation capability. QA Pilot should be able to assess application posture against applicable obligations (GDPR, SOC2, PIPEDA, QE-25, ISO27001, NIS2, etc.) using a profile-based model — not hard-coded regulations.

**Key insight:** This is the first capability where the Librarian context (provenance, decisions, evidence history, ownership) becomes a primary advantage. Compliance validation requires intent + structure, not just code scanning.

---

## Scope

### Included

| # | Area | Action |
|---|------|--------|
| 1 | Security Input Contract | Application structure, dependency inventory, configuration, auth flows, Librarian context |
| 2 | Compliance Profile Model | Profile-based framework selection (GDPR, SOC2, PIPEDA, QE-25, ISO27001, NIS2, etc.) |
| 3 | Finding Artifact Model | Extended schema: domain (security/privacy/compliance), framework, control reference, classification |
| 4 | Execution Model | 6-stage lifecycle + security-specific additions (dependency checks, config review, auth inspection, secret exposure, pattern detection) |
| 5 | Librarian Boundary | QA Pilot detects/classifies/reports → Librarian/Owner assess risk/accept/authorize |
| 6 | Capability Roadmap | Phase 4A architecture → 4B security validation → 4C compliance framework → 4D framework packs |

### Standards Coverage Model

```
compliance_profile:
  name: EU_SECURITY_PRIVACY_BASELINE
  frameworks:
    - GDPR
    - NIS2
    - EU_Cybersecurity_Act
    - OWASP_ASVS

additional_profiles:
    - SOC2
    - PIPEDA
    - ISO27001
    - QE_25
```

**Design principle:** Profiles determine applicable controls. QA Pilot does not decide compliance — it produces evidence against controls.

### Security Capability Layers

| Layer | Domain | Example Checks |
|-------|--------|---------------|
| Layer 1 | Technical Security | Dependency analysis, secrets, config, auth flows, input validation |
| Layer 2 | Privacy | Personal data inventory, collection purpose, consent, data export/deletion |
| Layer 3 | Governance Controls | Access control evidence, change traceability, audit trails, incident response |

### Explicit Non-Scope

- Penetration testing execution
- Vulnerability remediation automation
- Security approval authority
- Compliance certification
- Risk acceptance decisions
- Credential storage or transmission

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| SEC-ARCH-1 | Security input contract defined |
| SEC-ARCH-2 | Compliance profile model defined |
| SEC-ARCH-3 | Finding artifact schema defined (domain + framework + control reference) |
| SEC-ARCH-4 | Execution model defined with security-specific stages |
| SEC-ARCH-5 | Librarian boundary preserved (detect/classify/report only) |
| SEC-ARCH-6 | Implementation roadmap produced |
| SEC-ARCH-7 | Evidence artifact produced |

---

**Status:** ✅ AUTHORIZED — Owner-authorized 2026-07-20
**Ledger entry:** #183 (authorized)
