# Cross-System Decision Ownership Contract

**Sprint:** Cross-System Contract Hardening (#236)
**Status:** ACTIVE — Owner-authorized 2026-08-16

---

## 1. Purpose

Define where human authority enters the system.

## 2. Question

**Where does a human decision occur?**

## 3. Authority Model

### 3.1 System Responsibilities

| System | Responsibility | Boundary |
|--------|---------------|----------|
| **Detect** | Identify issues, gaps, risks | Observation only |
| **Explain** | Provide context, provenance, rationale | Information only |
| **Route** | Direct to appropriate decision-maker | Routing only |

### 3.2 Owner Responsibilities

| Responsibility | Authority | Boundary |
|---------------|-----------|----------|
| **Accept** | Risk acceptance | Final authority |
| **Reject** | Proposal rejection | Final authority |
| **Modify** | Change scope/requirements | Final authority |
| **Approve** | Authorization to proceed | Final authority |

## 4. Decision Flow

```
System Detects Issue
        │
        △
System Explains Context
        │
        △
System Routes to Owner
        │
        △
Owner Reviews
        │
        △
Owner Decides
        │
        △
System Records Decision
```

## 5. Decision Types

| Decision | System Role | Owner Role |
|----------|-------------|------------|
| Risk acceptance | Identify risk, explain impact | Accept, defer, or reject |
| Capability approval | Qualify capability, explain readiness | Approve or reject |
| Work authorization | Provide context, explain readiness | Authorize or reject |
| Finding closure | Detect finding, explain resolution | Verify and close |
| Governance change | Detect need, explain rationale | Approve modification |

## 6. System Constraints

Systems MUST NOT:

| Forbidden | Reason |
|-----------|--------|
| Self-approve | Owner approval required |
| Make governance decisions | Governance is Owner authority |
| Create binding commitments | Only Owner can commit |
| Modify authority scope | Only Owner can change authority |
| Close findings | Only Owner can verify resolution |

## 7. Owner Authority Preservation

| Principle | Rule |
|-----------|------|
| Authority is Owner-held | Systems recommend; Owner decides |
| Decisions are recorded | All Owner decisions are audit-logged |
| Decisions are final | System cannot override Owner decision |
| Decisions are scoped | Each decision has explicit boundaries |

## 8. Non-Authority Boundary

Decision ownership:

| May Do | May Not Do |
|--------|------------|
| Detect issues | Resolve issues |
| Explain context | Make decisions |
| Route to Owner | Bypass Owner |
| Record decisions | Modify decisions |
| Recommend actions | Authorize actions |
