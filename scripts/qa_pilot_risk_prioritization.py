"""
qa_pilot_risk_prioritization.py — Risk Prioritization Implementation

Phase 2 of Assurance Intelligence (#191 architecture).
Transforms existing findings into a ranked attention surface.
Three levels: HIGH ATTENTION / REVIEW / MONITOR.
"""

import json, os, subprocess
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
QA_PILOT_ROOT = os.path.dirname(PROJECT_ROOT)

RISK_WEIGHTS = {
    "security": {"OWNER_DECISION_REQUIRED": "HIGH_ATTENTION", "GAP": "HIGH_ATTENTION", "OBSERVATION": "REVIEW"},
    "privacy":  {"OWNER_DECISION_REQUIRED": "HIGH_ATTENTION", "GAP": "HIGH_ATTENTION", "OBSERVATION": "REVIEW"},
    "dependency_risk": {"OWNER_DECISION_REQUIRED": "REVIEW", "OBSERVATION": "REVIEW"},
    "accessibility": {"OBSERVATION": "MONITOR"},
    "performance": {"OBSERVATION": "MONITOR"},
    "regression": {"OBSERVATION": "REVIEW"},
    "uat": {"OBSERVATION": "MONITOR"},
    "language": {"OBSERVATION": "MONITOR"},
    "release": {"OWNER_REVIEW_REQUIRED": "HIGH_ATTENTION", "OWNER_DECISION_REQUIRED": "HIGH_ATTENTION", "OBSERVATION": "REVIEW"},
}

def load_evidence(rel_path):
    path = os.path.join(QA_PILOT_ROOT, rel_path)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def get_change_context():
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=QA_PILOT_ROOT)
        diff = subprocess.run(["git", "diff", "--name-only", "HEAD~1"], capture_output=True, text=True, cwd=QA_PILOT_ROOT)
        return {
            "commit": commit.stdout.strip() if commit.returncode == 0 else "unknown",
            "changed_files": [f.strip() for f in diff.stdout.split("\n") if f.strip()] if diff.returncode == 0 else []
        }
    except:
        return {"commit": "unknown", "changed_files": []}

def classify_finding(profile, finding):
    """Classify a single finding into HIGH_ATTENTION / REVIEW / MONITOR."""
    status = finding.get("status", "OBSERVATION") if isinstance(finding, dict) else "OBSERVATION"
    weights = RISK_WEIGHTS.get(profile, {})
    return weights.get(status, "MONITOR")

def main():
    context = get_change_context()
    
    # Load evidence sources
    release = load_evidence("data/release-readiness-evidence.json")
    lineage = load_evidence("data/evidence-lineage.json")
    
    prioritized = {"HIGH_ATTENTION": [], "REVIEW": [], "MONITOR": []}
    
    # Classify from release readiness summary
    if release:
        summary = release.get("assurance_report", {}).get("summary", {})
        overall = summary.get("overall", "OBSERVATION")
        priority = RISK_WEIGHTS.get("release", {}).get(overall, "MONITOR")
        prioritized[priority].append({
            "capability": "Release Readiness",
            "category": "Aggregate",
            "status": overall,
            "priority": priority
        })
        
        for inp in release.get("assurance_report", {}).get("inputs", []):
            cap_name = inp.get("name", "")
            status = inp.get("status", "OBSERVATION")
            profile_key = "dependency_risk" if "dependency" in cap_name.lower() else \
                          cap_name.lower().replace(" ", "_")
            priority = RISK_WEIGHTS.get(profile_key, {}).get(status, "MONITOR")
            prioritized[priority].append({
                "capability": cap_name,
                "category": "capability",
                "status": status,
                "priority": priority
            })
    
    # Classify individual findings from lineage
    if lineage:
        for finding in lineage.get("lineage", {}).get("current_findings", []):
            profile = finding.get("profile", "unknown")
            overall = finding.get("overall", "OBSERVATION")
            # Map profile name to risk weight key
            profile_key = "release" if "release" in profile.lower() else \
                          "privacy" if "privacy" in profile.lower() else \
                          "security" if "security" in profile.lower() else \
                          "dependency_risk" if "dependency" in profile.lower() or "risk" in profile.lower() else \
                          "regression" if "reg" in profile.lower() else \
                          "accessibility" if "access" in profile.lower() else \
                          "performance" if "perf" in profile.lower() else \
                          "uat" if "uat" in profile.lower() or "scenario" in profile.lower() else \
                          profile.lower()
            priority = RISK_WEIGHTS.get(profile_key, {}).get(overall, "MONITOR")
            prioritized[priority].append({
                "source": finding.get("evidence_file"),
                "profile": profile,
                "overall": overall,
                "priority": priority
            })
    
    report = {
        "assurance_attention": {
            "generated_at": datetime.now().isoformat(),
            "change_context": context,
            "prioritization": {
                "high_attention": prioritized["HIGH_ATTENTION"],
                "review": prioritized["REVIEW"],
                "monitor": prioritized["MONITOR"]
            },
            "summary": {
                "total_findings": sum(len(v) for v in prioritized.values()),
                "high_attention_count": len(prioritized["HIGH_ATTENTION"]),
                "review_count": len(prioritized["REVIEW"]),
                "monitor_count": len(prioritized["MONITOR"]),
            },
            "authority_level": "advisory",
            "owner_action_required": len(prioritized["HIGH_ATTENTION"]) > 0
        }
    }
    
    print(json.dumps({"assurance_attention": {k: v for k, v in report["assurance_attention"].items() if k != "prioritization" or k and k == "summary"}}, indent=2))
    
    print(f"\nASSURANCE ATTENTION REPORT")
    print(f"{'='*50}")
    print(f"Change: {context['commit']} ({len(context['changed_files'])} files)")
    print(f"{'='*50}")
    
    for priority in ["HIGH_ATTENTION", "REVIEW", "MONITOR"]:
        items = prioritized[priority]
        if items:
            print(f"\n{priority} ({len(items)})")
            print("-" * 30)
            for item in items[:5]:
                cap = item.get("capability") or item.get("profile", "?")
                st = item.get("status") or item.get("overall", "?")
                print(f"  {cap:25s} {st}")
    
    print(f"\nSummary: {report['assurance_attention']['summary']['high_attention_count']} HIGH, {report['assurance_attention']['summary']['review_count']} REVIEW, {report['assurance_attention']['summary']['monitor_count']} MONITOR")

    evidence_path = os.path.join(QA_PILOT_ROOT, "data", "risk-prioritization-evidence.json")
    with open(evidence_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nEvidence written to: {evidence_path}")

if __name__ == "__main__":
    main()
