#!/usr/bin/env python3
"""
Knowledge Findings → Decision Bridge

P7.2-5: Projection layer that creates decision candidates from knowledge findings.

This script:
1. Reads knowledge findings from the knowledge substrate CLI
2. Creates decision candidates in the governance decision queue
3. Preserves finding identity through finding_ref field
4. Writes updated decision queue

Constraints:
- Advisory only (no automatic decisions)
- Owner remains sole decision authority
- Existing governance flows unchanged
- Finding identity preserved
"""

import json
import subprocess
import sys
import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Paths
KNOWLEDGE_CLI = Path.home() / ".librarian/addons/knowledge-substrate/knowledge-substrate-cli"
DECISION_QUEUE = Path("/Users/andrew/Desktop/CarbideFrame/active/librarian/data/decisions/decision-queue.json")


def get_knowledge_findings():
    """Read knowledge findings from the substrate CLI."""
    result = subprocess.run(
        [str(KNOWLEDGE_CLI), "findings"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Error reading findings: {result.stderr}", file=sys.stderr)
        return []
    
    data = json.loads(result.stdout)
    return data.get("findings", [])


def compute_finding_hash(finding):
    """Compute a deterministic hash for a finding.
    
    Uses summary + finding_type for stable hash (finding IDs are regenerated each scan).
    """
    canonical = json.dumps({
        "summary": finding.get("summary"),
        "finding_type": finding.get("finding_type")
    }, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def create_decision_candidate(finding):
    """Create a decision candidate from a knowledge finding."""
    finding_hash = compute_finding_hash(finding)
    
    # Map finding types to decision options
    finding_type = finding.get("finding_type", "unknown")
    if finding_type == "orphan_implementation":
        options = [
            {"action": "address", "description": "Create work order to investigate and resolve orphan"},
            {"action": "dismiss", "description": "Orphan is expected or not actionable"},
            {"action": "defer", "description": "Defer to later review"}
        ]
        recommendation = "Investigate orphan entity for potential lifecycle issue"
    elif finding_type == "unreferenced_artifact":
        options = [
            {"action": "address", "description": "Create work order to link artifact to entities"},
            {"action": "dismiss", "description": "Unreferenced artifact is expected or not actionable"},
            {"action": "defer", "description": "Defer to later review"}
        ]
        recommendation = "Investigate unreferenced artifact for potential governance gap"
    else:
        options = [
            {"action": "address", "description": "Investigate finding"},
            {"action": "dismiss", "description": "Finding is not actionable"},
            {"action": "defer", "description": "Defer to later review"}
        ]
        recommendation = "Review finding for potential governance impact"
    
    return {
        "queue_id": f"finding-{finding_hash}",
        "source": "knowledge_finding",
        "entity": finding.get("artifact_ids", ["unknown"])[0] if finding.get("artifact_ids") else "unknown",
        "context": finding.get("summary", "No summary"),
        "impact": f"Finding type: {finding_type}. Resolution may improve governance coherence.",
        "options": options,
        "recommendation": recommendation,
        "authority": "Owner",
        "severity": "info",
        "decision": {
            "status": "pending",
            "type": "knowledge_finding",
            "finding_ref": {
                "finding_id": finding.get("id"),
                "finding_type": finding_type,
                "finding_status": finding.get("status", "discovered"),
                "knowledge_substrate_snapshot": finding_hash,
                "created_at": finding.get("created_at")
            }
        }
    }


def update_decision_queue(candidates):
    """Update the decision queue with new candidates."""
    # Read existing queue
    with open(DECISION_QUEUE, "r") as f:
        queue = json.load(f)
    
    existing_ids = {item.get("queue_id") for item in queue.get("items", [])}
    
    # Add new candidates (skip duplicates)
    new_count = 0
    for candidate in candidates:
        if candidate["queue_id"] not in existing_ids:
            queue["items"].append(candidate)
            queue["total_items"] = queue.get("total_items", 0) + 1
            queue["pending_items"] = queue.get("pending_items", 0) + 1
            new_count += 1
    
    # Update timestamp
    queue["built_at"] = datetime.now(timezone.utc).isoformat()
    
    # Write updated queue
    with open(DECISION_QUEUE, "w") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)
    
    return new_count


def main():
    print("P7.2-5: Knowledge Findings → Decision Bridge")
    print("=" * 60)
    
    # 1. Read knowledge findings
    print("\n1. Reading knowledge findings...")
    findings = get_knowledge_findings()
    print(f"   Found {len(findings)} findings")
    
    # 2. Create decision candidates
    print("\n2. Creating decision candidates...")
    candidates = [create_decision_candidate(f) for f in findings]
    print(f"   Created {len(candidates)} candidates")
    
    # 3. Update decision queue
    print("\n3. Updating decision queue...")
    new_count = update_decision_queue(candidates)
    print(f"   Added {new_count} new candidates")
    
    # 4. Summary
    print("\n4. Summary:")
    print(f"   Findings processed: {len(findings)}")
    print(f"   Candidates created: {len(candidates)}")
    print(f"   New queue entries: {new_count}")
    
    # 5. Verify
    print("\n5. Verification:")
    with open(DECISION_QUEUE, "r") as f:
        queue = json.load(f)
    print(f"   Total items in queue: {queue['total_items']}")
    print(f"   Pending items: {queue['pending_items']}")
    
    finding_candidates = [i for i in queue["items"] if i.get("source") == "knowledge_finding"]
    print(f"   Knowledge finding candidates: {len(finding_candidates)}")
    
    print("\n" + "=" * 60)
    print("Bridge projection complete. Owner disposition required for each candidate.")


if __name__ == "__main__":
    main()
