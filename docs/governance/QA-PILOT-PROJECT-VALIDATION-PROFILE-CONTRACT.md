# QA Pilot Project Validation Profile Contract

**Purpose:** Bridge between project startup and QA-Pilot validation. Defines what testing applies to a given project, which domains are enabled, and what review gates are required.

**Architecture:**

```
STARTUP CONTRACT
    │
    ├── identifies project
    ├── loads capabilities
    ├── exposes validation availability
    │
    ▼
VALIDATION PROFILE (this contract)
    │
    ├── selects test domains
    ├── references applicable contracts
    ├── specifies review gates
    │
    ▼
QA-PILOT PIPELINE
    │
    ├── runs domain tests
    ├── produces validation package
    └── reports for owner review
```

**Schema:** `docs/schemas/qa-project-validation-profile.schema.json`

---

## 1. Purpose

Ensure that every governed project knows what QA-Pilot validation applies to it. The startup contract announces `qa-pilot is available`. The validation profile answers `qa-pilot means these tests, these contracts, and these review gates for your project`.

## 2. Profile Resolution

At startup, the project resolves its validation profile:

```
start <project-id>
    │
    ▼
Project identity resolved
    │
    ├── Check for project validation profile
    ├── If found: load profile → configure pipeline
    └── If not found: use default profile based on project_type
    │
    ▼
Pipeline ready
```

### Default Profiles by Project Type

| Project Type | Default Domains | Review Gate |
|---|---|---|
| `governance` | regression, security, uat, accessibility, ai | Owner |
| `mcp_bridge` | regression, security | Owner |
| `add_on` | regression, security, uat | Owner |
| `extension` | regression, security | Owner |
| `runtime` | regression, security, performance | Owner |
| `tracker` | regression | Peer |
| `external` | regression | Automated only |

## 3. Example: Librarian Validation Profile

```json
{
  "profile_schema": "qa-project-validation-profile-v1",
  "project_id": "librarian",
  "project_type": "governance",
  "validation_profile": "release-validation-v1",
  "qa_pilot_version": "1.0.0",
  "enabled_domains": [
    "regression",
    "security",
    "uat",
    "accessibility",
    "ai"
  ],
  "required_reviews": ["owner"],
  "contract_refs": [
    "learning-object-v1",
    "qa-pilot-sdk-integration",
    "qa-pilot-epic-scenario-suite",
    "qa-pilot-receipt"
  ],
  "evidence_source": "sdk",
  "startup_routing": {
    "available": true,
    "next_pipeline_action": "run-pipeline"
  }
}
```

## 4. Startup Integration

The startup flow should:

1. Resolve project identity (existing)
2. Load startup contract (existing)
3. Resolve validation profile (new — this contract)
4. If `startup_routing.available` is true, QA-Pilot pipeline is ready
5. Set `next_pipeline_action` based on state:
   - `run-pipeline`: First validation run needed
   - `review-last`: Previous results available for review
   - `configure-adapter`: Project adapter needs setup

## 5. Files

| File | Description |
|---|---|
| `docs/schemas/qa-project-validation-profile.schema.json` | Profile schema |
| `docs/governance/QA-PILOT-PROJECT-VALIDATION-PROFILE-CONTRACT.md` | This contract document |
| `profiles/librarian-validation-profile.json` | Librarian validation profile (example) |

## 6. Key Invariants

| Invariant | Enforcement |
|---|---|
| QA-Pilot determines what tests apply | Profile declares enabled_domains |
| Startup does not embed test rules | Profile references contracts, does not inline them |
| Every project knows its review gate | required_reviews is mandatory |
| Validation profiles are advisory | advisory_only: true in schema |
