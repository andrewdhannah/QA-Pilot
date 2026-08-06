#!/usr/bin/env python3
"""QA Pilot Workbench Owner Action Readiness CLI."""
import argparse, json, os, sys, datetime
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "workbench-owner-action-readiness")
STORE_INDEX = os.path.join(STORE_DIR, "readiness-index.json")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-workbench-owner-action-readiness.schema.json")
HO_STORE_DIR = os.path.join(PROJECT_ROOT, "data", "workbench-handoff-review-outcomes")
DISCLAIMER = "This readiness record derives action readiness from the full workbench chain for Owner review only. It does not authorize action, execute work, approve intake, verify evidence, close workbench items, mutate the chain, or seal anything. Custody is qa-pilot-local. Librarian impact is none."
VALID_STATES = ["ready_for_owner_decision", "needs_revision", "blocked", "not_ready"]
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
def _load_rd(rid):
    path = os.path.join(STORE_DIR, f"{rid}.json")
    if not os.path.exists(path): return None
    with open(path) as f: return json.load(f)
def _save_rd(record):
    with open(os.path.join(STORE_DIR, f"{record['readiness_id']}.json"), "w") as f: json.dump(record, f, indent=2)
def _load_outcome(oid):
    path = os.path.join(HO_STORE_DIR, f"{oid}.json")
    if os.path.exists(path):
        with open(path) as f: return json.load(f)
    return None
def _validate_schema(record):
    try:
        import jsonschema
        with open(SCHEMA_PATH) as f: schema = json.load(f)
        try: jsonschema.validate(record, schema); return True, []
        except jsonschema.exceptions.ValidationError as e: return False, [f"schema violation: {e.message}"]
    except ImportError: return True, []
def _validate_rd_rules(record):
    violations = []
    if record.get("readiness_state") not in VALID_STATES: violations.append(f"RD-1: readiness_state must be one of {VALID_STATES}")
    if not record.get("advisory_only", False): violations.append("RD-2: advisory_only must be True")
    if record.get("custody", "") != "qa-pilot-local": violations.append("RD-3: custody must be qa-pilot-local")
    if record.get("librarian_impact", "") != "none": violations.append("RD-4: librarian_impact must be 'none'")
    if record.get("authority_disclaimer", "") != DISCLAIMER: violations.append("RD-5: authority_disclaimer mismatch")
    forbidden = ["executed_","execution_result","authorizes_execution","seal_","sealed",
                 "approval_status","approved_by","evidence_verified","items_closed",
                 "mutates_outcome","mutates_handoff","mutates_intake","mutates_summary","mutates_receipt","mutates_packet","mutates_export"]
    for key in record:
        for p in forbidden:
            if p in key.lower(): violations.append(f"RD-6: forbidden field '{key}' claims {p.replace('_',' ')}")
    rationale = record.get("readiness_rationale", "").lower()
    for kw in ["executed","authorizes","seal","approved","verified","closed","defect accepted"]:
        if kw in rationale: violations.append(f"RD-7: readiness_rationale contains authority-claiming term '{kw}'")
    for key in record:
        kl = key.lower()
        if any(kw in kl for kw in ["registry","rcr_","srs_"]): violations.append(f"RD-8: readiness carries registry/RCR/SRS field '{key}'")
    return violations
def cmd_create(args):
    _ensure_store()
    outcome = _load_outcome(args.outcome_id)
    if outcome is None: print(f"ERROR: Outcome {args.outcome_id} not found"); sys.exit(1)
    rid = args.readiness_id or f"RD-{outcome.get('source_action_packet_id','UNKN').split('-')[-1]}-{int(datetime.datetime.utcnow().timestamp()) % 10000}"
    record = {
        "readiness_id": rid, "source_outcome_id": args.outcome_id,
        "source_handoff_id": outcome.get("source_handoff_id",""),
        "source_export_id": outcome.get("source_export_id",""),
        "source_action_packet_id": outcome.get("source_action_packet_id",""),
        "source_receipt_id": outcome.get("source_receipt_id",""),
        "source_summary_id": outcome.get("source_summary_id",""),
        "source_intake_id": outcome.get("source_intake_id",""),
        "source_item_ids": outcome.get("source_item_ids",[]),
        "readiness_state": args.readiness_state, "readiness_rationale": args.rationale,
        "recorded_at": _now(), "authority_disclaimer": DISCLAIMER,
        "custody": "qa-pilot-local", "advisory_only": True, "librarian_impact": "none",
    }
    schema_ok, schema_issues = _validate_schema(record)
    rule_issues = _validate_rd_rules(record)
    if schema_issues or rule_issues:
        for i in schema_issues + rule_issues: print(f"VALIDATION: {i}")
    index = _load_index()
    if rid in index.get("records", []): print(f"ERROR: Readiness {rid} already exists"); sys.exit(1)
    _save_rd(record); index.setdefault("records",[]).append(rid); _save_index(index)
    print(f"Readiness created: {rid}"); print(f"  State:          {record['readiness_state']}")
    print(f"  Outcome:        {record['source_outcome_id']}"); print(f"  Advisory-only:  True")
def cmd_read(args):
    record = _load_rd(args.readiness_id)
    if record is None: print(f"ERROR: Readiness {args.readiness_id} not found"); sys.exit(1)
    print(json.dumps(record, indent=2))
def cmd_list(args):
    index = _load_index(); records = index.get("records", [])
    if not records: print("No readiness records."); return
    print(f"Owner Action Readiness ({len(records)}):")
    print("=" * 120)
    for rid in records:
        rec = _load_rd(rid)
        if rec is None: print(f"  {rid}: MISSING"); continue
        st = rec.get("readiness_state", "?")
        oid = rec.get("source_outcome_id", "?")
        count = len(rec.get("source_item_ids", [])); ts = rec.get("recorded_at", "?")[:19]
        print(f"  {rid:24s} [{st:28s}] items={count:2d}  outcome={oid:20s}  [{ts}]")
def cmd_validate(args):
    if args.readiness_id:
        record = _load_rd(args.readiness_id)
        if record is None: print(f"ERROR: Readiness {args.readiness_id} not found"); sys.exit(1)
    else:
        with open(args.readiness_file) as f: record = json.load(f)
    schema_ok, schema_issues = _validate_schema(record)
    rule_issues = _validate_rd_rules(record)
    all_issues = schema_issues + rule_issues
    rid = record.get("readiness_id", "?")
    if not all_issues: print(f"VALID: {rid}"); print("ALL CHECKS PASS")
    else: print(f"INVALID: {rid}"); [print(f"  {i}") for i in all_issues]; sys.exit(1)
def cmd_status(args):
    index = _load_index(); records = index.get("records", [])
    if not records: print("No readiness records."); return
    by_state = {}; total_items = 0
    for rid in records:
        rec = _load_rd(rid)
        if rec is None: continue
        s = rec.get("readiness_state", "?"); by_state[s] = by_state.get(s, 0) + 1
        total_items += len(rec.get("source_item_ids", []))
    print(f"Owner Action Readiness Status"); print("=" * 50)
    print(f"  Total records:    {len(records)}"); print(f"  Total items:      {total_items}")
    print(f"  By state:"); [print(f"    {s:28s}: {c}") for s, c in sorted(by_state.items())]
    print(f"  Advisory-only:    True")
def main():
    parser = argparse.ArgumentParser(description="QA Pilot Owner Action Readiness CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    p_cr = sub.add_parser("readiness-create")
    p_cr.add_argument("outcome_id"); p_cr.add_argument("--readiness-id")
    p_cr.add_argument("--readiness-state", required=True, choices=VALID_STATES); p_cr.add_argument("--rationale", required=True)
    p_cr.set_defaults(func=cmd_create)
    p_rd = sub.add_parser("readiness-read"); p_rd.add_argument("readiness_id"); p_rd.set_defaults(func=cmd_read)
    p_li = sub.add_parser("readiness-list"); p_li.set_defaults(func=cmd_list)
    p_va = sub.add_parser("readiness-validate"); p_va.add_argument("readiness_id", nargs="?"); p_va.add_argument("--readiness-file"); p_va.set_defaults(func=cmd_validate)
    p_st = sub.add_parser("readiness-status"); p_st.set_defaults(func=cmd_status)
    args = parser.parse_args(); args.func(args)
if __name__ == "__main__":
    main()
