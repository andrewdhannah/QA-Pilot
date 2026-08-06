#!/usr/bin/env python3
"""
QA Workbench Owner Action Packet Validator.

Validates Owner action packets against schema + AP business rules.

Modes:
  fixture   Validate all action packet fixtures in a directory
  validate  Validate a single action packet JSON file
  live      Validate live action packet records from the store

AP Rules:
  AP-1: action_state must be a valid enum value
  AP-2: advisory_only must be True
  AP-3: custody must be qa-pilot-local
  AP-4: librarian_impact must be 'none'
  AP-5: authority_disclaimer must match exactly
  AP-6: Packet cannot claim execution, seal, verification, closure, or mutation
  AP-7: Rationale must not claim autonomous execution, seal, or closure authority
  AP-8: Packet cannot carry registry/RCR/SRS fields
"""

import argparse, json, os, sys, glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-workbench-owner-action-packet.schema.json")
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "workbench-owner-action-packets")
STORE_INDEX = os.path.join(STORE_DIR, "action-index.json")

DISCLAIMER = "This Owner action packet records the intended next action path only. It does not execute the action, approve intake, verify evidence, close workbench items, seal work, mutate source records, or create autonomous authority. Custody is qa-pilot-local. Librarian impact is none."
VALID_STATES = ["proposed", "owner_authorized", "deferred", "rejected"]
VALID_DECISIONS = ["accepted_for_action", "authorized", "deferred", "rejected"]


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
    """Validate all AP rules. Returns list of (check_name, detail) tuples."""
    results = []

    # AP-1: Valid action_state
    if record.get("action_state") not in VALID_STATES:
        results.append(("AP-1", f"action_state must be one of {VALID_STATES}"))

    # AP-2: advisory_only
    if record.get("advisory_only") is not True:
        results.append(("AP-2", "advisory_only must be True"))

    # AP-3: custody
    if record.get("custody", "") != "qa-pilot-local":
        results.append(("AP-3", "custody must be qa-pilot-local"))

    # AP-4: librarian_impact
    if record.get("librarian_impact", "") != "none":
        results.append(("AP-4", "librarian_impact must be 'none'"))

    # AP-5: authority_disclaimer
    if record.get("authority_disclaimer", "") != DISCLAIMER:
        results.append(("AP-5", "authority_disclaimer mismatch"))

    # AP-6: No execution, seal, verification, closure, or mutation fields
    forbidden_patterns = [
        "executed", "execution_result", "seal_action", "seal_scope",
        "evidence_verified", "verification_detail", "verification_status",
        "items_closed", "closed", "closure_date", "closure_reason",
        "mutates_", "mutates_intake", "mutates_summary", "mutates_receipt",
    ]
    for key in record:
        kl = key.lower()
        for pattern in forbidden_patterns:
            if pattern in kl:
                results.append(("AP-6", f"forbidden field '{key}' claims {pattern.replace('_', ' ')}"))

    # AP-7: Rationale must not claim execution, seal, or closure authority
    rationale = record.get("rationale", "").lower()
    for kw in ["executed autonomously", "seal", "approved", "verified", "closed", "defect accepted"]:
        if kw in rationale:
            results.append(("AP-7", f"rationale contains authority-claiming term '{kw}'"))

    # AP-8: No registry/RCR/SRS fields
    for key in record:
        kl = key.lower()
        if any(kw in kl for kw in ["registry", "rcr_", "srs_"]):
            results.append(("AP-8", f"packet carries registry/RCR/SRS field '{key}'"))

    return results


def cmd_fixture(args):
    """Validate all action packet fixtures in a directory."""
    directory = args.directory or os.path.join(PROJECT_ROOT, "docs", "examples", "qa-pilot-owner-action-packet")
    schema = load_schema()

    if not os.path.isdir(directory):
        print(f"Fixtures directory not found: {directory}"); sys.exit(1)

    json_files = sorted(glob.glob(os.path.join(directory, "*.json")))
    if not json_files:
        print(f"No fixture files found in {directory}"); sys.exit(1)

    total = passed = failed = 0
    for fpath in json_files:
        fname = os.path.basename(fpath)
        with open(fpath) as f:
            try:
                record = json.load(f)
            except json.JSONDecodeError as e:
                print(f"  {fname}: INVALID JSON — {e}"); failed += 1; continue

        total += 1
        schema_ok, schema_issues = validate_schema(record, schema)
        rule_issues = validate_all_rules(record)
        all_issues = schema_issues + rule_issues

        is_valid = fname.startswith("valid-")
        is_invalid = fname.startswith("invalid-")

        if is_valid:
            if not all_issues:
                print(f"  {fname}: PASS"); passed += 1
            else:
                print(f"  {fname}: FAIL (expected PASS)")
                for check, detail in all_issues: print(f"    [{check}] {detail}")
                failed += 1
        elif is_invalid:
            if all_issues:
                print(f"  {fname}: PASS (rejected as expected)")
                for check, detail in all_issues[:3]: print(f"    [{check}] {detail}")
                passed += 1
            else:
                print(f"  {fname}: FAIL (expected rejection but all checks pass)"); failed += 1

    print(f"\nFixture validation: {passed} pass, {failed} fail, {total} total")
    if failed > 0: sys.exit(1)


def cmd_validate(args):
    """Validate single action packet files."""
    schema = load_schema()
    for fpath in args.json_files:
        with open(fpath) as f:
            record = json.load(f)
        schema_ok, schema_issues = validate_schema(record, schema)
        rule_issues = validate_all_rules(record)
        all_issues = schema_issues + rule_issues
        pid = record.get("action_packet_id", fpath)
        if not all_issues:
            print(f"VALID: {pid}")
        else:
            print(f"INVALID: {pid}")
            for check, detail in all_issues: print(f"  [{check}] {detail}")


def cmd_live(args):
    """Validate live action packet records from the store."""
    schema = load_schema()
    if not os.path.exists(STORE_INDEX):
        print("No live action packet store found."); return
    with open(STORE_INDEX) as f:
        index = json.load(f)
    records = index.get("records", [])
    if not records:
        print("No live action packet records found."); return

    passed = failed = 0
    for pid in records:
        path = os.path.join(STORE_DIR, f"{pid}.json")
        if not os.path.exists(path):
            print(f"  {pid}: MISSING"); failed += 1; continue
        with open(path) as f:
            record = json.load(f)
        schema_ok, schema_issues = validate_schema(record, schema)
        rule_issues = validate_all_rules(record)
        all_issues = schema_issues + rule_issues
        if not all_issues:
            print(f"  {pid}: PASS"); passed += 1
        else:
            print(f"  {pid}: FAIL")
            for check, detail in all_issues: print(f"    [{check}] {detail}")
            failed += 1

    print(f"\nLive action packet validation: {passed} pass, {failed} fail")
    if failed > 0: sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="QA Workbench Owner Action Packet Validator")
    sub = parser.add_subparsers(dest="mode", required=True)
    p_f = sub.add_parser("fixture"); p_f.add_argument("directory", nargs="?"); p_f.set_defaults(func=cmd_fixture)
    p_v = sub.add_parser("validate"); p_v.add_argument("json_files", nargs="+"); p_v.set_defaults(func=cmd_validate)
    p_l = sub.add_parser("live"); p_l.set_defaults(func=cmd_live)
    args = parser.parse_args(); args.func(args)

if __name__ == "__main__":
    main()
