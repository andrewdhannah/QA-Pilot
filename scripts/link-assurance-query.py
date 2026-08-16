#!/usr/bin/env python3
"""
LINK Assurance Query Surface — QA-PILOT-LINK-ASSURANCE-INTEGRATION-1

Read-only interface for LINK to consume assurance state for planning context.

Commands:
  project <project_id>    Get assurance state for a single project
  fleet                   Get fleet assurance state
  history <project_id>    Get qualification history for a project
  context <project_id>    Get planning context for a project
  projection              Generate LINK-consumable projection
"""

import sys
import os
import json
from datetime import datetime, timezone
from pathlib import Path

# --- Configuration ---

PROJECT_ROOT = Path(__file__).parent.parent
EVIDENCE_STORE = PROJECT_ROOT / "data" / "runtime-evidence"
PROJECTS_DIR = EVIDENCE_STORE / "projects"
RISK_FILE = EVIDENCE_STORE / "risk-assessments.json"
HISTORY_FILE = EVIDENCE_STORE / "qualification-history.json"
DISCOVERY_FILE = EVIDENCE_STORE / "discovery-projection.json"
LINK_PROJECTION_FILE = EVIDENCE_STORE / "link-projection.json"


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


def get_risk_assessment(project_id):
    """Get risk assessment for a project."""
    risk_data = load_json(RISK_FILE)
    if not risk_data:
        return None
    
    # Check if risk_data has projects array
    if "projects" in risk_data:
        for p in risk_data["projects"]:
            if p.get("project_id") == project_id:
                return p
    
    return None


def get_qualification_history(project_id):
    """Get qualification history for a project."""
    history = load_json(HISTORY_FILE)
    if not history:
        return {"history": [], "total_runs": 0, "last_run": None}
    
    # Filter history by project (simplified - in real system would have project refs)
    return history


def get_freshness_state(project_id):
    """Get freshness state for a project."""
    discovery = load_json(DISCOVERY_FILE)
    if not discovery:
        return "unknown"
    
    for project in discovery.get("projects", []):
        if project.get("project_id") == project_id:
            return project.get("freshness_state", "unknown")
    
    return "unknown"


def get_coverage_state(project_id):
    """Get coverage state for a project."""
    discovery = load_json(DISCOVERY_FILE)
    if not discovery:
        return "unknown"
    
    for project in discovery.get("projects", []):
        if project.get("project_id") == project_id:
            return project.get("coverage_state", "unknown")
    
    return "unknown"


def get_qualification_status(project_id):
    """Get qualification status for a project."""
    results_file = EVIDENCE_STORE / "qualification-results.json"
    if not results_file.exists():
        return "untested"
    
    try:
        results = load_json(results_file)
        for result in results.get("results", []):
            # In real system, would filter by project
            if result.get("disposition") == "PASS":
                return "pass"
            elif result.get("disposition") == "FINDING":
                return "finding"
    except:
        pass
    
    return "untested"


def get_project_assurance_state(project_id):
    """Get assurance state for a single project."""
    # Gather data from multiple sources
    risk = get_risk_assessment(project_id)
    freshness = get_freshness_state(project_id)
    coverage = get_coverage_state(project_id)
    qualification = get_qualification_status(project_id)
    history = get_qualification_history(project_id)
    
    # Determine status
    if risk and risk.get("risk_band") in ("attention_required", "urgent"):
        status = "degraded"
    elif freshness == "stale":
        status = "degraded"
    elif qualification == "untested":
        status = "unknown"
    else:
        status = "operational"
    
    # Build assurance state
    assurance_state = {
        "status": status,
        "risk_band": risk.get("risk_band", "unknown") if risk else "unknown",
        "risk_score": risk.get("risk_score", 0) if risk else 0,
        "coverage": coverage,
        "freshness": freshness,
        "qualification_status": qualification,
    }
    
    # Build drivers
    drivers = []
    if risk:
        drivers.extend(risk.get("drivers", []))
    if coverage in ("minimal", "none", "unknown"):
        drivers.append(f"coverage_{coverage}")
    if freshness in ("stale", "unknown"):
        drivers.append(f"freshness_{freshness}")
    
    # Build recommendations
    recommendations = []
    if risk:
        recommendations.extend(risk.get("recommendations", []))
    if coverage == "partial":
        recommendations.append("Consider expanding evidence coverage")
    if freshness == "stale":
        recommendations.append("Consider refreshing evidence")
    
    # Build evidence refs
    evidence_refs = []
    if risk:
        for ref in risk.get("evidence_refs", []):
            evidence_refs.append({
                "ref": ref,
                "type": "qualification_result",
                "disposition": "unknown"
            })
    
    return {
        "project_id": project_id,
        "projection_timestamp": datetime.now(timezone.utc).isoformat(),
        "assurance_state": assurance_state,
        "drivers": drivers,
        "recommendations": recommendations,
        "evidence_refs": evidence_refs,
        "provenance": {
            "risk_assessment_id": risk.get("assessment_id") if risk else None,
            "qualification_run_id": history.get("last_run"),
            "freshness_assessment_source": "discover-fleet-freshness.py"
        },
        "authority": "observation_only"
    }


def get_fleet_assurance_state():
    """Get assurance state for all governed projects."""
    if not PROJECTS_DIR.exists():
        return {
            "projection_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_projects": 0,
            "by_status": {},
            "by_risk_band": {},
            "attention_needed": [],
            "projects": []
        }
    
    projects = []
    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if project_dir.is_dir():
            state = get_project_assurance_state(project_dir.name)
            projects.append(state)
    
    # Aggregate
    by_status = {}
    by_risk_band = {}
    attention_needed = []
    
    for p in projects:
        status = p["assurance_state"]["status"]
        risk_band = p["assurance_state"]["risk_band"]
        
        by_status[status] = by_status.get(status, 0) + 1
        by_risk_band[risk_band] = by_risk_band.get(risk_band, 0) + 1
        
        if risk_band in ("attention_required", "urgent"):
            attention_needed.append({
                "project_id": p["project_id"],
                "risk_band": risk_band,
                "reasons": p["drivers"]
            })
    
    return {
        "projection_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_projects": len(projects),
        "by_status": by_status,
        "by_risk_band": by_risk_band,
        "attention_needed": attention_needed,
        "projects": projects
    }


def get_assurance_history(project_id):
    """Get qualification history for a project."""
    history = get_qualification_history(project_id)
    
    return {
        "project_id": project_id,
        "history": history.get("runs", [])[-10:],  # Last 10 runs
        "total_runs": history.get("total_runs", 0),
        "last_run": history.get("last_run_id")
    }


def get_planning_context(project_id):
    """Get planning context for a project."""
    state = get_project_assurance_state(project_id)
    
    # Build human-readable context
    context_parts = []
    
    # Coverage context
    coverage = state["assurance_state"]["coverage"]
    if coverage == "partial":
        context_parts.append(f"Existing evidence coverage is partial")
    elif coverage == "minimal":
        context_parts.append(f"Existing evidence coverage is minimal")
    elif coverage == "none":
        context_parts.append(f"No evidence coverage exists")
    
    # Risk context
    risk_band = state["assurance_state"]["risk_band"]
    risk_score = state["assurance_state"]["risk_score"]
    if risk_band != "healthy":
        context_parts.append(f"Risk band: {risk_band} (score: {risk_score})")
    
    # Qualification context
    qual_status = state["assurance_state"]["qualification_status"]
    if qual_status == "finding":
        context_parts.append("Previous qualification found issues")
    elif qual_status == "untested":
        context_parts.append("No qualification performed yet")
    
    # Freshness context
    freshness = state["assurance_state"]["freshness"]
    if freshness in ("stale", "aging"):
        context_parts.append(f"Evidence is {freshness}")
    
    # Recommendations
    if state["recommendations"]:
        context_parts.append("Recommendations:")
        for r in state["recommendations"]:
            context_parts.append(f"  - {r}")
    
    return {
        "project_id": project_id,
        "planning_context": "\n".join(context_parts) if context_parts else "No assurance concerns",
        "assurance_state": state["assurance_state"],
        "drivers": state["drivers"],
        "authority": "observation_only"
    }


def cmd_project(args):
    """Get assurance state for a single project."""
    if len(args) < 1:
        print("Usage: project <project_id>")
        sys.exit(1)
    
    project_id = args[0]
    state = get_project_assurance_state(project_id)
    
    print(f"Assurance State: {project_id}")
    print("=" * 60)
    print(json.dumps(state, indent=2))


def cmd_fleet(args):
    """Get fleet assurance state."""
    state = get_fleet_assurance_state()
    
    print("Fleet Assurance State")
    print("=" * 60)
    print(f"Generated: {state['projection_timestamp']}")
    print(f"Projects:  {state['total_projects']}")
    print()
    
    print("By Status:")
    for status, count in state["by_status"].items():
        print(f"  {status}: {count}")
    
    print()
    print("By Risk Band:")
    for band, count in state["by_risk_band"].items():
        print(f"  {band}: {count}")
    
    if state["attention_needed"]:
        print()
        print("Attention Needed:")
        for item in state["attention_needed"]:
            print(f"  [{item['risk_band'].upper()}] {item['project_id']}")
            for r in item["reasons"]:
                print(f"    - {r}")


def cmd_history(args):
    """Get qualification history for a project."""
    if len(args) < 1:
        print("Usage: history <project_id>")
        sys.exit(1)
    
    project_id = args[0]
    history = get_assurance_history(project_id)
    
    print(f"Qualification History: {project_id}")
    print("=" * 60)
    print(f"Total runs: {history['total_runs']}")
    print(f"Last run:   {history['last_run'] or 'none'}")
    print()
    
    if not history["history"]:
        print("No qualification runs yet.")
        return
    
    for run in history["history"]:
        print(f"  [{run.get('result', {}).get('disposition', 'unknown')}] {run['qualification_run_id']}")
        print(f"    Trigger: {run['trigger']['trigger_type']}")
        print(f"    Executed: {run['executed_at']}")
        print()


def cmd_context(args):
    """Get planning context for a project."""
    if len(args) < 1:
        print("Usage: context <project_id>")
        sys.exit(1)
    
    project_id = args[0]
    context = get_planning_context(project_id)
    
    print(f"Planning Context: {project_id}")
    print("=" * 60)
    print()
    print("Assurance Context for Planning:")
    print()
    print(context["planning_context"])
    print()
    print("---")
    print(f"Authority: {context['authority']}")
    print("This is advisory context, not a command.")


def cmd_projection(args):
    """Generate LINK-consumable projection."""
    fleet = get_fleet_assurance_state()
    
    projection = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "projection_type": "link_assurance",
        "fleet_state": fleet,
        "link_interfaces": {
            "get_project_assurance_state": "read-only",
            "get_fleet_assurance_state": "read-only",
            "get_assurance_history": "read-only",
            "get_planning_context": "read-only"
        },
        "authority_boundary": {
            "can_mutate": False,
            "can_trigger": False,
            "can_decide": False,
            "advisory_only": True
        }
    }
    
    save_json(LINK_PROJECTION_FILE, projection)
    print(f"LINK projection saved: {LINK_PROJECTION_FILE}")
    print(f"Projects: {fleet['total_projects']}")


COMMANDS = {
    "project": cmd_project,
    "fleet": cmd_fleet,
    "history": cmd_history,
    "context": cmd_context,
    "projection": cmd_projection,
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
