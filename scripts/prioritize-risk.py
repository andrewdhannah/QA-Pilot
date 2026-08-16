#!/usr/bin/env python3
"""
Risk Prioritization Engine — QA-PILOT-RISK-PRIORITIZATION-1

Advisory risk ranking model over existing assurance observations.

Commands:
  assess-project <project_id>    Assess risk for a single project
  assess-fleet                   Assess risk for all projects
  explain <project_id>           Explain risk score for a project
  fleet                          Show fleet risk summary
  projection                     Generate risk-aware discovery projection
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
PROJECTION_FILE = EVIDENCE_STORE / "discovery-projection.json"

# Risk model weights
IMPACT_WEIGHTS = {
    "inform-only": 1.0,
    "recommendation": 2.0,
    "mutation_capability": 3.0,
    "canonical_state": 4.0,
}

CONFIDENCE_WEIGHTS = {
    "qualified": 1.0,
    "partial": 0.7,
    "unknown": 0.4,
}

FRESHNESS_FACTORS = {
    "current": 1.0,
    "aging": 1.2,
    "stale": 1.5,
    "unknown": 2.0,
    "historical": 1.0,  # Records: historical is still valid
    "archived": 1.0,    # Records: archived is still valid
}

HISTORICAL_FACTORS = {
    "no_findings": 1.0,
    "repeated_findings": 1.5,
    "unresolved_findings": 2.0,
}

# Risk bands
RISK_BANDS = [
    (0, 20, "healthy"),
    (21, 50, "monitor"),
    (51, 80, "attention_required"),
    (81, 100, "urgent"),
]

# Coverage domains
COVERAGE_DOMAINS = [
    "runtime_action",
    "runtime_lifecycle",
    "runtime_resource",
    "qualification",
    "security",
    "accessibility",
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


def get_risk_band(score):
    """Get risk band for a score."""
    for low, high, band in RISK_BANDS:
        if low <= score <= high:
            return band
    return "urgent"


def assess_impact_weight(project_id):
    """Assess impact weight based on project's authority scope."""
    # For now, all projects are recommendation-scope
    # Future: read from project governance profile
    return IMPACT_WEIGHTS["recommendation"], "recommendation"


def assess_confidence_weight(project_dir):
    """Assess confidence weight based on evidence quality."""
    records_dir = project_dir / "records"
    snapshots_dir = project_dir / "snapshots"
    
    has_qualified = False
    has_any = False
    
    for evidence_dir in [records_dir, snapshots_dir]:
        if not evidence_dir.exists():
            continue
        for f in evidence_dir.glob("*.json"):
            has_any = True
            try:
                evidence = load_json(f)
                if evidence.get("custody", {}).get("verification_state") == "verified":
                    has_qualified = True
            except:
                pass
    
    if has_qualified:
        return CONFIDENCE_WEIGHTS["qualified"], "qualified"
    elif has_any:
        return CONFIDENCE_WEIGHTS["partial"], "partial"
    else:
        return CONFIDENCE_WEIGHTS["unknown"], "unknown"


def assess_freshness_factor(project_dir):
    """Assess freshness factor based on evidence recency."""
    records_dir = project_dir / "records"
    snapshots_dir = project_dir / "snapshots"
    
    freshest_label = "unknown"
    freshest_timestamp = None
    
    now = datetime.now(timezone.utc)
    
    for evidence_dir in [records_dir, snapshots_dir]:
        if not evidence_dir.exists():
            continue
        for f in evidence_dir.glob("*.json"):
            try:
                evidence = load_json(f)
                captured_at = evidence.get("freshness", {}).get("captured_at")
                if captured_at:
                    ts = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
                    if freshest_timestamp is None or ts > freshest_timestamp:
                        freshest_timestamp = ts
                        freshest_label = evidence.get("freshness", {}).get("confidence_label", "unknown")
            except:
                pass
    
    return FRESHNESS_FACTORS.get(freshest_label, 2.0), freshest_label


def assess_historical_pattern(project_id, project_dir):
    """Assess historical pattern factor based on findings."""
    # Check qualification results
    results_file = EVIDENCE_STORE / "qualification-results.json"
    if results_file.exists():
        try:
            results = load_json(results_file)
            for result in results.get("results", []):
                if result.get("disposition") == "FINDING":
                    return HISTORICAL_FACTORS["unresolved_findings"], "unresolved_findings"
        except:
            pass
    
    # Check for any findings in evidence
    records_dir = project_dir / "records"
    if records_dir.exists():
        for f in records_dir.glob("*.json"):
            try:
                evidence = load_json(f)
                # Simple heuristic: if evidence has findings field
                if evidence.get("findings"):
                    return HISTORICAL_FACTORS["repeated_findings"], "repeated_findings"
            except:
                pass
    
    return HISTORICAL_FACTORS["no_findings"], "no_findings"


def assess_coverage_drivers(project_dir):
    """Assess which coverage domains are missing."""
    drivers = []
    
    for domain in COVERAGE_DOMAINS:
        domain_found = False
        for evidence_dir in [project_dir / "records", project_dir / "snapshots"]:
            if evidence_dir.exists():
                for f in evidence_dir.glob("*.json"):
                    try:
                        evidence = load_json(f)
                        event_type = evidence.get("context", {}).get("execution_context", {}).get("event_type", "")
                        if domain == "runtime_action" and event_type == "runtime_action":
                            domain_found = True
                        elif domain == "runtime_lifecycle" and event_type == "runtime_lifecycle":
                            domain_found = True
                        elif domain == "runtime_resource" and event_type == "runtime_resource":
                            domain_found = True
                    except:
                        pass
        
        if not domain_found:
            drivers.append(f"missing_{domain}_coverage")
    
    return drivers


def assess_project(project_id):
    """Assess risk for a single project."""
    project_dir = PROJECTS_DIR / project_id
    
    if not project_dir.exists():
        return {
            "project_id": project_id,
            "assessment_id": f"RA-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{project_id}",
            "assessed_at": datetime.now(timezone.utc).isoformat(),
            "risk_score": 50,
            "risk_band": "monitor",
            "factors": {
                "impact_weight": 2.0,
                "confidence_weight": 0.4,
                "freshness_factor": 2.0,
                "historical_pattern_factor": 1.0,
                "raw_score": 1.6,
                "normalized_score": 50,
            },
            "drivers": ["project_not_found"],
            "evidence_refs": [],
            "recommendations": ["Project directory not found — cannot assess risk"],
            "advisory_only": True,
        }
    
    # Assess factors
    impact_weight, impact_source = assess_impact_weight(project_id)
    confidence_weight, confidence_source = assess_confidence_weight(project_dir)
    freshness_factor, freshness_source = assess_freshness_factor(project_dir)
    historical_factor, historical_source = assess_historical_pattern(project_id, project_dir)
    
    # Calculate raw score
    raw_score = impact_weight * confidence_weight * freshness_factor * historical_factor
    
    # Normalize to 0-100 scale
    # Max possible: 4.0 * 1.0 * 2.0 * 2.0 = 16.0
    # Min possible: 1.0 * 0.4 * 1.0 * 1.0 = 0.4
    # Normalize: (raw - min) / (max - min) * 100
    min_score = 0.4
    max_score = 16.0
    normalized_score = min(100, max(0, int((raw_score - min_score) / (max_score - min_score) * 100)))
    
    risk_band = get_risk_band(normalized_score)
    
    # Assess drivers
    coverage_drivers = assess_coverage_drivers(project_dir)
    drivers = []
    if freshness_source in ("stale", "unknown"):
        drivers.append(f"freshness_{freshness_source}")
    if historical_source != "no_findings":
        drivers.append(f"historical_{historical_source}")
    drivers.extend(coverage_drivers[:3])  # Limit to top 3 coverage drivers
    
    # Generate recommendations
    recommendations = []
    if "missing_security_coverage" in drivers:
        recommendations.append("Consider adding security evidence coverage")
    if "missing_accessibility_coverage" in drivers:
        recommendations.append("Consider adding accessibility evidence coverage")
    if "missing_runtime_lifecycle_coverage" in drivers:
        recommendations.append("Consider adding runtime lifecycle event capture")
    if freshness_source in ("stale", "unknown"):
        recommendations.append("Consider refreshing evidence")
    if historical_source == "unresolved_findings":
        recommendations.append("Review unresolved findings")
    
    return {
        "project_id": project_id,
        "assessment_id": f"RA-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{project_id}",
        "assessed_at": datetime.now(timezone.utc).isoformat(),
        "risk_score": normalized_score,
        "risk_band": risk_band,
        "factors": {
            "impact_weight": impact_weight,
            "confidence_weight": confidence_weight,
            "freshness_factor": freshness_factor,
            "historical_pattern_factor": historical_factor,
            "raw_score": raw_score,
            "normalized_score": normalized_score,
        },
        "drivers": drivers,
        "evidence_refs": [],
        "recommendations": recommendations,
        "advisory_only": True,
        "authority_boundary": {
            "can_dispatch": False,
            "can_remediate": False,
            "can_close_findings": False,
            "can_decide": False,
        },
    }


def assess_fleet():
    """Assess risk for all projects."""
    if not PROJECTS_DIR.exists():
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_projects": 0,
            "by_band": {},
            "attention_needed": [],
            "projects": [],
        }
    
    projects = []
    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if project_dir.is_dir():
            assessment = assess_project(project_dir.name)
            projects.append(assessment)
    
    # Fleet summary
    band_counts = {}
    attention_needed = []
    
    for p in projects:
        band = p["risk_band"]
        band_counts[band] = band_counts.get(band, 0) + 1
        
        if band in ("attention_required", "urgent"):
            attention_needed.append({
                "project_id": p["project_id"],
                "risk_score": p["risk_score"],
                "risk_band": p["risk_band"],
                "drivers": p["drivers"],
            })
    
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_projects": len(projects),
        "by_band": band_counts,
        "attention_needed": attention_needed,
        "projects": projects,
    }


def cmd_assess_project(args):
    """Assess risk for a single project."""
    if len(args) < 1:
        print("Usage: assess-project <project_id>")
        sys.exit(1)
    
    project_id = args[0]
    assessment = assess_project(project_id)
    
    print(f"Risk Assessment: {project_id}")
    print("=" * 60)
    print(f"  Score:       {assessment['risk_score']}/100 ({assessment['risk_band']})")
    print(f"  Assessment:  {assessment['assessment_id']}")
    print()
    
    print("  Factors:")
    f = assessment["factors"]
    print(f"    Impact:            {f['impact_weight']}")
    print(f"    Confidence:        {f['confidence_weight']}")
    print(f"    Freshness:         {f['freshness_factor']}")
    print(f"    Historical:        {f['historical_pattern_factor']}")
    print(f"    Raw:               {f['raw_score']:.2f}")
    print(f"    Normalized:        {f['normalized_score']}")
    print()
    
    if assessment["drivers"]:
        print("  Drivers:")
        for d in assessment["drivers"]:
            print(f"    - {d}")
        print()
    
    if assessment["recommendations"]:
        print("  Recommendations:")
        for r in assessment["recommendations"]:
            print(f"    - {r}")


def cmd_assess_fleet(args):
    """Assess risk for all projects."""
    fleet = assess_fleet()
    
    print("Fleet Risk Assessment")
    print("=" * 60)
    print(f"Generated: {fleet['generated_at']}")
    print(f"Projects:  {fleet['total_projects']}")
    print()
    
    print("By Risk Band:")
    for band, count in fleet["by_band"].items():
        print(f"  {band}: {count}")
    
    if fleet["attention_needed"]:
        print()
        print("Attention Needed:")
        for item in fleet["attention_needed"]:
            print(f"  [{item['risk_band'].upper()}] {item['project_id']}: score={item['risk_score']}")
            for d in item["drivers"]:
                print(f"    - {d}")


def cmd_explain(args):
    """Explain risk score for a project."""
    if len(args) < 1:
        print("Usage: explain <project_id>")
        sys.exit(1)
    
    project_id = args[0]
    assessment = assess_project(project_id)
    
    print(f"Risk Explanation: {project_id}")
    print("=" * 60)
    print(f"Risk Score: {assessment['risk_score']}/100 ({assessment['risk_band']})")
    print()
    
    f = assessment["factors"]
    print("Factor Breakdown:")
    print(f"  Impact: {f['impact_weight']} (recommendation scope)")
    print(f"  Confidence: {f['confidence_weight']} (evidence quality)")
    print(f"  Freshness: {f['freshness_factor']} (uncertainty level)")
    print(f"  Historical: {f['historical_pattern_factor']} (finding pattern)")
    print(f"  Raw: {f['impact_weight']} × {f['confidence_weight']} × {f['freshness_factor']} × {f['historical_pattern_factor']} = {f['raw_score']:.2f}")
    print(f"  Normalized: {f['normalized_score']}/100")
    print()
    
    if assessment["drivers"]:
        print("Drivers:")
        for d in assessment["drivers"]:
            print(f"  - {d}")
        print()
    
    print("This assessment means:")
    if assessment["risk_band"] == "healthy":
        print("  No attention needed. Evidence is sufficient and current.")
    elif assessment["risk_band"] == "monitor":
        print("  Watch for changes. Evidence is adequate but could be improved.")
    elif assessment["risk_band"] == "attention_required":
        print("  Human should review. Evidence gaps or issues detected.")
    elif assessment["risk_band"] == "urgent":
        print("  Immediate attention needed. Significant evidence gaps or issues.")
    
    print()
    print("Authority boundary:")
    print("  This is an advisory ranking only.")
    print("  It does NOT determine what must be changed.")
    print("  Owner decides what action to take.")


def cmd_fleet(args):
    """Show fleet risk summary."""
    fleet = assess_fleet()
    
    print("Fleet Risk Summary")
    print("=" * 60)
    print(f"Generated: {fleet['generated_at']}")
    print(f"Projects:  {fleet['total_projects']}")
    print()
    
    for p in fleet["projects"]:
        print(f"  {p['project_id']}: {p['risk_score']}/100 ({p['risk_band']})")
        if p["drivers"]:
            for d in p["drivers"][:2]:
                print(f"    - {d}")
    
    if fleet["attention_needed"]:
        print()
        print(f"Attention needed: {len(fleet['attention_needed'])} projects")


def cmd_projection(args):
    """Generate risk-aware discovery projection."""
    fleet = assess_fleet()
    
    # Load existing projection
    if PROJECTION_FILE.exists():
        projection = load_json(PROJECTION_FILE)
    else:
        projection = {}
    
    # Extend with risk data
    projection["risk_assessment"] = {
        "generated_at": fleet["generated_at"],
        "total_projects": fleet["total_projects"],
        "by_band": fleet["by_band"],
        "attention_needed": fleet["attention_needed"],
    }
    
    # Extend per-project data
    if "projects" in projection:
        for proj in projection["projects"]:
            project_id = proj.get("project_id")
            risk = next((p for p in fleet["projects"] if p["project_id"] == project_id), None)
            if risk:
                proj["risk_band"] = risk["risk_band"]
                proj["risk_score"] = risk["risk_score"]
                proj["attention_reasons"] = risk["drivers"]
    
    save_json(PROJECTION_FILE, projection)
    print(f"Discovery projection updated: {PROJECTION_FILE}")
    print(f"Risk assessment added for {fleet['total_projects']} projects")


COMMANDS = {
    "assess-project": cmd_assess_project,
    "assess-fleet": cmd_assess_fleet,
    "explain": cmd_explain,
    "fleet": cmd_fleet,
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
