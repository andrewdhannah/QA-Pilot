#!/usr/bin/env python3
"""
Assurance Observatory — QA-PILOT-ASSURANCE-OBSERVATORY-1

Aggregates assurance ecosystem outputs into human-decidable project health views.

Commands:
  fleet               Generate fleet-wide observatory report
  project <id>        Show project health detail
  trends              Show fleet trends
  attention           Show projects needing attention
  status              Show observatory status
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
EVIDENCE_STORE = PROJECT_ROOT / "data" / "runtime-evidence"
PROJECTS_DIR = EVIDENCE_STORE / "projects"
ONBOARDING_DIR = DATA_DIR / "onboarding-records"
DISCOVERIES_DIR = DATA_DIR / "capability-discoveries"
OBSERVATORY_DIR = DATA_DIR / "observatory-reports"


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


def get_onboarded_projects():
    """Get list of onboarded projects."""
    projects = []
    
    if ONBOARDING_DIR.exists():
        for f in ONBOARDING_DIR.glob("*.json"):
            record = load_json(f)
            if record:
                projects.append(record.get("project_id"))
    
    # Also check evidence store for projects not in onboarding
    if PROJECTS_DIR.exists():
        for project_dir in PROJECTS_DIR.iterdir():
            if project_dir.is_dir() and project_dir.name not in projects:
                projects.append(project_dir.name)
    
    return projects


def get_project_health(project_id):
    """Get health assessment for a project."""
    health = {
        "project_id": project_id,
        "health": "healthy",
        "health_rationale": "All checks pass",
        "evidence_coverage": "unknown",
        "qualification_state": "untested",
        "risk_band": "unknown",
        "risk_score": 0,
        "capability_gaps": 0,
        "planning_accuracy": "no_data",
        "recommended_attention": "none"
    }
    
    # Check evidence coverage
    project_dir = PROJECTS_DIR / project_id
    if project_dir.exists():
        records = list((project_dir / "records").glob("*.json")) if (project_dir / "records").exists() else []
        snapshots = list((project_dir / "snapshots").glob("*.json")) if (project_dir / "snapshots").exists() else []
        total = len(records) + len(snapshots)
        
        if total == 0:
            health["evidence_coverage"] = "none"
        elif total < 3:
            health["evidence_coverage"] = "minimal"
        elif total < 10:
            health["evidence_coverage"] = "partial"
        else:
            health["evidence_coverage"] = "full"
    else:
        health["evidence_coverage"] = "unknown"
    
    # Check qualification state
    history_file = EVIDENCE_STORE / "qualification-history.json"
    if history_file.exists():
        try:
            history = load_json(history_file)
            if history.get("total_runs", 0) > 0:
                finding_count = sum(1 for r in history.get("runs", []) if r.get("result", {}).get("disposition") == "FINDING")
                if finding_count > 0:
                    health["qualification_state"] = "finding"
                else:
                    health["qualification_state"] = "pass"
        except:
            pass
    
    # Check risk
    risk_file = EVIDENCE_STORE / "risk-assessments.json"
    if risk_file.exists():
        try:
            risk_data = load_json(risk_file)
            if "projects" in risk_data:
                for p in risk_data["projects"]:
                    if p.get("project_id") == project_id:
                        health["risk_band"] = p.get("risk_band", "unknown")
                        health["risk_score"] = p.get("risk_score", 0)
        except:
            pass
    
    # Check capability gaps
    if DISCOVERIES_DIR.exists():
        for f in DISCOVERIES_DIR.glob("*.json"):
            discovery = load_json(f)
            if discovery and discovery.get("project_id") == project_id:
                health["capability_gaps"] = discovery.get("summary", {}).get("total_findings", 0)
    
    # Determine overall health
    issues = []
    
    if health["evidence_coverage"] in ("none", "unknown"):
        issues.append("no evidence")
    
    if health["qualification_state"] == "finding":
        issues.append("qualification findings")
    
    if health["risk_band"] in ("attention_required", "urgent"):
        issues.append(f"risk band: {health['risk_band']}")
    
    if health["capability_gaps"] > 0:
        issues.append(f"{health['capability_gaps']} capability gaps")
    
    if issues:
        health["health_rationale"] = "; ".join(issues)
        if any(i in ["qualification findings", "risk band: urgent"] for i in issues):
            health["health"] = "critical"
            health["recommended_attention"] = "immediate review"
        elif any(i in ["no evidence", "risk band: attention_required"] for i in issues):
            health["health"] = "attention_needed"
            health["recommended_attention"] = "review recommended"
        else:
            health["health"] = "monitor"
            health["recommended_attention"] = "watch for changes"
    
    return health


def compute_fleet_summary(projects_health):
    """Compute fleet-wide summary."""
    health_dist = {"healthy": 0, "monitor": 0, "attention_needed": 0, "critical": 0}
    
    for p in projects_health:
        health = p["health"]
        health_dist[health] = health_dist.get(health, 0) + 1
    
    # Determine overall status
    if health_dist.get("critical", 0) > 0:
        overall = "critical"
    elif health_dist.get("attention_needed", 0) > 0:
        overall = "degraded"
    elif health_dist.get("monitor", 0) > 0:
        overall = "monitoring"
    else:
        overall = "operational"
    
    return {
        "total_projects": len(projects_health),
        "health_distribution": health_dist,
        "overall_status": overall
    }


def compute_trends():
    """Compute fleet-wide trends."""
    # Simplified trend computation
    return {
        "risk_trend": "stable",
        "freshness_trend": "stable",
        "coverage_trend": "stable"
    }


def generate_observatory_report():
    """Generate fleet-wide observatory report."""
    projects = get_onboarded_projects()
    projects_health = [get_project_health(p) for p in projects]
    
    fleet_summary = compute_fleet_summary(projects_health)
    trends = compute_trends()
    
    attention_needed = [
        {
            "project_id": p["project_id"],
            "reason": p["health_rationale"],
            "priority": "high" if p["health"] == "critical" else "medium"
        }
        for p in projects_health
        if p["health"] in ("attention_needed", "critical")
    ]
    
    report = {
        "observatory_id": generate_id("OBS"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "fleet_summary": fleet_summary,
        "projects": projects_health,
        "trends": trends,
        "attention_needed": attention_needed,
        "advisory_only": True
    }
    
    return report


def cmd_fleet(args):
    """Generate fleet-wide observatory report."""
    report = generate_observatory_report()
    
    # Save report
    save_json(OBSERVATORY_DIR / f"{report['observatory_id']}.json", report)
    
    print(f"Assurance Observatory: {report['observatory_id']}")
    print("=" * 60)
    print(f"Generated: {report['generated_at']}")
    print()
    
    print("Fleet Summary:")
    print(f"  Total projects: {report['fleet_summary']['total_projects']}")
    print(f"  Overall status: {report['fleet_summary']['overall_status']}")
    print(f"  Health distribution:")
    for health, count in report['fleet_summary']['health_distribution'].items():
        print(f"    {health}: {count}")
    print()
    
    print("Projects:")
    for p in report["projects"]:
        print(f"  {p['project_id']}: {p['health']}")
        print(f"    Coverage: {p['evidence_coverage']}")
        print(f"    Qualification: {p['qualification_state']}")
        print(f"    Risk: {p['risk_band']} ({p['risk_score']})")
        if p['capability_gaps'] > 0:
            print(f"    Capability gaps: {p['capability_gaps']}")
        if p['recommended_attention'] != 'none':
            print(f"    Attention: {p['recommended_attention']}")
    
    if report["attention_needed"]:
        print()
        print("Attention Needed:")
        for a in report["attention_needed"]:
            print(f"  [{a['priority'].upper()}] {a['project_id']}: {a['reason']}")


def cmd_project(args):
    """Show project health detail."""
    if len(args) < 1:
        print("Usage: project <project_id>")
        sys.exit(1)
    
    project_id = args[0]
    health = get_project_health(project_id)
    
    print(f"Project Health: {project_id}")
    print("=" * 60)
    print(f"  Health: {health['health']}")
    print(f"  Rationale: {health['health_rationale']}")
    print()
    print(f"  Evidence Coverage: {health['evidence_coverage']}")
    print(f"  Qualification State: {health['qualification_state']}")
    print(f"  Risk Band: {health['risk_band']} ({health['risk_score']})")
    print(f"  Capability Gaps: {health['capability_gaps']}")
    print(f"  Planning Accuracy: {health['planning_accuracy']}")
    print()
    print(f"  Recommended Attention: {health['recommended_attention']}")


def cmd_trends(args):
    """Show fleet trends."""
    trends = compute_trends()
    
    print("Fleet Trends")
    print("=" * 60)
    print(f"  Risk trend: {trends['risk_trend']}")
    print(f"  Freshness trend: {trends['freshness_trend']}")
    print(f"  Coverage trend: {trends['coverage_trend']}")


def cmd_attention(args):
    """Show projects needing attention."""
    projects = get_onboarded_projects()
    attention = []
    
    for project_id in projects:
        health = get_project_health(project_id)
        if health["health"] in ("attention_needed", "critical"):
            attention.append(health)
    
    print("Projects Needing Attention")
    print("=" * 60)
    
    if not attention:
        print("  No projects need attention.")
        return
    
    for p in attention:
        print(f"\n  {p['project_id']}: {p['health']}")
        print(f"    {p['health_rationale']}")
        print(f"    Attention: {p['recommended_attention']}")


def cmd_status(args):
    """Show observatory status."""
    reports = list(OBSERVATORY_DIR.glob("*.json")) if OBSERVATORY_DIR.exists() else []
    projects = get_onboarded_projects()
    
    print("Assurance Observatory Status")
    print("=" * 60)
    print(f"  Projects monitored: {len(projects)}")
    print(f"  Reports generated: {len(reports)}")


COMMANDS = {
    "fleet": cmd_fleet,
    "project": cmd_project,
    "trends": cmd_trends,
    "attention": cmd_attention,
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
