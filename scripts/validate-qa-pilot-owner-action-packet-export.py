#!/usr/bin/env python3
"""
QA Workbench Action Packet Export Validator.

Validates action packet exports against schema + AXP business rules.

AXP Rules:
  AXP-1: action_state must be valid enum value
  AXP-2: advisory_only must be True
  AXP-3: custody must be qa-pilot-local
  AXP-4: librarian_impact must be 'none'
  AXP-5: authority_disclaimer must match exactly
  AXP-6: Export cannot claim execution, authorization, seal, approval, verification, or closure
  AXP-7: Rationale must not claim execution, authorization, seal, or closure authority
  AXP-8: Export cannot carry registry/RCR/SRS fields
"""

import argparse, json, os, sys, glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-workbench-action-packet-export.schema.json")
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "workbench-action-packet-exports")
STORE_INDEX = os.path.join(STORE_DIR, "export-index.json")

DISCLAIMER = "This action packet export packages the intended action path for downstream handoff only. It does not execute work, authorize execution, approve intake, verify evidence, close workbench items, mutate packets, mutate source records, seal anything, or create autonomous authority. Custody is qa-pilot-local. Librarian impact is none."
VALID_AP_STATES = ["proposed", "owner_authorized", "deferred", "rejected"]


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
    results = []
    if record.get("action_state") not in VALID_AP_STATES:
        results.append(("AXP-1", f"action_state must be one of {VALID_AP_STATES}"))
    if record.get("advisory_only") is not True:
        results.append(("AXP-2", "advisory_only must be True"))
    if record.get("custody", "") != "qa-pilot-local":
        results.append(("AXP-3", "custody must be qa-pilot-local"))
    if record.get("librarian_impact", "") != "none":
        results.append(("AXP-4", "librarian_impact must be 'none'"))
    if record.get("authority_disclaimer", "") != DISCLAIMER:
        results.append(("AXP-5", "authority_disclaimer mismatch"))
    
    forbidden_patterns = [
        "executed", "execution_result", "authorizes_execution", "seal_", "sealed",
        "approval_status", "approved_by", "evidence_verified", "items_closed",
        "mutates_intake", "mutates_summary", "mutates_receipt", "mutates_packet",
    ]
    for key in record:
        kl = key.lower()
        for pattern in forbidden_patterns:
            if pattern in kl:
                results.append(("AXP-6", f"forbidden field '{key}' claims {pattern.replace('_', ' ')}"))

    rationale = record.get("rationale", "").lower()
    for kw in ["executed", "authorizes", "seal", "approved", "verified", "closed", "defect accepted"]:
        if kw in rationale:
            results.append(("AXP-7", f"rationale contains authority-claiming term '{kw}'"))

    for key in record:
        kl = key.lower()
        if any(kw in kl for kw in ["registry", "rcr_", "srs_"]):
            results.append(("AXP-8", f"export carries registry/RCR/SRS field '{key}'"))

    return results


def cmd_fixture(args):
    directory = args.directory or os.path.join(PROJECT_ROOT, "docs", "examples", "qa-pilot-action-packet-export")
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
    schema = load_schema()
    for fpath in args.json_files:
        with open(fpath) as f:
            record = json.load(f)
        schema_ok, schema_issues = validate_schema(record, schema)
        rule_issues = validate_all_rules(record)
        all_issues = schema_issues + rule_issues
        eid = record.get("export_id", fpath)
        if not all_issues:
            print(f"VALID: {eid}")
        else:
            print(f"INVALID: {eid}")
            for check, detail in all_issues: print(f"  [{check}] {detail}")


def cmd_live(args):
    schema = load_schema()
    if not os.path.exists(STORE_INDEX):
        print("No live action export store found."); return
    with open(STORE_INDEX) as f:
        index = json.load(f)
    records = index.get("records", [])
    if not records:
        print("No live action export records found."); return
    passed = failed = 0
    for eid in records:
        path = os.path.join(STORE_DIR, f"{eid}.json")
        if not os.path.exists(path):
            print(f"  {eid}: MISSING"); failed += 1; continue
        with open(path) as f:
            record = json.load(f)
        schema_ok, schema_issues = validate_schema(record, schema)
        rule_issues = validate_all_rules(record)
        all_issues = schema_issues + rule_issues
        if not all_issues:
            print(f"  {eid}: PASS"); passed += 1
        else:
            print(f"  {eid}: FAIL")
            for check, detail in all_issues: print(f"    [{check}] {detail}")
            failed += 1
    print(f"\nLive export validation: {passed} pass, {failed} fail")
    if failed > 0: sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="QA Workbench Action Packet Export Validator")
    sub = parser.add_subparsers(dest="mode", required=True)
    p_f = sub.add_parser("fixture"); p_f.add_argument("directory", nargs="?"); p_f.set_defaults(func=cmd_fixture)
    p_v = sub.add_parser("validate"); p_v.add_argument("json_files", nargs="+"); p_v.set_defaults(func=cmd_validate)
    p_l = sub.add_parser("live"); p_l.set_defaults(func=cmd_live)
    args = parser.parse_args(); args.func(args)

if __name__ == "__main__":
    main()
