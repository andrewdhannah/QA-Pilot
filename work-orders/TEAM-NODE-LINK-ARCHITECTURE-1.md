# TEAM-NODE-LINK-ARCHITECTURE-1

**Work Packet:** Multi-Person LINK Architecture
**Phase:** 1 — Design
**Status:** IN PROGRESS
**Date:** 2026-08-18
**Agent:** OpenWork-Claude (mimo-v2.5)

---

## Purpose

Define the team operating model: people, Nodes, LINK personas, roles, agents, planning, and continuity.

---

## 1. Identity Model

### Separate Concepts

| Concept | Owner | Description |
|---------|-------|-------------|
| Human identity | Librarian Core | Governed human identity (real name, credentials) |
| Node identity | Librarian Core | Cryptographic Node identity (machine/device) |
| LINK persona | Librarian Core | Assigned from controlled vocabulary (Atlas, Forge, Sentinel, ...) |
| Project role | Team/Owner | Project Lead, Engineer, QA Lead, Documentation |
| Agent identity | Node | Per-agent identity (model, runtime, capabilities) |
| Authority set | Librarian Core | Governed permissions per role/scope |

### LINK Persona Vocabulary

```
Atlas       — Planning / Coordination
Forge       — Engineering / Implementation
Sentinel    — Verification / QA
Scribe      — Knowledge / Documentation
Beacon      — Communication / Status
Scout       — Discovery / Research
Pathfinder  — Architecture / Design
Navigator   — Release / Deployment
Stewards    — Custody / Governance
Relay       — Transport / Integration
Vector      — Security / Compliance
Architect   — System Design
```

### Identity Record

```json
{
  "human_id": "<governed human identity>",
  "node_id": "<cryptographic Node identity>",
  "link_persona": "Sentinel",
  "membership": "Project X",
  "role": "QA Lead",
  "authority": "<governed authority set>",
  "agents": ["<agent-1>", "<agent-2>"]
}
```

---

## 2. Team Structure

```
TEAM
 ├── People
 │    ├── project roles
 │    ├── availability
 │    └── capacity
 │
 ├── Nodes
 │    ├── Node identity
 │    ├── LINK persona
 │    ├── local capabilities
 │    └── agents
 │
 ├── Shared LINK
 │    ├── conversations
 │    ├── planning
 │    ├── assignments
 │    ├── handoffs
 │    ├── decisions
 │    └── coordination
 │
 └── Planning
      ├── Work Orders
      ├── Work Packets
      ├── availability
      ├── continuity
      ├── authorization envelopes
      ├── agent operating context
      └── refinement boundaries
```

---

## 3. Role-Based Operating Context

Roles tell agents HOW to behave, not WHAT they're authorized to do.

### QA Lead (Sentinel)

```
ROLE CONTEXT
────────────
Project Role: QA Lead

Primary responsibilities:
- Independent verification
- Test planning
- Regression analysis
- Evidence collection
- Finding generation

Operating principles:
- Do not modify production implementation
- Prefer independent verification
- Attach evidence to claims
- Escalate unresolved findings
- Do not resolve Owner decisions
```

### Engineer (Forge)

```
ROLE CONTEXT
────────────
Project Role: Engineer

Primary responsibilities:
- Implementation
- Technical investigation
- Work Packet execution
- Code review
- Engineering handoff

Operating principles:
- Work within assigned packets
- Produce implementation evidence
- Request clarification when scope is ambiguous
- Do not self-authorize beyond packet scope
```

### Project Lead (Atlas)

```
ROLE CONTEXT
────────────
Project Role: Project Lead

Primary responsibilities:
- Planning
- Coordination
- Work assignment
- Progress tracking
- Decision routing

Operating principles:
- Plan within governance constraints
- Assign work through governed channels
- Track progress via evidence
- Route decisions to Owner
- Do not execute implementation
```

---

## 4. Three Instruction Layers

```
1. System governance (Librarian-defined, non-negotiable)
   "You cannot perform an action without the required authority."

2. Role operating context (Project/team defined)
   "You are operating as a QA Lead."

3. Work-specific instructions (Work Packet defined)
   "Verify authentication behavior against acceptance criteria AUTH-17."
```

Together:

```
Governance
    ↓
Role
    ↓
Work Packet
    ↓
Agent execution
    ↓
Evidence
```

---

## 5. Agent Specialization

Agents can be specialized without being trusted.

```
Forge (Engineer)
 ├── Coding Agent
 ├── Code Review Agent
 └── Debug Agent

Sentinel (QA Lead)
 ├── Test Agent
 ├── Regression Agent
 └── Evidence Agent

Atlas (Project Lead)
 ├── Planning Agent
 ├── Coordination Agent
 └── Project Analysis Agent
```

**Capability ≠ Authority**

An agent may have the capability to call a tool but still require an authorized Work Packet or Owner decision before that capability can be exercised.

---

## 6. Planning Packet as Operational Continuity Contract

### Structure

```
PLANNING PACKET
──────────────────────────────────

Team
  Members
  Roles
  LINK identities

Availability
  Working periods
  Holidays
  Planned absences
  Time zones

Capacity
  Human capacity
  Agent capacity
  Node capacity

Work
  Work Orders
  Work Packets
  Dependencies
  Milestones

Continuity
  Agent delegation rules
  Permitted unattended work
  Human review requirements
  Escalation conditions

Governance
  Authority
  Scope
  Approval requirements
  Evidence requirements
```

### Authorization Envelope

```
AUTHORIZED TESTING ENVELOPE

Purpose:
  Verify authentication implementation.

Authorized refinement:
  YES

Permitted refinement:
  Tests directly derived from
  implementation behavior.

Maximum scope:
  Authentication subsystem.

Permitted evidence:
  Test results, logs, screenshots,
  reproducible findings.

May create findings:
  YES

May modify production code:
  NO

May change acceptance criteria:
  NO

May declare release:
  NO

Escalate when:
  New security domain encountered.
```

---

## 7. Three-State Model

### 1. Pre-authorized

```
Plan → authorized → agent executes
```

No additional human intervention required.

### 2. Bounded refinement

```
Authorized plan
    ↓
Implementation reality
    ↓
Agent adapts within defined rules
    ↓
Evidence + explanation
```

Still autonomous.

### 3. Boundary crossing

```
Agent encounters something outside authorized scope
    ↓
LINK detects difference
    ↓
Pause / escalate
    ↓
Human decision
```

---

## 8. LINK as Explanation Layer

When a human returns from absence:

```
WHILE YOU WERE AWAY
────────────────────────────

Sentinel unavailable: 5 days

Pre-authorized work:
  7 packets

Completed:
  7

Agent refinements:
  3

Out-of-scope changes:
  0

Findings:
  2

Material deviations:
  1

Human decisions required:
  1
```

---

## 9. Distributed Teams

```
Toronto
  Forge — Engineering
     └── Node + agents

Ottawa
  Sentinel — QA
     └── Node + QA-Pilot

Montreal
  Atlas — Project Lead
     └── Node + planning agents
```

Shared Librarian state provides continuity. Work packets move through the team while humans are offline, within pre-authorized boundaries.

---

## 10. Governance Invariant

**Human absence does not create an authority vacuum.**
**Agent continuity does not create authority escalation.**

---

## Acceptance Gates

| Gate | Requirement |
|------|-------------|
| TEAM-001 | Identity model defined (6 separate concepts) |
| TEAM-002 | LINK persona vocabulary established |
| TEAM-003 | Role-based operating context defined |
| TEAM-004 | Three instruction layers specified |
| TEAM-005 | Planning packet structure defined |
| TEAM-006 | Authorization envelope model defined |
| TEAM-007 | Three-state model (pre-authorized, bounded, boundary) |
| TEAM-008 | LINK explanation layer defined |
| TEAM-009 | Distributed team model defined |
| TEAM-010 | Governance invariants documented |

---

*Design in progress. No implementation — architecture definition only.*
