"""
qa_pilot_evidence_lineage.py — Evidence Lineage Implementation

Phase 1 of Assurance Intelligence (#191 architecture).
Connects changes → assurance execution → findings → evidence → decision context.
"""

import json, os, subprocess
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
QA_PILOT_ROOT = os.path.dirname(PROJECT_ROOT)

IMPACT_MAP = {
    "browser-app/": ["accessibility", "language", "uat"],
    "browser-app/js/": ["language", "dependency_risk"],
    "browser-app/admin/": ["accessibility", "uat"],
    "browser-app/apps/": ["accessibility", "uat"],
    "scripts/": ["regression"],
    "docs/": ["privacy", "security"],
    "project-state/": ["regression"],
    "data/": ["privacy", "security"],
}

def get_change_context():
    """Get current change context from git."""
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=QA_PILOT_ROOT)
        commit_short = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=QA_PILOT_ROOT)
        diff = subprocess.run(["git", "diff", "--name-only", "HEAD~1"], capture_output=True, text=True, cwd=QA_PILOT_ROOT)
        return {
            "commit": commit.stdout.strip() if commit.returncode == 0 else "unknown",
            "commit_short": commit_short.stdout.strip() if commit_short.returncode == 0 else "unknown",
            "changed_files": [f.strip() for f in diff.stdout.split("\n") if f.strip()] if diff.returncode == 0 else []
        }
    except:
        return {"commit": "unknown", "commit_short": "unknown", "changed_files": []}

def map_impact(changed_files):
    """Map changed files to affected profiles."""
    affected = set()
    for f in changed_files:
        for prefix, profiles in IMPACT_MAP.items():
            if f.startswith(prefix):
                affected.update(profiles)
    return sorted(affected)

def get_evidence_freshness():
    """Check freshness of existing evidence artifacts."""
    fresh = []
    evidence_dir = os.path.join(QA_PILOT_ROOT, "data")
    if not os.path.exists(evidence_dir):
        return fresh
    now = datetime.now()
    for f in sorted(os.listdir(evidence_dir)):
        if not f.endswith(".json"):
            continue
        path = os.path.join(evidence_dir, f)
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        age_minutes = int((now - mtime).total_seconds() / 60)
        fresh.append({"file": f, "age_minutes": age_minutes})
    return fresh

def get_profile_findings():
    """Extract findings from existing assurance evidence files."""
    findings = []
    evidence_dir = os.path.join(QA_PILOT_ROOT, "data")
    if not os.path.exists(evidence_dir):
        return findings
    for f in sorted(os.listdir(evidence_dir)):
        if not f.endswith(".json"):
            continue
        path = os.path.join(evidence_dir, f)
        try:
            with open(path) as fp:
                data = json.load(fp)
        except:
            continue
        # Extract overall finding from assurance report or artifact
        if "assurance_report" in data:
            report = data["assurance_report"]
            findings.append({
                "evidence_file": f,
                "profile": report.get("profile", "unknown"),
                "overall": report.get("overall", "unknown"),
                "owner_action_required": report.get("owner_action_required", False),
                "generated_at": report.get("generated_at", "unknown")
            })
        elif "artifact" in data:
            art = data["artifact"]
            findings.append({
                "evidence_file": f,
                "profile": art.get("identity", "unknown"),
                "overall": "OBSERVATION",
                "owner_action_required": False,
                "generated_at": "unknown"
            })
    return findings

def main():
    context = get_change_context()
    affected = map_impact(context["changed_files"])
    freshness = get_evidence_freshness()
    findings = get_profile_findings()
    
    lineage = {
        "lineage": {
            "change_id": context["commit_short"],
            "commit": context["commit"],
            "detected_at": datetime.now().isoformat(),
            "changed_files": context["changed_files"][:20],
            "impact_analysis": {
                "affected_profiles": affected,
                "total_profiles": len(affected)
            },
            "evidence_freshness": {
                "all_evidence": freshness,
                "oldest_minutes": freshness[-1]["age_minutes"] if freshness else 0,
                "newest_minutes": freshness[0]["age_minutes"] if freshness else 0,
                "total_files": len(freshness)
            },
            "current_findings": findings,
            "findings_summary": {
                "total": len(findings),
                "owner_action_required": sum(1 for f in findings if f["owner_action_required"]),
                "highest_severity": "OWNER_DECISION_REQUIRED" if any(f["owner_action_required"] for f in findings) else "OBSERVATION"
            }
        }
    }
    
    print(json.dumps(lineage, indent=2))
    print(f"\nLineage recorded: commit={context['commit_short']}")
    print(f"  Changed files: {len(context['changed_files'])}")
    print(f"  Affected profiles: {', '.join(affected) if affected else 'none (full suite)'}")
    print(f"  Evidence files: {len(freshness)}")
    print(f"  Active findings: {len(findings)} ({lineage['lineage']['findings_summary']['owner_action_required']} require Owner action)")

    lineage_path = os.path.join(QA_PILOT_ROOT, "data", "evidence-lineage.json")
    with open(lineage_path, "w") as f:
        json.dump(lineage, f, indent=2)
    print(f"Lineage written to: {lineage_path}")

if __name__ == "__main__":
    main()
