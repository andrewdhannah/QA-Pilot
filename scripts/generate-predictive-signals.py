#!/usr/bin/env python3
"""
Predictive Risk Signal Engine — QA-PILOT-PREDICTIVE-RISK-SIGNALS-1

Generates forward-looking risk indicators from current state and patterns.

Commands:
  generate <project_id>    Generate signals for a project
  generate-all             Generate signals for all projects
  list                     List generated signals
  explain <signal_id>      Explain a signal
  status                   Show signal status
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
SIGNALS_DIR = DATA_DIR / "predictive-signals"
PATTERNS_DIR = DATA_DIR / "historical-patterns"
TRENDS_DIR = DATA_DIR / "trend-records"


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


def get_current_risk(project_id):
    """Get current risk for a project."""
    risk_file = EVIDENCE_STORE / "risk-assessments.json"
    if not risk_file.exists():
        return 50, "unknown"
    
    try:
        risk_data = load_json(risk_file)
        if "projects" in risk_data:
            for p in risk_data["projects"]:
                if p.get("project_id") == project_id:
                    return p.get("risk_score", 50), p.get("risk_band", "unknown")
    except:
        pass
    
    return 50, "unknown"


def get_risk_trajectory(project_id):
    """Get risk trajectory from trends."""
    if not TRENDS_DIR.exists():
        return "unknown", "low"
    
    risk_trends = []
    for f in TRENDS_DIR.glob("*.json"):
        trend = load_json(f)
        if trend and trend.get("project_id") == project_id and trend.get("metric") == "risk_score":
            risk_trends.append(trend)
    
    if not risk_trends:
        return "unknown", "low"
    
    # Check latest trend
    latest = risk_trends[-1]
    direction = latest.get("direction", "unknown")
    confidence = latest.get("confidence", "low")
    
    return direction, confidence


def get_pattern_evidence(project_id):
    """Get pattern evidence for a project."""
    if not PATTERNS_DIR.exists():
        return [], "insufficient"
    
    patterns = []
    for f in PATTERNS_DIR.glob("*.json"):
        pattern = load_json(f)
        if pattern:
            patterns.append(pattern)
    
    if not patterns:
        return [], "insufficient"
    
    # Check pattern confidence
    high_confidence = sum(1 for p in patterns if p.get("confidence") == "high")
    medium_confidence = sum(1 for p in patterns if p.get("confidence") == "medium")
    
    if high_confidence > 0:
        confidence = "high"
    elif medium_confidence > 0:
        confidence = "medium"
    elif len(patterns) > 0:
        confidence = "low"
    else:
        confidence = "insufficient"
    
    return patterns, confidence


def generate_signals(project_id):
    """Generate predictive signals for a project."""
    signals = []
    
    # Get inputs
    current_risk, risk_band = get_current_risk(project_id)
    trajectory, trajectory_confidence = get_risk_trajectory(project_id)
    patterns, pattern_confidence = get_pattern_evidence(project_id)
    
    # Signal 1: Emerging risk (if trajectory increasing)
    if trajectory == "degrading" or (trajectory == "unknown" and current_risk > 50):
        confidence = "low" if pattern_confidence == "insufficient" else pattern_confidence
        
        signals.append({
            "signal_id": generate_id("PRS"),
            "project_id": project_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "signal_type": "emerging_risk",
            "current_risk": current_risk,
            "projected_condition": "increased_attention_possible",
            "time_horizon": "30_days",
            "confidence": confidence,
            "basis": [
                f"current_risk_{risk_band}",
                f"trajectory_{trajectory}",
                f"pattern_confidence_{pattern_confidence}"
            ],
            "pattern_refs": [p.get("pattern_id") for p in patterns[:3]],
            "evidence_refs": [],
            "advisory_only": True
        })
    
    # Signal 2: Evidence degradation (if coverage low)
    # Check evidence freshness
    project_dir = PROJECTS_DIR / project_id
    if project_dir.exists():
        records = list((project_dir / "records").glob("*.json")) if (project_dir / "records").exists() else []
        if len(records) == 0:
            confidence = "low" if pattern_confidence == "insufficient" else pattern_confidence
            
            signals.append({
                "signal_id": generate_id("PRS"),
                "project_id": project_id,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "signal_type": "evidence_degradation",
                "current_risk": current_risk,
                "projected_condition": "evidence_coverage_may_decline",
                "time_horizon": "60_days",
                "confidence": confidence,
                "basis": [
                    "no_runtime_evidence",
                    f"pattern_confidence_{pattern_confidence}"
                ],
                "pattern_refs": [p.get("pattern_id") for p in patterns[:3]],
                "evidence_refs": [],
                "advisory_only": True
            })
    
    # If no signals generated, create a "no signal" record
    if not signals:
        signals.append({
            "signal_id": generate_id("PRS"),
            "project_id": project_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "signal_type": "no_actionable_signal",
            "current_risk": current_risk,
            "projected_condition": "stable",
            "time_horizon": "30_days",
            "confidence": "low",
            "basis": [
                f"current_risk_{risk_band}",
                f"trajectory_{trajectory}",
                "insufficient_pattern_data"
            ],
            "pattern_refs": [],
            "evidence_refs": [],
            "advisory_only": True
        })
    
    return signals


def cmd_generate(args):
    """Generate signals for a project."""
    if len(args) < 1:
        print("Usage: generate <project_id>")
        sys.exit(1)
    
    project_id = args[0]
    signals = generate_signals(project_id)
    
    # Save signals
    for signal in signals:
        save_json(SIGNALS_DIR / f"{signal['signal_id']}.json", signal)
    
    print(f"Predictive Risk Signals: {project_id}")
    print("=" * 60)
    
    for signal in signals:
        print(f"\n  Signal: {signal['signal_id']}")
        print(f"  Type: {signal['signal_type']}")
        print(f"  Current Risk: {signal['current_risk']}")
        print(f"  Projected: {signal['projected_condition']}")
        print(f"  Horizon: {signal['time_horizon']}")
        print(f"  Confidence: {signal['confidence']}")
        print(f"  Basis: {', '.join(signal['basis'])}")
    
    print()
    print("  This is a predictive signal, not a finding.")
    print("  Owner decides action.")


def cmd_generate_all(args):
    """Generate signals for all projects."""
    if not PROJECTS_DIR.exists():
        print("No projects found.")
        return
    
    all_signals = []
    
    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if project_dir.is_dir():
            signals = generate_signals(project_dir.name)
            for signal in signals:
                save_json(SIGNALS_DIR / f"{signal['signal_id']}.json", signal)
            all_signals.extend(signals)
            
            print(f"\n  {project_dir.name}:")
            for signal in signals:
                print(f"    [{signal['confidence']}] {signal['signal_type']}: {signal['projected_condition']}")
    
    print(f"\n{'='*60}")
    print(f"Total signals: {len(all_signals)}")


def cmd_list(args):
    """List generated signals."""
    if not SIGNALS_DIR.exists():
        print("No signals generated yet.")
        return
    
    signals = []
    for f in sorted(SIGNALS_DIR.glob("*.json")):
        signals.append(load_json(f))
    
    print(f"Predictive Risk Signals ({len(signals)})")
    print("=" * 60)
    
    for s in signals:
        print(f"\n  [{s['confidence'].upper()}] {s['signal_id']}")
        print(f"    Project: {s['project_id']}")
        print(f"    Type: {s['signal_type']}")
        print(f"    Projected: {s['projected_condition']}")


def cmd_explain(args):
    """Explain a signal."""
    if len(args) < 1:
        print("Usage: explain <signal_id>")
        sys.exit(1)
    
    signal_id = args[0]
    signal_file = SIGNALS_DIR / f"{signal_id}.json"
    
    if not signal_file.exists():
        print(f"Signal not found: {signal_id}")
        return
    
    signal = load_json(signal_file)
    
    print(f"Signal Explanation: {signal_id}")
    print("=" * 60)
    print(f"  Project: {signal['project_id']}")
    print(f"  Type: {signal['signal_type']}")
    print(f"  Current Risk: {signal['current_risk']}")
    print(f"  Projected: {signal['projected_condition']}")
    print(f"  Horizon: {signal['time_horizon']}")
    print(f"  Confidence: {signal['confidence']}")
    print()
    print("  Basis:")
    for basis in signal["basis"]:
        print(f"    - {basis}")
    print()
    print("  This is a predictive signal, not a finding.")
    print("  Association does not imply causation.")
    print("  Owner decides action.")


def cmd_status(args):
    """Show signal status."""
    signals = list(SIGNALS_DIR.glob("*.json")) if SIGNALS_DIR.exists() else []
    
    print("Predictive Risk Signal Status")
    print("=" * 60)
    print(f"  Signals: {len(signals)}")


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
