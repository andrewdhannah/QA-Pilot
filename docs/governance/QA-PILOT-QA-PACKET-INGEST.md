# QA Pilot QA Packet Ingest — Governance Document

**Sprint:** QA-PILOT-QA-PACKET-INGEST-1
**Lane:** parallel_planning
**Boundary:** QA Pilot-local only
**Authority:** advisory-only. No cross-project write authority.

---

## 1. Purpose

Define how QA Pilot validates and imports governed Librarian QA export packets into QA Pilot-local derived storage. This is the ingestion side of the cross-project QA / training MCP bridge.

QA Pilot may ingest, validate, store, and inspect governed export packets from Librarian — but QA Pilot never mutates Librarian authority directly.

## 2. Ingestion Rules

### PI-1 through PI-14

| Rule | Description |
|------|-------------|
| PI-1 | `packet_type` must be a known type |
| PI-2 | `source_project` must be `librarian` |
| PI-3 | `consumer_project` must be `qa-pilot` |
| PI-4 | `authority_status` must be valid |
| PI-5 | `authoritative_export` must have payload |
| PI-6 | `generated_at` must be valid ISO 8601 UTC |
| PI-7 | `source_packet_hash` must be valid SHA-256 |
| PI-8 | `allowed_use` must not contain forbidden |
| PI-9 | `forbidden_use` must contain all required |
| PI-10 | `owner_decision_required_for_apply` must be true |
| PI-11 | No Librarian mutation paths in payload |
| PI-12 | `training_simulated` must restrict uses |
| PI-13 | `generated_at` not in future |
| PI-14 | No Librarian runtime refs in docs/schema |

### Packet Custody Schema

Every ingested packet must include:

| Field | Type | Constraint |
|-------|------|------------|
| `packet_type` | string | `qa_claim_registry`, `project_state`, `milestone_regression`, `training_source` |
| `source_project` | string | `const: "librarian"` |
| `consumer_project` | string | `const: "qa-pilot"` |
| `authority_status` | string | `authoritative_export`, `advisory_copy`, `training_simulated` |
| `generated_at` | string | ISO 8601 UTC (Z suffix) |
| `source_db_revision` | string | minLength 1 |
| `source_packet_hash` | string | SHA-256 hex (64 chars) |
| `source_docs` | array | string items |
| `allowed_use` | array | enum: `qa_regression`, `training_doc_generation`, `simulation` |
| `forbidden_use` | array | must include all three forbidden categories |
| `owner_decision_required_for_apply` | boolean | `const: true` |
| `payload` | object | optional — packet data |
| `custody_notes` | string | optional |

## 3. Authority Classification

| Classification | Meaning | Allowed QA Pilot Use |
|----------------|---------|---------------------|
| `authoritative_export` | Canonical Librarian state | QA regression, simulation |
| `advisory_copy` | Derived/replicated copy | QA regression, training doc generation, simulation |
| `training_simulated` | Not real authority | Training doc generation, simulation only — NOT QA regression |

## 4. Stored Packet Record

Every ingested packet is stored in `data/packets/ingested/` with index at `data/packets/ingested-index.json`.

Each record includes:

| Field | Description |
|-------|-------------|
| `ingest_id` | Unique identifier (`qpi-{type}-{hash_prefix}`) |
| `packet_type` | Type of packet |
| `source_project` | Originating project |
| `authority_status` | Authority classification |
| `generated_at` | When the source packet was generated |
| `source_packet_hash` | SHA-256 for integrity verification |
| `store_path` | Path to stored packet JSON |
| `ingested_at` | When QA Pilot consumed the packet |
| `advisory` | Always `true` |
| `cross_project_write_authorized` | Always `false` |
| `owner_apply_required` | Always `true` |

## 5. Boundary Rules

**Allowed:**
- Validate and ingest Librarian export packets
- Store ingested packets in QA Pilot-local derived storage
- List and inspect ingested packets
- Clear ingested packets (local-only operation)

**Forbidden:**
- Write to Librarian DB
- Register MCP tools in Librarian runtime
- Mutate Librarian files or authority
- Auto-apply or auto-accept ingested packet content
- Promote `training_simulated` or `advisory_copy` to authoritative status
- Execute cross-project writes of any kind

## 6. Cross-Project Safety

Every ingested packet is explicitly marked:

- `advisory: True`
- `cross_project_write_authorized: False`
- `owner_apply_required: True`

No packet ingested by QA Pilot may be used to directly mutate Librarian state, substitute for an Owner decision, or promote training results to authority.

## 7. Dependencies

| Sprint | Dependency Type | Status |
|--------|----------------|--------|
| QA-PILOT-CROSS-PROJECT-MCP-QA-BRIDGE-PLAN-1 | Design authority | ✅ Sealed |
| LIBRARIAN-QA-PACKET-EXPORT-1 | Input source (Librarian-side export) | 🔍 Planned |

This sprint defines QA Pilot's ingestion schema and validation against the bridge plan's packet custody model. Live ingestion of actual Librarian export packets requires LIBRARIAN-QA-PACKET-EXPORT-1 to be sealed first.

## 8. Reference

- **Schema:** `docs/schemas/qa-pilot-qa-packet-ingest.schema.json`
- **Validator:** `scripts/validate-qa-pilot-qa-packet-ingest.py`
- **Test runner:** `scripts/test-qa-pilot-qa-packet-ingest.sh`
- **Ingest CLI:** `scripts/qa_pilot_qa_packet_ingest.py`
- **Fixtures:** `docs/examples/qa-pilot-qa-packet-ingest/`
- **Design direction:** `receipts/decision-resolutions/dd-project-sandbox-model-1.json`
- **Sprint authorization:** `receipts/decision-resolutions/od-qa-pilot-qa-packet-ingest-1.json`
