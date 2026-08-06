#!/usr/bin/env python3
"""
QA Pilot Workbench Action Handoff Intake CLI.

Commands:
  handoff-intake     Ingest an action packet export for downstream review
  handoff-read       Read a stored handoff intake record by ID
  handoff-list       List stored handoff intake records
  handoff-validate   Validate a handoff intake against schema + HI rules
  handoff-status     Show aggregate handoff intake status

Authority boundaries:
  Intake receives an exported action path for downstream review only.
  It does not execute the action, authorize execution, approve intake,
  verify evidence, close items, mutate source records, or seal anything.
"""

import argparse, json, os, sys, datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "workbench-action-handoff-intake")
STORE_INDEX = os.path.join(STORE_DIR, "handoff-index.json")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-workbench-action-handoff-intake.schema.json")
AXP_STORE_DIR = os.path.join(PROJECT_ROOT, "data", "workbench-action-packet-exports")

DISCLAIMER = "This action handoff intake receives an exported action path for downstream review only. It does not execute the action, authorize execution, approve intake, verify evidence, close workbench items, mutate source records, or seal anything. Custody is qa-pilot-local. Librarian impact is none."

VALID_STATES = ["proposed", "owner_authorized", "deferred", "rejected"]
VALID_DECISIONS = ["accepted_for_action", "authorized", "deferred", "rejected"]
VALID_INTAKE_STATUSES = ["received", "in_review", "completed", "deferred"]


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


def _load_handoff(handoff_id):
    path = os.path.join(STORE_DIR, f"{handoff_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def _save_handoff(record):
    path = os.path.join(STORE_DIR, f"{record['handoff_id']}.json")
    with open(path, "w") as f:
        json.dump(record, f, indent=2)


def _load_export(export_id):
    path = os.path.join(AXP_STORE_DIR, f"{export_id}.json")
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


def _validate_hi_rules(record):
    violations = []
    if record.get("action_state") not in VALID_STATES:
        violations.append(f"HI-1: action_state must be one of {VALID_STATES}")
    if not record.get("advisory_only", False):
        violations.append("HI-2: advisory_only must be True")
    if record.get("custody", "") != "qa-pilot-local":
        violations.append("HI-3: custody must be qa-pilot-local")
    if record.get("librarian_impact", "") != "none":
        violations.append("HI-4: librarian_impact must be 'none'")
    if record.get("authority_disclaimer", "") != DISCLAIMER:
        violations.append("HI-5: authority_disclaimer mismatch")
    forbidden = ["executed_", "execution_result", "authorizes_execution", "seal_", "sealed",
                 "approval_status", "approved_by", "evidence_verified", "items_closed",
                 "mutates_intake", "mutates_summary", "mutates_receipt", "mutates_packet",
                 "mutates_export"]
    for key in record:
        kl = key.lower()
        for p in forbidden:
            if p in kl:
                violations.append(f"HI-6: forbidden field '{key}' claims {p.replace('_', ' ')}")
    rationale = record.get("rationale", "").lower() if record.get("rationale") else ""
    for kw in ["executed", "authorizes", "seal", "approved", "verified", "closed", "defect accepted"]:
        if kw in rationale:
            violations.append(f"HI-7: rationale contains authority-claiming term '{kw}'")
    for key in record:
        kl = key.lower()
        if any(kw in kl for kw in ["registry", "rcr_", "srs_"]):
            violations.append(f"HI-8: intake carries registry/RCR/SRS field '{key}'")
    return violations


def cmd_intake(args):
    _ensure_store()
    record = _load_export(args.export_id)
    if record is None:
        print(f"ERROR: Export {args.export_id} not found"); sys.exit(1)

    handoff_id = args.handoff_id or f"HI-{record.get('source_action_packet_id', 'UNKN').split('-')[-1]}-{int(datetime.datetime.utcnow().timestamp()) % 10000}"

    intake = {
        "handoff_id": handoff_id,
        "source_export_id": args.export_id,
        "source_action_packet_id": record.get("source_action_packet_id", ""),
        "source_receipt_id": record.get("source_receipt_id", ""),
        "source_summary_id": record.get("source_summary_id", ""),
        "source_intake_id": record.get("source_intake_id", ""),
        "source_item_ids": record.get("source_item_ids", []),
        "source_evidence_ids": record.get("source_evidence_ids", []),
        "action_state": record.get("action_state", ""),
        "decision": record.get("decision", ""),
        "rationale": record.get("rationale", ""),
        "intake_status": "received",
        "received_at": _now(),
        "authority_disclaimer": DISCLAIMER,
        "custody": "qa-pilot-local",
        "advisory_only": True,
        "librarian_impact": "none",
    }

    schema_ok, schema_issues = _validate_schema(intake)
    rule_issues = _validate_hi_rules(intake)
    if schema_issues or rule_issues:
        for i in schema_issues + rule_issues: print(f"VALIDATION: {i}")

    index = _load_index()
    if handoff_id in index.get("records", []):
        print(f"ERROR: Handoff {handoff_id} already exists"); sys.exit(1)

    _save_handoff(intake)
    index.setdefault("records", []).append(handoff_id)
    _save_index(index)

    print(f"Handoff intake created: {handoff_id}")
    print(f"  Source export:  {intake['source_export_id']}")
    print(f"  State:          {intake['action_state']}")
    print(f"  Decision:       {intake['decision']}")
    print(f"  Items:          {len(intake['source_item_ids'])}")
    print(f"  Advisory-only:  True")


def cmd_read(args):
    record = _load_handoff(args.handoff_id)
    if record is None: print(f"ERROR: Handoff {args.handoff_id} not found"); sys.exit(1)
    print(json.dumps(record, indent=2))


def cmd_list(args):
    index = _load_index()
    records = index.get("records", [])
    if not records: print("No handoff intakes."); return
    print(f"Action Handoff Intakes ({len(records)}):")
    print("=" * 120)
    for hid in records:
        rec = _load_handoff(hid)
        if rec is None: print(f"  {hid}: MISSING"); continue
        src = rec.get("source_export_id", "?")
        state = rec.get("action_state", "?")
        dec = rec.get("decision", "?")
        count = len(rec.get("source_item_ids", []))
        ts = rec.get("received_at", "?")[:19]
        print(f"  {hid:24s} [{state:18s}] dec={dec:22s} items={count:2d}  src={src:20s}  [{ts}]")


def cmd_validate(args):
    if args.handoff_id:
        record = _load_handoff(args.handoff_id)
        if record is None: print(f"ERROR: Handoff {args.handoff_id} not found"); sys.exit(1)
    else:
        with open(args.handoff_file) as f: record = json.load(f)
    schema_ok, schema_issues = _validate_schema(record)
    rule_issues = _validate_hi_rules(record)
    all_issues = schema_issues + rule_issues
    hid = record.get("handoff_id", "?")
    if not all_issues: print(f"VALID: {hid}"); print("ALL CHECKS PASS")
    else:
        print(f"INVALID: {hid}")
        for i in all_issues: print(f"  {i}"); sys.exit(1)


def cmd_status(args):
    index = _load_index()
    records = index.get("records", [])
    if not records: print("No handoff intakes."); return
    by_state = {}; by_decision = {}; by_istatus = {}; total_items = 0
    for hid in records:
        rec = _load_handoff(hid)
        if rec is None: continue
        s = rec.get("action_state", "?")
        d = rec.get("decision", "?")
        st = rec.get("intake_status", "?")
        by_state[s] = by_state.get(s, 0) + 1
        by_decision[d] = by_decision.get(d, 0) + 1
        by_istatus[st] = by_istatus.get(st, 0) + 1
        total_items += len(rec.get("source_item_ids", []))
    print(f"Action Handoff Intake Status")
    print("=" * 50)
    print(f"  Total intakes:    {len(records)}")
    print(f"  Total items:      {total_items}")
    print(f"  By action state:"); [print(f"    {s:18s}: {c}") for s, c in sorted(by_state.items())]
    print(f"  By intake status:"); [print(f"    {s:18s}: {c}") for s, c in sorted(by_istatus.items())]
    print(f"  Advisory-only:    True")
    print(f"  Authority note:   Handoff intakes are for downstream review only.")


def main():
    parser = argparse.ArgumentParser(description="QA Pilot Action Handoff Intake CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    p_in = sub.add_parser("handoff-intake")
    p_in.add_argument("export_id"); p_in.add_argument("--handoff-id"); p_in.set_defaults(func=cmd_intake)
    p_rd = sub.add_parser("handoff-read"); p_rd.add_argument("handoff_id"); p_rd.set_defaults(func=cmd_read)
    p_li = sub.add_parser("handoff-list"); p_li.set_defaults(func=cmd_list)
    p_va = sub.add_parser("handoff-validate"); p_va.add_argument("handoff_id", nargs="?"); p_va.add_argument("--handoff-file"); p_va.set_defaults(func=cmd_validate)
    p_st = sub.add_parser("handoff-status"); p_st.set_defaults(func=cmd_status)
    args = parser.parse_args(); args.func(args)

if __name__ == "__main__":
    main()
