# QA Pilot Training Simulation — Governance Document

**Sprint:** QA-PILOT-LOCAL-TRAINING-SIM-1
**Lane:** parallel_planning
**Boundary:** QA Pilot-local only
**Authority:** advisory-only. No cross-project write authority.

---

## 1. Purpose

Define a QA Pilot-local simulation layer that uses ingested, regression-proven QA packets as advisory training examples only. This is a **simulation-only** layer — it generates advisory test cases from real ingested packet data, validates them against governance rules, and produces read-only results.

**The training sim is not a training system.** It does not fine-tune models, run training loops, apply packets, activate MCP bridges, or promote packet content to authority.

## 2. Core Invariants

| Invariant | TS Rule | Description |
|-----------|---------|-------------|
| Advisory-only | TS-3 | Every sim case has `advisory: true` |
| Owner decision required | TS-4 | Every sim case has `owner_decision_required: true` |
| Local reproducible | TS-6 | `reproducible_from` must be within `data/packets/ingested/` |
| No mutation paths | TS-7 | Sim inputs cannot contain mutation-authorizing keys or Librarian paths |
| No cross-project write | TS-8 | Sim inputs cannot claim cross-project write authority |
| Unsafe content quarantined | TS-9 | Unsafe sim cases must have expected_behavior indicating rejection |
| No Librarian references | TS-10 | No Librarian runtime/MCPController paths in sim schema |

## 3. Simulation Rules

### TS-1 through TS-10

| Rule | Description |
|------|-------------|
| TS-1 | `sim_id` must match pattern `qa-pilot-sim-[a-z0-9-]+` |
| TS-2 | `sim_type` must be a known type: advisory_training, boundary_test, rejection_test, reconstruction_test |
| TS-3 | `advisory` must be `true` — sim cases are advisory/test material only |
| TS-4 | `owner_decision_required` must be `true` — Owner decision required for downstream apply |
| TS-5 | `source` must reference a valid ingested packet (ingest_id, SHA-256 hash, packet type) |
| TS-6 | `reproducible_from` must be within QA Pilot local store (`data/packets/ingested/`) |
| TS-7 | No mutation-authorizing keys or Librarian mutation paths in inputs |
| TS-8 | No cross-project write claims in inputs |
| TS-9 | Unsafe sim cases must have `expected_behavior` containing reject/quarantine/block/deny |
| TS-10 | No Librarian runtime/MCPController path references in sim schema |

### Generated Sim Case Record

Every generated sim case includes:

| Field | Type | Constraint |
|-------|------|------------|
| `sim_id` | string | `qa-pilot-sim-{type}-{hash}` |
| `sim_type` | string | advisory_training, boundary_test, rejection_test, reconstruction_test |
| `source.ingest_id` | string | references ingested packet |
| `source.packet_hash` | string | SHA-256 hex |
| `source.packet_type` | string | from known packet types |
| `scenario` | string | human-readable description |
| `inputs` | object | sim input data |
| `expected_behavior` | string | expected sim outcome |
| `advisory` | boolean | `const: true` |
| `owner_decision_required` | boolean | `const: true` |
| `generated_at` | string | ISO 8601 UTC |
| `reproducible_from` | string | must be `data/packets/ingested/...` |
| `unsafe_action_required` | boolean | flags unsafe content |
| `notes` | string | optional |

### Sim Result Record

| Field | Type | Constraint |
|-------|------|------------|
| `result_id` | string | `qa-pilot-sim-result-{id}` |
| `sim_id` | string | references the sim case |
| `outcome` | string | passed, failed, error, quarantined |
| `observations` | string | free-text observations |
| `advisory` | boolean | `const: true` |
| `generated_at` | string | ISO 8601 UTC |

## 4. Allowed Behavior

- ✅ Generate sim cases from ingested, regression-proven packet records
- ✅ Validate sim cases against TS-1 through TS-10 rules
- ✅ List and inspect generated sim cases
- ✅ Produce read-only simulation results (passed/failed/quarantined)
- ✅ Test that invalid/unsafe packet content is rejected or quarantined
- ✅ Verify reproducibility from local store

## 5. Explicitly Forbidden (Hard Boundaries)

| Action | Status |
|--------|--------|
| Model fine-tuning | 🚫 Forbidden |
| Runtime training loop | 🚫 Forbidden |
| Packet application path | 🚫 Forbidden |
| MCP bridge activation | 🚫 Forbidden |
| Cross-project writes | 🚫 Forbidden |
| Librarian file mutation | 🚫 Forbidden |
| Authority promotion from packet content | 🚫 Forbidden |
| Owner decision bypass | 🚫 Forbidden |
| Auto-apply or auto-accept behavior | 🚫 Forbidden |
| Register MCP tools | 🚫 Forbidden |

## 6. Data Flow

```
Ingested Packet Store (data/packets/ingested/)
    │
    ▼
Training Sim CLI (generate)
    │
    ▼
Sim Cases (data/sim/cases/) ───► Validator (TS-1-10)
    │
    ▼
Sim Results (data/sim/results/) ──► Read-only advisory output
    │
    ▼
Owner decision required for any downstream application
```

Every step is QA Pilot-local. No data leaves the workspace. No cross-project path is created.

## 7. Dependencies

| Sprint | Dependency Type | Status |
|--------|----------------|--------|
| QA-PILOT-QA-PACKET-INGEST-1 (#17) | Sealed ingest pipeline — source of packet data | ✅ Sealed |
| QA-PILOT-MILESTONE-REGRESSION-SUITE-1 (#18) | Sealed regression suite — proven ingest chain stability | ✅ Sealed |

## 8. Next Valid Consumers

After this sprint is sealed, the following sprints are authorized:

- **QA-PILOT-CROSS-PROJECT-MCP-QA-BRIDGE-PLAN-1** (follow-up) — Bridge activation only after simulation layer proves advisory-only behavior

## 9. Reference

- **Case schema:** `docs/schemas/qa-pilot-training-sim-case.schema.json`
- **Result schema:** `docs/schemas/qa-pilot-training-sim-result.schema.json`
- **Validator:** `scripts/validate-qa-pilot-training-sim.py`
- **CLI:** `scripts/qa_pilot_training_sim.py`
- **Test runner:** `scripts/test-qa-pilot-training-sim.sh`
- **Fixtures:** `docs/examples/qa-pilot-training-sim/`
- **Ingest CLI (upstream):** `scripts/qa_pilot_qa_packet_ingest.py`
- **Regression suite (proven chain):** `scripts/test-qa-pilot-milestone-regression.sh`
