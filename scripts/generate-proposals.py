#!/usr/bin/env python3
"""
Improvement Proposal Generator

Bridges preventive recommendations to governed work proposals.

Commands:
  generate <project_id>    Generate proposals for a project
  generate-all             Generate proposals for all projects
  list                     List proposals
  decide <id> <decision>   Record owner decision
  explain <id>             Explain a proposal
  status                   Show proposal status
"""

import sys
import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "assurance"
RECOMMENDATIONS_DIR = DATA_DIR / "preventive-recommendations"
PROPOSALS_DIR = DATA_DIR / "improvement-proposals"
EVIDENCE_STORE = PROJECT_ROOT / "data" / "runtime-evidence"


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


def get_project_recommendations(project_id):
    recs = []
    if RECOMMENDATIONS_DIR.exists():
        for f in RECOMMENDATIONS_DIR.glob("*.json"):
            rec = load_json(f)
            if rec and rec.get("project_id") == project_id and rec.get("recommendation_type") != "no_recommendation":
                recs.append(rec)
    return recs


def get_risk_context(project_id):
    risk_file = EVIDENCE_STORE / "risk-assessments.json"
    if not risk_file.exists():
        return {"current_risk": 0, "risk_band": "unknown"}
    
    try:
        risk_data = load_json(risk_file)
        if "projects" in risk_data:
            for p in risk_data["projects"]:
                if p.get("project_id") == project_id:
                    return {"current_risk": p.get("risk_score", 0), "risk_band": p.get("risk_band", "unknown")}
    except:
        pass
    
    return {"current_risk": 0, "risk_band": "unknown"}


def get_economic_context(project_id):
    economics_dir = DATA_DIR / "economics-reports"
    if not economics_dir.exists():
        return {"attention_score": 0, "attention_level": "unknown"}
    
    for f in economics_dir.glob("*.json"):
        econ = load_json(f)
        if econ and econ.get("project_id") == project_id:
            return {"attention_score": econ.get("attention_score", 0), "attention_level": econ.get("attention_level", "unknown")}
    
    return {"attention_score": 0, "attention_level": "unknown"}


def generate_proposal(recommendation):
    return {
        "proposal_id": generate_id("IP"),
        "project_id": recommendation["project_id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "recommendation_refs": [recommendation["recommendation_id"]],
        "evidence_refs": recommendation.get("evidence_refs", []),
        "risk_context": get_risk_context(recommendation["project_id"]),
        "economic_context": get_economic_context(recommendation["project_id"]),
        "expected_outcome": recommendation.get("rationale", "Improve assurance posture"),
        "status": "pending_owner_review",
        "owner_decision": None,
        "owner_rationale": None,
        "work_packet_id": None,
        "advisory_only": True
    }


def cmd_generate(args):
    if len(args) < 1:
        print("Usage: generate <project_id>")
        sys.exit(1)
    
    project_id = args[0]
    recs = get_project_recommendations(project_id)
    proposals = []
    
    for rec in recs:
        proposal = generate_proposal(rec)
        save_json(PROPOSALS_DIR / f"{proposal['proposal_id']}.json", proposal)
        proposals.append(proposal)
    
    print(f"Improvement Proposals: {project_id}")
    print("=" * 60)
    
    for prop in proposals:
        print(f"\n  Proposal: {prop['proposal_id']}")
        print(f"  Status: {prop['status']}")
        print(f"  Recommendation: {prop['recommendation_refs'][0]}")
        print(f"  Expected: {prop['expected_outcome']}")
        print(f"  Risk: {prop['risk_context']['risk_band']} ({prop['risk_context']['current_risk']})")
    
    if not proposals:
        print("\n  No actionable recommendations. No proposals generated.")
    
    print()
    print("  This is a proposal, not authorization.")
    print("  Owner decides whether to proceed.")


def cmd_generate_all(args):
    if not RECOMMENDATIONS_DIR.exists():
        print("No recommendations found.")
        return
    
    projects = set()
    for f in RECOMMENDATIONS_DIR.glob("*.json"):
        rec = load_json(f)
        if rec and rec.get("recommendation_type") != "no_recommendation":
            projects.add(rec.get("project_id"))
    
    all_proposals = []
    
    for project_id in sorted(projects):
        recs = get_project_recommendations(project_id)
        for rec in recs:
            proposal = generate_proposal(rec)
            save_json(PROPOSALS_DIR / f"{proposal['proposal_id']}.json", proposal)
            all_proposals.append(proposal)
        
        print(f"\n  {project_id}:")
        for prop in [p for p in all_proposals if p["project_id"] == project_id]:
            print(f"    [{prop['status']}] {prop['proposal_id']}: {prop['expected_outcome'][:50]}...")
    
    print(f"\n{'='*60}")
    print(f"Total proposals: {len(all_proposals)}")


def cmd_decide(args):
    if len(args) < 2:
        print("Usage: decide <proposal_id> <accepted|rejected|deferred>")
        sys.exit(1)
    
    proposal_id = args[0]
    decision = args[1]
    
    if decision not in ["accepted", "rejected", "deferred"]:
        print("Decision must be: accepted, rejected, or deferred")
        sys.exit(1)
    
    proposal_file = PROPOSALS_DIR / f"{proposal_id}.json"
    if not proposal_file.exists():
        print(f"Proposal not found: {proposal_id}")
        sys.exit(1)
    
    proposal = load_json(proposal_file)
    proposal["status"] = decision
    proposal["owner_decision"] = decision
    proposal["owner_rationale"] = f"Owner decided: {decision}"
    
    save_json(proposal_file, proposal)
    
    print(f"Owner Decision: {proposal_id}")
    print("=" * 60)
    print(f"  Decision: {decision}")
    print(f"  Status: {proposal['status']}")
    if decision == "accepted":
        print("  Next: Ready for work packet creation")


def cmd_explain(args):
    if len(args) < 1:
        print("Usage: explain <proposal_id>")
        sys.exit(1)
    
    proposal_id = args[0]
    proposal_file = PROPOSALS_DIR / f"{proposal_id}.json"
    
    if not proposal_file.exists():
        print(f"Proposal not found: {proposal_id}")
        return
    
    proposal = load_json(proposal_file)
    
    print(f"Proposal Explanation: {proposal_id}")
    print("=" * 60)
    print(f"  Project: {proposal['project_id']}")
    print(f"  Status: {proposal['status']}")
    print(f"  Recommendations: {', '.join(proposal['recommendation_refs'])}")
    print(f"  Expected: {proposal['expected_outcome']}")
    print(f"  Risk: {proposal['risk_context']['risk_band']} ({proposal['risk_context']['current_risk']})")
    print(f"  Attention: {proposal['economic_context']['attention_level']} ({proposal['economic_context']['attention_score']})")
    if proposal.get("owner_decision"):
        print(f"  Owner Decision: {proposal['owner_decision']}")
    print()
    print("  This is a proposal, not authorization.")
    print("  Owner decides whether to proceed.")


def cmd_list(args):
    if not PROPOSALS_DIR.exists():
        print("No proposals generated yet.")
        return
    
    proposals = []
    for f in sorted(PROPOSALS_DIR.glob("*.json")):
        proposals.append(load_json(f))
    
    print(f"Improvement Proposals ({len(proposals)})")
    print("=" * 60)
    
    for p in proposals:
        print(f"\n  [{p['status']}] {p['proposal_id']}")
        print(f"    Project: {p['project_id']}")
        print(f"    Expected: {p['expected_outcome'][:60]}...")


def cmd_status(args):
    proposals = list(PROPOSALS_DIR.glob("*.json")) if PROPOSALS_DIR.exists() else []
    
    print("Improvement Proposal Status")
    print("=" * 60)
    print(f"  Proposals: {len(proposals)}")


COMMANDS = {
    "generate": cmd_generate,
    "generate-all": cmd_generate_all,
    "decide": cmd_decide,
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
