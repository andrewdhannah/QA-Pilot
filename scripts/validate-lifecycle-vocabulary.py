#!/usr/bin/env python3
"""
LVC-004: Lifecycle Vocabulary Conflation Detector.

Validates governance state dimensions for orthogonality violations.
Produces Findings for conflation — does NOT auto-repair or mutate state.

Usage:
    python3 scripts/validate-lifecycle-vocabulary.py [--registry PATH]

Exit codes:
    0 — all checks pass
    1 — conflation violations detected
    2 — schema/structural errors
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone


# --- Conflation Rules ---

RULES = {
    "LCV-001": {
        "description": "lifecycle_state must not be used as qualification_state",
        "check": "lifecycle_as_qualification",
    },
    "LCV-002": {
        "description": "health_state must not imply qualification",
        "check": "health_implies_qualification",
    },
    "LCV-003": {
        "description": "qualification_state must not imply execution permission",
        "check": "qualification_implies_execution",
    },
    "LCV-004": {
        "description": "SYSTEM_COMPONENT/HISTORICAL_LINEAGE must have qualification_state N/A",
        "check": "type_qualification_applicability",
    },
    "LCV-005": {
        "description": "SYSTEM_COMPONENT/HISTORICAL_LINEAGE must have execution_policy N/A",
        "check": "type_execution_applicability",
    },
}

# Entity types where qualification_state should be N/A
QUALIFICATION_NA_TYPES = {"SYSTEM_COMPONENT", "HISTORICAL_LINEAGE"}

# Entity types where execution_policy should be N/A
EXECUTION_POLICY_NA_TYPES = {"SYSTEM_COMPONENT", "HISTORICAL_LINEAGE"}


def check_lcv_001(entity):
    """LCV-001: lifecycle_state must not be used as qualification_state."""
    findings = []
    gs = entity.get("governance_state", {})
    ls = gs.get("lifecycle_state", "")
    qs = gs.get("qualification_state", "")

    # Check if lifecycle state values are being used where qualification should be
    # This detects the old pattern where current_phase was used as qualification proxy
    lifecycle_as_qualification_values = {"QUALIFIED", "UNREVIEWED", "REVIEW_REQUIRED", "DISQUALIFIED"}
    if ls in lifecycle_as_qualification_values and ls == qs:
        findings.append({
            "rule": "LCV-001",
            "severity": "error",
            "project_id": entity.get("project_id"),
            "message": f"lifecycle_state '{ls}' matches qualification_state — possible conflation",
            "dimension_conflict": "lifecycle_state/qualification_state",
        })

    return findings


def check_lcv_002(entity):
    """LCV-002: health_state must not imply qualification."""
    findings = []
    gs = entity.get("governance_state", {})
    hs = gs.get("health_state", "")
    qs = gs.get("qualification_state", "")

    # HEALTHY should not imply QUALIFIED
    if hs == "HEALTHY" and qs == "QUALIFIED":
        # This is a legal combination, but we flag if health is the ONLY evidence
        # For now, just check that qualification has its own authority
        pass  # Legal — no finding

    # DEGRADED should not imply DISQUALIFIED
    if hs == "DEGRADED" and qs == "DISQUALIFIED":
        findings.append({
            "rule": "LCV-002",
            "severity": "error",
            "project_id": entity.get("project_id"),
            "message": f"health_state DEGRADED with qualification_state DISQUALIFIED — health may be used as qualification proxy",
            "dimension_conflict": "health_state/qualification_state",
        })

    return findings


def check_lcv_003(entity):
    """LCV-003: qualification_state must not imply execution permission."""
    findings = []
    gs = entity.get("governance_state", {})
    qs = gs.get("qualification_state", "")
    ep = gs.get("execution_policy", "")

    # QUALIFIED should not automatically imply AUTO execution
    if qs == "QUALIFIED" and ep == "AUTO":
        findings.append({
            "rule": "LCV-003",
            "severity": "error",
            "project_id": entity.get("project_id"),
            "message": f"qualification_state QUALIFIED with execution_policy AUTO — qualification may be used as execution permission proxy",
            "dimension_conflict": "qualification_state/execution_policy",
        })

    # UNREVIEWED should not imply BLOCKED (this is the natural state, not conflation)
    # Actually UNREVIEWED + BLOCKED is the correct initial state — no finding

    return findings


def check_lcv_004(entity):
    """LCV-004: SYSTEM_COMPONENT/HISTORICAL_LINEAGE must have qualification_state N/A."""
    findings = []
    gs = entity.get("governance_state", {})
    et = gs.get("entity_type", "")
    qs = gs.get("qualification_state", "")

    if et in QUALIFICATION_NA_TYPES and qs != "N/A":
        findings.append({
            "rule": "LCV-004",
            "severity": "error",
            "project_id": entity.get("project_id"),
            "message": f"entity_type {et} has qualification_state {qs} — should be N/A",
            "dimension_conflict": "entity_type/qualification_state",
        })

    return findings


def check_lcv_005(entity):
    """LCV-005: SYSTEM_COMPONENT/HISTORICAL_LINEAGE must have execution_policy N/A."""
    findings = []
    gs = entity.get("governance_state", {})
    et = gs.get("entity_type", "")
    ep = gs.get("execution_policy", "")

    if et in EXECUTION_POLICY_NA_TYPES and ep != "N/A":
        findings.append({
            "rule": "LCV-005",
            "severity": "error",
            "project_id": entity.get("project_id"),
            "message": f"entity_type {et} has execution_policy {ep} — should be N/A",
            "dimension_conflict": "entity_type/execution_policy",
        })

    return findings


CHECK_FUNCTIONS = {
    "lifecycle_as_qualification": check_lcv_001,
    "health_implies_qualification": check_lcv_002,
    "qualification_implies_execution": check_lcv_003,
    "type_qualification_applicability": check_lcv_004,
    "type_execution_applicability": check_lcv_005,
}


def validate_registry(registry_path):
    """Validate all entities in the registry for conflation violations."""
    with open(registry_path) as f:
        registry = json.load(f)

    all_findings = []
    entities_checked = 0

    for entity in registry.get("projects", []):
        entities_checked += 1
        for rule_id, rule_def in RULES.items():
            check_fn = CHECK_FUNCTIONS[rule_def["check"]]
            findings = check_fn(entity)
            all_findings.extend(findings)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "registry_path": str(registry_path),
        "entities_checked": entities_checked,
        "rules_applied": list(RULES.keys()),
        "findings_count": len(all_findings),
        "findings": all_findings,
        "verdict": "PASS" if len(all_findings) == 0 else "FAIL",
    }


def main():
    registry_path = None
    for i, arg in enumerate(sys.argv):
        if arg == "--registry" and i + 1 < len(sys.argv):
            registry_path = sys.argv[i + 1]

    if registry_path is None:
        workspace = Path(__file__).parent.parent.parent.parent
        registry_path = workspace / ".librarian" / "project-index-v2.json"

    result = validate_registry(Path(registry_path))

    # Write findings
    workspace = Path(__file__).parent.parent.parent.parent
    findings_path = workspace / "active" / "qa-pilot" / "evidence" / "LVC-001" / "conflation-findings.json"
    with open(findings_path, "w") as f:
        json.dump(result, f, indent=2)

    # Print summary
    print(f"Registry: {result['registry_path']}")
    print(f"Entities checked: {result['entities_checked']}")
    print(f"Rules applied: {', '.join(result['rules_applied'])}")
    print(f"Findings: {result['findings_count']}")
    print(f"Verdict: {result['verdict']}")
    print()

    if result["findings"]:
        print("FINDINGS (routed to disposition pipeline — NOT auto-repaired):")
        for f in result["findings"]:
            print(f"  [{f['rule']}] {f['severity'].upper()}: {f['message']}")
        sys.exit(1)
    else:
        print("No conflation violations detected.")
        sys.exit(0)


if __name__ == "__main__":
    main()
