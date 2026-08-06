# QA Pilot Qualification Framework — Architecture

**Part of:** QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1
**Tier:** T1 (Required for Architecture)
**Prepared:** 2026-07-16
**Status:** Proposed — planning output, not implemented

---

## Part I — Qualification Schema Design

### 1.1 Design Principles

| Principle | Rationale |
|-----------|-----------|
| **Compatible with MQR, not dependent on it** | QA Pilot may understand Librarian contracts; may not depend on Librarian implementation |
| **Advisory-only** | Qualification records never authorize work, never seal, never mutate governance state |
| **Evidence-grounded** | Every qualification record must reference verifiable evidence |
| **Deterministic** | Same inputs always produce same qualification result |
| **Extensible** | Schema supports artifact, process, and reviewer dimensions |
| **Backward-compatible** | New qualification layer does not modify existing sealed layers |

### 1.2 Qualification Record Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "docs/schemas/qa-pilot-qualification-record.schema.json",
  "title": "QA Pilot Qualification Record",
  "description": "A governed qualification record for QA Pilot artifacts, processes, or reviewer actions. Records are advisory-only and evidence-grounded.",
  "type": "object",
  "required": [
    "record_id",
    "qualification_type",
    "target_id",
    "target_type",
    "qualification_level",
    "evidence_refs",
    "assessed_at",
    "assessed_by",
    "advisory_only",
    "custody",
    "librarian_impact"
  ],
  "properties": {
    "record_id": {
      "type": "string",
      "pattern": "^QR-[A-Z0-9]{8}-[0-9]{4}$",
      "description": "Unique qualification record identifier (e.g., QR-ART-E001-0001)"
    },
    "qualification_type": {
      "type": "string",
      "enum": ["artifact", "process", "reviewer"],
      "description": "Dimension of qualification — artifact (does output satisfy requirements), process (was work performed through approved workflow), reviewer (was decision authority correctly applied)"
    },
    "target_id": {
      "type": "string",
      "description": "Identifier of the qualified target (e.g., workbench item ID, sprint ID, checklist ID)"
    },
    "target_type": {
      "type": "string",
      "enum": [
        "workbench_item",
        "evidence_packet",
        "test_case",
        "result_packet",
        "epic_suite",
        "checklist",
        "review_packet",
        "decision_packet",
        "sprint",
        "startup_surface",
        "registry_entry",
        "custody_receipt",
        "pipeline_layer",
        "export_packet",
        "action_packet",
        "handoff_packet",
        "review_outcome",
        "readiness_posture"
      ],
      "description": "Type of target being qualified"
    },
    "qualification_level": {
      "type": "string",
      "enum": ["unqualified", "spot_checked", "peer_reviewed", "audited", "exempt"],
      "description": "Qualification level: unqualified (no evidence), spot_checked (single-pass verification), peer_reviewed (independent verification), audited (formal audit trail), exempt (excluded by policy)"
    },
    "qualification_criteria": {
      "type": "object",
      "properties": {
        "required_level": {
          "type": "string",
          "enum": ["unqualified", "spot_checked", "peer_reviewed", "audited", "exempt"],
          "description": "Minimum required qualification level"
        },
        "pass_rate_threshold": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "description": "Minimum pass rate (0.0-1.0) for qualification"
        },
        "evidence_count_min": {
          "type": "integer",
          "minimum": 0,
          "description": "Minimum number of evidence refs required"
        },
        "authority_check_required": {
          "type": "boolean",
          "description": "Whether authority boundary check is required"
        }
      }
    },
    "evidence_refs": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["evidence_id", "evidence_type", "evidence_source", "verification_status"],
        "properties": {
          "evidence_id": {
            "type": "string",
            "description": "Identifier of the evidence record"
          },
          "evidence_type": {
            "type": "string",
            "enum": [
              "receipt",
              "validation_result",
              "test_result",
              "custody_audit",
              "drift_check",
              "pipeline_health",
              "registry_state",
              "snapshot_baseline",
              "owner_decision",
              "review_outcome",
              "advisory_packet",
              "export_packet",
              "workbench_item",
              "evidence_packet",
              "checklist_result",
              "linker_result"
            ]
          },
          "evidence_source": {
            "type": "string",
            "description": "File path or reference to the evidence"
          },
          "verification_status": {
            "type": "string",
            "enum": ["verified", "stale", "missing", "corrupted"],
            "description": "Current verification status of the evidence"
          },
          "verified_at": {
            "type": "string",
            "format": "date-time",
            "description": "When this evidence was last verified"
          }
        }
      }
    },
    "sub_dimension_scores": {
      "type": "object",
      "description": "Per-sub-dimension scores (e.g., {syntax: 0.95, completeness: 0.88, authority: 1.0})",
      "additionalProperties": {
        "type": "number",
        "minimum": 0.0,
        "maximum": 1.0
      }
    },
    "overall_score": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Aggregate qualification score across all sub-dimensions"
    },
    "lifecycle_state": {
      "type": "string",
      "enum": ["proposed", "in_progress", "completed", "expired", "superseded", "revoked"],
      "description": "Lifecycle state of this qualification record"
    },
    "provenance": {
      "type": "object",
      "required": ["assessor_id", "session_id", "tool_call_log"],
      "properties": {
        "assessor_id": {
          "type": "string",
          "description": "Agent or human that performed the qualification"
        },
        "session_id": {
          "type": "string",
          "description": "Work session identifier"
        },
        "tool_call_log": {
          "type": "string",
          "description": "Reference to tool call log for reproducibility"
        }
      }
    },
    "expiry_date": {
      "type": "string",
      "format": "date",
      "description": "When this qualification must be re-assessed (default: 90d from assessed_at)"
    },
    "superseded_by": {
      "type": "string",
      "description": "If superseded, the record_id of the superseding qualification"
    },
    "notes": {
      "type": "string",
      "description": "Free-text caveats, known gaps, edge cases"
    },
    "advisory_only": {
      "type": "boolean",
      "const": true,
      "description": "Must always be true — qualification records never authorize work"
    },
    "custody": {
      "type": "string",
      "const": "qa-pilot-local",
      "description": "Must always be qa-pilot-local"
    },
    "librarian_impact": {
      "type": "string",
      "const": "none",
      "description": "Must always be none"
    },
    "assessed_at": {
      "type": "string",
      "format": "date-time",
      "description": "When the qualification was assessed"
    },
    "assessed_by": {
      "type": "string",
      "description": "Entity that performed the assessment"
    }
  },
  "allOf": [
    {
      "if": {
        "properties": { "qualification_type": { "const": "artifact" } }
      },
      "then": {
        "required": ["overall_score", "sub_dimension_scores"]
      }
    },
    {
      "if": {
        "properties": { "qualification_type": { "const": "process" } }
      },
      "then": {
        "required": ["lifecycle_state", "provenance"]
      }
    },
    {
      "if": {
        "properties": { "qualification_type": { "const": "reviewer" } }
      },
      "then": {
        "required": ["provenance", "evidence_refs"]
      }
    }
  ]
}
```

### 1.3 Qualification Levels

```
                        QUALIFICATION LEVELS
                    ┌──────────────────────────────┐
                    │        AUDITED               │
                    │  Formal audit trail,         │
                    │  independent verification,   │
                    │  full evidence package       │
                    ├──────────────────────────────┤
                    │      PEER_REVIEWED           │
                    │  Independent verification,   │
                    │  secondary evidence check,   │
                    │  review receipt              │
                    ├──────────────────────────────┤
                    │      SPOT_CHECKED            │
                    │  Single-pass verification,   │
                    │  evidence exists check,      │
                    │  automated validation        │
                    ├──────────────────────────────┤
                    │      UNQUALIFIED             │
                    │  No evidence, not verified,  │
                    │  default state               │
                    └──────────────────────────────┘
                         EXEMPT (policy-based)
```

| Level | Code | Pass Rate | Min Evidence | Valid For | Authority Check |
|-------|------|-----------|--------------|-----------|-----------------|
| Unqualified | UNQ | N/A | 0 | N/A | No |
| Spot Checked | SPT | ≥ 0.80 | ≥ 1 | 30 days | No |
| Peer Reviewed | PRV | ≥ 0.90 | ≥ 2 | 90 days | Yes |
| Audited | AUD | ≥ 0.95 | ≥ 3 | 180 days | Yes |
| Exempt | EXM | N/A | 0 (policy) | Varies | N/A |

### 1.4 Target Type → Qualification Level Mapping

Default qualification requirements per target type (based on Landscape Catalog analysis):

| Target Type | Default Min Level | Rationale |
|-------------|-------------------|-----------|
| workbench_item | spot_checked | Workbench items are advisory; light verification sufficient |
| evidence_packet | peer_reviewed | Evidence trust requires independent verification |
| test_case | spot_checked | Test cases are derived; single-pass adequate |
| result_packet | peer_reviewed | Results feed upstream decisions; peer review warranted |
| epic_suite | peer_reviewed | Epic-level aggregation requires independent check |
| checklist | audited | Checklists define evidence requirements; highest rigor |
| review_packet | peer_reviewed | Review packets are Owner-facing; peer review required |
| decision_packet | audited | Decision packets carry decision authority implications |
| sprint | peer_reviewed | Sprints aggregate many artifacts |
| startup_surface | spot_checked | Surfaces are read-only displays |
| custody_receipt | audited | Custody is foundational trust layer |
| export_packet | spot_checked | Exports are copies of internal state |
| action_packet | peer_reviewed | Action packets direct work |
| handoff_packet | peer_reviewed | Handoffs cross boundaries |
| review_outcome | peer_reviewed | Outcomes inform Owner decisions |
| readiness_posture | spot_checked | Readiness is derived state |

---

## Part II — Evidence Pipeline

### 2.1 Pipeline Architecture

```
                        EXISTING QA PILOT LAYERS
    ┌─────────────────────────────────────────────────────────┐
    │  Evidence Sources         │  Intake & Validation         │
    │  ┌──────────────────┐    │  ┌────────────────────────┐  │
    │  │ #33 MCP Evidence │    │  │ #44 Evidence Checklist │  │
    │  │ #4 Receipt Store │───▶│  │ #45 Review Packet      │──▶
    │  │ #11 Audit Store  │    │  │ #46 Evidence Linker    │  │
    │  │ #26 Custody Recpt│    │  └────────────────────────┘  │
    │  └──────────────────┘    │                               │
    │                          │  ┌────────────────────────┐  │
    │  Pipeline Health         │  │ #38 Pipeline Health    │  │
    │  ┌──────────────────┐    │  │ #39 Drift Detection   │──▶
    │  │ #48 Layer Registry│───▶│  │ #40 Recovery Diag    │  │
    │  │ #49 Drift Registry│    │  └────────────────────────┘  │
    │  └──────────────────┘    │                               │
    │                          │  ┌────────────────────────┐  │
    │  Workbench               │  │ #66 Workbench Items    │  │
    │  ┌──────────────────┐    │  │ #67 Evidence Linking  │──▶
    │  │ #72 Review Intake │───▶│  │ #68 Status Lifecycle │  │
    │  │ #76 Decision Recpt│    │  │ #70 Export Packet    │  │
    │  └──────────────────┘    │  └────────────────────────┘  │
    │                          │                               │
    │  Review Depth            │  ┌────────────────────────┐  │
    │  ┌──────────────────┐    │  │ #88 Depth Thresholds  │  │
    │  │ #90 Decision Pkt  │───▶│  │ #91 Risk-Based Review│──▶
    │  │                   │    │  └────────────────────────┘  │
    │  └──────────────────┘    │                               │
    │                          │  ┌────────────────────────┐  │
    │  Startup Surfaces        │  │ #37 Pipeline Surface   │  │
    │  ┌──────────────────┐    │  │ #43 ODR Surface       │──▶
    │  │ #50 Registry Surf │───▶│  │ #52 RCR Surface       │  │
    │  │ #56 SRS Snapshot  │    │  │ #58 SUG Surface       │  │
    │  └──────────────────┘    │  └────────────────────────┘  │
    └─────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                      ┌─────────────────────────┐
                      │  QUALIFICATION PIPELINE  │
                      │                         │
                      │  1. Evidence Collection  │
                      │     (read existing data) │
                      │                         │
                      │  2. Evidence Validation  │
                      │     (verify schema, age) │
                      │                         │
                      │  3. Qualification Eval   │
                      │     (score vs criteria)  │
                      │                         │
                      │  4. Record Generation    │
                      │     (create QR- record)  │
                      │                         │
                      │  5. Persistence          │
                      │     (store + index)      │
                      │                         │
                      │  6. Surface Update       │
                      │     (expose in startup)  │
                      └─────────────────────────┘
                                    │
                                    ▼
                      ┌─────────────────────────┐
                      │  OUTPUTS                │
                      │  ┌───────────────────┐  │
                      │  │ QR- records       │  │
                      │  │ Qualification idx │  │
                      │  │ Startup surface   │  │
                      │  │ Decision packets  │  │
                      │  └───────────────────┘  │
                      └─────────────────────────┘
```

### 2.2 Evidence Chain

Each qualification record's evidence chain follows this provenance model:

```
Qualification Record (QR-*)
  ├── evidence_refs[]
  │   ├── evidence_id: "EM-20260707-001"
  │   ├── evidence_type: "evidence_packet"
  │   ├── evidence_source: "data/evidence/EM-20260707-001.json"
  │   ├── verification_status: "verified"
  │   └── verified_at: "2026-07-16T12:00:00Z"
  │
  ├── evidence_id: "RP-20260707-003"
  │   ├── evidence_type: "result_packet"
  │   ├── evidence_source: "data/result-packets/RP-20260707-003.json"
  │   ├── verification_status: "verified"
  │   └── verified_at: "2026-07-16T12:00:00Z"
  │
  └── evidence_id: "CR-20260707-012"
      ├── evidence_type: "custody_receipt"
      ├── evidence_source: "data/custody-receipts/CR-20260707-012.json"
      ├── verification_status: "verified"
      └── verified_at: "2026-07-16T12:00:00Z"
```

**Provenance invariants:**
- Every evidence ref must resolve to an existing file with matching JSON Schema
- Stale evidence (age > 90d) must be re-verified before qualification
- Missing evidence drops qualification to `unqualified`
- Corrupted evidence must be reported but does not block other evidence refs

### 2.3 Feed Sources by Qualification Type

| Qualification Type | Primary Feed | Secondary Feed | Verification |
|-------------------|--------------|----------------|--------------|
| **Artifact** (`artifact`) | #33 Evidence intake | #35 Result packets | EM-validator, RP-validator |
| **Process** (`process`) | #66 Workbench items | #68 Status lifecycle | WB-validator, WL-validator |
| **Reviewer** (`reviewer`) | #42 ODR receipts | #76 Decision receipts | ODR-validator, WDR-validator |

### 2.4 Evidence Cache & Freshness

| Cache Tier | Source | Max Age | Refresh Trigger |
|------------|--------|---------|-----------------|
| Hot | Evidence intake (#33) | 7 days | Any qualification request |
| Warm | Pipeline health (#38) | 30 days | Startup surface regeneration |
| Cold | Custody receipts (#26) | 90 days | Seal review |

---

## Part III — Qualification Execution Model

### 3.1 Inputs

| Input | Source | Required |
|-------|--------|----------|
| Target ID | Specified by caller | Yes |
| Qualification type | Specified by caller | Yes |
| Qualification criteria | From framework defaults or override | No (use defaults) |
| Evidence refs | Auto-discovered from pipeline | No (minimal if absent) |

### 3.2 Execution Flow

```
1. RESOLVE
   └─ Load target from QA Pilot data store
   └─ Identify target type from target_id prefix/pattern
   └─ Load default qualification criteria for target type

2. COLLECT
   └─ Discover available evidence from pipeline layers
   └─ Filter by freshness (exclude stale > 90d)
   └─ Verify each evidence ref (schema validation, file existence)

3. EVALUATE
   └─ Compute sub-dimension scores:
       ├─ schema_compliance: did evidence pass schema validation?
       ├─ evidence_freshness: is evidence within max age?
       ├─ evidence_diversity: how many distinct evidence types?
       ├─ authority_boundary: does evidence claim authority it shouldn't?
       └─ provenance_quality: is evidence provenance complete?
   └─ Compute overall_score (weighted average)
   └─ Map score to qualification level

4. RECORD
   └─ Create qualification record (QR-*)
   └─ Validate against schema
   └─ Write to qualification store
   └─ Update qualification index

5. REPORT
   └─ Return qualification record
   └─ Optionally update startup surface
   └─ Optionally create decision packet
```

### 3.3 Evaluation Algorithm

```
function qualify(target_id, qualification_type, criteria = null):
    # 1. Resolve target
    target = resolve_target(target_id)
    if target is None:
        return error("Target not found")

    # 2. Load criteria (defaults or override)
    q_criteria = criteria or default_criteria(target.type)

    # 3. Collect evidence
    evidence = collect_evidence(target, qualification_type)
    verified_evidence = [e for e in evidence if verify_evidence(e)]

    # 4. If no verified evidence, return unqualified
    if len(verified_evidence) == 0:
        return QualificationRecord(
            level="unqualified",
            score=0.0,
            evidence_refs=[],
            lifecycle="completed"
        )

    # 5. Compute sub-dimension scores
    scores = {
        "schema_compliance": mean([e.schema_valid for e in verified_evidence]),
        "evidence_freshness": freshness_score(verified_evidence),
        "evidence_diversity": diversity_score(verified_evidence),
        "authority_boundary": authority_score(verified_evidence),
        "provenance_quality": provenance_score(verified_evidence)
    }

    # 6. Compute overall score
    weights = {
        "schema_compliance": 0.25,
        "evidence_freshness": 0.20,
        "evidence_diversity": 0.15,
        "authority_boundary": 0.25,
        "provenance_quality": 0.15
    }
    overall = sum(scores[k] * weights[k] for k in weights)

    # 7. Map to qualification level
    level = "unqualified"
    if overall >= 0.95:
        level = "audited"
    elif overall >= 0.90:
        level = "peer_reviewed"
    elif overall >= 0.80:
        level = "spot_checked"

    # If authority boundary check fails, cap at spot_checked
    if scores["authority_boundary"] < 0.90:
        level = min(level, "spot_checked")

    # 8. Create record
    return QualificationRecord(
        record_id=generate_id("QR", qualification_type),
        qualification_type=qualification_type,
        target_id=target_id,
        target_type=target.type,
        qualification_level=level,
        evidence_refs=[ref_for(e) for e in verified_evidence],
        sub_dimension_scores=scores,
        overall_score=overall,
        lifecycle_state="completed",
        advisory_only=True,
        custody="qa-pilot-local",
        librarian_impact="none",
        assessed_at=now(),
        assessed_by=current_agent(),
        expiry_date=expiry_for(level)
    )
```

### 3.4 Lifecycle States

```
                    QUALIFICATION RECORD LIFECYCLE

     ┌──────────┐    assess()    ┌──────────────┐
     │ PROPOSED │──────────────▶│ IN PROGRESS   │
     └──────────┘               └──────┬───────┘
                                       │
                           ┌───────────┴───────────┐
                           │                       │
                           ▼                       ▼
                    ┌──────────────┐      ┌──────────────┐
                    │  COMPLETED   │      │   EXPIRED    │
                    │  (qualified) │      │  (past 90d)  │
                    └──────┬───────┘      └──────┬───────┘
                           │                     │
                           │                     │
                           ▼                     │
                    ┌──────────────┐             │
                    │ SUPERSEDED   │◀────────────┘
                    │ (by newer QR)│
                    └──────────────┘

     ┌──────────────┐
     │   REVOKED    │ (Owner action only)
     └──────────────┘
```

| State | Description | Entry Condition | Exit Condition |
|-------|-------------|-----------------|----------------|
| Proposed | Record created, not yet assessed | Schema validation pass | Start assessment |
| In Progress | Assessment running | Assessment initiated | Assessment complete |
| Completed | Assessment finished, has level | All sub-dimensions scored | Expiry or superseded |
| Expired | Past expiry date | 90d (spot_checked) / 180d (audited) since assessed_at | Re-assess |
| Superseded | Replaced by newer record | Newer QR- targeting same target_id | Archival |
| Revoked | Owner-action only | Explicit Owner revocation | Permanent |

### 3.5 Trigger Conditions

| Trigger | Action | Qualification Type |
|---------|--------|-------------------|
| Workbench item created | Auto-qualify artifact | artifact |
| Workbench item status change | Re-qualify artifact | artifact |
| Evidence ingested (#33) | Re-qualify affected targets | artifact, process |
| Pipeline health regression (#38) | Re-qualify pipeline layers | process |
| Custody receipt created (#24) | Re-qualify affected targets | process |
| Startup surface generation | Re-qualify all startup-exposed layers | artifact, process |
| Owner decision recorded (#42) | Re-qualify reviewer dimension | reviewer |
| Manual request | Explicit qualification request | all |

---

## Part IV — Boundary Definition: QA Pilot vs. Librarian

| Dimension | QA Pilot Qualification | Librarian MQR |
|-----------|----------------------|---------------|
| **Scope** | QA processes, artifacts, reviewer actions | AI Model capabilities |
| **Schema** | QR- record (this document) | MQR record |
| **Evidence source** | QA Pilot internal pipeline (#33–#160) | Model shootout runs |
| **Target types** | workbench_item, evidence_packet, result, etc. | model_id + task_category |
| **Levels** | unqualified, spot_checked, peer_reviewed, audited, exempt | unqualified, fast_pass, qualified, expert |
| **Consumer** | QA Pilot startup surface, Owner review panel | Model Router, Work Intake Agent |
| **Trust model** | 2-tier: pipeline-verified, Owner-audited | 3-tier: first-party, vetted, published |
| **Access control** | QA Pilot-local only | Librarian-managed |
| **Authority** | Advisory-only — never authorizes work | Advisory-only — recommends, Owner decides |
| **Librarian dependency** | None (contracts readable as reference) | N/A (Librarian-owned) |

---

## Part V — Auto-generated Sections

The following sections are defined for Tier 1 architecture but will be fully detailed in implementation sprints:

### V.1 Registry Impact (RCR)

Adding the Qualification Framework introduces new registry layers:
- Qualification record store (`data/qualification-records/`)
- Qualification index (`data/qualification-index/`)
- Qualification surface extension to startup

### V.2 Snapshot Baseline (SRS)

Post-Tier 1 completion, a new SRS baseline should capture:
- Qualification record count (0, initially)
- Qualification index state
- Qualification posture in startup surface
- Per-target-type qualification coverage

### V.3 Surface Extension Pattern

Following the existing startup surface extension pattern (used by #43, #50, #52, #55, #58, #75, #77, #79, #81, #83, #85, #87, #89), the Qualification Surface will be added as a new section in the startup report showing:
- Total qualified targets
- Per-level distribution
- Coverage gaps
- Latest qualification date
- Expired qualifications

---

## Part VI — Reviewer Workflow Model (Tier 3 — Defined, Not Overbuilt)

### 6.1 Reviewer Qualification

Reviewer qualification assesses whether human/Owner decision authority was correctly applied. It is the third implementation priority (after Artifact and Process).

**Scope:**
- Verify that review receipts exist and are valid
- Check that authority boundaries were respected
- Confirm that reviewer identity matches expected role
- Validate that decision timing is within expected windows

**Evidence sources:**
- #42 ODR receipts (Owner review decision receipts)
- #76 WDR receipts (workbench decision receipts)
- #90 DP decision packets
- Custody receipts proving authority checks

**Sketch (not an implementation):**
```python
def qualify_reviewer(target_id):
    receipts = find_review_receipts(target_id)
    if not receipts:
        return {"level": "unqualified", "reason": "no review receipts found"}
    
    # Check: authority boundary respected?
    authority_ok = all(r.get("authority_boundary") == "respected" for r in receipts)
    
    # Check: reviewer identity matches expectation?
    identity_ok = all(r.get("reviewer") in EXPECTED_REVIEWERS for r in receipts)
    
    # Check: timing within window?
    timing_ok = all(r.get("reviewed_at") <= r.get("deadline") for r in receipts)
    
    level = "audited" if (authority_ok and identity_ok and timing_ok) else "peer_reviewed"
    return {"level": level, "receipts_checked": len(receipts)}
```

### 6.2 Artifact Qualification (Detailed — First Implementation Target)

Artifact qualification assesses whether the output satisfies requirements. This is the **first implementation target**.

**Sub-dimensions:**

| Dimension | Weight | Source | Evaluation |
|-----------|--------|--------|------------|
| Schema compliance | 25% | Target's schema validation result | 1.0 if validated, 0.0 if not |
| Evidence freshness | 20% | Evidence timestamps | Linear decay over 90d |
| Evidence diversity | 15% | Count of distinct evidence types | Max at 5+ types |
| Authority boundary | 25% | No authority-claiming fields in target | 1.0 if clean, 0.0 if violations |
| Provenance quality | 15% | Completeness of target's provenance | Ratio of present to expected fields |

## Part VII — Reporting Surface Concepts (Tier 3 — Defined, Not Overbuilt)

### 7.1 Qualification Posture in Startup Surface

When implemented, the Qualification Framework will add to the startup surface:

```
--- Qualification Posture ---
Qualified targets:     42
By level:
  audited:             8
  peer_reviewed:      18
  spot_checked:       12
  unqualified:         3
  exempt:              1
By type:
  artifact:           30
  process:            10
  reviewer:            2
Coverage:             72/160 (45.0%)
Latest qualification:  2026-07-16
Expired:               0
```

### 7.2 Dashboard Concepts

Future dashboard/reporting surfaces (not designed, concepts only):

- **Coverage heatmap**: Per-layer-group qualification rate (visual)
- **Trend chart**: Qualification score over time for key targets
- **Gap analysis**: Which targets lack minimum required level
- **Expiry alert**: Qualifications approaching expiry date
- **Drift correlation**: Qualification score vs. pipeline health correlation

### 7.3 Report Formats

Follow existing QA Pilot surface pattern:

| Mode | Output | Precedent |
|------|--------|-----------|
| `--format text` | Human-readable summary table | #37 pipeline startup surface |
| `--format json` | Machine-readable structured data | #28 custody summary surface |
| `--format markdown` | Decision packet | #90 decision packet format |

---

## Part VIII — Staged Implementation (for Sprint Sequence)

| Phase | Sprint | What It Delivers |
|-------|--------|------------------|
| **P0** | QUALIFICATION-SCHEMA-1 | QR- schema, validator, fixtures, qualification store |
| **P1** | QUALIFICATION-EVIDENCE-PIPELINE-1 | Evidence collection from existing layers, auto-discovery |
| **P2** | QUALIFICATION-EXECUTION-1 | Evaluation engine, lifecycle management, trigger wiring |
| **P3** | QUALIFICATION-REVIEW-SURFACE-1 | Decision packet CLI, startup surface extension |
| **P4** | QUALIFICATION-ROUNDTRIP-VALIDATION-1 | End-to-end validation against real QA Pilot data |

---

*Qualification Framework Architecture prepared as part of QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1 (Tier 1). This is a planning document — no implementation, seal, or ledger mutation is authorized.*
