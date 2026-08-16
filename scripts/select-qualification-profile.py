#!/usr/bin/env python3
"""
Adaptive Qualification Profile Selection Engine — QA-PILOT-ADAPTIVE-QUALIFICATION-1

Selects qualification profiles based on artifact type, risk state, history, and coverage.

Commands:
  select <project_id> <artifact_type>    Select profile for an artifact
  list-profiles                          List available profiles
  history                                Show selection history
  status                                 Show selection status
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
PROFILES_DIR = DATA_DIR / "qualification-profiles"
SELECTIONS_DIR = DATA_DIR / "profile-selections"
RISK_FILE = DATA_DIR / "risk-assessments.json" if (DATA_DIR / "risk-assessments.json").exists() else PROJECT_ROOT / "data" / "runtime-evidence" / "risk-assessments.json"
HISTORY_FILE = DATA_DIR / "calibration-history.json"
EVIDENCE_STORE = PROJECT_ROOT / "data" / "runtime-evidence"


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


# --- Default Profiles ---

DEFAULT_PROFILES = [
    {
        "profile_id": "BASELINE",
        "name": "Baseline Profile",
        "applicable_artifact_types": ["*"],
        "required_checks": ["contract", "evidence"],
        "optional_checks": ["performance"],
        "escalation_indicators": [],
        "rationale": "Default profile for low-risk artifacts with no special requirements.",
        "advisory_only": True
    },
    {
        "profile_id": "RUNTIME-STANDARD",
        "name": "Standard Runtime Profile",
        "applicable_artifact_types": ["runtime_action", "runtime_lifecycle", "runtime_resource"],
        "required_checks": ["contract", "evidence", "provenance"],
        "optional_checks": ["security", "performance"],
        "escalation_indicators": ["stale_evidence"],
        "rationale": "For runtime evidence requiring basic validation.",
        "advisory_only": True
    },
    {
        "profile_id": "RUNTIME-HIGH-ASSURANCE",
        "name": "High Assurance Runtime Profile",
        "applicable_artifact_types": ["runtime_capability", "runtime_action", "runtime_lifecycle"],
        "required_checks": ["contract", "evidence", "authority", "security", "runtime_validation"],
        "optional_checks": ["accessibility", "performance"],
        "escalation_indicators": ["previous_authority_findings", "high_risk_band", "stale_evidence"],
        "rationale": "For runtime capabilities with authority scope, requiring comprehensive validation.",
        "advisory_only": True
    },
    {
        "profile_id": "GOVERNANCE-CRITICAL",
        "name": "Critical Governance Profile",
        "applicable_artifact_types": ["governance_surface", "authority_declaration", "capability_registration"],
        "required_checks": ["contract", "evidence", "authority", "security", "discoverability", "provenance"],
        "optional_checks": ["accessibility", "performance", "documentation"],
        "escalation_indicators": ["previous_governance_findings", "critical_risk_band"],
        "rationale": "For governance-critical artifacts requiring maximum validation depth.",
        "advisory_only": True
    }
]


def ensure_profiles():
    """Ensure default profiles exist."""
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    
    for profile in DEFAULT_PROFILES:
        profile_file = PROFILES_DIR / f"{profile['profile_id']}.json"
        if not profile_file.exists():
            save_json(profile_file, profile)


def get_risk_state(project_id):
    """Get risk state for a project."""
    risk_file = EVIDENCE_STORE / "risk-assessments.json"
    if not risk_file.exists():
        return {"risk_band": "unknown", "risk_score": 0}
    
    try:
        risk_data = load_json(risk_file)
        if "projects" in risk_data:
            for p in risk_data["projects"]:
                if p.get("project_id") == project_id:
                    return {"risk_band": p.get("risk_band", "unknown"), "risk_score": p.get("risk_score", 0)}
    except:
        pass
    
    return {"risk_band": "unknown", "risk_score": 0}


def get_historical_findings(project_id):
    """Get historical findings for a project."""
    history_file = EVIDENCE_STORE / "qualification-history.json"
    if not history_file.exists():
        return {"has_findings": False, "finding_count": 0}
    
    try:
        history = load_json(history_file)
        finding_count = sum(1 for r in history.get("runs", []) if r.get("result", {}).get("disposition") == "FINDING")
        return {"has_findings": finding_count > 0, "finding_count": finding_count}
    except:
        pass
    
    return {"has_findings": False, "finding_count": 0}


def get_coverage_state(project_id):
    """Get coverage state for a project."""
    discovery_file = EVIDENCE_STORE / "discovery-projection.json"
    if not discovery_file.exists():
        return {"coverage": "unknown", "freshness": "unknown"}
    
    try:
        discovery = load_json(discovery_file)
        for project in discovery.get("projects", []):
            if project.get("project_id") == project_id:
                return {
                    "coverage": project.get("coverage_state", "unknown"),
                    "freshness": project.get("freshness_state", "unknown")
                }
    except:
        pass
    
    return {"coverage": "unknown", "freshness": "unknown"}


def select_profile(project_id, artifact_type):
    """Select qualification profile based on inputs."""
    # Gather inputs
    risk = get_risk_state(project_id)
    history = get_historical_findings(project_id)
    coverage = get_coverage_state(project_id)
    
    # Determine escalation indicators
    escalation_indicators = []
    
    if risk["risk_band"] in ("attention_required", "urgent"):
        escalation_indicators.append("high_risk_band")
    
    if history["has_findings"]:
        escalation_indicators.append("previous_authority_findings")
    
    if coverage["freshness"] == "stale":
        escalation_indicators.append("stale_evidence")
    
    if coverage["coverage"] in ("minimal", "none", "unknown"):
        escalation_indicators.append("coverage_below_threshold")
    
    # Load profiles
    ensure_profiles()
    profiles = []
    for f in PROFILES_DIR.glob("*.json"):
        profiles.append(load_json(f))
    
    # Find matching profile
    # Priority: GOVERNANCE-CRITICAL > RUNTIME-HIGH-ASSURANCE > RUNTIME-STANDARD > BASELINE
    selected_profile = None
    selection_reasons = []
    
    for profile in profiles:
        # Check if artifact type matches
        if "*" in profile["applicable_artifact_types"] or artifact_type in profile["applicable_artifact_types"]:
            # Check if escalation indicators match
            matching_indicators = [i for i in profile["escalation_indicators"] if i in escalation_indicators]
            if matching_indicators:
                selected_profile = profile
                selection_reasons = matching_indicators
                break
    
    # Fallback to highest priority matching profile
    if not selected_profile:
        for profile in profiles:
            if "*" in profile["applicable_artifact_types"] or artifact_type in profile["applicable_artifact_types"]:
                selected_profile = profile
                selection_reasons = ["default_match"]
                break
    
    if not selected_profile:
        selected_profile = DEFAULT_PROFILES[0]
        selection_reasons = ["fallback"]
    
    # Build selection record
    selection = {
        "selection_id": generate_id("QS"),
        "project_id": project_id,
        "artifact_type": artifact_type,
        "selected_at": datetime.now(timezone.utc).isoformat(),
        "selected_profile": selected_profile["profile_id"],
        "profile_name": selected_profile["name"],
        "inputs": {
            "risk_state": risk,
            "historical_findings": history,
            "coverage_state": coverage,
            "escalation_indicators": escalation_indicators
        },
        "selection_reasons": selection_reasons,
        "required_checks": selected_profile["required_checks"],
        "optional_checks": selected_profile.get("optional_checks", []),
        "rationale": selected_profile["rationale"],
        "advisory_only": True
    }
    
    return selection


def cmd_select(args):
    """Select profile for an artifact."""
    if len(args) < 2:
        print("Usage: select <project_id> <artifact_type>")
        print("Example: select librarian runtime_action")
        sys.exit(1)
    
    project_id = args[0]
    artifact_type = args[1]
    
    selection = select_profile(project_id, artifact_type)
    
    # Save selection
    save_json(SELECTIONS_DIR / f"{selection['selection_id']}.json", selection)
    
    print(f"Profile Selection: {selection['selection_id']}")
    print("=" * 60)
    print(f"  Project:   {project_id}")
    print(f"  Artifact:  {artifact_type}")
    print(f"  Profile:   {selection['selected_profile']} ({selection['profile_name']})")
    print()
    print("  Reasons:")
    for reason in selection["selection_reasons"]:
        print(f"    - {reason}")
    print()
    print("  Required Checks:")
    for check in selection["required_checks"]:
        print(f"    - {check}")
    if selection["optional_checks"]:
        print("  Optional Checks:")
        for check in selection["optional_checks"]:
            print(f"    - {check}")
    print()
    print(f"  Rationale: {selection['rationale']}")


def cmd_list_profiles(args):
    """List available profiles."""
    ensure_profiles()
    
    print("Qualification Profiles")
    print("=" * 60)
    
    for f in sorted(PROFILES_DIR.glob("*.json")):
        profile = load_json(f)
        print(f"\n  {profile['profile_id']}: {profile['name']}")
        print(f"    Applicable: {', '.join(profile['applicable_artifact_types'])}")
        print(f"    Required: {', '.join(profile['required_checks'])}")
        if profile.get("optional_checks"):
            print(f"    Optional: {', '.join(profile['optional_checks'])}")
        if profile.get("escalation_indicators"):
            print(f"    Escalation: {', '.join(profile['escalation_indicators'])}")


def cmd_history(args):
    """Show selection history."""
    if not SELECTIONS_DIR.exists():
        print("No selection history yet.")
        return
    
    selections = []
    for f in sorted(SELECTIONS_DIR.glob("*.json")):
        selections.append(load_json(f))
    
    print(f"Selection History ({len(selections)})")
    print("=" * 60)
    
    for s in selections[-10:]:  # Show last 10
        print(f"\n  [{s['selected_profile']}] {s['selection_id']}")
        print(f"    Project: {s['project_id']}")
        print(f"    Artifact: {s['artifact_type']}")
        print(f"    Reasons: {', '.join(s['selection_reasons'])}")


def cmd_status(args):
    """Show selection status."""
    ensure_profiles()
    
    profile_count = len(list(PROFILES_DIR.glob("*.json")))
    selection_count = len(list(SELECTIONS_DIR.glob("*.json"))) if SELECTIONS_DIR.exists() else 0
    
    print("Adaptive Qualification Status")
    print("=" * 60)
    print(f"Profiles:    {profile_count}")
    print(f"Selections:  {selection_count}")


COMMANDS = {
    "select": cmd_select,
    "list-profiles": cmd_list_profiles,
    "history": cmd_history,
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
