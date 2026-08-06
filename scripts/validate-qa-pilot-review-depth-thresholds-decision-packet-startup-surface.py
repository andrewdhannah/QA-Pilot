#!/usr/bin/env python3
"""QA Pilot Review Depth Thresholds Decision Packet Startup Surface Validator. DP-SS-1 through DP-SS-6."""
import argparse, json, os, sys, glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas",
    "qa-pilot-review-depth-thresholds-decision-packet-startup-surface.schema.json")
VALID_PACKET_STATES = ["prepared", "needs_owner_review", "deferred", "closed_by_owner"]
VALID_TD_STATES = ["sufficient", "needs_more_context", "blocked"]


def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def validate_schema(record, schema):
    try:
        import jsonschema
        try:
            jsonschema.validate(record, schema)
            return True, []
        except jsonschema.exceptions.ValidationError as e:
            return False, [("SCHEMA", f"schema violation: {e.message}")]
    except ImportError:
        return True, []


def validate_all_rules(record):
    """Validate DP-SS rules against a surface record.

    DP-SS-1: Surface section present
    DP-SS-2: Packet count reported (0 or more is valid)
    DP-SS-3: Latest packet ID reported when packets exist
    DP-SS-4: Latest packet state and threshold/bundle references reported when packets exist
    DP-SS-5: Read-only/advisory-only, no authority claims
    DP-SS-6: Honest empty/absent state
    """
    results = []
    surface = record.get("dp_surface", record)

    # DP-SS-1: Surface section present
    if isinstance(surface, dict) and "dp_status" in surface:
        results.append(("DP-SS-1", "Decision packet surface section present"))
    else:
        results.append(("DP-SS-1", "Missing dp_surface"))

    # DP-SS-2: Packet count reported (0 or more)
    pc = surface.get("packet_count", -1) if isinstance(surface, dict) else -1
    if isinstance(pc, int) and pc >= 0:
        results.append(("DP-SS-2", f"Packet count: {pc}"))
    else:
        results.append(("DP-SS-2", f"Invalid packet count: {pc}"))

    # DP-SS-3: Latest packet ID when packets exist
    if pc > 0:
        lpid = surface.get("latest_packet_id") if isinstance(surface, dict) else None
        if lpid:
            results.append(("DP-SS-3", f"Latest packet: {lpid}"))
        else:
            results.append(("DP-SS-3", "Missing latest packet ID"))
    else:
        results.append(("DP-SS-3", "No packets (honest empty state)"))

    # DP-SS-4: State and references when packets exist
    if pc > 0:
        lps = surface.get("latest_packet_state") if isinstance(surface, dict) else None
        lts = surface.get("latest_threshold_state") if isinstance(surface, dict) else None
        ltb = surface.get("latest_threshold_id") if isinstance(surface, dict) else None
        leb = surface.get("latest_evidence_bundle_ref") if isinstance(surface, dict) else None

        state_ok = lps in VALID_PACKET_STATES
        td_state_ok = lts in VALID_TD_STATES if lts else True
        refs_ok = bool(ltb) and bool(leb)

        details = []
        if lps:
            details.append(f"state={lps}")
        if ltb:
            details.append(f"threshold={ltb}")
        if leb:
            details.append(f"bundle={leb}")

        if state_ok and td_state_ok and refs_ok:
            results.append(("DP-SS-4", f"Latest state/references: {'; '.join(details)}"))
        else:
            results.append(("DP-SS-4", f"Incomplete state/references: {'; '.join(details) if details else 'missing'}"))
    else:
        results.append(("DP-SS-4", "No packets (skip)"))

    # DP-SS-5: No authority claims
    dp_text = ""
    authority_claim_detected = False
    if isinstance(surface, dict):
        # Check status/classification text
        dp_text = str(surface.get("dp_status", "")) + " " + str(surface.get("classification", ""))
        text_authority = any(kw in dp_text for kw in [
            "approve", "seal", "verified", "closed", "executed", "authorizes",
            "auto_accept", "auto_reject", "creates", "decides", "accepts",
        ])
        # Check field keys for authority-claiming names
        forbidden_keys = ["approved_by", "sealed_by", "sealed_at", "executed_by",
                          "executed_at", "verified_by", "closed_by", "decision_result",
                          "authorizes_execution", "approval_status", "evidence_verified"]
        key_authority = any(kw in str(list(surface.keys())) for kw in forbidden_keys)

        authority_claim_detected = text_authority or key_authority

    if not authority_claim_detected:
        results.append(("DP-SS-5", "No authority claims in DP surface (advisory-only)"))
    else:
        results.append(("DP-SS-5", "Authority claim detected in DP surface"))

    # DP-SS-6: Honest empty/absent state
    dss = surface.get("dp_status", "absent") if isinstance(surface, dict) else "absent"
    if pc == 0 and dss in ("absent", "empty"):
        results.append(("DP-SS-6", f"Honest empty state: {dss} (no decision packets)"))
    elif pc == 0:
        results.append(("DP-SS-6", f"Inconsistent empty state: count=0 but status='{dss}'"))
    elif pc > 0:
        results.append(("DP-SS-6", f"Packets present ({pc}) — honest report"))
    else:
        results.append(("DP-SS-6", f"Unknown state"))

    return results


def cmd_fixture(args):
    directory = args.directory or os.path.join(PROJECT_ROOT, "docs", "examples",
        "qa-pilot-review-depth-thresholds-decision-packet-startup-surface")
    schema = load_schema() if os.path.exists(SCHEMA_PATH) else None

    if not os.path.isdir(directory):
        print(f"Fixtures directory not found: {directory}")
        sys.exit(1)

    json_files = sorted(glob.glob(os.path.join(directory, "*.json")))
    if not json_files:
        print(f"No fixture files found in {directory}")
        sys.exit(1)

    total = passed = failed = 0
    for fpath in json_files:
        fname = os.path.basename(fpath)
        with open(fpath) as f:
            try:
                record = json.load(f)
            except json.JSONDecodeError as e:
                print(f"  {fname}: INVALID JSON — {e}")
                failed += 1
                continue

        total += 1

        if record.get("$schema", "").endswith("decision-packet-startup-surface-v1") or "dp_surface" in record:
            schema_ok, schema_issues = validate_schema(record, schema) if schema else (True, [])
        else:
            schema_ok, schema_issues = True, []

        rule_results = validate_all_rules(record)
        rule_issues = [(r[0], r[1]) for r in rule_results if "Fail" in r[1] or "Missing" in r[1] or "Invalid" in r[1] or "Authority claim" in r[1] or "Inconsistent" in r[1] or "Incomplete" in r[1]]
        all_issues = schema_issues + rule_issues if hasattr(rule_issues, '__iter__') and not isinstance(rule_issues[0] if rule_issues else None, str) else []

        is_valid = fname.startswith("valid-")
        is_invalid = fname.startswith("invalid-")

        if is_valid:
            if not all_issues and all("Fail" not in r[1] for r in rule_results):
                print(f"  {fname}: PASS")
                passed += 1
            else:
                print(f"  {fname}: FAIL")
                for c, d in all_issues if isinstance(all_issues, list) else []:
                    print(f"    [{c}] {d}")
                for r in rule_results:
                    if "missing" in r[1].lower() or "authority claim" in r[1].lower() or "inconsistent" in r[1].lower() or "Incomplete" in r[1] or "incomplete" in r[1]:
                        print(f"    [{r[0]}] {r[1]}")
                failed += 1
        elif is_invalid:
            has_issues = False
            issue_msgs = []
            for r in rule_results:
                if "Fail" in r[1] or "Missing" in r[1] or "Invalid" in r[1] or "Authority claim" in r[1] or "Inconsist" in r[1]:
                    has_issues = True
                    issue_msgs.append(r[1])
            if schema_issues:
                has_issues = True
                issue_msgs.append(f"[SCHEMA] {schema_issues[0][1] if isinstance(schema_issues[0], tuple) else schema_issues[0]}")

            if has_issues:
                print(f"  {fname}: PASS (rejected)")
                for m in issue_msgs[:3]:
                    print(f"    -> {m}")
                passed += 1
            else:
                print(f"  {fname}: FAIL (expected rejection)")
                for r in rule_results:
                    print(f"    [{r[0]}] {r[1]}")
                failed += 1

    print(f"\nFixture validation: {passed} pass, {failed} fail, {total} total")
    sys.exit(1 if failed else 0)


def cmd_validate(args):
    schema = load_schema() if os.path.exists(SCHEMA_PATH) else None
    for fpath in args.json_files:
        with open(fpath) as f:
            record = json.load(f)
        rule_results = validate_all_rules(record)

        surface_id = fpath
        if isinstance(record, dict):
            surface = record.get("dp_surface", record)
            surface_id = surface.get("latest_packet_id", fpath)

        all_issues = []
        for rule_id, msg in rule_results:
            is_pass = not any(kw in msg for kw in ["Fail", "Missing", "Invalid", "Authority claim", "Inconsist", "Incomplete"])
            if is_pass:
                print(f"PASS [{rule_id}] {msg}")
            else:
                print(f"FAIL [{rule_id}] {msg}")
                all_issues.append((rule_id, msg))

        if all_issues:
            print(f"\nINVALID: {surface_id}")
        else:
            print(f"\nVALID: {surface_id}")


def cmd_live(args):
    index_path = os.path.join(PROJECT_ROOT, "data", "review-decision-packets", "packet-index.json")
    if not os.path.exists(index_path):
        print("No live decision packet store found.")
        return

    with open(index_path) as f:
        index = json.load(f)
    records = index.get("records", [])
    if not records:
        print("No live decision packet records found.")
        return

    from scripts.qa_pilot_review_depth_thresholds_decision_packet_startup_surface import gather_dp_surface
    dp = gather_dp_surface()
    rule_results = validate_all_rules({"dp_surface": dp})
    passed = failed = 0
    for rule_id, msg in rule_results:
        is_pass = not any(kw in msg for kw in ["Fail", "Missing", "Invalid", "Authority claim", "Inconsist", "Incomplete"])
        if is_pass:
            print(f"  {rule_id}: PASS — {msg}")
            passed += 1
        else:
            print(f"  {rule_id}: FAIL — {msg}")
            failed += 1
    print(f"\nLive surface validation: {passed} pass, {failed} fail")
    sys.exit(1 if failed else 0)


def main():
    parser = argparse.ArgumentParser(
        description="QA Pilot Review Depth Thresholds Decision Packet Startup Surface Validator")
    sub = parser.add_subparsers(dest="mode", required=True)

    p_f = sub.add_parser("fixture")
    p_f.add_argument("directory", nargs="?")
    p_f.set_defaults(func=cmd_fixture)

    p_v = sub.add_parser("validate")
    p_v.add_argument("json_files", nargs="+")
    p_v.set_defaults(func=cmd_validate)

    p_l = sub.add_parser("live")
    p_l.set_defaults(func=cmd_live)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
