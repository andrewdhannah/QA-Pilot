#!/usr/bin/env python3
"""
Project Onboarding Engine — QA-PILOT-PROJECT-ONBOARDING-1

Repeatable onboarding path for new governed projects.

Commands:
  onboard <project_id> <instance> <identity_source>    Onboard a new project
  status <project_id>                                  Show onboarding status
  list                                                 List all onboarded projects
  history                                              Show onboarding history
"""

import sys
import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# --- Configuration ---

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "assurance"
ONBOARDING_DIR = DATA_DIR / "onboarding-records"
EVIDENCE_STORE = PROJECT_ROOT / "data" / "runtime-evidence"
PROJECTS_DIR = EVIDENCE_STORE / "projects"

# Valid evidence domains
VALID_DOMAINS = [
    "runtime_action",
    "runtime_lifecycle",
    "runtime_resource",
    "qualification",
    "security",
    "accessibility"
]

# Onboarding states
STATES = ["registered", "evidence_connected", "qualification_ready", "assurance_active"]


def load_json(path):
    """Load a JSON file."""
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    """Save data to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def generate_id(prefix):
    """Generate a unique ID with prefix."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    h = hashlib.sha256(f"{prefix}{ts}".encode()).hexdigest()[:8]
    return f"{prefix}-{ts}-{h}"


def validate_identity(project_id, instance, identity_source):
    """Validate project identity."""
    errors = []
    
    if not project_id or not project_id.strip():
        errors.append("project_id is required")
    
    if not instance or not instance.strip():
        errors.append("project_instance is required")
    
    if not identity_source or not identity_source.strip():
        errors.append("identity_source is required")
    
    return len(errors) == 0, errors


def register_evidence_sources(project_id, domains):
    """Register evidence sources."""
    # Validate domains
    invalid_domains = [d for d in domains if d not in VALID_DOMAINS]
    if invalid_domains:
        return False, f"Invalid domains: {invalid_domains}"
    
    # Create project evidence directories
    project_dir = PROJECTS_DIR / project_id
    records_dir = project_dir / "records"
    snapshots_dir = project_dir / "snapshots"
    
    records_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    
    return True, []


def verify_provenance(project_id):
    """Verify provenance chain."""
    # Check if project has evidence with complete provenance
    project_dir = PROJECTS_DIR / project_id
    
    if not project_dir.exists():
        return True, []  # No evidence yet, provenance will be verified on ingestion
    
    # Check existing evidence
    for evidence_dir in [project_dir / "records", project_dir / "snapshots"]:
        if evidence_dir.exists():
            for f in evidence_dir.glob("*.json"):
                evidence = load_json(f)
                if evidence:
                    provenance = evidence.get("provenance", {})
                    if not provenance.get("execution_identity"):
                        return False, f"Missing execution_identity in {f.name}"
                    if not provenance.get("governance_context"):
                        return False, f"Missing governance_context in {f.name}"
    
    return True, []


def map_qualification_profiles(project_id, artifact_types):
    """Map qualification profiles."""
    # Default mapping based on artifact types
    mappings = {}
    
    for artifact_type in artifact_types:
        if artifact_type in ["runtime_capability", "runtime_action", "runtime_lifecycle"]:
            mappings[artifact_type] = "RUNTIME-STANDARD"
        elif artifact_type in ["governance_surface", "authority_declaration"]:
            mappings[artifact_type] = "GOVERNANCE-CRITICAL"
        else:
            mappings[artifact_type] = "BASELINE"
    
    default_profile = "RUNTIME-STANDARD" if any("runtime" in t for t in artifact_types) else "BASELINE"
    
    return {
        "default_profile": default_profile,
        "artifact_mappings": mappings
    }


def assign_freshness_policy(project_id):
    """Assign freshness policy."""
    return {
        "record_threshold_minutes": 60,
        "snapshot_refresh_minutes": 15,
        "record_labels": {
            "current": "< 60 min",
            "historical": "60 min - 4 hr",
            "archived": "> 4 hr"
        },
        "snapshot_labels": {
            "current": "< 15 min",
            "aging": "15 - 60 min",
            "stale": "> 60 min"
        }
    }


def generate_link_projection(project_id):
    """Generate LINK projection."""
    # Create metadata for LINK visibility
    metadata = {
        "project_id": project_id,
        "evidence_coverage": {
            "total_records": 0,
            "total_snapshots": 0,
            "last_ingested_at": None,
            "qualification_status": "untested"
        },
        "adapter": {
            "adapter_id": f"{project_id}-runtime-adapter",
            "adapter_version": "1.0.0",
            "supported_event_types": ["runtime_action", "runtime_lifecycle", "runtime_resource"]
        }
    }
    
    # Save to project metadata
    project_dir = PROJECTS_DIR / project_id
    metadata_file = project_dir / "metadata.json"
    save_json(metadata_file, metadata)
    
    return True


def verify_isolation(project_id):
    """Verify project isolation."""
    project_dir = PROJECTS_DIR / project_id
    
    if not project_dir.exists():
        return True, []
    
    # Check that project directories don't reference other projects
    for f in project_dir.rglob("*.json"):
        content = load_json(f)
        if content:
            # Check for cross-project references
            if isinstance(content, dict):
                source = content.get("source", "")
                if source and source != project_id and source != "qa-pilot":
                    return False, f"Cross-project reference found in {f.name}: source={source}"
    
    return True, []


def onboard_project(project_id, instance, identity_source, artifact_types=None):
    """Onboard a new project."""
    if artifact_types is None:
        artifact_types = ["runtime_action", "runtime_lifecycle"]
    
    onboarding_id = generate_id("ONB")
    
    # Step 1: Validate identity
    identity_valid, identity_errors = validate_identity(project_id, instance, identity_source)
    if not identity_valid:
        return None, f"Identity validation failed: {identity_errors}"
    
    state = "registered"
    
    # Step 2: Register evidence sources
    evidence_registered, evidence_errors = register_evidence_sources(project_id, ["runtime_action", "runtime_lifecycle"])
    if not evidence_registered:
        return None, f"Evidence registration failed: {evidence_errors}"
    
    state = "evidence_connected"
    
    # Step 3: Verify provenance
    provenance_valid, provenance_errors = verify_provenance(project_id)
    if not provenance_valid:
        return None, f"Provenance verification failed: {provenance_errors}"
    
    # Step 4: Map qualification profiles
    profiles = map_qualification_profiles(project_id, artifact_types)
    state = "qualification_ready"
    
    # Step 5: Assign freshness policy
    freshness_policy = assign_freshness_policy(project_id)
    
    # Step 6: Generate LINK projection
    link_generated = generate_link_projection(project_id)
    
    # Step 7: Verify isolation
    isolation_valid, isolation_errors = verify_isolation(project_id)
    if not isolation_valid:
        return None, f"Isolation verification failed: {isolation_errors}"
    
    state = "assurance_active"
    
    # Create onboarding record
    onboarding = {
        "onboarding_id": onboarding_id,
        "project_id": project_id,
        "onboarded_at": datetime.now(timezone.utc).isoformat(),
        "adapter_version": "1.0.0",
        "state": state,
        "identity": {
            "project_id": project_id,
            "project_instance": instance,
            "identity_source": identity_source
        },
        "evidence_sources": {
            "domains": ["runtime_action", "runtime_lifecycle"],
            "provenance_complete": True
        },
        "qualification_profiles": profiles,
        "freshness_policy": freshness_policy,
        "link_projection": {
            "visible": link_generated,
            "generated_at": datetime.now(timezone.utc).isoformat()
        },
        "isolation_verified": isolation_valid,
        "advisory_only": True
    }
    
    # Save onboarding record
    save_json(ONBOARDING_DIR / f"{onboarding_id}.json", onboarding)
    
    return onboarding, None


def cmd_onboard(args):
    """Onboard a new project."""
    if len(args) < 3:
        print("Usage: onboard <project_id> <instance> <identity_source>")
        print("Example: onboard agent-bridge agent-bridge-prod-001 agent-bridge-registry")
        sys.exit(1)
    
    project_id = args[0]
    instance = args[1]
    identity_source = args[2]
    
    # Check if project already onboarded
    existing = list(ONBOARDING_DIR.glob("*.json")) if ONBOARDING_DIR.exists() else []
    for f in existing:
        record = load_json(f)
        if record and record.get("project_id") == project_id:
            print(f"Project already onboarded: {project_id}")
            print(f"  Onboarding ID: {record['onboarding_id']}")
            print(f"  State: {record['state']}")
            return
    
    onboarding, error = onboard_project(project_id, instance, identity_source)
    
    if error:
        print(f"ERROR: {error}")
        sys.exit(1)
    
    print(f"Project Onboarded: {onboarding['onboarding_id']}")
    print("=" * 60)
    print(f"  Project:  {project_id}")
    print(f"  Instance: {instance}")
    print(f"  Source:   {identity_source}")
    print(f"  State:    {onboarding['state']}")
    print()
    print("  Qualification Profiles:")
    for artifact, profile in onboarding["qualification_profiles"]["artifact_mappings"].items():
        print(f"    {artifact}: {profile}")
    print()
    print(f"  Isolation Verified: {onboarding['isolation_verified']}")


def cmd_status(args):
    """Show onboarding status."""
    if len(args) < 1:
        print("Usage: status <project_id>")
        sys.exit(1)
    
    project_id = args[0]
    
    # Find onboarding record
    if not ONBOARDING_DIR.exists():
        print(f"Project not onboarded: {project_id}")
        return
    
    for f in ONBOARDING_DIR.glob("*.json"):
        record = load_json(f)
        if record and record.get("project_id") == project_id:
            print(f"Onboarding Status: {project_id}")
            print("=" * 60)
            print(f"  Onboarding ID: {record['onboarding_id']}")
            print(f"  State: {record['state']}")
            print(f"  Onboarded at: {record['onboarded_at']}")
            print(f"  Adapter version: {record['adapter_version']}")
            print()
            print("  Identity:")
            print(f"    Project: {record['identity']['project_id']}")
            print(f"    Instance: {record['identity']['project_instance']}")
            print(f"    Source: {record['identity']['identity_source']}")
            print()
            print("  Evidence Sources:")
            print(f"    Domains: {', '.join(record['evidence_sources']['domains'])}")
            print(f"    Provenance complete: {record['evidence_sources']['provenance_complete']}")
            print()
            print("  Qualification Profiles:")
            print(f"    Default: {record['qualification_profiles']['default_profile']}")
            print()
            print(f"  Isolation Verified: {record['isolation_verified']}")
            return
    
    print(f"Project not onboarded: {project_id}")


def cmd_list(args):
    """List all onboarded projects."""
    if not ONBOARDING_DIR.exists():
        print("No projects onboarded yet.")
        return
    
    records = []
    for f in ONBOARDING_DIR.glob("*.json"):
        records.append(load_json(f))
    
    print(f"Onboarded Projects ({len(records)})")
    print("=" * 60)
    
    for r in records:
        print(f"\n  {r['project_id']}")
        print(f"    State: {r['state']}")
        print(f"    Onboarded: {r['onboarded_at']}")


def cmd_history(args):
    """Show onboarding history."""
    if not ONBOARDING_DIR.exists():
        print("No onboarding history yet.")
        return
    
    records = []
    for f in ONBOARDING_DIR.glob("*.json"):
        records.append(load_json(f))
    
    print(f"Onboarding History ({len(records)})")
    print("=" * 60)
    
    for r in records:
        print(f"\n  [{r['state']}] {r['onboarding_id']}")
        print(f"    Project: {r['project_id']}")
        print(f"    Onboarded: {r['onboarded_at']}")


COMMANDS = {
    "onboard": cmd_onboard,
    "status": cmd_status,
    "list": cmd_list,
    "history": cmd_history,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        print(f"Commands: {', '.join(COMMANDS.keys())}")
        sys.exit(0)
    
    cmd = sys.argv[1]
    args = sys.argv[2:]
    COMMANDS[cmd](args)


if __name__ == "__main__":
    main()
