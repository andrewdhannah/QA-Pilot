"""
qa_pilot_finding_lifecycle.py — Finding Lifecycle Implementation

Persists finding states, surfaces Owner acknowledgment queue,
extends lineage with lifecycle events, integrates with history recorder.
"""

import json, os
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
QA_PILOT_ROOT = os.path.dirname(PROJECT_ROOT)
FINDING_STORE = os.path.join(QA_PILOT_ROOT, "data", "finding-lifecycle.json")
HISTORY_PATH = os.path.join(QA_PILOT_ROOT, "data", "assurance-history.json")

def load_json(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def load_findings():
    if os.path.exists(FINDING_STORE):
        with open(FINDING_STORE) as f:
            return json.load(f)
    return {"findings": [], "metadata": {"created": datetime.now().isoformat(), "version": "1.0"}}

def import_from_risk():
    """Import existing risk-prioritized findings into lifecycle store."""
    risk = load_json(os.path.join(QA_PILOT_ROOT, "data", "risk-prioritization-evidence.json"))
    if not risk:
        return []
    
    findings_store = load_findings()
    existing_ids = {f["id"] for f in findings_store["findings"]}
    new_findings = []
    
    attention = risk.get("assurance_attention", {}).get("prioritization", {})
    for priority in ["high_attention", "review", "monitor"]:
        items = attention.get(priority, [])
        for item in items:
            fid = f"FLD-{item.get('capability', item.get('profile', 'unknown'))}-{datetime.now().strftime('%H%M%S')}"
            if fid not in existing_ids:
                f = {
                    "id": fid,
                    "source": item.get("evidence_file") or item.get("source", "unknown"),
                    "capability": item.get("capability", item.get("profile", "unknown")),
                    "risk": priority.upper(),
                    "state": "OPEN",
                    "acknowledged": False,
                    "created_at": datetime.now().isoformat(),
                    "state_history": [{"state": "OPEN", "timestamp": datetime.now().isoformat(), "trigger": "assurance_run"}],
                    "owner_actions": [],
                    "resolution_evidence": None,
                }
                findings_store["findings"].append(f)
                new_findings.append(f)
    
    findings_store["metadata"]["last_updated"] = datetime.now().isoformat()
    with open(FINDING_STORE, "w") as f:
        json.dump(findings_store, f, indent=2)
    return new_findings

def build_owner_queue(findings_store):
    """Build Owner acknowledgment queue from findings."""
    queue = {"high_attention": [], "review": [], "monitor": []}
    for f in findings_store["findings"]:
        entry = {
            "id": f["id"],
            "source": f["source"],
            "state": f["state"],
            "acknowledged": f["acknowledged"],
            "age_hours": round((datetime.now() - datetime.fromisoformat(f["created_at"])).total_seconds() / 3600, 1),
        }
        risk = f.get("risk", "MONITOR")
        if risk == "HIGH_ATTENTION":
            queue["high_attention"].append(entry)
        elif risk == "REVIEW":
            queue["review"].append(entry)
        else:
            queue["monitor"].append(entry)
    return queue

def extend_history(findings_store):
    """Extend assurance history with finding lifecycle states."""
    history = load_json(HISTORY_PATH)
    if history and "assurance_history" in history and history["assurance_history"]:
        latest = history["assurance_history"][-1]
        latest["finding_lifecycle"] = {
            "total_findings": len(findings_store["findings"]),
            "by_state": {},
            "unacknowledged_high": 0,
        }
        state_counts = {}
        for f in findings_store["findings"]:
            s = f["state"]
            state_counts[s] = state_counts.get(s, 0) + 1
            if s == "OPEN" and f.get("risk") == "HIGH_ATTENTION" and not f["acknowledged"]:
                latest["finding_lifecycle"]["unacknowledged_high"] += 1
        latest["finding_lifecycle"]["by_state"] = state_counts
        with open(HISTORY_PATH, "w") as f:
            json.dump(history, f, indent=2)

def main():
    new = import_from_risk()
    store = load_findings()
    queue = build_owner_queue(store)
    extend_history(store)
    
    evidence = {
        "artifact": {"identity": f"FLC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"},
        "intent": "Finding lifecycle implementation — state storage, Owner queue, lineage extension, history integration",
        "classification": "assurance",
        "execution_method": "lifecycle_management",
        "findings": {
            "new_findings_imported": len(new),
            "total_findings": len(store["findings"]),
            "state_distribution": {},
            "owner_queue": {
                "high_attention_pending": len(queue["high_attention"]),
                "review_pending": len(queue["review"]),
                "monitor": len(queue["monitor"]),
            },
        },
        "authority_level": "advisory"
    }
    
    state_dist = {}
    for f in store["findings"]:
        st = f["state"]
        state_dist[st] = state_dist.get(st, 0) + 1
    evidence["findings"]["state_distribution"] = state_dist
    
    print(json.dumps(evidence, indent=2))
    print(f"\nFinding lifecycle: {len(store['findings'])} total, {len(new)} new")
    print(f"Owner queue: {queue['high_attention']} HIGH, {len(queue['review'])} REVIEW, {len(queue['monitor'])} MONITOR")
    print(f"States: {state_dist}")

    ev_path = os.path.join(QA_PILOT_ROOT, "data", "finding-lifecycle-evidence.json")
    with open(ev_path, "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"Evidence written to: {ev_path}")
    print(f"Finding store at: {FINDING_STORE}")

if __name__ == "__main__":
    main()
