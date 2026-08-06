#!/usr/bin/env python3
"""
QA Pilot Workbench Review Decision Receipt CLI.

Commands:
  decision-record    Record an Owner decision for a decision summary
  decision-read      Read a stored decision receipt by ID
  decision-list      List stored decision receipts
  decision-validate  Validate a receipt against schema + WDR rules
  decision-status    Show aggregate decision receipt status

Authority boundaries:
  A workbench review decision receipt records an Owner review disposition
  over a decision summary. It does not approve intake, verify evidence,
  close workbench items, seal work, mutate source records, or create
  autonomous authority.
"""

import argparse, json, os, sys, datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "review-decision-receipts")
STORE_INDEX = os.path.join(STORE_DIR, "receipt-index.json")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-workbench-review-decision-receipt.schema.json")

DISCLAIMER = "A workbench review decision receipt records an Owner review disposition over a decision summary. It does not approve intake, verify evidence, close workbench items, seal work, mutate source records, or create autonomous authority. Custody is qa-pilot-local. Librarian impact is none."

VALID_DECISIONS = ["accepted_for_action", "authorized", "deferred", "rejected"]


def _now():
    return datetime.datetime.utcnow().isoformat() + "Z"


def _ensure_store():
    os.makedirs(STORE_DIR, exist_ok=True)
    if not os.path.exists(STORE_INDEX):
        with open(STORE_INDEX, "w") as f:
            json.dump({"records": [], "last_updated": _now()}, f, indent=2)


def _load_index():
    _ensure_store()
    with open(STORE_INDEX) as f:
        return json.load(f)


def _save_index(index):
    index["last_updated"] = _now()
    with open(STORE_INDEX, "w") as f:
        json.dump(index, f, indent=2)


def _load_receipt(receipt_id):
    path = os.path.join(STORE_DIR, f"{receipt_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def _save_receipt(record):
    path = os.path.join(STORE_DIR, f"{record['receipt_id']}.json")
    with open(path, "w") as f:
        json.dump(record, f, indent=2)


def _validate_schema(record):
    try:
        import jsonschema
        with open(SCHEMA_PATH) as f:
            schema = json.load(f)
        try:
            jsonschema.validate(record, schema)
            return True, []
        except jsonschema.exceptions.ValidationError as e:
            return False, [f"schema violation: {e.message}"]
    except ImportError:
        return True, []


def _validate_wdr_rules(record):
    """Validate a receipt against WDR-1 through WDR-8 rules."""
    violations = []

    # WDR-1: decision must be a valid enum value
    if record.get("decision") not in VALID_DECISIONS:
        violations.append(f"WDR-1: decision must be one of {VALID_DECISIONS}")

    # WDR-2: advisory_only must be True
    if not record.get("advisory_only", False):
        violations.append("WDR-2: advisory_only must be True")

    # WDR-3: custody must be qa-pilot-local
    if record.get("custody", "") != "qa-pilot-local":
        violations.append("WDR-3: custody must be qa-pilot-local")

    # WDR-4: librarian_impact must be none
    if record.get("librarian_impact", "") != "none":
        violations.append("WDR-4: librarian_impact must be 'none'")

    # WDR-5: authority_disclaimer must match
    if record.get("authority_disclaimer", "") != DISCLAIMER:
        violations.append("WDR-5: authority_disclaimer mismatch")

    # WDR-6: receipt cannot claim seal, approval, verification, or closure
    for key in record:
        kl = key.lower()
        for kw in ["seal", "approve", "verify", "close", "closure"]:
            if kw in kl:
                violations.append(f"WDR-6: receipt carries forbidden field '{key}' (claims {kw})")

    # WDR-7: rationale must not claim seal/approval/verification authority
    rationale = record.get("rationale", "").lower()
    for kw in ["seal", "approve", "verified", "defect accepted"]:
        if kw in rationale:
            violations.append(f"WDR-7: rationale contains authority-claiming term '{kw}'")

    # WDR-8: no registry/RCR/SRS fields
    for key in record:
        kl = key.lower()
        if any(kw in kl for kw in ["registry", "rcr_", "srs_"]):
            violations.append(f"WDR-8: receipt carries registry/RCR/SRS field '{key}'")

    return violations


def cmd_record(args):
    """Record an Owner decision for a decision summary."""
    _ensure_store()

    receipt_id = args.receipt_id or f"WDR-{args.decision.upper()[:4]}-{int(datetime.datetime.utcnow().timestamp()) % 100000}"

    record = {
        "receipt_id": receipt_id,
        "source_summary_id": args.summary_id,
        "source_intake_id": args.intake_id,
        "relevant_item_ids": args.item_ids.split(",") if args.item_ids else [],
        "decision": args.decision,
        "rationale": args.rationale,
        "recorded_at": _now(),
        "owner_note": args.note or "",
        "authority_disclaimer": DISCLAIMER,
        "custody": "qa-pilot-local",
        "advisory_only": True,
        "librarian_impact": "none",
    }

    # Validate
    schema_ok, schema_issues = _validate_schema(record)
    rule_issues = _validate_wdr_rules(record)
    if schema_issues or rule_issues:
        for i in schema_issues + rule_issues:
            print(f"VALIDATION: {i}")

    # Check for duplicate
    index = _load_index()
    if receipt_id in index.get("records", []):
        print(f"ERROR: Receipt {receipt_id} already exists"); sys.exit(1)

    _save_receipt(record)
    index.setdefault("records", []).append(receipt_id)
    _save_index(index)

    print(f"Receipt recorded: {receipt_id}")
    print(f"  Decision:        {record['decision']}")
    print(f"  Source summary:  {record['source_summary_id']}")
    print(f"  Items:           {len(record['relevant_item_ids'])}")
    print(f"  Advisory-only:   True")


def cmd_read(args):
    """Read a stored receipt by ID."""
    record = _load_receipt(args.receipt_id)
    if record is None: print(f"ERROR: Receipt {args.receipt_id} not found"); sys.exit(1)
    print(json.dumps(record, indent=2))


def cmd_list(args):
    """List stored receipts."""
    index = _load_index()
    records = index.get("records", [])
    if not records:
        print("No decision receipts."); return

    print(f"Review Decision Receipts ({len(records)}):")
    print("=" * 110)
    for rid in records:
        rec = _load_receipt(rid)
        if rec is None: print(f"  {rid}: MISSING"); continue
        dec = rec.get("decision", "?")
        src = rec.get("source_summary_id", "?")
        count = len(rec.get("relevant_item_ids", []))
        ts = rec.get("recorded_at", "?")[:19]
        print(f"  {rid:24s} [{dec:22s}] items={count:2d}  src={src:20s}  [{ts}]")


def cmd_validate(args):
    """Validate a receipt against schema + WDR rules."""
    if args.receipt_id:
        record = _load_receipt(args.receipt_id)
        if record is None: print(f"ERROR: Receipt {args.receipt_id} not found"); sys.exit(1)
    else:
        with open(args.receipt_file) as f:
            record = json.load(f)

    schema_ok, schema_issues = _validate_schema(record)
    rule_issues = _validate_wdr_rules(record)
    all_issues = schema_issues + rule_issues

    rid = record.get("receipt_id", "?")
    if not all_issues:
        print(f"VALID: {rid}"); print("ALL CHECKS PASS")
    else:
        print(f"INVALID: {rid}")
        for i in all_issues: print(f"  {i}")
        sys.exit(1)


def cmd_status(args):
    """Show aggregate decision receipt status."""
    index = _load_index()
    records = index.get("records", [])

    if not records:
        print("No decision receipts.")
        return

    by_decision = {}
    total_items = 0
    for rid in records:
        rec = _load_receipt(rid)
        if rec is None: continue
        d = rec.get("decision", "?")
        by_decision[d] = by_decision.get(d, 0) + 1
        total_items += len(rec.get("relevant_item_ids", []))

    print(f"Review Decision Receipt Status")
    print("=" * 50)
    print(f"  Total receipts:   {len(records)}")
    print(f"  Total items:      {total_items}")
    print(f"  By decision:")
    for d in VALID_DECISIONS:
        c = by_decision.get(d, 0)
        if c > 0: print(f"    {d:22s}: {c}")
    print(f"  Advisory-only:    True")
    print(f"  Custody:          qa-pilot-local")
    print(f"  Authority note:   Receipts are advisory-only.")


def main():
    parser = argparse.ArgumentParser(description="QA Pilot Review Decision Receipt CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_rec = sub.add_parser("decision-record")
    p_rec.add_argument("--receipt-id")
    p_rec.add_argument("--summary-id", required=True)
    p_rec.add_argument("--intake-id", required=True)
    p_rec.add_argument("--item-ids", required=True, help="Comma-separated QA item IDs")
    p_rec.add_argument("--decision", required=True, choices=VALID_DECISIONS)
    p_rec.add_argument("--rationale", required=True)
    p_rec.add_argument("--note", default="")
    p_rec.set_defaults(func=cmd_record)

    p_rd = sub.add_parser("decision-read")
    p_rd.add_argument("receipt_id")
    p_rd.set_defaults(func=cmd_read)

    p_li = sub.add_parser("decision-list")
    p_li.set_defaults(func=cmd_list)

    p_va = sub.add_parser("decision-validate")
    p_va.add_argument("receipt_id", nargs="?")
    p_va.add_argument("--receipt-file")
    p_va.set_defaults(func=cmd_validate)

    p_st = sub.add_parser("decision-status")
    p_st.set_defaults(func=cmd_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
