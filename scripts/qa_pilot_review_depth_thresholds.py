#!/usr/bin/env python3
"""QA Pilot Review Depth Threshold CLI."""
import argparse, json, os, sys, datetime
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "review-depth-thresholds")
STORE_INDEX = os.path.join(STORE_DIR, "threshold-index.json")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-pilot-review-depth-threshold.schema.json")
DISCLAIMER = "This review-depth threshold evaluation is advisory-only. It does not auto-accept evidence, auto-reject findings, execute work, approve intake, verify evidence, close workbench items, mutate the evidence chain, or seal anything. Owner remains the final decision point. Custody is qa-pilot-local. Librarian impact is none."
VALID_STATES = ["sufficient", "needs_more_context", "blocked"]
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
def _load_threshold(tid):
    path = os.path.join(STORE_DIR, f"{tid}.json")
    if not os.path.exists(path): return None
    with open(path) as f: return json.load(f)
def _save_threshold(record):
    with open(os.path.join(STORE_DIR, f"{record['threshold_id']}.json"), "w") as f: json.dump(record, f, indent=2)
def _validate_schema(record):
    try:
        import jsonschema
        with open(SCHEMA_PATH) as f: schema = json.load(f)
        try: jsonschema.validate(record, schema); return True, []
        except jsonschema.exceptions.ValidationError as e: return False, [f"schema violation: {e.message}"]
    except ImportError: return True, []
def _validate_td_rules(record):
    violations = []
    if record.get("threshold_state") not in VALID_STATES: violations.append(f"TD-1: threshold_state must be one of {VALID_STATES}")
    if not record.get("advisory_only", False): violations.append("TD-2: advisory_only must be True")
    if record.get("custody", "") != "qa-pilot-local": violations.append("TD-3: custody must be qa-pilot-local")
    if record.get("librarian_impact", "") != "none": violations.append("TD-4: librarian_impact must be 'none'")
    if record.get("authority_disclaimer", "") != DISCLAIMER: violations.append("TD-5: authority_disclaimer mismatch")
    forbidden = ["auto_accept","auto_acceptance","auto_reject","auto_rejection","executed_","execution_result",
                 "authorizes_execution","seal_","sealed","approval_status","approved_by",
                 "evidence_verified","items_closed","mutates_evidence","mutates_chain","mutates_outcome"]
    for key in record:
        for p in forbidden:
            if p in key.lower(): violations.append(f"TD-6: forbidden field '{key}' claims {p.replace('_',' ')}")
    rationale = record.get("rationale", "").lower()
    for kw in ["auto-accepted","auto-accept","auto-rejected","auto-reject","executed","authorizes","seal","approved","verified","closed","defect accepted"]:
        if kw in rationale: violations.append(f"TD-7: rationale contains authority-claiming term '{kw}'")
    for key in record:
        kl = key.lower()
        if any(kw in kl for kw in ["registry","rcr_","srs_"]): violations.append(f"TD-8: threshold carries registry/RCR/SRS field '{key}'")
    return violations
def cmd_evaluate(args):
    _ensure_store()
    tid = args.threshold_id or f"TD-EVAL-{int(datetime.datetime.utcnow().timestamp()) % 100000}"
    context = {
        "evidence_bundle_ref": args.bundle_ref or "E4-BUNDLE-001",
        "consistency_guard_refs": args.consistency_refs.split(",") if args.consistency_refs else ["RC-01","RC-02","RC-03","RC-04","RC-05","RC-06","RC-07","RC-08","RC-09","RC-10","RC-11"],
        "evidence_item_count": int(args.evidence_count) if args.evidence_count else 0,
        "consistency_check_count": int(args.consistency_total) if args.consistency_total else 0,
        "consistency_pass_count": int(args.consistency_pass) if args.consistency_pass else 0,
    }
    record = {
        "threshold_id": tid,
        "source_evidence_context": context,
        "threshold_state": args.state,
        "rationale": args.rationale,
        "evaluated_at": _now(),
        "authority_disclaimer": DISCLAIMER,
        "custody": "qa-pilot-local",
        "advisory_only": True,
        "librarian_impact": "none",
    }
    schema_ok, schema_issues = _validate_schema(record)
    rule_issues = _validate_td_rules(record)
    if schema_issues or rule_issues:
        for i in schema_issues + rule_issues: print(f"VALIDATION: {i}")
    index = _load_index()
    if tid in index.get("records", []): print(f"ERROR: Threshold {tid} already exists"); sys.exit(1)
    _save_threshold(record); index.setdefault("records",[]).append(tid); _save_index(index)
    print(f"Threshold evaluated: {tid}"); print(f"  State:          {record['threshold_state']}")
    print(f"  Evidence items: {context.get('evidence_item_count',0)}"); print(f"  Advisory-only:  True")
def cmd_read(args):
    record = _load_threshold(args.threshold_id)
    if record is None: print(f"ERROR: Threshold {args.threshold_id} not found"); sys.exit(1)
    print(json.dumps(record, indent=2))
def cmd_list(args):
    index = _load_index(); records = index.get("records", [])
    if not records: print("No review depth thresholds."); return
    print(f"Review Depth Thresholds ({len(records)}):")
    print("=" * 100)
    for tid in records:
        rec = _load_threshold(tid)
        if rec is None: print(f"  {tid}: MISSING"); continue
        st = rec.get("threshold_state", "?"); ec = rec.get("source_evidence_context",{}).get("evidence_item_count",0)
        ts = rec.get("evaluated_at", "?")[:19]
        print(f"  {tid:24s} [{st:20s}] items={ec:2d}  [{ts}]")
def cmd_validate(args):
    if args.threshold_id:
        record = _load_threshold(args.threshold_id)
        if record is None: print(f"ERROR: Threshold {args.threshold_id} not found"); sys.exit(1)
    else:
        with open(args.threshold_file) as f: record = json.load(f)
    schema_ok, schema_issues = _validate_schema(record)
    rule_issues = _validate_td_rules(record)
    all_issues = schema_issues + rule_issues
    tid = record.get("threshold_id", "?")
    if not all_issues: print(f"VALID: {tid}"); print("ALL CHECKS PASS")
    else: print(f"INVALID: {tid}"); [print(f"  {i}") for i in all_issues]; sys.exit(1)
def cmd_status(args):
    index = _load_index(); records = index.get("records", [])
    if not records: print("No review depth thresholds."); return
    by_state = {}; total_items = 0
    for tid in records:
        rec = _load_threshold(tid)
        if rec is None: continue
        s = rec.get("threshold_state", "?"); by_state[s] = by_state.get(s, 0) + 1
        total_items += rec.get("source_evidence_context",{}).get("evidence_item_count",0)
    print(f"Review Depth Threshold Status"); print("=" * 50)
    print(f"  Total evaluations: {len(records)}"); print(f"  Total items:      {total_items}")
    print(f"  By state:"); [print(f"    {s:20s}: {c}") for s, c in sorted(by_state.items())]
    print(f"  Advisory-only:    True"); print(f"  Note: Thresholds do not auto-accept or auto-reject.")
def main():
    parser = argparse.ArgumentParser(description="QA Pilot Review Depth Threshold CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    p_ev = sub.add_parser("threshold-evaluate")
    p_ev.add_argument("--threshold-id"); p_ev.add_argument("--state", required=True, choices=VALID_STATES)
    p_ev.add_argument("--rationale", required=True); p_ev.add_argument("--bundle-ref"); p_ev.add_argument("--consistency-refs")
    p_ev.add_argument("--evidence-count"); p_ev.add_argument("--consistency-total"); p_ev.add_argument("--consistency-pass")
    p_ev.set_defaults(func=cmd_evaluate)
    p_rd = sub.add_parser("threshold-read"); p_rd.add_argument("threshold_id"); p_rd.set_defaults(func=cmd_read)
    p_li = sub.add_parser("threshold-list"); p_li.set_defaults(func=cmd_list)
    p_va = sub.add_parser("threshold-validate"); p_va.add_argument("threshold_id", nargs="?"); p_va.add_argument("--threshold-file"); p_va.set_defaults(func=cmd_validate)
    p_st = sub.add_parser("threshold-status"); p_st.set_defaults(func=cmd_status)
    args = parser.parse_args(); args.func(args)
if __name__ == "__main__":
    main()
