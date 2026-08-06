# Assurance Evidence Contract

**Extracted from:** EPIC-ASSURANCE-OPERATIONS-ADOPTION-1 (#207–#210)
**Sprint:** #215 — ASSURANCE-CONTRACT-EVIDENCE-STATE-CONTRACT-FORMALIZATION-1
**Status:** DRAFT — 🔍 Pending Owner review

---

## 1. Purpose

Define the canonical assurance evidence object and the two-class evidence model (record vs snapshot) that survived across all 4 consumer adoption shapes.

## 2. Evidence Classes

Evidence is divided into two mutually exclusive classes:

### 2.1 `assurance_record`

Historical, durable evidence of a governed event.

**Properties:**

| Property | Type | Requirement |
|----------|------|-------------|
| `evidence_class` | `"record"` | REQUIRED |
| Is immutable | boolean | MUST be true |
| Is replayable | boolean | MUST be true |
| Age can invalidate? | No | Record remains valid as historical proof indefinitely |
| Storage | Governed intake | MUST enter through validated write path |

**Examples from adoption baselines:**
- QA Pilot: EP-* packets, QR-* qualification records, RCR-* receipt changes
- Librarian: Receipts, sprint ledger entries, release gates
- Agent Bridge: Intake receipts, custody artifacts, audit trails
- Runtime Node: Integration receipts, qualification records, proof chain

### 2.2 `assurance_snapshot`

Transient, current-state observation of a live system.

**Properties:**

| Property | Type | Requirement |
|----------|------|-------------|
| `evidence_class` | `"snapshot"` | REQUIRED |
| Is refreshable | boolean | MUST be true |
| Is time-bound | boolean | MUST have `refresh_expected_at` |
| Age can invalidate? | Yes | Snapshot IS invalidated by age exceeding refresh interval |
| Storage | Observation endpoint | MUST NOT enter record store without governed intake |

**Examples from adoption baselines:**
- Agent Bridge: Queue state, pairing state, aggregated status
- Runtime Node: Health checks, port availability, process state, service status, uptime

### 2.3 Relationship Rules (Cross-Consumer Invariants)

The following rules survived across all 4 consumer shapes and are therefore contractual:

1. **R1 — Immutability of records:** A record proves what happened at a point in time. It cannot be modified or deleted.
2. **R2 — Transience of snapshots:** A snapshot describes what is observed right now. It expires when its refresh interval elapses.
3. **R3 — No cross-mutation:** A snapshot must never overwrite or mutate a record.
4. **R4 — No implication:** A record must never imply current operational state. A snapshot must never replace historical proof.
5. **R5 — Separate projection:** The assurance projection layer must render record and snapshot evidence separately or with clear temporal classification.
6. **R6 — Evidence class label:** Every evidence item rendered in a projection must carry its `evidence_class` label.

## 3. Canonical Evidence Object

Every evidence object MUST conform to the following structure:

```
AssuranceEvidence {
    identity: {
        evidence_id: string,        // Unique identifier (EP-, QR-, RCR-, etc.)
        timestamp: ISO8601,         // When the evidence was captured
        source: string              // Consumer project that produced it
    },
    observation: {
        observed_state: string,     // What was observed (free text)
        artifact_refs: string[],    // References to supporting artifacts
        measurements: object        // Optional quantitative measurements
    },
    context: {
        environment: string,        // Execution environment description
        consumer_shape: string,     // Which consumer shape produced this
        execution_context: object   // Additional context key-value pairs
    },
    custody: {
        origin: string,             // Provenance origin
        chain: string[],            // Custody chain references
        verification_state: string  // verified | unverified | stale
    },
    evidence_class: "record" | "snapshot",
    freshness: {
        captured_at: ISO8601,       // REQUIRED
        validated_at: ISO8601?,     // OPTIONAL for records
        refresh_expected_at: ISO8601?,  // REQUIRED for snapshots
        confidence_label: "current" | "historical" | "archived" | "stale" | "unknown"
    }
}
```

## 4. Contract Provenance Requirement

Every contract extracted from assurance evidence MUST be traceable backwards through:

```
Contract
    |
    v
Finding
    |
    v
Evidence
    |
    v
Adoption Baseline
    |
    v
Consumer Shape
```

## 5. Evidence State Validation Rules

| Rule ID | Rule | Enforcement |
|---------|------|-------------|
| EV-1 | Every evidence item has `evidence_class` | Schema validation |
| EV-2 | Records have `validated_at` (optional) | Schema validation |
| EV-3 | Snapshots have `refresh_expected_at` | Schema validation |
| EV-4 | No evidence item may contain `authorization` or `dispatch` fields | Negative schema test |
| EV-5 | Evidence descriptions (observed_state) must describe what happened, not what should happen | Contract review |

## 6. Cross-Consumer Evidence Classification Matrix

| Evidence Source | Class | Consumer | Adoption Baseline |
|----------------|-------|----------|-------------------|
| EP-* evidence packets | `record` | QA Pilot | #207 |
| EC-* evidence checklists | `record` | QA Pilot | #207 |
| QR-* qualification records | `record` | QA Pilot | #207 |
| RCR-* registry change receipts | `record` | QA Pilot | #207 |
| qapr-* production receipts | `record` | QA Pilot | #207 |
| TC-* test cases | `record` | QA Pilot | #207 |
| ERS-* epic regression suites | `record` | QA Pilot | #207 |
| SRS-* regression snapshots | `record` | QA Pilot | #207 |
| OD-* dashboard projections | `record` | QA Pilot | #207 |
| LIB_RECEIPT | `record` | Librarian | #207 |
| LIB_LEDGER | `record` | Librarian | #207 |
| LIB_GATE | `record` | Librarian | #207 |
| AB_INTAKE | `record` | Agent Bridge | #209 |
| AB_CUSTODY | `record` | Agent Bridge | #209 |
| AB_INTENT | `record` | Agent Bridge | #209 |
| AB_REVIEW | `record` | Agent Bridge | #209 |
| AB_QUEUE | `snapshot` | Agent Bridge | #209 |
| AB_PAIRING | `snapshot` | Agent Bridge | #209 |
| AB_STATUS | `snapshot` | Agent Bridge | #209 |
| RN_INTEGRATION | `record` | Runtime Node | #210 |
| RN_QUALIFICATION | `record` | Runtime Node | #210 |
| RN_PROOF | `record` | Runtime Node | #210 |
| RN_HEALTH | `snapshot` | Runtime Node | #210 |
| RN_PORT | `snapshot` | Runtime Node | #210 |
| RN_PROCESS | `snapshot` | Runtime Node | #210 |
| RN_SERVICE | `snapshot` | Runtime Node | #210 |

## 7. Invariants That Survived All 4 Consumer Shapes

The following properties were confirmed across all 4 adoption baselines and are therefore contractual:

| Invariant | Confirmed By | Contract Rule |
|-----------|-------------|---------------|
| Evidence has identity + observation + context | QA Pilot (#207), Librarian (#207), Agent Bridge (#209), Runtime Node (#210) | EV-ID-1 |
| Evidence is either record or snapshot | Runtime Node (#210), Agent Bridge (#209) — confirmed universal | EV-CLASS-1 |
| Records are immutable | All 4 consumers | EV-REC-1 |
| Snapshots are transient | Agent Bridge (#209), Runtime Node (#210) | EV-SNP-1 |
| Record ≠ snapshot — no cross-mutation | Runtime Node (#210) — safety confirmed accidental, formalized here | EV-SEP-1 |
| Absence is valid information | All 4 consumers — missing capabilities are not failures | EV-ABS-1 |
| Governance concepts map directly | Librarian (#207), Agent Bridge (#209), Runtime Node (#210) | EV-GOV-1 |
| Project-specific mechanics go in adapters | All 3 adopters | EV-ADP-1 |
| Authority boundary is invariant | All 4 consumers | EV-AUTH-1 |
