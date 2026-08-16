#!/usr/bin/env python3
"""
Planning Accuracy Measurement Engine — QA-PILOT-PLANNING-ACCURACY-MEASUREMENT-1

Measures whether assurance context improves planning decisions.

Commands:
  record-intent       Record a planning intent
  record-outcome      Record an execution outcome
  analyze             Analyze variance for a planning intent
  signals             Show learning signals
  history             Show measurement history
  status              Show measurement status
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
INTENTS_DIR = DATA_DIR / "planning-intents"
OUTCOMES_DIR = DATA_DIR / "execution-outcomes"
VARIANCES_DIR = DATA_DIR / "variance-analyses"
SIGNALS_DIR = DATA_DIR / "learning-signals"
HISTORY_FILE = DATA_DIR / "measurement-history.json"


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


def load_history():
    """Load measurement history."""
    history = load_json(HISTORY_FILE)
    if history is None:
        return {"intents": 0, "outcomes": 0, "variances": 0, "signals": 0}
    return history


def save_history(history):
    """Save measurement history."""
    save_json(HISTORY_FILE, history)


def cmd_record_intent(args):
    """Record a planning intent."""
    if len(args) < 2:
        print("Usage: record-intent <project_id> <complexity> <effort_days> <risk_level>")
        print("Example: record-intent librarian low 3 low")
        sys.exit(1)
    
    project_id = args[0]
    complexity = args[1]
    effort_days = int(args[2])
    risk_level = args[3]
    
    intent_id = generate_id("PI")
    
    intent = {
        "intent_id": intent_id,
        "project_id": project_id,
        "planned_at": datetime.now(timezone.utc).isoformat(),
        "planning_context": {
            "assurance_state": "operational",
            "risk_band": "monitor",
            "coverage": "partial",
            "freshness": "current"
        },
        "estimates": {
            "complexity": complexity,
            "effort_days": effort_days,
            "risk_level": risk_level,
            "expected_findings": 0
        },
        "decision_rationale": "Recorded for planning accuracy measurement",
        "advisory_only": True
    }
    
    # Save intent
    save_json(INTENTS_DIR / f"{intent_id}.json", intent)
    
    # Update history
    history = load_history()
    history["intents"] += 1
    save_history(history)
    
    print(f"Planning Intent Recorded: {intent_id}")
    print(f"  Project: {project_id}")
    print(f"  Complexity: {complexity}")
    print(f"  Effort: {effort_days} days")
    print(f"  Risk: {risk_level}")


def cmd_record_outcome(args):
    """Record an execution outcome."""
    if len(args) < 4:
        print("Usage: record-outcome <intent_id> <complexity> <effort_days> <findings>")
        print("Example: record-outcome PI-001 medium 5 2")
        sys.exit(1)
    
    intent_id = args[0]
    complexity = args[1]
    effort_days = int(args[2])
    findings = int(args[3])
    
    # Verify intent exists
    intent_file = INTENTS_DIR / f"{intent_id}.json"
    if not intent_file.exists():
        print(f"ERROR: Intent not found: {intent_id}")
        sys.exit(1)
    
    outcome_id = generate_id("EO")
    
    outcome = {
        "outcome_id": outcome_id,
        "intent_id": intent_id,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "actual": {
            "complexity": complexity,
            "effort_days": effort_days,
            "findings": findings,
            "severity_breakdown": {
                "critical": 0,
                "high": 0,
                "medium": findings if findings > 0 else 0,
                "low": 0
            }
        },
        "assurance_impact": {
            "qualification_findings": 0,
            "risk_band_changed": False,
            "evidence_gaps_discovered": []
        },
        "advisory_only": True
    }
    
    # Save outcome
    save_json(OUTCOMES_DIR / f"{outcome_id}.json", outcome)
    
    # Update history
    history = load_history()
    history["outcomes"] += 1
    save_history(history)
    
    print(f"Execution Outcome Recorded: {outcome_id}")
    print(f"  Intent: {intent_id}")
    print(f"  Complexity: {complexity}")
    print(f"  Effort: {effort_days} days")
    print(f"  Findings: {findings}")


def analyze_variance(intent_id):
    """Analyze variance for a planning intent."""
    # Load intent
    intent_file = INTENTS_DIR / f"{intent_id}.json"
    if not intent_file.exists():
        return None, f"Intent not found: {intent_id}"
    
    intent = load_json(intent_file)
    
    # Find matching outcome
    outcome = None
    if OUTCOMES_DIR.exists():
        for f in OUTCOMES_DIR.glob("*.json"):
            o = load_json(f)
            if o.get("intent_id") == intent_id:
                outcome = o
                break
    
    if not outcome:
        return None, f"No outcome found for intent: {intent_id}"
    
    # Compute variance
    estimates = intent["estimates"]
    actual = outcome["actual"]
    
    # Effort variance
    effort_estimated = estimates["effort_days"]
    effort_actual = actual["effort_days"]
    effort_variance_pct = ((effort_actual - effort_estimated) / effort_estimated * 100) if effort_estimated > 0 else 0
    effort_direction = "over" if effort_actual > effort_estimated else ("under" if effort_actual < effort_estimated else "exact")
    
    # Findings variance
    expected_findings = estimates.get("expected_findings", 0)
    actual_findings = actual["findings"]
    findings_variance = actual_findings - expected_findings
    findings_direction = "more_than_expected" if findings_variance > 0 else ("less_than_expected" if findings_variance < 0 else "as_expected")
    
    # Complexity variance
    complexity_map = {"low": 1, "medium": 2, "high": 3, "very_high": 4}
    planned_complexity = complexity_map.get(estimates["complexity"], 1)
    actual_complexity = complexity_map.get(actual["complexity"], 1)
    complexity_direction = "underestimated" if actual_complexity > planned_complexity else ("overestimated" if actual_complexity < planned_complexity else "accurate")
    
    # Determine learning signal
    learning_signal = None
    if abs(effort_variance_pct) > 50:
        learning_signal = {
            "type": "planning_gap",
            "description": f"Effort variance: {effort_variance_pct:.1f}%",
            "recommendation": "Review estimation approach for similar work",
            "confidence": "medium"
        }
    elif findings_variance > 0:
        learning_signal = {
            "type": "coverage_gap",
            "description": f"Unexpected findings: {findings_variance}",
            "recommendation": "Consider expanding evidence coverage",
            "confidence": "medium"
        }
    elif actual_complexity > planned_complexity:
        learning_signal = {
            "type": "planning_gap",
            "description": f"Complexity underestimated: {estimates['complexity']} → {actual['complexity']}",
            "recommendation": "Review complexity assessment criteria",
            "confidence": "low"
        }
    else:
        learning_signal = {
            "type": "assurance_benefit",
            "description": "Planning estimates were accurate",
            "recommendation": "Continue current planning approach",
            "confidence": "high"
        }
    
    variance = {
        "variance_id": generate_id("VA"),
        "intent_id": intent_id,
        "outcome_id": outcome["outcome_id"],
        "project_id": intent["project_id"],
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "variance": {
            "effort": {
                "estimated": effort_estimated,
                "actual": effort_actual,
                "variance_pct": round(effort_variance_pct, 1),
                "direction": effort_direction
            },
            "findings": {
                "expected": expected_findings,
                "actual": actual_findings,
                "variance": findings_variance,
                "direction": findings_direction
            },
            "complexity": {
                "planned": estimates["complexity"],
                "actual": actual["complexity"],
                "direction": complexity_direction
            }
        },
        "root_cause": learning_signal["description"],
        "learning_signal": learning_signal,
        "advisory_only": True
    }
    
    return variance, None


def cmd_analyze(args):
    """Analyze variance for a planning intent."""
    if len(args) < 1:
        print("Usage: analyze <intent_id>")
        sys.exit(1)
    
    intent_id = args[0]
    variance, error = analyze_variance(intent_id)
    
    if error:
        print(f"ERROR: {error}")
        sys.exit(1)
    
    # Save variance
    save_json(VARIANCES_DIR / f"{variance['variance_id']}.json", variance)
    
    # Save learning signal
    signal = variance["learning_signal"]
    signal_record = {
        "signal_id": generate_id("LS"),
        "variance_id": variance["variance_id"],
        "intent_id": intent_id,
        "project_id": variance["project_id"],
        "type": signal["type"],
        "description": signal["description"],
        "recommendation": signal["recommendation"],
        "confidence": signal["confidence"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "advisory_only": True
    }
    save_json(SIGNALS_DIR / f"{signal_record['signal_id']}.json", signal_record)
    
    # Update history
    history = load_history()
    history["variances"] += 1
    history["signals"] += 1
    save_history(history)
    
    print(f"Variance Analysis: {variance['variance_id']}")
    print()
    print("Effort Variance:")
    print(f"  Estimated: {variance['variance']['effort']['estimated']} days")
    print(f"  Actual:    {variance['variance']['effort']['actual']} days")
    print(f"  Variance:  {variance['variance']['effort']['variance_pct']}% ({variance['variance']['effort']['direction']})")
    print()
    print("Findings Variance:")
    print(f"  Expected:  {variance['variance']['findings']['expected']}")
    print(f"  Actual:    {variance['variance']['findings']['actual']}")
    print(f"  Variance:  {variance['variance']['findings']['variance']}")
    print()
    print("Learning Signal:")
    print(f"  Type: {signal['type']}")
    print(f"  {signal['description']}")
    print(f"  Recommendation: {signal['recommendation']}")


def cmd_signals(args):
    """Show learning signals."""
    if not SIGNALS_DIR.exists():
        print("No learning signals yet.")
        return
    
    signals = []
    for f in sorted(SIGNALS_DIR.glob("*.json")):
        signals.append(load_json(f))
    
    print(f"Learning Signals ({len(signals)})")
    print("=" * 60)
    
    for s in signals[-10:]:  # Show last 10
        print(f"\n  [{s['type']}] {s['signal_id']}")
        print(f"    Project: {s['project_id']}")
        print(f"    {s['description']}")
        print(f"    Recommendation: {s['recommendation']}")
        print(f"    Confidence: {s['confidence']}")


def cmd_history(args):
    """Show measurement history."""
    history = load_history()
    
    print("Measurement History")
    print("=" * 60)
    print(f"Planning Intents:    {history['intents']}")
    print(f"Execution Outcomes:  {history['outcomes']}")
    print(f"Variance Analyses:   {history['variances']}")
    print(f"Learning Signals:    {history['signals']}")


def cmd_status(args):
    """Show measurement status."""
    history = load_history()
    
    # Count files
    intents_count = len(list(INTENTS_DIR.glob("*.json"))) if INTENTS_DIR.exists() else 0
    outcomes_count = len(list(OUTCOMES_DIR.glob("*.json"))) if OUTCOMES_DIR.exists() else 0
    variances_count = len(list(VARIANCES_DIR.glob("*.json"))) if VARIANCES_DIR.exists() else 0
    signals_count = len(list(SIGNALS_DIR.glob("*.json"))) if SIGNALS_DIR.exists() else 0
    
    print("Planning Accuracy Measurement Status")
    print("=" * 60)
    print(f"Intents:    {intents_count}")
    print(f"Outcomes:   {outcomes_count}")
    print(f"Variances:  {variances_count}")
    print(f"Signals:    {signals_count}")
    print()
    
    # Check for unanalyzed intents
    analyzed_intents = set()
    if VARIANCES_DIR.exists():
        for f in VARIANCES_DIR.glob("*.json"):
            v = load_json(f)
            analyzed_intents.add(v.get("intent_id"))
    
    unanalyzed = []
    if INTENTS_DIR.exists():
        for f in INTENTS_DIR.glob("*.json"):
            intent = load_json(f)
            if intent["intent_id"] not in analyzed_intents:
                unanalyzed.append(intent["intent_id"])
    
    if unanalyzed:
        print(f"Unanalyzed intents: {len(unanalyzed)}")
        for iid in unanalyzed:
            print(f"  - {iid}")
    else:
        print("All intents analyzed.")


COMMANDS = {
    "record-intent": cmd_record_intent,
    "record-outcome": cmd_record_outcome,
    "analyze": cmd_analyze,
    "signals": cmd_signals,
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
