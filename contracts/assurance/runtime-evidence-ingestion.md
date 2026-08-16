# Runtime Evidence Ingestion Contract

**Sprint:** QA-PILOT-RUNTIME-EVIDENCE-COMPLETION-1 (#221)
**Status:** ACTIVE — Authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define how runtime events (`runtime-action-event`, `runtime-lifecycle-event`, `runtime-resource-observation`) become QA Pilot-governed evidence objects conforming to the assurance evidence contract.

## 2. Event-to-Evidence Mapping

### 2.1 Evidence Class Assignment

| Event Type | Evidence Class | Reason |
|------------|---------------|--------|
| `runtime_action_event` | `assurance_record` | Historical proof of what the runtime did. Immutable. |
| `runtime_lifecycle_event` | `assurance_record` | Historical proof of session lifecycle. Immutable. |
| `runtime_resource_observation` | `assurance_snapshot` | Current observation of resource consumption. Time-bound. |

### 2.2 Freshness Classification

| Event Type | Confidence Labels | Threshold |
|------------|-------------------|-----------|
| `runtime_action_event` | `current` < 60min, `historical` < 4hr, `archived` >= 4hr | Age-based |
| `runtime_lifecycle_event` | `current` < 60min, `historical` < 4hr, `archived` >= 4hr | Age-based |
| `runtime_resource_observation` | `current` < 15min, `stale` >= 15min | Refresh-interval-based |

## 3. Ingestion Path

```
FlightPlan Event (wire format)
    |
    v
Schema Validation (runtime-*-v1.schema.json)
    |
    v
Provenance Validation (runtime-evidence-provenance-v1.schema.json)
    |
    v
Freshness Classification (based on event_type)
    |
    v
Evidence Object Assembly (assurance-evidence-v1 structure)
    |
    v
Append-Only Store (data/runtime-evidence/)
    |
    v
Ingestion Receipt (RAI-* identifier)
```

## 4. Evidence Object Assembly

### 4.1 Field Mapping

| Assurance Evidence Field | Source | Required |
|--------------------------|--------|----------|
| `identity.evidence_id` | Generated: `RAE-*` / `RLE-*` / `RRO-*` prefix + timestamp + hex | Yes |
| `identity.timestamp` | Event `timestamp` | Yes |
| `identity.source` | `"qa-pilot"` (this sprint is QA-Pilot only) | Yes |
| `observation.observed_state` | Derived from event_type + action/lifecycle_event | Yes |
| `observation.artifact_refs` | References to source event file | Yes |
| `observation.measurements` | For resource observations: consumed tokens, goose level | Optional |
| `context.environment` | From provenance `runtime_identity` | Yes |
| `context.consumer_shape` | `"runtime_evidence"` (new consumer shape) | Yes |
| `context.execution_context` | From provenance `execution_identity` | Yes |
| `custody.origin` | `"scripts/validate-runtime-evidence.py"` | Yes |
| `custody.chain` | Empty array (first link in chain) | Yes |
| `custody.verification_state` | `"verified"` (validated by ingestion path) | Yes |
| `evidence_class` | Assigned per §2.1 | Yes |
| `freshness.captured_at` | Event `timestamp` | Yes |
| `freshness.validated_at` | Ingestion timestamp | Optional |
| `freshness.refresh_expected_at` | For snapshots: `captured_at` + refresh interval. For records: `null` | Conditional |
| `freshness.confidence_label` | Computed per §2.2 | Yes |

### 4.2 Provenance Mapping

| Provenance Group | Source | Required |
|------------------|--------|----------|
| `execution_identity.node_identity` | From event `execution_identity.node_identity` or default QA-Pilot node | Yes |
| `execution_identity.runtime_identity` | From event `execution_identity.runtime_identity` | Yes |
| `execution_identity.agent_identity` | From event `execution_identity.agent_identity` | Yes |
| `execution_identity.model_identity` | From event `model_identity` (resource observation) or `execution_identity.model_identity` | Yes |
| `execution_identity.session_identity` | From event `session_id` + `timestamp` | Yes |
| `governance_context.project_identity` | Default: `{"project_id": "qa-pilot", "project_type": "add_on"}` | Yes |
| `governance_context.work_packet_identity` | From event `work_packet_id` / `work_order_id` | Optional |
| `governance_context.owner_identity` | Default: `{"owner_id": "andrew-hannah"}` | Optional |
| `governance_context.authority_scope` | Default: `{"scope": "qa_pilot_local", "constraints": ["advisory_only", "no_cross_project_mutation"]}` | Yes |

## 5. Validation Rules

| Rule ID | Rule | Enforcement |
|---------|------|-------------|
| REI-1 | Every ingested event must pass schema validation against its source schema | Schema validation |
| REI-2 | Every ingested event must have provenance (execution_identity + governance_context) | Provenance validation |
| REI-3 | Evidence class must match event type per §2.1 | Classification validation |
| REI-4 | Freshness labels must be computed correctly per §2.2 | Freshness validation |
| REI-5 | Evidence must not contain `authorization` or `dispatch` fields | Authority boundary (CAG-RUNTIME-008) |
| REI-6 | Evidence must not directly trigger any write path | Authority boundary (CAG-RUNTIME-008) |
| REI-7 | Ingestion is append-only — no overwrites, no deletions | Store invariant |
| REI-8 | Every evidence item must be traceable to its source event | Provenance chain |

## 6. Authority Boundary (CAG-RUNTIME-008)

Runtime evidence is observation only. It does not become authority.

**Allowed:**
- "Agent X executed action Y" → Evidence record
- "QA-Pilot recommends review" → Finding/recommendation through existing review surface

**Not Allowed:**
- "QA-Pilot authorizes rollback" → Authority expansion
- Runtime evidence directly triggering any write path
- Runtime evidence bypassing the Owner decision contract

**Validation:** The ingestion path checks that evidence objects do not contain `authorization`, `dispatch`, `executed`, `sealed`, `approved`, or `owner_decision` fields. Any such fields cause ingestion rejection.

## 7. Store Layout

```
data/runtime-evidence/
  index.json                    # Append-only index of all ingested evidence
  records/                      # assurance_record evidence (action + lifecycle events)
    RAE-*.json
    RLE-*.json
  snapshots/                    # assurance_snapshot evidence (resource observations)
    RRO-*.json
```

## 8. Receipt Format

Every successful ingestion produces a receipt:

```json
{
  "receipt_id": "RAI-<timestamp>-<hex>",
  "event_id": "RAE-* | RLE-* | RRO-*",
  "evidence_id": "RAE-* | RLE-* | RRO-*",
  "evidence_class": "record | snapshot",
  "confidence_label": "current | historical | archived | stale",
  "ingested_at": "ISO8601",
  "ingested_by": "scripts/validate-runtime-evidence.py",
  "validation_passed": true,
  "authority_boundary_preserved": true
}
```
