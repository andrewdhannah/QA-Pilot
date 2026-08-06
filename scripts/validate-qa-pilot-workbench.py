#!/usr/bin/env python3
"""
QA Workbench Validator — validates QA workbench items against schema + business rules.

Modes: fixture, validate, live, chain

Business rules:
  WB-1 through WB-12: item + evidence-link rules
  WL-1 through WL-7: lifecycle rules
  EL-1 through EL-5: evidence-link business rules
"""

import argparse, json, os, sys, glob, subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "workbench-items")
STORE_INDEX = os.path.join(STORE_DIR, "workbench-index.json")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-workbench-item.schema.json")
EVIDENCE_LINK_SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-workbench-evidence-link.schema.json")

VALID_STATUSES = ["draft", "open", "triaged", "evidence_attached", "needs_review", "deferred", "resolved_locally"]

ALLOWED_TRANSITIONS = {
    "draft": ["open"],
    "open": ["triaged"],
    "triaged": ["evidence_attached"],
    "evidence_attached": ["needs_review"],
    "needs_review": ["deferred", "resolved_locally"],
    "deferred": ["open"],
    "resolved_locally": ["open"],
}


def load_schema(path=None):
    with open(path or SCHEMA_PATH) as f:
        return json.load(f)


def validate_schema(item, schema):
    try:
        import jsonschema
        try:
            jsonschema.validate(item, schema)
            return True, []
        except jsonschema.exceptions.ValidationError as e:
            return False, [f"schema violation: {e.message}"]
    except ImportError:
        return True, []


def validate_evidence_link_schema(link):
    schema = load_schema(EVIDENCE_LINK_SCHEMA_PATH)
    return validate_schema(link, schema)


def validate_business_rules(item):
    violations = []
    
    # WB-1: advisory_only
    if not item.get("advisory_only", False):
        violations.append("WB-1: advisory_only must be True")
    
    # WB-2: custody
    if item.get("custody", "") != "qa-pilot-local":
        violations.append("WB-2: custody must be qa-pilot-local")
    
    # WB-3: librarian_impact
    if item.get("librarian_impact", "") != "none":
        violations.append("WB-3: librarian_impact must be 'none'")
    
    # WB-5: authority claims
    auth_patterns = ["this item is approved", "this item is sealed", "claims approval authority",
                     "claims seal authority", "seal authority over", "approved and verified", "this item has authority"]
    for key in ["title", "description"]:
        val = str(item.get(key, "")).lower()
        for p in auth_patterns:
            if p in val:
                violations.append(f"WB-5: item {key} claims authority ('{p}'): '{val[:80]}'")
    
    # WB-7: accepted requires ref
    if item.get("owner_decision_state") == "accepted" and not item.get("owner_decision_ref"):
        violations.append("WB-7: accepted owner_decision_state requires owner_decision_ref")
    
    # WB-8: no registry fields
    for key in item:
        kl = key.lower()
        if any(kw in kl for kw in ["registry", "rcr_", "srs_"]):
            violations.append(f"WB-8: item has registry/RCR/SRS field ('{key}')")
    
    # WQ-1: item must not claim approval/seal authority in queryable fields (title, description, status)
    title = str(item.get("title", "")).lower()
    desc = str(item.get("description", "")).lower()
    for phrase in ["approved and verified", "seal authority", "claims approval", "claims seal"]:
        if phrase in title or phrase in desc:
            violations.append(f"WQ-1: item has authority-claiming content ({phrase})")
    
    # WQ-2: queryable items must have valid lifecycle_history (if lifecycle_history is present)
    lh = item.get("lifecycle_history", [])
    if lh:
        last = lh[-1]
        if last.get("to_status") != item.get("status"):
            violations.append(f"WQ-2: item lifecycle mismatch — query results would be inconsistent")
    
    # WQ-3: summary-eligible items must not claim verification in lifecycle reasons
    for entry in lh:
        reason = str(entry.get("transition_reason", "")).lower()
        if "verified" in reason:
            violations.append(f"WQ-3: item lifecycle reason claims verification ('{reason[:60]}')")
    
    # Evidence link rules (WB-9 through WB-12)
    for link in item.get("evidence_links", []):
        lid = link.get("evidence_link_id", "?")
        link_ok, link_msgs = validate_evidence_link_schema(link)
        for m in link_msgs: violations.append(f"WB-9: evidence_link '{lid}': {m}")
        reason = str(link.get("attachment_reason", "")).lower()
        for p in ["proves defect", "confirms defect", "is approved for", "confer seal", "has authority"]:
            if p in reason: violations.append(f"WB-10: evidence_link '{lid}' reason claims authority ('{p}')")
        ref = link.get("evidence_ref", "")
        if ref.startswith("LIB-") or "/librarian/" in str(link.get("source_path", "")).lower():
            violations.append(f"WB-11: evidence_link '{lid}' references Librarian path")
        for lk in link:
            lkl = lk.lower()
            if any(kw in lkl for kw in ["registry", "rcr_", "srs_"]):
                violations.append(f"WB-12: evidence_link '{lid}' has registry/RCR/SRS field ('{lk}')")
    
    # Lifecycle rules (WL-1 through WL-7)
    for entry in item.get("lifecycle_history", []):
        fs = entry.get("from_status", "")
        ts = entry.get("to_status", "")
        if fs not in VALID_STATUSES and fs != "__init__":
            violations.append(f"WL-1: lifecycle entry invalid from_status '{fs}'")
        if ts not in VALID_STATUSES:
            violations.append(f"WL-1: lifecycle entry invalid to_status '{ts}'")
        if not entry.get("advisory_only", False):
            violations.append(f"WL-2: lifecycle entry advisory_only must be True")
        if not entry.get("transition_reason") or len(entry.get("transition_reason", "")) < 3:
            violations.append(f"WL-3: lifecycle entry missing transition_reason")
        reason = str(entry.get("transition_reason", "")).lower()
        for p in ["approved", "verified", "sealed", "defect accepted"]:
            if p in reason:
                violations.append(f"WL-4: lifecycle reason claims '{p}' authority")
    
    # WL-5: resolved_locally must not claim Owner approval
    if item.get("status") == "resolved_locally":
        for entry in item.get("lifecycle_history", []):
            if entry.get("to_status") == "resolved_locally":
                reason = str(entry.get("transition_reason", "")).lower()
                if "owner" in reason and ("accept" in reason or "approv" in reason):
                    violations.append("WL-5: resolved_locally reason claims Owner approval")
    
    return violations


def validate_lifecycle_rules(item):
    violations = []
    history = item.get("lifecycle_history", [])
    
    if history:
        last_entry = history[-1]
        if last_entry.get("to_status") != item.get("status"):
            violations.append(f"WL-6: final history to_status '{last_entry.get('to_status')}' != item status '{item.get('status')}'")
    
    for i, entry in enumerate(history):
        if i == 0 and entry.get("from_status") == "__init__":
            continue
        if i == 0: continue
        prev = history[i-1]
        expected_from = prev.get("to_status")
        actual_from = entry.get("from_status")
        if expected_from != actual_from:
            violations.append(f"WL-7: history gap at entry {i}: from '{actual_from}', expected '{expected_from}'")
    
    return violations


def validate_evidence_links(item):
    violations = []
    links = item.get("evidence_links", [])
    ids = [l.get("evidence_link_id") for l in links]
    for lid in set(ids):
        if ids.count(lid) > 1: violations.append(f"EL-1: Duplicate evidence_link_id '{lid}'")
    for link in links:
        lid = link.get("evidence_link_id", "?")
        if not link.get("advisory_only", False): violations.append(f"EL-2: evidence_link '{lid}' advisory_only must be True")
        if link.get("custody", "") != "qa-pilot-local": violations.append(f"EL-3: evidence_link '{lid}' custody must be qa-pilot-local")
        expected = "Evidence attachment does not prove defect validity or imply Owner approval."
        if link.get("authority_note", "") != expected: violations.append(f"EL-4: evidence_link '{lid}' authority_note mismatch")
        valid_types = ["validator_output","arp_packet","evidence_packet","test_result","epic_regression_suite","train_sim_result","result_packet","checklist_item","owner_decision_receipt","manual_observation"]
        if link.get("evidence_type") not in valid_types: violations.append(f"EL-5: evidence_link '{lid}' unsupported type '{link.get('evidence_type')}'")
    return violations


def validate_item(item):
    results = []
    schema_ok, schema_issues = validate_schema(item, load_schema())
    for issue in schema_issues: results.append(("SCHEMA", issue))
    for v in validate_business_rules(item): results.append(("BUSINESS", v))
    for v in validate_evidence_links(item): results.append(("EVIDENCE_LINK", v))
    for v in validate_lifecycle_rules(item): results.append(("LIFECYCLE", v))
    return not results, results


def cmd_fixture(args):
    directory = args.directory or os.path.join(PROJECT_ROOT, "docs", "examples", "qa-pilot-workbench")
    if not os.path.isdir(directory): print(f"ERROR: Directory not found: {directory}"); sys.exit(1)
    
    json_files = sorted(glob.glob(os.path.join(directory, "*.json")))
    if not json_files: print(f"No JSON files found in {directory}"); sys.exit(1)
    
    passed, errors, total_checks = 0, 0, 0
    for fpath in json_files:
        fname = os.path.basename(fpath)
        try:
            with open(fpath) as f: item = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[PARSE ERROR] {fname}: {e}"); errors += 1; continue
        
        is_valid, results = validate_item(item)
        total_checks += len(results)
        expected = fname.startswith("valid")
        
        if is_valid == expected:
            passed += 1
            msg = "ALL CHECKS PASS" if is_valid else f"Correctly rejected ({len(results)} issues)"
            print(f"[PASS] {fname}: {msg}")
            if not is_valid:
                for ct, d in results: print(f"  [{ct}] {d}")
        else:
            errors += 1
            print(f"[UNEXPECTED] {fname}: expected valid={expected}, got valid={is_valid}")
            if not is_valid:
                for ct, d in results: print(f"  [{ct}] {d}")
    
    vc = sum(1 for f in json_files if os.path.basename(f).startswith("valid"))
    ic = sum(1 for f in json_files if os.path.basename(f).startswith("invalid"))
    print(f"\n=== Fixture validation: {passed}/{len(json_files)} pass ({vc} valid, {ic} invalid, {total_checks} total checks) ===")
    if errors > 0: sys.exit(1)


def cmd_validate(args):
    any_fail = False
    for fpath in args.json_files:
        try:
            with open(fpath) as f: item = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[PARSE ERROR] {fpath}: {e}"); any_fail = True; continue
        is_valid, results = validate_item(item)
        iid = item.get("qa_item_id", os.path.basename(fpath))
        if is_valid: print(f"[PASS] {iid}: ALL CHECKS PASS")
        else: any_fail = True; print(f"[FAIL] {iid}: {len(results)} issue(s)"); [print(f"  [{ct}] {d}") for ct, d in results]
    if any_fail: sys.exit(1)


def cmd_live(args):
    if not os.path.exists(STORE_INDEX): print("No workbench store found."); return
    with open(STORE_INDEX) as f: index = json.load(f)
    items = index.get("items", [])
    if not items: print("No stored items."); return
    all_ok = True
    for item_id in items:
        ipath = os.path.join(STORE_DIR, f"{item_id}.json")
        if not os.path.exists(ipath): print(f"[MISSING] {item_id}"); all_ok = False; continue
        with open(ipath) as f: item = json.load(f)
        is_valid, results = validate_item(item)
        if is_valid: print(f"[PASS] {item_id}")
        else: all_ok = False; print(f"[FAIL] {item_id}: {len(results)} issue(s)"); [print(f"  [{ct}] {d}") for ct, d in results]
    if all_ok: print(f"\nALL CHECKS PASS — {len(items)} items validated")
    else: print(f"\nSOME CHECKS FAILED"); sys.exit(1)


def cmd_chain(args):
    validators = [
        ("Pipeline Health", ["python3", "scripts/validate-qa-pilot-pipeline-health-regression.py", "fixture"]),
        ("Pipeline Drift", ["python3", "scripts/validate-qa-pilot-pipeline-drift-detection.py", "fixture"]),
        ("Pipeline Layer Registry", ["python3", "scripts/validate-qa-pilot-pipeline-layer-registry.py", "fixture"]),
        ("Startup Surface Snapshot", ["python3", "scripts/validate-qa-pilot-startup-surface-regression-snapshot.py", "fixture"]),
    ]
    all_ok = True
    for name, cmd in validators:
        fc = [sys.executable, os.path.join(PROJECT_ROOT, cmd[1])] + cmd[2:]
        r = subprocess.run(fc, capture_output=True, text=True, cwd=PROJECT_ROOT)
        if r.returncode == 0: print(f"[PASS] {name}")
        else: all_ok = False; print(f"[FAIL] {name}"); [print(f"  {l}") for l in r.stdout.splitlines()[-3:]]
    
    print("\n--- QA Workbench Lifecycle Validator ---")
    fdir = os.path.join(PROJECT_ROOT, "docs", "examples", "qa-pilot-workbench")
    json_files = sorted(glob.glob(os.path.join(fdir, "*.json")))
    wb_ok = True
    for fpath in json_files:
        with open(fpath) as f: item = json.load(f)
        is_valid, results = validate_item(item)
        fname = os.path.basename(fpath)
        expected = fname.startswith("valid")
        if is_valid == expected: print(f"[PASS] {fname}")
        else: wb_ok = False; print(f"[FAIL] {fname}: expected valid={expected}")
    if all_ok and wb_ok: print(f"\n=== FULL CHAIN PASS ===")
    else: print(f"\n=== CHAIN HAS FAILURES ==="); sys.exit(1)


PACKET_DISCLAIMER = "This export packet is advisory-only. It does not verify item correctness, imply defect acceptance, imply Owner approval, or close/seal/promote QA items. Custody is qa-pilot-local. Librarian impact is none."
PACKET_SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-workbench-export-packet.schema.json")
VALID_STATUSES = ["draft","open","triaged","evidence_attached","needs_review","deferred","resolved_locally"]


def validate_packet(packet):
    """Validate an export packet. Returns (is_valid, [(check, detail)])."""
    results = []
    
    # Schema validation
    try:
        import jsonschema
        with open(PACKET_SCHEMA_PATH) as f:
            schema = json.load(f)
        try:
            jsonschema.validate(packet, schema)
        except jsonschema.exceptions.ValidationError as e:
            results.append(("SCHEMA", f"packet schema: {e.message}"))
    except ImportError:
        pass
    
    # WP-1: advisory_only
    if not packet.get("advisory_only", False):
        results.append(("WP-1", "packet advisory_only must be True"))
    
    # WP-2: custody
    if packet.get("custody", "") != "qa-pilot-local":
        results.append(("WP-2", "packet custody must be qa-pilot-local"))
    
    # WP-3: librarian_impact
    if packet.get("librarian_impact", "") != "none":
        results.append(("WP-3", "packet librarian_impact must be 'none'"))
    
    # WP-4: authority_disclaimer
    if packet.get("authority_disclaimer", "") != PACKET_DISCLAIMER:
        results.append(("WP-4", "packet authority_disclaimer mismatch"))
    
    # WP-5: validate each included item against business rules
    for item in packet.get("included_items", []):
        iid = item.get("qa_item_id", "?")
        
        # Reuse item-level validation
        for v in validate_business_rules(item):
            results.append(("WP-5", f"item '{iid}': {v}"))
        for v in validate_evidence_links(item):
            results.append(("WP-5", f"item '{iid}': {v}"))
        for v in validate_lifecycle_rules(item):
            results.append(("WP-5", f"item '{iid}': {v}"))
    
    # WP-6: items must have valid statuses
    for item in packet.get("included_items", []):
        if item.get("status") not in VALID_STATUSES:
            results.append(("WP-6", f"item '{item.get('qa_item_id','?')}' invalid status '{item.get('status')}'"))
    
    # WP-7: source_query should have command/filters
    sq = packet.get("source_query")
    if sq and "command" not in sq and "filters" not in sq:
        results.append(("WP-7", "source_query missing command or filters"))
    
    # WP-8: no registry/RCR/SRS fields in items
    for item in packet.get("included_items", []):
        for key in item:
            kl = key.lower()
            if any(kw in kl for kw in ["registry", "rcr_", "srs_"]):
                results.append(("WP-8", f"item '{item.get('qa_item_id','?')}' has registry/RCR/SRS field ('{key}')"))
    
    return not results, results


def cmd_packet(args):
    """Validate export packet fixtures from a directory."""
    directory = args.directory or os.path.join(PROJECT_ROOT, "docs", "examples", "qa-pilot-export-packet")
    if not os.path.isdir(directory):
        print(f"ERROR: Directory not found: {directory}"); sys.exit(1)
    
    json_files = sorted(glob.glob(os.path.join(directory, "*.json")))
    if not json_files:
        print(f"No JSON files found in {directory}"); sys.exit(1)
    
    passed, errors = 0, 0
    for fpath in json_files:
        fname = os.path.basename(fpath)
        try:
            with open(fpath) as f: packet = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[PARSE ERROR] {fname}: {e}"); errors += 1; continue
        
        is_valid, results = validate_packet(packet)
        expected = fname.startswith("valid")
        
        if is_valid == expected:
            passed += 1
            msg = "ALL CHECKS PASS" if is_valid else f"Correctly rejected ({len(results)} issues)"
            print(f"[PASS] {fname}: {msg}")
            if not is_valid:
                for ct, d in results: print(f"  [{ct}] {d}")
        else:
            errors += 1
            print(f"[UNEXPECTED] {fname}: expected valid={expected}, got valid={is_valid}")
            if not is_valid:
                for ct, d in results: print(f"  [{ct}] {d}")
    
    vc = sum(1 for f in json_files if os.path.basename(f).startswith("valid"))
    ic = sum(1 for f in json_files if os.path.basename(f).startswith("invalid"))
    print(f"\n=== Packet validation: {passed}/{len(json_files)} pass ({vc} valid, {ic} invalid) ===")
    if errors > 0: sys.exit(1)


INTAKE_DISCLAIMER = "This review intake record is advisory-only. It does not approve packet contents, verify item correctness, accept defects, or close/seal/promote anything. Custody is qa-pilot-local. Librarian impact is none."
INTAKE_SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-workbench-review-intake.schema.json")


def validate_intake(record):
    """Validate a review intake record. Returns (is_valid, [(check, detail)])."""
    results = []
    
    try:
        import jsonschema
        with open(INTAKE_SCHEMA_PATH) as f:
            schema = json.load(f)
        try:
            jsonschema.validate(record, schema)
        except jsonschema.exceptions.ValidationError as e:
            results.append(("SCHEMA", f"intake schema: {e.message}"))
    except ImportError:
        pass
    
    # IR-1: advisory_only
    if not record.get("advisory_only", False):
        results.append(("IR-1", "intake advisory_only must be True"))
    
    # IR-2: custody
    if record.get("custody", "") != "qa-pilot-local":
        results.append(("IR-2", "intake custody must be qa-pilot-local"))
    
    # IR-3: librarian_impact
    if record.get("librarian_impact", "") != "none":
        results.append(("IR-3", "intake librarian_impact must be 'none'"))
    
    # IR-4: authority_disclaimer
    if record.get("authority_disclaimer", "") != INTAKE_DISCLAIMER:
        results.append(("IR-4", "intake authority_disclaimer mismatch"))
    
    # IR-5: source_packet_id must start with XPK-
    if not record.get("source_packet_id", "").startswith("XPK-"):
        results.append(("IR-5", "source_packet_id must start with XPK-"))
    
    # IR-6: included_item_ids must be present
    if not record.get("included_item_ids"):
        results.append(("IR-6", "included_item_ids is empty"))
    
    # IR-7: no registry/RCR/SRS fields
    for key in record:
        kl = key.lower()
        if any(kw in kl for kw in ["registry", "rcr_", "srs_"]):
            results.append(("IR-7", f"intake has registry/RCR/SRS field ('{key}')"))
    
    return not results, results


def cmd_intake(args):
    """Validate review intake fixtures from a directory."""
    directory = args.directory or os.path.join(PROJECT_ROOT, "docs", "examples", "qa-pilot-review-intake")
    if not os.path.isdir(directory):
        print(f"ERROR: Directory not found: {directory}"); sys.exit(1)
    
    json_files = sorted(glob.glob(os.path.join(directory, "*.json")))
    if not json_files:
        print(f"No JSON files found."); sys.exit(1)
    
    passed, errors = 0, 0
    for fpath in json_files:
        fname = os.path.basename(fpath)
        try:
            with open(fpath) as f: record = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[PARSE ERROR] {fname}: {e}"); errors += 1; continue
        
        is_valid, results = validate_intake(record)
        expected = fname.startswith("valid")
        
        if is_valid == expected:
            passed += 1
            msg = "ALL CHECKS PASS" if is_valid else f"Correctly rejected ({len(results)} issues)"
            print(f"[PASS] {fname}: {msg}")
            if not is_valid:
                for ct, d in results: print(f"  [{ct}] {d}")
        else:
            errors += 1
            print(f"[UNEXPECTED] {fname}: expected valid={expected}, got valid={is_valid}")
            if not is_valid:
                for ct, d in results: print(f"  [{ct}] {d}")
    
    vc = sum(1 for f in json_files if os.path.basename(f).startswith("valid"))
    ic = sum(1 for f in json_files if os.path.basename(f).startswith("invalid"))
    print(f"\n=== Intake validation: {passed}/{len(json_files)} pass ({vc} valid, {ic} invalid) ===")
    if errors > 0: sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="QA Workbench Validator")
    sub = parser.add_subparsers(dest="mode", required=True)
    p_f = sub.add_parser("fixture"); p_f.add_argument("directory", nargs="?"); p_f.set_defaults(func=cmd_fixture)
    p_v = sub.add_parser("validate"); p_v.add_argument("json_files", nargs="+"); p_v.set_defaults(func=cmd_validate)
    p_l = sub.add_parser("live"); p_l.set_defaults(func=cmd_live)
    p_c = sub.add_parser("chain"); p_c.add_argument("--quick", action="store_true"); p_c.set_defaults(func=cmd_chain)
    p_p = sub.add_parser("packet"); p_p.add_argument("directory", nargs="?"); p_p.set_defaults(func=cmd_packet)
    p_i = sub.add_parser("intake"); p_i.add_argument("directory", nargs="?"); p_i.set_defaults(func=cmd_intake)
    args = parser.parse_args(); args.func(args)

if __name__ == "__main__":
    main()
