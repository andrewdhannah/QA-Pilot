#!/usr/bin/env python3
"""
Governance State Reader — Read-only access to canonical five-dimensional governance state.

Reads from project-index-v2.json. Provides entity governance context
to consumers (qualification engine, health assessment, etc.).

This module is READ-ONLY. It does not write to the registry.
"""

import json
import os
from pathlib import Path
from typing import Optional

# Default registry path (workspace-level)
DEFAULT_REGISTRY_PATH = Path(__file__).parent.parent.parent.parent / ".librarian" / "project-index-v2.json"


def load_registry(registry_path: Optional[Path] = None) -> dict:
    """Load the project-index-v2.json registry."""
    path = registry_path or DEFAULT_REGISTRY_PATH
    if not path.exists():
        raise FileNotFoundError(f"Registry not found: {path}")
    with open(path) as f:
        return json.load(f)


def get_entity_governance_state(project_id: str, registry_path: Optional[Path] = None) -> Optional[dict]:
    """
    Get the canonical governance state for a single entity.
    
    Returns dict with all 5 dimensions, or None if entity not found.
    """
    registry = load_registry(registry_path)
    for project in registry.get("projects", []):
        if project.get("project_id") == project_id:
            gs = project.get("governance_state", {})
            return {
                "project_id": project_id,
                "entity_type": gs.get("entity_type"),
                "lifecycle_state": gs.get("lifecycle_state"),
                "qualification_state": gs.get("qualification_state"),
                "health_state": gs.get("health_state"),
                "execution_policy": gs.get("execution_policy"),
            }
    return None


def get_all_entity_governance_states(registry_path: Optional[Path] = None) -> list:
    """
    Get canonical governance state for all entities.
    
    Returns list of dicts, one per entity, each with all 5 dimensions.
    """
    registry = load_registry(registry_path)
    states = []
    for project in registry.get("projects", []):
        gs = project.get("governance_state", {})
        states.append({
            "project_id": project.get("project_id"),
            "entity_type": gs.get("entity_type"),
            "lifecycle_state": gs.get("lifecycle_state"),
            "qualification_state": gs.get("qualification_state"),
            "health_state": gs.get("health_state"),
            "execution_policy": gs.get("execution_policy"),
        })
    return states


def get_dimension(project_id: str, dimension: str, registry_path: Optional[Path] = None) -> Optional[str]:
    """
    Get a single dimension for an entity.
    
    Valid dimensions: entity_type, lifecycle_state, qualification_state, health_state, execution_policy
    """
    valid_dimensions = {"entity_type", "lifecycle_state", "qualification_state", "health_state", "execution_policy"}
    if dimension not in valid_dimensions:
        raise ValueError(f"Invalid dimension: {dimension}. Must be one of: {valid_dimensions}")
    
    state = get_entity_governance_state(project_id, registry_path)
    if state is None:
        return None
    return state.get(dimension)


def get_governance_state_snapshot(project_id: str, registry_path: Optional[Path] = None) -> Optional[dict]:
    """
    Get a complete governance state snapshot for an entity, including metadata.
    
    Returns a snapshot suitable for inclusion in qualification receipts.
    """
    state = get_entity_governance_state(project_id, registry_path)
    if state is None:
        return None
    
    import datetime
    return {
        "snapshot_type": "governance_state",
        "snapshot_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": "project-index-v2.json",
        "governance_state": state,
    }


def validate_state_independence(project_id: str, registry_path: Optional[Path] = None) -> dict:
    """
    Validate that all 5 dimensions are independently populated for an entity.
    
    Returns validation result with pass/fail per dimension.
    """
    state = get_entity_governance_state(project_id, registry_path)
    if state is None:
        return {"valid": False, "error": f"Entity not found: {project_id}"}
    
    checks = {}
    for dim in ["entity_type", "lifecycle_state", "qualification_state", "health_state", "execution_policy"]:
        value = state.get(dim)
        checks[dim] = {
            "populated": value is not None and value != "",
            "value": value,
        }
    
    all_populated = all(c["populated"] for c in checks.values())
    return {
        "valid": all_populated,
        "project_id": project_id,
        "checks": checks,
    }


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Governance State Reader")
    sub = parser.add_subparsers(dest="command")
    
    # get command
    get_cmd = sub.add_parser("get", help="Get governance state for an entity")
    get_cmd.add_argument("project_id", help="Entity project ID")
    get_cmd.add_argument("--dimension", help="Specific dimension to read")
    get_cmd.add_argument("--registry", help="Path to registry file")
    get_cmd.add_argument("--json", action="store_true", help="Output as JSON")
    
    # list command
    list_cmd = sub.add_parser("list", help="List governance state for all entities")
    list_cmd.add_argument("--registry", help="Path to registry file")
    list_cmd.add_argument("--json", action="store_true", help="Output as JSON")
    
    # validate command
    validate_cmd = sub.add_parser("validate", help="Validate state independence for an entity")
    validate_cmd.add_argument("project_id", help="Entity project ID")
    validate_cmd.add_argument("--registry", help="Path to registry file")
    
    args = parser.parse_args()
    
    registry_path = Path(args.registry) if hasattr(args, 'registry') and args.registry else None
    
    if args.command == "get":
        if args.dimension:
            value = get_dimension(args.project_id, args.dimension, registry_path)
            if value is None:
                print(f"Entity or dimension not found: {args.project_id}/{args.dimension}")
                return 1
            if hasattr(args, 'json') and args.json:
                print(json.dumps({"project_id": args.project_id, "dimension": args.dimension, "value": value}))
            else:
                print(f"{args.project_id}.{args.dimension} = {value}")
        else:
            state = get_entity_governance_state(args.project_id, registry_path)
            if state is None:
                print(f"Entity not found: {args.project_id}")
                return 1
            if hasattr(args, 'json') and args.json:
                print(json.dumps(state, indent=2))
            else:
                for dim in ["entity_type", "lifecycle_state", "qualification_state", "health_state", "execution_policy"]:
                    print(f"  {dim:25s} = {state.get(dim)}")
    
    elif args.command == "list":
        states = get_all_entity_governance_states(registry_path)
        if hasattr(args, 'json') and args.json:
            print(json.dumps(states, indent=2))
        else:
            for s in states:
                print(f"\n{s['project_id']}:")
                for dim in ["entity_type", "lifecycle_state", "qualification_state", "health_state", "execution_policy"]:
                    print(f"  {dim:25s} = {s.get(dim)}")
    
    elif args.command == "validate":
        result = validate_state_independence(args.project_id, registry_path)
        if result["valid"]:
            print(f"PASS: {args.project_id} — all 5 dimensions independently populated")
        else:
            print(f"FAIL: {args.project_id}")
            for dim, check in result.get("checks", {}).items():
                status = "OK" if check["populated"] else "MISSING"
                print(f"  {dim:25s} = {check['value']} [{status}]")
        return 0 if result["valid"] else 1
    
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    exit(main())
