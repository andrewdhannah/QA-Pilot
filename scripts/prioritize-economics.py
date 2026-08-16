#!/usr/bin/env python3
"""
Assurance Economics Engine — QA-PILOT-ASSURANCE-ECONOMICS-LAYER-1

Advisory resource prioritization by attention value scoring.

Commands:
  prioritize-project <project_id>    Prioritize a project
  prioritize-fleet                   Prioritize all projects
  explain <project_id>               Explain attention value score
  history                            Show prioritization history
  status                             Show economics status
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
ECONOMICS_DIR = DATA_DIR / "economics-reports"
ONBOARDING_DIR = DATA_DIR / "onboarding-records"
DISCOVERIES_DIR = DATA_DIR / "capability-discoveries"


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


def get_risk_exposure(project_id):
    """Get risk exposure for a project."""
    risk_file = EVIDENCE_STORE / "risk-assessments.json"
    if not risk_file.exists():
        return 50, "unknown", []  # Default medium risk
    
    try:
        risk_data = load_json(risk_file)
        if "projects" in risk_data:
            for p in risk_data["projects"]:
                if p.get("project_id") == project_id:
                    return p.get("risk_score", 50), p.get("risk_band", "unknown"), p.get("drivers", [])
    except:
        pass
    
    return 50, "unknown", []


def get_change_frequency(project_id):
    """Get change frequency for a project."""
    project_dir = PROJECTS_DIR / project_id
    if not project_dir.exists():
        return 1.0, 0  # Default average
    
    # Count evidence files as proxy for change frequency
    count = 0
    for evidence_dir in [project_dir / "records", project_dir / "snapshots"]:
        if evidence_dir.exists():
            count += len(list(evidence_dir.glob("*.json")))
    
    # Map count to frequency factor
    if count == 0:
        return 0.5, count  # Rarely changes
    elif count < 5:
        return 1.0, count  # Average
    elif count < 10:
        return 1.5, count  # Active
    else:
        return 2.0, count  # Frequently changes


def get_authority_impact(project_id):
    """Get authority impact for a project."""
    # Check onboarding for authority scope
    if ONBOARDING_DIR.exists():
        for f in ONBOARDING_DIR.glob("*.json"):
            record = load_json(f)
            if record and record.get("project_id") == project_id:
                # Default to recommendation scope
                return 2.0, "recommendation"
    
    return 1.0, "observation_only"


def get_confidence(project_id):
    """Get confidence level for a project."""
    project_dir = PROJECTS_DIR / project_id
    if not project_dir.exists():
        return 0.4, "no_evidence"  # Low confidence
    
    # Check evidence count
    count = 0
    for evidence_dir in [project_dir / "records", project_dir / "snapshots"]:
        if evidence_dir.exists():
            count += len(list(evidence_dir.glob("*.json")))
    
    if count == 0:
        return 0.4, "no_evidence"
    elif count < 3:
        return 0.7, "partial_evidence"
    else:
        return 1.0, "full_evidence"


def get_estimated_effort(project_id):
    """Get estimated effort for review."""
    # Check capability gaps as proxy for effort
    if DISCOVERIES_DIR.exists():
        for f in DISCOVERIES_DIR.glob("*.json"):
            discovery = load_json(f)
            if discovery and discovery.get("project_id") == project_id:
                gaps = discovery.get("summary", {}).get("total_findings", 0)
                if gaps == 0:
                    return 1.0, "minimal"
                elif gaps < 3:
                    return 2.0, "low"
                elif gaps < 5:
                    return 5.0, "medium"
                else:
                    return 10.0, "high"
    
    return 1.0, "minimal"


def compute_attention_value(project_id):
    """Compute attention value for a project."""
    # Get components
    risk_score, risk_band, risk_drivers = get_risk_exposure(project_id)
    change_freq, change_count = get_change_frequency(project_id)
    authority_impact, authority_scope = get_authority_impact(project_id)
    confidence, confidence_source = get_confidence(project_id)
    effort, effort_level = get_estimated_effort(project_id)
    
    # Compute attention value
    # Attention Value = Risk × Change × Impact × Confidence ÷ Effort
    attention_value = (risk_score * change_freq * authority_impact * confidence) / effort
    
    # Normalize to 0-100 scale
    # Max possible: 100 * 2.0 * 4.0 * 1.0 / 0.5 = 1600
    # Min possible: 0 * 0.5 * 1.0 * 0.4 / 10.0 = 0
    normalized_score = min(100, max(0, int(attention_value / 16)))  # Scale factor
    
    # Determine attention level
    if normalized_score <= 20:
        attention_level = "low"
    elif normalized_score <= 50:
        attention_level = "medium"
    elif normalized_score <= 80:
        attention_level = "high"
    else:
        attention_level = "critical"
    
    # Build contributing factors
    contributing_factors = []
    if risk_score > 50:
        contributing_factors.append(f"elevated risk ({risk_band})")
    if change_count > 5:
        contributing_factors.append(f"frequent changes ({change_count})")
    if authority_impact > 2.0:
        contributing_factors.append(f"authority scope ({authority_scope})")
    if confidence < 0.7:
        contributing_factors.append(f"low confidence ({confidence_source})")
    if effort > 5.0:
        contributing_factors.append(f"high effort ({effort_level})")
    
    # Build result
    result = {
        "economics_id": generate_id("ECON"),
        "project_id": project_id,
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "attention_score": normalized_score,
        "attention_level": attention_level,
        "components": {
            "risk_exposure": risk_score,
            "risk_band": risk_band,
            "change_frequency": change_freq,
            "change_count": change_count,
            "authority_impact": authority_impact,
            "authority_scope": authority_scope,
            "confidence": confidence,
            "confidence_source": confidence_source,
            "estimated_effort": effort,
            "effort_level": effort_level
        },
        "contributing_factors": contributing_factors,
        "evidence_refs": risk_drivers,
        "advisory_only": True
    }
    
    return result


def cmd_prioritize_project(args):
    """Prioritize a project."""
    if len(args) < 1:
        print("Usage: prioritize-project <project_id>")
        sys.exit(1)
    
    project_id = args[0]
    result = compute_attention_value(project_id)
    
    # Save result
    save_json(ECONOMICS_DIR / f"{result['economics_id']}.json", result)
    
    print(f"Economics Assessment: {project_id}")
    print("=" * 60)
    print(f"  Attention Score: {result['attention_score']}/100 ({result['attention_level']})")
    print()
    print("  Components:")
    print(f"    Risk Exposure: {result['components']['risk_exposure']} ({result['components']['risk_band']})")
    print(f"    Change Frequency: {result['components']['change_frequency']} ({result['components']['change_count']} changes)")
    print(f"    Authority Impact: {result['components']['authority_impact']} ({result['components']['authority_scope']})")
    print(f"    Confidence: {result['components']['confidence']} ({result['components']['confidence_source']})")
    print(f"    Estimated Effort: {result['components']['estimated_effort']} ({result['components']['effort_level']})")
    print()
    if result['contributing_factors']:
        print("  Contributing Factors:")
        for factor in result['contributing_factors']:
            print(f"    - {factor}")
    print()
    print("  This is an advisory recommendation.")
    print("  Owner decides action.")


def cmd_prioritize_fleet(args):
    """Prioritize all projects."""
    if not PROJECTS_DIR.exists():
        print("No projects found.")
        return
    
    results = []
    
    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if project_dir.is_dir():
            result = compute_attention_value(project_dir.name)
            save_json(ECONOMICS_DIR / f"{result['economics_id']}.json", result)
            results.append(result)
    
    # Sort by attention score
    results.sort(key=lambda x: x["attention_score"], reverse=True)
    
    print("Fleet Economics Assessment")
    print("=" * 60)
    
    for i, result in enumerate(results, 1):
        print(f"\n  {i}. {result['project_id']}")
        print(f"     Score: {result['attention_score']}/100 ({result['attention_level']})")
        if result['contributing_factors']:
            print(f"     Factors: {', '.join(result['contributing_factors'][:2])}")
    
    print()
    print("  This is an advisory ranking.")
    print("  Owner decides action.")


def cmd_explain(args):
    """Explain attention value score."""
    if len(args) < 1:
        print("Usage: explain <project_id>")
        sys.exit(1)
    
    project_id = args[0]
    result = compute_attention_value(project_id)
    
    print(f"Economics Explanation: {project_id}")
    print("=" * 60)
    print(f"Attention Score: {result['attention_score']}/100 ({result['attention_level']})")
    print()
    
    print("Component Breakdown:")
    print(f"  Risk Exposure: {result['components']['risk_exposure']}")
    print(f"    Band: {result['components']['risk_band']}")
    print(f"  × Change Frequency: {result['components']['change_frequency']}")
    print(f"    Count: {result['components']['change_count']}")
    print(f"  × Authority Impact: {result['components']['authority_impact']}")
    print(f"    Scope: {result['components']['authority_scope']}")
    print(f"  × Confidence: {result['components']['confidence']}")
    print(f"    Source: {result['components']['confidence_source']}")
    print(f"  ÷ Estimated Effort: {result['components']['estimated_effort']}")
    print(f"    Level: {result['components']['effort_level']}")
    print()
    
    # Show calculation
    raw = (result['components']['risk_exposure'] * 
           result['components']['change_frequency'] * 
           result['components']['authority_impact'] * 
           result['components']['confidence'])
    normalized = raw / result['components']['estimated_effort']
    print(f"  Raw: {result['components']['risk_exposure']} × {result['components']['change_frequency']} × {result['components']['authority_impact']} × {result['components']['confidence']} = {raw:.1f}")
    print(f"  Normalized: {raw:.1f} ÷ {result['components']['estimated_effort']} = {normalized:.1f}")
    print(f"  Score: {result['attention_score']}/100")
    print()
    
    if result['contributing_factors']:
        print("Contributing Factors:")
        for factor in result['contributing_factors']:
            print(f"  - {factor}")
    print()
    print("This is an advisory recommendation.")
    print("Owner decides action.")


def cmd_history(args):
    """Show prioritization history."""
    if not ECONOMICS_DIR.exists():
        print("No economics history yet.")
        return
    
    results = []
    for f in sorted(ECONOMICS_DIR.glob("*.json")):
        results.append(load_json(f))
    
    print(f"Economics History ({len(results)})")
    print("=" * 60)
    
    for r in results[-10:]:  # Show last 10
        print(f"\n  [{r['attention_level']}] {r['project_id']}")
        print(f"    Score: {r['attention_score']}/100")
        print(f"    Computed: {r['computed_at']}")


def cmd_status(args):
    """Show economics status."""
    reports = list(ECONOMICS_DIR.glob("*.json")) if ECONOMICS_DIR.exists() else []
    
    print("Assurance Economics Status")
    print("=" * 60)
    print(f"  Reports: {len(reports)}")


COMMANDS = {
    "prioritize-project": cmd_prioritize_project,
    "prioritize-fleet": cmd_prioritize_fleet,
    "explain": cmd_explain,
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
