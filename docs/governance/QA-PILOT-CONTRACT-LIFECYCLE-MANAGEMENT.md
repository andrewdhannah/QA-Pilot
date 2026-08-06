# QA Pilot Contract Lifecycle Management

**Purpose:** Define how contracts within the QA-Pilot framework are versioned, migrated, deprecated, and retired. Prevents drift between contracts, adapters, validators, and test assets as the framework grows.

**Effective:** 2026-07-24
**Applies to:** All contracts in `qa-pilot-manifest.json`

---

## 1. Contract Versioning

### 1.1 Version Schema

All QA-Pilot contracts use semantic versioning: `v<major>.<minor>`

| Component | When It Changes | Example |
|---|---|---|
| **Major** | Breaking change to required fields, enum values, or structural constraints | `v1` → `v2` |
| **Minor** | Adding optional fields, expanding enums, relaxing constraints | `v1.0` → `v1.1` |

### 1.2 Version Declaration

Every contract schema **must** declare its version in the `$id` field:

```json
{
  "$id": "https://github.com/andrewdhannah/QA-Pilot/schemas/learning-object-v1.schema.json",
  "title": "Learning Object v1"
}
```

The version is extracted from the schema filename: `learning-object-v1.schema.json` → version `v1`.

### 1.3 Version Compatibility

| Version Difference | Compatibility | Validator Behavior |
|---|---|---|
| Same major version | Backward compatible | All existing validators pass |
| New minor version | Forward compatible (optional fields only) | Existing validators pass; new fields ignored |
| New major version | Breaking — requires migration | Old validators fail; migration path required |

---

## 2. Contract Registry

The `qa-pilot-manifest.json` is the authoritative registry of all active contracts.

### 2.1 Contract Entry Requirements

Each contract in the manifest **must** include:

```json
{
  "learning_object_v1": {
    "schema": "docs/schemas/learning-object-v1.schema.json",
    "version": "v1",
    "status": "stable",                // stable | beta | deprecated
    "validators": ["scripts/validate-learning-object.py"],
    "deprecated_at": null,             // ISO date when deprecated
    "sunset_at": null                  // ISO date when removed
  }
}
```

### 2.2 Contract Status Lifecycle

```
draft → beta → stable → deprecated → sunset → removed
```

| Status | Meaning | Validator Behavior |
|---|---|---|
| `draft` | In development, not yet registered | No validators required |
| `beta` | Published but may change | Validators warn on beta use |
| `stable` | Published and guaranteed compatible | Normal validation |
| `deprecated` | Still works but scheduled for removal | Validators warn on deprecation |
| `sunset` | No longer available | Validators fail |
| `removed` | Deleted from registry | N/A |

### 2.3 Transition Rules

| Transition | Requires | Minimum Notice |
|---|---|---|
| draft → beta | Schema file exists | None |
| beta → stable | Validation suite exists, 1+ operational use | None |
| stable → deprecated | Replacement contract exists | 2 release cycles |
| deprecated → sunset | Migration path documented | 4 release cycles |
| sunset → removed | Notification sent | 1 release cycle |

---

## 3. Migration Rules

### 3.1 When Migration Is Required

Migration is required when moving from one major contract version to another (e.g., `learning-object-v1` → `learning-object-v2`).

### 3.2 Migration Path Requirements

Every major version change **must** provide a migration path that includes:

1. **Migration document** — explains what changed and why
2. **Schema diff** — exact field-level differences between versions
3. **Migration script** (if automated) — converts v1 instances to v2
4. **Coexistence period** — both versions validatable during transition

### 3.3 Migration Document Template

```markdown
# Migration: learning-object-v1 → learning-object-v2

## What Changed
- `source.finding_code` now requires `EV-` prefix (was optional)
- `certification.criteria` now requires `minLength: 10` on `description`

## Schema Diff
- ADDED: `source.finding_code` pattern restriction
- CHANGED: `certification.criteria[].description` minLength 1 → 10

## Migration Script
python3 scripts/migrate-learning-object-v1-to-v2.py <input> <output>

## Coexistence Period
Both v1 and v2 validators will pass for 2 release cycles.
After that, only v2 validators will be maintained.

## Verification
Run: python3 validators/validate-learning-object.py --schema v2
```

### 3.4 Zero-Downtime Migration

Contracts **must** support zero-downtime migration:

1. Add v2 schema alongside v1
2. Update validators to accept both versions during coexistence
3. Migrate all instances from v1 to v2
4. Deprecate v1
5. Remove v1 after sunset

---

## 4. Deprecation Policy

### 4.1 Deprecation Signals

A contract is eligible for deprecation when:

- A newer major version has been stable for 2+ release cycles
- No active adapter depends on it
- No active test references it
- The manifest `contracts` entry shows zero consumers

### 4.2 Deprecation Process

1. **Mark as deprecated** — set `status: "deprecated"` in manifest
2. **Notify consumers** — validators emit warnings when deprecated contracts are used
3. **Migration window** — 4 release cycles before sunset
4. **Remove** — set `status: "sunset"`, validators fail on use
5. **Delete** — set `status: "removed"`, remove from manifest

### 4.3 Deprecation Example

```json
{
  "receipt_v1": {
    "schema": "docs/schemas/qa-pilot-receipt.schema.json",
    "version": "v1",
    "status": "deprecated",
    "deprecated_at": "2026-09-01",
    "sunset_at": "2027-01-01",
    "replaced_by": "receipt_v2",
    "migration_path": "docs/migrations/receipt-v1-to-v2.md"
  }
}
```

---

## 5. Compatibility Guarantees

### 5.1 Within-Major-Version Compatibility

Within the same major version, contracts **guarantee**:

- All required fields remain required
- All field types remain the same
- All enum values remain valid (new values may be added)
- All patterns remain compatible (may be relaxed, not tightened)
- All constraints remain valid (may be relaxed, not tightened)

### 5.2 Validator Compatibility

Validators **must**:

- Accept all minor versions within their major version
- Reject schemas from different major versions (with clear error)
- Warn on deprecated contract usage
- Report the version they validated against

### 5.3 Adapter Compatibility

Adapters **must** declare which contract versions they support:

```json
{
  "adapter_id": "scenario_adapter",
  "supported_contracts": {
    "learning_object": ">=v1.0, <v2.0",
    "epic_scenario": ">=v1.0"
  }
}
```

---

## 6. Test Library Ownership

### 6.1 Test Definition Lifecycle

Each test in the library **must** declare:

```json
{
  "test_id": "REG-001",
  "title": "Cursor freshness regression",
  "contract_version": "learning-object-v1",
  "added_at": "2026-07-01",
  "maintainer": "qa-pilot-core",
  "status": "active",         // active | deprecated | archived
  "deprecated_at": null
}
```

### 6.2 Test-to-Contract Binding

Tests are bound to specific contract versions. When a contract is deprecated:

1. Tests targeting that version are flagged
2. A migration window opens (same as contract)
3. Tests must be updated to target the new version
4. After sunset, tests are archived

### 6.3 Ownership Rules

| Asset | Owner | Review Cadence |
|---|---|---|
| Core contracts (learning-object, SDK, epic-scenario) | QA-Pilot core | Each release cycle |
| Domain tests (security, accessibility, etc.) | Domain owner | Each domain update |
| Project-specific adapters | Project owner | On project change |
| Migration scripts | QA-Pilot core | Each major version change |

---

## 7. Adapter Lifecycle

### 7.1 Adapter Version Declaration

Every adapter in the manifest **must** declare:

```json
{
  "id": "scenario_adapter",
  "version": "v1",
  "entry_point": "scripts/qa_pilot_scenario_adapter.py",
  "supported_contracts": {
    "learning_object": "v1"
  },
  "status": "stable",
  "deprecated_at": null
}
```

### 7.2 Adapter Deprecation

Adapters follow the same lifecycle as contracts:

```
stable → deprecated → sunset → removed
```

An adapter is deprecated when:

- All contracts it depends on are deprecated
- A newer adapter replaces its functionality
- No active tests reference it

---

## 8. Enforcement

Compliance with this policy is enforced by the compatibility validator:

```
validate-qa-pilot-compatibility.py
  ├── PC-3:  All declared contract schemas exist on disk
  ├── PC-4:  All declared validators exist on disk
  ├── PC-5:  All capability entry points exist on disk
  └── LC-1 through LC-5:  (lifecycle checks — see below)
```

### Lifecycle Validation Rules

| Rule | Check |
|---|---|
| **LC-1** | All contracts in manifest have `status` field |
| **LC-2** | All `deprecated` contracts have `deprecated_at` date |
| **LC-3** | All `deprecated` contracts have `replaced_by` or `migration_path` |
| **LC-4** | No `sunset` contract is still referenced by active adapters |
| **LC-5** | All `stable` contracts have at least one validator declared |

---

## 9. Summary

| Policy | Rule |
|---|---|
| Version schema | Semantic: `v<major>.<minor>` |
| Contract lifecycle | `draft → beta → stable → deprecated → sunset → removed` |
| Migration requirement | Required for major version changes |
| Minimum deprecation notice | 4 release cycles |
| Compatibility scope | Within major version only |
| Validator requirement | Every stable contract needs at least one validator |
| Adapter declaration | Every adapter declares supported contract versions |

---

*This policy is governed by the QA-Pilot framework. Status: 🔍 Pending Owner verification.*
