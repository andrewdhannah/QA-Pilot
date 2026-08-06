# QA Pilot Push Integration Model

**Sprint:** QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1
**Status:** Planning — defines the event-driven integration between Librarian and QA Pilot
**Dependency:** QA-PILOT-QUALIFICATION-ARCHITECTURE.md (§6 Event Integration Model)

---

## 0. Architectural Constraint

QA Pilot must not poll the Librarian for changes. Polling is inconsistent with the rest of the architecture. All qualification triggers originate from Librarian events and are pushed to QA Pilot through a governed mechanism.

**Invariant:** QA Pilot never initiates communication to discover whether work is needed. The Librarian always tells it what to do and when.

---

## 1. Event Model

### 1.1 Event Source

The Librarian Sprint Ledger is the authoritative event source. When a sprint seals, the ledger transition is the trigger.

```
Sprint Ledger
    |
    status: "sealed" (transition detected)
    |
    v
Event Publisher
    |
    v
QA Pilot Event Consumer
```

### 1.2 Event Schema

```json
{
  "event": "SPRINT_SEALED",
  "schema": "platform-event-v1",
  "timestamp": "2026-07-16T12:00:00Z",
  "sprint": {
    "id": "SOME-SPRINT-1",
    "epic_id": "EPIC-SOME-EPIC-1",
    "previous_status": "active",
    "new_status": "sealed",
    "sealed_at": "2026-07-16T12:00:00Z",
    "sealed_by": "owner"
  },
  "scope": {
    "changed_targets": ["NODE-OWNER-QUEUE", "NODE-REGISTRY"],
    "qualification_required": ["security", "regression"],
    "qualification_level": "required",
    "change_types": ["new_interface", "schema_updated"],
    "code_locations_changed": [
      "Sources/App/Controllers/OwnerQueueController.swift",
      "Sources/App/Services/RegistryService.swift"
    ]
  },
  "provenance": {
    "publisher": "librarian-core",
    "ledger_entry": 502,
    "receipt_ref": "receipts/sprint-seals/SOME-SPRINT-1-seal.json"
  }
}
```

### 1.3 Event Fields

| Field | Required | Description |
|-------|----------|-------------|
| `event` | Yes | Event type identifier |
| `schema` | Yes | Schema version for the event payload |
| `timestamp` | Yes | When the event was published |
| `sprint.id` | Yes | The sprint that triggered the event |
| `sprint.previous_status` | Yes | Status before transition |
| `sprint.new_status` | Yes | Status after transition |
| `scope.changed_targets` | Yes | Array of node/component IDs that changed |
| `scope.qualification_required` | Yes | Array of qualification domains to run |
| `scope.qualification_level` | Yes | Minimum coverage level required |
| `scope.change_types` | No | Types of change detected (for generator optimization) |
| `scope.code_locations_changed` | No | Specific files changed (for targeted regeneration) |
| `provenance.publisher` | Yes | Which Librarian service published the event |
| `provenance.ledger_entry` | Yes | Ledger entry that triggered the event |
| `provenance.receipt_ref` | No | Optional reference to seal receipt |

---

## 2. Integration Mechanism

### 2.1 Recommended Approach: MCP-Based Push

QA Pilot exposes an MCP tool that the Librarian calls when an event occurs.

```
Librarian (event detected)
    |
    calls: qa_pilot_qualification_trigger(event_payload)
    |
    v
QA Pilot MCP Handler
    |
    1. Validate event schema
    2. Identify changed targets
    3. Filter by scope
    4. Execute qualification
    5. Return qualification receipt
    |
    v
Librarian (receives receipt)
    |
    updates evidence chain
```

### 2.2 MCP Tool Definition

```json
{
  "tool_name": "qa_pilot_qualification_trigger",
  "schema_version": "qap-qualification-v1",
  "description": "Trigger qualification for changed targets following a sprint seal event.",
  "authority": "R0",
  "mutates": false,
  "assigns_authority": false,
  "assigns_custody": false,
  "input": {
    "type": "object",
    "required": ["event", "scope"],
    "properties": {
      "event": { "type": "string", "enum": ["SPRINT_SEALED"] },
      "scope": {
        "type": "object",
        "required": ["changed_targets", "qualification_required"],
        "properties": {
          "changed_targets": { "type": "array", "items": { "type": "string" } },
          "qualification_required": { "type": "array", "items": { "type": "string" } }
        }
      }
    }
  },
  "output": {
    "type": "object",
    "required": ["status", "receipts"],
    "properties": {
      "status": { "enum": ["qualification_complete", "partial", "failed"] },
      "receipts": { "type": "array", "items": { "$ref": "qualification-receipt" } },
      "coverage": { "$ref": "coverage-report" }
    }
  }
}
```

### 2.3 Alternative: File-Based Event Queue

If MCP is not available for QA Pilot at this stage, a file-based event queue can serve as an intermediate mechanism:

```
Librarian writes event to:
    active/qa-pilot/inbox/qualification-events/{event-id}.json

QA Pilot detects new file (poll-only if MCP unavailable, but flagged as technical debt):
    Reads event
    Processes qualification
    Writes receipt to:
        active/qa-pilot/outbox/qualification-receipts/{receipt-id}.json

Librarian detects receipt file:
    Seals evidence
```

MCP-based push is the target architecture. File-based queue is a transitional mechanism only and must be documented as such.

---

## 3. Scope Filtering

QA Pilot must not requalify everything on every event. The scope field determines what to run.

### 3.1 Filtering Rules

| Scope Configuration | QA Pilot Behavior |
|--------------------|-------------------|
| `changed_targets: ["NODE-A"]` | Only generate/execute tests for NODE-A |
| `changed_targets: ["NODE-A", "NODE-B"]` | Generate/execute for both, independent result sets |
| `qualification_required: ["security"]` | Only security domain, not functional or performance |
| `qualification_required: ["security", "regression"]` | Both security and regression domains |
| `qualification_level: "required"` | Only run required-level tests; skip advisory |
| (all fields present) | Full scope: specific nodes, specific domains, specific level |

### 3.2 No-Scope Edge Case

If `changed_targets` is empty or absent, QA Pilot returns with no action:

```json
{
  "status": "qualification_complete",
  "message": "No changed targets specified — no qualification executed",
  "receipts": []
}
```

---

## 4. Receipt Return Flow

After qualification completes, QA Pilot returns one or more receipts.

### 4.1 Per-Component Receipt

Each qualified component produces its own receipt:

```json
{
  "receipt_type": "qualification",
  "domain": "security",
  "component_ref": "NODE-OWNER-QUEUE",
  "test_identity": "AUTH-BOUNDARY-001/rev:3",
  "result": "PASS",
  "coverage": {
    "required": 12,
    "executed": 12,
    "passed": 12,
    "level": "required"
  }
}
```

### 4.2 Aggregate Receipt

After all targeted components are qualified, an aggregate receipt is produced:

```json
{
  "receipt_type": "qualification_aggregate",
  "trigger_event": "SPRINT_SEALED",
  "sprint_id": "SOME-SPRINT-1",
  "components": {
    "total": 2,
    "qualified": 2,
    "failed": 0
  },
  "domains": {
    "security": "PASS",
    "regression": "PASS"
  },
  "overall": "QUALIFIED",
  "evidence_chain_ref": "receipts/qualification/SOME-SPRINT-1-aggregate.json"
}
```

### 4.3 Receipt Sealing

The aggregate receipt is sealed by the Librarian into the evidence chain, creating a link:

```
Sprint Seal Receipt #501
    ↓
Qualification Trigger Event
    ↓
QA Pilot Qualification Receipts
    ↓
Aggregate Qualification Receipt
    ↓
Librarian Evidence Chain (sealed)
```

---

## 5. Error Handling

### 5.1 QA Pilot Unavailable

If QA Pilot is unreachable when the Librarian pushes an event:

1. Librarian retries (configurable: 3 retries, 30s interval)
2. If all retries fail, Librarian emits a `QUALIFICATION_PENDING` event and continues
3. The pending qualification surfaces in the Owner's dashboard as a deferred action
4. Owner may manually trigger qualification via `qa_pilot_qualification_trigger`

### 5.2 Partial Failure

If some components qualify and others fail:

1. Aggregate receipt reports `partial` status
2. Each component receipt indicates its individual result
3. The coverage report identifies which components failed and what gaps exist
4. The release gate evaluates based on the configured `required_domains`

### 5.3 Invalid Event

If QA Pilot receives an event that fails schema validation:

1. Returns `invalid_event` error with schema violations
2. Librarian logs the error and surfaces in Owner dashboard
3. No qualification is executed for the invalid event

---

## 6. Transitional Path

### Phase 1: Manual (Current State)

Qualification is triggered manually via Owner command:

```
Owner: "Qualify project"
QA Pilot: Runs all domains for all components
```

### Phase 2: Event-Driven (Target State, after C2)

Qualification is triggered automatically by sprint seal events:

```
Sprint sealed → Push event → Targeted qualification → Receipt → Evidence chain
```

### Phase 3: Event-Driven + Selective (Future)

Qualification is triggered automatically and selectively:

```
Sprint sealed → Changed targets identified → Only affected domains regenerated
```

---

## 7. Acceptance Gates

| Gate | Requirement |
|------|-------------|
| PUSH-P1 | SPRINT_SEALED event schema defined and validated |
| PUSH-P2 | Scope filtering rules defined |
| PUSH-P3 | MCP tool interface defined for QA Pilot trigger |
| PUSH-P4 | Receipt return flow defined (per-component + aggregate) |
| PUSH-P5 | Error handling for unavailable, partial failure, invalid event |
| PUSH-P6 | Retry logic defined |
| PUSH-P7 | Transitional path defined (manual → event-driven → selective) |
| PUSH-P8 | Evidence chain linkage documented |

---

*Push integration model for QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1. Planning only. No implementation authority conferred.*
