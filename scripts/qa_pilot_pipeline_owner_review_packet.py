#!/usr/bin/env python3
"""
QA Pilot Pipeline Owner Review Packet — QA-PILOT-PIPELINE-OWNER-REVIEW-PACKET-1

Consolidates QA Pilot pipeline health, drift state, and recovery diagnostics into
a single bounded Owner-facing review artifact. Advisory-only. No action authority.

Usage:
    python3 scripts/qa_pilot_pipeline_owner_review_packet.py         # JSON output
    python3 scripts/qa_pilot_pipeline_owner_review_packet.py --report  # formatted
    python3 scripts/qa_pilot_pipeline_owner_review_packet.py --fixture <path>
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SURFACE_SCRIPT = SCRIPT_DIR / "qa_pilot_pipeline_startup_surface.py"
PH_VALIDATOR = SCRIPT_DIR / "validate-qa-pilot-pipeline-health-regression.py"
DR_DETECTOR = SCRIPT_DIR / "validate-qa-pilot-pipeline-drift-detection.py"
RD_DIAG = SCRIPT_DIR / "qa_pilot_pipeline_recovery_diagnostics.py"
SPRINT_LEDGER = REPO_ROOT / "project-state" / "sprint-ledger.json"
PROFILE = REPO_ROOT / "PROJECT-PROFILE.json"

ADVISORY_NOTICE = (
    "This Owner review packet is advisory-only. It does not approve, seal, merge, "
    "or assert production readiness. The Owner must decide on any action."
)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_cmd(cmd, timeout=20):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout, r.stderr, r.returncode)
    except Exception as e:
        return ("", str(e), -1)


def run_and_parse(cmd, json_key=None):
    """Run a command and parse JSON output. Returns dict or error dict."""
    out, err, rc = run_cmd(cmd)
    if not out:
        return {"error": err or "no output", "rc": rc}
    try:
        data = json.loads(out)
        if json_key and json_key in data:
            return data[json_key]
        return data
    except json.JSONDecodeError:
        return {"error": "parse failed", "raw": out[:200], "rc": rc}


def build_review_packet():
    """Consolidate all pipeline outputs into a single review packet."""
    packet = {
        "review_id": f"ORP-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "advisory": True,
        "advisory_notice": ADVISORY_NOTICE,
        "source_project": "qa-pilot",
        "custody": "qa-pilot-local",
        "librarian_mutation_authority": False,
        "sections": {},
        "owner_options": [],
        "summary": {},
    }

    # Section 1: Startup surface
    surface = run_and_parse(
        [sys.executable, str(SURFACE_SCRIPT), "report", "--format", "json"],
        json_key="pipeline"
    )
    packet["sections"]["startup_surface"] = {
        "status": "ok" if "sealed_head" in surface else "error",
        "sealed_head": surface.get("sealed_head", "unknown"),
        "active_sprint": surface.get("active_sprint", "none"),
        "pipeline_layers": len(surface.get("pipeline_layers", [])),
        "evidence_count": surface.get("evidence_count", 0),
        "test_case_count": surface.get("test_case_count", 0),
        "result_packet_count": surface.get("result_packet_count", 0),
        "epic_suite_count": surface.get("epic_suite_count", 0),
        "advisory": surface.get("advisory", False),
    }

    # Section 2: PH validator
    ph_out, _, ph_rc = run_cmd([sys.executable, str(PH_VALIDATOR)])
    ph_pass = "ALL PIPELINE HEALTH CHECKS PASS" in ph_out
    ph_lines = [l for l in ph_out.splitlines() if "✅" in l or "❌" in l]
    packet["sections"]["pipeline_health"] = {
        "status": "pass" if ph_pass else "fail",
        "checks_passed": sum(1 for l in ph_lines if "✅" in l),
        "checks_failed": sum(1 for l in ph_lines if "❌" in l),
        "total_checks": len(ph_lines),
    }

    # Section 3: Drift detection
    dr_out, _, dr_rc = run_cmd([sys.executable, str(DR_DETECTOR)])
    dr_drift_count = 0
    dr_lines = [l for l in dr_out.splitlines() if "✅" in l or "❌" in l]
    for l in dr_lines:
        if "❌" in l:
            dr_drift_count += 1
    packet["sections"]["drift_detection"] = {
        "status": "pass" if dr_drift_count == 0 else "drift_detected",
        "drifts": dr_drift_count,
        "total_checks": len(dr_lines),
    }

    # Section 4: Recovery diagnostics
    rd_data = run_and_parse([sys.executable, str(RD_DIAG)])
    rd_summary = rd_data.get("summary", {})
    rd_findings = rd_data.get("findings", [])
    packet["sections"]["recovery_diagnostics"] = {
        "status": "ok" if rd_summary.get("drifts", -1) >= 0 else "error",
        "drifts": rd_summary.get("drifts", 0),
        "ph_validator": rd_summary.get("ph_validator", "unknown"),
        "layers_affected": rd_summary.get("layers_affected", []),
        "recovery_steps": len(rd_data.get("recovery_summary", {}).get("steps", [])),
        "pipeline_layers": len(rd_data.get("pipeline_layers", {})),
    }

    # Section 5: Ledger summary
    if SPRINT_LEDGER.exists():
        try:
            ledger = load_json(str(SPRINT_LEDGER))
            sealed = [s for s in ledger.get("sprints", []) if s.get("status") == "sealed"]
            pending = [s for s in ledger.get("sprints", []) if s.get("status") == "pending_owner_review"]
            packet["sections"]["ledger"] = {
                "status": "ok",
                "total_sprints": len(ledger.get("sprints", [])),
                "total_sealed": len(sealed),
                "pending_review": len(pending),
                "last_sealed": max((s.get("sealed_number", 0) for s in sealed), default=0),
            }
        except Exception as e:
            packet["sections"]["ledger"] = {"status": "error", "detail": str(e)}

    # Owner options
    all_pass = all(
        s.get("status") in ("pass", "ok") for s in packet["sections"].values()
    )
    drifts_found = any(
        s.get("drifts", 0) > 0 for s in packet["sections"].values()
    )
    pending_review = packet.get("sections", {}).get("ledger", {}).get("pending_review", 0) > 0

    options = []
    if all_pass and not drifts_found:
        options.append({
            "id": "review_accept",
            "label": "Accept pipeline state",
            "description": "All checks pass, no drift detected. Pipeline is healthy.",
            "action": "none required",
        })
    if drifts_found:
        options.append({
            "id": "review_diagnostics",
            "label": "Review drift diagnostics",
            "description": "Review the drift and recovery diagnostic outputs before deciding.",
            "action": "python3 scripts/qa_pilot_pipeline_recovery_diagnostics.py --report",
        })
    options.append({
        "id": "review_authorize",
        "label": "Authorize a repair sprint",
        "description": "If drift is unacceptable, authorize a new QA Pilot sprint to repair it.",
        "action": "I authorize QA Pilot sprint QA-PILOT-PIPELINE-REPAIR-1.",
    })
    options.append({
        "id": "review_defer",
        "label": "Defer action",
        "description": "Pipeline state is advisory. Drifts can be addressed in a future sprint.",
        "action": "none required",
    })
    options.append({
        "id": "review_reject",
        "label": "Reject current state",
        "description": "If pipeline state is unrecoverable, reset affected layers.",
        "action": "Owner must manually reset affected layers in the sprint ledger.",
    })
    packet["owner_options"] = options

    # Summary
    packet["summary"] = {
        "all_sections_pass": all_pass,
        "drifts_detected": drifts_found,
        "pending_review": pending_review,
        "advisory": True,
        "owner_action_required": drifts_found or pending_review,
    }

    return packet


def format_report(packet):
    """Format as human-readable Owner review."""
    lines = []
    lines.append("QA Pilot Pipeline Owner Review Packet")
    lines.append("=" * 55)
    lines.append(f"Review ID:  {packet.get('review_id', 'unknown')}")
    lines.append(f"Generated:  {packet.get('timestamp', 'unknown')}")
    lines.append(f"Advisory:   True")
    lines.append(f"Custody:    {packet.get('custody', 'qa-pilot-local')}")
    lines.append(f"Mutation:   NONE")
    lines.append("")

    sections = packet.get("sections", {})
    for name, data in sections.items():
        status = data.get("status", "unknown")
        icon = "✅" if status in ("pass", "ok") else "❌"
        lines.append(f"  {icon} {name.replace('_', ' ').title()}")
        for k, v in data.items():
            if k != "status":
                lines.append(f"       {k}: {v}")
        lines.append("")

    options = packet.get("owner_options", [])
    lines.append("Owner Options")
    lines.append("-" * 55)
    for opt in options:
        lines.append(f"  [{opt['id']}]")
        lines.append(f"       {opt['label']}")
        lines.append(f"       {opt['description']}")
        lines.append(f"       Action: {opt['action']}")
        lines.append("")

    summary = packet.get("summary", {})
    lines.append("Summary")
    lines.append("-" * 55)
    for k, v in summary.items():
        lines.append(f"  {k}: {v}")
    lines.append("")
    lines.append(ADVISORY_NOTICE)
    return "\n".join(lines)


# ── Fixture validation ───────────────────────────────────────────────────────

def validate_fixture(data):
    checks = []
    checks.append(("OR-FIX-1", data.get("advisory") is not False, f"advisory = {data.get('advisory')}"))
    checks.append(("OR-FIX-2", data.get("custody") == "qa-pilot-local", f"custody = {data.get('custody')}"))
    checks.append(("OR-FIX-3", data.get("librarian_mutation_authority") is False, "no mutation"))
    checks.append(("OR-FIX-4", len(data.get("sections", {})) >= 4, f"{len(data.get('sections', {}))} sections"))
    checks.append(("OR-FIX-5", len(data.get("owner_options", [])) >= 3, f"{len(data.get('owner_options', []))} options"))
    if "_authority_claim" in data:
        checks.append(("OR-AUTH", False, "Contains _authority_claim"))
    else:
        checks.append(("OR-AUTH", True, "No authority claim"))
    if data.get("auto_repair", False):
        checks.append(("OR-REPAIR", False, "Auto-repair enabled"))
    else:
        checks.append(("OR-REPAIR", True, "No auto-repair"))
    all_pass = all(c[1] for c in checks)
    return (all_pass, checks)


def main():
    args = sys.argv[1:]

    if "--fixture" in args:
        idx = args.index("--fixture")
        if idx + 1 < len(args):
            fpath = args[idx + 1]
            try:
                data = load_json(fpath)
            except Exception as e:
                print(f"ERROR: {e}", file=sys.stderr)
                return 1
            valid, fchecks = validate_fixture(data)
            for cid, passed, msg in fchecks:
                prefix = "✅" if passed else "❌"
                print(f"  {prefix} {cid}: {msg}")
            print(f"\n{'✅ ALL FIXTURE CHECKS PASS' if valid else '❌ SOME CHECKS FAILED'}")
            return 0 if valid else 1

    packet = build_review_packet()
    if "--report" in args:
        print(format_report(packet))
    else:
        print(json.dumps(packet, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
