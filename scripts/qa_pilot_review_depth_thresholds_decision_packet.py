#!/usr/bin/env python3
"""QA Pilot Review Depth Thresholds Decision Packet CLI."""
import argparse, json, os, sys, datetime
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "review-decision-packets")
STORE_INDEX = os.path.join(STORE_DIR, "packet-index.json")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-pilot-review-depth-thresholds-decision-packet.schema.json")
TD_STORE_DIR = os.path.join(PROJECT_ROOT, "data", "review-depth-thresholds")
DISCLAIMER = "This decision packet connects evidence-depth posture to Owner review. It does not auto-accept evidence, auto-reject findings, approve intake, verify evidence, close workbench items, execute work, seal anything, or create autonomous authority. Owner is the only decision authority. Custody is qa-pilot-local. Librarian impact is none."
VALID_PACKET_STATES = ["prepared", "needs_owner_review", "deferred", "closed_by_owner"]
VALID_TD_STATES = ["sufficient", "needs_more_context", "blocked"]
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
def _load_packet(pid):
    path = os.path.join(STORE_DIR, f"{pid}.json")
    if not os.path.exists(path): return None
    with open(path) as f: return json.load(f)
def _save_packet(record):
    with open(os.path.join(STORE_DIR, f"{record['packet_id']}.json"), "w") as f: json.dump(record, f, indent=2)
def _load_threshold(tid):
    path = os.path.join(TD_STORE_DIR, f"{tid}.json")
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
def _validate_dp_rules(record):
    violations = []
    if record.get("packet_state") not in VALID_PACKET_STATES: violations.append(f"DP-1: packet_state must be one of {VALID_PACKET_STATES}")
    if not record.get("advisory_only", False): violations.append("DP-2: advisory_only must be True")
    if record.get("custody", "") != "qa-pilot-local": violations.append("DP-3: custody must be qa-pilot-local")
    if record.get("librarian_impact", "") != "none": violations.append("DP-4: librarian_impact must be 'none'")
    if record.get("authority_disclaimer", "") != DISCLAIMER: violations.append("DP-5: authority_disclaimer mismatch")
    forbidden = ["auto_accept","auto_acceptance","auto_reject","auto_rejection","executed_","execution_result",
                 "authorizes_execution","seal_","sealed","approval_status","approved_by",
                 "evidence_verified","items_closed","mutates_evidence","mutates_bundle","mutates_packet"]
    for key in record:
        for p in forbidden:
            if p in key.lower(): violations.append(f"DP-6: forbidden field '{key}' claims {p.replace('_',' ')}")
    summary = record.get("review_summary", "").lower()
    for kw in ["auto-accepted","auto-accept","auto-rejected","auto-reject","executed","authorizes","seal","approved","verified","closed","defect accepted"]:
        if kw in summary: violations.append(f"DP-7: review_summary contains authority-claiming term '{kw}'")
    for key in record:
        kl = key.lower()
        if any(kw in kl for kw in ["registry","rcr_","srs_"]): violations.append(f"DP-8: packet carries registry/RCR/SRS field '{key}'")
    return violations
def cmd_create(args):
    _ensure_store()
    threshold = _load_threshold(args.threshold_id)
    if threshold is None: print(f"ERROR: Threshold {args.threshold_id} not found"); sys.exit(1)
    pid = args.packet_id or f"DP-TD-{args.threshold_id.split('-')[-1]}-{int(datetime.datetime.utcnow().timestamp()) % 10000}"
    ctx = threshold.get("source_evidence_context", {})
    record = {
        "packet_id": pid, "source_threshold_id": args.threshold_id,
        "source_evidence_bundle_ref": ctx.get("evidence_bundle_ref", args.bundle_ref or "E4-BUNDLE-001"),
        "source_result_packet_ref": args.result_ref or "",
        "source_consistency_guard_refs": ctx.get("consistency_guard_refs", []),
        "threshold_state": threshold.get("threshold_state", ""),
        "packet_state": args.packet_state, "review_summary": args.review_summary,
        "created_at": _now(), "authority_disclaimer": DISCLAIMER,
        "custody": "qa-pilot-local", "advisory_only": True, "librarian_impact": "none",
    }
    schema_ok, schema_issues = _validate_schema(record)
    rule_issues = _validate_dp_rules(record)
    if schema_issues or rule_issues:
        for i in schema_issues + rule_issues: print(f"VALIDATION: {i}")
    index = _load_index()
    if pid in index.get("records", []): print(f"ERROR: Packet {pid} already exists"); sys.exit(1)
    _save_packet(record); index.setdefault("records",[]).append(pid); _save_index(index)
    print(f"Decision packet created: {pid}"); print(f"  State:          {record['packet_state']}")
    print(f"  TD state:       {record['threshold_state']}"); print(f"  Advisory-only:  True")
def cmd_read(args):
    record = _load_packet(args.packet_id)
    if record is None: print(f"ERROR: Packet {args.packet_id} not found"); sys.exit(1)
    print(json.dumps(record, indent=2))
def cmd_list(args):
    index = _load_index(); records = index.get("records", [])
    if not records: print("No decision packets."); return
    print(f"Decision Packets ({len(records)}):")
    print("=" * 100)
    for pid in records:
        rec = _load_packet(pid)
        if rec is None: print(f"  {pid}: MISSING"); continue
        ps = rec.get("packet_state", "?"); ts = rec.get("threshold_state", "?")
        ct = rec.get("created_at", "?")[:19]
        print(f"  {pid:24s} [{ps:20s}] td={ts:20s}  [{ct}]")
def cmd_validate(args):
    if args.packet_id:
        record = _load_packet(args.packet_id)
        if record is None: print(f"ERROR: Packet {args.packet_id} not found"); sys.exit(1)
    else:
        with open(args.packet_file) as f: record = json.load(f)
    schema_ok, schema_issues = _validate_schema(record)
    rule_issues = _validate_dp_rules(record)
    all_issues = schema_issues + rule_issues
    pid = record.get("packet_id", "?")
    if not all_issues: print(f"VALID: {pid}"); print("ALL CHECKS PASS")
    else: print(f"INVALID: {pid}"); [print(f"  {i}") for i in all_issues]; sys.exit(1)
def cmd_status(args):
    index = _load_index(); records = index.get("records", [])
    if not records: print("No decision packets."); return
    by_pstate = {}; by_tdstate = {}
    for pid in records:
        rec = _load_packet(pid)
        if rec is None: continue
        ps = rec.get("packet_state", "?"); ts = rec.get("threshold_state", "?")
        by_pstate[ps] = by_pstate.get(ps, 0) + 1; by_tdstate[ts] = by_tdstate.get(ts, 0) + 1
    print(f"Decision Packet Status"); print("=" * 50)
    print(f"  Total packets: {len(records)}"); print(f"  By packet state:"); [print(f"    {s:20s}: {c}") for s,c in sorted(by_pstate.items())]
    print(f"  By TD state:"); [print(f"    {s:20s}: {c}") for s,c in sorted(by_tdstate.items())]
    print(f"  Advisory-only: True"); print(f"  Note: Owner is the only decision authority.")
def main():
    parser = argparse.ArgumentParser(description="QA Pilot Review Depth Thresholds Decision Packet CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    p_cr = sub.add_parser("packet-create")
    p_cr.add_argument("threshold_id"); p_cr.add_argument("--packet-id"); p_cr.add_argument("--packet-state", required=True, choices=VALID_PACKET_STATES)
    p_cr.add_argument("--review-summary", required=True); p_cr.add_argument("--bundle-ref"); p_cr.add_argument("--result-ref")
    p_cr.set_defaults(func=cmd_create)
    p_rd = sub.add_parser("packet-read"); p_rd.add_argument("packet_id"); p_rd.set_defaults(func=cmd_read)
    p_li = sub.add_parser("packet-list"); p_li.set_defaults(func=cmd_list)
    p_va = sub.add_parser("packet-validate"); p_va.add_argument("packet_id", nargs="?"); p_va.add_argument("--packet-file"); p_va.set_defaults(func=cmd_validate)
    p_st = sub.add_parser("packet-status"); p_st.set_defaults(func=cmd_status)
    args = parser.parse_args(); args.func(args)
if __name__ == "__main__":
    main()
