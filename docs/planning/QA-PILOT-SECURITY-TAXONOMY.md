# QA Pilot Security Qualification Taxonomy

**Sprint:** QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1
**Status:** Planning — test category definitions for the security qualification domain
**Relationship:** Sub-domain of the Qualification Architecture defined in `QA-PILOT-QUALIFICATION-ARCHITECTURE.md`

---

## 0. Authority Notice

This taxonomy defines test categories for the security qualification domain. It does not define implementation. No security tools, scanners, or runtimes are specified. The taxonomy exists so that test generators, component evidence contracts, and coverage analysis have a bounded vocabulary.

---

## 1. Security Domain Scope

Security is one qualification domain within the QA Pilot qualification framework. It covers the evaluation of project components against security requirements derived from:

- Component classification (authority boundary, evidence store, public interface, etc.)
- Implementation location (files, symbols, routes, database tables)
- Authority model (owner_only, agent, public, system)
- Existing evidence and receipt patterns

### 1.1 Test Class Distribution

| Test Class | Coverage in Security Domain | Generation Model |
|-----------|----------------------------|------------------|
| Structural | Interface existence, auth middleware presence, route registration | Automatic — enumerable from component metadata |
| Behavioral | Schema validation, state transitions, error handling | Derived from contracts, schemas, API descriptions |
| Adversarial | Privilege escalation, forgery, injection, bypass | Derived from component classification + template suite |
| Domain | Custom organizational security policies, bespoke crypto logic | Human-authored; tracked by coverage analysis |

---

## 2. Security Test Categories

### 2.1 Application Security

Tests the security of the running application, its interfaces, and its data handling.

| Category | Test Class | Generation Input | Example Test IDs |
|----------|-----------|-----------------|------------------|
| Authentication | structural, adversarial | Component with `authentication` interface tag | AUTH-EXIST-001, AUTH-BYPASS-001, AUTH-FORGERY-001 |
| Authorization | structural, adversarial | Component with `authority_boundary` classification | AUTHZ-ACCESS-001, AUTHZ-ESCALATION-001, AUTHZ-DENY-001 |
| Session Handling | behavioral, adversarial | Component with session management interfaces | SESS-TIMEOUT-001, SESS-REPLAY-001, SESS-HIJACK-001 |
| Input Validation | structural, behavioral | Route with defined input schema | VAL-INJECTION-001, VAL-MALFORMED-001, VAL-BOUNDARY-001 |
| Injection Resistance | adversarial | Component classified as `execution_context` | INJ-SQL-001, INJ-CMD-001, INJ-LDAP-001 |
| API Security | structural, behavioral, adversarial | Registered API routes with authority model | API-RATE-001, API-AUTH-001, API-METHOD-001, API-IDOR-001 |

#### 2.1.1 Generation Rules — Authorization Category

**Input:**
```
Component: Owner Queue
Classification: authority_boundary
Interfaces:
  - POST /api/owner/action (owner_only)
  - GET /api/owner/pending (owner_only)
```

**Generated Tests (structural):**
| ID | Test | Expected |
|----|------|----------|
| AUTHZ-ACCESS-001 | Unauthenticated request to POST /api/owner/action returns 401 | 401 |
| AUTHZ-ACCESS-002 | Non-owner authenticated request to POST /api/owner/action returns 403 | 403 |
| AUTHZ-ACCESS-003 | Owner request to POST /api/owner/action returns 200 | 200 |

**Generated Tests (adversarial):**
| ID | Test | Expected |
|----|------|----------|
| AUTHZ-ESCALATION-001 | Standard user crafts request with owner-level claims | 403 |
| AUTHZ-ESCALATION-002 | Request with modified authority token to access owner endpoint | 403 |
| AUTHZ-FORGERY-001 | Receipt forgery attempt on owner action endpoint | 403 or 400 |

### 2.2 Dependency Security

Tests the security posture of external dependencies.

| Category | Test Class | Generation Input | Example Test IDs |
|----------|-----------|-----------------|------------------|
| Dependency Inventory | structural | Project manifest (Package.swift, requirements.txt, etc.) | DEP-INV-001 |
| Vulnerability Scanning | behavioral | Inventory + advisory database reference | DEP-CVE-001, DEP-CRITICAL-001 |
| Version Drift | structural | Declared version vs. resolved version | DEP-DRIFT-001, DEP-PIN-001 |
| License Risk | structural | Dependency license declarations | DEP-LICENSE-001, DEP-COPYLEFT-001 |
| Supply Chain | adversarial | Build pipeline configuration | DEP-SUPPLY-BUILD-001, DEP-SUPPLY-ARTIFACT-001 |

#### 2.2.1 Generation Rules — Dependency Inventory

**Input:**
```
Component: Librarian Server
Manifest: Package.swift
Dependencies:
  - swift-argument-parser (1.2.0)
  - swift-crypto (2.0.0)
  - sqlite-vapor (3.1.0)
```

**Generated Tests:**
| ID | Test | Expected |
|----|------|----------|
| DEP-INV-001 | All declared dependencies have resolved versions | PASS |
| DEP-DRIFT-001 | Resolved version matches declared constraint | PASS |
| DEP-LICENSE-001 | All dependency licenses are in allowed list | PASS |

### 2.3 Supply Chain Security

Tests the integrity of the build and release pipeline.

| Category | Test Class | Generation Input | Example Test IDs |
|----------|-----------|-----------------|------------------|
| SBOM Generation | structural | Build system + package manifest | SC-SBOM-001, SC-SBOM-COMPLETE-001 |
| Build Provenance | behavioral | CI/CD configuration | SC-BUILD-REPRO-001, SC-BUILD-SIGN-001 |
| Artifact Integrity | behavioral | Release artifact hashes | SC-ARTIFACT-HASH-001, SC-ARTIFACT-TAMPER-001 |
| Release Signing | structural | Release pipeline | SC-SIGN-001, SC-SIGN-VERIFY-001 |

### 2.4 Runtime Security

Tests the security posture of the deployed runtime environment.

| Category | Test Class | Generation Input | Example Test IDs |
|----------|-----------|-----------------|------------------|
| Configuration Validation | structural | Runtime configuration schema | RUNTIME-CONFIG-001, RUNTIME-SECRETS-001 |
| Exposed Services | structural, adversarial | Network interface declarations | RUNTIME-EXPOSE-001, RUNTIME-EXPOSE-ATTACK-001 |
| Permissions | structural, adversarial | Filesystem and capability declarations | RUNTIME-PERM-001, RUNTIME-PERM-ESCALATION-001 |
| Secrets Handling | structural, adversarial | Configuration + code references | RUNTIME-SECRET-HARDCODE-001, RUNTIME-SECRET-ENV-001 |

### 2.5 AI Governance Security (Librarian-Specific)

Tests the security of AI governance boundaries — unique to the Librarian platform.

| Category | Test Class | Generation Input | Example Test IDs |
|----------|-----------|-----------------|------------------|
| Authority Escalation | adversarial | Node with `authority_boundary` classification | AI-AUTH-ESCALATION-001, AI-AUTH-BYPASS-001 |
| Identity Spoofing | adversarial | Identity verification interfaces | AI-ID-SPOOF-001, AI-ID-FORGERY-001 |
| Receipt Forgery | adversarial | Evidence receipt system | AI-RCPT-FORGERY-001, AI-RCPT-TAMPER-001 |
| Registry Manipulation | adversarial | Node Registry interfaces | AI-REG-MODIFY-001, AI-REG-INJECT-001 |
| Prompt Injection | adversarial | AI-facing interfaces | AI-PROMPT-INJECT-001, AI-PROMPT-LEAK-001 |
| Agent Isolation | adversarial | Agent execution context | AI-AGENT-ESCAPE-001, AI-AGENT-PERM-001 |
| Authority Bypass | adversarial | Owner decision interfaces | AI-AUTHORITY-BYPASS-001, AI-SEAL-BYPASS-001 |

#### 2.5.1 Generation Rules — Authority Escalation

**Input:**
```
Component: Authority Enforcer
Classification: authority_boundary
Node Role: governance_enforcer
Interfaces:
  - POST /api/authority/check (system)
  - POST /api/authority/escalate (owner_only)
```

**Generated Tests:**
| ID | Test | Expected |
|----|------|----------|
| AI-AUTH-ESCALATION-001 | Agent request to self-escalate authority level returns 403 | 403 |
| AI-AUTH-ESCALATION-002 | Forged escalation request with modified authority token | 403 |
| AI-AUTH-BYPASS-001 | Direct API call bypassing authority check middleware | 403 |
| AI-AUTH-BYPASS-002 | Request to authority endpoint with missing evidence hash | 400 or 403 |

---

## 3. Category-to-Classification Mapping

These are the component classification tags that determine which security test categories apply.

| Component Classification | Security Categories Triggered |
|-------------------------|------------------------------|
| `authority_boundary` | Authorization, Authentication, AI Governance (all), API Security, Input Validation |
| `evidence_store` | Receipt Forgery, Integrity, Configuration Validation |
| `public_interface` | API Security, Authentication, Input Validation, Rate Limiting, Injection Resistance |
| `execution_context` | Agent Isolation, Injection Resistance, Permissions, Configuration Validation |
| `identity_provider` | Authentication, Identity Spoofing, Session Handling |
| `data_store` | Configuration Validation, Secrets Handling, Dependency Security |
| `registry` | Registry Manipulation, Authorization, Receipt Integrity |
| `build_pipeline` | Supply Chain, SBOM, Artifact Integrity, Build Provenance |
| `runtime_node` | Runtime Security (all), Configuration, Secrets, Exposed Services |
| `ai_interface` | Prompt Injection, Agent Isolation, Authority Escalation |

---

## 4. Template Reference

Each security test category maps to a generation template. Templates are parameterized by component metadata.

### 4.1 Template Structure

```json
{
  "template_id": "SEC-AUTHORIZATION-ACCESS",
  "category": "authorization",
  "test_class": "structural",
  "classification_required": ["authority_boundary"],
  "inputs_required": ["interfaces", "authority_model"],
  "generates": [
    {
      "base_id": "AUTHZ-ACCESS",
      "per_input": "route",
      "tests": [
        {
          "name": "Unauthenticated request returns 401",
          "method": "{route.method}",
          "path": "{route.path}",
          "auth": "none",
          "expected_status": 401
        },
        {
          "name": "Non-owner request returns 403",
          "method": "{route.method}",
          "path": "{route.path}",
          "auth": "non_owner",
          "expected_status": 403
        }
      ]
    }
  ]
}
```

---

## 5. Coverage Rules by Classification

Each component classification has a minimum coverage expectation.

| Classification | Required Categories | Minimum Pass Rate | Coverage Level |
|---------------|-------------------|-------------------|----------------|
| `authority_boundary` | authorization, authentication, ai_governance | 100% | required |
| `evidence_store` | receipt_integrity, configuration | 100% | required |
| `public_interface` | api_security, authentication, input_validation | 100% | required |
| `execution_context` | agent_isolation, permissions, injection | 100% | required |
| `identity_provider` | authentication, identity, session | 100% | required |
| `data_store` | secrets, configuration, dependency | 90% | required |
| `registry` | registry_integrity, authorization | 100% | required |
| `build_pipeline` | supply_chain, sbom, signing | 100% | required |
| `runtime_node` | runtime_security (all) | 90% | advisory |
| `ai_interface` | prompt_injection, agent_isolation | 100% | required |
| `documentation` | (none) | n/a | optional |
| `ui_component` | (none structural) | n/a | optional |

---

## 6. Non-Goals

The following are explicitly out of scope for the security taxonomy:

- ❌ Specification of specific security tools (SAST/DAST/SCA vendors)
- ❌ Runtime scanner configuration or integration
- ❌ Network penetration testing methodology
- ❌ Compliance framework mapping (SOC2, ISO 27001, etc.)
- ❌ Organizational security policy definition
- ❌ Bug bounty program design
- ❌ Incident response planning

These are separate concerns that may be addressed by domain tests but are not part of the generated qualification taxonomy.

---

## 7. Relationship to Release Gates

Security qualification feeds into release gates via the qualification profile:

```json
{
  "node_id": "NODE-LIBRARIAN-CORE",
  "qualification_profile": {
    "security": { "level": "required" },
    "release_gate": {
      "required_domains": ["functional", "security"],
      "security_requirements": {
        "min_pass_rate": 1.0,
        "blocking_categories": [
          "authorization",
          "authentication",
          "receipt_integrity",
          "ai_governance"
        ],
        "advisory_categories": [
          "dependency",
          "supply_chain"
        ]
      }
    }
  }
}
```

A release gate configured with `blocking_categories` prevents qualification from passing if any test in those categories fails. `advisory_categories` surface warnings but do not block.

---

*Security taxonomy for QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1. Planning only. No implementation authority conferred.*
