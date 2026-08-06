"""
qa_pilot_assurance_history_recorder.py — Assurance History Recorder

Append-only assurance history recording the chain from repository change
through evidence generation, classification, risk context, and Owner decision.
"""

import json, os, subprocess
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
QA_PILOT_ROOT = os.path.dirname(PROJECT_ROOT)
HISTORY_PATH = os.path.join(QA_PILOT_ROOT, "data", "assurance-history.json")

def get_change_context():
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=QA_PILOT_ROOT)
        diff = subprocess.run(["git", "diff", "--name-only", "HEAD~1"], capture_output=True, text=True, cwd=QA_PILOT_ROOT)
        author = subprocess.run(["git", "log", "-1", "--format=%an"], capture_output=True, text=True, cwd=QA_PILOT_ROOT)
        return {
            "commit": commit.stdout.strip() if commit.returncode == 0 else "unknown",
            "author": author.stdout.strip() if author.returncode == 0 else "unknown",
            "changed_files": [f.strip() for f in diff.stdout.split("\n") if f.strip()] if diff.returncode == 0 else []
        }
    except:
        return {"commit": "unknown", "author": "unknown", "changed_files": []}

def load_json(rel_path):
    path = os.path.join(QA_PILOT_ROOT, rel_path)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def load_existing_history():
    """Load existing history file (append-only)."""
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH) as f:
            return json.load(f)
    return {"assurance_history": [], "metadata": {"created": datetime.now().isoformat(), "version": "1.0", "append_only": True}}

def main():
    context = get_change_context()
    lineage = load_json("data/evidence-lineage.json")
    risk = load_json("data/risk-prioritization-evidence.json")
    release = load_json("data/release-readiness-evidence.json")
    
    # Build this history record
    record = {
        "sequence": None,
        "commit": context["commit"],
        "author": context["author"],
        "timestamp": datetime.now().isoformat(),
        "changed_files": context["changed_files"][:20],
        "evidence": {
            "evidence_lineage": bool(lineage),
            "risk_prioritization": bool(risk),
            "release_readiness": bool(release),
        },
        "findings": [],
        "risk_classification": {
            "high_attention": 0,
            "review": 0,
            "monitor": 0,
        },
        "release_state": "",
        "owner_decision_references": [],
    }
    
    # Extract findings from risk prioritization
    if risk:
        attention = risk.get("assurance_attention", {}).get("prioritization", {})
        record["risk_classification"]["high_attention"] = len(attention.get("high_attention", []))
        record["risk_classification"]["review"] = len(attention.get("review", []))
        record["risk_classification"]["monitor"] = len(attention.get("monitor", []))
        for item in attention.get("high_attention", []) + attention.get("review", [])[:3]:
            record["findings"].append({
                "source": item.get("source") or item.get("capability", "unknown"),
                "status": item.get("status") or item.get("overall", "unknown"),
                "priority": item.get("priority", "MONITOR")
            })
    
    if release:
        record["release_state"] = release.get("assurance_report", {}).get("summary", {}).get("overall", "unknown")
    
    if lineage:
        record["findings_summary"] = lineage.get("lineage", {}).get("findings_summary", {})
    
    # Load existing history and append
    history = load_existing_history()
    record["sequence"] = len(history["assurance_history"]) + 1
    history["assurance_history"].append(record)
    history["metadata"]["last_updated"] = datetime.now().isoformat()
    
    # Write append-only
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)
    
    print(f"\nASSURANCE HISTORY RECORDER")
    print("=" * 50)
    print(f"Record #{record['sequence']}")
    print(f"Commit: {record['commit']} by {record['author']}")
    print(f"Files changed: {len(context['changed_files'])}")
    print(f"Risk: {record['risk_classification']['high_attention']} HIGH, {record['risk_classification']['review']} REVIEW, {record['risk_classification']['monitor']} MONITOR")
    print(f"Release state: {record['release_state']}")
    print(f"Total history records: {len(history['assurance_history'])}")
    print(f"Mode: append-only")
    print(f"History stored at: {HISTORY_PATH}")

if __name__ == "__main__":
    main()
