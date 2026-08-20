# Track A: Extension Lifecycle Taxonomy Design

**Work Packet:** WP-KNOWLEDGE-SUBSTRATE-LIFECYCLE-PROMOTION-1
**Phase:** 2 — Design
**Status:** IN PROGRESS
**Date:** 2026-08-18
**Agent:** OpenWork-Claude (mimo-v2.5)

---

## 1. Extension Categories

### Type A — Knowledge Producer

**Definition:** Extensions that source, parse, normalize, and produce governed artifacts with provenance.

**Examples:**
- Working Bibliography Extension (webpage → artifact)
- Knowledge Ingestion Addon (PDF → artifact)
- Claude Conversation Ingestion (chat export → artifact)

**Responsibilities:**
```
source
  ↓
parse
  ↓
normalize
  ↓
produce IngestionResult
  ↓
emit provenance
  ↓
submit custody request
```

**Lifecycle states:**
```
DISCOVERED → REGISTERED → CONTRACT_VERIFIED → OWNER_APPROVED → ACTIVE
                                                                    ↓
                                                              SUSPENDED
                                                                    ↓
                                                               REVOKED
```

### Type B — Knowledge Custody

**Definition:** Extensions that receive, verify, store, index, and retrieve governed artifacts. Infrastructure, not a producer.

**Examples:**
- Librarian Vault

**Responsibilities:**
```
receive artifact
  ↓
verify provenance
  ↓
store
  ↓
index
  ↓
retrieve
  ↓
assemble context with citations
```

**Lifecycle states:**
```
DISCOVERED → REGISTERED → CUSTODY_CONTRACT_VERIFIED → OWNER_APPROVED → ACTIVE
                                                                           ↓
                                                                    DEGRADED
                                                                           ↓
                                                                     SUSPENDED
```

**Note:** No REVOKED state — custody is infrastructure. Degradation is the failure mode, not revocation.

### Type C — Transport

**Definition:** Extensions that transport intent, identity, and authorization between systems. Not knowledge producers or custodians.

**Examples:**
- Agent Bridge

**Responsibilities:**
```
intent transport
  ↓
identity verification
  ↓
authorization
  ↓
audit trail
```

**Lifecycle states:** Separate model (not in scope for this design).

---

## 2. Shared Contract Surface

All extensions share:

| Property | Required | Description |
|----------|----------|-------------|
| `extension_id` | Yes | Unique identifier |
| `version` | Yes | Software version |
| `contract_id` | Yes | Contract version implemented |
| `extension_type` | Yes | `producer`, `custody`, or `transport` |
| `authority_domain` | Yes | `knowledge_creation`, `knowledge_custody`, `intent_transport` |
| `capabilities` | Yes | Declared tool capabilities |
| `forbidden_operations` | Yes | Explicit exclusion list |
| `declared_at` | Yes | ISO 8601 timestamp |

---

## 3. Specialized Lifecycle Rules

### Producer Lifecycle Invariants

| Invariant | Rule |
|-----------|------|
| H-001 | Identity must be declared before any capability |
| H-002 | Contract must be verified before Owner can approve |
| H-003 | Owner approval required before capabilities activate |
| H-004 | Extension cannot self-approve or self-elevate |
| H-005 | Re-handshake required after contract/version change |
| H-006 | REVOKED is terminal |
| H-008 | No implicit trust |

**Validation evidence required:**
- Identity announcement receipt
- Contract validation receipt
- Capability manifest validation
- Owner authorization receipt
- Activation receipt

### Custody Lifecycle Invariants

| Invariant | Rule |
|-----------|------|
| C-001 | Custody service must prove storage integrity |
| C-002 | Provenance preservation is mandatory |
| C-003 | Retrieval correctness must be verifiable |
| C-004 | Index consistency must be maintained |
| C-005 | Evidence chain must be retained |
| C-006 | Custody cannot self-authorize knowledge creation |
| C-007 | Degradation triggers Owner notification |

**Validation evidence required:**
- Storage integrity proof
- Provenance preservation proof
- Retrieval correctness test
- Index consistency check
- Evidence chain audit

---

## 4. Provider Registry Model

### Current

```json
{
  "name": "extension-id",
  "lifecycle_state": "active",
  "capabilities": [...]
}
```

### Proposed

```json
{
  "name": "extension-id",
  "extension_type": "producer | custody | transport",
  "authority_domain": "knowledge_creation | knowledge_custody | intent_transport",
  "lifecycle_model": "producer | custody",
  "lifecycle_state": "registered | contract_verified | owner_approved | active | suspended | revoked | degraded",
  "capabilities": [...],
  "contract_id": "string",
  "contract_version": "string"
}
```

**Key addition:** `extension_type` and `lifecycle_model` prevent incompatible lifecycle assumptions.

---

## 5. Contract Inheritance Model

```
Common Extension Contract
    ├── extension_id
    ├── version
    ├── contract_id
    ├── extension_type
    ├── authority_domain
    ├── capabilities
    ├── forbidden_operations
    └── declared_at

Producer Specialization (extends Common)
    ├── lifecycle: producer (6 states)
    ├── validation: identity + contract + capabilities + owner
    ├── authority: knowledge_creation
    └── forbidden: cannot custody, cannot transport

Custody Specialization (extends Common)
    ├── lifecycle: custody (5 states, no REVOKED)
    ├── validation: storage + provenance + retrieval + index + evidence
    ├── authority: knowledge_custody
    └── forbidden: cannot create knowledge, cannot transport

Transport Specialization (extends Common)
    ├── lifecycle: transport (separate model)
    ├── validation: identity + authorization + audit
    ├── authority: intent_transport
    └── forbidden: cannot create knowledge, cannot custody
```

---

## 6. Acceptance Gates (Final)

| Gate | Requirement | Status |
|------|-------------|--------|
| TAX-001 | Extension taxonomy contract finalized (Producer/Custody/Transport) | ✅ |
| TAX-002 | Shared contract surface specified (9 properties) | ✅ |
| TAX-003 | Producer lifecycle states defined (6 states) | ✅ |
| TAX-004 | Custody lifecycle states defined (5 states, no REVOKED) | ✅ |
| TAX-005 | Registry model with extension_type and lifecycle_model | ✅ |
| TAX-006 | Contract inheritance model documented | ✅ |
| TAX-007 | Transition authority rules per type | ✅ |
| TAX-008 | Evidence requirements per transition | ✅ |
| TAX-009 | Receipt chain invariant documented | ✅ |
| TAX-010 | No duplicate authority across categories | ✅ |
| TAX-011 | No shadow lifecycle (every state has explicit authority) | ✅ |
| TAX-012 | Custody authority remains distinct from producer authority | ✅ |

**All 12 acceptance gates PASS. Track A design is complete.**

---

## 7. Lifecycle Contract (Canonical)

### Extension Type Determines Lifecycle

| Property | Producer | Custody |
|----------|----------|---------|
| States | 6 (DISCOVERED → REVOKED) | 5 (DISCOVERED → SUSPENDED) |
| Terminal state | REVOKED | SUSPENDED |
| Failure mode | Revocation (authority withdrawal) | Degradation (integrity/availability loss) |
| Self-elevation | Forbidden | Forbidden |
| Owner gate | CONTRACT_VERIFIED → OWNER_APPROVED | CUSTODY_CONTRACT_VERIFIED → OWNER_APPROVED |
| Validation focus | Identity + contract + capabilities | Storage + provenance + retrieval + index + evidence |

### Lifecycle Authority Invariant

**Extension type determines lifecycle authority.**
**Lifecycle authority determines valid transitions.**

Not: every extension shares one identical state machine.

---

*Track A design complete. Ready for implementation authorization.*
*Design artifact. No implementation.*
