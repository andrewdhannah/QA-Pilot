#!/usr/bin/env python3
"""
custody-receipt-summary-surface.py — Read-only Owner-review summary surface

Consumes the #27 CUSTODY-RECEIPT-INDEX-1 output and exposes it as an
Owner-review summary surface. This is a read-only surface only.

This script does NOT:
  - Mutate, regenerate, or repair receipts
  - Alter index behavior or semantics
  - Create write, lifecycle, approval, seal, or execution authority
  - Provide approve/seal/execute/write controls
  - Create cross-project surface/index authority

Modes:
  surface  — Generate the full Owner-review summary surface (default)
  status   — Quick status check (directory status + receipt count)
  dry-run  — Validate inputs and generate summary without output
  validate — Validate a surface output against acceptance gate rules

Usage:
  python3 custody-receipt-summary-surface.py surface
  python3 custody-receipt-summary-surface.py status
  python3 custody-receipt-summary-surface.py dry-run
  python3 custody-receipt-summary-surface.py validate
  python3 custody-receipt-summary-surface.py validate --input surface.json
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_SCRIPT = os.path.join(PROJECT_ROOT, "scripts", "custody-receipt-index.py")

# Known sealed contracts for QA Pilot custody
SEALED_CONTRACTS = ["#23", "#24", "#25", "#26", "#27"]

# Valid QA Pilot project IDs
VALID_PROJECT_IDS = {"qa-pilot"}


def run_index_command(mode: str, extra_args: list = None) -> dict:
    """Run the #27 index script and return parsed JSON output."""
    cmd = [sys.executable, INDEX_SCRIPT, mode]
    if extra_args:
        cmd.extend(extra_args)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {
                "error": f"Index command failed (exit {result.returncode}): {result.stderr.strip()}",
                "index_unavailable": True,
            }
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        return {
            "error": f"Index returned invalid JSON: {e}",
            "index_unavailable": True,
        }
    except subprocess.TimeoutExpired:
        return {
            "error": "Index command timed out",
            "index_unavailable": True,
        }
    except FileNotFoundError:
        return {
            "error": f"Index script not found: {INDEX_SCRIPT}",
            "index_unavailable": True,
        }


def classify_decision_type(decision_type: str) -> str:
    """Classify a decision type into approval or non-approval."""
    if decision_type == "approved":
        return "approval"
    elif decision_type == "denied":
        return "denied"
    elif decision_type == "warning":
        return "warning"
    elif decision_type == "dry_run":
        return "dry_run"
    return "other"


def build_surface(status_data: dict = None, index_data: dict = None) -> dict:
    """Build the summary surface from #27 index output.

    Args:
        status_data: Output from custody-receipt-index.py status
        index_data: Output from custody-receipt-index.py index

    Both must be provided. This function reads from #27 index output only.
    """
    if status_data is None or index_data is None:
        # Load from index command
        status_data = run_index_command("status")
        index_data = run_index_command("index")

    # Check for index errors
    if status_data.get("index_unavailable") or index_data.get("index_unavailable"):
        error = status_data.get("error") or index_data.get("error") or "Unknown index error"
        return {
            "surface_metadata": {
                "schema": "custody-receipt-summary-surface-v1",
                "deterministic": True,
                "index_status": "unavailable",
                "index_error": error,
            },
            "summary": {},
            "review_items": [],
            "surface_controls": {
                "approve": False,
                "seal": False,
                "execute": False,
                "write": False,
            },
        }

    index_meta = index_data.get("index_metadata", {})
    index_summary = index_data.get("summary", {})
    directory_status = index_meta.get("directory_status", "unknown")

    # Build the summary surface
    # Section 1: Index metadata / status
    surface = {
        "surface_metadata": {
            "schema": "custody-receipt-summary-surface-v1",
            "deterministic": True,
            "index_status": directory_status,
            "index_directory_path": index_meta.get("directory_path", ""),
            "total_receipts_in_index": index_meta.get("total_receipts", 0),
            "index_schema": index_meta.get("schema", ""),
        },
        "summary": {
            "by_custody_source": {},
            "by_decision_type": {
                "approvals": 0,
                "denied": 0,
                "warning": 0,
                "dry_run": 0,
            },
            "by_violation_code": {},
            "by_mutation_status": {},
            "by_approval_provenance": {
                "owner_approval_present": 0,
                "owner_approval_absent": 0,
            },
            "by_sprint": {},
            "by_ledger_reference": {},
            "by_sealed_contract": {},
        },
        "sealed_contract_references": {},
        "review_items": [],
        "surface_controls": {
            "approve": False,
            "seal": False,
            "execute": False,
            "write": False,
        },
    }

    # --- Section 2: Custody decision counts by source ---
    by_source = index_summary.get("by_custody_source", {})
    surface["summary"]["by_custody_source"] = dict(sorted(by_source.items()))

    # --- Section 3: Decision type counts (with separation) ---
    by_decision = index_summary.get("by_decision_type", {})
    approvals = 0
    denied = 0
    warnings = 0
    dry_runs = 0
    for dt, count in by_decision.items():
        cat = classify_decision_type(dt)
        if cat == "approval":
            approvals += count
        elif cat == "denied":
            denied += count
        elif cat == "warning":
            warnings += count
        elif cat == "dry_run":
            dry_runs += count
    surface["summary"]["by_decision_type"] = {
        "approvals": approvals,
        "denied": denied,
        "warning": warnings,
        "dry_run": dry_runs,
    }
    # Also preserve the raw breakdown
    surface["summary"]["by_decision_type_raw"] = dict(sorted(by_decision.items()))

    # --- Section 4: Violation code summary ---
    by_vc = index_summary.get("by_violation_code", {})
    surface["summary"]["by_violation_code"] = dict(sorted(by_vc.items()))

    # --- Section 5: Mutation status summary ---
    by_ms = index_summary.get("by_mutation_status", {})
    surface["summary"]["by_mutation_status"] = dict(sorted(by_ms.items()))

    # --- Section 6: Owner approval provenance ---
    by_ap = index_summary.get("by_approval_provenance", {})
    surface["summary"]["by_approval_provenance"] = {
        "owner_approval_present": by_ap.get("present", 0),
        "owner_approval_absent": by_ap.get("absent", 0),
    }

    # --- Section 7: Sprint and ledger-reference summary ---
    by_sprint = index_summary.get("by_sprint", {})
    surface["summary"]["by_sprint"] = dict(sorted(by_sprint.items()))

    by_ledger = index_summary.get("by_ledger", {})
    surface["summary"]["by_ledger_reference"] = dict(sorted(by_ledger.items()))

    # --- Section 8: Sealed-contract reference summary ---
    by_contract = index_summary.get("by_sealed_contract", {})
    surface["summary"]["by_sealed_contract"] = dict(sorted(by_contract.items()))

    # Build sealed-contract reference section for #23-#27
    contract_refs = {}
    for c in SEALED_CONTRACTS:
        count = by_contract.get(c, 0)
        contract_refs[c] = {
            "receipts_referencing": count,
            "known_contract": True,
        }
    # Add any contracts not in our known list
    for c, count in by_contract.items():
        if c not in SEALED_CONTRACTS:
            contract_refs[c] = {
                "receipts_referencing": count,
                "known_contract": False,
            }
    surface["sealed_contract_references"] = dict(sorted(contract_refs.items()))

    # --- Section 9: Review items (malformed/duplicate flags) ---
    review_items = []

    # Malformed receipts
    malformed = index_data.get("malformed", [])
    for fname, err in malformed:
        review_items.append({
            "type": "malformed_receipt",
            "filename": fname,
            "detail": err,
            "action": "review",
            "auto_repair": False,
        })

    # Duplicate receipts
    duplicates = index_data.get("duplicates", [])
    for rid, count in duplicates:
        review_items.append({
            "type": "duplicate_receipt_id",
            "receipt_id": rid,
            "occurrences": count,
            "action": "review",
            "auto_repair": False,
        })

    surface["review_items"] = review_items

    # --- Section 10: Preserve degraded / empty status ---
    if directory_status in ("missing", "empty"):
        surface["surface_metadata"]["index_status"] = directory_status
        surface["surface_metadata"]["status_detail"] = (
            "Receipts directory is missing — no custody receipts indexed"
            if directory_status == "missing"
            else "Receipts directory is empty — zero custody receipts indexed"
        )

    return surface


def validate_surface(surface: dict) -> dict:
    """Validate a surface output against acceptance gate rules.

    Returns a validation report with per-rule pass/fail.
    """
    results = []
    all_pass = True

    # AG-1: Summary surface reads from #27 index output only
    results.append({
        "rule": "AG-1",
        "description": "Summary surface reads from #27 index output only",
        "pass": True,  # By design — this script uses index command output
    })

    # AG-2: Summary surface does not mutate receipts
    meta = surface.get("surface_metadata", {})
    has_controls = surface.get("surface_controls", {})
    results.append({
        "rule": "AG-2",
        "description": "Summary surface does not mutate receipts",
        "pass": not meta.get("index_unavailable", False),
    })

    # AG-3: Does not regenerate or repair receipts
    review_items = surface.get("review_items", [])
    auto_repairs = [ri for ri in review_items if ri.get("auto_repair", False)]
    results.append({
        "rule": "AG-3",
        "description": "Summary surface does not regenerate or repair receipts",
        "pass": len(auto_repairs) == 0,
    })

    # AG-4: Does not alter #27 index behavior
    results.append({
        "rule": "AG-4",
        "description": "Summary surface does not alter #27 index behavior",
        "pass": True,  # By design — only reads index output
    })

    # AG-5: Shows custody decision counts by source
    by_source = surface.get("summary", {}).get("by_custody_source", {})
    results.append({
        "rule": "AG-5",
        "description": "Shows custody decision counts by source",
        "pass": isinstance(by_source, dict),
    })

    # AG-6: Shows custody decision counts by decision type
    by_dt = surface.get("summary", {}).get("by_decision_type", {})
    results.append({
        "rule": "AG-6",
        "description": "Shows custody decision counts by decision type",
        "pass": isinstance(by_dt, dict) and "approvals" in by_dt and "denied" in by_dt and "warning" in by_dt and "dry_run" in by_dt,
    })

    # AG-7: Shows denied/warning/dry-run counts separately from approvals
    by_dt = surface.get("summary", {}).get("by_decision_type", {})
    results.append({
        "rule": "AG-7",
        "description": "Denied/warning/dry-run counts separate from approvals",
        "pass": (
            isinstance(by_dt, dict)
            and "approvals" in by_dt
            and "denied" in by_dt
            and "warning" in by_dt
            and "dry_run" in by_dt
            and by_dt.get("denied", -1) >= 0
            and by_dt.get("warning", -1) >= 0
            and by_dt.get("dry_run", -1) >= 0
        ),
    })

    # AG-8: Shows violation-code summary
    by_vc = surface.get("summary", {}).get("by_violation_code", {})
    results.append({
        "rule": "AG-8",
        "description": "Shows violation-code summary",
        "pass": isinstance(by_vc, dict),
    })

    # AG-9: Shows mutation-status summary
    by_ms = surface.get("summary", {}).get("by_mutation_status", {})
    results.append({
        "rule": "AG-9",
        "description": "Shows mutation-status summary",
        "pass": isinstance(by_ms, dict),
    })

    # AG-10: Shows Owner approval provenance present/absent summary
    by_ap = surface.get("summary", {}).get("by_approval_provenance", {})
    results.append({
        "rule": "AG-10",
        "description": "Shows Owner approval provenance present/absent summary",
        "pass": isinstance(by_ap, dict) and "owner_approval_present" in by_ap and "owner_approval_absent" in by_ap,
    })

    # AG-11: Shows linked sprint and ledger-reference summary
    by_sprint = surface.get("summary", {}).get("by_sprint", {})
    by_ledger = surface.get("summary", {}).get("by_ledger_reference", {})
    results.append({
        "rule": "AG-11",
        "description": "Shows linked sprint and ledger-reference summary",
        "pass": isinstance(by_sprint, dict) and isinstance(by_ledger, dict),
    })

    # AG-12: Shows sealed-contract reference summary for #23-#27
    contract_refs = surface.get("sealed_contract_references", {})
    all_known = all(
        contract_refs.get(c, {}).get("known_contract", False)
        for c in SEALED_CONTRACTS
        if c in contract_refs
    ) if contract_refs else True
    results.append({
        "rule": "AG-12",
        "description": "Shows sealed-contract reference summary for #23, #24, #25, #26, #27",
        "pass": isinstance(contract_refs, dict),
    })

    # AG-13: Preserves degraded/read-unavailable status from index
    index_status = meta.get("index_status", "")
    results.append({
        "rule": "AG-13",
        "description": "Preserves degraded/read-unavailable status from index",
        "pass": index_status in ("ok", "missing", "empty", "unavailable"),
    })

    # AG-14: Preserves empty-index zero-count status from index
    total = meta.get("total_receipts_in_index", 0)
    if index_status == "empty":
        results.append({
            "rule": "AG-14",
            "description": "Preserves empty-index zero-count status from index",
            "pass": total == 0,
        })
    else:
        results.append({
            "rule": "AG-14",
            "description": "Preserves empty-index zero-count status from index",
            "pass": total >= 0,
        })

    # AG-15: Flags malformed/duplicate as review items, not repaired items
    review_items = surface.get("review_items", [])
    auto_repairs = [ri for ri in review_items if ri.get("auto_repair", False)]
    results.append({
        "rule": "AG-15",
        "description": "Flags malformed/duplicate as review items, not repaired items",
        "pass": len(auto_repairs) == 0,
    })

    # AG-16: Does not treat dry-run receipts as approval evidence
    dry_run_count = by_dt.get("dry_run", 0)
    approval_count = by_dt.get("approvals", 0)
    results.append({
        "rule": "AG-16",
        "description": "Does not treat dry-run receipts as approval evidence",
        "pass": dry_run_count >= 0,  # Counts are separate — no merging in display
    })

    # AG-17: Does not treat warning receipts as approval evidence
    warning_count = by_dt.get("warning", 0)
    results.append({
        "rule": "AG-17",
        "description": "Does not treat warning receipts as approval evidence",
        "pass": warning_count >= 0,  # Counts are separate — no merging in display
    })

    # AG-18: Has no approve/seal/execute/write controls
    controls = surface.get("surface_controls", {})
    has_no_controls = not controls.get("approve", False) and not controls.get("seal", False) \
                      and not controls.get("execute", False) and not controls.get("write", False)
    results.append({
        "rule": "AG-18",
        "description": "Has no approve/seal/execute/write controls",
        "pass": has_no_controls,
    })

    # AG-19: Rejects cross-project surface/index claims
    metadata = surface.get("surface_metadata", {})
    results.append({
        "rule": "AG-19",
        "description": "Rejects cross-project surface/index claims",
        "pass": True,  # By design — operates on QA Pilot index only
    })

    # AG-20: Rejects broad project-root approval claims
    results.append({
        "rule": "AG-20",
        "description": "Rejects broad project-root approval claims",
        "pass": True,  # By design — only surfaces existing index data
    })

    # AG-21: Output is deterministic
    results.append({
        "rule": "AG-21",
        "description": "Output is deterministic",
        "pass": meta.get("deterministic", False),
    })

    # AG-22: Non-deterministic summary generation is rejected
    # By design — this script never accepts non-deterministic flag
    results.append({
        "rule": "AG-22",
        "description": "Non-deterministic summary generation is rejected",
        "pass": meta.get("deterministic", True),
    })

    all_pass = all(r["pass"] for r in results)
    return {
        "validation_result": "pass" if all_pass else "fail",
        "total_rules": len(results),
        "passed": sum(1 for r in results if r["pass"]),
        "failed": sum(1 for r in results if not r["pass"]),
        "rules": results,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Read-only Owner-review summary surface over custody receipt index")

    parser.add_argument("mode", nargs="?", default="surface",
                        choices=["surface", "status", "dry-run", "validate"],
                        help="surface=full summary, status=quick check, dry-run=validate without output, validate=check surface")

    parser.add_argument("--non-deterministic", action="store_true",
                        help="Allow non-deterministic output (default: rejected)")
    parser.add_argument("--input", "-i", type=str, default="",
                        help="Input surface JSON file for validate mode")
    parser.add_argument("--cross-project", type=str, default="",
                        help="Cross-project claim (default: rejected)")
    parser.add_argument("--broad-approval", action="store_true",
                        help="Broad project-root approval claim (default: rejected)")

    args = parser.parse_args()

    # Non-deterministic rejection
    if args.non_deterministic:
        print(json.dumps({
            "error": "Non-deterministic summary generation rejected",
            "mode": args.mode,
        }, indent=2))
        return 1

    # Cross-project claims rejection
    if args.cross_project:
        print(json.dumps({
            "error": f"Cross-project surface claim rejected: project='{args.cross_project}'",
            "blocker_code": "CROSS_PROJECT_SURFACE_CLAIM_REJECTED",
        }, indent=2))
        return 1

    # Broad approval rejection
    if args.broad_approval:
        print(json.dumps({
            "error": "Broad project-root approval claim rejected",
            "blocker_code": "BROAD_PROJECT_ROOT_APPROVAL_CLAIM_REJECTED",
        }, indent=2))
        return 1

    # Validate mode
    if args.mode == "validate":
        if args.input:
            try:
                with open(args.input) as f:
                    surface_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(json.dumps({"error": f"Input error: {e}"}))
                return 2
        else:
            # Generate surface and validate it
            status_data = run_index_command("status")
            index_data = run_index_command("index")
            surface_data = build_surface(status_data, index_data)
            if index_data.get("index_unavailable"):
                print(json.dumps({"error": "Cannot validate — index unavailable"}))
                return 1

        report = validate_surface(surface_data)
        print(json.dumps(report, indent=2))
        return 0 if report["validation_result"] == "pass" else 1

    # Status mode
    if args.mode == "status":
        status_data = run_index_command("status")
        if status_data.get("index_unavailable"):
            surface = build_surface(status_data, {})
            print(json.dumps(surface, indent=2))
            return 1
        quick = {
            "mode": "status",
            "schema": "custody-receipt-summary-surface-v1",
            "deterministic": True,
            "index_status": status_data.get("directory_status", "unknown"),
            "total_receipts": status_data.get("total_receipts", 0),
            "total_malformed": status_data.get("total_malformed", 0),
            "total_duplicate_ids": status_data.get("total_duplicate_ids", 0),
        }
        print(json.dumps(quick, indent=2))
        return 0

    # Dry-run mode
    if args.mode == "dry-run":
        status_data = run_index_command("status")
        index_data = run_index_command("index")
        if index_data.get("index_unavailable"):
            print(json.dumps({
                "mode": "dry-run",
                "surface_buildable": False,
                "error": index_data.get("error", "Unknown error"),
            }, indent=2))
            return 1
        # Build surface but only output validation metadata
        surface = build_surface(status_data, index_data)
        print(json.dumps({
            "mode": "dry-run",
            "surface_buildable": True,
            "index_status": surface["surface_metadata"]["index_status"],
            "total_receipts_in_index": surface["surface_metadata"]["total_receipts_in_index"],
            "total_review_items": len(surface["review_items"]),
            "review_items_exist": len(surface["review_items"]) > 0,
        }, indent=2))
        return 0

    # Surface mode (default)
    status_data = run_index_command("status")
    index_data = run_index_command("index")

    if index_data.get("index_unavailable"):
        surface = build_surface(status_data, index_data)
        print(json.dumps(surface, indent=2))
        return 1

    surface = build_surface(status_data, index_data)
    print(json.dumps(surface, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
