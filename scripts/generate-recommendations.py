#!/usr/bin/env python3
"""
Preventive Recommendation Engine

Converts predictive signals into explainable advisory recommendations.

Commands:
  generate <project_id>    Generate recommendations for a project
  generate-all             Generate recommendations for all projects
  list                     List generated recommendations
  explain <id>             Explain a recommendation
  status                   Show recommendation status
"""

import sys
import os
import json
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "assurance"
SIGNALS_DIR = DATA_DIR / "predictive-signals"
RECOMMENDATIONS_DIR = DATA_DIR / "preventive-recommendations"
PATTERNS_DIR = DATA_DIR / "historical-patterns"


def load_json(path):
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def generate_id(prefix):
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    h = hashlib.sha256(f"{prefix}{ts}".encode()).hexdigest()[:8]
    return f"{prefix}-{ts}-{h}"


def get_project_signals(project_id):
    signals = []
    if SIGNALS_DIR.exists():
        for f in SIGNALS_DIR.glob("*.json"):
            signal = load_json(f)
            if signal and signal.get("project_id") == project_id:
                signals.append(signal)
    return signals


def generate_recommendation(signal):
    signal_type = signal.get("signal_type", "unknown")
    confidence = signal.get("confidence", "low")
    
    if signal_type == "no_actionable_signal":
        return {
            "recommendation_id": generate_id("PR"),
            "project_id": signal["project_id"],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "trigger_signal": signal["signal_id"],
            "recommendation_type": "no_recommendation",
            "confidence": confidence,
            "rationale": "Current evidence does not indicate preventive action opportunity.",
            "evidence_refs": signal.get("evidence_refs", []),
            "pattern_refs": signal.get("pattern_refs", []),
            "expiration": None,
            "owner_action_required": False,
            "advisory_only": True
        }
    
    elif signal_type == "evidence_degradation":
        return {
            "recommendation_id": generate_id("PR"),
            "project_id": signal["project_id"],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "trigger_signal": signal["signal_id"],
            "recommendation_type": "evidence_enhancement",
            "confidence": confidence,
            "rationale": "Consider increasing runtime evidence coverage before future capability activation.",
            "evidence_refs": signal.get("evidence_refs", []),
            "pattern_refs": signal.get("pattern_refs", []),
            "expiration": (datetime.now(timezone.utc) + timedelta(days=90)).isoformat(),
            "owner_action_required": False,
            "advisory_only": True
        }
    
    elif signal_type == "emerging_risk":
        return {
            "recommendation_id": generate_id("PR"),
            "project_id": signal["project_id"],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "trigger_signal": signal["signal_id"],
            "recommendation_type": "risk_review",
            "confidence": confidence,
            "rationale": "Risk trajectory suggests increased attention may be warranted.",
            "evidence_refs": signal.get("evidence_refs", []),
            "pattern_refs": signal.get("pattern_refs", []),
            "expiration": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "owner_action_required": False,
            "advisory_only": True
        }
    
    else:
        return {
            "recommendation_id": generate_id("PR"),
            "project_id": signal["project_id"],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "trigger_signal": signal["signal_id"],
            "recommendation_type": "no_recommendation",
            "confidence": "low",
            "rationale": "Insufficient basis for recommendation.",
            "evidence_refs": [],
            "pattern_refs": [],
            "expiration": None,
            "owner_action_required": False,
            "advisory_only": True
        }


def cmd_generate(args):
    if len(args) < 1:
        print("Usage: generate <project_id>")
        sys.exit(1)
    
    project_id = args[0]
    signals = get_project_signals(project_id)
    recommendations = []
    
    for signal in signals:
        rec = generate_recommendation(signal)
        save_json(RECOMMENDATIONS_DIR / f"{rec['recommendation_id']}.json", rec)
        recommendations.append(rec)
    
    print(f"Preventive Recommendations: {project_id}")
    print("=" * 60)
    
    for rec in recommendations:
        print(f"\n  Recommendation: {rec['recommendation_id']}")
        print(f"  Type: {rec['recommendation_type']}")
        print(f"  Confidence: {rec['confidence']}")
        print(f"  Rationale: {rec['rationale']}")
    
    if not recommendations:
        print("\n  No signals found. No recommendations generated.")
    
    print()
    print("  This is advisory guidance, not a requirement.")
    print("  Owner decides action.")


def cmd_generate_all(args):
    if not SIGNALS_DIR.exists():
        print("No signals found.")
        return
    
    all_recs = []
    projects = set()
    
    for f in SIGNALS_DIR.glob("*.json"):
        signal = load_json(f)
        if signal:
            projects.add(signal.get("project_id"))
    
    for project_id in sorted(projects):
        recs = []
        for f in SIGNALS_DIR.glob("*.json"):
            signal = load_json(f)
            if signal and signal.get("project_id") == project_id:
                rec = generate_recommendation(signal)
                save_json(RECOMMENDATIONS_DIR / f"{rec['recommendation_id']}.json", rec)
                recs.append(rec)
                all_recs.append(rec)
        
        print(f"\n  {project_id}:")
        for rec in recs:
            print(f"    [{rec['confidence']}] {rec['recommendation_type']}: {rec['rationale'][:60]}...")
    
    print(f"\n{'='*60}")
    print(f"Total recommendations: {len(all_recs)}")


def cmd_list(args):
    if not RECOMMENDATIONS_DIR.exists():
        print("No recommendations generated yet.")
        return
    
    recs = []
    for f in sorted(RECOMMENDATIONS_DIR.glob("*.json")):
        recs.append(load_json(f))
    
    print(f"Preventive Recommendations ({len(recs)})")
    print("=" * 60)
    
    for r in recs:
        print(f"\n  [{r['confidence'].upper()}] {r['recommendation_id']}")
        print(f"    Project: {r['project_id']}")
        print(f"    Type: {r['recommendation_type']}")
        print(f"    Rationale: {r['rationale'][:60]}...")


def cmd_explain(args):
    if len(args) < 1:
        print("Usage: explain <recommendation_id>")
        sys.exit(1)
    
    rec_id = args[0]
    rec_file = RECOMMENDATIONS_DIR / f"{rec_id}.json"
    
    if not rec_file.exists():
        print(f"Recommendation not found: {rec_id}")
        return
    
    rec = load_json(rec_file)
    
    print(f"Recommendation Explanation: {rec_id}")
    print("=" * 60)
    print(f"  Project: {rec['project_id']}")
    print(f"  Type: {rec['recommendation_type']}")
    print(f"  Confidence: {rec['confidence']}")
    print(f"  Trigger Signal: {rec['trigger_signal']}")
    print()
    print(f"  Rationale: {rec['rationale']}")
    print()
    if rec.get("expiration"):
        print(f"  Expires: {rec['expiration']}")
    print()
    print("  This is advisory guidance, not a requirement.")
    print("  Owner decides action.")


def cmd_status(args):
    recs = list(RECOMMENDATIONS_DIR.glob("*.json")) if RECOMMENDATIONS_DIR.exists() else []
    print("Preventive Recommendation Status")
    print("=" * 60)
    print(f"  Recommendations: {len(recs)}")


COMMANDS = {
    "generate": cmd_generate,
    "generate-all": cmd_generate_all,
    "list": cmd_list,
    "explain": cmd_explain,
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
