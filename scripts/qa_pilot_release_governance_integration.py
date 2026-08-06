"""
qa_pilot_release_governance_integration.py — Release Governance Integration

Connects assurance evidence to the release governance lifecycle.
"""

import json, os, subprocess
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
QA_PILOT_ROOT = os.path.dirname(PROJECT_ROOT)

def load_evidence(rel_path):
    path = os.path.join(QA_PILOT_ROOT, rel_path)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def main():
    context = {"commit": "unknown", "author": "unknown"}
    try:
        c = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=QA_PILOT_ROOT)
        a = subprocess.run(["git", "log", "-1", "--format=%an"], capture_output=True, text=True, cwd=QA_PILOT_ROOT)
        context = {"commit": c.stdout.strip() if c.returncode == 0 else "unknown", "author": a.stdout.strip() if a.returncode == 0 else "unknown"}
    except:
        pass
    
    release = load_evidence("data/release-readiness-evidence.json")
    risk = load_evidence("data/risk-prioritization-evidence.json")
    history = load_evidence("data/assurance-history.json")
    
    decision_package = {
        "release_governance": {
            "generated_at": datetime.now().isoformat(),
            "release_candidate": {
                "commit": context["commit"],
                "author": context["author"],
            },
            "assurance": {
                "release_readiness": release.get("assurance_report", {}).get("summary", {}).get("overall", "unknown") if release else "not available",
                "risk_high_attention": risk.get("assurance_attention", {}).get("prioritization", {}).get("high_attention", []) if risk else [],
                "history_records": len(history.get("assurance_history", [])) if history else 0,
            },
            "evidence_package": {
                "release_readiness": "data/release-readiness-evidence.json",
                "risk_prioritization": "data/risk-prioritization-evidence.json",
                "assurance_history": "data/assurance-history.json",
                "privacy": "data/privacy-assurance-evidence.json",
                "dependency_risk": "data/dependency-risk-evidence.json",
                "security": "data/security-assurance-evidence.json",
                "accessibility": "data/accessibility-evidence.json",
                "performance": "data/performance-baseline.json",
            },
            "owner_decision": {
                "required": True,
                "surface": "OWNER_DECISION_REQUIRED findings present — review HIGH ATTENTION items before release",
                "receipt_reference": None,
            },
            "authority_level": "advisory"
        }
    }
    
    print(json.dumps(decision_package, indent=2))
    print(f"\nRelease governance package created for commit {context['commit']}")
    print(f"Assurance: {decision_package['release_governance']['assurance']['release_readiness']}")
    print(f"Evidence files: {len(decision_package['release_governance']['evidence_package'])}")
    print(f"Owner decision required: {decision_package['release_governance']['owner_decision']['required']}")

    evidence_path = os.path.join(QA_PILOT_ROOT, "data", "release-governance-evidence.json")
    with open(evidence_path, "w") as f:
        json.dump(decision_package, f, indent=2)
    print(f"Evidence written to: {evidence_path}")

if __name__ == "__main__":
    main()
