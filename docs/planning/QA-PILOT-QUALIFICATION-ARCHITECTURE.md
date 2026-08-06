# QA Pilot Qualification Architecture

**Sprint:** QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1
**Authorized:** 2026-07-16
**Status:** Planning — not implementation
**Authority Owner:** Librarian (Core)
**Execution Layer:** QA Pilot

---

## 0. Authority Boundary

This document defines the architecture for a governed qualification framework. It is planning-only. No implementation, registry mutation, or seal authority is conferred.

### Ownership Model

```
Librarian (Core)                QA Pilot (Execution)
─────────────────────           ─────────────────────
Canonical project truth         How do we verify it?
What exists?                    Did verification pass?
What is authoritative?          What is the evidence?
Registry authority              Receipt creation
Owner decision surface          Coverage analysis
```

QA Pilot does **not** own qualification truth. It owns the execution, analysis, and evidence creation layer over Librarian-owned truth. This boundary is invariant.

---

## 1. Purpose

Define the architecture by which QA Pilot provides reusable qualification across Librarian-managed projects, using verified project component references to generate, execute, and report qualification tests across multiple domains.

### Why This Exists

The Librarian maintains structured knowledge of:
- Components and their responsibilities
- Ownership and authority boundaries
- Interfaces (APIs, schemas, routes)
- Implementation locations (files, symbols)
- Evidence and receipt lineage
- Runtime node capabilities and classification
- Sprint change history

QA Pilot must consume this knowledge to create qualification tests that are **traceable to actual implementation locations** — not inferred from assumptions.

---

## 2. Data Flow Architecture

```
                 Librarian
                     |
     ---------------------------------
     |               |               |
 Node Registry   Component Model   Evidence
     |               |               |
     ---------------------------------
                     |
         Qualification Targets
        (extend Node Profile)
                     |
                     v

                 QA Pilot
        -------------------------
        Test Generation Engine
        │  structural (enumerable from interfaces)
        │  behavioral (derived from contracts)
        │  adversarial (classification-driven)
        │  domain (human-authored, tracked)
        │
        Test Execution Engine
        Coverage Analysis
        Result Aggregation
        Receipt Creation
        -------------------------
                     |
                     v

             Qualification Receipt
                 (inherits Evidence Receipt)
                     |
                     v

                 Librarian
           Seal / Custody / Evidence Chain
```

### 2.1 Interface Contract

| Direction | Data | Authority |
|-----------|------|-----------|
| Librarian → QA Pilot | Qualification targets, component metadata, evidence references | Pull at qualification time or pushed via event |
| QA Pilot → Librarian | Qualification receipts, coverage reports, gap analysis | Push, sealed as evidence |

### 2.2 Evidentiary Claim Model

Generated qualification tests and their results must never claim:

> "I tested Owner Queue."

They must claim:

> "I tested Owner Queue because Registry Component ID X maps to verified implementation locations at `OwnerQueueService.swift:87`, and the following tests exercised those locations."

This distinction is what gives the system trust. Every result carries its provenance.

---

## 3. Qualification Domain Model

### 3.1 Domain Taxonomy

| Domain | Scope | Test Classes | Coverage Level |
|--------|-------|-------------|-----------------|
| Functional | Unit, integration, E2E, regression | structural, behavioral, domain | required |
| Performance | Benchmarks, latency, throughput, resource usage | behavioral, domain | advisory |
| Operational | Startup, reliability, recovery, health checks | structural, behavioral | required |
| Security | Static analysis, dependency audit, secret detection, dynamic, API, fuzz, supply chain | structural, behavioral, adversarial, domain | required |
| AI Governance | Authority boundary, receipt integrity, registry integrity, owner approval, prompt injection, agent isolation, evidence chain | structural, adversarial, domain | required |
| Compliance | Licensing, regulatory, policy | behavioral, domain | advisory |
| Accessibility | Screen reader, keyboard, contrast, focus | behavioral, domain | optional |
| Localization | i18n, locale, formatting | behavioral, domain | optional |
| Release | Build, packaging, signing, SBOM, gates | structural, behavioral | required |

### 3.2 Test Classes

| Class | Source | Generator Behavior | Example |
|-------|--------|-------------------|---------|
| **Structural** | Component metadata (interfaces, routes, schemas) | Enumerate every known interface → basic existence/exercise test | "POST /api/owner/action exists and returns 200 with auth" |
| **Behavioral** | Contracts, schemas, state machines | Derive from required fields, constraints, transitions | "Missing receipt_id rejected with 400" |
| **Adversarial** | Node classification, security boundary tags | Apply template suite based on classification tag | "Authority boundary → privilege escalation attempt" |
| **Domain** | Human-authored knowledge | Track coverage gap; never invent domain knowledge | "Our specific JWT rotation logic is correct" |

### 3.3 Coverage Levels

| Level | Meaning | Gate Behavior |
|-------|---------|---------------|
| `informational` | Coverage reported but never blocks | Dashboard only |
| `advisory` | Coverage gaps surfaced with recommendation | Warning in qualification receipt |
| `required` | All applicable tests must pass | Required for release qualification |

A missing visual regression test (`optional`) should not block a backend release. A missing authority-boundary test (`required`) should.

### 3.4 Qualification Manifest

The qualification manifest extends the **Node Profile** (not a separate file). It is governed project truth because it affects release gates, required evidence, operational readiness, and Owner decisions.

```
Node Registry
    |
    Node Profile
        |
        Qualification Profile
            |
            ├── enabled domains
            ├── required coverage levels
            ├── release gates
            └── exceptions
```

Example:

```json
{
  "node_id": "NODE-LIBRARIAN-CORE",
  "qualification_profile": {
    "functional": { "level": "required" },
    "security": { "level": "required" },
    "adversarial": { "level": "advisory" },
    "accessibility": { "level": "optional" },
    "release_gate": {
      "required_domains": ["functional", "security", "ai_governance"]
    }
  }
}
```

---

## 4. Test Identity Model

Because tests are regenerated, they need stable identity across revisions.

### 4.1 Identity Structure

```
AUTH-BOUNDARY-001         ← stable intent identity
        |
        +-- rev: 3        ← revision (component version binding)
        |
        +-- generated_from: NODE-AUTHORITY-MODEL v7
        |
        +-- receipts:
              receipt #001 (rev 1, PASS)
              receipt #002 (rev 2, PASS)
              receipt #003 (rev 3, FAIL → regression detected)
```

| Property | Rule |
|----------|------|
| Base ID | Stable across regenerations. Represents the qualification intent. |
| Revision | Incremented when the source component version changes. |
| Invalidation | Base ID is retired if the source component is removed entirely. |
| History | Receipt chain provides authoritative lineage. |

### 4.2 Lifecycle

```
Test Identity Created
        |
        v
Component Version
        |
        v
Generated Revision
        |
        v
Execution
        |
        v
Receipt (linked to identity + revision + component version)
```

The stable identity enables historical trend analysis, regression tracking, and maturity metrics. The revision prevents stale implementation references.

---

## 5. Receipt Model

Qualification receipts **inherit** from the existing Evidence Receipt pattern. They do not create a parallel receipt system.

### 5.1 Inheritance

```
Evidence Receipt (existing, Librarian)
    ├── provenance (agent_id, session_id, source, timestamp)
    ├── custody (hash, signer, chain_ref)
    ├── result (outcome, evidence_hash)
    │
    └── [EXTENDED BY]
        │
        Qualification Receipt (new, QA Pilot)
            ├── domain: "security"
            ├── test_class: "adversarial"
            ├── component_refs: ["NODE-OWNER-QUEUE"]
            ├── code_locations: ["OwnerQueueService.swift:87"]
            ├── generator_info: { type: "security-template", version: "1.0" }
            └── execution: { runner: "qa-pilot", artifacts: [...] }
```

### 5.2 Receipt Structure

```json
{
  "receipt_type": "qualification",
  "inherits": "evidence-receipt-v1",
  "domain": "security",
  "test_class": "adversarial",
  "component_refs": ["NODE-OWNER-QUEUE"],
  "code_locations": ["OwnerQueueService.swift:87"],
  "test_identity": "AUTH-BOUNDARY-001/rev:3",
  "generator": {
    "type": "security-template",
    "version": "1.0"
  },
  "execution": {
    "runner": "qa-pilot",
    "timestamp": "",
    "artifacts": [],
    "hash": ""
  },
  "result": "PASS",
  "coverage": {
    "domain": "security",
    "required": 12,
    "executed": 12,
    "passed": 12,
    "level": "required"
  }
}
```

---

## 6. Event Integration Model

Qualification is triggered via Librarian events. Polling is inconsistent with the rest of the architecture.

### 6.1 Trigger Flow

```
Sprint sealed
      |
      v
Ledger event published
      |
      v
Affected nodes/components identified (from sprint change set)
      |
      v
Qualification request issued (with scope)
      |
      v
QA Pilot executes qualification for affected targets
      |
      v
Receipts returned
      |
      v
Evidence chain updated
      |
      v
Librarian custody seal
```

### 6.2 Event Scope

The event includes scope so QA Pilot does not rerun everything:

```json
{
  "event": "SPRINT_SEALED",
  "sprint_id": "SOME-SPRINT-1",
  "changed_targets": ["NODE-OWNER-QUEUE", "NODE-REGISTRY"],
  "qualification_required": ["security", "regression"],
  "qualification_level": "required"
}
```

### 6.3 Push Model Integration

QA Pilot registers as a qualification consumer in the Librarian's event model. The MCP push event is the integration point — consistent with the existing custody chain push model.

---

## 7. Generator Authority Boundary

### 7.1 Default Behavior

QA Pilot-generated tests are **qualification artifacts**, not source changes. They live in QA Pilot's qualification artifact store, not in the target project repository.

```
QA Pilot

Test Generator
      |
      v
Qualification Artifact Store
      |
      v
Execution Harness
      |
      v
Evidence Receipt
      |
      v
Librarian Custody Chain
```

### 7.2 Future Materialization (Requires Owner Approval)

A future authorized workflow could materialize tests into the target repository, but this requires explicit Owner authorization and is a separate capability:

```
Owner Approval
      |
      v
Materialize Test Artifact
      |
      v
Commit To Project Repository
```

### 7.3 Invariant

Generation does not equal authority. Tests are evidence-producing objects, not automatically trusted source changes.

---

## 8. Coverage Intelligence

QA Pilot identifies coverage gaps by comparing known components against executed tests.

### 8.1 Gap Detection

```
Known Components
      |
      v
Required Tests (from qualification profile)
      |
      v
Executed Tests (from latest qualification run)
      |
      v
Coverage Gap Report
```

### 8.2 Gap Report Structure

```json
{
  "component": "NODE-OWNER-QUEUE",
  "implementation": {
    "files": 5,
    "interfaces": 3,
    "authority_class": "owner_only"
  },
  "security": {
    "required": 12,
    "executed": 12,
    "status": "qualified"
  },
  "gaps": [],
  "status": "QUALIFIED"
}
```

### 8.3 Feedback Loop

```
Project
    ↓
Component Database
    ↓
Generated Tests
    ↓
Execution
    ↓
Coverage Report
    ↓
Coverage Gaps
    ↓
Project Improvements
    ↓
(cycle repeats at next seal event)
```

---

## 9. Architectural Invariants

| # | Invariant | Enforcement |
|---|-----------|-------------|
| 1 | QA Pilot executes qualification; Librarian owns truth | Receipt authority chain |
| 2 | Qualification manifest extends Node Profile, not a separate system | Schema validation |
| 3 | No duplicate registry or identity system for qualification targets | Registry ID uniqueness check |
| 4 | Qualification receipts inherit existing Evidence Receipt patterns | Schema extension |  
| 5 | Test identities use stable base IDs with versioned revisions | Identity lifecycle validation |
| 6 | Generated tests are qualification artifacts, not source changes | File boundary enforcement |
| 7 | Coverage levels prevent false authority (informational/advisory/required) | Gate-level validation |
| 8 | Test regeneration observes component version boundaries | Revision tracking |
| 9 | Push events include scope; QA Pilot never polls | Event contract validation |
| 10 | Domain tests are tracked but never generated | Coverage gap reporting |

---

## 10. Dependencies

| Dependency | Relationship | Status |
|------------|-------------|--------|
| Node Registry (existing) | Supplies node identity and profile for qualification targets | ✅ Sealed |
| Node Profile schema (existing) | Extended with qualification manifest | ✅ Sealed |
| Evidence Receipt schema (existing) | Inherited by qualification receipts | ✅ Sealed |
| Platform Truth Model (existing) | Supplies authoritative component facts | ✅ Sealed |
| Sprint Ledger (existing) | Provides deterministic change triggers | ✅ Sealed |
| QA Pilot harness patterns (existing) | Underlying test execution infrastructure | ✅ Sealed |
| QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1 (this sprint) | Defines architecture | 🟡 In planning |
| PLATFORM-DEPLOYMENT-READINESS-ROADMAP-PLANNING-1 | Upstream consumer of qualification contracts | 📋 Planned |

---

*Architecture document for QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1. Planning only. No implementation authority conferred.*
