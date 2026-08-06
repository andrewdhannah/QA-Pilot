#!/usr/bin/env python3
"""
QA Pilot Workbench Owner Action Packet CLI.

Commands:
  action-create    Create an Owner action packet from a decision receipt
  action-read      Read a stored action packet by ID
  action-list      List stored action packets
  action-validate  Validate an action packet against schema + AP rules
  action-status    Show aggregate action packet status

Authority boundaries:
  Packet creation records the intended next action path only.
  It does not execute the action, approve intake, verify evidence,
  close items, seal work, mutate source records, or create autonomous
  authority.
"""

import argparse, json, os, sys, datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "workbench-owner-action-packets")
STORE_INDEX = os.path.join(STORE_DIR, "action-index.json")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-workbench-owner-action-packet.schema.json")

DISCLAIMER = "This Owner action packet records the intended next action path only. It does not execute the action, approve intake, verify evidence, close workbench items, seal work, mutate source records, or create autonomous authority. Custody is qa-pilot-local. Librarian impact is none."

VALID_STATES = ["proposed", "owner_authorized", "deferred", "rejected"]
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


def _load_packet(packet_id):
    path = os.path.join(STORE_DIR, f"{packet_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def _save_packet(record):
    path = os.path.join(STORE_DIR, f"{record['action_packet_id']}.json")
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


def _validate_ap_rules(record):
    """Validate an action packet against AP-1 through AP-8 rules."""
    violations = []

    # AP-1: action_state must be valid enum
    if record.get("action_state") not in VALID_STATES:
        violations.append(f"AP-1: action_state must be one of {VALID_STATES}")

    # AP-2: advisory_only must be True
    if not record.get("advisory_only", False):
        violations.append("AP-2: advisory_only must be True")

    # AP-3: custody must be qa-pilot-local
    if record.get("custody", "") != "qa-pilot-local":
        violations.append("AP-3: custody must be qa-pilot-local")

    # AP-4: librarian_impact must be none
    if record.get("librarian_impact", "") != "none":
        violations.append("AP-4: librarian_impact must be 'none'")

    # AP-5: authority_disclaimer must match
    if record.get("authority_disclaimer", "") != DISCLAIMER:
        violations.append("AP-5: authority_disclaimer mismatch")

    # AP-6: packet cannot claim execution, seal, verification, closure, or mutation
    forbidden_patterns = ["executed", "execution_result", "seal_action", "seal_scope",
                          "evidence_verified", "items_closed", "mutates_"]
    for key in record:
        kl = key.lower()
        for pattern in forbidden_patterns:
            if pattern in kl:
                violations.append(f"AP-6: forbidden field '{key}' claims {pattern.replace('_', ' ')}")

    # AP-7: rationale must not claim autonomous execution, seal, or closure authority
    rationale = record.get("rationale", "").lower()
    for kw in ["executed autonomously", "seal", "approved", "verified", "closed", "defect accepted"]:
        if kw in rationale:
            violations.append(f"AP-7: rationale contains authority-claiming term '{kw}'")

    # AP-8: no registry/RCR/SRS fields
    for key in record:
        kl = key.lower()
        if any(kw in kl for kw in ["registry", "rcr_", "srs_"]):
            violations.append(f"AP-8: packet carries registry/RCR/SRS field '{key}'")

    return violations


def cmd_create(args):
    """Create an Owner action packet."""
    _ensure_store()

    packet_id = args.packet_id or f"AP-{args.state.upper()[:4]}-{int(datetime.datetime.utcnow().timestamp()) % 100000}"

    evidence_ids = args.evidence_ids.split(",") if args.evidence_ids else []
    evidence_ids = [e.strip() for e in evidence_ids if e.strip()]

    record = {
        "action_packet_id": packet_id,
        "source_receipt_id": args.receipt_id,
        "source_summary_id": args.summary_id,
        "source_intake_id": args.intake_id,
        "source_item_ids": args.item_ids.split(",") if args.item_ids else [],
        "source_evidence_ids": evidence_ids,
        "action_state": args.state,
        "decision": args.decision,
        "rationale": args.rationale,
        "created_at": _now(),
        "owner_note": args.note or "",
        "authority_disclaimer": DISCLAIMER,
        "custody": "qa-pilot-local",
        "advisory_only": True,
        "librarian_impact": "none",
    }

    # Validate
    schema_ok, schema_issues = _validate_schema(record)
    rule_issues = _validate_ap_rules(record)
    if schema_issues or rule_issues:
        for i in schema_issues + rule_issues:
            print(f"VALIDATION: {i}")

    # Check for duplicate
    index = _load_index()
    if packet_id in index.get("records", []):
        print(f"ERROR: Packet {packet_id} already exists"); sys.exit(1)

    _save_packet(record)
    index.setdefault("records", []).append(packet_id)
    _save_index(index)

    print(f"Action packet created: {packet_id}")
    print(f"  State:           {record['action_state']}")
    print(f"  Decision:        {record['decision']}")
    print(f"  Source receipt:  {record['source_receipt_id']}")
    print(f"  Items:           {len(record['source_item_ids'])}")
    print(f"  Advisory-only:   True")


def cmd_read(args):
    """Read a stored action packet by ID."""
    record = _load_packet(args.packet_id)
    if record is None: print(f"ERROR: Packet {args.packet_id} not found"); sys.exit(1)
    print(json.dumps(record, indent=2))


def cmd_list(args):
    """List stored action packets."""
    index = _load_index()
    records = index.get("records", [])
    if not records:
        print("No action packets."); return

    print(f"Owner Action Packets ({len(records)}):")
    print("=" * 110)
    for pid in records:
        rec = _load_packet(pid)
        if rec is None: print(f"  {pid}: MISSING"); continue
        state = rec.get("action_state", "?")
        dec = rec.get("decision", "?")
        src = rec.get("source_receipt_id", "?")
        count = len(rec.get("source_item_ids", []))
        ts = rec.get("created_at", "?")[:19]
        print(f"  {pid:24s} [{state:18s}] dec={dec:22s} items={count:2d}  src={src:20s}  [{ts}]")


def cmd_validate(args):
    """Validate an action packet against schema + AP rules."""
    if args.packet_id:
        record = _load_packet(args.packet_id)
        if record is None: print(f"ERROR: Packet {args.packet_id} not found"); sys.exit(1)
    else:
        with open(args.packet_file) as f:
            record = json.load(f)

    schema_ok, schema_issues = _validate_schema(record)
    rule_issues = _validate_ap_rules(record)
    all_issues = schema_issues + rule_issues

    pid = record.get("action_packet_id", "?")
    if not all_issues:
        print(f"VALID: {pid}"); print("ALL CHECKS PASS")
    else:
        print(f"INVALID: {pid}")
        for i in all_issues: print(f"  {i}")
        sys.exit(1)


def cmd_status(args):
    """Show aggregate action packet status."""
    index = _load_index()
    records = index.get("records", [])

    if not records:
        print("No action packets.")
        return

    by_state = {}
    by_decision = {}
    total_items = 0
    for pid in records:
        rec = _load_packet(pid)
        if rec is None: continue
        s = rec.get("action_state", "?")
        d = rec.get("decision", "?")
        by_state[s] = by_state.get(s, 0) + 1
        by_decision[d] = by_decision.get(d, 0) + 1
        total_items += len(rec.get("source_item_ids", []))

    print(f"Owner Action Packet Status")
    print("=" * 50)
    print(f"  Total packets:    {len(records)}")
    print(f"  Total items:      {total_items}")
    print(f"  By state:")
    for s in VALID_STATES:
        c = by_state.get(s, 0)
        if c > 0: print(f"    {s:18s}: {c}")
    print(f"  By decision:")
    for d in VALID_DECISIONS:
        c = by_decision.get(d, 0)
        if c > 0: print(f"    {d:22s}: {c}")
    print(f"  Advisory-only:    True")
    print(f"  Custody:          qa-pilot-local")
    print(f"  Authority note:   Action packets record intended action paths only.")


def main():
    parser = argparse.ArgumentParser(description="QA Pilot Owner Action Packet CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_cr = sub.add_parser("action-create")
    p_cr.add_argument("--packet-id")
    p_cr.add_argument("--receipt-id", required=True)
    p_cr.add_argument("--summary-id", required=True)
    p_cr.add_argument("--intake-id", required=True)
    p_cr.add_argument("--item-ids", required=True, help="Comma-separated QA item IDs")
    p_cr.add_argument("--evidence-ids", default="", help="Comma-separated evidence IDs")
    p_cr.add_argument("--state", required=True, choices=VALID_STATES)
    p_cr.add_argument("--decision", required=True, choices=VALID_DECISIONS)
    p_cr.add_argument("--rationale", required=True)
    p_cr.add_argument("--note", default="")
    p_cr.set_defaults(func=cmd_create)

    p_rd = sub.add_parser("action-read")
    p_rd.add_argument("packet_id")
    p_rd.set_defaults(func=cmd_read)

    p_li = sub.add_parser("action-list")
    p_li.set_defaults(func=cmd_list)

    p_va = sub.add_parser("action-validate")
    p_va.add_argument("packet_id", nargs="?")
    p_va.add_argument("--packet-file")
    p_va.set_defaults(func=cmd_validate)

    p_st = sub.add_parser("action-status")
    p_st.set_defaults(func=cmd_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
