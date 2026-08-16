#!/usr/bin/env python3
"""
Runtime Evidence Federation Engine — QA-PILOT-RUNTIME-EVIDENCE-FEDERATION-1

Multi-project runtime evidence federation with project isolation.

Commands:
  ingest <project_id> <file>    Ingest a runtime event for a specific project
  qualify <project_id>          Qualify all evidence for a specific project
  qualify-all                   Qualify all projects
  status                        Show federation status
  projects                      List all projects with evidence
  discovery                     Show discovery metadata for all projects
"""

import sys
import os
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

# --- Configuration ---

PROJECT_ROOT = Path(__file__).parent.parent
EVIDENCE_STORE = PROJECT_ROOT / "data" / "runtime-evidence"
PROJECTS_DIR = EVIDENCE_STORE / "projects"
INDEX_FILE = EVIDENCE_STORE / "index.json"
DISCOVERY_FILE = EVIDENCE_STORE / "discovery.json"

# Event type detection
EVENT_TYPE_MAP = {
    "runtime_action": "runtime_action",
    "runtime_lifecycle": "runtime_lifecycle",
    "runtime_resource": "runtime_resource",
}

# Evidence class mapping
EVIDENCE_CLASS_MAP = {
    "runtime_action": "record",
    "runtime_lifecycle": "record",
    "runtime_resource": "snapshot",
}


def load_json(path):
    """Load a JSON file."""
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    """Save data to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def detect_event_type(event):
    """Detect event type from runtime event."""
    if event.get("event_type") == "runtime_action":
        return "runtime_action"
    elif event.get("event_type") == "runtime_lifecycle":
        return "runtime_lifecycle"
    elif event.get("observation_type") == "runtime_resource":
        return "runtime_resource"
    return None


def get_project_dir(project_id):
    """Get the evidence directory for a project."""
    return PROJECTS_DIR / project_id


def ensure_project_dirs(project_id):
    """Ensure project directories exist."""
    project_dir = get_project_dir(project_id)
    records_dir = project_dir / "records"
    snapshots_dir = project_dir / "snapshots"
    records_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    return project_dir, records_dir, snapshots_dir


def generate_id(prefix):
    """Generate a unique ID with prefix."""
    import hashlib
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    h = hashlib.sha256(f"{prefix}{ts}".encode()).hexdigest()[:8]
    return f"{prefix}-{ts}-{h}"


def validate_project_identity(event, project_id):
    """Validate that event has canonical project identity."""
    governance = event.get("governance_context", {})
    project_identity = governance.get("project_identity", {})
    
    if not project_identity.get("project_id"):
        return False, "Missing governance_context.project_identity.project_id"
    
    if not project_identity.get("project_instance"):
        return False, "Missing governance_context.project_identity.project_instance"
    
    if not project_identity.get("identity_source"):
        return False, "Missing governance_context.project_identity.identity_source"
    
    if project_identity["project_id"] != project_id:
        return False, f"Project ID mismatch: expected '{project_id}', got '{project_identity['project_id']}'"
    
    return True, None


def assemble_federated_evidence(event, event_type, project_id):
    """Assemble evidence object with canonical project identity."""
    import hashlib
    
    evidence_id_prefix = {
        "runtime_action": "RAE",
        "runtime_lifecycle": "RLE",
        "runtime_resource": "RRO",
    }
    evidence_id = generate_id(evidence_id_prefix.get(event_type, "RTE"))
    timestamp = event.get("timestamp", datetime.now(timezone.utc).isoformat())
    
    # Build observation
    if event_type == "runtime_action":
        observed_state = f"Action: {event.get('action', 'unknown')}"
    elif event_type == "runtime_lifecycle":
        observed_state = f"Lifecycle: {event.get('lifecycle_event', 'unknown')}"
    else:
        observed_state = f"Resource observation: {event.get('consumed', {}).get('goose_level', 'unknown')}"
    
    # Compute freshness
    now = datetime.now(timezone.utc)
    ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    age_seconds = (now - ts).total_seconds()
    
    evidence_class = EVIDENCE_CLASS_MAP.get(event_type, "record")
    if evidence_class == "record":
        if age_seconds < 3600:
            label = "current"
        elif age_seconds < 14400:
            label = "historical"
        else:
            label = "archived"
        refresh_expected = None
    else:
        if age_seconds < 900:
            label = "current"
        else:
            label = "stale"
        refresh_expected = timestamp
    
    # Get model identity
    model_identity = event.get("execution_identity", {}).get("model_identity", 
                      event.get("model_identity", {"provider": "unknown", "model": "unknown"}))
    
    return {
        "evidence_id": evidence_id,
        "schema_version": "assurance-evidence-v1",
        "evidence_class": evidence_class,
        "identity": {
            "evidence_id": evidence_id,
            "timestamp": timestamp,
            "source": project_id,
        },
        "observation": {
            "observed_state": observed_state,
            "artifact_refs": [event.get("event_id", event.get("observation_id", "unknown"))],
            "measurements": event.get("consumed") if event_type == "runtime_resource" else {},
        },
        "context": {
            "environment": f"{event.get('execution_identity', {}).get('runtime_identity', {}).get('runtime_type', 'unknown')}",
            "consumer_shape": "runtime_evidence",
            "execution_context": {
                "event_type": event_type,
                "project_id": project_id,
            },
        },
        "custody": {
            "origin": f"adapter:{project_id}",
            "chain": [],
            "verification_state": "verified",
        },
        "freshness": {
            "captured_at": timestamp,
            "validated_at": now.isoformat(),
            "refresh_expected_at": refresh_expected,
            "confidence_label": label,
        },
        "provenance": {
            "execution_identity": event.get("execution_identity", {}),
            "governance_context": event.get("governance_context", {}),
        },
        "federation": {
            "project_id": project_id,
            "ingested_at": now.isoformat(),
            "ingested_by": "scripts/federate-runtime-evidence.py",
        },
    }


def cmd_ingest(args):
    """Ingest a runtime event for a specific project."""
    if len(args) < 2:
        print("Usage: ingest <project_id> <file>")
        sys.exit(1)
    
    project_id = args[0]
    filepath = Path(args[1])
    
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)
    
    event = load_json(filepath)
    event_type = detect_event_type(event)
    
    if not event_type:
        print("ERROR: Cannot detect event type.")
        sys.exit(1)
    
    # Validate project identity (FED-001)
    valid, error = validate_project_identity(event, project_id)
    if not valid:
        print(f"ERROR: Project identity validation failed: {error}")
        sys.exit(1)
    
    # Ensure project directories
    project_dir, records_dir, snapshots_dir = ensure_project_dirs(project_id)
    
    # Assemble evidence
    evidence = assemble_federated_evidence(event, event_type, project_id)
    evidence_class = evidence["evidence_class"]
    
    # Store in project directory
    if evidence_class == "record":
        target_dir = records_dir
    else:
        target_dir = snapshots_dir
    
    target_file = target_dir / f"{evidence['evidence_id']}.json"
    save_json(target_file, evidence)
    
    # Update project metadata
    metadata_file = project_dir / "metadata.json"
    if metadata_file.exists():
        metadata = load_json(metadata_file)
    else:
        metadata = {
            "project_id": project_id,
            "evidence_coverage": {
                "total_records": 0,
                "total_snapshots": 0,
                "last_ingested_at": None,
                "qualification_status": "untested",
            },
            "adapter": {
                "adapter_id": f"{project_id}-runtime-adapter",
                "adapter_version": "1.0.0",
                "supported_event_types": ["runtime_action", "runtime_lifecycle", "runtime_resource"],
            },
        }
    
    if evidence_class == "record":
        metadata["evidence_coverage"]["total_records"] += 1
    else:
        metadata["evidence_coverage"]["total_snapshots"] += 1
    
    metadata["evidence_coverage"]["last_ingested_at"] = datetime.now(timezone.utc).isoformat()
    save_json(metadata_file, metadata)
    
    print(f"Ingested: {evidence['evidence_id']}")
    print(f"Project: {project_id}")
    print(f"Event type: {event_type}")
    print(f"Evidence class: {evidence_class}")
    print(f"Stored: {target_file}")


def cmd_qualify(args):
    """Qualify all evidence for a specific project."""
    if len(args) < 1:
        print("Usage: qualify <project_id>")
        sys.exit(1)
    
    project_id = args[0]
    project_dir = get_project_dir(project_id)
    
    if not project_dir.exists():
        print(f"ERROR: Project not found: {project_id}")
        sys.exit(1)
    
    # Run qualification
    import subprocess
    result = subprocess.run(
        ["python3", str(PROJECT_ROOT / "scripts" / "qualify-runtime-evidence.py"), "qualify-all"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT)
    )
    
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
    
    # Update project metadata
    metadata_file = project_dir / "metadata.json"
    if metadata_file.exists():
        metadata = load_json(metadata_file)
        results_file = EVIDENCE_STORE / "qualification-results.json"
        if results_file.exists():
            results = load_json(results_file)
            metadata["evidence_coverage"]["qualification_status"] = results.get("disposition", "unknown").lower()
            save_json(metadata_file, metadata)


def cmd_qualify_all(args):
    """Qualify all projects."""
    if not PROJECTS_DIR.exists():
        print("No projects found.")
        return
    
    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if project_dir.is_dir():
            print(f"\n{'='*60}")
            print(f"Qualifying: {project_dir.name}")
            print(f"{'='*60}")
            cmd_qualify([project_dir.name])


def cmd_status(args):
    """Show federation status."""
    if not PROJECTS_DIR.exists():
        print("No projects found.")
        return
    
    print("Runtime Evidence Federation Status")
    print("=" * 60)
    
    total_records = 0
    total_snapshots = 0
    
    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if not project_dir.is_dir():
            continue
        
        metadata_file = project_dir / "metadata.json"
        if metadata_file.exists():
            metadata = load_json(metadata_file)
            coverage = metadata.get("evidence_coverage", {})
            records = coverage.get("total_records", 0)
            snapshots = coverage.get("total_snapshots", 0)
            status = coverage.get("qualification_status", "untested")
            last_ingested = coverage.get("last_ingested_at", "never")
        else:
            records = len(list((project_dir / "records").glob("*.json"))) if (project_dir / "records").exists() else 0
            snapshots = len(list((project_dir / "snapshots").glob("*.json"))) if (project_dir / "snapshots").exists() else 0
            status = "untested"
            last_ingested = "unknown"
        
        total_records += records
        total_snapshots += snapshots
        
        print(f"\n  Project: {project_dir.name}")
        print(f"    Records:      {records}")
        print(f"    Snapshots:    {snapshots}")
        print(f"    Qualification: {status}")
        print(f"    Last ingested: {last_ingested}")
    
    print(f"\n{'='*60}")
    print(f"Total projects:  {len(list(PROJECTS_DIR.iterdir()))}")
    print(f"Total records:   {total_records}")
    print(f"Total snapshots: {total_snapshots}")


def cmd_projects(args):
    """List all projects with evidence."""
    if not PROJECTS_DIR.exists():
        print("No projects found.")
        return
    
    print("Projects with Runtime Evidence")
    print("=" * 40)
    
    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if project_dir.is_dir():
            metadata_file = project_dir / "metadata.json"
            if metadata_file.exists():
                metadata = load_json(metadata_file)
                adapter = metadata.get("adapter", {})
                print(f"\n  {project_dir.name}")
                print(f"    Adapter: {adapter.get('adapter_id', 'unknown')}")
                print(f"    Version: {adapter.get('adapter_version', 'unknown')}")
            else:
                print(f"\n  {project_dir.name}")


def cmd_discovery(args):
    """Show discovery metadata for all projects."""
    discovery = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "projects": [],
    }
    
    if not PROJECTS_DIR.exists():
        print(json.dumps(discovery, indent=2))
        return
    
    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if not project_dir.is_dir():
            continue
        
        metadata_file = project_dir / "metadata.json"
        if metadata_file.exists():
            metadata = load_json(metadata_file)
            discovery["projects"].append(metadata)
        else:
            discovery["projects"].append({
                "project_id": project_dir.name,
                "evidence_coverage": {
                    "total_records": 0,
                    "total_snapshots": 0,
                    "last_ingested_at": None,
                    "qualification_status": "untested",
                },
            })
    
    save_json(DISCOVERY_FILE, discovery)
    print(json.dumps(discovery, indent=2))


COMMANDS = {
    "ingest": cmd_ingest,
    "qualify": cmd_qualify,
    "qualify-all": cmd_qualify_all,
    "status": cmd_status,
    "projects": cmd_projects,
    "discovery": cmd_discovery,
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
