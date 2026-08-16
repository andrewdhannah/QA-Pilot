#!/usr/bin/env python3
"""
Capability Discovery Engine — QA-PILOT-CAPABILITY-DISCOVERY-1

Detects missing, incomplete, or inconsistent governance capabilities.

Commands:
  discover <project_id>    Discover capabilities for a project
  discover-all             Discover capabilities for all projects
  status                   Show discovery status
  history                  Show discovery history
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
ONBOARDING_DIR = DATA_DIR / "onboarding-records"
DISCOVERIES_DIR = DATA_DIR / "capability-discoveries"
HISTORY_FILE = DATA_DIR / "discovery-history.json"

# CAG requirements
CAG_REQUIREMENTS = [
    "declaration",
    "discoverability",
    "authority",
    "validation",
    "projection"
]

# Capability types to check
CAPABILITY_TYPES = [
    "runtime_assurance",
    "qualification",
    "risk_assessment",
    "planning_integration",
    "continuous_qualification",
    "adaptive_qualification",
    "project_onboarding"
]


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


def get_declared_capabilities(project_id):
    """Get declared capabilities for a project."""
    # Check onboarding record
    if ONBOARDING_DIR.exists():
        for f in ONBOARDING_DIR.glob("*.json"):
            record = load_json(f)
            if record and record.get("project_id") == project_id:
                # Extract capabilities from onboarding
                capabilities = []
                evidence_domains = record.get("evidence_sources", {}).get("domains", [])
                for domain in evidence_domains:
                    capabilities.append({
                        "capability": f"{domain}_assurance",
                        "status": "active",
                        "source": "onboarding"
                    })
                return capabilities
    
    return []


def get_observed_evidence(project_id):
    """Get observed evidence for a project."""
    project_dir = PROJECTS_DIR / project_id
    
    if not project_dir.exists():
        return {"total": 0, "domains": {}, "last_ingested": None}
    
    evidence = {"total": 0, "domains": {}, "last_ingested": None}
    
    for evidence_dir in [project_dir / "records", project_dir / "snapshots"]:
        if evidence_dir.exists():
            for f in evidence_dir.glob("*.json"):
                record = load_json(f)
                if record:
                    evidence["total"] += 1
                    domain = record.get("context", {}).get("execution_context", {}).get("event_type", "unknown")
                    evidence["domains"][domain] = evidence["domains"].get(domain, 0) + 1
                    
                    captured_at = record.get("freshness", {}).get("captured_at")
                    if captured_at:
                        if evidence["last_ingested"] is None or captured_at > evidence["last_ingested"]:
                            evidence["last_ingested"] = captured_at
    
    return evidence


def get_qualification_history(project_id):
    """Get qualification history for a project."""
    history_file = EVIDENCE_STORE / "qualification-history.json"
    if not history_file.exists():
        return {"total_runs": 0, "last_run": None, "findings": 0}
    
    try:
        history = load_json(history_file)
        finding_count = sum(1 for r in history.get("runs", []) if r.get("result", {}).get("disposition") == "FINDING")
        return {
            "total_runs": history.get("total_runs", 0),
            "last_run": history.get("last_run_id"),
            "findings": finding_count
        }
    except:
        return {"total_runs": 0, "last_run": None, "findings": 0}


def check_cag_compliance(project_id, capability):
    """Check CAG compliance for a capability."""
    findings = []
    
    # Check declaration
    if not capability.get("capability"):
        findings.append({
            "requirement": "declaration",
            "status": "missing",
            "description": "Capability not declared"
        })
    
    # Check discoverability (simplified - would check projection in real system)
    # For now, assume discoverable if capability exists
    
    # Check authority
    if not capability.get("authority_scope"):
        findings.append({
            "requirement": "authority",
            "status": "missing",
            "description": "Authority boundaries not declared"
        })
    
    # Check validation
    if not capability.get("validator"):
        findings.append({
            "requirement": "validation",
            "status": "missing",
            "description": "No validator defined"
        })
    
    # Check projection
    if not capability.get("in_projection"):
        findings.append({
            "requirement": "projection",
            "status": "missing",
            "description": "Not visible in startup projection"
        })
    
    return findings


def discover_project(project_id):
    """Discover capabilities for a project."""
    discovery_id = generate_id("CDR")
    
    # Gather data
    declared = get_declared_capabilities(project_id)
    evidence = get_observed_evidence(project_id)
    history = get_qualification_history(project_id)
    
    findings = []
    
    # Check for coverage gaps
    for cap in declared:
        cap_name = cap["capability"]
        
        # Check if evidence exists for this capability
        has_evidence = False
        for domain in evidence["domains"]:
            if domain in cap_name or cap_name in domain:
                has_evidence = True
                break
        
        if not has_evidence:
            findings.append({
                "finding_id": generate_id("CDF"),
                "project_id": project_id,
                "finding_type": "coverage_gap",
                "capability": cap_name,
                "description": f"Capability '{cap_name}' declared but no matching evidence found",
                "severity": "medium",
                "evidence_refs": [],
                "recommendation": f"Consider generating evidence for '{cap_name}' or removing declaration",
                "discovered_at": datetime.now(timezone.utc).isoformat(),
                "advisory_only": True
            })
    
    # Check for stale capabilities
    if evidence["last_ingested"]:
        try:
            last_ingested = datetime.fromisoformat(evidence["last_ingested"].replace("Z", "+00:00"))
            age_days = (datetime.now(timezone.utc) - last_ingested).days
            
            if age_days > 30:
                findings.append({
                    "finding_id": generate_id("CDF"),
                    "project_id": project_id,
                    "finding_type": "stale_capability",
                    "capability": "evidence_freshness",
                    "description": f"Last evidence ingested {age_days} days ago",
                    "severity": "low",
                    "evidence_refs": [],
                    "recommendation": "Consider refreshing evidence",
                    "discovered_at": datetime.now(timezone.utc).isoformat(),
                    "advisory_only": True
                })
        except:
            pass
    
    # Check for evidence gaps
    if history["total_runs"] == 0:
        findings.append({
            "finding_id": generate_id("CDF"),
            "project_id": project_id,
            "finding_type": "evidence_gap",
            "capability": "qualification",
            "description": "No qualification runs performed",
            "severity": "medium",
            "evidence_refs": [],
            "recommendation": "Consider running qualification",
            "discovered_at": datetime.now(timezone.utc).isoformat(),
            "advisory_only": True
        })
    
    # Build discovery record
    discovery = {
        "discovery_id": discovery_id,
        "project_id": project_id,
        "discovered_at": datetime.now(timezone.utc).isoformat(),
        "declared_capabilities": len(declared),
        "observed_evidence": evidence["total"],
        "qualification_runs": history["total_runs"],
        "findings": findings,
        "summary": {
            "total_findings": len(findings),
            "by_type": {},
            "by_severity": {}
        },
        "advisory_only": True
    }
    
    # Compute summary
    for f in findings:
        ftype = f["finding_type"]
        severity = f["severity"]
        discovery["summary"]["by_type"][ftype] = discovery["summary"]["by_type"].get(ftype, 0) + 1
        discovery["summary"]["by_severity"][severity] = discovery["summary"]["by_severity"].get(severity, 0) + 1
    
    return discovery


def cmd_discover(args):
    """Discover capabilities for a project."""
    if len(args) < 1:
        print("Usage: discover <project_id>")
        sys.exit(1)
    
    project_id = args[0]
    
    discovery = discover_project(project_id)
    
    # Save discovery
    save_json(DISCOVERIES_DIR / f"{discovery['discovery_id']}.json", discovery)
    
    # Update history
    history = load_json(HISTORY_FILE) or {"discoveries": 0, "findings": 0}
    history["discoveries"] += 1
    history["findings"] += discovery["summary"]["total_findings"]
    history["last_discovery"] = discovery["discovery_id"]
    save_json(HISTORY_FILE, history)
    
    print(f"Capability Discovery: {discovery['discovery_id']}")
    print("=" * 60)
    print(f"  Project: {project_id}")
    print(f"  Declared capabilities: {discovery['declared_capabilities']}")
    print(f"  Observed evidence: {discovery['observed_evidence']}")
    print(f"  Qualification runs: {discovery['qualification_runs']}")
    print()
    
    if discovery["findings"]:
        print(f"  Findings ({discovery['summary']['total_findings']}):")
        for f in discovery["findings"]:
            print(f"    [{f['severity'].upper()}] {f['finding_type']}: {f['description']}")
            print(f"      Recommendation: {f['recommendation']}")
    else:
        print("  No findings.")


def cmd_discover_all(args):
    """Discover capabilities for all projects."""
    if not PROJECTS_DIR.exists():
        print("No projects found.")
        return
    
    all_findings = []
    
    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if project_dir.is_dir():
            print(f"\nDiscovering: {project_dir.name}")
            discovery = discover_project(project_dir.name)
            
            # Save discovery
            save_json(DISCOVERIES_DIR / f"{discovery['discovery_id']}.json", discovery)
            
            all_findings.extend(discovery["findings"])
            
            if discovery["findings"]:
                for f in discovery["findings"]:
                    print(f"  [{f['severity'].upper()}] {f['finding_type']}: {f['description']}")
            else:
                print("  No findings.")
    
    print(f"\n{'='*60}")
    print(f"Total findings: {len(all_findings)}")


def cmd_status(args):
    """Show discovery status."""
    discoveries = list(DISCOVERIES_DIR.glob("*.json")) if DISCOVERIES_DIR.exists() else []
    history = load_json(HISTORY_FILE) or {"discoveries": 0, "findings": 0}
    
    print("Capability Discovery Status")
    print("=" * 60)
    print(f"Discoveries: {len(discoveries)}")
    print(f"Total findings: {history.get('findings', 0)}")
    print(f"Last discovery: {history.get('last_discovery', 'none')}")


def cmd_history(args):
    """Show discovery history."""
    if not DISCOVERIES_DIR.exists():
        print("No discovery history yet.")
        return
    
    discoveries = []
    for f in sorted(DISCOVERIES_DIR.glob("*.json")):
        discoveries.append(load_json(f))
    
    print(f"Discovery History ({len(discoveries)})")
    print("=" * 60)
    
    for d in discoveries[-10:]:  # Show last 10
        print(f"\n  {d['discovery_id']}: {d['project_id']}")
        print(f"    Findings: {d['summary']['total_findings']}")
        print(f"    Discovered: {d['discovered_at']}")


COMMANDS = {
    "discover": cmd_discover,
    "discover-all": cmd_discover_all,
    "status": cmd_status,
    "history": cmd_history,
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
