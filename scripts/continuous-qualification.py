#!/usr/bin/env python3
"""
Continuous Qualification Engine — QA-PILOT-CONTINUOUS-QUALIFICATION-1

Controlled requalification lifecycle when assurance-relevant state changes.

Commands:
  evaluate-triggers    Evaluate all pending triggers
  run-qualification    Run qualification for a specific trigger
  show-history         Show qualification run history
  show-pending         Show pending triggers
  status               Show continuous qualification status
"""

import sys
import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# --- Configuration ---

PROJECT_ROOT = Path(__file__).parent.parent
EVIDENCE_STORE = PROJECT_ROOT / "data" / "runtime-evidence"
PROJECTS_DIR = EVIDENCE_STORE / "projects"
HISTORY_FILE = EVIDENCE_STORE / "qualification-history.json"
TRIGGERS_FILE = EVIDENCE_STORE / "qualification-triggers.json"
QUALIFICATION_RESULTS = EVIDENCE_STORE / "qualification-results.json"

# Trigger types
TRIGGER_TYPES = [
    "evidence_change",
    "capability_change",
    "finding_change",
    "freshness_expiry",
    "policy_change",
]


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


def load_history():
    """Load qualification history."""
    history = load_json(HISTORY_FILE)
    if history is None:
        return {"runs": [], "last_run_id": None, "total_runs": 0}
    return history


def save_history(history):
    """Save qualification history."""
    save_json(HISTORY_FILE, history)


def load_triggers():
    """Load qualification triggers."""
    triggers = load_json(TRIGGERS_FILE)
    if triggers is None:
        return {"pending": [], "evaluated": [], "total_triggers": 0}
    return triggers


def save_triggers(triggers):
    """Save qualification triggers."""
    save_json(TRIGGERS_FILE, triggers)


def evaluate_evidence_triggers():
    """Evaluate triggers from evidence changes."""
    new_triggers = []
    
    if not PROJECTS_DIR.exists():
        return new_triggers
    
    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        
        # Check for evidence files
        for evidence_dir in [project_dir / "records", project_dir / "snapshots"]:
            if not evidence_dir.exists():
                continue
            for f in evidence_dir.glob("*.json"):
                trigger = {
                    "trigger_id": generate_id("TRIG"),
                    "trigger_type": "evidence_change",
                    "project_id": project_dir.name,
                    "source_ref": f.stem,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "status": "pending",
                }
                new_triggers.append(trigger)
    
    return new_triggers


def evaluate_freshness_triggers():
    """Evaluate triggers from freshness expiry."""
    new_triggers = []
    
    # Load fleet freshness
    freshness_file = EVIDENCE_STORE / "discovery-projection.json"
    if not freshness_file.exists():
        return new_triggers
    
    try:
        projection = load_json(freshness_file)
        for project in projection.get("projects", []):
            if project.get("freshness_state") == "stale":
                trigger = {
                    "trigger_id": generate_id("TRIG"),
                    "trigger_type": "freshness_expiry",
                    "project_id": project["project_id"],
                    "source_ref": f"freshness:{project['freshness_state']}",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "status": "pending",
                }
                new_triggers.append(trigger)
    except:
        pass
    
    return new_triggers


def evaluate_all_triggers():
    """Evaluate all trigger sources."""
    triggers = load_triggers()
    
    # Evaluate different trigger sources
    new_triggers = []
    new_triggers.extend(evaluate_evidence_triggers())
    new_triggers.extend(evaluate_freshness_triggers())
    
    # Add new triggers to pending
    triggers["pending"].extend(new_triggers)
    triggers["total_triggers"] = len(triggers["pending"]) + len(triggers["evaluated"])
    
    save_triggers(triggers)
    
    return new_triggers


def run_qualification(trigger):
    """Run qualification for a specific trigger."""
    # Run qualification
    import subprocess
    result = subprocess.run(
        ["python3", str(PROJECT_ROOT / "scripts" / "qualify-runtime-evidence.py"), "qualify-all"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT)
    )
    
    # Determine disposition
    if result.returncode == 0:
        disposition = "PASS"
        findings_count = 0
    else:
        disposition = "FINDING"
        findings_count = 1
    
    # Create qualification run record
    run_record = {
        "qualification_run_id": generate_id("QCR"),
        "trigger": {
            "trigger_type": trigger["trigger_type"],
            "source_ref": trigger["source_ref"],
            "triggered_at": trigger["created_at"],
            "triggered_by": "system",
        },
        "profile": "runtime-evidence-qualification-v1",
        "input_refs": [trigger["source_ref"]],
        "result": {
            "disposition": disposition,
            "findings_count": findings_count,
            "qr_record_id": None,
        },
        "authority": "observation_only",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "executed_by": "scripts/continuous-qualification.py",
    }
    
    # Append to history (append-only)
    history = load_history()
    history["runs"].append(run_record)
    history["last_run_id"] = run_record["qualification_run_id"]
    history["total_runs"] = len(history["runs"])
    save_history(history)
    
    # Move trigger from pending to evaluated
    triggers = load_triggers()
    if trigger in triggers["pending"]:
        triggers["pending"].remove(trigger)
        trigger["status"] = "evaluated"
        trigger["result_run_id"] = run_record["qualification_run_id"]
        triggers["evaluated"].append(trigger)
    triggers["total_triggers"] = len(triggers["pending"]) + len(triggers["evaluated"])
    save_triggers(triggers)
    
    return run_record


def cmd_evaluate_triggers(args):
    """Evaluate all pending triggers."""
    new_triggers = evaluate_all_triggers()
    
    print(f"Trigger Evaluation")
    print("=" * 60)
    print(f"New triggers found: {len(new_triggers)}")
    
    if new_triggers:
        print()
        for t in new_triggers:
            print(f"  [{t['trigger_type']}] {t['project_id']}: {t['source_ref']}")
    
    triggers = load_triggers()
    print(f"\nPending: {len(triggers['pending'])}")
    print(f"Evaluated: {len(triggers['evaluated'])}")


def cmd_run_qualification(args):
    """Run qualification for pending triggers."""
    triggers = load_triggers()
    
    if not triggers["pending"]:
        print("No pending triggers.")
        return
    
    print(f"Running Qualification")
    print("=" * 60)
    
    for trigger in triggers["pending"][:5]:  # Limit to 5 per run
        print(f"\n  Trigger: {trigger['trigger_id']}")
        print(f"  Type: {trigger['trigger_type']}")
        print(f"  Project: {trigger['project_id']}")
        
        run_record = run_qualification(trigger)
        
        print(f"  Result: {run_record['result']['disposition']}")
        print(f"  Run ID: {run_record['qualification_run_id']}")
    
    triggers = load_triggers()
    print(f"\nRemaining pending: {len(triggers['pending'])}")


def cmd_show_history(args):
    """Show qualification run history."""
    history = load_history()
    
    print(f"Qualification History")
    print("=" * 60)
    print(f"Total runs: {history['total_runs']}")
    print(f"Last run: {history['last_run_id'] or 'none'}")
    print()
    
    if not history["runs"]:
        print("No qualification runs yet.")
        return
    
    for run in history["runs"][-10:]:  # Show last 10
        print(f"  [{run['result']['disposition']}] {run['qualification_run_id']}")
        print(f"    Trigger: {run['trigger']['trigger_type']} ({run['trigger']['source_ref']})")
        print(f"    Executed: {run['executed_at']}")
        if run['result']['findings_count'] > 0:
            print(f"    Findings: {run['result']['findings_count']}")
        print()


def cmd_show_pending(args):
    """Show pending triggers."""
    triggers = load_triggers()
    
    print(f"Pending Triggers")
    print("=" * 60)
    print(f"Count: {len(triggers['pending'])}")
    print()
    
    if not triggers["pending"]:
        print("No pending triggers.")
        return
    
    for t in triggers["pending"]:
        print(f"  [{t['trigger_type']}] {t['project_id']}")
        print(f"    ID: {t['trigger_id']}")
        print(f"    Source: {t['source_ref']}")
        print(f"    Created: {t['created_at']}")
        print()


def cmd_status(args):
    """Show continuous qualification status."""
    history = load_history()
    triggers = load_triggers()
    
    print(f"Continuous Qualification Status")
    print("=" * 60)
    print(f"History:")
    print(f"  Total runs:     {history['total_runs']}")
    print(f"  Last run:       {history['last_run_id'] or 'none'}")
    print()
    print(f"Triggers:")
    print(f"  Pending:        {len(triggers['pending'])}")
    print(f"  Evaluated:      {len(triggers['evaluated'])}")
    print(f"  Total:          {triggers['total_triggers']}")
    
    # Count dispositions
    if history["runs"]:
        pass_count = sum(1 for r in history["runs"] if r["result"]["disposition"] == "PASS")
        finding_count = sum(1 for r in history["runs"] if r["result"]["disposition"] == "FINDING")
        print()
        print(f"Results:")
        print(f"  PASS:           {pass_count}")
        print(f"  FINDING:        {finding_count}")


COMMANDS = {
    "evaluate-triggers": cmd_evaluate_triggers,
    "run-qualification": cmd_run_qualification,
    "show-history": cmd_show_history,
    "show-pending": cmd_show_pending,
    "status": cmd_status,
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
