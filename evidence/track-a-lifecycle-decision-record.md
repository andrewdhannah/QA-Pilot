# Track A: Extension Lifecycle Decision Record

**Work Packet:** WP-KNOWLEDGE-SUBSTRATE-LIFECYCLE-PROMOTION-1
**Phase:** 2 — Design (continuation)
**Date:** 2026-08-18

---

## Purpose

Define the lifecycle decision record — what fields exist, who authorizes transitions, and what evidence is required for each extension type.

---

## 1. Common Fields (All Extension Types)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `extension_id` | string | Yes | Unique identifier |
| `extension_type` | enum | Yes | `producer`, `custody`, `transport` |
| `version` | string | Yes | Software version |
| `contract_id` | string | Yes | Contract version implemented |
| `current_state` | enum | Yes | Current lifecycle state |
| `previous_state` | enum | Yes | Previous state (for audit) |
| `transition_authority` | enum | Yes | `automated`, `owner`, `system` |
| `transition_reason` | string | Yes | Why the transition occurred |
| `transitioned_at` | ISO 8601 | Yes | When the transition occurred |
| `evidence_refs` | array | Yes | Receipts proving the transition |
| `authority_ref` | string | Conditional | Owner authorization ID (if owner-gated) |

---

## 2. Producer-Specific Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `declared_capabilities` | array | Yes | Tools the extension exposes |
| `forbidden_operations` | array | Yes | Explicit exclusions |
| `identity_receipt` | string | Yes | Identity announcement proof |
| `contract_validation_receipt` | string | Yes | Contract validation proof |
| `capability_validation_receipt` | string | Yes | Capability manifest validation |
| `owner_authorization_receipt` | string | Yes | Owner approval proof |
| `activation_receipt` | string | Yes | Activation proof |

### Producer Transition Evidence

| Transition | Authority | Required Evidence |
|------------|-----------|-------------------|
| DISCOVERED → REGISTERED | automated | Identity announcement receipt |
| REGISTERED → CONTRACT_VERIFIED | automated | Contract validation receipt + capability validation receipt |
| CONTRACT_VERIFIED → OWNER_APPROVED | owner | Owner authorization receipt |
| OWNER_APPROVED → ACTIVE | automated | Activation receipt |
| ACTIVE → SUSPENDED | automated | Drift detection evidence |
| ACTIVE → REVOKED | owner | Contract violation evidence + owner revocation receipt |
| SUSPENDED → ACTIVE | owner | Drift cleared evidence + owner reactivation receipt |
| SUSPENDED → REVOKED | owner | Owner termination receipt |

---

## 3. Custody-Specific Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `storage_integrity_proof` | string | Yes | Storage integrity verification |
| `provenance_preservation_proof` | string | Yes | Provenance chain integrity |
| `retrieval_correctness_proof` | string | Yes | Retrieval verification test |
| `index_consistency_proof` | string | Yes | Index integrity check |
| `evidence_chain_audit` | string | Yes | Evidence retention verification |
| `degradation_reason` | string | Conditional | Why degraded (if DEGRADED) |

### Custody Transition Evidence

| Transition | Authority | Required Evidence |
|------------|-----------|-------------------|
| DISCOVERED → REGISTERED | automated | Identity announcement receipt |
| REGISTERED → CUSTODY_CONTRACT_VERIFIED | automated | Storage integrity proof + provenance preservation proof + retrieval correctness proof + index consistency proof + evidence chain audit |
| CUSTODY_CONTRACT_VERIFIED → OWNER_APPROVED | owner | Owner authorization receipt |
| OWNER_APPROVED → ACTIVE | automated | Activation receipt |
| ACTIVE → DEGRADED | automated | Degradation evidence (integrity failure, availability loss) |
| ACTIVE → SUSPENDED | automated | Suspension evidence |
| DEGRADED → ACTIVE | owner | Recovery evidence + owner restoration receipt |
| DEGRADED → SUSPENDED | owner | Owner suspension receipt |
| SUSPENDED → ACTIVE | owner | Owner reactivation receipt |

---

## 4. Authority Model Summary

| Extension Type | Transition Authority | Self-Elevation | Revocation |
|---------------|---------------------|----------------|------------|
| Producer | automated + owner | Forbidden (H-004) | Yes (terminal) |
| Custody | automated + owner | Forbidden (C-006) | No (degraded instead) |
| Transport | separate model | TBD | TBD |

---

## 5. Evidence Chain Invariant

Every lifecycle transition must produce:

1. **Receipt** — immutable record of the transition
2. **Evidence** — proof that the transition was valid
3. **Authority** — who/what authorized the transition
4. **Timestamp** — when the transition occurred

The receipt chain is append-only. No transition can be retroactively modified.

---

## 6. Acceptance Gates

| Gate | Requirement |
|------|-------------|
| DR-001 | Common fields defined for all extension types |
| DR-002 | Producer-specific fields defined |
| DR-003 | Custody-specific fields defined |
| DR-004 | Transition authority rules specified |
| DR-005 | Evidence requirements defined per transition |
| DR-006 | Receipt chain invariant documented |
| DR-007 | No self-elevation allowed for any extension type |

---

*Design artifact. No implementation.*
