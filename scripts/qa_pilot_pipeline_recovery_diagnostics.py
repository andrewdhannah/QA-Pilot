#!/usr/bin/env python3
"""
QA Pilot Pipeline Recovery Diagnostics — QA-PILOT-PIPELINE-RECOVERY-DIAGNOSTICS-1

Advisory-only recovery diagnostics for QA Pilot pipeline drift.
Classifies drift failures by affected layer, identifies likely cause, and
presents bounded Owner-facing recovery options.

Does NOT auto-repair. Does NOT mutate canonical state.

Usage:
    python3 scripts/qa_pilot_pipeline_recovery_diagnostics.py
    python3 scripts/qa_pilot_pipeline_recovery_diagnostics.py --report
    python3 scripts/qa_pilot_pipeline_recovery_diagnostics.py --fixture <path>
"""

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DRIFT_DETECTOR = SCRIPT_DIR / "validate-qa-pilot-pipeline-drift-detection.py"
PH_VALIDATOR = SCRIPT_DIR / "validate-qa-pilot-pipeline-health-regression.py"
SURFACE_SCRIPT = SCRIPT_DIR / "qa_pilot_pipeline_startup_surface.py"
SPRINT_LEDGER = REPO_ROOT / "project-state" / "sprint-ledger.json"
PROFILE = REPO_ROOT / "PROJECT-PROFILE.json"

ADVISORY_NOTICE = (
    "This diagnostic report is advisory-only. It does not approve, seal, merge, "
    "or assert production readiness. Recovery options are Owner-suggested actions, "
    "not automated repair commands."
)

# ── Layer definitions ─────────────────────────────────────────────────────────

PIPELINE_LAYERS = {
    "EP": {"sprint": "#33 QA-PILOT-MCP-EVIDENCE-INTAKE-1", "prefix": "EP-", "store": "data/evidence/"},
    "TC": {"sprint": "#34 QA-PILOT-TEST-COMPOSITION-1", "prefix": "TC-", "store": "data/test-cases/"},
    "QR": {"sprint": "#35 QA-PILOT-RESULT-PACKET-EXPORT-1", "prefix": "QR-", "store": "data/result-packets/"},
    "ERS": {"sprint": "#36 QA-PILOT-EPIC-REGRESSION-BUILDER-1", "prefix": "ERS-", "store": "data/epic-regression/"},
    "STARTUP": {"sprint": "#37 QA-PILOT-EPIC-REGRESSION-STARTUP-SURFACE-1", "prefix": None, "store": None},
    "PH": {"sprint": "#38 QA-PILOT-PIPELINE-HEALTH-REGRESSION-1", "prefix": None, "store": None},
    "DR": {"sprint": "#39 QA-PILOT-PIPELINE-DRIFT-DETECTION-1", "prefix": None, "store": None},
}

# ── Drift classification ────────────────────────────────────────────────────

DR_CHECK_MAP = {
    "DR-1": {"layers": ["STARTUP", "LEDGER"], "cause": "stale_surface_or_ledger_mismatch",
             "desc": "Sealed head mismatch between startup surface and sprint ledger"},
    "DR-2": {"layers": ["STARTUP", "LEDGER", "PH"], "cause": "active_sprint_mismatch",
             "desc": "Active sprint differs across ledger, profile, and/or status surface"},
    "DR-3": {"layers": ["EP", "TC", "QR", "ERS", "STARTUP", "PH", "DR"], "cause": "missing_layer",
             "desc": "One or more sealed pipeline layers (#33-#39) are missing from the ledger"},
    "DR-4": {"layers": ["LEDGER"], "cause": "unexpected_extra_layer",
             "desc": "An unexpected sealed sprint exists outside the known pipeline layers"},
    "DR-5": {"layers": ["EP", "TC", "QR", "ERS"], "cause": "store_index_mismatch",
             "desc": "One or more data stores (EP/TC/QR/ERS) report inconsistent counts"},
    "DR-6": {"layers": ["STARTUP"], "cause": "stale_surface",
             "desc": "Startup surface output is stale (>5 minutes old)"},
    "DR-7": {"layers": ["PH"], "cause": "ph_validator_disagreement",
             "desc": "Pipeline health (PH) validator disagrees with current pipeline state"},
    "DR-8": {"layers": ["LEDGER", "PROFILE"], "cause": "boundary_field_mutation",
             "desc": "Posture, custody, or mutation boundary fields have changed"},
    "DR-9": {"layers": ["STARTUP"], "cause": "authority_claim_detected",
             "desc": "Authority, promotion, seal, or canonical-truth claims detected in surface"},
    "DR-10": {"layers": ["DR"], "cause": "bounded_report_violation",
              "desc": "Drift report itself is unbounded or improperly structured"},
}


def recovery_options(layers, cause, desc):
    """Generate Owner-facing advisory recovery options for a drift."""
    options = []
    all_options = {
        "stale_surface_or_ledger_mismatch": [
            "Regenerate the startup surface: python3 scripts/qa_pilot_pipeline_startup_surface.py report --format json",
            "Verify sealed head in sprint ledger: project-state/sprint-ledger.json",
            "If sealed head is incorrect, re-seal the correct sprint with: seal qa-pilot sprint <SPRINT-ID>",
        ],
        "active_sprint_mismatch": [
            "Check PROJECT-PROFILE.json active_sprint field and FEATURE-STATUS.md active_sprint entry",
            "If a sprint is in progress, set active_sprint to its ID in PROJECT-PROFILE.json",
            "If no sprint is active, set active_sprint to null in PROJECT-PROFILE.json",
        ],
        "missing_layer": [
            f"Verify the sprint ID exists in project-state/sprint-ledger.json",
            "If the sprint was sealed in a different session, the ledger may need re-indexing",
            "Re-seal the affected layer: seal qa-pilot sprint <SPRINT-ID>",
        ],
        "unexpected_extra_layer": [
            "Review the sealed sprint in project-state/sprint-ledger.json",
            "If it is a legitimate pipeline layer, update EXPECTED_LAYERS in the PH validator",
            "If it is an error, the sprint can be unsealed only by Owner action",
        ],
        "store_index_mismatch": [
            f"Check the affected data store index for corruption",
            "Run the layer's status command to verify: python3 scripts/qa_pilot_<layer>_*.py status",
            "If index is corrupted, clear and re-import data (Owner decision required)",
        ],
        "stale_surface": [
            "Refresh the startup surface: python3 scripts/qa_pilot_pipeline_startup_surface.py report --format json",
            "The surface regenerates on each call — staleness is expected between calls",
        ],
        "ph_validator_disagreement": [
            "Run PH validator diagnostics: python3 scripts/validate-qa-pilot-pipeline-health-regression.py",
            "If PH rules are stale due to pipeline expansion, update EXPECTED_LAYERS in the validator",
            "If a layer is missing, re-seal it with: seal qa-pilot sprint <SPRINT-ID>",
        ],
        "boundary_field_mutation": [
            "Check PROJECT-PROFILE.json sandbox_boundary and active_sprint fields",
            "Verify that sandbox_boundary remains 'harness_governed'",
            "Verify that active_sprint is null after seal, or set to the active sprint ID",
        ],
        "authority_claim_detected": [
            "Review the startup surface output for forbidden authority language",
            "Check if advisory notices were overwritten with promotion/seal language",
            "Re-run report: python3 scripts/qa_pilot_pipeline_startup_surface.py report",
        ],
        "bounded_report_violation": [
            "Review the drift detection script output for malformed results",
            "Re-run: python3 scripts/validate-qa-pilot-pipeline-drift-detection.py",
        ],
    }
    base_opts = all_options.get(cause, ["Review the affected layer manually"])
    options.extend(base_opts)
    return options


# ── Diagnostics Core ──────────────────────────────────────────────────────────

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_cmd(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout, r.stderr, r.returncode)
    except Exception as e:
        return ("", str(e), -1)


def parse_drift_output(drift_stdout):
    """Parse drift detector output into structured findings."""
    findings = []

    for line in drift_stdout.splitlines():
        # Match: prefix DR-N: message
        for dr_id in DR_CHECK_MAP:
            if re.search(r'\b' + dr_id + r'\b', line):
                is_drift = "❌" in line
                info = DR_CHECK_MAP[dr_id]
                finding = {
                    "check": dr_id,
                    "drift": is_drift,
                    "affected_layers": info["layers"],
                    "cause": info["cause"],
                    "description": info["desc"],
                    "detail": line.split(dr_id + ":")[-1].strip() if ":" in line else "",
                }
                if is_drift:
                    finding["recovery_options"] = recovery_options(
                        info["layers"], info["cause"], info["desc"]
                    )
                findings.append(finding)
                break

    return findings


def build_diagnostics():
    """Build full recovery diagnostics from live pipeline state."""
    diagnostics = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "advisory": True,
        "advisory_notice": ADVISORY_NOTICE,
        "source_project": "qa-pilot",
        "custody": "qa-pilot-local",
        "pipeline_layers": {k: v["sprint"] for k, v in PIPELINE_LAYERS.items()},
        "findings": [],
        "summary": {"total_checks": 0, "drifts": 0, "layers_affected": []},
    }

    # Run drift detector
    drift_out, drift_err, drift_rc = run_cmd([sys.executable, str(DRIFT_DETECTOR)])
    findings = parse_drift_output(drift_out)

    # Also run PH validator for additional context
    ph_out, ph_err, ph_rc = run_cmd([sys.executable, str(PH_VALIDATOR)])
    ph_pass = "ALL PIPELINE HEALTH CHECKS PASS" in ph_out

    diagnostics["findings"] = findings
    diagnostics["ph_validator_pass"] = ph_pass
    diagnostics["ph_validator_output"] = ph_out[:500] if ph_out else ""

    # Build summary
    total_checks = len([f for f in findings])
    drifts = [f for f in findings if f["drift"]]
    affected = set()
    for d in drifts:
        for l in d.get("affected_layers", []):
            affected.add(l)
    diagnostics["summary"] = {
        "total_checks": total_checks,
        "drifts": len(drifts),
        "layers_affected": sorted(affected),
        "ph_validator": "pass" if ph_pass else "fail",
    }

    # Build recovery summary
    if drifts:
        recovery_steps = []
        for d in drifts:
            for opt in d.get("recovery_options", []):
                if opt not in recovery_steps:
                    recovery_steps.append(opt)
        diagnostics["recovery_summary"] = {
            "note": "Recovery options are advisory-only. Do not auto-execute. Owner review required.",
            "steps": recovery_steps[:8],  # bounded
        }
    else:
        diagnostics["recovery_summary"] = {
            "note": "No drift detected — no recovery action needed.",
            "steps": [],
        }

    return diagnostics


# ── Report Formatting ─────────────────────────────────────────────────────────

def format_diagnostics(diag):
    """Format diagnostics as a human-readable advisory report."""
    lines = []
    lines.append("QA Pilot Pipeline Recovery Diagnostics")
    lines.append("=" * 55)
    lines.append(f"Generated: {diag.get('timestamp', 'unknown')}")
    lines.append(f"Advisory:  True")
    lines.append(f"Custody:   {diag.get('custody', 'qa-pilot-local')}")
    lines.append("")

    lines.append("Pipeline Layers")
    lines.append("-" * 55)
    for k, v in diag.get("pipeline_layers", {}).items():
        lines.append(f"  {k:8s}  {v}")
    lines.append("")

    s = diag.get("summary", {})
    lines.append(f"Drift Summary: {s.get('drifts', 0)} drifts in {s.get('total_checks', 0)} checks")
    lines.append(f"PH Validator:  {s.get('ph_validator', 'unknown')}")
    affected = s.get("layers_affected", [])
    if affected:
        lines.append(f"Affected:      {', '.join(affected)}")
    lines.append("")

    findings = diag.get("findings", [])
    drifts = [f for f in findings if f["drift"]]
    if drifts:
        lines.append("Drift Findings")
        lines.append("-" * 55)
        for d in drifts:
            status = "❌ DRIFT"
            lines.append(f"  {status}  {d['check']}: {d['description']}")
            lines.append(f"         Cause: {d['cause']}")
            lines.append(f"         Layers: {', '.join(d['affected_layers'])}")
            lines.append(f"         Detail: {d['detail']}")
            ropts = d.get("recovery_options", [])
            if ropts:
                lines.append(f"         Recovery options (advisory):")
                for r in ropts:
                    lines.append(f"           • {r}")
            lines.append("")

    recovery = diag.get("recovery_summary", {})
    lines.append("Recovery Summary")
    lines.append("-" * 55)
    lines.append(f"  {recovery.get('note', '')}")
    for step in recovery.get("steps", []):
        lines.append(f"  • {step}")
    lines.append("")

    lines.append(ADVISORY_NOTICE)
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def cmd_diagnose(report_mode):
    """Run diagnostics and output."""
    diag = build_diagnostics()
    if report_mode:
        print(format_diagnostics(diag))
    else:
        print(json.dumps(diag, indent=2))
    return 0


# ── Fixture validation mode ──────────────────────────────────────────────────

def validate_fixture(data):
    """Validate a fixture against diagnostic rules."""
    checks = []

    checks.append(("RD-FIX-1", data.get("advisory") is not False,
                   f"advisory = {data.get('advisory')}"))

    custody = data.get("custody", "qa-pilot-local")
    checks.append(("RD-FIX-2", custody == "qa-pilot-local",
                   f"custody = {custody}"))

    if data.get("has_recovery_options", False):
        recovery = data.get("recovery_summary", {})
        has_steps = bool(recovery.get("steps"))
        checks.append(("RD-FIX-RECOVERY", has_steps,
                       "Has recovery steps" if has_steps else "Missing recovery steps"))
        if recovery.get("steps"):
            advisory_note = recovery.get("note", "")
            checks.append(("RD-FIX-ADVISORY", "advisory" in advisory_note.lower() or "owner" in advisory_note.lower(),
                           "Recovery marked advisory" if "advisory" in advisory_note.lower() else "Advisory note present"))
    else:
        checks.append(("RD-FIX-RECOVERY", True, "No recovery options (no drift)"))

    # Check for authority claim
    if "_authority_claim" in data:
        checks.append(("RD-AUTH", False, "Contains _authority_claim"))
    else:
        checks.append(("RD-AUTH", True, "No authority claim"))

    # Auto-repair check
    if data.get("auto_repair", False):
        checks.append(("RD-REPAIR", False, "Auto-repair is enabled (must be false)"))
    else:
        checks.append(("RD-REPAIR", True, "No auto-repair"))

    all_pass = all(c[1] for c in checks)
    return (all_pass, checks)


# ── CLI ─────────────────────────────────────────────────────────────────────

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

    report_mode = "--report" in args
    return cmd_diagnose(report_mode)


if __name__ == "__main__":
    sys.exit(main())
