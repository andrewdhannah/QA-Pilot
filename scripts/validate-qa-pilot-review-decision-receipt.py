#!/usr/bin/env python3
"""
QA Workbench Review Decision Receipt Validator.

Validates review decision receipts against schema + WDR business rules.

Modes:
  fixture   Validate all receipt fixtures in a directory
  validate  Validate a single receipt JSON file
  live      Validate live receipt records from the store

WDR Rules:
  WDR-1: Decision must be a valid enum value
  WDR-2: advisory_only must be True
  WDR-3: custody must be qa-pilot-local
  WDR-4: librarian_impact must be 'none'
  WDR-5: authority_disclaimer must match exactly
  WDR-6: Receipt cannot claim seal, approval, verification, or closure
  WDR-7: Rationale must not claim seal/approval/verification authority
  WDR-8: Receipt cannot carry registry/RCR/SRS fields
"""

import argparse, json, os, sys, glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-workbench-review-decision-receipt.schema.json")
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "review-decision-receipts")
STORE_INDEX = os.path.join(STORE_DIR, "receipt-index.json")

DISCLAIMER = "A workbench review decision receipt records an Owner review disposition over a decision summary. It does not approve intake, verify evidence, close workbench items, seal work, mutate source records, or create autonomous authority. Custody is qa-pilot-local. Librarian impact is none."
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
    """Validate all WDR rules. Returns list of (check_name, detail) tuples."""
    results = []

    # WDR-1: Valid decision
    if record.get("decision") not in VALID_DECISIONS:
        results.append(("WDR-1", f"decision must be one of {VALID_DECISIONS}"))

    # WDR-2: advisory_only must be True
    if record.get("advisory_only") is not True:
        results.append(("WDR-2", "advisory_only must be True"))

    # WDR-3: custody
    if record.get("custody", "") != "qa-pilot-local":
        results.append(("WDR-3", f"custody must be qa-pilot-local"))

    # WDR-4: librarian_impact
    if record.get("librarian_impact", "") != "none":
        results.append(("WDR-4", f"librarian_impact must be 'none'"))

    # WDR-5: authority_disclaimer
    if record.get("authority_disclaimer", "") != DISCLAIMER:
        results.append(("WDR-5", "authority_disclaimer mismatch"))

    # WDR-6: No seal/approval/verification/closure fields
    forbidden_field_patterns = [
        "sealed", "seal_", "approval_status", "approved_by", "approved_at",
        "evidence_verified", "verification_detail", "verification_status",
        "items_closed", "closed", "closure_date", "closure_reason",
        "intake_approved", "intake_approval",
    ]
    for key in record:
        kl = key.lower()
        for pattern in forbidden_field_patterns:
            if pattern in kl:
                results.append(("WDR-6", f"forbidden field '{key}' claims {pattern.replace('_', ' ')}"))

    # WDR-7: Rationale must not claim authority
    rationale = record.get("rationale", "").lower()
    for kw in ["seal", "approve", "verified", "defect accepted"]:
        if kw in rationale:
            results.append(("WDR-7", f"rationale contains authority-claiming term '{kw}'"))

    # WDR-8: No registry/RCR/SRS fields
    for key in record:
        kl = key.lower()
        if any(kw in kl for kw in ["registry", "rcr_", "srs_"]):
            results.append(("WDR-8", f"receipt carries registry/RCR/SRS field '{key}'"))

    return results


def cmd_fixture(args):
    """Validate all receipt fixtures in a directory."""
    directory = args.directory or os.path.join(PROJECT_ROOT, "docs", "examples", "qa-pilot-review-decision-receipt")
    schema = load_schema()

    if not os.path.isdir(directory):
        print(f"Fixtures directory not found: {directory}")
        sys.exit(1)

    json_files = sorted(glob.glob(os.path.join(directory, "*.json")))
    if not json_files:
        print(f"No fixture files found in {directory}")
        sys.exit(1)

    total = 0
    passed = 0
    failed = 0

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
        schema_ok, schema_issues = validate_schema(record, schema)
        rule_issues = validate_all_rules(record)
        all_issues = schema_issues + rule_issues

        is_valid = fname.startswith("valid-")
        is_invalid = fname.startswith("invalid-")

        if is_valid:
            if not all_issues:
                print(f"  {fname}: PASS")
                passed += 1
            else:
                print(f"  {fname}: FAIL (expected PASS)")
                for check, detail in all_issues:
                    print(f"    [{check}] {detail}")
                failed += 1
        elif is_invalid:
            if all_issues:
                print(f"  {fname}: PASS (rejected as expected)")
                for check, detail in all_issues[:3]:
                    print(f"    [{check}] {detail}")
                passed += 1
            else:
                print(f"  {fname}: FAIL (expected rejection but all checks pass)")
                failed += 1
        else:
            print(f"  {fname}: SKIP")

    print(f"\nFixture validation: {passed} pass, {failed} fail, {total} total")
    if failed > 0:
        sys.exit(1)


def cmd_validate(args):
    """Validate a single receipt JSON file."""
    schema = load_schema()
    for fpath in args.json_files:
        with open(fpath) as f:
            record = json.load(f)

        schema_ok, schema_issues = validate_schema(record, schema)
        rule_issues = validate_all_rules(record)
        all_issues = schema_issues + rule_issues

        rid = record.get("receipt_id", fpath)
        if not all_issues:
            print(f"VALID: {rid}")
        else:
            print(f"INVALID: {rid}")
            for check, detail in all_issues:
                print(f"  [{check}] {detail}")


def cmd_live(args):
    """Validate live receipt records from the store."""
    schema = load_schema()
    if not os.path.exists(STORE_INDEX):
        print("No live receipt store found.")
        return

    with open(STORE_INDEX) as f:
        index = json.load(f)

    records = index.get("records", [])
    if not records:
        print("No live receipt records found.")
        return

    passed = 0
    failed = 0
    for rid in records:
        path = os.path.join(STORE_DIR, f"{rid}.json")
        if not os.path.exists(path):
            print(f"  {rid}: MISSING")
            failed += 1
            continue
        with open(path) as f:
            record = json.load(f)

        schema_ok, schema_issues = validate_schema(record, schema)
        rule_issues = validate_all_rules(record)
        all_issues = schema_issues + rule_issues

        if not all_issues:
            print(f"  {rid}: PASS")
            passed += 1
        else:
            print(f"  {rid}: FAIL")
            for check, detail in all_issues:
                print(f"    [{check}] {detail}")
            failed += 1

    print(f"\nLive receipt validation: {passed} pass, {failed} fail")
    if failed > 0:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="QA Workbench Review Decision Receipt Validator")
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
