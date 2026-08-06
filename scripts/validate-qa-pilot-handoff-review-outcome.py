#!/usr/bin/env python3
"""QA Workbench Handoff Review Outcome Validator. HO-1 through HO-8."""
import argparse, json, os, sys, glob
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SCHEMA_PATH = os.path.join(PROJECT_ROOT,"docs","schemas","qa-workbench-handoff-review-outcome.schema.json")
STORE_DIR = os.path.join(PROJECT_ROOT,"data","workbench-handoff-review-outcomes")
STORE_INDEX = os.path.join(STORE_DIR,"outcome-index.json")
DISCLAIMER = "This handoff review outcome records downstream review posture only. It does not execute work, authorize execution, approve intake, verify evidence, close workbench items, mutate the handoff/source chain, or seal anything. Custody is qa-pilot-local. Librarian impact is none."
VALID_OUTCOMES = ["ready_for_owner_action","needs_revision","blocked","rejected"]
def load_schema():
    with open(SCHEMA_PATH) as f: return json.load(f)
def validate_schema(record, schema):
    try:
        import jsonschema
        try: jsonschema.validate(record, schema); return True, []
        except jsonschema.exceptions.ValidationError as e: return False, [("SCHEMA", f"schema violation: {e.message}")]
    except ImportError: return True, []
def validate_all_rules(record):
    results = []
    if record.get("outcome_state") not in VALID_OUTCOMES: results.append(("HO-1", f"outcome_state must be one of {VALID_OUTCOMES}"))
    if record.get("advisory_only") is not True: results.append(("HO-2", "advisory_only must be True"))
    if record.get("custody","") != "qa-pilot-local": results.append(("HO-3", "custody must be qa-pilot-local"))
    if record.get("librarian_impact","") != "none": results.append(("HO-4", "librarian_impact must be 'none'"))
    if record.get("authority_disclaimer","") != DISCLAIMER: results.append(("HO-5", "authority_disclaimer mismatch"))
    forbidden = ["executed_","execution_result","authorizes_execution","seal_","sealed",
                 "approval_status","approved_by","evidence_verified","items_closed",
                 "mutates_handoff","mutates_intake","mutates_summary","mutates_receipt","mutates_packet","mutates_export"]
    for key in record:
        for p in forbidden:
            if p in key.lower(): results.append(("HO-6", f"forbidden field '{key}' claims {p.replace('_',' ')}"))
    summary = record.get("review_summary","").lower()
    for kw in ["executed","authorizes","seal","approved","verified","closed","defect accepted"]:
        if kw in summary: results.append(("HO-7", f"review_summary contains authority-claiming term '{kw}'"))
    for key in record:
        kl = key.lower()
        if any(kw in kl for kw in ["registry","rcr_","srs_"]): results.append(("HO-8", f"outcome carries registry/RCR/SRS field '{key}'"))
    return results
def cmd_fixture(args):
    directory = args.directory or os.path.join(PROJECT_ROOT,"docs","examples","qa-pilot-handoff-review-outcome")
    schema = load_schema()
    if not os.path.isdir(directory): print(f"Fixtures directory not found: {directory}"); sys.exit(1)
    json_files = sorted(glob.glob(os.path.join(directory,"*.json")))
    if not json_files: print(f"No fixture files found in {directory}"); sys.exit(1)
    total=passed=failed=0
    for fpath in json_files:
        fname=os.path.basename(fpath)
        with open(fpath) as f:
            try: record=json.load(f)
            except json.JSONDecodeError as e: print(f"  {fname}: INVALID JSON — {e}"); failed+=1; continue
        total+=1
        schema_ok,schema_issues=validate_schema(record,schema)
        rule_issues=validate_all_rules(record)
        all_issues=schema_issues+rule_issues
        is_valid=fname.startswith("valid-"); is_invalid=fname.startswith("invalid-")
        if is_valid:
            if not all_issues: print(f"  {fname}: PASS"); passed+=1
            else: print(f"  {fname}: FAIL"); [print(f"    [{c}] {d}") for c,d in all_issues]; failed+=1
        elif is_invalid:
            if all_issues: print(f"  {fname}: PASS (rejected)"); [print(f"    [{c}] {d}") for c,d in all_issues[:3]]; passed+=1
            else: print(f"  {fname}: FAIL (expected rejection)"); failed+=1
    print(f"\nFixture validation: {passed} pass, {failed} fail, {total} total")
    if failed>0: sys.exit(1)
def cmd_validate(args):
    schema=load_schema()
    for fpath in args.json_files:
        with open(fpath) as f: record=json.load(f)
        schema_ok,schema_issues=validate_schema(record,schema)
        rule_issues=validate_all_rules(record)
        all_issues=schema_issues+rule_issues
        oid=record.get("outcome_id",fpath)
        if not all_issues: print(f"VALID: {oid}")
        else: print(f"INVALID: {oid}"); [print(f"  [{c}] {d}") for c,d in all_issues]
def cmd_live(args):
    schema=load_schema()
    if not os.path.exists(STORE_INDEX): print("No live outcome store found."); return
    with open(STORE_INDEX) as f: index=json.load(f)
    records=index.get("records",[])
    if not records: print("No live outcome records found."); return
    passed=failed=0
    for oid in records:
        path=os.path.join(STORE_DIR,f"{oid}.json")
        if not os.path.exists(path): print(f"  {oid}: MISSING"); failed+=1; continue
        with open(path) as f: record=json.load(f)
        schema_ok,schema_issues=validate_schema(record,schema)
        rule_issues=validate_all_rules(record)
        all_issues=schema_issues+rule_issues
        if not all_issues: print(f"  {oid}: PASS"); passed+=1
        else: print(f"  {oid}: FAIL"); [print(f"    [{c}] {d}") for c,d in all_issues]; failed+=1
    print(f"\nLive outcome validation: {passed} pass, {failed} fail")
    if failed>0: sys.exit(1)
def main():
    parser=argparse.ArgumentParser(description="QA Workbench Handoff Review Outcome Validator")
    sub=parser.add_subparsers(dest="mode",required=True)
    p_f=sub.add_parser("fixture"); p_f.add_argument("directory",nargs="?"); p_f.set_defaults(func=cmd_fixture)
    p_v=sub.add_parser("validate"); p_v.add_argument("json_files",nargs="+"); p_v.set_defaults(func=cmd_validate)
    p_l=sub.add_parser("live"); p_l.set_defaults(func=cmd_live)
    args=parser.parse_args(); args.func(args)
if __name__=="__main__":
    main()
