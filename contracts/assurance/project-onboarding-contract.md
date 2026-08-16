# Project Onboarding Contract

**Sprint:** QA-PILOT-PROJECT-ONBOARDING-1 (#232)
**Status:** ACTIVE — Authorized 2026-08-16
**Boundary:** QA Pilot-local advisory surface only

---

## 1. Purpose

Define the repeatable onboarding path for new governed projects entering the assurance ecosystem.

## 2. Onboarding State Model

```
registered
      │
      △
evidence_connected
      │
      △
qualification_ready
      │
      △
assurance_active
```

### State Definitions

| State | Meaning | Requirements |
|-------|---------|--------------|
| `registered` | Project identity validated | Valid project_id, project_instance, identity_source |
| `evidence_connected` | Evidence sources reachable | At least one evidence domain declared and verified |
| `qualification_ready` | Profiles mapped | Default qualification profiles assigned |
| `assurance_active` | Full assurance participation | All above + freshness policy + LINK projection |

## 3. Onboarding Record

```json
{
  "onboarding_id": "ONB-20260816-001",
  "project_id": "new-project",
  "onboarded_at": "2026-08-16T05:00:00Z",
  "adapter_version": "1.0.0",
  "state": "assurance_active",
  "identity": {
    "project_id": "new-project",
    "project_instance": "new-project-prod-001",
    "identity_source": "project-registry"
  },
  "evidence_sources": {
    "domains": ["runtime_action", "runtime_lifecycle"],
    "provenance_complete": true
  },
  "qualification_profiles": {
    "default_profile": "RUNTIME-STANDARD",
    "artifact_mappings": {
      "runtime_action": "RUNTIME-STANDARD",
      "runtime_lifecycle": "RUNTIME-STANDARD"
    }
  },
  "freshness_policy": {
    "record_threshold_minutes": 60,
    "snapshot_refresh_minutes": 15
  },
  "link_projection": {
    "visible": true,
    "generated_at": "2026-08-16T05:00:00Z"
  },
  "isolation_verified": true,
  "advisory_only": true
}
```

## 4. Onboarding Validation Rules

| Rule | Check | Failure |
|------|-------|---------|
| PO-R1 | project_id is non-empty string | Reject onboarding |
| PO-R2 | project_instance is non-empty string | Reject onboarding |
| PO-R3 | identity_source is non-empty string | Reject onboarding |
| PO-R4 | At least one evidence domain declared | State = registered |
| PO-R5 | Evidence domain is valid type | Reject domain |
| PO-R6 | Provenance fields complete | State = evidence_connected |
| PO-R7 | Qualification profile exists | State = qualification_ready |
| PO-R8 | Freshness policy configured | State = assurance_active |
| PO-R9 | LINK projection generated | Visibility confirmed |
| PO-R10 | Isolation directories created | No cross-project paths |

## 5. Isolation Invariant

Onboarding MUST NOT create cross-project dependencies:

```
QA-Pilot Evidence
        ≠
Librarian Evidence
        ≠
New Project Evidence
```

QA-Pilot can compare and aggregate. It cannot merge ownership or authority.

## 6. Adapter Interface

```python
class ProjectAssuranceAdapter:
    """Interface for project onboarding."""
    
    def validate_identity(self, project_config) -> bool:
        """Validate project identity."""
        pass
    
    def register_evidence_sources(self, project_id, domains) -> bool:
        """Register evidence sources."""
        pass
    
    def verify_provenance(self, project_id) -> bool:
        """Verify provenance chain."""
        pass
    
    def map_qualification_profiles(self, project_id, artifact_types) -> dict:
        """Map qualification profiles."""
        pass
    
    def assign_freshness_policy(self, project_id) -> dict:
        """Assign freshness policy."""
        pass
    
    def generate_link_projection(self, project_id) -> bool:
        """Generate LINK projection."""
        pass
    
    def verify_isolation(self, project_id) -> bool:
        """Verify project isolation."""
        pass
```
