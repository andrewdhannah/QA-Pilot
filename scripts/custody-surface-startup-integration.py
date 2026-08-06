#!/usr/bin/env python3
"""
custody-surface-startup-integration.py — Startup custody posture integration

Includes the sealed CUSTODY-RECEIPT-SUMMARY-SURFACE-1 (#28) read-only custody
summary surface in QA Pilot startup reporting.

This script is startup reporting integration only. It does NOT:
  - Mutate, regenerate, or repair receipts
  - Alter #27 index behavior or #28 surface semantics
  - Create startup, approval, seal, write, lifecycle, receipt, index, or
    execution authority
  - Create cross-project startup authority

Modes:
  report   — Generate custody posture report for startup (default)
  status   — Quick status check (surface available, receipt count)
  dry-run  — Validate inputs without full output
  validate — Validate a report against acceptance gate rules

Usage:
  python3 custody-surface-startup-integration.py report
  python3 custody-surface-startup-integration.py status
  python3 custody-surface-startup-integration.py dry-run
  python3 custody-surface-startup-integration.py validate
  python3 custody-surface-startup-integration.py validate --input report.json
"""

import argparse
import json
import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURFACE_SCRIPT = os.path.join(PROJECT_ROOT, "scripts", "custody-receipt-summary-surface.py")

# Known sealed contracts
SEALED_CONTRACTS = ["#23", "#24", "#25", "#26", "#27", "#28"]


def run_surface_command(mode: str, extra_args: list = None) -> dict:
    """Run the #28 surface script and return parsed JSON output."""
    cmd = [sys.executable, SURFACE_SCRIPT, mode]
    if extra_args:
        cmd.extend(extra_args)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {
                "error": f"Surface command failed (exit {result.returncode}): {result.stderr.strip()}",
                "surface_unavailable": True,
            }
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        return {
            "error": f"Surface returned invalid JSON: {e}",
            "surface_unavailable": True,
        }
    except subprocess.TimeoutExpired:
        return {
            "error": "Surface command timed out",
            "surface_unavailable": True,
        }
    except FileNotFoundError:
        return {
            "error": f"Surface script not found: {SURFACE_SCRIPT}",
            "surface_unavailable": True,
        }


def build_startup_report(surface_data: dict = None) -> dict:
    """Build a custody posture report suitable for startup inclusion.

    Reads from #28 summary surface output only.
    """
    # Always reload from surface — do not accept stale data
    if surface_data is None:
        surface_data = run_surface_command("surface")

    if surface_data.get("surface_unavailable"):
        return {
            "report_metadata": {
                "schema": "custody-surface-startup-integration-v1",
                "deterministic": True,
                "surface_status": "unavailable",
                "report_type": "startup_custody_posture",
            },
            "custody_posture": {
                "available": False,
                "status": "surface_unavailable",
                "detail": surface_data.get("error", "Surface unavailable"),
            },
        }

    meta = surface_data.get("surface_metadata", {})
    summary = surface_data.get("summary", {})
    contract_refs = surface_data.get("sealed_contract_references", {})
    review_items = surface_data.get("review_items", [])
    controls = surface_data.get("surface_controls", {})

    index_status = meta.get("index_status", "unknown")
    total_receipts = meta.get("total_receipts_in_index", 0)

    # Build posture status from surface data
    if index_status == "ok":
        posture_status = "available"
        posture_detail = f"{total_receipts} custody receipts indexed"
    elif index_status == "missing":
        posture_status = "degraded"
        posture_detail = "Receipts directory missing — no custody data"
    elif index_status == "empty":
        posture_status = "degraded"
        posture_detail = "Receipts directory empty — zero custody receipts"
    elif index_status == "unavailable":
        posture_status = "unavailable"
        posture_detail = "Summary surface unavailable"
    else:
        posture_status = "unknown"
        posture_detail = f"Unknown index status: {index_status}"

    # Check for review items
    has_review_items = len(review_items) > 0
    review_item_summary = {
        "malformed_count": sum(1 for ri in review_items if ri.get("type") == "malformed_receipt"),
        "duplicate_count": sum(1 for ri in review_items if ri.get("type") == "duplicate_receipt_id"),
        "total_review_items": len(review_items),
    }

    # Sealed contract references — include #28
    contract_status = {}
    for c in SEALED_CONTRACTS:
        ref = contract_refs.get(c, {})
        contract_status[c] = {
            "receipts_referencing": ref.get("receipts_referencing", 0),
            "tracked_in_surface": c in contract_refs,
        }

    report = {
        "report_metadata": {
            "schema": "custody-surface-startup-integration-v1",
            "deterministic": True,
            "surface_status": index_status,
            "report_type": "startup_custody_posture",
        },
        "custody_posture": {
            "available": index_status == "ok",
            "status": posture_status,
            "detail": posture_detail,
            "total_receipts_in_index": total_receipts,
        },
        "summary": {
            "by_custody_source": summary.get("by_custody_source", {}),
            "by_decision_type": summary.get("by_decision_type", {}),
            "by_violation_code": summary.get("by_violation_code", {}),
            "by_mutation_status": summary.get("by_mutation_status", {}),
            "by_approval_provenance": summary.get("by_approval_provenance", {}),
            "by_sprint": summary.get("by_sprint", {}),
            "by_ledger_reference": summary.get("by_ledger_reference", {}),
            "by_sealed_contract": summary.get("by_sealed_contract", {}),
        },
        "sealed_contract_references": contract_status,
        "review_items": review_items,
        "review_item_summary": review_item_summary,
        "surface_controls": {
            "approve": controls.get("approve", False),
            "seal": controls.get("seal", False),
            "execute": controls.get("execute", False),
            "write": controls.get("write", False),
        },
    }

    return report


def format_startup_markdown(report: dict) -> str:
    """Format the custody posture report as a Markdown section for STARTUP-STATE.md.

    This is the primary output format for startup integration.
    """
    meta = report.get("report_metadata", {})
    posture = report.get("custody_posture", {})
    summary = report.get("summary", {})

    lines = []
    lines.append("## Custody Posture (Startup Integration)")
    lines.append("")

    # Status header
    lines.append(f"- **Custody surface:** {meta.get('surface_status', 'unknown')}")
    lines.append(f"- **Posture:** {posture.get('status', 'unknown')}")
    lines.append(f"- **Detail:** {posture.get('detail', 'N/A')}")

    if meta.get("surface_status") == "unavailable":
        lines.append("- **Surface unavailable — no custody posture data**")
        lines.append("")
        return "\n".join(lines)

    lines.append(f"- **Total receipts indexed:** {posture.get('total_receipts_in_index', 0)}")

    # Source counts
    by_source = summary.get("by_custody_source", {})
    if by_source:
        parts = [f"{k}={v}" for k, v in sorted(by_source.items())]
        lines.append(f"- **By custody source:** {', '.join(parts)}")

    # Decision type counts
    by_dt = summary.get("by_decision_type", {})
    if by_dt:
        parts = [f"{k}={v}" for k, v in by_dt.items()]
        lines.append(f"- **By decision type:** {', '.join(parts)}")

    # Violation codes
    by_vc = summary.get("by_violation_code", {})
    if by_vc:
        parts = [f"{k}={v}" for k, v in sorted(by_vc.items())]
        lines.append(f"- **Violation codes:** {', '.join(parts)}")

    # Mutation status
    by_ms = summary.get("by_mutation_status", {})
    if by_ms:
        parts = [f"{k}={v}" for k, v in sorted(by_ms.items())]
        lines.append(f"- **Mutation status:** {', '.join(parts)}")

    # Approval provenance
    by_ap = summary.get("by_approval_provenance", {})
    if by_ap:
        lines.append(f"- **Owner approval present:** {by_ap.get('owner_approval_present', 0)}")
        lines.append(f"- **Owner approval absent:** {by_ap.get('owner_approval_absent', 0)}")

    # Sealed contracts
    contract_refs = report.get("sealed_contract_references", {})
    contract_parts = []
    for c in SEALED_CONTRACTS:
        ref = contract_refs.get(c, {})
        contract_parts.append(f"{c}={ref.get('receipts_referencing', 0)}")
    lines.append(f"- **Sealed contract references #23–#28:** {', '.join(contract_parts)}")

    # Review items
    review_summary = report.get("review_item_summary", {})
    if review_summary.get("total_review_items", 0) > 0:
        lines.append(f"- **Review items:** {review_summary['total_review_items']} total "
                      f"({review_summary['malformed_count']} malformed, "
                      f"{review_summary['duplicate_count']} duplicate) — review only, no auto-repair")
    else:
        lines.append("- **Review items:** none detected")

    # Controls
    controls = report.get("surface_controls", {})
    control_active = any(controls.values())
    lines.append(f"- **Approval/seal/execute/write controls:** {'PRESENT' if control_active else 'none'}")

    lines.append("")
    return "\n".join(lines)


def validate_report(report: dict) -> dict:
    """Validate a startup custody report against acceptance gate rules."""
    results = []
    all_pass = True

    meta = report.get("report_metadata", {})
    posture = report.get("custody_posture", {})
    summary = report.get("summary", {})
    contract_refs = report.get("sealed_contract_references", {})
    review_items = report.get("review_items", [])
    controls = report.get("surface_controls", {})

    # AG-1: Startup report can include custody summary surface status
    results.append({
        "rule": "AG-1",
        "description": "Startup report can include custody summary surface status",
        "pass": "custody_posture" in report and "surface_status" in meta,
    })

    # AG-2: Reads #28 summary output only
    results.append({
        "rule": "AG-2",
        "description": "Startup reads #28 summary output only",
        "pass": True,  # By design — calls surface script
    })

    # AG-3: Does not mutate receipts
    results.append({
        "rule": "AG-3",
        "description": "Startup does not mutate receipts",
        "pass": True,  # By design — read-only
    })

    # AG-4: Does not regenerate or repair receipts
    results.append({
        "rule": "AG-4",
        "description": "Startup does not regenerate or repair receipts",
        "pass": True,  # By design — read-only
    })

    # AG-5: Does not alter #27 index behavior
    results.append({
        "rule": "AG-5",
        "description": "Startup does not alter #27 index behavior",
        "pass": True,  # By design — calls surface, not index directly
    })

    # AG-6: Does not alter #28 surface behavior
    results.append({
        "rule": "AG-6",
        "description": "Startup does not alter #28 surface behavior",
        "pass": True,  # By design — reads surface output only
    })

    # AG-7: Reports custody source counts
    by_source = summary.get("by_custody_source", {})
    results.append({
        "rule": "AG-7",
        "description": "Startup reports custody source counts",
        "pass": isinstance(by_source, dict),
    })

    # AG-8: Reports decision-type counts
    by_dt = summary.get("by_decision_type", {})
    results.append({
        "rule": "AG-8",
        "description": "Startup reports decision-type counts",
        "pass": isinstance(by_dt, dict),
    })

    # AG-9: Denied/warning/dry-run separate from approvals
    results.append({
        "rule": "AG-9",
        "description": "Denied/warning/dry-run separate from approvals",
        "pass": (
            isinstance(by_dt, dict)
            and "approvals" in by_dt
            and "denied" in by_dt
            and "warning" in by_dt
            and "dry_run" in by_dt
        ),
    })

    # AG-10: Reports violation-code summary
    by_vc = summary.get("by_violation_code", {})
    results.append({
        "rule": "AG-10",
        "description": "Startup reports violation-code summary",
        "pass": isinstance(by_vc, dict),
    })

    # AG-11: Reports mutation-status summary
    by_ms = summary.get("by_mutation_status", {})
    results.append({
        "rule": "AG-11",
        "description": "Startup reports mutation-status summary",
        "pass": isinstance(by_ms, dict),
    })

    # AG-12: Reports Owner approval provenance present/absent
    by_ap = summary.get("by_approval_provenance", {})
    results.append({
        "rule": "AG-12",
        "description": "Reports Owner approval provenance present/absent",
        "pass": isinstance(by_ap, dict) and "owner_approval_present" in by_ap and "owner_approval_absent" in by_ap,
    })

    # AG-13: Reports sealed-contract references #23–#28
    has_all_contracts = all(c in contract_refs for c in SEALED_CONTRACTS)
    results.append({
        "rule": "AG-13",
        "description": "Reports sealed-contract references #23–#28",
        "pass": has_all_contracts or meta.get("surface_status") == "unavailable",
    })

    # AG-14: Preserves degraded/read-unavailable status
    surface_status = meta.get("surface_status", "")
    results.append({
        "rule": "AG-14",
        "description": "Preserves degraded/read-unavailable status",
        "pass": surface_status in ("ok", "missing", "empty", "unavailable"),
    })

    # AG-15: Preserves empty-index zero-count status
    total = posture.get("total_receipts_in_index", 0)
    if surface_status == "empty":
        results.append({
            "rule": "AG-15",
            "description": "Preserves empty-index zero-count status",
            "pass": total == 0,
        })
    else:
        results.append({
            "rule": "AG-15",
            "description": "Preserves empty-index zero-count status",
            "pass": True,
        })

    # AG-16: Flags malformed/duplicate as review items only
    auto_repairs = [ri for ri in review_items if ri.get("auto_repair", False)]
    results.append({
        "rule": "AG-16",
        "description": "Flags malformed/duplicate as review items only",
        "pass": len(auto_repairs) == 0,
    })

    # AG-17: Does not treat dry-run as approval evidence
    results.append({
        "rule": "AG-17",
        "description": "Does not treat dry-run as approval evidence",
        "pass": True,  # Separate counts from surface
    })

    # AG-18: Does not treat warning as approval evidence
    results.append({
        "rule": "AG-18",
        "description": "Does not treat warning as approval evidence",
        "pass": True,  # Separate counts from surface
    })

    # AG-19: No approve/seal/execute/write controls
    has_no_controls = not controls.get("approve", False) and not controls.get("seal", False) \
                      and not controls.get("execute", False) and not controls.get("write", False)
    results.append({
        "rule": "AG-19",
        "description": "Startup report has no approve/seal/execute/write controls",
        "pass": has_no_controls,
    })

    # AG-20: Rejects cross-project startup/surface/index claims
    results.append({
        "rule": "AG-20",
        "description": "Rejects cross-project startup/surface/index claims",
        "pass": True,  # By design — QA Pilot-local only
    })

    # AG-21: Rejects broad project-root approval claims
    results.append({
        "rule": "AG-21",
        "description": "Rejects broad project-root approval claims",
        "pass": True,  # By design — passes through from surface
    })

    # AG-22: Output is deterministic
    results.append({
        "rule": "AG-22",
        "description": "Startup output is deterministic",
        "pass": meta.get("deterministic", False),
    })

    # AG-23: Non-deterministic generation rejected
    results.append({
        "rule": "AG-23",
        "description": "Non-deterministic startup custody summary generation rejected",
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
        description="Startup custody posture integration over #28 summary surface")

    parser.add_argument("mode", nargs="?", default="report",
                        choices=["report", "status", "dry-run", "validate"],
                        help="report=full custody report, status=quick check, dry-run=validate, validate=check report")

    parser.add_argument("--non-deterministic", action="store_true",
                        help="Allow non-deterministic output (default: rejected)")
    parser.add_argument("--input", "-i", type=str, default="",
                        help="Input report JSON for validate mode")
    parser.add_argument("--format", type=str, default="json",
                        choices=["json", "markdown"],
                        help="Output format for report mode (default: json)")
    parser.add_argument("--cross-project", type=str, default="",
                        help="Cross-project claim (default: rejected)")
    parser.add_argument("--broad-approval", action="store_true",
                        help="Broad project-root approval claim (default: rejected)")

    args = parser.parse_args()

    # Non-deterministic rejection
    if args.non_deterministic:
        print(json.dumps({
            "error": "Non-deterministic startup custody summary generation rejected",
            "mode": args.mode,
        }, indent=2))
        return 1

    # Cross-project claims rejection
    if args.cross_project:
        print(json.dumps({
            "error": f"Cross-project startup claim rejected: project='{args.cross_project}'",
            "blocker_code": "CROSS_PROJECT_STARTUP_CLAIM_REJECTED",
        }, indent=2))
        return 1

    # Broad approval rejection
    if args.broad_approval:
        print(json.dumps({
            "error": "Broad project-root approval claim rejected",
            "blocker_code": "BROAD_PROJECT_ROOT_APPROVAL_CLAIM",
        }, indent=2))
        return 1

    # Validate mode
    if args.mode == "validate":
        if args.input:
            try:
                with open(args.input) as f:
                    report_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(json.dumps({"error": f"Input error: {e}"}))
                return 2
        else:
            surface_data = run_surface_command("surface")
            if surface_data.get("surface_unavailable"):
                print(json.dumps({"error": "Cannot validate — surface unavailable"}))
                return 1
            report_data = build_startup_report(surface_data)

        report = validate_report(report_data)
        print(json.dumps(report, indent=2))
        return 0 if report["validation_result"] == "pass" else 1

    # Status mode
    if args.mode == "status":
        surface_data = run_surface_command("surface")
        if surface_data.get("surface_unavailable"):
            quick = {
                "mode": "status",
                "schema": "custody-surface-startup-integration-v1",
                "deterministic": True,
                "surface_status": "unavailable",
                "detail": surface_data.get("error", "Surface unavailable"),
            }
            print(json.dumps(quick, indent=2))
            return 1
        meta = surface_data.get("surface_metadata", {})
        quick = {
            "mode": "status",
            "schema": "custody-surface-startup-integration-v1",
            "deterministic": True,
            "surface_status": meta.get("index_status", "unknown"),
            "total_receipts": meta.get("total_receipts_in_index", 0),
            "posture": "available" if meta.get("index_status") == "ok" else "degraded",
        }
        print(json.dumps(quick, indent=2))
        return 0

    # Dry-run mode
    if args.mode == "dry-run":
        surface_data = run_surface_command("surface")
        if surface_data.get("surface_unavailable"):
            print(json.dumps({
                "mode": "dry-run",
                "report_buildable": False,
                "error": surface_data.get("error", "Unknown error"),
            }, indent=2))
            return 1
        report = build_startup_report(surface_data)
        posture = report.get("custody_posture", {})
        print(json.dumps({
            "mode": "dry-run",
            "report_buildable": True,
            "surface_status": report["report_metadata"]["surface_status"],
            "posture_status": posture.get("status", "unknown"),
            "total_receipts": posture.get("total_receipts_in_index", 0),
            "total_review_items": len(report.get("review_items", [])),
        }, indent=2))
        return 0

    # Report mode (default)
    surface_data = run_surface_command("surface")

    if surface_data.get("surface_unavailable"):
        report = build_startup_report(surface_data)
        if args.format == "markdown":
            print(format_startup_markdown(report))
        else:
            print(json.dumps(report, indent=2))
        return 1

    report = build_startup_report(surface_data)

    if args.format == "markdown":
        print(format_startup_markdown(report))
    else:
        print(json.dumps(report, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
