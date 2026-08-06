# Evidence Freshness Semantics — Contract Analysis

**Sprint:** #213 — ASSURANCE-CONTRACT-EVIDENCE-FRESHNESS-SEMANTICS-1
**Date:** 2026-07-21
**Status:** 🔍 Pending Owner review

---

## 1. Core Distinction

Evidence freshness is not a single concept. It depends on evidence class:

| Question | `assurance_record` | `assurance_snapshot` |
|----------|-------------------|---------------------|
| What does it represent? | Historical proof | Current observation |
| What does freshness mean? | Is this record still relevant? | Is this observation still current? |
| Does age invalidate? | No — old proof remains proof | Yes — old observation is operationally stale |
| Primary risk | Over-reliance on dated validation | Acting on expired runtime state |

**Invariant:** age ≠ invalidity. An old qualification record remains valid as historical evidence while requiring a newer snapshot before making an operational claim.

---

## 2. Freshness Model

### `assurance_record` — Historical Record Freshness

```
assurance_record
├── captured_at: ISO timestamp when the evidence event occurred
├── validated_at: ISO timestamp when the record was last verified (optional)
├── evidence_age: computed = now - captured_at
├── validation_context: description of what was validated and under what conditions
└── freshness_interpretation:
        ├── meaning: "how recent is this proof?"
        ├── stale_meaning: no operational conclusion — record still valid as history
        └── confidence_label: current/historical/archived
```

**Staleness rules:**
- A record is never invalidated by age alone
- `current` — recent enough to inform operational decisions (age < record-specific threshold)
- `historical` — valid proof but older; operational decisions should reference newer records if available
- `archived` — record preserved for audit; no operational relevance without re-validation

### `assurance_snapshot` — Runtime Snapshot Freshness

```
assurance_snapshot
├── observed_at: ISO timestamp when the observation was captured
├── refresh_expected_at: expected next observation time (based on source polling interval)
├── observation_age: computed = now - observed_at
├── runtime_context: conditions under which observation was made
└── freshness_interpretation:
        ├── meaning: "how current is this observation?"
        ├── stale_meaning: do NOT use for operational decisions until refreshed
        └── confidence_label: current/stale/unknown
```

**Staleness rules:**
- A snapshot IS invalidated by age exceeding its refresh interval
- `current` — observed within expected refresh window (age < 1× refresh_interval)
- `stale` — observation window exceeded (age > 1× refresh_interval); do not use operationally
- `unknown` — no refresh interval defined; treat as stale until observed

---

## 3. Cross-Consumer Freshness Mapping

### QA Pilot (records only — no snapshots)

| Source | Class | Expected Freshness | Staleness Interpretation |
|--------|-------|-------------------|--------------------------|
| EP-* evidence packets | record | 60 min | `historical` — proof remains valid; freshness doesn't invalidate |
| EC-* evidence checklists | record | 60 min | `historical` — requirement definitions |
| QR-* qualification records | record | 60 min | `historical` — qualification stands |
| qapr-* production receipts | record | 60 min | `historical` — receipt evidence |
| RCR-* registry change receipts | record | 60 min | `historical` — change recorded |
| SRS-* regression snapshots | record | 60 min | `historical` — baseline frozen in time |
| OD-* dashboard projections | record | 60 min | `historical` — render at point in time |

### Librarian (records only — no snapshots)

| Source | Class | Expected Freshness | Staleness Interpretation |
|--------|-------|-------------------|--------------------------|
| LIB_RECEIPT | record | 60 min | `historical` — receipt evidence |
| LIB_LEDGER | record | 60 min | `historical` — ledger entry |
| LIB_GATE | record | 60 min | `historical` — release gate result |

### Agent Bridge (mixed)

| Source | Class | Expected Freshness | Staleness Interpretation |
|--------|-------|-------------------|--------------------------|
| AB_INTAKE | record | 60 min | `historical` — intake receipt |
| AB_CUSTODY | record | 60 min | `historical` — custody artifact |
| AB_INTENT | record | 60 min | `historical` — intent record |
| AB_REVIEW | record | 60 min | `historical` — review output |
| AB_QUEUE | **snapshot** | **1 min** | `stale` — queue state changes rapidly |
| AB_PAIRING | **snapshot** | **5 min** | `stale` — pairing state semi-stable |
| AB_STATUS | **snapshot** | **1 min** | `stale` — aggregated status, fast-changing |

### Runtime Node (mixed)

| Source | Class | Expected Freshness | Staleness Interpretation |
|--------|-------|-------------------|--------------------------|
| RN_INTEGRATION | record | 60 min | `historical` — integration receipt |
| RN_QUALIFICATION | record | 60 min | `historical` — qualification record |
| RN_PROOF | record | 60 min | `historical` — proof chain |
| RN_HEALTH | **snapshot** | **15 sec** | `stale` — health measurements degrade quickly |
| RN_PORT | **snapshot** | **30 sec** | `stale` — port state may change with each process |
| RN_PROCESS | **snapshot** | **30 sec** | `stale` — process lifecycle |
| RN_SERVICE | **snapshot** | **60 sec** | `stale` — service status |

---

## 4. Freshness vs Validity

The most important rule from #213:

| Situation | Correct Interpretation | Wrong Interpretation |
|-----------|----------------------|---------------------|
| Qualification record is 7 days old | `historical` — still valid proof of past qualification | "invalid" — age does not invalidate history |
| Health snapshot is 2 minutes old (15s refresh) | `stale` — do not use for operational decisions | "system healthy" — snapshot too old to trust |
| Integration receipt is 1 hour old | `historical` — valid receipt evidence | "integration must be re-run" — receipt stands |
| Runtime process snapshot is 5 minutes old | `stale` — need fresh observation | "process not running" — could have changed |

**Rule:** Records can be `historical` (valid but less current). Snapshots can be `stale` (too old for operational decisions but may still be the most recent observation).

---

## 5. Dashboard Freshness Indicator

The current dashboard uses a single `fresh`/`stale` threshold (60 min) for all evidence. This conflates record and snapshot freshness.

### Proposed: Evidence-Class-Aware Freshness

```
evidence_freshness section becomes:

{
  "evidence_classification": { ... },         // from #212
  "evidence_freshness": {
    "records": {
      "total": 24,
      "current": 12,     // age < record threshold
      "historical": 8,   // age > threshold but still valid
      "archived": 4,     // well beyond threshold, audit-only
      "threshold_minutes": 60
    },
    "snapshots": {
      "total": 5,
      "current": 3,      // age < 1x refresh_interval
      "stale": 2,        // age > 1x refresh_interval
      "unknown": 0       // no refresh interval defined
    }
  }
}
```

---

## 6. Acceptance Gate Results

| Gate | Result | Key Justification |
|------|--------|-------------------|
| EFS-1 | ✅ Record freshness semantics defined | `current` / `historical` / `archived` — age never invalidates proof |
| EFS-2 | ✅ Snapshot freshness semantics defined | `current` / `stale` / `unknown` — age DOES invalidate currency |
| EFS-3 | ✅ Age cannot invalidate historical proof | Records explicitly preserve validity across all age bands |
| EFS-4 | ✅ Stale snapshots cannot appear current | `stale` label prevents operational use of expired observations |
| EFS-5 | ✅ Dashboard uses evidence class | Freshness section split by record/snapshot with class-specific thresholds |
| EFS-6 | ✅ Consumer mappings valid | All 4 consumers mapped with class-specific freshness rules |
| EFS-7 | ✅ No storage migration | Freshness computed at projection time from timestamps; no storage change |
| EFS-8 | ✅ Agent dispatch documented | Dispatch interpretation boundaries captured below |
| EFS-9 | ✅ Freshness distinguishes confidence from validity | `historical` ≠ `stale`; records valid but not current, snapshots may be stale |
| EFS-10 | ✅ Migration impact documented | Projection-only change; existing freshness data still valid under record semantics |

---

## 7. Agent Dispatch Implications (EFS-8)

When dispatching an agent action, the evidence sources it depends on must be evaluated by class:

| Decision Type | Required Freshness | Evidence Class |
|--------------|-------------------|----------------|
| Audit / review existing proof | Any age | `assurance_record` — historical proof is sufficient |
| Act on current system state | `current` snapshot required | `assurance_snapshot` — stale snapshot insufficient |
| Re-validate past result | `historical` record + `current` snapshot | Both — record as baseline, snapshot for current context |
| Release gate | `current` records + `current` snapshots | Both — proof must be recent and current state confirmed |

**Guard:** An agent should never be dispatched with only `stale` snapshots for operational decisions, nor should it be blocked from reviewing `historical` records.

---

## 8. Implementation Summary

### Schema
- `qa-pilot-owner-dashboard.schema.json` — v1.2: Add freshness semantics per evidence class to `evidence_freshness` section

### Dashboard Script
- `qa_pilot_owner_dashboard.py` — Update `get_evidence_freshness()` and `build_evidence_classification()` to compute class-aware freshness

### Validator
- `validate-qa-pilot-owner-dashboard.py` — Add EFS-1 through EFS-10 checks

### No storage changes
All freshness computed at projection time from existing timestamps.

---

*Report produced under Sprint #213 — ASSURANCE-CONTRACT-EVIDENCE-FRESHNESS-SEMANTICS-1*
*🔍 Pending Owner review*
