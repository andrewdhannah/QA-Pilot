#!/usr/bin/env python3
"""
QA Pilot Workbench Action Packet Export CLI.

Commands:
  action-export          Export an action packet for downstream handoff
  action-export-read     Read a stored action export by ID
  action-export-list     List stored action exports
  action-export-validate Validate an action export against schema + AXP rules
  action-export-status   Show aggregate action export status

Authority boundaries:
  Export packages the intended action path for handoff only.
  It does not execute work, authorize execution, approve intake,
  verify evidence, close items, mutate packets, mutate sources,
  or seal anything.
"""

import argparse, json, os, sys, datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "workbench-action-packet-exports")
STORE_INDEX = os.path.join(STORE_DIR, "export-index.json")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-workbench-action-packet-export.schema.json")
AP_STORE_DIR = os.path.join(PROJECT_ROOT, "data", "workbench-owner-action-packets")

DISCLAIMER = "This action packet export packages the intended action path for downstream handoff only. It does not execute work, authorize execution, approve intake, verify evidence, close workbench items, mutate packets, mutate source records, seal anything, or create autonomous authority. Custody is qa-pilot-local. Librarian impact is none."

VALID_AP_STATES = ["proposed", "owner_authorized", "deferred", "rejected"]
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


def _load_export(export_id):
    path = os.path.join(STORE_DIR, f"{export_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def _save_export(record):
    path = os.path.join(STORE_DIR, f"{record['export_id']}.json")
    with open(path, "w") as f:
        json.dump(record, f, indent=2)


def _load_action_packet(packet_id):
    path = os.path.join(AP_STORE_DIR, f"{packet_id}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


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


def _validate_axp_rules(record):
    """Validate an action export against AXP-1 through AXP-8 rules."""
    violations = []

    # AXP-1: action_state must be valid
    if record.get("action_state") not in VALID_AP_STATES:
        violations.append(f"AXP-1: action_state must be one of {VALID_AP_STATES}")

    # AXP-2: advisory_only must be True
    if not record.get("advisory_only", False):
        violations.append("AXP-2: advisory_only must be True")

    # AXP-3: custody must be qa-pilot-local
    if record.get("custody", "") != "qa-pilot-local":
        violations.append("AXP-3: custody must be qa-pilot-local")

    # AXP-4: librarian_impact must be none
    if record.get("librarian_impact", "") != "none":
        violations.append("AXP-4: librarian_impact must be 'none'")

    # AXP-5: authority_disclaimer must match
    if record.get("authority_disclaimer", "") != DISCLAIMER:
        violations.append("AXP-5: authority_disclaimer mismatch")

    # AXP-6: export cannot claim execution, authorization, seal, approval, verification, or closure
    forbidden_patterns = [
        "executed", "execution_result", "authorizes_execution", "seal_", "sealed",
        "approval_status", "approved_by", "evidence_verified", "items_closed",
        "mutates_intake", "mutates_summary", "mutates_receipt", "mutates_packet",
    ]
    for key in record:
        kl = key.lower()
        for pattern in forbidden_patterns:
            if pattern in kl:
                violations.append(f"AXP-6: forbidden field '{key}' claims {pattern.replace('_', ' ')}")

    # AXP-7: rationale must not claim execution, authorization, seal, or closure authority
    rationale = record.get("rationale", "").lower()
    for kw in ["executed", "authorizes", "seal", "approved", "verified", "closed", "defect accepted"]:
        if kw in rationale:
            violations.append(f"AXP-7: rationale contains authority-claiming term '{kw}'")

    # AXP-8: no registry/RCR/SRS fields
    for key in record:
        kl = key.lower()
        if any(kw in kl for kw in ["registry", "rcr_", "srs_"]):
            violations.append(f"AXP-8: export carries registry/RCR/SRS field '{key}'")

    return violations


def cmd_export(args):
    """Export an action packet for downstream handoff."""
    _ensure_store()

    # Load source action packet
    packet = _load_action_packet(args.packet_id)
    if packet is None:
        print(f"ERROR: Action packet {args.packet_id} not found"); sys.exit(1)

    export_id = args.export_id or f"AXPK-{args.packet_id.split('-')[-1]}-{int(datetime.datetime.utcnow().timestamp()) % 10000}"

    evidence_ids = args.evidence_ids.split(",") if args.evidence_ids else packet.get("source_evidence_ids", [])
    evidence_ids = [e.strip() for e in evidence_ids if e.strip()]

    record = {
        "export_id": export_id,
        "source_action_packet_id": args.packet_id,
        "source_receipt_id": packet.get("source_receipt_id", args.receipt_id),
        "source_summary_id": packet.get("source_summary_id", args.summary_id),
        "source_intake_id": packet.get("source_intake_id", args.intake_id),
        "source_item_ids": args.item_ids.split(",") if args.item_ids else packet.get("source_item_ids", []),
        "source_evidence_ids": evidence_ids,
        "action_state": packet.get("action_state", args.state),
        "decision": packet.get("decision", args.decision),
        "rationale": packet.get("rationale", args.rationale),
        "exported_at": _now(),
        "authority_disclaimer": DISCLAIMER,
        "custody": "qa-pilot-local",
        "advisory_only": True,
        "librarian_impact": "none",
    }

    # Validate
    schema_ok, schema_issues = _validate_schema(record)
    rule_issues = _validate_axp_rules(record)
    if schema_issues or rule_issues:
        for i in schema_issues + rule_issues:
            print(f"VALIDATION: {i}")
        if args.strict:
            print("ERROR: Strict mode – rejecting"); sys.exit(1)

    # Check duplicate
    index = _load_index()
    if export_id in index.get("records", []):
        print(f"ERROR: Export {export_id} already exists"); sys.exit(1)

    _save_export(record)
    index.setdefault("records", []).append(export_id)
    _save_index(index)

    print(f"Action export created: {export_id}")
    print(f"  Source packet:   {record['source_action_packet_id']}")
    print(f"  State:           {record['action_state']}")
    print(f"  Decision:        {record['decision']}")
    print(f"  Items:           {len(record['source_item_ids'])}")
    print(f"  Advisory-only:   True")


def cmd_read(args):
    """Read a stored action export by ID."""
    record = _load_export(args.export_id)
    if record is None: print(f"ERROR: Export {args.export_id} not found"); sys.exit(1)
    print(json.dumps(record, indent=2))


def cmd_list(args):
    """List stored action exports."""
    index = _load_index()
    records = index.get("records", [])
    if not records:
        print("No action exports."); return

    print(f"Action Packet Exports ({len(records)}):")
    print("=" * 110)
    for eid in records:
        rec = _load_export(eid)
        if rec is None: print(f"  {eid}: MISSING"); continue
        src = rec.get("source_action_packet_id", "?")
        state = rec.get("action_state", "?")
        dec = rec.get("decision", "?")
        count = len(rec.get("source_item_ids", []))
        ts = rec.get("exported_at", "?")[:19]
        print(f"  {eid:24s} [{state:18s}] dec={dec:22s} items={count:2d}  src={src:20s}  [{ts}]")


def cmd_validate(args):
    """Validate an action export against schema + AXP rules."""
    if args.export_id:
        record = _load_export(args.export_id)
        if record is None: print(f"ERROR: Export {args.export_id} not found"); sys.exit(1)
    else:
        with open(args.export_file) as f:
            record = json.load(f)

    schema_ok, schema_issues = _validate_schema(record)
    rule_issues = _validate_axp_rules(record)
    all_issues = schema_issues + rule_issues

    eid = record.get("export_id", "?")
    if not all_issues:
        print(f"VALID: {eid}"); print("ALL CHECKS PASS")
    else:
        print(f"INVALID: {eid}")
        for i in all_issues: print(f"  {i}")
        sys.exit(1)


def cmd_status(args):
    """Show aggregate action export status."""
    index = _load_index()
    records = index.get("records", [])

    if not records:
        print("No action exports.")
        return

    by_state = {}
    by_decision = {}
    total_items = 0
    for eid in records:
        rec = _load_export(eid)
        if rec is None: continue
        s = rec.get("action_state", "?")
        d = rec.get("decision", "?")
        by_state[s] = by_state.get(s, 0) + 1
        by_decision[d] = by_decision.get(d, 0) + 1
        total_items += len(rec.get("source_item_ids", []))

    print(f"Action Export Status")
    print("=" * 50)
    print(f"  Total exports:    {len(records)}")
    print(f"  Total items:      {total_items}")
    print(f"  By state:")
    for s in VALID_AP_STATES:
        c = by_state.get(s, 0)
        if c > 0: print(f"    {s:18s}: {c}")
    print(f"  By decision:")
    for d in VALID_DECISIONS:
        c = by_decision.get(d, 0)
        if c > 0: print(f"    {d:22s}: {c}")
    print(f"  Advisory-only:    True")
    print(f"  Authority note:   Exports package action paths for handoff only.")


def main():
    parser = argparse.ArgumentParser(description="QA Pilot Action Packet Export CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ex = sub.add_parser("action-export")
    p_ex.add_argument("packet_id", help="Source action packet ID")
    p_ex.add_argument("--export-id")
    p_ex.add_argument("--receipt-id", help="Override receipt ID")
    p_ex.add_argument("--summary-id", help="Override summary ID")
    p_ex.add_argument("--intake-id", help="Override intake ID")
    p_ex.add_argument("--item-ids", help="Comma-separated item IDs (override)")
    p_ex.add_argument("--evidence-ids", help="Comma-separated evidence IDs")
    p_ex.add_argument("--state", choices=VALID_AP_STATES, help="Override state")
    p_ex.add_argument("--decision", choices=VALID_DECISIONS, help="Override decision")
    p_ex.add_argument("--rationale", help="Override rationale")
    p_ex.add_argument("--strict", action="store_true")
    p_ex.set_defaults(func=cmd_export)

    p_rd = sub.add_parser("action-export-read")
    p_rd.add_argument("export_id")
    p_rd.set_defaults(func=cmd_read)

    p_li = sub.add_parser("action-export-list")
    p_li.set_defaults(func=cmd_list)

    p_va = sub.add_parser("action-export-validate")
    p_va.add_argument("export_id", nargs="?")
    p_va.add_argument("--export-file")
    p_va.set_defaults(func=cmd_validate)

    p_st = sub.add_parser("action-export-status")
    p_st.set_defaults(func=cmd_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
