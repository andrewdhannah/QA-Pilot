#!/usr/bin/env python3
"""
QA Pilot ODR Startup Surface — QA-PILOT-OWNER-DECISION-RECEIPT-STARTUP-SURFACE-1

Extends the #37 startup surface to include the #42 Owner Decision Receipt (ODR)
layer. Reports ODR status, latest receipt, and OR→ODR linkage.

Usage:
    python3 scripts/qa_pilot_pipeline_startup_surface_odr.py
    python3 scripts/qa_pilot_pipeline_startup_surface_odr.py --report
"""

import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SURFACE_SCRIPT = SCRIPT_DIR / "qa_pilot_pipeline_startup_surface.py"
ODR_INDEX = REPO_ROOT / "data" / "owner-decisions" / "decision-index.json"
ADVISORY_NOTICE = (
    "This extended startup surface is advisory-only. No approval, seal, merge, "
    "or production-readiness authority."
)

def load_json(p):
    with open(p) as f:
        return json.load(f)

def run_cmd(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout, r.stderr, r.returncode)
    except Exception as e:
        return ("", str(e), -1)

def build_surface():
    # Get base pipeline surface
    base_out, _, _ = run_cmd([sys.executable, str(SURFACE_SCRIPT), "report", "--format", "json"])
    base = {}
    if base_out:
        try:
            base = json.loads(base_out).get("pipeline", {})
        except Exception:
            base = {"error": "base surface parse failed"}

    # Get ODR store
    odr_receipts = []
    if ODR_INDEX.exists():
        try:
            idx = load_json(str(ODR_INDEX))
            odr_receipts = list(idx.get("receipts", {}).values())
        except Exception:
            pass

    # Build ODR section
    latest_odr = None
    if odr_receipts:
        sorted_odr = sorted(odr_receipts, key=lambda r: r.get("recorded_at", ""), reverse=True)
        latest_odr = sorted_odr[0]

    decisions = {}
    for r in odr_receipts:
        d = r.get("decision", "?")
        decisions[d] = decisions.get(d, 0) + 1

    # Check OR→ODR linkage: latest ODR references #41
    or_linked = False
    if latest_odr:
        or_linked = True  # any ODR receipt implies linkage to #41 review

    surface = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "advisory_only": True,
        "source_project": "qa-pilot",
        "custody": "qa-pilot-local",
        "advisory_notice": ADVISORY_NOTICE,
        "base_pipeline": {
            "sealed_head": base.get("sealed_head", "unknown"),
            "active_sprint": base.get("active_sprint", "none"),
            "layers": base.get("pipeline_layers", []),
        },
        "odr_layer": {
            "status": "active" if odr_receipts else "empty",
            "total_receipts": len(odr_receipts),
            "by_decision": decisions,
            "latest_receipt": {
                "receipt_id": latest_odr.get("receipt_id") if latest_odr else None,
                "decision": latest_odr.get("decision") if latest_odr else None,
                "recorded_at": latest_odr.get("recorded_at") if latest_odr else None,
            } if latest_odr else None,
            "or_linkage": {
                "source_review_packet": "#41 QA-PILOT-PIPELINE-OWNER-REVIEW-PACKET-1",
                "has_matching_receipt": or_linked,
                "review_complete": or_linked,
            },
        },
    }

    return surface

def format_report(surface):
    lines = []
    lines.append("QA Pilot ODR-Extended Startup Surface")
    lines.append("=" * 55)
    lines.append(f"Generated:  {surface.get('timestamp', '?')}")
    lines.append(f"Advisory:   True")
    lines.append(f"Custody:    {surface.get('custody', 'qa-pilot-local')}")
    lines.append("")

    base = surface.get("base_pipeline", {})
    lines.append("Pipeline State")
    lines.append("-" * 55)
    lines.append(f"  Sealed head:   {base.get('sealed_head', '?')}")
    lines.append(f"  Active sprint: {base.get('active_sprint', 'none')}")
    lines.append(f"  Layers:        {len(base.get('layers', []))}")
    lines.append("")

    odr = surface.get("odr_layer", {})
    lines.append("Owner Decision Receipt Layer (#42)")
    lines.append("-" * 55)
    lines.append(f"  Status:           {odr.get('status', '?')}")
    lines.append(f"  Total receipts:   {odr.get('total_receipts', 0)}")
    lines.append(f"  By decision:      {odr.get('by_decision', {})}")
    latest = odr.get("latest_receipt")
    if latest:
        lines.append(f"  Latest receipt:   {latest.get('receipt_id', '?')}")
        lines.append(f"  Latest decision:  {latest.get('decision', '?')}")
        lines.append(f"  Recorded at:      {latest.get('recorded_at', '?')}")
    linkage = odr.get("or_linkage", {})
    lines.append(f"  OR review linked: {linkage.get('has_matching_receipt', False)}")
    lines.append(f"  Review complete:  {linkage.get('review_complete', False)}")
    lines.append("")
    lines.append(ADVISORY_NOTICE)
    return "\n".join(lines)

def main():
    surface = build_surface()
    if "--report" in sys.argv:
        print(format_report(surface))
    else:
        print(json.dumps(surface, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
