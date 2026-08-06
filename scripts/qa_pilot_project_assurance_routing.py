#!/usr/bin/env python3
"""
qa_pilot_project_assurance_routing.py — Multi-Project Assurance Routing

Routes assurance state from multiple projects into a common operational view
without creating duplicate authority, lifecycle, or evidence domains.

Invariant: Multiple projects, one assurance language, separate sources of truth.
"""

import json
import os
import sys
from datetime import datetime, timezone

QA_PILOT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(QA_PILOT_ROOT, "data")


def load_json(path):
    if path and os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
    return None


def detect_project_type(project_root):
    """Detect which scanner adapter to use based on project file layout."""
    data_dir = os.path.join(project_root, "data")
    # QA Pilot has data/finding-lifecycle.json
    if os.path.exists(os.path.join(data_dir, "finding-lifecycle.json")):
        return "qa-pilot"
    # Librarian has project-state/sprint-ledger.json but no data/finding-lifecycle
    if os.path.exists(os.path.join(project_root, "project-state", "sprint-ledger.json")):
        return "librarian"
    return "unknown"


def scan_librarian_assurance(project_root, project_id=None):
    """Librarian adapter: load assurance state from Librarian's project layout.
    
    Librarian has:
      - startup-contract.json for identity
      - project-state/sprint-ledger.json for sprint history
      - receipts/ for evidence
      - docs/governance/ for governance docs
      - No finding lifecycle, evidence pipeline, or continuous loop
    """
    if not project_id:
        project_id = os.path.basename(os.path.normpath(project_root))
    
    # Project identity from startup contract
    identity_path = os.path.join(project_root, "startup-contract.json")
    identity = load_json(identity_path)
    
    # Sprint ledger
    sprint_ledger_path = os.path.join(project_root, "project-state", "sprint-ledger.json")
    sprint_ledger = load_json(sprint_ledger_path)
    
    # Sprint history
    total_sprints = 0
    sealed_sprints = 0
    latest_sprint_id = "none"
    if sprint_ledger:
        sprints = sprint_ledger.get("sprints", [])
        total_sprints = len(sprints)
        sealed_sprints = sum(1 for s in sprints if s.get("status") == "sealed")
        if sprints:
            latest = sprints[-1]
            latest_sprint_id = f"#{latest.get('sealed_number', '?')} {latest['id']}"
    
    # Evidence freshness from receipts directory (git timestamps)
    receipts_dir = os.path.join(project_root, "receipts")
    evidence_files = []
    if os.path.exists(receipts_dir):
        for fname in os.listdir(receipts_dir):
            fpath = os.path.join(receipts_dir, fname)
            if os.path.isfile(fpath) and not fname.startswith("."):
                age_min = int((datetime.now().timestamp() - os.path.getmtime(fpath)) / 60)
                evidence_files.append({
                    "file": fname,
                    "age_minutes": age_min,
                    "state": "stale" if age_min > 60 else "fresh"
                })
    
    # Governance docs
    gov_dir = os.path.join(project_root, "docs", "governance")
    gov_files = 0
    if os.path.exists(gov_dir):
        gov_files = len([f for f in os.listdir(gov_dir) if f.endswith(".md")])
    
    return {
        "project_id": project_id,
        "project_root": project_root,
        "adapter": "librarian",
        "status": "available",
        "assurance": {
            "findings": {
                "total": 0,
                "by_state": {"NO_FINDING_LIFECYCLE": total_sprints},
                "unacknowledged": 0,
                "note": "Librarian does not use finding lifecycle — sprint history shown as proxy"
            },
            "risk": {
                "total": 0,
                "priority_counts": {},
                "note": "Librarian has no risk prioritization model"
            },
            "registry": {
                "layers": total_sprints,
                "max_slot": latest_sprint_id,
                "note": "Librarian sprint ledger used as layer proxy"
            },
            "evidence_freshness": {
                "total_files": len(evidence_files),
                "fresh": sum(1 for f in evidence_files if f["state"] == "fresh"),
                "stale": sum(1 for f in evidence_files if f["state"] == "stale"),
                "evidence_files": evidence_files[:5],
                "source": "receipts/ directory timestamps"
            },
            "owner_queue": {
                "pending": 0,
                "total": sealed_sprints,
                "note": "Librarian embeds Owner decisions in seal records"
            },
            "readiness": {
                "status": "available" if os.path.exists(os.path.join(project_root, "RELEASE-GATE.md")) else "no_data",
                "note": "release-gate.md" if os.path.exists(os.path.join(project_root, "RELEASE-GATE.md")) else "no release gate found"
            }
        }
    }


def scan_project_assurance(project_root, project_id=None):
    """Detect project type and dispatch to the correct adapter."""
    ptype = detect_project_type(project_root)
    
    if ptype == "librarian":
        return scan_librarian_assurance(project_root, project_id)
    if ptype != "qa-pilot":
        return None
    
    data_dir = os.path.join(project_root, "data")
    if not os.path.exists(data_dir):
        return None
    if not project_id:
        project_id = os.path.basename(project_root)
    
    # Load finding lifecycle
    finding_store = os.path.join(data_dir, "finding-lifecycle.json")
    findings = load_json(finding_store)
    
    # Load evidence lineage
    evidence_lineage = os.path.join(data_dir, "evidence-lineage.json")
    evidence = load_json(evidence_lineage)
    
    # Load risk prioritization
    risk_store = os.path.join(data_dir, "risk-prioritization-evidence.json")
    risk = load_json(risk_store)
    
    # Load release readiness
    readiness_store = os.path.join(data_dir, "release-readiness-evidence.json")
    readiness = load_json(readiness_store)
    
    # Load registry
    registry_path = os.path.join(data_dir, "pipeline-layer-registry", "registry.json")
    registry = load_json(registry_path)
    
    # Load owner decisions
    decision_index = os.path.join(data_dir, "owner-decisions", "decision-index.json")
    decisions = load_json(decision_index)
    
    # Compute evidence freshness from store or fallback to lineage
    freshness = None
    if evidence:
        freshness = evidence.get("lineage", {}).get("evidence_freshness")
        if not freshness:
            freshness = evidence.get("evidence_freshness")
    
    # Count findings by state
    all_findings = findings.get("findings", []) if findings else []
    by_state = {}
    for f in all_findings:
        state = f.get("state", "UNKNOWN")
        by_state[state] = by_state.get(state, 0) + 1
    
    # Count risk priorities
    priority_counts = {}
    total_risk = 0
    if risk:
        attention = risk.get("assurance_attention", {}).get("prioritization", {})
        for priority in risk.get("priority_order", ["high_attention", "review", "monitor"]):
            items = attention.get(priority, [])
            priority_counts[priority] = len(items)
            total_risk += len(items)
    
    return {
        "project_id": project_id,
        "project_root": project_root,
        "status": "available",
        "assurance": {
            "findings": {
                "total": len(all_findings),
                "by_state": by_state,
                "unacknowledged": sum(1 for f in all_findings if not f.get("acknowledged", False))
            },
            "risk": {
                "total": total_risk,
                "priority_counts": priority_counts
            },
            "registry": {
                "layers": len(registry.get("layers", [])) if registry else 0,
                "max_slot": max((l["slot"] for l in registry["layers"]), default=0) if registry else 0
            },
            "evidence_freshness": {
                "total_files": len(freshness.get("all_evidence", [])) if freshness else 0,
                "fresh": sum(1 for e in freshness.get("all_evidence", []) if e.get("age_minutes", 999) <= 60) if freshness else 0,
                "stale": sum(1 for e in freshness.get("all_evidence", []) if e.get("age_minutes", 999) > 60) if freshness else 0
            } if freshness else {"total_files": 0, "fresh": 0, "stale": 0},
            "owner_queue": {
                "pending": sum(1 for d in (decisions.get("decisions", []) if decisions else []) if d.get("status") == "pending"),
                "total": len(decisions.get("decisions", [])) if decisions else 0
            },
            "readiness": {
                "status": readiness.get("overall", {}).get("status", "unknown") if readiness else "no_data"
            }
        }
    }


def route_projects(project_paths):
    """Load and route assurance state from multiple projects.
    
    Returns a structured routing view with per-project state and
    cross-project comparison data.
    """
    projects = []
    for path in project_paths:
        pid = os.path.basename(os.path.normpath(path))
        state = scan_project_assurance(path, project_id=pid)
        if state:
            projects.append(state)
    
    # Build cross-project comparison
    cross_project = {
        "total_projects": len(projects),
        "total_findings": sum(p["assurance"]["findings"]["total"] for p in projects),
        "total_risk_items": sum(p["assurance"]["risk"]["total"] for p in projects),
        "total_evidence_files": sum(p["assurance"]["evidence_freshness"]["total_files"] for p in projects),
        "total_owner_decisions": sum(p["assurance"]["owner_queue"]["total"] for p in projects),
        "projects_with_readiness": sum(1 for p in projects if p["assurance"]["readiness"]["status"] != "no_data"),
    }
    
    return {
        "routing_id": f"R-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "invariant": "Multiple projects, one assurance language, separate sources of truth.",
        "cross_project": cross_project,
        "projects": {p["project_id"]: p["assurance"] for p in projects}
    }


def format_routing_report(routing):
    """Render routing state as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("QA Pilot — Multi-Project Assurance Routing")
    lines.append(f"Generated: {routing['generated_at']}")
    lines.append(f"Invariant: {routing['invariant']}")
    lines.append("=" * 60)
    lines.append("")
    
    cp = routing["cross_project"]
    lines.append(f"── Cross-Project Summary ──")
    lines.append(f"  Projects: {cp['total_projects']}")
    lines.append(f"  Total findings: {cp['total_findings']}")
    lines.append(f"  Total risk items: {cp['total_risk_items']}")
    lines.append(f"  Total evidence files: {cp['total_evidence_files']}")
    lines.append(f"  Total owner decisions: {cp['total_owner_decisions']}")
    lines.append(f"  Projects with readiness data: {cp['projects_with_readiness']}")
    lines.append("")
    
    for pid, state in routing.get("projects", {}).items():
        lines.append(f"── Project: {pid} ──")
        f = state["findings"]
        lines.append(f"  Findings: {f['total']} ({f['unacknowledged']} unacknowledged)")
        if f.get("by_state"):
            for s, c in sorted(f["by_state"].items()):
                lines.append(f"    {s}: {c}")
        r = state["risk"]
        lines.append(f"  Risk items: {r['total']}")
        for p, c in r.get("priority_counts", {}).items():
            lines.append(f"    {p}: {c}")
        reg = state["registry"]
        lines.append(f"  Registry: {reg['layers']} layers (max slot {reg['max_slot']})")
        ef = state["evidence_freshness"]
        lines.append(f"  Evidence: {ef['total_files']} files ({ef['fresh']} fresh, {ef['stale']} stale)")
        oq = state["owner_queue"]
        lines.append(f"  Owner queue: {oq['pending']} pending / {oq['total']} total")
        rd = state["readiness"]
        lines.append(f"  Release readiness: {rd['status']}")
        lines.append("")
    
    lines.append("=" * 60)
    lines.append("End of Routing Report — project boundaries preserved")
    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="QA Pilot Multi-Project Assurance Routing")
    parser.add_argument("mode", nargs="?", default="report",
                        choices=["report", "status", "validate"],
                        help="Output mode")
    parser.add_argument("--projects", nargs="*", default=[],
                        help="Project root paths to route (default: QA Pilot only)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    # Default: route QA Pilot itself
    project_paths = args.projects if args.projects else [QA_PILOT_ROOT]
    
    routing = route_projects(project_paths)
    
    if args.json or args.mode == "status":
        print(json.dumps(routing, indent=2))
    elif args.mode == "validate":
        checks = {
            "routing_produced": len(routing.get("projects", {})) > 0,
            "cross_project_summary": routing.get("cross_project", {}).get("total_projects", 0) > 0,
            "project_identity_preserved": all(
                k in routing.get("projects", {}) for k in
                [os.path.basename(p) for p in project_paths]
            ) if project_paths else True,
            "invariant_present": "Multiple projects" in routing.get("invariant", ""),
        }
        print(json.dumps({"validator": "PAR-ROUTING", "checks": checks, "all_pass": all(checks.values())}, indent=2))
    else:
        print(format_routing_report(routing))


if __name__ == "__main__":
    main()
