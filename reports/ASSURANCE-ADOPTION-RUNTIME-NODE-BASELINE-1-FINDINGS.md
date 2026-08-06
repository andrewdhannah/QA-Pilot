# Runtime Node Assurance Adoption Baseline — Discovery Findings

**Sprint:** #210 — ASSURANCE-ADOPTION-RUNTIME-NODE-BASELINE-1
**Date:** 2026-07-21
**Status:** 🔍 Pending Owner review

---

## Primary Question

> Can Runtime Node express operational reality through the assurance model without creating runtime-specific assurance semantics?

**Answer:** Yes — with one critical distinction the model must preserve: **artifact evidence** vs **runtime evidence**.

---

## Acceptance Gate Results

### RN-AD-1 — Runtime Node identity mapped

**Result:** ✅ DIRECT — single identity, compound repo dependency

Runtime Node has `project_id: "runtime-node"`, lifecycle cursor at Phase 8, 25 sealed sprints, standard project infrastructure (README, FEATURE-STATUS.md, SESSION-HANDOFF.md).

**Notable:** Runtime Node depends on a companion repo (`TheLibrarian-main`) for integration receipts and verifiers. The v2 receipt schema lives in the companion repo, not in this repo. This is a **cross-repo dependency pattern** — runtime-node generates evidence, TheLibrarian-main validates it.

| Identity Component | Source | Assurance Mapping |
|--------------------|--------|-------------------|
| `project_id` | lifecycle-cursor.json | DIRECT |
| Sprint history | 25 lifecycle events | DIRECT |
| Companion dependency | TheLibrarian-main (receipt schema) | Adapter note — cross-repo evidence verification |
| Platform identity | Windows x86_64, PowerShell, Rust/Python | New dimension — platform-specific assurance |

**Classification:** DIRECT mapping. Cross-repo dependency is different from compound identity (Agent Bridge) — this is a distributed evidence verification pattern, not a multi-component project.

---

### RN-AD-2 — Runtime evidence sources identified

**Result:** ✅ DIRECT (6 types), NEW CATEGORY (artifact vs runtime distinction)

Runtime Node produces 12 distinct evidence source types — 3 of them introduce a new evidence category not seen in prior consumers:

| Source | Shape | Maps to | Classification |
|--------|-------|---------|---------------|
| Integration receipts (v2) | JSON with artifact SHA-256, provenance, timestamps | Evidence intake | DIRECT |
| Qualification records | Rebuild hash comparison, gate results, build metadata | Evidence intake | DIRECT |
| Health measurements | Per-profile health, overall status, uptime | Operational state | **NEW — runtime evidence** |
| Model fit evidence | JSON fixtures capturing context/ngl verification | Validation outputs | DIRECT |
| Process lifecycle | start→select→healthy→chat→stop→shutdown lifecycle | Operational state | **NEW — runtime evidence** |
| Refusal conditions | 7 structured 403 responses | Security posture | DIRECT |
| Endpoint fixtures | 17 JSON fixtures capturing router state | Test evidence | DIRECT |
| Build metadata | cargo version, rustc, target triple, build duration | Build provenance | DIRECT |
| Orphan/port cleanup state | Process list, port availability, service state | Operational evidence | **NEW — runtime evidence** |
| Contract tests | ROUTER-HTTP-CONTRACT.md with 12 invariants | Contract evidence | DIRECT |
| Network boundary proof | 127.0.0.1 binding, auth token policy | Security posture | DIRECT |
| SEC-1 inheritance | 3 trust boundaries, 28/1/0 review | Security posture | DIRECT |

**Finding:** 9 of 12 map directly. 3 introduce a genuinely new category — **runtime evidence** (transient, current-state measurements). This is the first consumer where the artifact/runtime distinction is forced.

---

### RN-AD-3 — Qualification records map to evidence lineage

**Result:** ✅ DIRECT — qualification records are the cleanest evidence lineage in any consumer

The Runtime Node qualification proof chain is a model of clean evidence lineage:

```
Step 1: Source HEAD proof     → e7cfe33 (runtime-node), 1e32002 (main)
Step 2: Artifact hash proof   → SHA-256 84EB797A...
Step 3: Governed rebuild      → Rebuild hash matches receipt; 38/38 gate passed
```

Qualification records capture:
- Source HEAD, toolchain versions, build metadata
- Receipt artifact hash vs rebuilt artifact hash
- Honest match/mismatch recording (no forced pass)
- Verifier gate: 48 checks including structure, hash format, cross-validation

**Gap noted:** The v2 receipt schema lives in `TheLibrarian-main`, not in the runtime-node repo. Evidence lineage crosses repository boundaries — the assurance adapter must know where to find the companion's schema and receipts.

| Feature | Maps to Assurance |
|---------|-------------------|
| Rebuild from known source HEAD | Evidence provenance |
| Artifact hash comparison | Integrity verification |
| Gate checks (38/38 passed) | Validation result |
| Honest mismatch recording | Core principle: absence is valid info |
| Cross-repo schema dependency | Adapter concern |

---

### RN-AD-4 — Hardware/runtime state represented without distortion

**Result:** ✅ REPRESENTED — but the model needs a new concept for **runtime evidence**

This is the most significant finding of Phase 3.

Runtime Node produces evidence in two fundamentally different categories:

```
ARTIFACT evidence (durable, historical):
  "this was validated"
  - Qualification record: binary hash matched on 2026-06-22
  - Integration receipt: 38/38 gate passed
  - Model profile: verified at ngl=80, context=4096

RUNTIME evidence (transient, current-state):
  "this is true now"
  - Health check: backend healthy/degraded/failed
  - Port 9130: free/occupied
  - Process state: running/stopped/orphaned
  - Service status: Running/Stopped
```

The current assurance model has no category for runtime evidence. Every prior consumer (QA Pilot, Librarian, Agent Bridge) produced artifact evidence exclusively — receipts, documents, fixtures, test outputs. Runtime Node introduces ephemeral operational measurements.

**Critical rule:** Runtime evidence must NOT overwrite artifact evidence, and artifact evidence must NOT imply current operational state.

| Scenario | Correct Behavior | Wrong Behavior |
|----------|-----------------|----------------|
| Qualification passed; service stopped | Show both: ✅ validated, ❌ not running | Hide qualification or imply service is healthy |
| Health degraded; qualification still valid | Show both: ❌ degraded, ✅ qualification record | Overwrite qualification with degraded |
| Port free; no current runtime | Show: ✅ port free, no runtime active | Infer readiness from port status |

**Classification:** ADAPTER needed — a runtime evidence adapter that:
1. Preserves artifact evidence as immutable history
2. Renders runtime evidence as snapshot (timestamped, transient, non-overwriting)
3. Never conflates "was validated" with "is running"

---

### RN-AD-5 — Operational vs validated state remains distinct

**Result:** ✅ DISTINCT — Runtime Node's own architecture enforces this separation

Runtime Node's infrastructure already makes this distinction naturally:
- **Receipts** = validated/documented (in `receipts/`)
- **Health/status endpoints** = operational (GET `/backend/health`, GET `/backend/status`)
- **Service state** = current (Stopped/Manual)
- **Process state** = transient (checked at runtime, not persisted)

The assurance model must mirror this separation. A single "assurance state" concept that conflates both would lose information.

**Design recommendation for Phase 4:** The contract extraction should define:
- `assurance_record` — durable, historical, tamper-evident (what exists today)
- `assurance_snapshot` — transient, current-state, timestamped (new concept from Phase 3)

---

### RN-AD-6 — Transient runtime conditions do not corrupt assurance history

**Result:** ✅ SAFE — no mechanism exists to corrupt history, but the model must be explicit

Current state: Runtime Node's qualification records, integration receipts, and proof chain are all emitted as files in `receipts/`. They are write-once, not overwritten. There is no mechanism for a health check failure to modify a qualification record.

However, the assurance model currently has no guard against a future implementation conflating the two. Phase 4 contract extraction should formalize:

1. **Write-time separation** — Different storage paths/schemas for records vs snapshots
2. **Read-time separation** — Assurance projection must source from both and label each
3. **No overwrite rule** — A runtime observation must never modify an artifact record

---

### RN-AD-7 — Missing runtime capabilities remain visible

**Result:** ✅ DIRECT — model handles absences correctly

Capabilities Runtime Node does not possess:

| Missing Capability | Impact | Visible? |
|--------------------|--------|----------|
| Continuous assurance loop | No automated evidence → review cycle | ✅ Visible as gap |
| Finding lifecycle | No open/review/closed workflow | ✅ Visible as gap |
| Multi-project dashboard | No governance surface | ✅ Visible as gap |
| Risk classification | No risk scoring system | ✅ Visible as gap |
| Structured sprint ledger | Sprints array empty in ledger JSON | ✅ Visible as gap |
| Machine-readable evidence pipeline | No EP/TC/QR/ERS stores | ✅ Visible as gap |

**Finding:** Same pattern as Agent Bridge. All absences are correctly representable.

---

### RN-AD-8 — Runtime-specific concepts classified as adapter vs core candidates

**Result:** ✅ CLASSIFIED — 1 new core concept flagged, 4 adapter concerns

| Concept | Classification | Rationale |
|---------|---------------|-----------|
| **Artifact vs runtime evidence distinction** | **CORE CANDIDATE** | This distinction survived 3 consumer shapes. QA Pilot's pipeline evidence = artifact. Librarian's receipts = artifact. Agent Bridge's intents = artifact. Runtime Node's health/state = runtime. This dichotomy is universal — it should be standardized at the contract layer. |
| Cross-repo evidence verification | ADAPTER | Companion repo dependency is a topology choice, not an assurance property |
| Windows-specific process management | ADAPTER | Platform-specific operational detail |
| Hardware qualification (GPU memory) | ADAPTER | Environment-specific measurement |
| Service lifecycle (Manual/Stopped) | ADAPTER | Deployment policy, not assurance |

**Recommendation:** The artifact/runtime distinction is the strongest candidate for core model expansion from any Phase 1-3 consumer. It is the only concept that:
1. Survived all 3 consumer shapes
2. Would have been invisible without Phase 3
3. Is a universal property of any project with both historical records and live operations

---

### RN-AD-9 — Adoption friction measured

**Result:** ✅ LOW — lower than Agent Bridge

| Friction | Severity | Source |
|----------|----------|--------|
| Artifact vs runtime evidence category missing | **MEDIUM** | Model gap — affects assurance projection format |
| Cross-repo schema dependency | LOW | Verification schema lives in TheLibrarian-main repo |
| No structured sprint ledger | LOW | Sprints array empty in ledger JSON |
| Platform-specific paths | LOW | Windows paths (G:\\), PowerShell scripts |
| Pipeline layers absent (same as Phase 2) | LOW | Expected for infrastructure project |

**Overall friction:** LOW (4/5 items). The runtime evidence category is the only medium-severity item, and it's a genuine model gap that Phase 3 was designed to find.

**Comparison across all consumers:**

| Consumer | Friction | New Model Insights |
|----------|----------|-------------------|
| QA Pilot | Baseline | — |
| Librarian | LOW | Confidence: model generalizes beyond its origin |
| Agent Bridge | LOW-MEDIUM | Compound identity gap; adapter classification needed |
| Runtime Node | LOW | **Artifact vs runtime evidence** — the strongest contract extraction signal yet |

---

### RN-AD-10 — Contract implications recorded for Phase 4

**Result:** ✅ RECORDED — 3 contract implications

---

## Cross-Cutting Finding: The Artifact/Runtime Dichotomy

This is the most important finding of the entire adoption epic. Every prior consumer produced **artifact evidence** exclusively. Runtime Node is the first to produce both:

```
┌─────────────────────────────────────────────────┐
│                 Evidence Universe               │
├─────────────────────┬───────────────────────────┤
│   ARTIFACT Evidence │   RUNTIME Evidence         │
│   (durable, past)   │   (transient, current)     │
├─────────────────────┼───────────────────────────┤
│ Receipts            │ Health check results       │
│ Qualification recs  │ Port availability          │
│ Proof chain         │ Process state              │
│ Sprint closeouts    │ Service status             │
│ Test fixtures       │ Orphan detection           │
│ Contracts           │ Uptime measurements        │
├─────────────────────┼───────────────────────────┤
│ "this was validated"│ "this is true now"         │
│ Immutable           │ Ephemeral                  │
│ Tamper-evident      │ Timestamp-sensitive        │
│ Replayable          │ Non-replayable             │
└─────────────────────┴───────────────────────────┘
```

This distinction must be standardized at the contract layer. Without it:
- A stale qualification record could be mistaken for current operational readiness
- A transient health failure could be read as permanent capability loss
- The assurance projection would be a single value with no temporal dimension

---

## Phase 4 Contract Implications

Three findings ready for Phase 4 contract extraction:

### 1. Artifact/Runtime Evidence Distinction (Strongest Signal)
The model needs two evidence classes: `assurance_record` (historical) and `assurance_snapshot` (current). All 3 consumers produce records; only Runtime Node produces both. This is the right time to standardize.

### 2. Absence is Valid Information (Confirmed across all 3 adopters)
Every consumer demonstrated: missing capabilities are not failures. The model handles gaps correctly. This principle should be formalized in the contract.

### 3. Adapter Boundary Pattern (Converged)
All 3 adopters revealed the same pattern:
- Governance concepts map directly
- Project-specific operational mechanics go in adapters
- Compound/identity topology issues are rare (1 of 3 consumers)

This pattern should become the standard onboarding template.

---

## Adoption Epic Evidence Summary

| Consumer | Shape | Key Finding | Recommendation | Status |
|----------|-------|-------------|---------------|--------|
| QA Pilot | Full lifecycle | Baseline implementation | — | ✅ |
| Librarian | Governance/doc | Direct portability (5/7) | ADAPT | ✅ SEALED #207 |
| Agent Bridge | Runtime/integration | Operational portability (compound identity gap) | ADAPT | ✅ SEALED #209 |
| **Runtime Node** | **Hardware/operational** | **Artifact vs runtime evidence distinction** | **ADAPT + model note** | **🔍 PENDING** |

---

*Report produced under Sprint #210 — ASSURANCE-ADOPTION-RUNTIME-NODE-BASELINE-1*
*🔍 Pending Owner review*
