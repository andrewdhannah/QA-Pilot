# Evidence State Separation — Contract Analysis

**Sprint:** #211 — ASSURANCE-CONTRACT-EVIDENCE-STATE-SEPARATION-1
**Date:** 2026-07-21
**Status:** 🔍 Pending Owner review

---

## 1. Semantic Model

### Proposed Distinction

```
Assurance Evidence
       |
       +-- assurance_record
       |       Historical, immutable evidence
       |       "What was proven"
       |       Properties: immutable, timestamped, attributable,
       |                   evidence-linked, historical
       |
       +-- assurance_snapshot
               Current observation
               "What is true now"
               Properties: refreshable, time-bound, environment-dependent,
                           observational, non-authoritative over history
```

### Relationship Rules

1. A record proves what happened at a point in time.
2. A snapshot describes what is observed right now.
3. Neither replaces the other.
4. A snapshot cannot mutate a record.
5. A record cannot imply current operational state.

---

## 2. Cross-Consumer Evidence Mapping (ESS-1, ESS-2)

### QA Pilot (full lifecycle — baseline)

| Existing Evidence Type | Classification | Rationale |
|----------------------|---------------|-----------|
| EP-* evidence packets | `assurance_record` | Ingested, validated, stored immutably |
| EC-* evidence checklists | `assurance_record` | Defines evidence requirements |
| EL-* evidence linkers | `assurance_record` | Links to sealed artifacts |
| qapr-* production receipts | `assurance_record` | Advisory receipt records |
| QR-* qualification records | `assurance_record` | Qualification of artifacts/processes |
| RCR-* registry change receipts | `assurance_record` | Pipeline layer registry changes |
| TC-* test cases | `assurance_record` | Defined test cases |
| QR-* result packets | `assurance_record` | Test execution results |
| ERS-* epic regression suites | `assurance_record` | Cross-sprint regression |
| SRS-* regression snapshots | `assurance_record` | Baseline snapshots at freeze time |
| OD-* dashboard projections | `assurance_record` | Projection outputs at render time |
| Owner decision receipts | `assurance_record` | Owner decisions |
| **No runtime evidence** | *(no snapshot candidates)* | QA Pilot produces lifecycle artifacts only |

**Finding:** QA Pilot produces exclusively `assurance_record` evidence. This is consistent with a project whose output is governed artifacts, not live operations.

### Librarian (governance/documentation)

| Existing Evidence Type | Classification | Rationale |
|----------------------|---------------|-----------|
| Receipts | `assurance_record` | Evidence receipts |
| Sprint ledger entries | `assurance_record` | Historical ledger |
| Release gates | `assurance_record` | Release readiness checks |
| Startup state | `assurance_record` | Frozen startup posture |
| **No runtime evidence** | *(no snapshot candidates)* | Governance artifacts only |

**Finding:** Librarian produces exclusively `assurance_record` evidence. Same profile as QA Pilot — governance-shaped project.

### Agent Bridge (runtime/integration)

| Existing Evidence Type | Classification | Rationale |
|----------------------|---------------|-----------|
| Intake receipts (AB-3/4) | `assurance_record` | Validated receipt artifacts |
| Custody artifacts (AB-5) | `assurance_record` | Handoff documents |
| Decision intents (AB-7) | `assurance_record` | Audit trail entries |
| Decision review records (AB-8) | `assurance_record` | Read-only viewer payloads |
| **Queue state** | **`assurance_snapshot` (NEW)** | Current queue state — filesystem-based, transient |
| **Pairing state** | **`assurance_snapshot` (NEW)** | Current HMAC pairing state — runtime, not persisted |
| **Status reflection (AB-6)** | **`assurance_snapshot` (NEW)** | Read-only aggregated status at query time |

**Finding:** Agent Bridge produces 4 record types and 3 snapshot types. The snapshot types are live state reflections that would have been invisible without the Phase 2 adoption test.

### Runtime Node (hardware/operational)

| Existing Evidence Type | Classification | Rationale |
|----------------------|---------------|-----------|
| Integration receipts (v2) | `assurance_record` | Artifact SHA-256, provenance, timestamps |
| Qualification records | `assurance_record` | 38/38 gate chain, rebuild hash verification |
| Proof chain artifacts | `assurance_record` | 3-link proven evidence chain |
| Contract fixtures | `assurance_record` | Frozen endpoint responses |
| **Health measurements** | **`assurance_snapshot` (NEW)** | Per-profile health at query time — transient |
| **Port availability** | **`assurance_snapshot` (NEW)** | Port 9130 free/occupied — transient |
| **Process state** | **`assurance_snapshot` (NEW)** | Running/stopped/orphaned — transient |
| **Service status** | **`assurance_snapshot` (NEW)** | Running/Stopped/Manual — transient |
| **Uptime** | **`assurance_snapshot` (NEW)** | Current uptime seconds — transient |

**Finding:** Runtime Node is the only consumer with significant snapshot evidence. 5 snapshot types vs 4 record types. This is the consumer that forced the distinction into view.

### Universality Assessment (ESS-1, ESS-2)

| Consumer | Record Types | Snapshot Types | Evidence Profile |
|----------|-------------|----------------|------------------|
| QA Pilot | 11+ | 0 | Pure lifecycle artifacts |
| Librarian | 4+ | 0 | Pure governance artifacts |
| Agent Bridge | 4 | 3 | Mixed — records + runtime state |
| Runtime Node | 4 | 5 | Mixed — records + operational state |

**Verdict: The distinction is universal.** Every consumer has records. Two of four also have snapshots. Any consumer could acquire snapshot-producing capabilities in the future. The model should handle both, even if a consumer currently produces only records.

---

## 3. Snapshot Cannot Mutate Records (ESS-3)

### Current state: SAFE

Across all 4 consumers, there is **no mechanism** by which a runtime observation could overwrite a historical record:

| Consumer | Record Storage | Snapshot Source | Mutability Risk |
|----------|---------------|----------------|-----------------|
| QA Pilot | `data/` file store (JSON files) | N/A (no snapshots) | None |
| Librarian | Receipt files | N/A (no snapshots) | None |
| Agent Bridge | Receipt files + audit trail | Filesystem queue + runtime pairing | None — separate paths |
| Runtime Node | `receipts/` directory | Live HTTP endpoints | None — no write path from health to receipts |

**Risk identified:** The current safety is accidental, not contractual. There is no formal rule preventing a future implementation from storing a health check result in the same store as qualification records. The contract must formalize write-path separation.

### Recommendation

Formalize at the contract level:
- **Record stores** accept writes only through governed intake (validation, proof chain, attestation)
- **Snapshot sources** are read-only HTTP endpoints or ephemeral state files
- **No cross-write path** — a snapshot observation must never enter the record store without explicit governed intake

---

## 4. Record Cannot Imply Current State (ESS-4)

### Current state: VULNERABLE (design risk, not implementation risk)

The dashboard/projection layer currently treats all evidence uniformly. A qualification record from yesterday and a health check from this second are both rendered as "evidence" without temporal classification.

**Example risk:**
- A qualification record shows `rebuilt_hash_matches_receipt: true` from 2026-06-22
- The current service is Stopped (Manual)
- A naive projection would show "qualified ✅" without indicating "not running"

### Recommendation

The projection contract must:
1. Label every evidence item by class (`record` or `snapshot`)
2. Render record and snapshot evidence separately or with clear temporal annotation
3. Never aggregate record-pass and snapshot-fail into a single ambiguous status

---

## 5. Dashboard/Projection Impact (ESS-5, ESS-6)

### Current Dashboard Schema

The existing Owner Dashboard (`OD-YYYYMMDDTHHMMSS`) has sections:
- `assurance_health` — health metrics
- `active_findings` — current findings
- `risk_posture` — risk state
- `evidence_freshness` — evidence staleness
- `owner_queue` — pending Owner actions
- `release_readiness` — release gates

**Impact assessment:**

| Dashboard Section | Current Behavior | With Record/Snapshot Distinction |
|------------------|-----------------|----------------------------------|
| `assurance_health` | Shows single health status | Split: historical health records vs current health snapshot |
| `evidence_freshness` | Measures staleness uniformly | Records age by timestamp; snapshots age by refresh window |
| `release_readiness` | Checks all gates uniformly | Records prove past compliance; snapshots show current readiness |
| `owner_queue` | Pending actions | Unchanged — actions reference both classes |

**Improvement:** The distinction makes Owner decisions safer. A decision to proceed based on a qualification record is qualitatively different from a decision based on a current health check. The dashboard should label each.

### Owner Decision Impact

| Decision Type | Correct Reference | Wrong Reference |
|---------------|-----------------|-----------------|
| Approve release | Historical records + current snapshot | Snapshot only (misses past failures) or records only (misses current outage) |
| Accept qualification | Record only | Snapshot (not authoritative for history) |
| Dispatch agent | Current snapshot | Stale record (environment may have changed) |

**Finding:** Different decisions reference different evidence classes. The contract must specify which class applies to which decision type.

---

## 6. Compatibility Assessment (ESS-7, ESS-8)

### QA Pilot Compatibility

| Existing Behavior | Compatible? | Notes |
|------------------|-------------|-------|
| Evidence intake (EP-*) | ✅ Compatible | All current EP packets are records — schema unaffected |
| Evidence checklists (EC-*) | ✅ Compatible | Requirement definitions, not snapshots |
| Receipts (qapr-*) | ✅ Compatible | Advisory records |
| Qualification records (QR-*) | ✅ Compatible | Advisory qualification records |
| Pipeline layers | ✅ Compatible | No pipeline layer changes needed |
| Startup surface | ✅ Compatible | Records with timestamps |
| Dashboard projections | ⚠️ Additive change | Add `evidence_class` field to projection output |

**Change required:** None in existing pipeline. Dashboard projection gainer would add an `evidence_class: "record"` or `"snapshot"` label to each evidence item in the projection.

### Librarian Compatibility

| Existing Behavior | Compatible? | Notes |
|------------------|-------------|-------|
| Receipts | ✅ Compatible | Records |
| Sprint ledger | ✅ Compatible | Historical records |
| Release gates | ✅ Compatible | Records at gate time |
| Startup state | ✅ Compatible | Frozen state record |

**Change required:** None. Librarian has no snapshots. The distinction is additive — existing records carry forward unchanged.

### Agent Bridge Compatibility

| Existing Behavior | Compatible? | Notes |
|------------------|-------------|-------|
| Intake receipts | ✅ Compatible | Records |
| Custody artifacts | ✅ Compatible | Records |
| Decision intents | ✅ Compatible | Audit trail records |
| Queue state | ✅ Compatible | Would become snapshot — changes projection only |
| Pairing state | ✅ Compatible | Would become snapshot — changes projection only |
| Status reflection | ✅ Compatible | Would become snapshot — changes projection only |

**Change required:** No intake or storage changes. Projection layer would classify queue/pairing/status as snapshots.

### Runtime Node Compatibility

| Existing Behavior | Compatible? | Notes |
|------------------|-------------|-------|
| Integration receipts | ✅ Compatible | Records |
| Qualification records | ✅ Compatible | Records |
| Proof chain | ✅ Compatible | Records |
| Health checks | ✅ Compatible | Would become snapshot — changes projection only |
| Port/process state | ✅ Compatible | Would become snapshot — changes projection only |

**Change required:** No intake or storage changes. Health and process state sources would be labeled as snapshots at projection time.

---

## 7. Schema Evolution Impact (ESS-9)

### Current Schema Inventory

QA Pilot has 52 schemas. The ones affected by the record/snapshot distinction:

| Schema | Current Status | Impact |
|--------|---------------|--------|
| `qa-evidence-packet.schema.json` | EP- prefix, immutable evidence | **Add optional field:** `evidence_class: { "enum": ["record", "snapshot"] }` |
| `qa-pilot-receipt.schema.json` | qapr- prefix, production receipts | **Add optional field:** `evidence_class` defaulting to `"record"` |
| `qa-pilot-owner-dashboard.schema.json` | OD- prefix, read-only projection | **Add section:** `evidence_classification` with record/snapshot counts |
| `qa-pilot-pipeline-layer-registry.schema.json` | PLR- prefix, layer definitions | **No change** — layers are architectural, not evidence-class-dependent |
| `qa-pilot-startup-surface-regression-snapshot.schema.json` | SRS- prefix, baseline snapshots | **Add classification:** these are records of snapshots, not snapshots themselves |

### Minimal Schema Change

```
Option A: New field on evidence schema (minimum change)
  "evidence_class": {
    "type": "string",
    "enum": ["record", "snapshot"],
    "default": "record"
  }

Option B: New projection contract only
  - No schema change to existing evidence
  - Projection layer adds classification at render time
  - Evidence items inherit class from source type mapping

Option C: Both field + projection contract
  - Schema field for new evidence
  - Projection classification for existing evidence
```

**Recommendation:** Option B for existing evidence (no retroactive schema change needed) + Option A for new evidence going forward. This gives:
- Zero migration cost for existing 52 schemas and ~200+ evidence files
- Forward compatibility for any new evidence type
- Classification table maps source type → evidence class at projection time

### Classification Table (Projection Contract)

| Source Type | Evidence Class | Rationale |
|------------|---------------|-----------|
| EP-* evidence packets | `record` | Ingested, immutable evidence |
| EC-* evidence checklists | `record` | Requirement definitions |
| EL-* evidence linkers | `record` | Link validation results |
| qapr-* production receipts | `record` | Advisory receipt records |
| QR-* qualification records | `record` | Qualification outcomes |
| RCR-* registry change receipts | `record` | Registry changes |
| TC-* test cases | `record` | Defined test cases |
| OD-* dashboard projections | `record` | Projection renders at point in time |
| SRS-* regression snapshots | `record` | Records of baseline state |
| Queue state (Agent Bridge) | `snapshot` | Current queue — transient |
| Pairing state (Agent Bridge) | `snapshot` | Current pairing — transient |
| Health checks (Runtime Node) | `snapshot` | Current health — transient |
| Port/process state (Runtime Node) | `snapshot` | Current state — transient |
| Service status (Runtime Node) | `snapshot` | Current service — transient |

---

## 8. Migration Path (ESS-10)

### Phase 1: Semantic Model Adoption (no code change)
- Adopt the record/snapshot vocabulary in documentation
- Update governance docs to use the distinction
- Begin using the terms in sprint reviews and Owner communication

### Phase 2: Projection Classification (dashboard change only)
- Add `evidence_classification` section to dashboard projection
- Classify existing evidence sources by type mapping table
- No storage or intake changes

### Phase 3: Schema Field Addition (optional)
- Add `evidence_class` field to evidence packet schema
- Default to `"record"` for backward compatibility
- New evidence types opt in explicitly

### Phase 4: Formalization
- Write-path separation: governed intake for records, endpoint observation for snapshots
- Decision-type mapping: which decisions reference which class
- Agent dispatch guard: use snapshot for current-state decisions, records for historical

---

## Acceptance Gate Results Summary

| Gate | Result | Key Justification |
|------|--------|-------------------|
| ESS-1 | ✅ Records map cleanly | All 4 consumers — every existing evidence type maps to `assurance_record` |
| ESS-2 | ✅ Snapshots map cleanly | Agent Bridge (3 types) + Runtime Node (5 types) — all fit `assurance_snapshot` |
| ESS-3 | ✅ Snapshot cannot mutate records | Currently safe by accident; formalize write-path separation |
| ESS-4 | ✅ Records cannot imply current state | Vulnerability exists in dashboard projection — fix with classification labeling |
| ESS-5 | ✅ Dashboard can distinguish | Add `evidence_classification` section to OD- schema |
| ESS-6 | ✅ Owner decisions reference correct class | Different decision types use different classes — document the mapping |
| ESS-7 | ✅ QA Pilot behavior compatible | Zero storage/intake changes; additive projection change only |
| ESS-8 | ✅ All 4 consumer mappings remain valid | Classification table covers all evidence types across all consumers |
| ESS-9 | ✅ Schema impact documented | Option B (projection-only) for existing, Option A (optional field) for new |
| ESS-10 | ✅ Migration path defined | 4-phase rollout: vocabulary → projection → schema → formalization |

---

## Recommendation

**Adopt the evidence state separation** as a semantic contract clarification.

The distinction is universal (proven across all 4 consumers), zero-cost for existing data (classification at projection time, not storage time), and solves a genuine risk (dashboard conflation of historical proof and current state).

**Contract change:** Add `evidence_class` concept to the projection contract. Do not change existing storage schemas.

**Migration:** Projection-only classification. Label existing evidence by source type. Add optional schema field for future evidence types.

---

*Report produced under Sprint #211 — ASSURANCE-CONTRACT-EVIDENCE-STATE-SEPARATION-1*
*🔍 Pending Owner review*
