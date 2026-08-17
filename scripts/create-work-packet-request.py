#!/usr/bin/env python3
"""
Work Packet Request Handoff Adapter

Translates accepted improvement proposals to work packet requests.

Commands:
  create <proposal_id>    Create request from accepted proposal
  create-all              Create requests for all accepted proposals
  list                    List work packet requests
  explain <request_id>    Explain a request
  status                  Show handoff status
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


def get_accepted_proposals():
    proposals = []
    if PROPOSALS_DIR.exists():
        for f in PROPOSALS_DIR.glob("*.json"):
            prop = load_json(f)
            if prop and prop.get("status") == "accepted":
                proposals.append(prop)
    return proposals


def create_request(proposal):
    return {
        "request_id": generate_id("WPR"),
        "proposal_id": proposal["proposal_id"],
        "project_id": proposal["project_id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "recommendation_refs": proposal.get("recommendation_refs", []),
        "evidence_refs": proposal.get("evidence_refs", []),
        "risk_context": proposal.get("risk_context", {}),
        "owner_decision_id": proposal.get("owner_decision", "accepted"),
        "requested_scope": "evidence_enhancement",
        "expected_outcome": proposal.get("expected_outcome", ""),
        "status": "submitted",
        "work_packet_id": None,
        "advisory_only": True
    }


def cmd_create(args):
    if len(args) < 1:
        print("Usage: create <proposal_id>")
        sys.exit(1)
    
    proposal_id = args[0]
    proposal_file = PROPOSALS_DIR / f"{proposal_id}.json"
    
    if not proposal_file.exists():
        print(f"Proposal not found: {proposal_id}")
        sys.exit(1)
    
    proposal = load_json(proposal_file)
    
    if proposal.get("status") != "accepted":
        print(f"ERROR: Proposal {proposal_id} is not accepted (status: {proposal.get('status')})")
        print("Only accepted proposals can create work packet requests.")
        sys.exit(1)
    
    request = create_request(proposal)
    save_json(REQUESTS_DIR / f"{request['request_id']}.json", request)
    
    print(f"Work Packet Request Created: {request['request_id']}")
    print("=" * 60)
    print(f"  Proposal: {request['proposal_id']}")
    print(f"  Project: {request['project_id']}")
    print(f"  Scope: {request['requested_scope']}")
    print(f"  Status: {request['status']}")
    print()
    print("  This is a request, not authorization.")
    print("  Librarian processes work packet creation.")


def cmd_create_all(args):
    proposals = get_accepted_proposals()
    
    if not proposals:
        print("No accepted proposals found.")
        return
    
    requests = []
    
    for proposal in proposals:
        request = create_request(proposal)
        save_json(REQUESTS_DIR / f"{request['request_id']}.json", request)
        requests.append(request)
    
    print(f"Work Packet Requests Created: {len(requests)}")
    print("=" * 60)
    
    for req in requests:
        print(f"\n  {req['request_id']}: {req['project_id']}")
        print(f"    Scope: {req['requested_scope']}")
        print(f"    Proposal: {req['proposal_id']}")
    
    print()
    print("  These are requests, not authorizations.")
    print("  Librarian processes work packet creation.")


def cmd_list(args):
    if not REQUESTS_DIR.exists():
        print("No work packet requests yet.")
        return
    
    requests = []
    for f in sorted(REQUESTS_DIR.glob("*.json")):
        requests.append(load_json(f))
    
    print(f"Work Packet Requests ({len(requests)})")
    print("=" * 60)
    
    for r in requests:
        print(f"\n  [{r['status']}] {r['request_id']}")
        print(f"    Project: {r['project_id']}")
        print(f"    Scope: {r['requested_scope']}")
        print(f"    Proposal: {r['proposal_id']}")


def cmd_explain(args):
    if len(args) < 1:
        print("Usage: explain <request_id>")
        sys.exit(1)
    
    request_id = args[0]
    request_file = REQUESTS_DIR / f"{request_id}.json"
    
    if not request_file.exists():
        print(f"Request not found: {request_id}")
        return
    
    request = load_json(request_file)
    
    print(f"Work Packet Request: {request_id}")
    print("=" * 60)
    print(f"  Project: {request['project_id']}")
    print(f"  Status: {request['status']}")
    print(f"  Proposal: {request['proposal_id']}")
    print(f"  Scope: {request['requested_scope']}")
    print(f"  Expected: {request['expected_outcome']}")
    print(f"  Owner Decision: {request['owner_decision_id']}")
    print()
    print("  This is a request, not authorization.")
    print("  Librarian processes work packet creation.")


def cmd_status(args):
    requests = list(REQUESTS_DIR.glob("*.json")) if REQUESTS_DIR.exists() else []
    
    print("Work Packet Integration Status")
    print("=" * 60)
    print(f"  Requests: {len(requests)}")


COMMANDS = {
    "create": cmd_create,
    "create-all": cmd_create_all,
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
