# QA-PILOT-EVIDENCE-CHECKLIST.md — QA Pilot Evidence Checklist

**Status:** 🔍 Active (sprint #44)
**Authority:** Advisory-only. No approval, seal, execution, write, or sprint-start authority conferred.
**Custody:** QA Pilot-local only. No Librarian mutation permitted.

---

## 1. Purpose

Define the first bounded QA Pilot checklist layer. A checklist is a contract that enumerates what evidence must exist before a QA claim is reviewable. It consumes sealed risk-register evidence pointers from the existing pipeline (#33-#43) and turns them into explicit, reviewable QA evidence requirements.

---

## 2. Definitions

| Term | Definition |
|------|-----------|
| **Evidence Checklist** | A QA Pilot-local packet (`EC-*`) enumerating evidence requirements for a specific QA claim or review scope. |
| **Checklist Item** | A single evidence requirement (`ECI-*`) within a checklist, with its own class, state, and evidence references. |
| **Evidence Class** | `required` — evidence must exist for the QA claim to be reviewable; `optional` — evidence strengthens but does not block review. |
| **Checklist State** | `blocked` — prerequisite missing or broken; `degraded` — evidence exists with known gaps; `ready` — sufficient evidence present. |
| **Pipeline Ref** | Reference to a sealed pipeline layer (evidence intake, test composition, result export, epic regression, etc.) that provides the evidence. |

---

## 3. Schema

The evidence checklist schema is defined at `docs/schemas/qa-pilot-evidence-checklist.schema.json` (Draft 2020-12).

### 3.1 Required Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `checklist_id` | string (pattern `^EC-[A-Z0-9-]+$`) | Unique checklist identifier |
| `title` | string | Human-readable name |
| `description` | string (min 10 chars) | Scope this checklist covers |
| `evidence_class` | enum (`required`, `optional`) | Whether the whole checklist is required |
| `items` | array (min 1) | Evidence requirement items |
| `pipeline_refs` | array (min 1) | References to sealed pipeline layers |
| `advisory_only` | boolean (`true`) | Always advisory |
| `custody` | string (`qa-pilot-local`) | Local custody only |
| `librarian_impact` | string (`none`) | No Librarian mutation |

### 3.2 Checklist Item Fields

| Field | Type | Description |
|-------|------|-------------|
| `item_id` | string (pattern `^ECI-[A-Z0-9-]+$`) | Unique item identifier |
| `description` | string | What evidence is required |
| `evidence_class` | enum (`required`, `optional`) | Item-level class override |
| `state` | enum (`blocked`, `degraded`, `ready`) | Current readiness |
| `rationale` | string (min 10 chars) | Why this evidence is required |
| `evidence_refs` | array | References to pipeline evidence |

### 3.3 State Definitions

| State | Meaning | Reviewable? |
|-------|---------|-------------|
| `blocked` | Prerequisite missing or broken; review cannot proceed | No |
| `degraded` | Evidence exists with known gaps; review may proceed with caveats | Advisory |
| `ready` | Sufficient evidence present; review may proceed | Yes |

---

## 4. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| EC-1 | Checklist must conform to qa-pilot-evidence-checklist.schema.json | Schema |
| EC-2 | advisory_only must be true | Schema const |
| EC-3 | custody must be qa-pilot-local | Schema pattern |
| EC-4 | librarian_impact must be none | Schema const |
| EC-5 | At least one checklist item required | Schema minItems |
| EC-6 | At least one pipeline ref required | Schema minItems |
| EC-7 | Items with state=blocked must include rationale | Schema conditional |
| EC-8 | Item IDs must be unique within a checklist | Validator |
| EC-9 | Pipeline refs must reference known sealed layers (#33-#43) | Validator |
| EC-10 | No approval, seal, execute, write, or sprint-start authority claimed | Validator |
| EC-11 | All pipeline refs reference QA Pilot-local custody only | Validator |
| EC-12 | No Librarian mutation authority referenced | Validator |

---

## 5. Pipeline References

Evidence checklists link to the sealed advisory pipeline layers. The recognized layers are:

| # | Layer | Sprint ID |
|---|-------|-----------|
| 33 | Evidence Intake | QA-PILOT-MCP-EVIDENCE-INTAKE-1 |
| 34 | Test Composition | QA-PILOT-TEST-COMPOSITION-1 |
| 35 | Result Export | QA-PILOT-RESULT-PACKET-EXPORT-1 |
| 36 | Epic Regression Builder | QA-PILOT-EPIC-REGRESSION-BUILDER-1 |
| 37 | Pipeline Startup Surface | QA-PILOT-EPIC-REGRESSION-STARTUP-SURFACE-1 |
| 38 | Pipeline Health Regression | QA-PILOT-PIPELINE-HEALTH-REGRESSION-1 |
| 39 | Drift Detection | QA-PILOT-PIPELINE-DRIFT-DETECTION-1 |
| 40 | Recovery Diagnostics | QA-PILOT-PIPELINE-RECOVERY-DIAGNOSTICS-1 |
| 41 | Owner Review Packet | QA-PILOT-PIPELINE-OWNER-REVIEW-PACKET-1 |
| 42 | Owner Decision Receipt | QA-PILOT-OWNER-REVIEW-DECISION-RECEIPT-1 |
| 43 | ODR Startup Surface | QA-PILOT-OWNER-DECISION-RECEIPT-STARTUP-SURFACE-1 |

---

## 6. Authority

- **Advisory-only.** Evidence checklists are advisory artifacts. They do not approve, seal, execute, write, or authorize sprint starts.
- **QA Pilot-local custody.** All checklist data resides within QA Pilot-local paths only.
- **No Librarian mutation.** Checklist validation rejects any reference to Librarian mutation authority.
- **Existing boundaries preserved.** The #33-#43 advisory-only custody boundaries are unchanged by this contract.
- **No cross-project write authorization.** Checklist items cannot authorize writes outside QA Pilot.

---

## 7. Invariants

| # | Invariant | Enforcement |
|---|-----------|-------------|
| I-1 | All valid checklist packets must pass schema validation | Schema + validator |
| I-2 | All invalid fixtures must fail schema validation | Validator |
| I-3 | advisory_only=true invariant is unchangeable | Schema const |
| I-4 | custody=qa-pilot-local invariant is unchangeable | Schema pattern |
| I-5 | librarian_impact=none invariant is unchangeable | Schema const |
| I-6 | No checklist item may claim approval/seal/execute/write authority | Validator |
| I-7 | No pipeline ref may reference Librarian custody | Validator |
| I-8 | All existing #33-#43 validators and test runners remain green | Regression |
