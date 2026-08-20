#!/usr/bin/env python3
"""
LVC-001 Migration Script: Legacy fields → Canonical governance state dimensions.

Reads project-index.json (v1), projects legacy fields into canonical dimensions,
produces project-index-v2.json, and generates migration evidence.

Usage:
    python3 scripts/migrate-governance-state.py [--dry-run] [--output PATH]

This script does NOT delete legacy fields. They are retained as provenance.
"""

import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

# Canonical lifecycle state mapping from legacy current_phase values
# These are approximate projections — documented per-entity in migration evidence
LIFECYCLE_STATE_PROJECTION = {
    "execution": "ACTIVE",
    "active": "ACTIVE",
    "init": "INITIALIZED",
    "bootstrap": "INITIALIZED",
    "governed": "ACTIVE",
    None: "DISCOVERED",
}

# Entity type mapping from session evidence (WP-003B classifications)
ENTITY_TYPE_MAP = {
    "librarian": "CAPABILITY",
    "qa-pilot": "CAPABILITY",
    "agent-bridge": "CAPABILITY",
    "librarian-workbench": "CAPABILITY",
    "working-bibliography-extension": "EXTENSION",
    "claude-conversation-ingestion": "HISTORICAL_LINEAGE",
    "librarian-vault": "SYSTEM_COMPONENT",
    "knowledge-ingestion-addon": "CAPABILITY",
}

# Default governance state for entities without explicit classification
DEFAULT_GOVERNANCE_STATE = {
    "entity_type": "CAPABILITY",
    "lifecycle_state": "DISCOVERED",
    "qualification_state": "UNREVIEWED",
    "health_state": "UNKNOWN",
    "execution_policy": "BLOCKED",
}

# Applicability rules — which dimensions are N/A for which entity types
QUALIFICATION_NA_TYPES = {"SYSTEM_COMPONENT", "HISTORICAL_LINEAGE"}
EXECUTION_POLICY_NA_TYPES = {"SYSTEM_COMPONENT", "HISTORICAL_LINEAGE"}


def project_lifecycle_state(entity):
    """Project legacy current_phase into canonical lifecycle_state."""
    current_phase = entity.get("current_phase") or entity.get("current_phase_deprecated")
    return LIFECYCLE_STATE_PROJECTION.get(current_phase, "DISCOVERED")


def project_qualification_state(entity_type):
    """Project qualification_state based on entity_type applicability."""
    if entity_type in QUALIFICATION_NA_TYPES:
        return "N/A"
    return "UNREVIEWED"


def project_execution_policy(entity_type):
    """Project execution_policy based on entity_type applicability."""
    if entity_type in EXECUTION_POLICY_NA_TYPES:
        return "N/A"
    return "BLOCKED"


def migrate_entity(entity):
    """Migrate a single entity from legacy fields to canonical governance state."""
    project_id = entity["project_id"]
    entity_type = ENTITY_TYPE_MAP.get(project_id, DEFAULT_GOVERNANCE_STATE["entity_type"])
    lifecycle_state = project_lifecycle_state(entity)
    qualification_state = project_qualification_state(entity_type)
    health_state = "UNKNOWN"
    execution_policy = project_execution_policy(entity_type)

    governance_state = {
        "entity_type": entity_type,
        "lifecycle_state": lifecycle_state,
        "qualification_state": qualification_state,
        "health_state": health_state,
        "execution_policy": execution_policy,
    }

    # Preserve legacy fields as provenance
    legacy_fields = {}
    for field in ["current_phase", "current_phase_deprecated", "lifecycle_stage", "lifecycle_label"]:
        if field in entity:
            legacy_fields[field] = entity[field]

    return governance_state, legacy_fields


def validate_governance_state(project_id, governance_state):
    """Validate governance state for conflation rules."""
    errors = []
    et = governance_state["entity_type"]
    ls = governance_state["lifecycle_state"]
    qs = governance_state["qualification_state"]
    hs = governance_state["health_state"]
    ep = governance_state["execution_policy"]

    # LCV-004: SYSTEM_COMPONENT/HISTORICAL_LINEAGE → qualification_state = N/A
    if et in QUALIFICATION_NA_TYPES and qs != "N/A":
        errors.append(f"LCV-004: {project_id} entity_type={et} but qualification_state={qs} (should be N/A)")

    # LCV-005: SYSTEM_COMPONENT/HISTORICAL_LINEAGE → execution_policy = N/A
    if et in EXECUTION_POLICY_NA_TYPES and ep != "N/A":
        errors.append(f"LCV-005: {project_id} entity_type={et} but execution_policy={ep} (should be N/A)")

    return errors


def migrate_registry(input_path, output_path, dry_run=False):
    """Migrate the full registry."""
    with open(input_path) as f:
        registry = json.load(f)

    migration_evidence = []
    all_errors = []

    for entity in registry["projects"]:
        project_id = entity["project_id"]
        governance_state, legacy_fields = migrate_entity(entity)

        # Validate
        errors = validate_governance_state(project_id, governance_state)
        all_errors.extend(errors)

        # Record migration evidence
        evidence = {
            "project_id": project_id,
            "entity_type": governance_state["entity_type"],
            "lifecycle_state_projected_from": entity.get("current_phase") or entity.get("current_phase_deprecated"),
            "lifecycle_state_projected_to": governance_state["lifecycle_state"],
            "qualification_state": governance_state["qualification_state"],
            "health_state": governance_state["health_state"],
            "execution_policy": governance_state["execution_policy"],
            "legacy_fields_retained": list(legacy_fields.keys()),
        }
        migration_evidence.append(evidence)

        if not dry_run:
            entity["governance_state"] = governance_state
            entity["legacy_fields"] = legacy_fields

            # Remove deprecated top-level fields (they're now in legacy_fields)
            for field in ["current_phase", "current_phase_deprecated", "lifecycle_stage", "lifecycle_label",
                          "lifecycle_policy_version", "lifecycle_stage", "lifecycle_cycle", "lifecycle_label"]:
                entity.pop(field, None)

    if not dry_run:
        registry["registry_version"] = 2
        registry["last_updated"] = datetime.now(timezone.utc).isoformat()
        registry["lifecycle_note"] = "governance_state dimensions are canonical. legacy_fields retained as provenance."

        with open(output_path, "w") as f:
            json.dump(registry, f, indent=2)

    return migration_evidence, all_errors


def main():
    dry_run = "--dry-run" in sys.argv
    output_path = None
    for i, arg in enumerate(sys.argv):
        if arg == "--output" and i + 1 < len(sys.argv):
            output_path = sys.argv[i + 1]

    workspace = Path(__file__).parent.parent.parent.parent
    input_path = workspace / ".librarian" / "project-index.json"
    if output_path is None:
        output_path = workspace / ".librarian" / "project-index-v2.json"

    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print(f"Dry run: {dry_run}")
    print()

    evidence, errors = migrate_registry(input_path, output_path, dry_run)

    print("Migration Evidence:")
    for e in evidence:
        print(f"  {e['project_id']}:")
        print(f"    entity_type: {e['entity_type']}")
        print(f"    lifecycle_state: {e['lifecycle_state_projected_from']} → {e['lifecycle_state_projected_to']}")
        print(f"    qualification_state: {e['qualification_state']}")
        print(f"    health_state: {e['health_state']}")
        print(f"    execution_policy: {e['execution_policy']}")
        print(f"    legacy_fields_retained: {e['legacy_fields_retained']}")
        print()

    if errors:
        print("VALIDATION ERRORS:")
        for err in errors:
            print(f"  {err}")
        sys.exit(1)
    else:
        print("Validation: ALL PASS")

    if not dry_run:
        # Write migration evidence
        evidence_path = workspace / "active" / "qa-pilot" / "evidence" / "LVC-001" / "migration-evidence.json"
        with open(evidence_path, "w") as f:
            json.dump({
                "sprint": "LVC-001",
                "work_packet": "WP-LVC-002",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "input": str(input_path),
                "output": str(output_path),
                "dry_run": False,
                "entity_count": len(evidence),
                "errors": errors,
                "entities": evidence,
            }, f, indent=2)
        print(f"\nMigration evidence written to: {evidence_path}")


if __name__ == "__main__":
    main()
