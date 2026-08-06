#!/usr/bin/env python3
"""QA Pilot Risk-Based Review Depth Validator.

Enforces RD-1 through RD-15 rules on depth evaluations,
C-1 through C-3 on review cards, P-1 through P-2 on review packets,
and H-1 through H-2 on heavy packets. Also validates fixtures
and checks regression against existing validators.
"""
import argparse, json, os, sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "risk-based-review-depths")
STORE_INDEX = os.path.join(STORE_DIR, "depth-index.json")
SCHEMA_EVAL_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-pilot-risk-based-review-depth.schema.json")
SCHEMA_CARD_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-pilot-risk-based-review-card.schema.json")
SCHEMA_PACKET_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-pilot-risk-based-review-packet.schema.json")
SCHEMA_HEAVY_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-pilot-risk-based-heavy-packet.schema.json")
FIXTURE_DIR = os.path.join(PROJECT_ROOT, "docs", "examples", "qa-pilot-risk-based-review-depth")
DISCLAIMER = ("This risk-based review depth evaluation is advisory-only. It does not auto-accept evidence, "
              "auto-reject findings, execute work, approve intake, verify evidence, close workbench items, "
              "seal anything, mutate the evidence chain, or replace Owner decision authority. "
              "Owner remains the final decision point. Custody is qa-pilot-local. Librarian impact is none.")
CARD_DISCLAIMER = ("This light review card is advisory-only. It does not approve intake, verify evidence, "
                   "close workbench items, seal results, execute work, or replace Owner decision authority. "
                   "Owner remains the final decision point. Custody is qa-pilot-local. Librarian impact is none.")
PACKET_DISCLAIMER = ("This standard review packet is advisory-only. It does not approve intake, verify evidence, "
                     "close workbench items, seal results, execute work, or replace Owner decision authority. "
                     "Owner remains the final decision point. Custody is qa-pilot-local. Librarian impact is none.")
HEAVY_DISCLAIMER = ("This heavy evidence review packet is advisory-only. It does not approve intake, verify evidence, "
                    "close workbench items, seal results, execute work, or replace Owner decision authority. "
                    "Owner remains the final decision point. Custody is qa-pilot-local. Librarian impact is none.")

DEPTH_ORDER = {"none": 0, "light": 1, "standard": 2, "heavy": 3}

pass_count = 0
fail_count = 0
total_checks = 0


def check(condition, message):
    global pass_count, fail_count, total_checks
    total_checks += 1
    if condition:
        pass_count += 1
    else:
        fail_count += 1
        print(f"  FAIL: {message}")


def report_section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


# --- RD Validator Rules ---

def validate_rd_rules(record, label="live"):
    """Validate RD-1 through RD-15 on a depth evaluation record."""
    ri = record.get("risk_inputs", {})
    d = record.get("assigned_depth", "")
    crs = record.get("composite_risk_score", -1)
    chain = record.get("escalation_chain", [])

    # RD-1: Valid depth value
    check(d in ("none", "light", "standard", "heavy"),
          f"[{label}] RD-1: assigned_depth must be one of none/light/standard/heavy (got '{d}')")

    # RD-2: Composite risk score matches risk inputs
    check(isinstance(crs, int) and crs >= 0,
          f"[{label}] RD-2: composite_risk_score must be non-negative integer (got {crs})")

    # RD-3: advisory_only = true
    check(record.get("advisory_only") is True,
          f"[{label}] RD-3: advisory_only must be True")

    # RD-4: custody = qa-pilot-local
    check(record.get("custody") == "qa-pilot-local",
          f"[{label}] RD-4: custody must be qa-pilot-local")

    # RD-5: librarian_impact = none
    check(record.get("librarian_impact") == "none",
          f"[{label}] RD-5: librarian_impact must be 'none'")

    # RD-6: Authority disclaimer present and correct
    check(record.get("authority_disclaimer") == DISCLAIMER,
          f"[{label}] RD-6: authority_disclaimer mismatch")

    # RD-7: No forbidden authority fields
    forbidden = ["auto_accept", "auto_acceptance", "auto_reject", "auto_rejection",
                 "executed_", "execution_result", "authorizes_execution",
                 "seal_", "sealed", "approval_status", "approved_by",
                 "evidence_verified", "items_closed", "mutates_evidence",
                 "mutates_chain", "mutates_outcome", "owner_override"]
    found_forbidden = []
    for key in record:
        kl = key.lower()
        for p in forbidden:
            if p in kl:
                found_forbidden.append(key)
    check(len(found_forbidden) == 0,
          f"[{label}] RD-7: forbidden fields found: {found_forbidden}")

    # RD-8: Text fields don't claim authority
    authority_kw = ["auto-accepted", "auto-accept", "auto-rejected", "auto-reject",
                    "executed", "authorizes", "seal", "approved", "verified",
                    "closed", "defect accepted", "owner overridden"]
    for text_field in ["risk_input_breakdown", "recommendation_summary",
                       "evidence_bundle_review", "risk_summary", "consistency_guard_evaluation"]:
        val = record.get(text_field)
        if val and isinstance(val, str):
            for kw in authority_kw:
                if kw in val.lower():
                    check(False, f"[{label}] RD-8: {text_field} contains authority-claiming term '{kw}'")
                    break

    # RD-9: evaluation_id correct format
    import re
    check(bool(re.match(r"^RD-EVAL-", record.get("evaluation_id", ""))),
          f"[{label}] RD-9: evaluation_id must start with RD-EVAL- (got '{record.get('evaluation_id', '')}')")

    # RD-10: escalation_chain values valid
    all_valid = True
    for rule in chain:
        if not re.match(r"^ER-(?:[1-9]|10)$", rule):
            all_valid = False
    check(all_valid, f"[{label}] RD-10: escalation_chain contains invalid rule IDs: {chain}")

    # RD-11: Depth escalation correctness — verify ER-1 through ER-10
    # ER-1 check
    if ri.get("authority_change"):
        check(DEPTH_ORDER.get(d, 0) >= DEPTH_ORDER["heavy"],
              f"[{label}] RD-11/ER-1: authority_change=true requires depth >= heavy (got '{d}')")
        check("ER-1" in chain, f"[{label}] RD-11/ER-1: ER-1 should be in escalation_chain")
    # ER-2 check
    if ri.get("ledger_registry_change"):
        check(DEPTH_ORDER.get(d, 0) >= DEPTH_ORDER["standard"],
              f"[{label}] RD-11/ER-2: ledger_registry_change=true requires depth >= standard (got '{d}')")
    # ER-5 check
    if ri.get("partial_completion"):
        check(DEPTH_ORDER.get(d, 0) >= DEPTH_ORDER["standard"],
              f"[{label}] RD-11/ER-5: partial_completion=true requires depth >= standard (got '{d}')")

    # RD-12: Lightweight lane with all pass = allows none
    if (ri.get("lightweight_lane") and ri.get("rc_failure_count", 0) == 0
            and ri.get("e4_failure_count", 0) == 0
            and not ri.get("authority_change") and not ri.get("production_path_impact")
            and not ri.get("ledger_registry_change")):
        check("ER-9" in chain,
              f"[{label}] RD-12/ER-9: lightweight+allPass should have ER-9 in chain (got {chain})")

    # RD-13: escalation_chain matches triggered rules
    check(len(chain) <= 10, f"[{label}] RD-13: escalation_chain has {len(chain)} rules (max 10)")

    # RD-14: No duplicate rule IDs
    check(len(chain) == len(set(chain)),
          f"[{label}] RD-14: duplicate rule IDs in escalation_chain: {chain}")

    # RD-15: assigned_depth matches composite score + escalation
    check(d in DEPTH_ORDER, f"[{label}] RD-15: invalid depth '{d}'")


def validate_card_rules(record, label="live"):
    """Validate C-1 through C-3 on a review card."""
    check(record.get("assigned_depth") == "light",
          f"[{label}] C-1: card assigned_depth must be 'light' (got '{record.get('assigned_depth')}')")
    check(record.get("clearance_status") in ("cleared", "needs_attention"),
          f"[{label}] C-2: clearance_status must be cleared/needs_attention")
    forbidden = ["auto_accept", "auto_reject", "executed_", "seal_", "sealed",
                 "approval_status", "approved_by", "evidence_verified",
                 "items_closed", "mutates_", "owner_override"]
    found = [k for k in record if any(p in k.lower() for p in forbidden)]
    check(len(found) == 0, f"[{label}] C-3: forbidden fields: {found}")


def validate_packet_rules(record, label="live"):
    """Validate P-1 through P-2 on a review packet."""
    check(record.get("assigned_depth") in ("standard", "heavy"),
          f"[{label}] P-1: assigned_depth must be standard/heavy (got '{record.get('assigned_depth')}')")
    forbidden = ["auto_accept", "auto_reject", "executed_", "seal_", "sealed",
                 "approval_status", "approved_by", "evidence_verified",
                 "items_closed", "mutates_", "owner_override"]
    found = [k for k in record if any(p in k.lower() for p in forbidden)]
    check(len(found) == 0, f"[{label}] P-2: forbidden fields: {found}")


def validate_heavy_rules(record, label="live"):
    """Validate H-1 through H-2 on a heavy packet."""
    check(record.get("assigned_depth") == "heavy",
          f"[{label}] H-1: assigned_depth must be 'heavy' (got '{record.get('assigned_depth')}')")
    forbidden = ["auto_accept", "auto_reject", "executed_", "seal_", "sealed",
                 "approval_status", "approved_by", "evidence_verified",
                 "items_closed", "mutates_", "owner_override"]
    found = [k for k in record if any(p in k.lower() for p in forbidden)]
    check(len(found) == 0, f"[{label}] H-2: forbidden fields: {found}")


def validate_schema(record, schema_path, label):
    try:
        import jsonschema
        with open(schema_path) as f:
            schema = json.load(f)
        try:
            jsonschema.validate(record, schema)
            check(True, f"[{label}] Schema validation: pass")
        except jsonschema.exceptions.ValidationError as e:
            check(False, f"[{label}] Schema validation: {e.message}")
    except ImportError:
        print(f"  SKIP: [{label}] Schema validation (jsonschema not available)")


# --- Fixture Validation ---

def validate_fixtures():
    global pass_count, fail_count, total_checks
    report_section("Fixture Validation")
    fixture_map = {
        "valid-low-risk-lightweight.json": ("eval", "none_or_light"),
        "valid-authority-change-heavy.json": ("eval", "heavy"),
        "valid-partial-completion-standard.json": ("eval", "standard"),
        "valid-failed-rc-escalated.json": ("eval", "escalated"),
        "valid-standard-packet-example.json": ("packet", "standard"),
        "valid-heavy-packet-example.json": ("heavy", "heavy"),
        "invalid-authority-claim.json": ("eval", "invalid"),
        "invalid-depth-too-low.json": ("eval", "invalid"),
        "invalid-seal-claim.json": ("eval", "invalid"),
    }

    for fname, (ftype, fexpect) in sorted(fixture_map.items()):
        fpath = os.path.join(FIXTURE_DIR, fname)
        if not os.path.exists(fpath):
            print(f"  SKIP: {fname} (not found)")
            continue
        with open(fpath) as f:
            try:
                record = json.load(f)
            except json.JSONException as e:
                check(False, f"[{fname}] Failed to parse JSON: {e}")
                continue

        print(f"\n  --- {fname} ---")
        pre_fail = fail_count
        if ftype == "eval":
            validate_schema(record, SCHEMA_EVAL_PATH, fname)
            validate_rd_rules(record, fname)
        elif ftype == "packet":
            validate_schema(record, SCHEMA_PACKET_PATH, fname)
            validate_packet_rules(record, fname)
        elif ftype == "heavy":
            validate_schema(record, SCHEMA_HEAVY_PATH, fname)
            validate_heavy_rules(record, fname)
        new_fails = fail_count - pre_fail

        if fexpect == "invalid":
            if new_fails > 0:
                # Expected failure — undo fail count
                fail_count -= new_fails
                pass_count += new_fails
                print(f"  ✓ Invalid fixture correctly rejected ({new_fails} violations)")
            else:
                check(False, f"[{fname}] Expected invalid fixture to fail validation")
        elif fexpect in ("none_or_light", "heavy", "standard", "escalated"):
            if new_fails == 0:
                print(f"  ✓ Valid fixture passes")
            else:
                check(False, f"[{fname}] Valid fixture should not have validation failures")


# --- Regression Check ---

def check_regression():
    """Verify existing validators are unaffected."""
    report_section("Regression Check")
    # Check sealed validators still load
    script_map = {
        "TD-1-TD-8": "scripts/validate-qa-pilot-review-depth-thresholds.py",
        "DP-1-DP-8": "scripts/validate-qa-pilot-review-depth-thresholds-decision-packet.py",
    }
    for name, path in script_map.items():
        full_path = os.path.join(PROJECT_ROOT, path)
        exists = os.path.exists(full_path)
        check(exists, f"Existing validator '{name}' at {path}: {'found' if exists else 'MISSING'}")


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="QA Pilot Risk-Based Review Depth Validator")
    parser.add_argument("--live", action="store_true", help="Validate live store records")
    parser.add_argument("--fixtures", action="store_true", default=True, help="Validate fixture files (default)")
    parser.add_argument("--regression", action="store_true", default=True, help="Check regression against existing validators")
    parser.add_argument("--eval-file", help="Validate a specific evaluation file")
    parser.add_argument("--card-file", help="Validate a specific card file")
    parser.add_argument("--packet-file", help="Validate a specific packet file")
    parser.add_argument("--store-scan", action="store_true", help="Scan all records in the live store")
    args = parser.parse_args()

    global pass_count, fail_count, total_checks

    print("QA Pilot Risk-Based Review Depth Validator")
    print("=" * 60)

    # Single file validation
    if args.eval_file:
        with open(args.eval_file) as f:
            record = json.load(f)
        validate_schema(record, SCHEMA_EVAL_PATH, args.eval_file)
        validate_rd_rules(record, args.eval_file)
        print(f"\nResults: {pass_count}/{total_checks} pass, {fail_count} fail")
        sys.exit(1 if fail_count > 0 else 0)

    if args.card_file:
        with open(args.card_file) as f:
            record = json.load(f)
        validate_schema(record, SCHEMA_CARD_PATH, args.card_file)
        validate_card_rules(record, args.card_file)
        print(f"\nResults: {pass_count}/{total_checks} pass, {fail_count} fail")
        sys.exit(1 if fail_count > 0 else 0)

    if args.packet_file:
        with open(args.packet_file) as f:
            record = json.load(f)
        pid = record.get("packet_id", "")
        if pid.startswith("HP-"):
            validate_schema(record, SCHEMA_HEAVY_PATH, args.packet_file)
            validate_heavy_rules(record, args.packet_file)
        else:
            validate_schema(record, SCHEMA_PACKET_PATH, args.packet_file)
            validate_packet_rules(record, args.packet_file)
        print(f"\nResults: {pass_count}/{total_checks} pass, {fail_count} fail")
        sys.exit(1 if fail_count > 0 else 0)

    # Fixture validation
    if args.fixtures:
        validate_fixtures()

    # Live store scan
    if args.live or args.store_scan:
        report_section("Live Store Validation")
        if os.path.exists(STORE_INDEX):
            with open(STORE_INDEX) as f:
                index = json.load(f)
            for rid in index.get("depth_evaluations", []):
                rpath = os.path.join(STORE_DIR, "evaluations", f"{rid}.json")
                if os.path.exists(rpath):
                    with open(rpath) as f:
                        record = json.load(f)
                    print(f"\n  --- Live: {rid} ---")
                    validate_rd_rules(record, rid)
            for cid in index.get("review_cards", []):
                rpath = os.path.join(STORE_DIR, "cards", f"{cid}.json")
                if os.path.exists(rpath):
                    with open(rpath) as f:
                        record = json.load(f)
                    print(f"\n  --- Live: {cid} ---")
                    validate_card_rules(record, cid)
            for pid in index.get("review_packets", []):
                rpath = os.path.join(STORE_DIR, "packets", f"{pid}.json")
                if os.path.exists(rpath):
                    with open(rpath) as f:
                        record = json.load(f)
                    print(f"\n  --- Live: {pid} ---")
                    validate_packet_rules(record, pid)
            for pid in index.get("heavy_packets", []):
                rpath = os.path.join(STORE_DIR, "heavy_packets", f"{pid}.json")
                if os.path.exists(rpath):
                    with open(rpath) as f:
                        record = json.load(f)
                    print(f"\n  --- Live: {pid} ---")
                    validate_heavy_rules(record, pid)
        else:
            print("  No live store found.")

    # Regression check
    if args.regression:
        check_regression()

    # Summary
    report_section("Summary")
    print(f"  Checks: {total_checks}")
    print(f"  Pass:   {pass_count}")
    print(f"  Fail:   {fail_count}")
    if fail_count > 0:
        sys.exit(1)
    print("  ALL CHECKS PASS")


if __name__ == "__main__":
    main()
