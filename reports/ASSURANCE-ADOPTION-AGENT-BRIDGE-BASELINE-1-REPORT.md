# ASSURANCE-ADOPTION-AGENT-BRIDGE-BASELINE-1 — Adoption Baseline Report

**Sprint:** #209
**Date:** 2026-07-20
**Status:** 🔍 Pending Owner review
**Epic:** EPIC-ASSURANCE-OPERATIONS-ADOPTION-1 (Phase 2)

---

## Executive Summary

Agent Bridge validates that the assurance model transfers to execution-shaped projects. The mapping is less direct than Librarian but more revealing: Agent Bridge's evidence sources are fundamentally different (runtime, integration, extension code), yet the core assurance concepts (identity, governance, ownership, operational state) remain applicable. Adapters will differ in kind, not just degree, from those built for Librarian.

---

## Mapping Assessment

### Direct Mappings

| Assurance Concept | Agent Bridge Equivalent | Quality |
|-------------------|------------------------|---------|
| **Project Identity** | `PACKAGE-MANIFEST.txt` + `docs/PRODUCT-OVERVIEW.md` | ✅ Present, different format |
| **Governance Documents** | `docs/security/`, `docs/custody/`, `docs/architecture/` | ✅ Rich governance documentation |
| **Ownership Authority** | `SECURITY-AUTHORITY-MODEL.md`, custody docs | ✅ Explicit authority model |
| **Operational State** | `server/server.log`, `server/bridge-config.json` | ✅ Runtime state accessible |
| **Sprint History** | `SESSION-HANDOFF.md` sprint table | ⚠️ Embedded in handoff doc, no machine-readable ledger |

### Adapter-Needed Mappings

| Assurance Concept | Gap | Adapter Approach |
|-------------------|-----|------------------|
| **Evidence Lineage** | No centralized evidence store; evidence is in docs/ (custody, security, release) | Map docs/ directory tree to evidence categories by subdirectory |
| **Evidence Freshness** | No timestamps indexed; file system mtime available | Derive from file modification times across docs/ and scripts/ |
| **Release Readiness** | No RELEASE-GATE.md; release docs at `docs/release/` | Map `docs/release/RELEASE-NOTES.md` presence as readiness signal |
| **Decision Queue** | Decisions embedded in custody docs | Extract from `docs/custody/agent-bridge/` contents |

### No Mappings (Not Present)

| Concept | Status |
|---------|--------|
| Finding Lifecycle | ❌ No equivalent — not applicable to integration-focused project |
| Risk Prioritization Model | ❌ No equivalent — risk handled through security docs |
| Continuous Assurance Loop | ❌ No equivalent — no automated assurance run |
| Pipeline Layer Registry | ❌ No equivalent — no pipeline abstraction |
| Sprint Ledger (machine-readable) | ❌ Sprint history in prose handoff, not JSON |

---

## Adapter Requirements Compared to Librarian

| Dimension | Librarian | Agent Bridge | Difference |
|-----------|-----------|-------------|------------|
| Identity source | startup-contract.json | PACKAGE-MANIFEST.txt + docs/ | Different format, same concept |
| Evidence source | receipts/ directory | docs/ subdirectories | Same concept, different location |
| Sprint history | sprint-ledger.json (JSON) | SESSION-HANDOFF.md (prose) | **Fundamentally different** — no machine-readable ledger |
| Governance depth | docs/governance/ (40+ files) | docs/security/, docs/custody/ (fewer) | Less structured but still present |
| Runtime state | Not applicable (governance project) | server/config, server/log | **New concept** — Agent Bridge has runtime state |
| Extension identity | Not applicable | extension/manifest.json | **New concept** — multi-component project |

---

## Key Discovery: Multi-Component Identity

Agent Bridge is the first project tested that has **multiple identity-bearing components**:
- The bridge server (server/package.json)
- The browser extension (extension/manifest.json)  
- The GitHub refresh pack (agent-bridge-github-refresh-pack/)

This introduces a concept not present in either QA Pilot (single Python project) or Librarian (single Swift project): **multi-component project identity**. The assurance model currently assumes one project = one identity. Agent Bridge suggests some projects are compound.

**Classification:** Genuine gap — not a QA Pilot-specific artifact. May need model refinement.

---

## Friction Points

| Friction | Severity | Note |
|----------|----------|------|
| No machine-readable sprint history | HIGH | **Most significant gap.** Agent Bridge's sprint history is prose in SESSION-HANDOFF.md. No ledger to parse. May need a lightweight sprint index to participate in assurance projection. |
| Multi-component identity | MEDIUM | Server, extension, and refresh pack have separate identities. Model needs to handle compound projects. |
| No centralized evidence index | LOW | Evidence scattered across docs/ subdirectories. Adapter can discover by convention. |
| Runtime evidence not in QA Pilot model | MEDIUM | Agent Bridge has real runtime state (server config, logs, queue). These don't map to finding lifecycle or evidence pipeline. May need a new "runtime health" concept or handle as adapter-only. |

---

## AB-AD Gate Results

| Gate | Result |
|------|--------|
| AB-AD-1: Agent Bridge identity mapped | ✅ PASS — PACKAGE-MANIFEST.txt serves as identity source |
| AB-AD-2: Runtime/integration evidence sources identified | ✅ PASS — server/, extension/, docs/ all have evidence |
| AB-AD-3: Existing receipts map into evidence lineage | ⚠️ PARTIAL — no receipts directory, but docs/custody/ serves analogously |
| AB-AD-4: Ownership boundaries preserved | ✅ PASS — SECURITY-AUTHORITY-MODEL.md defines boundaries |
| AB-AD-5: Missing capabilities remain visible | ✅ PASS — finding lifecycle, risk model correctly absent |
| AB-AD-6: No premature concept promotion | ✅ PASS — multi-component identity noted as gap, not promoted |
| AB-AD-7: Adoption friction measured | ✅ PASS — 4 friction points documented |
| AB-AD-8: Adapter requirements classified | ✅ PASS — 3 categories: identity, evidence, sprint history |

---

## Adoption Recommendation

**Recommendation: ADAPT — with one model note.**

The assurance model transfers to execution-shaped projects, but Agent Bridge identifies one genuine model gap: **multi-component project identity** is not currently representable.

### Required Changes

| Change | Effort | Priority |
|--------|--------|----------|
| Add Agent Bridge path mapping to routing auto-detection | Small | Required for Phase 2 |
| Create evidence adapter for docs/ directory sources | Small | Required for evidence freshness |
| Document multi-component identity as model observation | None (observation) | Informational |

### Potential Model Refinement

Agent Bridge raises a question: should the assurance model support multi-component projects? Currently the answer is "not yet" — the adapter layer can flatten components into a single project view. Long-term, a compound identity concept may be needed for projects with distinct server/extension/package boundaries.

---

## Comparison: Librarian vs. Agent Bridge

| Dimension | Librarian | Agent Bridge |
|-----------|-----------|-------------|
| Primary evidence | Governance receipts | Runtime config + extension code |
| Sprint history | Machine-readable (JSON) | Prose (handoff doc) |
| Project shape | Single-component | Multi-component |
| Risk model | None (explicit gap) | None (explicit gap) |
| Finding lifecycle | None (explicit gap) | None (explicit gap) |
| Adapter complexity | Low (format differences) | Medium (structure differences) |
| Model gap identified | None | Multi-component identity |
