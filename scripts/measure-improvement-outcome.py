#!/usr/bin/env python3
"""
Improvement Outcome Measurement Engine

Measures whether interventions improved the condition that caused the recommendation.

Commands:
  measure <proposal_id>    Measure outcome for a proposal
  measure-all              Measure outcomes for all completed proposals
  list                     List outcome measurements
  explain <outcome_id>     Explain an outcome
  status                   Show outcome status
"""

import sys
import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "assurance"
PROPOSALS_DIR = DATA_DIR / "improvement-proposals"
REQUESTS_DIR = DATA_DIR / "work-packet-requests"
OUTCOMES_DIR = DATA_DIR / "improvement-outcomes"
EVIDENCE_STORE = PROJECT_ROOT / "data" / "runtime-evidence"
PROJECTS_DIR = EVIDENCE_STORE / "projects"


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


def get_completed_proposals():
    proposals = []
    if PROPOSALS_DIR.exists():
        for f in PROPOSALS_DIR.glob("*.json"):
            prop = load_json(f)
            if prop and prop.get("status") in ["accepted", "converted"]:
                proposals.append(prop)
    return proposals


def get_baseline(project_id):
    project_dir = PROJECTS_DIR / project_id
    if not project_dir.exists():
        return {"metric": "evidence_coverage", "value": "unknown", "evidence_ref": "none"}
    
    records = list((project_dir / "records").glob("*.json")) if (project_dir / "records").exists() else []
    
    if len(records) == 0:
        return {"metric": "evidence_coverage", "value": "none", "evidence_ref": "none", "captured_at": datetime.now(timezone.utc).isoformat()}
    elif len(records) < 3:
        return {"metric": "evidence_coverage", "value": "minimal", "evidence_ref": records[0].stem, "captured_at": datetime.now(timezone.utc).isoformat()}
    else:
        return {"metric": "evidence_coverage", "value": "partial", "evidence_ref": records[0].stem, "captured_at": datetime.now(timezone.utc).isoformat()}


def get_post_change(project_id):
    project_dir = PROJECTS_DIR / project_id
    if not project_dir.exists():
        return {"metric": "evidence_coverage", "value": "unknown", "evidence_ref": "none"}
    
    records = list((project_dir / "records").glob("*.json")) if (project_dir / "records").exists() else []
    
    if len(records) == 0:
        return {"metric": "evidence_coverage", "value": "none", "evidence_ref": "none", "captured_at": datetime.now(timezone.utc).isoformat()}
    elif len(records) < 3:
        return {"metric": "evidence_coverage", "value": "minimal", "evidence_ref": records[-1].stem, "captured_at": datetime.now(timezone.utc).isoformat()}
    else:
        return {"metric": "evidence_coverage", "value": "partial", "evidence_ref": records[-1].stem, "captured_at": datetime.now(timezone.utc).isoformat()}


def compare_outcomes(baseline, post_change):
    coverage_order = {"none": 0, "minimal": 1, "partial": 2, "full": 3, "unknown": -1}
    
    base_val = coverage_order.get(baseline.get("value", "unknown"), -1)
    post_val = coverage_order.get(post_change.get("value", "unknown"), -1)
    
    if base_val == -1 or post_val == -1:
        return {"direction": "inconclusive", "confidence": "low", "delta": f"{baseline.get('value')} → {post_change.get('value')}"}
    
    if post_val > base_val:
        return {"direction": "improved", "confidence": "medium", "delta": f"{baseline.get('value')} → {post_change.get('value')}"}
    elif post_val < base_val:
        return {"direction": "degraded", "confidence": "medium", "delta": f"{baseline.get('value')} → {post_change.get('value')}"}
    else:
        return {"direction": "unchanged", "confidence": "medium", "delta": f"{baseline.get('value')} → {post_change.get('value')}"}


def measure_outcome(proposal):
    baseline = get_baseline(proposal["project_id"])
    post_change = get_post_change(proposal["project_id"])
    comparison = compare_outcomes(baseline, post_change)
    
    return {
        "outcome_id": generate_id("IO"),
        "proposal_id": proposal["proposal_id"],
        "work_packet_id": proposal.get("work_packet_id"),
        "project_id": proposal["project_id"],
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "baseline": baseline,
        "post_change": post_change,
        "comparison": comparison,
        "measurement_criteria": f"Evidence coverage changed from {baseline.get('value')} to {post_change.get('value')}",
        "provenance_chain": {
            "recommendation_id": proposal.get("recommendation_refs", [None])[0],
            "proposal_id": proposal["proposal_id"],
            "owner_decision": proposal.get("owner_decision"),
            "work_packet_id": proposal.get("work_packet_id")
        },
        "advisory_only": True
    }


def cmd_measure(args):
    if len(args) < 1:
        print("Usage: measure <proposal_id>")
        sys.exit(1)
    
    proposal_id = args[0]
    proposal_file = PROPOSALS_DIR / f"{proposal_id}.json"
    
    if not proposal_file.exists():
        print(f"Proposal not found: {proposal_id}")
        sys.exit(1)
    
    proposal = load_json(proposal_file)
    outcome = measure_outcome(proposal)
    save_json(OUTCOMES_DIR / f"{outcome['outcome_id']}.json", outcome)
    
    print(f"Improvement Outcome: {outcome['outcome_id']}")
    print("=" * 60)
    print(f"  Proposal: {outcome['proposal_id']}")
    print(f"  Project: {outcome['project_id']}")
    print(f"  Direction: {outcome['comparison']['direction']}")
    print(f"  Confidence: {outcome['comparison']['confidence']}")
    print(f"  Delta: {outcome['comparison']['delta']}")
    print(f"  Criteria: {outcome['measurement_criteria']}")
    print()
    print("  This is a measurement, not a judgment.")
    print("  Outcome does not imply approval or closure.")


def cmd_measure_all(args):
    proposals = get_completed_proposals()
    
    if not proposals:
        print("No completed proposals found.")
        return
    
    outcomes = []
    
    for proposal in proposals:
        outcome = measure_outcome(proposal)
        save_json(OUTCOMES_DIR / f"{outcome['outcome_id']}.json", outcome)
        outcomes.append(outcome)
    
    print(f"Improvement Outcomes Measured: {len(outcomes)}")
    print("=" * 60)
    
    for outcome in outcomes:
        print(f"\n  [{outcome['comparison']['direction']}] {outcome['outcome_id']}")
        print(f"    Project: {outcome['project_id']}")
        print(f"    Delta: {outcome['comparison']['delta']}")
        print(f"    Confidence: {outcome['comparison']['confidence']}")
    
    print()
    print("  These are measurements, not judgments.")


def cmd_list(args):
    if not OUTCOMES_DIR.exists():
        print("No outcomes measured yet.")
        return
    
    outcomes = []
    for f in sorted(OUTCOMES_DIR.glob("*.json")):
        outcomes.append(load_json(f))
    
    print(f"Improvement Outcomes ({len(outcomes)})")
    print("=" * 60)
    
    for o in outcomes:
        print(f"\n  [{o['comparison']['direction']}] {o['outcome_id']}")
        print(f"    Project: {o['project_id']}")
        print(f"    Delta: {o['comparison']['delta']}")


def cmd_explain(args):
    if len(args) < 1:
        print("Usage: explain <outcome_id>")
        sys.exit(1)
    
    outcome_id = args[0]
    outcome_file = OUTCOMES_DIR / f"{outcome_id}.json"
    
    if not outcome_file.exists():
        print(f"Outcome not found: {outcome_id}")
        return
    
    outcome = load_json(outcome_file)
    
    print(f"Outcome Explanation: {outcome_id}")
    print("=" * 60)
    print(f"  Project: {outcome['project_id']}")
    print(f"  Direction: {outcome['comparison']['direction']}")
    print(f"  Confidence: {outcome['comparison']['confidence']}")
    print(f"  Delta: {outcome['comparison']['delta']}")
    print()
    print("  Baseline:")
    print(f"    Metric: {outcome['baseline']['metric']}")
    print(f"    Value: {outcome['baseline']['value']}")
    print("  Post-Change:")
    print(f"    Metric: {outcome['post_change']['metric']}")
    print(f"    Value: {outcome['post_change']['value']}")
    print()
    print(f"  Criteria: {outcome['measurement_criteria']}")
    print()
    print("  This is a measurement, not a judgment.")
    print("  Outcome does not imply approval or closure.")


def cmd_status(args):
    outcomes = list(OUTCOMES_DIR.glob("*.json")) if OUTCOMES_DIR.exists() else []
    
    print("Improvement Outcome Status")
    print("=" * 60)
    print(f"  Outcomes: {len(outcomes)}")


COMMANDS = {
    "measure": cmd_measure,
    "measure-all": cmd_measure_all,
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
