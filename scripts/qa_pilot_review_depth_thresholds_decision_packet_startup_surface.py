#!/usr/bin/env python3
"""
QA Pilot Review Depth Thresholds Decision Packet Startup Surface.

Exposes decision packet (#90) posture in the QA Pilot startup/status surface.
Reports packet count, latest packet, state, threshold/evidence bundle references.

Modes:
  report   — Generate full decision packet startup surface report (default)
  status   — Quick decision packet surface check
  validate — Validate a surface report against DP-SS acceptance rules

Boundary:
  This surface may display decision packet posture only. It does not create
  packets, make Owner decisions, accept/reject results, authorize execution,
  verify evidence, close reviews, mutate evidence/result packets, or create
  seal authority.

Usage:
  python3 scripts/qa_pilot_review_depth_thresholds_decision_packet_startup_surface.py report
  python3 scripts/qa_pilot_review_depth_thresholds_decision_packet_startup_surface.py status
  python3 scripts/qa_pilot_review_depth_thresholds_decision_packet_startup_surface.py validate
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DP_STORE_DIR = PROJECT_ROOT / "data" / "review-decision-packets"
DP_STORE_INDEX = DP_STORE_DIR / "packet-index.json"

ADVISORY_NOTICE = (
    "This startup surface reports decision packet posture only. It does not "
    "create packets, make Owner decisions, accept/reject results, authorize "
    "execution, verify evidence, close reviews, mutate evidence/result "
    "packets, or create seal authority."
)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def gather_dp_surface():
    """Gather decision packet posture from the packet store.

    Reads the decision packet index and latest packet records to report
    decision packet layer posture. Reports honest empty/absent state
    when no packets exist. Does not create, validate, or mutate packet
    records. Returns dict with packet presence, counts, latest details,
    and bounded advisory classification.
    """
    dp = {
        "packet_count": 0,
        "latest_packet_id": None,
        "latest_packet_state": None,
        "latest_threshold_id": None,
        "latest_threshold_state": None,
        "latest_evidence_bundle_ref": None,
        "latest_result_packet_ref": None,
        "latest_consistency_guard_refs": [],
        "latest_timestamp": None,
        "by_packet_state": {},
        "by_threshold_state": {},
        "dp_status": "absent",
        "classification": "unknown",
    }

    if not DP_STORE_INDEX.exists():
        dp["dp_status"] = "absent"
        dp["classification"] = "unknown"
        return dp

    try:
        index = load_json(str(DP_STORE_INDEX))
        records = index.get("records", [])
        if not records:
            dp["dp_status"] = "empty"
            dp["classification"] = "unknown"
            return dp

        dp["packet_count"] = len(records)

        # Load latest packet (last record in index)
        latest_id = records[-1]
        latest_path = DP_STORE_DIR / f"{latest_id}.json"
        if latest_path.exists():
            latest = load_json(str(latest_path))
            dp["latest_packet_id"] = latest.get("packet_id")
            dp["latest_packet_state"] = latest.get("packet_state")
            dp["latest_threshold_id"] = latest.get("source_threshold_id")
            dp["latest_threshold_state"] = latest.get("threshold_state")
            dp["latest_evidence_bundle_ref"] = latest.get("source_evidence_bundle_ref")
            dp["latest_result_packet_ref"] = latest.get("source_result_packet_ref")
            dp["latest_consistency_guard_refs"] = latest.get("source_consistency_guard_refs", [])
            dp["latest_timestamp"] = latest.get("created_at")

        # Aggregate by state
        by_pstate = {}
        by_tdstate = {}
        for pid in records:
            p = DP_STORE_DIR / f"{pid}.json"
            if p.exists():
                try:
                    rec = load_json(str(p))
                    ps = rec.get("packet_state", "?")
                    ts = rec.get("threshold_state", "?")
                    by_pstate[ps] = by_pstate.get(ps, 0) + 1
                    by_tdstate[ts] = by_tdstate.get(ts, 0) + 1
                except Exception:
                    pass
        dp["by_packet_state"] = by_pstate
        dp["by_threshold_state"] = by_tdstate

        dp["dp_status"] = "present"
        dp["classification"] = "ready"
    except Exception:
        dp["dp_status"] = "absent"
        dp["classification"] = "unknown"

    return dp


def format_report(dp):
    """Format the decision packet startup surface report."""
    lines = []
    lines.append("QA Pilot Decision Packet Startup Surface (#90)")
    lines.append("=" * 60)
    lines.append(f"Generated:           {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append(f"Advisory:            True")
    lines.append(f"Custody:             qa-pilot-local")
    lines.append(f"Librarian impact:    none")
    lines.append("")

    lines.append("Decision Packet Posture")
    lines.append("-" * 60)
    count = dp.get("packet_count", 0)
    status = dp.get("dp_status", "absent")
    lines.append(f"  Packet count:      {count}")
    if count > 0:
        lines.append(f"  Latest packet:     {dp.get('latest_packet_id', '?')}")
        lines.append(f"  Latest state:      {dp.get('latest_packet_state', '?')}")
        lines.append(f"  Latest threshold:  {dp.get('latest_threshold_id', '?')}")
        lines.append(f"  Threshold state:   {dp.get('latest_threshold_state', '?')}")
        lines.append(f"  Evidence bundle:   {dp.get('latest_evidence_bundle_ref', '?')}")
        lines.append(f"  Result packet ref: {dp.get('latest_result_packet_ref', '?')}")
        guards = dp.get("latest_consistency_guard_refs", [])
        lines.append(f"  Consistency refs:  {', '.join(guards) if guards else 'none'}")
        ts = dp.get("latest_timestamp", "?")
        if ts and len(ts) > 19:
            ts = ts[:19]
        lines.append(f"  Latest timestamp:  {ts if ts else '?'}")

        # By-state breakdown
        by_ps = dp.get("by_packet_state", {})
        by_ts = dp.get("by_threshold_state", {})
        if by_ps:
            lines.append(f"  By packet state:   {'; '.join(f'{s}:{c}' for s, c in sorted(by_ps.items()))}")
        if by_ts:
            lines.append(f"  By threshold state:{'; '.join(f'{s}:{c}' for s, c in sorted(by_ts.items()))}")

        cls = dp.get("classification", "unknown")
        cls_str = {"ready": "ready", "degraded": "degraded", "blocked": "blocked", "unknown": "unknown"}
        lines.append(f"  Classification:    {cls_str.get(cls, cls)}")
    else:
        lines.append(f"  Posture:           {status} (no decision packets to report)")
    lines.append("")
    lines.append(ADVISORY_NOTICE)
    return "\n".join(lines)


# ── DP-SS Validation Rules ──────────────────────────────────────────────

DP_SS_RULES = {
    "DP-SS-1": "Decision packet surface section present in report",
    "DP-SS-2": "Packet count reported (0 or more is valid — honest empty state allowed)",
    "DP-SS-3": "Latest packet ID reported when packets exist",
    "DP-SS-4": "Latest packet state and threshold/evidence bundle references reported when packets exist",
    "DP-SS-5": "DP surface is read-only/advisory-only, cannot imply operational authority",
    "DP-SS-6": "DP section honestly reports empty/absent state (no false failure when empty)",
}


def validate_surface(dp):
    """Validate a decision packet surface against DP-SS acceptance rules."""
    checks = []

    # DP-SS-1: Surface section present
    checks.append(("DP-SS-1", bool(dp), "DP surface section present" if dp else "Missing dp_surface"))

    # DP-SS-2: Packet count reported
    pc = dp.get("packet_count", 0) if dp else 0
    pc_ok = isinstance(pc, int) and pc >= 0
    checks.append(("DP-SS-2", pc_ok, f"Packet count: {pc}" if pc_ok else f"Invalid count: {pc}"))

    # DP-SS-3: Latest packet ID when packets exist
    if pc > 0:
        lpid = dp.get("latest_packet_id") if dp else None
        checks.append(("DP-SS-3", bool(lpid), f"Latest packet: {lpid}" if lpid else "Missing latest packet ID"))
    else:
        checks.append(("DP-SS-3", True, "No packets (skip — honest empty state)"))

    # DP-SS-4: Latest packet state, threshold/bundle references when packets exist
    if pc > 0:
        valid_states = ("prepared", "needs_owner_review", "deferred", "closed_by_owner")
        valid_td_states = ("sufficient", "needs_more_context", "blocked")
        lps = dp.get("latest_packet_state") if dp else None
        lts = dp.get("latest_threshold_state") if dp else None
        ltb = dp.get("latest_threshold_id") if dp else None
        leb = dp.get("latest_evidence_bundle_ref") if dp else None
        lrp = dp.get("latest_result_packet_ref") if dp else None
        lcg = dp.get("latest_consistency_guard_refs") if dp else []

        state_ok = lps in valid_states
        td_state_ok = lts in valid_td_states if lts else True
        refs_ok = bool(ltb) and bool(leb)

        detail_parts = []
        if lps:
            detail_parts.append(f"state={lps}")
        if ltb:
            detail_parts.append(f"threshold={ltb}")
        if leb:
            detail_parts.append(f"bundle={leb}")

        all_ok = state_ok and td_state_ok and refs_ok
        checks.append((
            "DP-SS-4", all_ok,
            f"Latest: {'; '.join(detail_parts)}" if detail_parts else "Missing state/references"
        ))
    else:
        checks.append(("DP-SS-4", True, "No packets (skip)"))

    # DP-SS-5: Read-only/advisory-only, no authority claims
    dp_text = str(dp.get("dp_status", "")) + " " + str(dp.get("classification", ""))
    text_authority = any(kw in dp_text for kw in [
        "approve", "seal", "verified", "closed", "executed", "authorizes",
        "auto_accept", "auto_reject", "creates", "decides", "accepts",
    ])
    # Check field keys for authority-claiming names
    forbidden_keys = ["approved_by", "sealed_by", "sealed_at", "executed_by",
                      "executed_at", "verified_by", "closed_by", "decision_result",
                      "authorizes_execution", "approval_status", "evidence_verified"]
    key_authority = any(kw in str(list(dp.keys())) for kw in forbidden_keys)
    has_authority = text_authority or key_authority
    checks.append((
        "DP-SS-5", not has_authority,
        "No authority claims in DP surface" if not has_authority else "Authority claim in DP surface"
    ))

    # DP-SS-6: Honest empty/absent state
    dss = dp.get("dp_status", "absent") if dp else "absent"
    if pc == 0 and dss in ("absent", "empty"):
        checks.append(("DP-SS-6", True, f"Honest empty state: {dss} (no decision packets yet)"))
    elif pc == 0:
        checks.append(("DP-SS-6", False, f"Inconsistent empty state: count=0 but status='{dss}'"))
    else:
        checks.append(("DP-SS-6", True, f"Packets present ({pc}) — honest report"))

    all_pass = all(c[1] for c in checks)
    return (all_pass, checks)


# ── Commands ────────────────────────────────────────────────────────────

def cmd_report(args):
    """Generate decision packet startup surface report."""
    dp = gather_dp_surface()

    if args.format == "json":
        result = {
            "source_project": "qa-pilot",
            "custody": "qa-pilot-local",
            "librarian_impact": "none",
            "advisory_only": True,
            "advisory_notice": ADVISORY_NOTICE,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "dp_surface": dp,
        }
        print(json.dumps(result, indent=2))
    else:
        print(format_report(dp))

    return 0


def cmd_status(args):
    """Quick decision packet surface check."""
    dp = gather_dp_surface()
    count = dp.get("packet_count", 0)
    status = dp.get("dp_status", "absent")
    cls = dp.get("classification", "unknown")
    print(f"DP Posture:     {status}")
    print(f"Packet count:   {count}")
    if count > 0:
        print(f"Latest packet:  {dp.get('latest_packet_id', '?')}")
        print(f"Latest state:   {dp.get('latest_packet_state', '?')}")
        print(f"Latest thresh:  {dp.get('latest_threshold_id', '?')}")
    else:
        print(f"State:          no decision packets to report")
    print(f"Classification: {cls}")
    print(f"Advisory-only:  True")
    return 0


def cmd_validate(args):
    """Validate a decision packet surface report against DP-SS rules."""
    if args.input:
        try:
            data = load_json(args.input)
            if "dp_surface" in data:
                dp = data["dp_surface"]
            else:
                dp = data
        except Exception as e:
            print(f"ERROR: Failed to load input: {e}", file=sys.stderr)
            return 1
    else:
        dp = gather_dp_surface()

    all_pass, checks = validate_surface(dp)

    for rule_id, passed, message in checks:
        prefix = "PASS" if passed else "FAIL"
        print(f"  [{prefix}] {rule_id}: {message}")

    if all_pass:
        print("\nALL DP-SS CHECKS PASS")
        return 0
    else:
        print("\nSOME DP-SS CHECKS FAILED")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="QA Pilot Review Depth Thresholds Decision Packet Startup Surface"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    report_p = subparsers.add_parser("report", help="Generate decision packet startup surface report")
    report_p.add_argument("--format", choices=["text", "json"], default="text")

    subparsers.add_parser("status", help="Quick decision packet surface check")

    val_p = subparsers.add_parser("validate", help="Validate decision packet surface report")
    val_p.add_argument("--input", help="Path to report JSON file to validate")

    args = parser.parse_args()

    if args.command == "report":
        sys.exit(cmd_report(args))
    elif args.command == "status":
        sys.exit(cmd_status(args))
    elif args.command == "validate":
        sys.exit(cmd_validate(args))


if __name__ == "__main__":
    main()
