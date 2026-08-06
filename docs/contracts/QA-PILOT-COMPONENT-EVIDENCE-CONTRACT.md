# QA Pilot Component Evidence Contract

**Sprint:** QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1
**Status:** Planning — defines the contract connecting components to code locations for test generation
**Relationship:** This contract extends the existing Node Registry profile, it does not create a new identity system.

---

## 0. Core Principle

Tests must trace to real implementation locations. The component evidence contract defines how a Node Registry component's profile maps to the code, interfaces, and authority boundaries that a test generator consumes.

This contract does **not** create a new component identity system. It extends the existing Node Registry profile with qualification-relevant metadata.

---

## 1. Contract Structure

The component evidence contract is embedded within the Node Profile. It does not exist as a separate file. The extension adds a `qualification_target` block to the existing node profile.

### 1.1 Profile Extension

```json
{
  "node_id": "NODE-OWNER-QUEUE",
  "node_type": "governance_component",
  "display_name": "Owner Queue",

  "qualification_target": {
    "enabled": true,
    "domains": ["functional", "security", "ai_governance"],

    "locations": {
      "source_files": [
        {
          "path": "Sources/OwnerQueue/OwnerQueueService.swift",
          "symbols": ["submitOwnerAction", "validateAuthority"],
          "lines": "1-245"
        },
        {
          "path": "Sources/OwnerQueue/OwnerQueueModels.swift",
          "symbols": ["OwnerActionRequest", "OwnerActionResponse"],
          "lines": "1-89"
        }
      ],
      "routes": [
        {
          "method": "POST",
          "path": "/api/owner/action",
          "authority": "owner_only"
        },
        {
          "method": "GET",
          "path": "/api/owner/pending",
          "authority": "owner_only"
        }
      ],
      "schemas": [
        {
          "name": "owner-action-request",
          "path": "docs/schemas/owner-action-request.schema.json"
        }
      ],
      "database_tables": ["owner_actions", "owner_queue"],
      "configuration_keys": ["owner.queue.timeout", "owner.queue.retry_limit"]
    },

    "test_references": {
      "existing_test_files": [
        "Tests/OwnerQueueTests.swift"
      ],
      "existing_test_identities": [
        "OWNER-QUEUE-FUNC-001",
        "OWNER-QUEUE-FUNC-002"
      ]
    }
  }
}
```

### 1.2 Field Reference

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `qualification_target.enabled` | Yes | boolean | Whether this component participates in qualification |
| `qualification_target.domains` | Yes | string[] | Which qualification domains apply to this component |
| `locations.source_files[].path` | Yes | string | Relative path from project root |
| `locations.source_files[].symbols` | No | string[] | Exported symbols/functions in this file |
| `locations.source_files[].lines` | No | string | Line range for the component's primary definition |
| `locations.routes[].method` | Yes (if routes exist) | string | HTTP method |
| `locations.routes[].path` | Yes (if routes exist) | string | URL path |
| `locations.routes[].authority` | Yes (if routes exist) | string | Authority level required |
| `locations.schemas[].name` | No | string | Schema reference name |
| `locations.schemas[].path` | No | string | Schema file path |
| `locations.database_tables` | No | string[] | Database tables owned/used by this component |
| `locations.configuration_keys` | No | string[] | Configuration keys relevant to this component |
| `test_references.existing_test_files` | No | string[] | Known test files for this component |
| `test_references.existing_test_identities` | No | string[] | Known test identity IDs associated with this component |

---

## 2. How the Generator Uses This Contract

### 2.1 Structural Test Generation

The generator iterates over `locations.routes` to produce interface tests:

```
For each route:
  1. Determine authority level (from route.authority)
  2. Generate authentication tests (unauthenticated → expected 401)
  3. Generate authorization tests (wrong authority → expected 403)
  4. Generate method tests (wrong HTTP method → expected 405)

Example output for POST /api/owner/action (owner_only):
  - AUTH-OWNER-QUEUE-001: GET /api/owner/action → 405
  - AUTH-OWNER-QUEUE-002: POST /api/owner/action (no auth) → 401
  - AUTH-OWNER-QUEUE-003: POST /api/owner/action (non-owner) → 403
  - AUTH-OWNER-QUEUE-004: POST /api/owner/action (owner) → 200/201
```

### 2.2 Behavioral Test Generation

The generator uses `locations.schemas[]` to derive contract tests:

```
For each schema:
  1. Parse required fields
  2. Generate missing-field rejection tests
  3. Generate type-mismatch tests
  4. Generate boundary-value tests (min/max length, range, pattern)

Example output for owner-action-request schema:
  - BEH-OWNER-QUEUE-001: Missing "receipt_id" → 400
  - BEH-OWNER-QUEUE-002: Missing "actor_id" → 400
  - BEH-OWNER-QUEUE-003: Invalid "receipt_id" format → 400
```

### 2.3 Adversarial Test Generation

The generator uses component metadata (node_type, route.authority, existing classification) to derive adversarial tests:

```
For each component with authority_boundary or security_relevant classification:
  1. Apply classification-to-category mapping (from taxonomy)
  2. Generate adversarial template suite

Example output for NODE-OWNER-QUEUE (authority_boundary, owner_only):
  - ADV-OWNER-QUEUE-001: Privilege escalation via modified authority token
  - ADV-OWNER-QUEUE-002: Receipt forgery in request body
  - ADV-OWNER-QUEUE-003: Replay attack with captured request
  - ADV-OWNER-QUEUE-004: Malformed owner action payload
```

---

## 3. Code Location Provenance

Every generated test must carry the evidence of where it came from.

### 3.1 Test → Code Linking

```json
{
  "test_identity": "AUTH-OWNER-QUEUE-001",
  "revision": 2,
  "generated_from": {
    "node_id": "NODE-OWNER-QUEUE",
    "location_type": "route",
    "source": "POST /api/owner/action",
    "authority": "owner_only",
    "file_references": [
      {
        "path": "Sources/OwnerQueue/OwnerQueueService.swift",
        "symbol": "submitOwnerAction",
        "line": 87
      }
    ]
  },
  "execution_receipt": "receipts/qualification/AUTH-OWNER-QUEUE-001-rev2.json"
}
```

### 3.2 Provenance Chain

```
Registry Entry (NODE-OWNER-QUEUE)
    ↓
Qualification Target (profile extension)
    ↓
Source File Reference (OwnerQueueService.swift:87)
    ↓
Generated Test (AUTH-OWNER-QUEUE-001)
    ↓
Execution
    ↓
Receipt with Code References
```

A reviewer can trace from a test result back to the exact implementation line that was tested, through the registry identity.

---

## 4. Contract Validation Rules

| # | Rule | Enforcement |
|---|------|-------------|
| 1 | `qualification_target.enabled` must be boolean | Schema validation |
| 2 | If enabled, at least one location type must be present | Schema validation |
| 3 | Source file paths must be relative to project root | Validator check |
| 4 | Source file paths must reference existing files (when evaluated) | Runtime check |
| 5 | Route paths must not be duplicated across components | Registry consistency check |
| 6 | Route authority must be a valid value (owner_only, agent, public, system) | Enum validation |
| 7 | Schema paths must reference existing files | Runtime check |
| 8 | Test references must reference existing test identity IDs | Cross-reference check |

---

## 5. Default Contract

Components that do not have a `qualification_target` block are treated as:

```json
{
  "qualification_target": {
    "enabled": false,
    "domains": []
  }
}
```

They are excluded from qualification entirely. No coverage gap is reported. This preserves backward compatibility with existing Node Profiles.

---

## 6. Contract Updates

The qualification target is updated as part of the Node Profile lifecycle:

| Event | Qualification Target Action |
|-------|---------------------------|
| New component registered | Add qualification_target block (default: disabled) |
| Component source changes | Update source file references, route list |
| Component deprecation | Set enabled: false |
| Component removed | Remove qualification_target block entirely |

Updates follow the existing Node Registry update protocol (candidate → owner action → apply → registry).

---

## 7. Acceptance Gates

| Gate | Requirement |
|------|-------------|
| CE-P1 | Qualification target extension defined as Node Profile addition (not separate file) |
| CE-P2 | Source file reference format defined with path, symbols, lines |
| CE-P3 | Route reference format defined with method, path, authority |
| CE-P4 | Schema reference format defined with name, path |
| CE-P5 | Test-to-code provenance linking defined |
| CE-P6 | Validation rules defined (8 rules) |
| CE-P7 | Default contract defined (disabled for backward compatibility) |
| CE-P8 | Contract update lifecycle documented |
| CE-P9 | No duplicate identity system created |

---

*Component evidence contract for QA-PILOT-QUALIFICATION-FOUNDATION-PLANNING-1. Planning only. No implementation authority conferred.*
