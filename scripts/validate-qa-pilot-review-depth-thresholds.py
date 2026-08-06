#!/usr/bin/env python3
"""QA Pilot Review Depth Threshold Validator. TD-1 through TD-8."""
import argparse, json, os, sys, glob
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SCHEMA_PATH = os.path.join(PROJECT_ROOT,"docs","schemas","qa-pilot-review-depth-threshold.schema.json")
STORE_DIR = os.path.join(PROJECT_ROOT,"data","review-depth-thresholds")
STORE_INDEX = os.path.join(STORE_DIR,"threshold-index.json")
DISCLAIMER = "This review-depth threshold evaluation is advisory-only. It does not auto-accept evidence, auto-reject findings, execute work, approve intake, verify evidence, close workbench items, mutate the evidence chain, or seal anything. Owner remains the final decision point. Custody is qa-pilot-local. Librarian impact is none."
VALID_STATES = ["sufficient","needs_more_context","blocked"]
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
    if record.get("threshold_state") not in VALID_STATES: results.append(("TD-1", f"threshold_state must be one of {VALID_STATES}"))
    if record.get("advisory_only") is not True: results.append(("TD-2", "advisory_only must be True"))
    if record.get("custody","") != "qa-pilot-local": results.append(("TD-3", "custody must be qa-pilot-local"))
    if record.get("librarian_impact","") != "none": results.append(("TD-4", "librarian_impact must be 'none'"))
    if record.get("authority_disclaimer","") != DISCLAIMER: results.append(("TD-5", "authority_disclaimer mismatch"))
    forbidden = ["auto_accept","auto_acceptance","auto_reject","auto_rejection","executed_","execution_result",
                 "authorizes_execution","seal_","sealed","approval_status","approved_by",
                 "evidence_verified","items_closed","mutates_evidence","mutates_chain","mutates_outcome"]
    for key in record:
        for p in forbidden:
            if p in key.lower(): results.append(("TD-6", f"forbidden field '{key}' claims {p.replace('_',' ')}"))
    rationale = record.get("rationale","").lower()
    for kw in ["auto-accepted","auto-accept","auto-rejected","auto-reject","executed","authorizes","seal","approved","verified","closed","defect accepted"]:
        if kw in rationale: results.append(("TD-7", f"rationale contains authority-claiming term '{kw}'"))
    for key in record:
        kl = key.lower()
        if any(kw in kl for kw in ["registry","rcr_","srs_"]): results.append(("TD-8", f"threshold carries registry/RCR/SRS field '{key}'"))
    return results
def cmd_fixture(args):
    directory = args.directory or os.path.join(PROJECT_ROOT,"docs","examples","qa-pilot-review-depth-thresholds")
    schema = load_schema()
    if not os.path.isdir(directory): print(f"Fixtures directory not found: {directory}"); sys.exit(1)
    json_files = sorted(glob.glob(os.path.join(directory,"*.json")))
    if not json_files: print(f"No fixture files found in {directory}"); sys.exit(1)
    total=passed=failed=0
    for fpath in json_files:
        fname = os.path.basename(fpath)
        with open(fpath) as f:
            try: record = json.load(f)
            except json.JSONDecodeError as e: print(f"  {fname}: INVALID JSON — {e}"); failed+=1; continue
        total+=1
        schema_ok,schema_issues = validate_schema(record,schema)
        rule_issues = validate_all_rules(record)
        all_issues = schema_issues+rule_issues
        is_valid = fname.startswith("valid-"); is_invalid = fname.startswith("invalid-")
        if is_valid:
            if not all_issues: print(f"  {fname}: PASS"); passed+=1
            else: print(f"  {fname}: FAIL"); [print(f"    [{c}] {d}") for c,d in all_issues]; failed+=1
        elif is_invalid:
            if all_issues: print(f"  {fname}: PASS (rejected)"); [print(f"    [{c}] {d}") for c,d in all_issues[:3]]; passed+=1
            else: print(f"  {fname}: FAIL (expected rejection)"); failed+=1
    print(f"\nFixture validation: {passed} pass, {failed} fail, {total} total")
    if failed>0: sys.exit(1)
def cmd_validate(args):
    schema = load_schema()
    for fpath in args.json_files:
        with open(fpath) as f: record = json.load(f)
        schema_ok,schema_issues = validate_schema(record,schema)
        rule_issues = validate_all_rules(record)
        all_issues = schema_issues+rule_issues
        tid = record.get("threshold_id",fpath)
        if not all_issues: print(f"VALID: {tid}")
        else: print(f"INVALID: {tid}"); [print(f"  [{c}] {d}") for c,d in all_issues]
def cmd_live(args):
    schema = load_schema()
    if not os.path.exists(STORE_INDEX): print("No live threshold store found."); return
    with open(STORE_INDEX) as f: index = json.load(f)
    records = index.get("records",[])
    if not records: print("No live threshold records found."); return
    passed=failed=0
    for tid in records:
        path = os.path.join(STORE_DIR,f"{tid}.json")
        if not os.path.exists(path): print(f"  {tid}: MISSING"); failed+=1; continue
        with open(path) as f: record = json.load(f)
        schema_ok,schema_issues = validate_schema(record,schema)
        rule_issues = validate_all_rules(record)
        all_issues = schema_issues+rule_issues
        if not all_issues: print(f"  {tid}: PASS"); passed+=1
        else: print(f"  {tid}: FAIL"); [print(f"    [{c}] {d}") for c,d in all_issues]; failed+=1
    print(f"\nLive threshold validation: {passed} pass, {failed} fail")
    if failed>0: sys.exit(1)
def main():
    parser = argparse.ArgumentParser(description="QA Pilot Review Depth Threshold Validator")
    sub = parser.add_subparsers(dest="mode",required=True)
    p_f = sub.add_parser("fixture"); p_f.add_argument("directory",nargs="?"); p_f.set_defaults(func=cmd_fixture)
    p_v = sub.add_parser("validate"); p_v.add_argument("json_files",nargs="+"); p_v.set_defaults(func=cmd_validate)
    p_l = sub.add_parser("live"); p_l.set_defaults(func=cmd_live)
    args = parser.parse_args(); args.func(args)
if __name__=="__main__":
    main()
