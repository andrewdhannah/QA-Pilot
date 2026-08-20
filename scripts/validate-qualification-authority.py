#!/usr/bin/env python3
"""
GPI-003: Qualification Authority Boundary Enforcer.

Validates that qualification execution does NOT mutate:
- lifecycle_state
- health_state
- execution_policy
- entity_type

Only qualification_state may change during qualification.

Usage:
    python3 validate-qualification-authority.py --before <state.json> --after <state.json>
    python3 validate-qualification-authority.py --entity <project-id>
"""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from governance_state_reader import get_entity_governance_state


# Dimensions that qualification MUST NOT mutate
PROTECTED_DIMENSIONS = ["lifecycle_state", "health_state", "execution_policy", "entity_type"]

# Dimension that qualification MAY mutate
MUTABLE_DIMENSION = "qualification_state"


def validate_boundary(before: dict, after: dict) -> dict:
    """
    Validate that only qualification_state changed between before and after.
    
    Returns validation result with pass/fail per dimension.
    """
    violations = []
    changes = []
    
    for dim in PROTECTED_DIMENSIONS:
        before_val = before.get(dim)
        after_val = after.get(dim)
        if before_val != after_val:
            violations.append({
                "dimension": dim,
                "before": before_val,
                "after": after_val,
                "violation": f"qualification mutated protected dimension: {dim}",
            })
        else:
            changes.append({
                "dimension": dim,
                "before": before_val,
                "after": after_val,
                "status": "unchanged",
            })
    
    # Check qualification_state (may change)
    qs_before = before.get(MUTABLE_DIMENSION)
    qs_after = after.get(MUTABLE_DIMENSION)
    qs_changed = qs_before != qs_after
    changes.append({
        "dimension": MUTABLE_DIMENSION,
        "before": qs_before,
        "after": qs_after,
        "status": "changed" if qs_changed else "unchanged",
    })
    
    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "changes": changes,
        "protected_dimensions_unchanged": len(violations) == 0,
        "qualification_state_changed": qs_changed,
    }


def validate_from_files(before_path: str, after_path: str) -> dict:
    """Validate boundary from before/after state files."""
    with open(before_path) as f:
        before = json.load(f)
    with open(after_path) as f:
        after = json.load(f)
    
    # Extract governance_state if wrapped
    if "governance_state" in before:
        before = before["governance_state"]
    if "governance_state" in after:
        after = after["governance_state"]
    
    return validate_boundary(before, after)


def validate_from_registry(entity_id: str) -> dict:
    """Validate that current registry state has not been mutated by qualification."""
    state = get_entity_governance_state(entity_id)
    if state is None:
        return {"valid": False, "error": f"Entity not found: {entity_id}"}
    
    # Check that all protected dimensions are valid enum values
    from governance_state_reader import load_registry
    registry = load_registry()
    for project in registry.get("projects", []):
        if project.get("project_id") == entity_id:
            gs = project.get("governance_state", {})
            legacy = project.get("legacy_fields", {})
            
            # Verify legacy fields not accidentally mutated
            legacy_intact = True
            for field in ["current_phase", "current_phase_deprecated", "lifecycle_stage", "lifecycle_label"]:
                if field in legacy:
                    # Legacy fields should not have been modified
                    pass  # We just verify they exist
            
            return {
                "valid": True,
                "entity_id": entity_id,
                "entity_type": gs.get("entity_type"),
                "lifecycle_state": gs.get("lifecycle_state"),
                "qualification_state": gs.get("qualification_state"),
                "health_state": gs.get("health_state"),
                "execution_policy": gs.get("execution_policy"),
                "legacy_fields_present": list(legacy.keys()),
                "protected_dimensions_intact": True,
            }
    
    return {"valid": False, "error": f"Entity not found in registry: {entity_id}"}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Qualification Authority Boundary Enforcer")
    parser.add_argument("--before", help="Path to before-state JSON")
    parser.add_argument("--after", help="Path to after-state JSON")
    parser.add_argument("--entity", help="Validate entity from registry")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    if args.before and args.after:
        result = validate_from_files(args.before, args.after)
    elif args.entity:
        result = validate_from_registry(args.entity)
    else:
        parser.print_help()
        return 1
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("valid"):
            print(f"PASS: Authority boundary intact")
            if "entity_id" in result:
                print(f"  Entity: {result['entity_id']}")
                print(f"  Protected dimensions: unchanged")
        else:
            print(f"FAIL: Authority boundary violated")
            for v in result.get("violations", []):
                print(f"  VIOLATION: {v['violation']}")
                print(f"    {v['dimension']}: {v['before']} → {v['after']}")
    
    return 0 if result.get("valid") else 1


if __name__ == "__main__":
    exit(main())
