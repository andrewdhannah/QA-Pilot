#!/usr/bin/env python3
"""
QA Pilot Workbench Handoff Review Outcome CLI.

Commands:
  outcome-record    Record a downstream review outcome for a handoff intake
  outcome-read      Read a stored outcome by ID
  outcome-list      List stored outcomes
  outcome-validate  Validate an outcome against schema + HO rules
  outcome-status    Show aggregate outcome status

Authority boundaries:
  Outcome records downstream review posture only.
  It does not execute work, authorize execution, approve intake,
  verify evidence, close items, mutate the handoff/source chain,
  or seal anything.
"""
import argparse, json, os, sys, datetime
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "workbench-handoff-review-outcomes")
STORE_INDEX = os.path.join(STORE_DIR, "outcome-index.json")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-workbench-handoff-review-outcome.schema.json")
HI_STORE_DIR = os.path.join(PROJECT_ROOT, "data", "workbench-action-handoff-intake")
DISCLAIMER = "This handoff review outcome records downstream review posture only. It does not execute work, authorize execution, approve intake, verify evidence, close workbench items, mutate the handoff/source chain, or seal anything. Custody is qa-pilot-local. Librarian impact is none."
VALID_OUTCOMES = ["ready_for_owner_action", "needs_revision", "blocked", "rejected"]

def _now(): return datetime.datetime.utcnow().isoformat() + "Z"
def _ensure_store():
    os.makedirs(STORE_DIR, exist_ok=True)
    if not os.path.exists(STORE_INDEX):
        with open(STORE_INDEX, "w") as f: json.dump({"records": [], "last_updated": _now()}, f, indent=2)
def _load_index():
    _ensure_store()
    with open(STORE_INDEX) as f: return json.load(f)
def _save_index(index):
    index["last_updated"] = _now()
    with open(STORE_INDEX, "w") as f: json.dump(index, f, indent=2)
def _load_outcome(oid):
    path = os.path.join(STORE_DIR, f"{oid}.json")
    if not os.path.exists(path): return None
    with open(path) as f: return json.load(f)
def _save_outcome(record):
    with open(os.path.join(STORE_DIR, f"{record['outcome_id']}.json"), "w") as f: json.dump(record, f, indent=2)
def _load_handoff(hid):
    path = os.path.join(HI_STORE_DIR, f"{hid}.json")
    if os.path.exists(path):
        with open(path) as f: return json.load(f)
    return None

def _validate_schema(record):
    try:
        import jsonschema
        with open(SCHEMA_PATH) as f: schema = json.load(f)
        try:
            jsonschema.validate(record, schema); return True, []
        except jsonschema.exceptions.ValidationError as e: return False, [f"schema violation: {e.message}"]
    except ImportError: return True, []

def _validate_ho_rules(record):
    violations = []
    if record.get("outcome_state") not in VALID_OUTCOMES: violations.append(f"HO-1: outcome_state must be one of {VALID_OUTCOMES}")
    if not record.get("advisory_only", False): violations.append("HO-2: advisory_only must be True")
    if record.get("custody", "") != "qa-pilot-local": violations.append("HO-3: custody must be qa-pilot-local")
    if record.get("librarian_impact", "") != "none": violations.append("HO-4: librarian_impact must be 'none'")
    if record.get("authority_disclaimer", "") != DISCLAIMER: violations.append("HO-5: authority_disclaimer mismatch")
    forbidden = ["executed_","execution_result","authorizes_execution","seal_","sealed",
                 "approval_status","approved_by","evidence_verified","items_closed",
                 "mutates_handoff","mutates_intake","mutates_summary","mutates_receipt","mutates_packet","mutates_export"]
    for key in record:
        kl = key.lower()
        for p in forbidden:
            if p in kl: violations.append(f"HO-6: forbidden field '{key}' claims {p.replace('_',' ')}")
    summary = record.get("review_summary", "").lower()
    for kw in ["executed","authorizes","seal","approved","verified","closed","defect accepted"]:
        if kw in summary: violations.append(f"HO-7: review_summary contains authority-claiming term '{kw}'")
    for key in record:
        kl = key.lower()
        if any(kw in kl for kw in ["registry","rcr_","srs_"]): violations.append(f"HO-8: outcome carries registry/RCR/SRS field '{key}'")
    return violations

def cmd_record(args):
    _ensure_store()
    handoff = _load_handoff(args.handoff_id)
    if handoff is None: print(f"ERROR: Handoff {args.handoff_id} not found"); sys.exit(1)
    oid = args.outcome_id or f"HO-{handoff.get('source_action_packet_id','UNKN').split('-')[-1]}-{int(datetime.datetime.utcnow().timestamp()) % 10000}"
    record = {
        "outcome_id": oid, "source_handoff_id": args.handoff_id,
        "source_export_id": handoff.get("source_export_id",""),
        "source_action_packet_id": handoff.get("source_action_packet_id",""),
        "source_receipt_id": handoff.get("source_receipt_id",""),
        "source_summary_id": handoff.get("source_summary_id",""),
        "source_intake_id": handoff.get("source_intake_id",""),
        "source_item_ids": handoff.get("source_item_ids",[]),
        "outcome_state": args.outcome_state, "review_summary": args.review_summary,
        "recorded_at": _now(), "authority_disclaimer": DISCLAIMER,
        "custody": "qa-pilot-local", "advisory_only": True, "librarian_impact": "none",
    }
    schema_ok, schema_issues = _validate_schema(record)
    rule_issues = _validate_ho_rules(record)
    if schema_issues or rule_issues:
        for i in schema_issues + rule_issues: print(f"VALIDATION: {i}")
    index = _load_index()
    if oid in index.get("records", []): print(f"ERROR: Outcome {oid} already exists"); sys.exit(1)
    _save_outcome(record); index.setdefault("records", []).append(oid); _save_index(index)
    print(f"Outcome recorded: {oid}"); print(f"  State:          {record['outcome_state']}")
    print(f"  Handoff:        {record['source_handoff_id']}"); print(f"  Advisory-only:  True")

def cmd_read(args):
    record = _load_outcome(args.outcome_id)
    if record is None: print(f"ERROR: Outcome {args.outcome_id} not found"); sys.exit(1)
    print(json.dumps(record, indent=2))

def cmd_list(args):
    index = _load_index(); records = index.get("records", [])
    if not records: print("No review outcomes."); return
    print(f"Handoff Review Outcomes ({len(records)}):")
    print("=" * 120)
    for oid in records:
        rec = _load_outcome(oid)
        if rec is None: print(f"  {oid}: MISSING"); continue
        hid = rec.get("source_handoff_id", "?"); st = rec.get("outcome_state", "?")
        count = len(rec.get("source_item_ids", [])); ts = rec.get("recorded_at", "?")[:19]
        print(f"  {oid:24s} [{st:24s}] items={count:2d}  handoff={hid:20s}  [{ts}]")

def cmd_validate(args):
    if args.outcome_id:
        record = _load_outcome(args.outcome_id)
        if record is None: print(f"ERROR: Outcome {args.outcome_id} not found"); sys.exit(1)
    else:
        with open(args.outcome_file) as f: record = json.load(f)
    schema_ok, schema_issues = _validate_schema(record)
    rule_issues = _validate_ho_rules(record)
    all_issues = schema_issues + rule_issues
    oid = record.get("outcome_id", "?")
    if not all_issues: print(f"VALID: {oid}"); print("ALL CHECKS PASS")
    else: print(f"INVALID: {oid}"); [print(f"  {i}") for i in all_issues]; sys.exit(1)

def cmd_status(args):
    index = _load_index(); records = index.get("records", [])
    if not records: print("No review outcomes."); return
    by_state = {}; total_items = 0
    for oid in records:
        rec = _load_outcome(oid)
        if rec is None: continue
        s = rec.get("outcome_state", "?"); by_state[s] = by_state.get(s, 0) + 1
        total_items += len(rec.get("source_item_ids", []))
    print(f"Handoff Review Outcome Status"); print("=" * 50)
    print(f"  Total outcomes:   {len(records)}"); print(f"  Total items:      {total_items}")
    print(f"  By state:"); [print(f"    {s:24s}: {c}") for s, c in sorted(by_state.items())]
    print(f"  Advisory-only:    True")

def main():
    parser = argparse.ArgumentParser(description="QA Pilot Handoff Review Outcome CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    p_re = sub.add_parser("outcome-record")
    p_re.add_argument("handoff_id"); p_re.add_argument("--outcome-id"); p_re.add_argument("--outcome-state", required=True, choices=VALID_OUTCOMES)
    p_re.add_argument("--review-summary", required=True); p_re.set_defaults(func=cmd_record)
    p_rd = sub.add_parser("outcome-read"); p_rd.add_argument("outcome_id"); p_rd.set_defaults(func=cmd_read)
    p_li = sub.add_parser("outcome-list"); p_li.set_defaults(func=cmd_list)
    p_va = sub.add_parser("outcome-validate"); p_va.add_argument("outcome_id", nargs="?"); p_va.add_argument("--outcome-file"); p_va.set_defaults(func=cmd_validate)
    p_st = sub.add_parser("outcome-status"); p_st.set_defaults(func=cmd_status)
    args = parser.parse_args(); args.func(args)

if __name__ == "__main__":
    main()
