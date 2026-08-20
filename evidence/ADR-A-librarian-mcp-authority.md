# ADR-A: Librarian MCP as Sole Distributed Authority

**Decision Record:** ADR-A
**Date:** 2026-08-18
**Status:** SEALED
**Work Packet:** VAULT-MCP-TOPOLOGY-RECONCILIATION-1

---

## Decision

Librarian MCP (:3457) is the sole distributed MCP authority. All knowledge capabilities — including Vault custody operations — are consumed through the existing Librarian authority boundary. No add-on operates as a peer MCP authority.

---

## Context

Three add-ons (KIA, WB, Vault) currently expose independent MCP servers. This creates competing integration surfaces and risks recreating the dual-authority topology that was just eliminated.

---

## Consequences

### Before

```
KIA MCP ──┐
WB MCP  ──┼── competing integration surfaces
Vault MCP ┘
```

### After

```
                 Librarian MCP
                  sole authority
                       │
                governed interface
                       │
             ┌─────────┴─────────┐
             │                   │
          Producers            Vault
       KIA / WB / CCI          Custody
             │                   │
             └─────────┬─────────┘
                       ▼
                 Librarian Core
```

### Invariants Established

| Invariant | Rule |
|-----------|------|
| Single authority | Librarian MCP is the only distributed MCP endpoint |
| Add-on composition | Add-ons are internal components behind Librarian MCP |
| Custody ≠ authority | Vault provides custody infrastructure, not governance authority |
| Producer ≠ authority | Producers produce artifacts, not governance decisions |
| Remote access | Nodes connect to Librarian MCP, not to add-on MCPs |

---

## Gates Passed

VLT-001 through VLT-010: ALL PASS

---

*Architectural Decision Record — sealed.*
