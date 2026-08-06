# Agent Bridge Assurance Adoption Baseline — Discovery Findings

**Sprint:** #209 — ASSURANCE-ADOPTION-AGENT-BRIDGE-BASELINE-1
**Date:** 2026-07-21
**Status:** 🔍 Pending Owner review

---

## Primary Question

> Can Agent Bridge express its operational state through the existing assurance model without introducing Agent Bridge-specific assurance semantics?

**Answer:** Yes — with one notable compound-identity gap and operational-state adapters.

---

## Acceptance Gate Results

### AB-AD-1 — Agent Bridge identity mapped

**Result:** ✅ DIRECT (with compound-identity gap flagged)

Agent Bridge has a single `project_id: "agent-bridge"` at Phase 8, lifecycle-cursor.json, PACKAGE-MANIFEST.txt, and standard governance metadata (feature status, session handoff, SEC-1 inheritance). The top-level project identity maps directly to the assurance model.

**Gap flagged:** Agent Bridge is physically three components — server (Node.js HTTP server in `server/`), extension (Chrome extension in `extension/`), and refresh-pack (GitHub packaging in `agent-bridge-github-refresh-pack/`). Each component has its own SEC-1 inheritance declaration. The core assurance model assumes single-component project identity. This is the first time a project has had **compound identity**.

| Component | SEC-1 Inheritance | Authority |
|-----------|------------------|-----------|
| Server (bridge core) | Class A/B/C/E | Non-authoritative transport |
| Extension (browser) | Class A/B/C/E | Intent-only, no authority |
| Refresh pack (packaging) | Not declared | Distribution only |

**Classification:** Adapter needed — compose three scope components into one assurance identity projection. Flagged as model-level gap candidate for Phase 4 (contract decision).

---

### AB-AD-2 — Runtime/integration evidence sources identified

**Result:** ✅ DIRECT for governance evidence, ADAPTER for runtime evidence

Agent Bridge produces 11 distinct evidence source types:

| Source | Shape | Maps to | Classification |
|--------|-------|---------|---------------|
| Intake receipts (AB-3) | JSON with integrity hash, provenance | Evidence intake | DIRECT |
| Receipt validation (AB-4) | 14-point validation rules | Evidence validation | DIRECT |
| Custody artifacts (AB-5) | Formal custody handoff doc | Custody evidence | DIRECT |
| Status reflection (AB-6) | Read-only aggregated status | Operational state | ADAPTER |
| Decision intents (AB-7) | Signed audit trail entries | Decision records | DIRECT |
| Decision review (AB-8) | Read-only viewer payload | Review surface | DIRECT |
| Pairing records (AB-9) | HMAC pairing state | Operational state | ADAPTER |
| Taskbar intents (AB-10) | Signed intent via popup | Decision records | DIRECT |
| Acceptance tests | JS test files with pass counts | Validation outputs | DIRECT |
| SEC-1 declarations | Inheritance docs | Security posture | DIRECT |
| Queue state | Filesystem-based work packets | Operational state | ADAPTER |

**Finding:** 7 of 11 source types map directly. 3 runtime-specific sources (status, pairing, queue) need adapters. 1 (SEC-1) is a unique security form not present in QA Pilot but maps cleanly.

---

### AB-AD-3 — Existing receipts map into evidence lineage

**Result:** ✅ DIRECT (receipt layer), ADAPTER (evidence chain shape differs)

Agent Bridge has a trust chain but it is **flat** rather than layered:

```
Agent Bridge:  receipt → custody → status → intent → review
QA Pilot:      evidence → test → result → epic regression → dashboard
```

Capabilities Agent Bridge has that map directly:
- ✅ Intake receipt generation and validation (AB-3, AB-4)
- ✅ Custody handoff with provenance (AB-5)
- ✅ Decision intent audit trail (AB-7)
- ✅ Read-only decision review (AB-8)
- ✅ Status reflection (AB-6, read-only, paired)

Capabilities Agent Bridge does NOT have (explicit gaps):
- ❌ No test composition layer
- ❌ No result packet layer
- ❌ No epic regression builder
- ❌ No continuous assurance loop
- ❌ No finding lifecycle management
- ❌ No risk prioritization

**Finding:** Receipts map directly. The missing layers are valid absences — Agent Bridge is earlier in its maturity. No adapter needed for the flat structure; the evidence lineage adapter expresses existing receipts while correctly showing missing pipeline layers as gaps.

---

### AB-AD-4 — Ownership boundaries preserved

**Result:** ✅ DIRECT — maps cleaner than QA Pilot's own model

Agent Bridge has explicit non-authoritative declarations at every layer:

| Layer | Declaration | Enforcement |
|-------|------------|-------------|
| Severability | "agent-bridge is intentionally non-authoritative" | Product-level |
| AB-3 intake | `requiresHumanApproval = true` forced | Code-level |
| AB-7 intent | Queue counts unchanged after submission | Code-level (31 tests) |
| AB-8 review | POST/PUT/DELETE → 405 "AB-8 is read-only" | Code-level (248 tests) |
| Extension | No authority fields, no identity exposure | SEC-1 Class E |
| Pairing | Proves identity, does not grant authority | Architecture-level |
| Governing line | "Decision intent ≠ approval" | Documentation-level |

**Finding:** No adapter needed for ownership. Agent Bridge's boundary enforcement is more explicit than QA Pilot's. The core model's ownership concept can reference Agent Bridge as a positive example of boundary hygiene.

---

### AB-AD-5 — Missing assurance capabilities remain visible

**Result:** ✅ DIRECT — model correctly shows absences

Capabilities Agent Bridge does not possess (compared to QA Pilot full pipeline):

| Missing Capability | Impact | Visibility |
|--------------------|--------|------------|
| Continuous assurance loop | No automated evidence → review cycle | Visible as gap |
| Finding lifecycle | No open/review/closed workflow | Visible as gap |
| Multi-layer evidence pipeline | No EP/TC/QR/ERS stores | Visible as gap |
| Epic regression | No cross-sprint regression builder | Visible as gap |
| Risk prioritization | No risk scoring system | Visible as gap |
| Owner dashboard | No governance surface | Visible as gap |
| Drift detection | No consistency checker | Visible as gap |

**Finding:** Every missing capability is correctly representable as an absence in the assurance model. No adapter needed — the model's gap-handling is working as designed.

---

### AB-AD-6 — No Agent Bridge concepts promoted into core model prematurely

**Result:** ✅ COMPLIANT — no promotion required; one model gap flagged for future

| Agent Bridge-specific Concept | Should Promote? | Reasoning |
|------------------------------|----------------|-----------|
| Compound project identity (3 components) | ⏸️ **Flagged — do not promote yet** | Genuine model gap, but defer to Phase 4 contract decision |
| HMAC pairing-based identity | ❌ No | Bridge-specific security pattern |
| Non-authoritative intent channels | ❌ No | Agent Bridge design choice |
| Extension-visible vs internal state | ❌ No | Chrome extension context |
| SEC-1 class inheritance model | ❌ No | Already covered by Librarian security model |

**Finding:** Complete compliance. The compound identity gap is the only model-level observation — it should be documented in the model gap log but not acted upon until at least Phase 4.

---

### AB-AD-7 — Adoption friction measured

**Result:** ✅ FRICTION MEASURED — low-to-medium overall

| Friction | Severity | Source | Resolution Path |
|----------|----------|--------|----------------|
| Compound project identity | **MEDIUM** | 3 physical components under 1 project_id | Adapter: compose from PACKAGE-MANIFEST.txt and SEC-1 declarations |
| No machine-readable sprint history | LOW | Prose-only in SESSION-HANDOFF.md | Accept as-is; structured not required for baseline |
| Flat vs layered evidence chain | LOW | No multi-layer pipeline | Accept divergence; adapter handles shape difference |
| Runtime state (queue, pairing) | LOW | Filesystem state, not persisted docs | Adapter: read live endpoints for snapshot |
| Test format divergence | LOW | JS tests, not structured fixtures | Accept as-is; pass counts are extractable |
| No lifecycle cursor sprint history | LOW | prose-only, no structured ledger | Accept for Phase 2; re-evaluate if adapter built |

**Overall friction:** Low (4/6 items) to Medium (1/6 — compound identity). Agent Bridge adoption is significantly less frictional than expected for the first execution-shaped project.

---

### AB-AD-8 — Adapter requirements classified

**Result:** ✅ CLASSIFIED — 3 adapter types, 4 direct mappings, 1 explicit gap

| Assurance Surface | Classification | Adapter Complexity | Notes |
|-------------------|---------------|-------------------|-------|
| Project identity | **ADAPTER** (compound compose) | Medium | Compose 3 components from PACKAGE-MANIFEST + SEC-1 inheritance per component |
| Evidence lineage — receipts | DIRECT | None | JSON receipts with integrity hashes map as-is |
| Evidence lineage — runtime | **ADAPTER** (state snapshot) | Low | Poll `/api/status`, read queue directory, render as operational evidence |
| Ownership boundaries | DIRECT | None | Maps cleaner than QA Pilot; use as reference |
| Governance records | DIRECT | None | Decision receipts, audit trail, lifecycle events |
| Missing capabilities | GAP (explicit) | None | Model handles absences correctly |
| Risk signals | **ADAPTER** (from test failures) | Low | Failed validations (8 invalid fixtures in tests/fixtures/) map to risk signals |

**Adapter summary:** 3 adapters needed: (1) compound identity composition, (2) runtime state snapshot, (3) risk signal from test failures. All low-to-medium complexity. Compare with Librarian adoption (0 adapters, all direct mapping except operational state projection).

---

## Cross-Cutting Findings

### What transfers cleanly
- Receipt-based evidence (AB-3/4/5 maps to EP-*)
- Decision records (AB-7/8 maps to Owner decision receipts)
- Security posture (SEC-1 maps to governance profile)
- Non-authoritative design (maps to assurance principle)

### What needs adapters
- **Compound identity** — 3-component project needs composition layer
- **Runtime state** — queue/pairing/status is live state, not persisted evidence
- **Test outputs** — JS tests need structured wrapper for pipeline consumption

### What is genuinely absent (explicit gaps)
- Pipeline layers (test composition, result packets, epic regression)
- Continuous assurance loop
- Finding lifecycle
- Risk classification system

### Model-level gap (not Agent Bridge-specific)
**Compound project identity** — The core assurance model assumes project = single entity. Agent Bridge (server + extension + refresh pack) and potentially Runtime Node (node + agent + authority) suggest this is a general limitation, not a project-specific one. Flagged for Phase 4 contract discussion.

---

## Recommendation

**ADAPT** — proceed with adapter construction at appropriate phase.

The model transfers to execution-shaped projects with low-medium friction. The compound identity finding is the most significant model-level observation — it affects how identity is projected, not whether the model works.

Librarian comparison:
| Dimension | Librarian (Phase 1) | Agent Bridge (Phase 2) |
|-----------|-------------------|----------------------|
| Direct mapping | 5/7 concepts | 4/7 concepts |
| Adapters needed | 1 (operational state projection) | 3 (identity compose + runtime state + risk signals) |
| Model gaps found | 0 | 1 (compound identity) |
| Adoption friction | LOW | LOW-MEDIUM |
| Recommendation | ADAPT | ADAPT |

---

*Report produced under Sprint #209 — ASSURANCE-ADOPTION-AGENT-BRIDGE-BASELINE-1*
*🔍 Pending Owner review*
