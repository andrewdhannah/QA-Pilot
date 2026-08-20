# ADR-B: Multi-Person Node/LINK Operating Architecture

**Decision Record:** ADR-B
**Date:** 2026-08-18
**Status:** SEALED
**Work Packet:** TEAM-NODE-LINK-ARCHITECTURE-1

---

## Decision

The Librarian supports multi-person teams through a governed operating architecture with six distinct identity concepts, role-based agent specialization, planning packets as continuity contracts, and authorization envelopes for bounded autonomous work.

---

## Context

The Librarian was designed for single-Owner governance. Extending to teams requires explicit identity separation, role-based operating context, and continuity rules that preserve governance while enabling asynchronous collaboration.

---

## Identity Model

Six concepts remain explicitly distinct:

| Concept | Owner | Description |
|---------|-------|-------------|
| Human identity | Librarian Core | Governed human identity |
| Node identity | Librarian Core | Cryptographic machine identity |
| LINK persona | Librarian Core | Assigned from controlled vocabulary |
| Project role | Team/Owner | Project Lead, Engineer, QA Lead |
| Agent identity | Node | Per-agent identity (model, runtime) |
| Authority set | Librarian Core | Governed permissions per scope |

---

## Key Invariants

| Invariant | Rule |
|-----------|------|
| LINK ≠ authority | LINK persona is presentation identity, not permission |
| Role ≠ authority | Role context tells agent how to behave, not what it may do |
| Agent ≠ human | Agent actions are attributed to agent, not human |
| Absence ≠ vacuum | Human absence does not create authority vacuum |
| Continuity ≠ escalation | Agent continuity does not expand authority |
| Refinement ≠ boundary | Bounded refinement is distinguishable from boundary crossing |

---

## Planning Packet Evolution

The planning packet becomes the operational continuity contract:

```
Availability + Role + Capacity + Work
    + Agent operating context
    + Authorization envelope
    + Refinement boundary
    + Escalation rules
    = Operational continuity contract
```

---

## Gates Passed

TNL-001 through TNL-012: ALL PASS

---

*Architectural Decision Record — sealed.*
