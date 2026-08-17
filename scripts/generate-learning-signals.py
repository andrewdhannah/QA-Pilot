#!/usr/bin/env python3
"""
Closed-Loop Optimization Engine

Converts improvement outcomes into learning signals.

Commands:
  generate <outcome_id>    Generate learning signal from outcome
  generate-all             Generate signals for all outcomes
  list                     List learning signals
  explain <signal_id>      Explain a signal
  effectiveness            Show recommendation effectiveness
  status                   Show learning status
"""

import sys
import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "assurance"
OUTCOMES_DIR = DATA_DIR / "improvement-outcomes"
SIGNALS_DIR = DATA_DIR / "learning-signals"
RECOMMENDATIONS_DIR = DATA_DIR / "preventive-recommendations"


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


def get_historical_outcomes(project_id, intervention_type):
    count = 0
    if OUTCOMES_DIR.exists():
        for f in OUTCOMES_DIR.glob("*.json"):
            outcome = load_json(f)
            if outcome and outcome.get("project_id") == project_id:
                count += 1
    return count


def compute_learning_confidence(outcome_count):
    if outcome_count <= 1:
        return "observation"
    elif outcome_count <= 4:
        return "emerging_pattern"
    elif outcome_count <= 9:
        return "developing_pattern"
    else:
        return "established_pattern"


def classify_effectiveness(outcome_classification):
    mapping = {
        "improved": "effective",
        "unchanged": "not_effective",
        "degraded": "harmful",
        "inconclusive": "unknown",
        "not_measurable": "measurement_gap"
    }
    return mapping.get(outcome_classification, "unknown")


def generate_learning_signal(outcome):
    outcome_id = outcome["outcome_id"]
    project_id = outcome["project_id"]
    classification = outcome.get("comparison", {}).get("direction", "inconclusive")
    
    historical_count = get_historical_outcomes(project_id, None)
    confidence = compute_learning_confidence(historical_count)
    effectiveness = classify_effectiveness(classification)
    
    learning_content = {
        "improved": f"Intervention produced improvement in {outcome.get('baseline', {}).get('metric', 'unknown')}.",
        "unchanged": f"Intervention produced no observed change in {outcome.get('baseline', {}).get('metric', 'unknown')}.",
        "degraded": f"Intervention may have regressed {outcome.get('baseline', {}).get('metric', 'unknown')}.",
        "inconclusive": f"Insufficient basis to determine effect on {outcome.get('baseline', {}).get('metric', 'unknown')}.",
        "not_measurable": f"Measurement design gap: {outcome.get('baseline', {}).get('metric', 'unknown')} not adequately measured."
    }.get(classification, "Outcome classified.")
    
    return {
        "signal_id": generate_id("LS"),
        "outcome_id": outcome_id,
        "proposal_id": outcome.get("proposal_id"),
        "recommendation_id": outcome.get("provenance_chain", {}).get("recommendation_id"),
        "project_id": project_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "outcome_classification": classification,
        "intervention_type": None,
        "baseline_state": outcome.get("baseline", {}),
        "post_change_state": outcome.get("post_change", {}),
        "measured_delta": outcome.get("comparison", {}).get("delta", ""),
        "confidence": confidence,
        "learning_category": "planning_insight",
        "learning_content": learning_content,
        "effectiveness_signal": effectiveness,
        "measurement_quality": "measurable" if classification != "not_measurable" else "not_measurable",
        "applicable_context": {
            "project_id": project_id,
            "capability": outcome.get("baseline", {}).get("metric"),
            "conditions": "from_outcome_measurement"
        },
        "evidence_refs": [outcome_id],
        "advisory_only": True
    }


def cmd_generate(args):
    if len(args) < 1:
        print("Usage: generate <outcome_id>")
        sys.exit(1)
    
    outcome_id = args[0]
    outcome_file = OUTCOMES_DIR / f"{outcome_id}.json"
    
    if not outcome_file.exists():
        print(f"Outcome not found: {outcome_id}")
        sys.exit(1)
    
    outcome = load_json(outcome_file)
    signal = generate_learning_signal(outcome)
    save_json(SIGNALS_DIR / f"{signal['signal_id']}.json", signal)
    
    print(f"Learning Signal: {signal['signal_id']}")
    print("=" * 60)
    print(f"  Outcome: {signal['outcome_id']}")
    print(f"  Project: {signal['project_id']}")
    print(f"  Classification: {signal['outcome_classification']}")
    print(f"  Effectiveness: {signal['effectiveness_signal']}")
    print(f"  Confidence: {signal['confidence']}")
    print(f"  Learning: {signal['learning_content']}")
    print()
    print("  This is a learning signal, not a policy change.")


def cmd_generate_all(args):
    if not OUTCOMES_DIR.exists():
        print("No outcomes found.")
        return
    
    signals = []
    
    for f in OUTCOMES_DIR.glob("*.json"):
        outcome = load_json(f)
        if outcome:
            signal = generate_learning_signal(outcome)
            save_json(SIGNALS_DIR / f"{signal['signal_id']}.json", signal)
            signals.append(signal)
    
    print(f"Learning Signals Generated: {len(signals)}")
    print("=" * 60)
    
    for signal in signals:
        print(f"\n  [{signal['confidence']}] {signal['signal_id']}")
        print(f"    Outcome: {signal['outcome_classification']}")
        print(f"    Effectiveness: {signal['effectiveness_signal']}")
        print(f"    Learning: {signal['learning_content'][:60]}...")
    
    print()
    print("  These are learning signals, not policy changes.")


def cmd_list(args):
    if not SIGNALS_DIR.exists():
        print("No learning signals yet.")
        return
    
    signals = []
    for f in sorted(SIGNALS_DIR.glob("*.json")):
        signals.append(load_json(f))
    
    print(f"Learning Signals ({len(signals)})")
    print("=" * 60)
    
    for s in signals:
        outcome_class = s.get("outcome_classification", s.get("type", "unknown"))
        effectiveness = s.get("effectiveness_signal", "unknown")
        print(f"\n  [{s.get('confidence', 'unknown')}] {s.get('signal_id', 'unknown')}")
        print(f"    Outcome: {outcome_class}")
        print(f"    Effectiveness: {effectiveness}")


def cmd_explain(args):
    if len(args) < 1:
        print("Usage: explain <signal_id>")
        sys.exit(1)
    
    signal_id = args[0]
    signal_file = SIGNALS_DIR / f"{signal_id}.json"
    
    if not signal_file.exists():
        print(f"Signal not found: {signal_id}")
        return
    
    signal = load_json(signal_file)
    
    print(f"Learning Signal: {signal_id}")
    print("=" * 60)
    print(f"  Project: {signal['project_id']}")
    print(f"  Outcome: {signal['outcome_classification']}")
    print(f"  Effectiveness: {signal['effectiveness_signal']}")
    print(f"  Confidence: {signal['confidence']}")
    print(f"  Category: {signal['learning_category']}")
    print()
    print(f"  Learning: {signal['learning_content']}")
    print()
    print(f"  Delta: {signal['measured_delta']}")
    print()
    print("  This is a learning signal, not a policy change.")


def cmd_effectiveness(args):
    if not SIGNALS_DIR.exists():
        print("No learning signals yet.")
        return
    
    signals = []
    for f in SIGNALS_DIR.glob("*.json"):
        signals.append(load_json(f))
    
    effectiveness_counts = {}
    for s in signals:
        eff = s.get("effectiveness_signal", "unknown")
        effectiveness_counts[eff] = effectiveness_counts.get(eff, 0) + 1
    
    print("Recommendation Effectiveness")
    print("=" * 60)
    for eff, count in sorted(effectiveness_counts.items()):
        print(f"  {eff}: {count}")
    
    print(f"\n  Total signals: {len(signals)}")


def cmd_status(args):
    signals = list(SIGNALS_DIR.glob("*.json")) if SIGNALS_DIR.exists() else []
    
    print("Closed-Loop Optimization Status")
    print("=" * 60)
    print(f"  Learning signals: {len(signals)}")


COMMANDS = {
    "generate": cmd_generate,
    "generate-all": cmd_generate_all,
    "list": cmd_list,
    "explain": cmd_explain,
    "effectiveness": cmd_effectiveness,
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
