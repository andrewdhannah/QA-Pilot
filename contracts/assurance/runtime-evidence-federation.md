# Runtime Evidence Federation Contract

**Sprint:** QA-PILOT-RUNTIME-EVIDENCE-FEDERATION-1 (#223)
**Status:** ACTIVE — Authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define the governed multi-project runtime evidence boundary. Establish how QA-Pilot consumes runtime evidence from multiple projects while preserving source ownership, evidence provenance, authority separation, and project isolation.

## 2. Core Principles

### 2.1 Source Ownership

Projects own their evidence. QA-Pilot evaluates evidence. It does not become the evidence authority.

```
Project Runtime
       │
       △
Evidence Produced (project-owned)
       │
       △
QA-Pilot Qualification (evaluator)
       │
       △
Qualification Result (advisory-only)
```

### 2.2 No Centralized Authority

Federation does not create a central evidence authority. Each project retains:
- Ownership of its evidence
- Authority over its runtime
- Control over its adapter

### 2.3 Project Isolation

Evidence from Project A cannot:
- Alter Project B records
- Satisfy Project B qualification requirements
- Create Project B authority context

## 3. Project Identity Schema

Every runtime evidence object must carry canonical project identity:

```json
{
  "project_identity": {
    "project_id": "string (required)",
    "project_instance": "string (required)",
    "identity_source": "string (required)"
  }
}
```

| Field | Purpose | Example |
|-------|---------|---------|
| `project_id` | Canonical project identifier | `"librarian"`, `"qa-pilot"`, `"agent-bridge"` |
| `project_instance` | Specific runtime instance | `"librarian-prod-node-001"` |
| `identity_source` | Where the identity was verified | `"librarian-registry"`, `"qa-pilot-profile"` |

**Rule:** QA-Pilot must never infer project identity from runtime identity. The adapter must provide explicit project identity.

## 4. Adapter Contract

### 4.1 Adapter Responsibilities

| Responsibility | Owner | Description |
|----------------|-------|-------------|
| Extraction | Adapter | Extract runtime events from project-specific format |
| Translation | Adapter | Translate to QA-Pilot evidence schema |
| Project mapping | Adapter | Map project-specific concepts to canonical identity |
| Identity assertion | Adapter | Assert project_identity with identity_source |

### 4.2 QA-Pilot Responsibilities

| Responsibility | Owner | Description |
|----------------|-------|-------------|
| Validation | QA-Pilot | Validate evidence against schema and provenance rules |
| Qualification | QA-Pilot | Evaluate evidence against qualification checks |
| Evidence result | QA-Pilot | Produce advisory-only qualification result |
| Isolation enforcement | QA-Pilot | Prevent cross-project contamination |

### 4.3 Adapter Interface

```python
class RuntimeEvidenceAdapter:
    """Interface for project-specific runtime evidence adapters."""
    
    def extract(self, source) -> list[RuntimeEvent]:
        """Extract runtime events from project source."""
        pass
    
    def translate(self, event) -> dict:
        """Translate project event to QA-Pilot evidence format."""
        pass
    
    def project_identity(self) -> ProjectIdentity:
        """Return canonical project identity for this adapter."""
        pass
    
    def validate(self, event) -> bool:
        """Validate event before ingestion."""
        pass
```

## 5. Evidence Store Layout

```
data/runtime-evidence/
  projects/
    qa-pilot/
      records/
      snapshots/
    librarian/
      records/
      snapshots/
  index.json                    # Cross-project index (read-only aggregation)
  qualification-results.json    # Per-project qualification results
```

**Rule:** Each project's evidence is stored in its own directory. The cross-project index is read-only and never modifies project evidence.

## 6. Federation Rules

| Rule ID | Rule | Enforcement |
|---------|------|-------------|
| FED-R1 | Every evidence record must have canonical project_identity | Schema validation |
| FED-R2 | Project identity must come from adapter, not be inferred | Adapter contract |
| FED-R3 | Evidence directories are per-project, never shared | Store layout |
| FED-R4 | Cross-project index is read-only | Store invariant |
| FED-R5 | Qualification runs per-project, not cross-project | Qualification engine |
| FED-R6 | No evidence mutation across project boundaries | Isolation enforcement |
| FED-R7 | Adapter must not introduce authority fields | CAG-RUNTIME-008 |

## 7. Qualification After Federation

Qualification becomes per-project:

```
Project A Evidence
       │
       △
Qualify(Project A) → Result A

Project B Evidence
       │
       △
Qualify(Project B) → Result B
```

NOT:
```
Project A + Project B Evidence
       │
       △
Qualify(merged) → Single Result (wrong)
```

## 8. Discovery Metadata

Every project's evidence store carries metadata for future discovery:

```json
{
  "project_id": "librarian",
  "evidence_coverage": {
    "total_records": 0,
    "total_snapshots": 0,
    "last_ingested_at": null,
    "qualification_status": "untested"
  },
  "adapter": {
    "adapter_id": "librarian-runtime-adapter",
    "adapter_version": "1.0.0",
    "supported_event_types": ["runtime_action", "runtime_lifecycle", "runtime_resource"]
  }
}
```

This metadata supports future queries like "What projects have runtime assurance coverage?" without implementing LINK integration.
