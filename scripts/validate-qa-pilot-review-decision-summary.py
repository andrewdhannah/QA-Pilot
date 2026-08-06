#!/usr/bin/env python3
"""
QA Workbench Review Decision Summary Validator.

Validates review decision summaries against schema + DS business rules.

Modes:
  fixture   Validate all summary fixtures in a directory
  validate  Validate a single summary JSON file
  live      Validate live summary records from the summary store

DS Rules:
  DS-1: Summary must be read-only (no status changes, no seal, no approval field)
  DS-2: Summary must be advisory-only (advisory_only=True)
  DS-3: Summary must preserve intake/source packet identity
  DS-4: Summary counts must match included intake records
  DS-5: Advisory next actions must be bounded
  DS-6: Summary cannot claim approval, verification, seal, closure, or defect acceptance
  DS-7: Summary cannot mutate lifecycle or intake status
  DS-8: Summary cannot include Librarian paths or impact
"""

import argparse, json, os, sys, glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SUMMARY_SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-workbench-review-decision-summary.schema.json")
SUMMARY_STORE_DIR = os.path.join(PROJECT_ROOT, "data", "review-decision-summaries")
SUMMARY_STORE_INDEX = os.path.join(SUMMARY_STORE_DIR, "summary-index.json")

ADVISORY_NEXT_ACTIONS = {
    "review_needs_review_items",
    "review_deferred_items",
    "review_resolved_locally_items",
    "assign_severity_priority",
    "collect_evidence",
    "triage_intake",
    "create_review_packet",
    "export_for_owner_review",
    "no_action_required",
}

DISCLAIMER = "This review decision summary is advisory-only. It does not approve the intake, verify evidence, accept defects, close items, or seal anything. It does not mutate intake records, source packets, or Librarian. Custody is qa-pilot-local. Librarian impact is none."


def load_schema():
    with open(SUMMARY_SCHEMA_PATH) as f:
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
    """
    Validate all DS rules against a summary record.
    Returns list of (check_name, detail) tuples for each failure.
    Empty list = all pass.
    """
    results = []

    # DS-1: Summary must be read-only
    if record.get("intake_status") is not None:
        results.append(("DS-1", "summary must not carry intake_status"))
    if record.get("sealed", False) is True:
        results.append(("DS-1", "summary must not claim sealed=True"))
    if record.get("approval_status") is not None:
        results.append(("DS-1", "summary must not carry approval_status"))
    if record.get("approved_by") is not None:
        results.append(("DS-1", "summary must not carry approved_by"))
    if record.get("closed", False) is True:
        results.append(("DS-1", "summary must not claim closed=True"))
    if record.get("defect_accepted", False) is True:
        results.append(("DS-1", "summary must not claim defect_accepted"))
    if record.get("verification_status") is not None:
        results.append(("DS-1", "summary must not carry verification_status"))

    # DS-2: Summary must be advisory-only
    if record.get("advisory_only") is not True:
        results.append(("DS-2", "advisory_only must be True"))

    # DS-3: Summary must preserve intake/source packet identity
    iid = record.get("intake_id", "")
    if not iid.startswith("IR-"):
        results.append(("DS-3", f"intake_id must start with IR- (got '{iid}')"))
    pid = record.get("source_packet_id", "")
    if not pid.startswith("XPK-"):
        results.append(("DS-3", f"source_packet_id must start with XPK- (got '{pid}')"))

    # DS-4: Summary counts must match
    status_counts = record.get("status_counts", {})
    total_from_status = sum(status_counts.values()) if status_counts else 0
    item_count = record.get("item_count", 0)
    if total_from_status != item_count:
        results.append(("DS-4", f"status_counts sum ({total_from_status}) != item_count ({item_count})"))

    # Check that item categories counts are consistent
    categories_count = (
        len(record.get("unresolved_items", []))
        + len(record.get("needs_review_items", []))
        + len(record.get("deferred_items", []))
        + len(record.get("resolved_locally_items", []))
    )
    if categories_count != item_count:
        results.append(("DS-4", f"categorized items total ({categories_count}) != item_count ({item_count})"))

    # DS-5: Advisory next actions must be bounded
    actions = record.get("advisory_next_actions", [])
    if not isinstance(actions, list):
        results.append(("DS-5", "advisory_next_actions must be a list"))
    else:
        for a in actions:
            if a not in ADVISORY_NEXT_ACTIONS:
                results.append(("DS-5", f"unbounded action '{a}' — not in allowed set"))

    # DS-6: Summary cannot claim approval, verification, seal, closure, or defect acceptance
    text = json.dumps(record)
    # Check field names (not just values)
    forbidden_field_patterns = [
        "approval_status", "approved_by", "approval_date",
        "verification_status", "verification_detail",
        "defect_accepted", "acceptance_rationale",
        "sealed", "closed", "closed_at", "closure_reason",
    ]
    for pattern in forbidden_field_patterns:
        # Check if any top-level key or nested key matches
        def _check_keys(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    fp = f"{path}.{k}" if path else k
                    if k == pattern:
                        results.append(("DS-6", f"forbidden field '{fp}' claims {pattern.replace('_', ' ')}"))
                    _check_keys(v, fp)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    _check_keys(item, f"{path}[{i}]")
        _check_keys(record)

    # DS-7: Summary cannot mutate lifecycle or intake status
    if record.get("new_status") is not None:
        results.append(("DS-7", "summary must not carry new_status (would mutate lifecycle)"))
    if record.get("new_intake_status") is not None:
        results.append(("DS-7", "summary must not carry new_intake_status (would mutate intake)"))

    # DS-8: Summary cannot include Librarian paths or impact
    if record.get("librarian_impact", "") != "none":
        results.append(("DS-8", f"librarian_impact must be 'none' (got '{record.get('librarian_impact')}')"))
    if record.get("custody", "") != "qa-pilot-local":
        results.append(("DS-8", f"custody must be qa-pilot-local (got '{record.get('custody')}')"))

    # Check for registry/RCR/SRS fields
    for key in record:
        kl = key.lower()
        if any(kw in kl for kw in ["registry", "rcr_", "srs_"]):
            results.append(("DS-8", f"summary carries registry/RCR/SRS field '{key}'"))

    text = json.dumps(record)
    for path_pattern in ["librarian/", "/librarian", "active/librarian"]:
        if path_pattern in text:
            # Check if it's in the authority_disclaimer (allowed)
            if path_pattern not in DISCLAIMER:
                results.append(("DS-8", f"summary contains Librarian path reference ('{path_pattern}')"))

    return results


def cmd_fixture(args):
    """Validate all summary fixtures in a directory."""
    directory = args.directory or os.path.join(PROJECT_ROOT, "docs", "examples", "qa-pilot-review-decision-summary")
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
            print(f"  {fname}: SKIP (does not start with valid- or invalid-)")

    print(f"\nFixture validation: {passed} pass, {failed} fail, {total} total")
    if failed > 0:
        sys.exit(1)


def cmd_validate(args):
    """Validate a single summary JSON file."""
    schema = load_schema()
    for fpath in args.json_files:
        with open(fpath) as f:
            record = json.load(f)

        schema_ok, schema_issues = validate_schema(record, schema)
        rule_issues = validate_all_rules(record)
        all_issues = schema_issues + rule_issues

        sid = record.get("summary_id", fpath)
        if not all_issues:
            print(f"VALID: {sid}")
        else:
            print(f"INVALID: {sid}")
            for check, detail in all_issues:
                print(f"  [{check}] {detail}")


def cmd_live(args):
    """Validate live summary records from the summary store."""
    schema = load_schema()
    if not os.path.exists(SUMMARY_STORE_INDEX):
        print("No live summary store found.")
        return

    with open(SUMMARY_STORE_INDEX) as f:
        index = json.load(f)

    records = index.get("records", [])
    if not records:
        print("No live summary records found.")
        return

    passed = 0
    failed = 0
    for sid in records:
        path = os.path.join(SUMMARY_STORE_DIR, f"{sid}.json")
        if not os.path.exists(path):
            print(f"  {sid}: MISSING")
            failed += 1
            continue
        with open(path) as f:
            record = json.load(f)

        schema_ok, schema_issues = validate_schema(record, schema)
        rule_issues = validate_all_rules(record)
        all_issues = schema_issues + rule_issues

        if not all_issues:
            print(f"  {sid}: PASS")
            passed += 1
        else:
            print(f"  {sid}: FAIL")
            for check, detail in all_issues:
                print(f"    [{check}] {detail}")
            failed += 1

    print(f"\nLive summary validation: {passed} pass, {failed} fail")
    if failed > 0:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="QA Workbench Review Decision Summary Validator")
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
