# Cross-System Capability Consumption Contract

**Sprint:** Cross-System Contract Hardening (#236)
**Status:** ACTIVE — Owner-authorized 2026-08-16

---

## 1. Purpose

Define how agents discover and use capabilities safely.

## 2. Question

**How does an agent discover and use a capability safely?**

## 3. Capability Consumption Flow

```
Agent
   │
   △
Registry Lookup
   │
   △
Authority Boundary Check
   │
   △
Documentation Review
   │
   △
Evidence Verification
   │
   △
Health Status Check
   │
   △
Capability Use
```

## 4. Registry Lookup

### 4.1 Required Fields

```json
{
  "capability_id": "string",
  "capability_name": "string",
  "capability_type": "string",
  "provider_system": "string",
  "authority_scope": "string",
  "health_status": "healthy | degraded | unknown"
}
```

### 4.2 Discovery Rules

| Rule | Requirement |
|------|-------------|
| Identity | Capability must have unique ID |
| Documentation | Capability must have description |
| Authority | Capability must declare scope |
| Health | Capability must report status |

## 5. Authority Boundary

### 5.1 Authority Scope Types

| Scope | Meaning | Agent May |
|-------|---------|-----------|
| `read_only` | Observation only | Read state |
| `recommendation` | Advisory output | Recommend actions |
| `mutation` | State changes | Modify state (with approval) |
| `critical` | High-impact changes | Modify state (with Owner approval) |

### 5.2 Agent Constraints

Agents MUST NOT:

| Forbidden | Reason |
|-----------|--------|
| Exceed authority scope | Stay within declared boundaries |
| Self-approve | Owner approval required for mutations |
| Modify governance state | Governance is separate from execution |
| Bypass qualification | All changes must be qualified |

## 6. Documentation References

Every capability must reference:

- Description of what it does
- Authority boundaries
- Evidence requirements
- Health status interpretation

## 7. Evidence References

Capability use must reference:

- Qualification status
- Risk assessment
- Evidence coverage
- Freshness state

## 8. Health Status Interpretation

| Status | Meaning | Agent Action |
|--------|---------|--------------|
| `healthy` | Capability operational | May use |
| `degraded` | Capability partially operational | Use with caution |
| `unknown` | Cannot determine status | Do not use until verified |

## 9. Non-Authority Boundary

Capability consumption:

| May Do | May Not Do |
|--------|------------|
| Discover capabilities | Modify capability definitions |
| Check authority | Expand authority scope |
| Use within bounds | Self-approve actions |
| Report health | Modify health status |
| Reference evidence | Create false evidence |
