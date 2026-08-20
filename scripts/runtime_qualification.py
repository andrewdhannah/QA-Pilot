#!/usr/bin/env python3
"""
GPI-001 Runtime Qualification — Execute qualification against canonical governance state.

Reads canonical five-dimensional state, evaluates qualification evidence,
produces qualification result with state snapshot. Does NOT mutate
lifecycle_state, health_state, execution_policy, or entity_type.

Usage:
    python3 runtime_qualification.py evaluate --entity <project-id>
    python3 runtime_qualification.py batch [--re-evaluate]
    python3 runtime_qualification.py status --entity <project-id>
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add scripts dir to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from governance_state_reader import (
    get_entity_governance_state,
    get_governance_state_snapshot,
    validate_state_independence,
    load_registry,
)

PROJECT_ROOT = SCRIPT_DIR.parent
QUALIFICATION_EXECUTION = SCRIPT_DIR / "qa_pilot_qualification_execution.py"
RESULTS_DIR = PROJECT_ROOT / "data" / "gpi-001-results"
RESULTS_INDEX = RESULTS_DIR / "results-index.json"


def _now():
    return datetime.now(timezone.utc).isoformat()


def _ensure_dirs():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if not RESULTS_INDEX.exists():
        with open(RESULTS_INDEX, "w") as f:
            json.dump({"results": [], "last_updated": _now()}, f, indent=2)


def _load_index():
    _ensure_dirs()
    try:
        with open(RESULTS_INDEX) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"results": [], "last_updated": _now()}


def _save_index(index):
    index["last_updated"] = _now()
    with open(RESULTS_INDEX, "w") as f:
        json.dump(index, f, indent=2)


def cmd_evaluate(args):
    """Evaluate qualification for an entity with canonical state context."""
    _ensure_dirs()
    
    entity_id = args.entity
    
    # Step 1: Read canonical governance state
    state = get_entity_governance_state(entity_id)
    if state is None:
        print(f"Entity not found: {entity_id}")
        return 1
    
    # Step 2: Validate state independence
    validation = validate_state_independence(entity_id)
    if not validation["valid"]:
        print(f"FAIL: Entity {entity_id} has incomplete governance state")
        return 1
    
    # Step 3: Get state snapshot for receipt
    snapshot = get_governance_state_snapshot(entity_id)
    
    # Step 4: Determine qualification applicability
    entity_type = state.get("entity_type")
    qualification_state = state.get("qualification_state")
    
    if qualification_state == "N/A":
        # Entity type does not support qualification (SYSTEM_COMPONENT, HISTORICAL_LINEAGE)
        result = {
            "result_id": f"GPI001-{entity_id}",
            "entity_id": entity_id,
            "entity_type": entity_type,
            "qualification_applicable": False,
            "qualification_reason": f"entity_type {entity_type} does not support qualification",
            "qualification_state_before": qualification_state,
            "qualification_state_after": qualification_state,
            "canonical_state_snapshot": snapshot,
            "assessed_at": _now(),
            "assessed_by": "gpi-001-runtime-qualification",
        }
        print(f"Qualification not applicable: {entity_id} (entity_type={entity_type})")
    else:
        # Step 5: Execute qualification evaluation
        # Read existing QR records for this entity
        qr_store = PROJECT_ROOT / "data" / "qualification-records"
        qr_index_path = qr_store / "qualification-index.json"
        
        entity_records = []
        if qr_index_path.exists():
            with open(qr_index_path) as f:
                qr_index = json.load(f)
            for rid in qr_index.get("records", []):
                qr_path = qr_store / f"{rid}.json"
                if qr_path.exists():
                    with open(qr_path) as f:
                        record = json.load(f)
                    if record.get("target_id") == entity_id:
                        entity_records.append(record)
        
        # Evaluate qualification level from available evidence
        if entity_records:
            # Use existing qualification execution engine
            scores = []
            for record in entity_records:
                level = record.get("qualification_level", "unqualified")
                score = record.get("overall_score", 0.0)
                scores.append({"record_id": record.get("record_id"), "level": level, "score": score})
            
            # Compute aggregate qualification
            avg_score = sum(s["score"] for s in scores) / len(scores) if scores else 0.0
            levels = [s["level"] for s in scores]
            
            if "audited" in levels:
                agg_level = "audited"
            elif "peer_reviewed" in levels:
                agg_level = "peer_reviewed"
            elif "spot_checked" in levels:
                agg_level = "spot_checked"
            else:
                agg_level = "unqualified"
            
            assessment = "pass" if agg_level in ("audited", "peer_reviewed") else \
                         "advisory" if agg_level == "spot_checked" else "fail"
        else:
            # No QR records — qualification is unreviewed
            avg_score = 0.0
            agg_level = "unqualified"
            assessment = "fail"
            scores = []
        
        # Step 6: Determine target qualification_state
        if agg_level in ("audited", "peer_reviewed"):
            target_qs = "QUALIFIED"
        elif agg_level == "spot_checked":
            target_qs = "REVIEW_REQUIRED"
        else:
            target_qs = "UNREVIEWED"
        
        result = {
            "result_id": f"GPI001-{entity_id}",
            "entity_id": entity_id,
            "entity_type": entity_type,
            "qualification_applicable": True,
            "qualification_state_before": qualification_state,
            "qualification_state_after": target_qs,
            "qualification_level": agg_level,
            "assessment": assessment,
            "overall_score": avg_score,
            "record_count": len(entity_records),
            "record_details": scores,
            "canonical_state_snapshot": snapshot,
            "assessed_at": _now(),
            "assessed_by": "gpi-001-runtime-qualification",
        }
        
        print(f"Qualification: {entity_id}")
        print(f"  Entity type:          {entity_type}")
        print(f"  Records evaluated:    {len(entity_records)}")
        print(f"  Average score:        {avg_score:.4f}")
        print(f"  Qualification level:  {agg_level}")
        print(f"  Assessment:           {assessment}")
        print(f"  qualification_state:  {qualification_state} → {target_qs}")
    
    # Step 7: Write result
    result_path = RESULTS_DIR / f"{result['result_id']}.json"
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    
    # Update index
    idx = _load_index()
    if result["result_id"] not in idx.get("results", []):
        idx.setdefault("results", []).append(result["result_id"])
        _save_index(idx)
    
    print(f"  Result:               {result['result_id']}")
    
    # Step 8: Verify authority boundary — registry unchanged except qualification_state
    post_state = get_entity_governance_state(entity_id)
    boundary_violations = []
    for dim in ["lifecycle_state", "health_state", "execution_policy", "entity_type"]:
        if post_state.get(dim) != state.get(dim):
            boundary_violations.append(f"{dim}: {state.get(dim)} → {post_state.get(dim)}")
    
    if boundary_violations:
        print(f"  AUTHORITY VIOLATION: {boundary_violations}")
        return 1
    
    return 0


def cmd_batch(args):
    """Batch-evaluate all entities."""
    registry = load_registry()
    results = {"pass": 0, "advisory": 0, "fail": 0, "na": 0, "total": 0}
    
    for project in registry.get("projects", []):
        entity_id = project.get("project_id")
        eval_args = argparse.Namespace(entity=entity_id)
        code = cmd_evaluate(eval_args)
        if code == 0:
            gs = project.get("governance_state", {})
            qs = gs.get("qualification_state", "")
            if qs == "N/A":
                results["na"] += 1
            else:
                result_path = RESULTS_DIR / f"GPI001-{entity_id}.json"
                if result_path.exists():
                    with open(result_path) as f:
                        r = json.load(f)
                    level = r.get("qualification_level", "unqualified")
                    if level in ("audited", "peer_reviewed"):
                        results["pass"] += 1
                    elif level == "spot_checked":
                        results["advisory"] += 1
                    else:
                        results["fail"] += 1
        results["total"] += 1
    
    print(f"\nBatch results: {results['total']} entities")
    print(f"  PASS:     {results['pass']}")
    print(f"  ADVISORY: {results['advisory']}")
    print(f"  FAIL:     {results['fail']}")
    print(f"  N/A:      {results['na']}")
    return 0


def cmd_status(args):
    """Show qualification status for an entity."""
    state = get_entity_governance_state(args.entity)
    if state is None:
        print(f"Entity not found: {args.entity}")
        return 1
    
    result_path = RESULTS_DIR / f"GPI001-{args.entity}.json"
    if result_path.exists():
        with open(result_path) as f:
            result = json.load(f)
        print(f"Entity: {args.entity}")
        print(f"  entity_type:          {state['entity_type']}")
        print(f"  lifecycle_state:      {state['lifecycle_state']}")
        print(f"  qualification_state:  {state['qualification_state']}")
        print(f"  health_state:         {state['health_state']}")
        print(f"  execution_policy:     {state['execution_policy']}")
        print(f"  Last qualification:   {result.get('qualification_level', 'unknown')}")
        print(f"  Assessment:           {result.get('assessment', 'unknown')}")
        print(f"  Score:                {result.get('overall_score', 0.0):.4f}")
        print(f"  Assessed at:          {result.get('assessed_at', 'unknown')}")
    else:
        print(f"Entity: {args.entity}")
        print(f"  entity_type:          {state['entity_type']}")
        print(f"  lifecycle_state:      {state['lifecycle_state']}")
        print(f"  qualification_state:  {state['qualification_state']}")
        print(f"  health_state:         {state['health_state']}")
        print(f"  execution_policy:     {state['execution_policy']}")
        print(f"  No qualification result yet")
    return 0


def main():
    parser = argparse.ArgumentParser(description="GPI-001 Runtime Qualification")
    sub = parser.add_subparsers(dest="command")
    
    eval_cmd = sub.add_parser("evaluate", help="Evaluate qualification for an entity")
    eval_cmd.add_argument("--entity", required=True, help="Entity project ID")
    
    batch_cmd = sub.add_parser("batch", help="Batch-evaluate all entities")
    batch_cmd.add_argument("--re-evaluate", action="store_true", help="Re-evaluate already evaluated entities")
    
    status_cmd = sub.add_parser("status", help="Show qualification status")
    status_cmd.add_argument("--entity", required=True, help="Entity project ID")
    
    args = parser.parse_args()
    
    if args.command == "evaluate":
        return cmd_evaluate(args)
    elif args.command == "batch":
        return cmd_batch(args)
    elif args.command == "status":
        return cmd_status(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit(main())
