#!/usr/bin/env python3
"""
Fleet Freshness Discovery Engine — QA-PILOT-FLEET-FRESHNESS-DISCOVERY-1

Advisory discovery layer that identifies evidence freshness and coverage
state across governed projects.

Commands:
  assess <project_id>    Assess freshness and coverage for a single project
  assess-all             Assess all projects
  fleet                  Show fleet-wide freshness summary
  projection             Generate discovery projection
  recommendations        Show recommendations for all projects
"""

import sys
import os
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

# --- Configuration ---

PROJECT_ROOT = Path(__file__).parent.parent
EVIDENCE_STORE = PROJECT_ROOT / "data" / "runtime-evidence"
PROJECTS_DIR = EVIDENCE_STORE / "projects"
PROJECTION_FILE = EVIDENCE_STORE / "discovery-projection.json"

# Freshness windows (seconds)
RECORD_WINDOWS = {
    "current": 60 * 60,      # 60 minutes
    "historical": 4 * 60 * 60,  # 4 hours
}
SNAPSHOT_WINDOWS = {
    "current": 15 * 60,      # 15 minutes
    "aging": 60 * 60,        # 60 minutes
}

# Coverage domains
COVERAGE_DOMAINS = [
    "runtime_action",
    "runtime_lifecycle",
    "runtime_resource",
    "qualification",
    "security",
    "accessibility",
]

# Essential domains (for minimal coverage)
ESSENTIAL_DOMAINS = [
    "runtime_action",
    "runtime_lifecycle",
]


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


def compute_record_freshness(captured_at_str):
    """Compute freshness label for a record."""
    now = datetime.now(timezone.utc)
    try:
        ts = datetime.fromisoformat(captured_at_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return "unknown"
    
    age_seconds = (now - ts).total_seconds()
    
    if age_seconds < RECORD_WINDOWS["current"]:
        return "current"
    elif age_seconds < RECORD_WINDOWS["historical"]:
        return "historical"
    else:
        return "archived"


def compute_snapshot_freshness(captured_at_str):
    """Compute freshness label for a snapshot."""
    now = datetime.now(timezone.utc)
    try:
        ts = datetime.fromisoformat(captured_at_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return "unknown"
    
    age_seconds = (now - ts).total_seconds()
    
    if age_seconds < SNAPSHOT_WINDOWS["current"]:
        return "current"
    elif age_seconds < SNAPSHOT_WINDOWS["aging"]:
        return "aging"
    else:
        return "stale"


def assess_domain(project_dir, domain):
    """Assess freshness and coverage for a single domain."""
    records_dir = project_dir / "records"
    snapshots_dir = project_dir / "snapshots"
    
    # Count evidence in this domain
    count = 0
    freshest_label = "unknown"
    freshest_timestamp = None
    
    for evidence_dir in [records_dir, snapshots_dir]:
        if not evidence_dir.exists():
            continue
        for f in evidence_dir.glob("*.json"):
            try:
                evidence = load_json(f)
            except:
                continue
            
            # Check if this evidence belongs to this domain
            event_type = evidence.get("context", {}).get("execution_context", {}).get("event_type", "")
            evidence_class = evidence.get("evidence_class", "")
            
            domain_match = False
            if domain == "runtime_action" and event_type == "runtime_action":
                domain_match = True
            elif domain == "runtime_lifecycle" and event_type == "runtime_lifecycle":
                domain_match = True
            elif domain == "runtime_resource" and event_type == "runtime_resource":
                domain_match = True
            elif domain == "qualification" and evidence.get("schema_version", "").startswith("qualification"):
                domain_match = True
            
            if domain_match:
                count += 1
                captured_at = evidence.get("freshness", {}).get("captured_at")
                if captured_at:
                    if evidence_class == "record":
                        label = compute_record_freshness(captured_at)
                    else:
                        label = compute_snapshot_freshness(captured_at)
                    
                    # Track freshest
                    if freshest_timestamp is None or captured_at > freshest_timestamp:
                        freshest_label = label
                        freshest_timestamp = captured_at
    
    if count == 0:
        return {
            "status": "uncovered",
            "freshness": "unknown",
            "count": 0,
        }
    
    return {
        "status": "covered",
        "freshness": freshest_label,
        "count": count,
    }


def assess_project(project_id):
    """Assess freshness and coverage for a single project."""
    project_dir = PROJECTS_DIR / project_id
    
    if not project_dir.exists():
        return {
            "project_id": project_id,
            "freshness_state": "unknown",
            "coverage_state": "unknown",
            "domains": {},
            "missing_domains": COVERAGE_DOMAINS.copy(),
            "last_qualification": None,
            "recommendations": [f"Project directory not found: {project_id}"],
        }
    
    # Assess each domain
    domains = {}
    covered_count = 0
    essential_covered = 0
    freshest_timestamp = None
    
    for domain in COVERAGE_DOMAINS:
        assessment = assess_domain(project_dir, domain)
        domains[domain] = assessment
        
        if assessment["status"] == "covered":
            covered_count += 1
            if domain in ESSENTIAL_DOMAINS:
                essential_covered += 1
    
    # Determine coverage state
    coverage_ratio = covered_count / len(COVERAGE_DOMAINS)
    essential_ratio = essential_covered / len(ESSENTIAL_DOMAINS)
    
    if coverage_ratio >= 1.0:
        coverage_state = "full"
    elif coverage_ratio >= 0.5:
        coverage_state = "partial"
    elif essential_ratio >= 0.5:
        coverage_state = "minimal"
    elif covered_count == 0:
        coverage_state = "none"
    else:
        coverage_state = "unknown"
    
    # Determine freshness state (freshest evidence across all domains)
    freshness_states = []
    for domain, assessment in domains.items():
        if assessment["freshness"] != "unknown":
            freshness_states.append(assessment["freshness"])
    
    if not freshness_states:
        freshness_state = "unknown"
    elif "current" in freshness_states:
        freshness_state = "current"
    elif "aging" in freshness_states:
        freshness_state = "aging"
    elif "stale" in freshness_states:
        freshness_state = "stale"
    else:
        freshness_state = "historical"
    
    # Missing domains
    missing_domains = [d for d, a in domains.items() if a["status"] == "uncovered"]
    
    # Recommendations
    recommendations = []
    if "runtime_lifecycle" in missing_domains:
        recommendations.append("Consider adding runtime lifecycle event capture")
    if "runtime_resource" in missing_domains:
        recommendations.append("Consider adding runtime resource observation")
    if "security" in missing_domains:
        recommendations.append("Consider adding security evidence")
    if "accessibility" in missing_domains:
        recommendations.append("Consider adding accessibility evidence")
    if freshness_state == "stale":
        recommendations.append("Evidence is stale — consider refreshing")
    if coverage_state == "none":
        recommendations.append("No evidence coverage — consider adding basic runtime evidence")
    
    return {
        "project_id": project_id,
        "freshness_state": freshness_state,
        "coverage_state": coverage_state,
        "domains": domains,
        "missing_domains": missing_domains,
        "last_qualification": None,
        "recommendations": recommendations,
    }


def assess_fleet():
    """Assess freshness and coverage for all projects."""
    if not PROJECTS_DIR.exists():
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_projects": 0,
            "projects_by_freshness": {},
            "projects_by_coverage": {},
            "attention_needed": [],
            "projects": [],
        }
    
    projects = []
    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if project_dir.is_dir():
            assessment = assess_project(project_dir.name)
            projects.append(assessment)
    
    # Fleet summary
    freshness_counts = {}
    coverage_counts = {}
    attention_needed = []
    
    for p in projects:
        fs = p["freshness_state"]
        cs = p["coverage_state"]
        freshness_counts[fs] = freshness_counts.get(fs, 0) + 1
        coverage_counts[cs] = coverage_counts.get(cs, 0) + 1
        
        # Determine attention priority
        if cs in ("none", "unknown"):
            priority = "high"
            reason = f"Coverage state: {cs}"
        elif cs == "minimal":
            priority = "medium"
            reason = "Minimal coverage — only essential domains"
        elif fs == "stale":
            priority = "medium"
            reason = "Evidence is stale"
        elif cs == "partial":
            priority = "low"
            reason = f"Partial coverage — missing: {', '.join(p['missing_domains'][:3])}"
        else:
            continue
        
        attention_needed.append({
            "project_id": p["project_id"],
            "reason": reason,
            "priority": priority,
        })
    
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_projects": len(projects),
        "projects_by_freshness": freshness_counts,
        "projects_by_coverage": coverage_counts,
        "attention_needed": attention_needed,
        "projects": projects,
    }


def cmd_assess(args):
    """Assess freshness and coverage for a single project."""
    if len(args) < 1:
        print("Usage: assess <project_id>")
        sys.exit(1)
    
    project_id = args[0]
    assessment = assess_project(project_id)
    
    print(f"Fleet Freshness Assessment: {project_id}")
    print("=" * 60)
    print(f"  Freshness:    {assessment['freshness_state']}")
    print(f"  Coverage:     {assessment['coverage_state']}")
    print(f"  Missing:      {', '.join(assessment['missing_domains']) or 'none'}")
    print()
    
    print("  Domains:")
    for domain, info in assessment["domains"].items():
        status_icon = "✓" if info["status"] == "covered" else "✗"
        print(f"    [{status_icon}] {domain}: {info['status']} ({info['freshness']}, {info['count']} records)")
    
    if assessment["recommendations"]:
        print()
        print("  Recommendations:")
        for r in assessment["recommendations"]:
            print(f"    - {r}")


def cmd_assess_all(args):
    """Assess all projects."""
    fleet = assess_fleet()
    
    print("Fleet Freshness Assessment — All Projects")
    print("=" * 60)
    
    for p in fleet["projects"]:
        print(f"\n  Project: {p['project_id']}")
        print(f"    Freshness: {p['freshness_state']}")
        print(f"    Coverage:  {p['coverage_state']}")
        print(f"    Missing:   {', '.join(p['missing_domains']) or 'none'}")
    
    print(f"\n{'='*60}")
    print(f"Total projects: {fleet['total_projects']}")
    print(f"By freshness: {fleet['projects_by_freshness']}")
    print(f"By coverage: {fleet['projects_by_coverage']}")


def cmd_fleet(args):
    """Show fleet-wide freshness summary."""
    fleet = assess_fleet()
    
    print("Fleet Freshness Summary")
    print("=" * 60)
    print(f"Generated: {fleet['generated_at']}")
    print(f"Projects:  {fleet['total_projects']}")
    print()
    
    print("By Freshness:")
    for state, count in fleet["projects_by_freshness"].items():
        print(f"  {state}: {count}")
    
    print()
    print("By Coverage:")
    for state, count in fleet["projects_by_coverage"].items():
        print(f"  {state}: {count}")
    
    if fleet["attention_needed"]:
        print()
        print("Attention Needed:")
        for item in fleet["attention_needed"]:
            print(f"  [{item['priority'].upper()}] {item['project_id']}: {item['reason']}")


def cmd_projection(args):
    """Generate discovery projection."""
    fleet = assess_fleet()
    
    projection = {
        "generated_at": fleet["generated_at"],
        "total_projects": fleet["total_projects"],
        "projects_by_freshness": fleet["projects_by_freshness"],
        "projects_by_coverage": fleet["projects_by_coverage"],
        "attention_needed": fleet["attention_needed"],
        "projects": [
            {
                "project_id": p["project_id"],
                "freshness_state": p["freshness_state"],
                "coverage_state": p["coverage_state"],
                "missing_domains": p["missing_domains"],
                "last_qualification": p["last_qualification"],
                "recommendations": p["recommendations"],
            }
            for p in fleet["projects"]
        ],
    }
    
    save_json(PROJECTION_FILE, projection)
    print(f"Discovery projection saved to: {PROJECTION_FILE}")
    print(f"Projects: {projection['total_projects']}")
    print(f"Attention needed: {len(projection['attention_needed'])}")


def cmd_recommendations(args):
    """Show recommendations for all projects."""
    fleet = assess_fleet()
    
    print("Fleet Recommendations")
    print("=" * 60)
    
    has_recommendations = False
    for p in fleet["projects"]:
        if p["recommendations"]:
            has_recommendations = True
            print(f"\n  {p['project_id']}:")
            for r in p["recommendations"]:
                print(f"    - {r}")
    
    if not has_recommendations:
        print("  No recommendations. All projects have sufficient coverage.")


COMMANDS = {
    "assess": cmd_assess,
    "assess-all": cmd_assess_all,
    "fleet": cmd_fleet,
    "projection": cmd_projection,
    "recommendations": cmd_recommendations,
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
