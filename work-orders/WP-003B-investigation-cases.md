# WP-003B — Investigation Cases

**Date:** 2026-08-16
**Status:** Classification pending — awaiting investigation evidence

---

## Case 1: working-bibliography-extension

**Classification:** REGISTERED
**Current lifecycle_phase:** empty

### Existing Governance Concepts

This extension already has:
- Manifest/baseline behavior
- Custody concepts
- Extension-scoped drift detection

### Investigation Questions

| Question | Current Answer |
|---|---|
| Does it still participate in the current capability lifecycle? | Unknown |
| Is there a provider? | Unknown |
| Is there evidence of recent activity? | None observed |
| Does the capability projection reference it? | In governance entities only |

### Possible Outcomes

**Path A:** REGISTERED → ACTIVE_CAPABILITY
- If investigation reveals it's an active extension with ongoing use

**Path B:** REGISTERED → DEPRECATED_CANDIDATE
- If investigation reveals it's no longer part of the current capability lifecycle

### Decision Required

Owner decision on which path. No mutation until investigation completes.

---

## Case 2: librarian-vault

**Classification:** REGISTERED
**Current lifecycle_phase:** empty

### Abstraction Distinction

This entity may not be a capability in the same sense as others.

**Capability:** "does work on behalf of the system"
**Infrastructure:** "provides substrate required by capabilities"

If Vault is infrastructure, forcing it through capability lifecycle states creates an abstraction mismatch.

### Investigation Questions

| Question | Current Answer |
|---|---|
| Is Vault a user-facing capability? | Unknown |
| Is it infrastructure that capabilities run on? | Possible |
| Does it have a provider? | Unknown |
| Is there evidence of recent activity? | None observed |
| Does the knowledge substrate depend on it? | Possible relationship |

### Possible Outcomes

**Path A:** REGISTERED → ACTIVE_CAPABILITY (Initialize)
- If Vault is a capability that does work

**Path B:** REGISTERED → SYSTEM_COMPONENT
- If Vault is infrastructure, not a capability
- Requires a new lifecycle category: `SYSTEM_COMPONENT` or `FOUNDATIONAL_SERVICE`

**Path C:** REGISTERED → DEPRECATED_CANDIDATE
- If Vault is superseded by another component

### Decision Required

Owner decision on abstraction level. The registry model may need to handle infrastructure components differently from capabilities.

---

## Registry State After WP-003B

| Entity | lifecycle_phase | Status |
|---|---|---|
| librarian | execution | Sealed |
| agent-bridge | execution | Sealed |
| librarian-workbench | execution | Sealed |
| qa-pilot | init | Sealed |
| knowledge-ingestion-addon | init | Sealed |
| working-bibliography-extension | (empty) | Investigation pending |
| claude-conversation-ingestion | (empty) | ARCHIVED — superseded |
| librarian-vault | (empty) | Investigation pending |

**6 of 8 populated. 2 investigation cases remain.**
