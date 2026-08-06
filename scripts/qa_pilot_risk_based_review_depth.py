#!/usr/bin/env python3
"""QA Pilot Risk-Based Review Depth CLI.

Implements risk-based review depth selection consuming 9 risk inputs,
ER-1 through ER-10 escalation rules, and producing 3 review output contract types.
Advisory-only. QA Pilot-local. No execution, approval, seal, or mutation authority.
"""
import argparse, json, os, sys, datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "risk-based-review-depths")
STORE_INDEX = os.path.join(STORE_DIR, "depth-index.json")
SCHEMA_EVAL_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-pilot-risk-based-review-depth.schema.json")
SCHEMA_CARD_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-pilot-risk-based-review-card.schema.json")
SCHEMA_PACKET_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-pilot-risk-based-review-packet.schema.json")
SCHEMA_HEAVY_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-pilot-risk-based-heavy-packet.schema.json")
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


def _now():
    return datetime.datetime.utcnow().isoformat() + "Z"


def _ensure_store():
    os.makedirs(STORE_DIR, exist_ok=True)
    if not os.path.exists(STORE_INDEX):
        with open(STORE_INDEX, "w") as f:
            json.dump({"depth_evaluations": [], "review_cards": [], "review_packets": [], "heavy_packets": [],
                       "last_updated": _now()}, f, indent=2)


def _load_index():
    _ensure_store()
    with open(STORE_INDEX) as f:
        return json.load(f)


def _save_index(index):
    index["last_updated"] = _now()
    with open(STORE_INDEX, "w") as f:
        json.dump(index, f, indent=2)


def _load_record(subdir, rid):
    path = os.path.join(STORE_DIR, subdir, f"{rid}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def _save_record(subdir, record, rid):
    os.makedirs(os.path.join(STORE_DIR, subdir), exist_ok=True)
    with open(os.path.join(STORE_DIR, subdir, f"{rid}.json"), "w") as f:
        json.dump(record, f, indent=2)


def _validate_schema(record, schema_path):
    try:
        import jsonschema
        with open(schema_path) as f:
            schema = json.load(f)
        try:
            jsonschema.validate(record, schema)
            return True, []
        except jsonschema.exceptions.ValidationError as e:
            return False, [f"schema violation: {e.message}"]
    except ImportError:
        return True, []


# --- Risk Scoring ---

def _compute_risk_score(ri):
    """Compute composite risk score from risk inputs."""
    score = 0
    if ri["authority_change"]:
        score += 10
    if ri["production_path_impact"]:
        score += 7
    if ri["ledger_registry_change"]:
        score += 8
    if ri["cross_node_involvement"]:
        score += 5
    if ri["partial_completion"]:
        score += 5
    # Incomplete requirements: 0=none, 1-2=some(+3), 3+=many(+6)
    if ri["incomplete_requirements"] >= 3:
        score += 6
    elif ri["incomplete_requirements"] >= 1:
        score += 3
    # RC failures: 0=none, >=1 but <50%=some(+3), >=50%=many(+6)
    rc_total = ri["rc_total_count"]
    rc_fail = ri["rc_failure_count"]
    if rc_total > 0:
        rc_fail_rate = rc_fail / rc_total
        if rc_fail_rate >= 0.5:
            score += 6
        elif rc_fail > 0:
            score += 3
    # E4 failures: 0=none, >=1 but <50%=some(+3), >=50%=many(+6)
    e4_total = ri["e4_total_count"]
    e4_fail = ri["e4_failure_count"]
    if e4_total > 0:
        e4_fail_rate = e4_fail / e4_total
        if e4_fail_rate >= 0.5:
            score += 6
        elif e4_fail > 0:
            score += 3
    # Lightweight lane reduces score
    if ri["lightweight_lane"]:
        score = max(0, score - 3)
    return score


def _base_depth(score):
    """Assign base review depth from composite risk score (pre-escalation)."""
    if score <= 3:
        return "none"
    elif score <= 10:
        return "light"
    elif score <= 20:
        return "standard"
    else:
        return "heavy"


DEPTH_ORDER = {"none": 0, "light": 1, "standard": 2, "heavy": 3}


def _escalate(depth, escalation_rules):
    """Apply ER-1 through ER-10 escalation rules, returning (final_depth, triggered_rules)."""
    triggered = []
    rd = DEPTH_ORDER[depth]

    ri = escalation_rules.get("risk_inputs", {})
    fired = escalation_rules.get("fired_rules", [])

    # ER-1: Authority change → heavy
    if ri.get("authority_change"):
        rd = max(rd, DEPTH_ORDER["heavy"])
        if "ER-1" not in fired:
            fired.append("ER-1")

    # ER-2: Ledger/registry change → standard
    if ri.get("ledger_registry_change"):
        rd = max(rd, DEPTH_ORDER["standard"])
        if "ER-2" not in fired:
            fired.append("ER-2")

    # ER-3: Production-path mutation → standard
    if ri.get("production_path_impact"):
        rd = max(rd, DEPTH_ORDER["standard"])
        if "ER-3" not in fired:
            fired.append("ER-3")

    # ER-4: Cross-node involvement → standard
    if ri.get("cross_node_involvement"):
        rd = max(rd, DEPTH_ORDER["standard"])
        if "ER-4" not in fired:
            fired.append("ER-4")

    # ER-5: Partial completion → standard
    if ri.get("partial_completion"):
        rd = max(rd, DEPTH_ORDER["standard"])
        if "ER-5" not in fired:
            fired.append("ER-5")

    # ER-6: Incomplete requirements → standard
    if ri.get("incomplete_requirements", 0) > 0:
        rd = max(rd, DEPTH_ORDER["standard"])
        if "ER-6" not in fired:
            fired.append("ER-6")

    # ER-7: RC failures → escalate one level
    rc_total = ri.get("rc_total_count", 0)
    rc_fail = ri.get("rc_failure_count", 0)
    if rc_total > 0 and rc_fail > 0:
        rd = min(rd + 1, DEPTH_ORDER["heavy"])
        if "ER-7" not in fired:
            fired.append("ER-7")

    # ER-8: E4 failures → escalate one level
    e4_total = ri.get("e4_total_count", 0)
    e4_fail = ri.get("e4_failure_count", 0)
    if e4_total > 0 and e4_fail > 0:
        rd = min(rd + 1, DEPTH_ORDER["heavy"])
        if "ER-8" not in fired:
            fired.append("ER-8")

    # ER-9: Lightweight lane + all pass + no authority/prod/registry → none
    if (ri.get("lightweight_lane") and rc_fail == 0 and e4_fail == 0
            and not ri.get("authority_change") and not ri.get("production_path_impact")
            and not ri.get("ledger_registry_change")):
        rd = min(rd, DEPTH_ORDER["none"])
        if "ER-9" not in fired:
            fired.append("ER-9")

    # ER-10: Multiple rules → highest depth wins (already implemented by max())
    if len(fired) > 1 and "ER-10" not in fired:
        fired.append("ER-10")

    # Reverse map
    rev_map = {v: k for k, v in DEPTH_ORDER.items()}
    return rev_map[rd], fired


# --- RD Validator Rules ---

def _validate_rd_rules(record):
    violations = []
    rid = record.get("evaluation_id", "?")

    # RD-1: Valid depth value
    valid_depths = ["none", "light", "standard", "heavy"]
    d = record.get("assigned_depth")
    if d not in valid_depths:
        violations.append(f"RD-1: assigned_depth '{d}' must be one of {valid_depths}")

    # RD-2: Composite risk score >= 0
    crs = record.get("composite_risk_score", -1)
    if not isinstance(crs, int) or crs < 0:
        violations.append(f"RD-2: composite_risk_score must be a non-negative integer (got {crs})")

    # RD-3: advisory_only = true
    if not record.get("advisory_only", False):
        violations.append("RD-3: advisory_only must be True")

    # RD-4: custody = qa-pilot-local
    if record.get("custody", "") != "qa-pilot-local":
        violations.append("RD-4: custody must be qa-pilot-local")

    # RD-5: librarian_impact = none
    if record.get("librarian_impact", "") != "none":
        violations.append("RD-5: librarian_impact must be 'none'")

    # RD-6: Authority disclaimer present and correct
    if record.get("authority_disclaimer", "") != DISCLAIMER:
        violations.append("RD-6: authority_disclaimer mismatch")

    # RD-7: No auto-accept/auto-reject/execution/seal/approval fields
    forbidden = ["auto_accept", "auto_acceptance", "auto_reject", "auto_rejection",
                 "executed_", "execution_result", "authorizes_execution",
                 "seal_", "sealed", "approval_status", "approved_by",
                 "evidence_verified", "items_closed", "mutates_evidence",
                 "mutates_chain", "mutates_outcome", "owner_override"]
    for key in record:
        kl = key.lower()
        for p in forbidden:
            if p in kl:
                violations.append(f"RD-7: forbidden field '{key}' claims {p.replace('_',' ')}")

    # RD-8: Rationale/description does not claim authority
    for text_field in ["risk_input_breakdown", "recommendation_summary",
                       "evidence_bundle_review", "risk_summary", "consistency_guard_evaluation"]:
        val = record.get(text_field)
        if val and isinstance(val, str):
            vl = val.lower()
            for kw in ["auto-accepted", "auto-accept", "auto-rejected", "auto-reject",
                       "executed", "authorizes", "seal", "approved", "verified",
                       "closed", "defect accepted", "owner overridden"]:
                if kw in vl:
                    violations.append(f"RD-8: {text_field} contains authority-claiming term '{kw}'")

    # RD-9: evaluation_id pattern
    eid = record.get("evaluation_id", "")
    import re
    if not re.match(r"^RD-EVAL-", eid):
        violations.append(f"RD-9: evaluation_id must start with RD-EVAL- (got '{eid}')")

    # RD-10: escalation_chain values valid
    chain = record.get("escalation_chain", [])
    for rule in chain:
        if not re.match(r"^ER-(?:[1-9]|10)$", rule):
            violations.append(f"RD-10: escalation_chain contains invalid rule '{rule}'")

    return violations


def _validate_card_rules(record):
    violations = []
    # C-1: assigned_depth must be 'light'
    if record.get("assigned_depth") != "light":
        violations.append("C-1: card assigned_depth must be 'light'")
    # C-2: clearance_status valid
    if record.get("clearance_status") not in ("cleared", "needs_attention"):
        violations.append("C-2: clearance_status must be 'cleared' or 'needs_attention'")
    # C-3: Cannot contain authority claims
    for key in record:
        kl = key.lower()
        for p in ["auto_accept", "auto_reject", "executed_", "seal_", "sealed",
                   "approval_status", "approved_by", "evidence_verified",
                   "items_closed", "mutates_", "owner_override"]:
            if p in kl:
                violations.append(f"C-3: forbidden field '{key}'")
    return violations


def _validate_packet_rules(record):
    violations = []
    if record.get("assigned_depth") not in ("standard", "heavy"):
        violations.append("P-1: packet assigned_depth must be 'standard' or 'heavy'")
    for key in record:
        kl = key.lower()
        for p in ["auto_accept", "auto_reject", "executed_", "seal_", "sealed",
                   "approval_status", "approved_by", "evidence_verified",
                   "items_closed", "mutates_", "owner_override"]:
            if p in kl:
                violations.append(f"P-2: forbidden field '{key}'")
    return violations


def _validate_heavy_rules(record):
    violations = []
    if record.get("assigned_depth") != "heavy":
        violations.append("H-1: heavy packet assigned_depth must be 'heavy'")
    for key in record:
        kl = key.lower()
        for p in ["auto_accept", "auto_reject", "executed_", "seal_", "sealed",
                   "approval_status", "approved_by", "evidence_verified",
                   "items_closed", "mutates_", "owner_override"]:
            if p in kl:
                violations.append(f"H-2: forbidden field '{key}'")
    return violations


# --- CLI Commands ---

def cmd_evaluate(args):
    _ensure_store()
    rid = args.eval_id or f"RD-EVAL-{int(datetime.datetime.utcnow().timestamp()) % 100000:06d}"

    risk_inputs = {
        "authority_change": args.authority_change,
        "production_path_impact": args.production_path_impact,
        "ledger_registry_change": args.ledger_registry_change,
        "cross_node_involvement": args.cross_node_involvement,
        "partial_completion": args.partial_completion,
        "incomplete_requirements": args.incomplete_requirements,
        "rc_failure_count": args.rc_failure_count,
        "rc_total_count": args.rc_total_count,
        "e4_failure_count": args.e4_failure_count,
        "e4_total_count": args.e4_total_count,
        "lightweight_lane": args.lightweight_lane,
    }

    score = _compute_risk_score(risk_inputs)
    base = _base_depth(score)
    fired_rules = []
    escalation_context = {
        "risk_inputs": risk_inputs,
        "fired_rules": fired_rules,
    }
    final_depth, fired = _escalate(base, escalation_context)

    # Default pack all RC refs if not specified
    result_ref = args.result_ref or "QR-UNKNOWN"

    record = {
        "evaluation_id": rid,
        "result_packet_ref": result_ref,
        "risk_inputs": risk_inputs,
        "composite_risk_score": score,
        "assigned_depth": final_depth,
        "escalation_chain": sorted(set(fired), key=lambda x: int(x.split("-")[1])),
        "evaluated_at": _now(),
        "authority_disclaimer": DISCLAIMER,
        "custody": "qa-pilot-local",
        "advisory_only": True,
        "librarian_impact": "none",
    }

    schema_ok, schema_issues = _validate_schema(record, SCHEMA_EVAL_PATH)
    rule_issues = _validate_rd_rules(record)
    all_issues = schema_issues + rule_issues
    if all_issues:
        for i in all_issues:
            print(f"VALIDATION: {i}")

    index = _load_index()
    if rid in index.get("depth_evaluations", []):
        print(f"ERROR: Evaluation {rid} already exists")
        sys.exit(1)

    _save_record("evaluations", record, rid)
    index.setdefault("depth_evaluations", []).append(rid)
    _save_index(index)

    print(f"Depth evaluation: {rid}")
    print(f"  Risk score:  {score}")
    print(f"  Base depth:  {base}")
    print(f"  Final depth: {final_depth}")
    print(f"  Escalation:  {', '.join(sorted(set(fired), key=lambda x: int(x.split('-')[1]))) if fired else '(none)'}")
    print(f"  Advisory-only: True")


def cmd_read(args):
    record = _load_record("evaluations", args.eval_id)
    if record is None:
        print(f"ERROR: Evaluation {args.eval_id} not found")
        sys.exit(1)
    print(json.dumps(record, indent=2))


def cmd_list(args):
    index = _load_index()
    evals = index.get("depth_evaluations", [])
    if not evals:
        print("No risk-based review depth evaluations.")
        return
    print(f"Risk-Based Review Depth Evaluations ({len(evals)}):")
    print("=" * 110)
    for rid in evals:
        rec = _load_record("evaluations", rid)
        if rec is None:
            print(f"  {rid:48s}: MISSING")
            continue
        d = rec.get("assigned_depth", "?")
        sc = rec.get("composite_risk_score", 0)
        ts = rec.get("evaluated_at", "?")[:19]
        esc = ",".join(rec.get("escalation_chain", []))
        print(f"  {rid:48s} [{d:8s}] score={sc:2d}  [{ts}]  esc=[{esc}]")


def cmd_validate(args):
    if args.eval_id:
        record = _load_record("evaluations", args.eval_id)
        if record is None:
            print(f"ERROR: Evaluation {args.eval_id} not found")
            sys.exit(1)
    elif args.eval_file:
        with open(args.eval_file) as f:
            record = json.load(f)
    elif args.card_id:
        record = _load_record("cards", args.card_id)
        if record is None:
            print(f"ERROR: Card {args.card_id} not found")
            sys.exit(1)
    elif args.card_file:
        with open(args.card_file) as f:
            record = json.load(f)
    elif args.packet_id:
        record = _load_record("packets", args.packet_id)
        if record is None:
            print(f"ERROR: Packet {args.packet_id} not found")
            sys.exit(1)
    elif args.packet_file:
        with open(args.packet_file) as f:
            record = json.load(f)
    else:
        print("ERROR: Specify --eval-id, --eval-file, --card-id, --card-file, --packet-id, or --packet-file")
        sys.exit(1)

    all_issues = []

    # Determine which schema/validator to use
    eid = record.get("evaluation_id", "")
    cid = record.get("card_id", "")
    pid = record.get("packet_id", "")

    if eid and eid.startswith("RD-EVAL-"):
        schema_ok, schema_issues = _validate_schema(record, SCHEMA_EVAL_PATH)
        rule_issues = _validate_rd_rules(record)
        all_issues = schema_issues + rule_issues
    elif cid and cid.startswith("RC-"):
        schema_ok, schema_issues = _validate_schema(record, SCHEMA_CARD_PATH)
        rule_issues = _validate_card_rules(record)
        all_issues = schema_issues + rule_issues
    elif pid and pid.startswith("RP-"):
        schema_ok, schema_issues = _validate_schema(record, SCHEMA_PACKET_PATH)
        rule_issues = _validate_packet_rules(record)
        all_issues = schema_issues + rule_issues
    elif pid and pid.startswith("HP-"):
        schema_ok, schema_issues = _validate_schema(record, SCHEMA_HEAVY_PATH)
        rule_issues = _validate_heavy_rules(record)
        all_issues = schema_issues + rule_issues
    else:
        all_issues.append("Could not determine record type from ID prefix")

    ident = eid or cid or pid or "?"
    if not all_issues:
        print(f"VALID: {ident}")
        print("ALL CHECKS PASS")
    else:
        print(f"INVALID: {ident}")
        for i in all_issues:
            print(f"  {i}")
        sys.exit(1)


def cmd_status(args):
    index = _load_index()
    evals = index.get("depth_evaluations", [])
    cards = index.get("review_cards", [])
    packets = index.get("review_packets", [])
    heavy = index.get("heavy_packets", [])

    by_depth = {}
    total_score = 0
    for rid in evals:
        rec = _load_record("evaluations", rid)
        if rec is None:
            continue
        d = rec.get("assigned_depth", "?")
        by_depth[d] = by_depth.get(d, 0) + 1
        total_score += rec.get("composite_risk_score", 0)

    print("Risk-Based Review Depth Status")
    print("=" * 50)
    print(f"  Total evaluations: {len(evals)}")
    print(f"  By assigned depth:")
    for d in ["none", "light", "standard", "heavy"]:
        print(f"    {d:10s}: {by_depth.get(d, 0)}")
    print(f"  Average risk score: {(total_score / max(len(evals), 1)):.1f}")
    print(f"  Review cards:       {len(cards)}")
    print(f"  Review packets:     {len(packets)}")
    print(f"  Heavy packets:      {len(heavy)}")
    print(f"  Advisory-only:      True")
    print("  Note: Depth assignments do not approve, seal, or authorize.")


def cmd_card_create(args):
    eval_rec = _load_record("evaluations", args.eval_id)
    if eval_rec is None:
        print(f"ERROR: Evaluation {args.eval_id} not found")
        sys.exit(1)
    if eval_rec.get("assigned_depth") != "light":
        print(f"WARNING: Evaluation depth is '{eval_rec.get('assigned_depth')}', not 'light'")

    ri = eval_rec.get("risk_inputs", {})
    rc_total = ri.get("rc_total_count", 0)
    rc_fail = ri.get("rc_failure_count", 0)
    e4_total = ri.get("e4_total_count", 0)
    e4_fail = ri.get("e4_failure_count", 0)
    rc_pass = rc_total - rc_fail
    e4_pass = e4_total - e4_fail

    clearance = "needs_attention" if (rc_fail > 0 or e4_fail > 0) else "cleared"

    cid = f"RC-{int(datetime.datetime.utcnow().timestamp()) % 100000:06d}"
    record = {
        "card_id": cid,
        "source_evaluation_id": eval_rec["evaluation_id"],
        "assigned_depth": "light",
        "risk_summary": args.risk_summary or f"Risk score {eval_rec['composite_risk_score']} — light review depth assigned. {rc_pass}/{rc_total} RC checks pass, {e4_pass}/{e4_total} E4 checks pass.",
        "rc_pass_count": rc_pass,
        "rc_total_count": rc_total,
        "rc_pass_rate": rc_pass / max(rc_total, 1),
        "eb_pass_count": e4_pass,
        "eb_total_count": e4_total,
        "eb_pass_rate": e4_pass / max(e4_total, 1),
        "clearance_status": clearance,
        "generated_at": _now(),
        "authority_disclaimer": CARD_DISCLAIMER,
        "custody": "qa-pilot-local",
        "advisory_only": True,
        "librarian_impact": "none",
    }

    schema_ok, schema_issues = _validate_schema(record, SCHEMA_CARD_PATH)
    rule_issues = _validate_card_rules(record)
    all_issues = schema_issues + rule_issues
    if all_issues:
        for i in all_issues:
            print(f"VALIDATION: {i}")

    index = _load_index()
    if cid in index.get("review_cards", []):
        print(f"ERROR: Card {cid} already exists")
        sys.exit(1)

    _save_record("cards", record, cid)
    index.setdefault("review_cards", []).append(cid)
    _save_index(index)
    print(f"Review card created: {cid}")
    print(f"  Clearance: {clearance}")
    print(f"  Advisory-only: True")


def cmd_packet_create(args):
    eval_rec = _load_record("evaluations", args.eval_id)
    if eval_rec is None:
        print(f"ERROR: Evaluation {args.eval_id} not found")
        sys.exit(1)

    ri = eval_rec.get("risk_inputs", {})
    pid = f"RP-{int(datetime.datetime.utcnow().timestamp()) % 100000:06d}"
    record = {
        "packet_id": pid,
        "source_evaluation_id": eval_rec["evaluation_id"],
        "assigned_depth": "standard",
        "evidence_bundle_review": args.evidence_review or f"E4 evidence bundle: {ri.get('e4_total_count', 0)} checks, {ri.get('e4_failure_count', 0)} failures.",
        "per_finding_commentary": [{"finding_ref": "E4-OVERALL", "commentary": f"{ri.get('e4_failure_count', 0)} E4 failures detected."}],
        "consistency_guard_evaluation": args.consistency_eval or f"RC guards: {ri.get('rc_total_count', 0)} checks, {ri.get('rc_failure_count', 0)} failures.",
        "risk_input_breakdown": {
            "authority_change": ri.get("authority_change", False),
            "production_path_impact": ri.get("production_path_impact", False),
            "ledger_registry_change": ri.get("ledger_registry_change", False),
            "cross_node_involvement": ri.get("cross_node_involvement", False),
            "partial_completion": ri.get("partial_completion", False),
            "incomplete_requirements_count": ri.get("incomplete_requirements", 0),
            "rc_failures": f"{ri.get('rc_failure_count', 0)}/{ri.get('rc_total_count', 0)}",
            "e4_failures": f"{ri.get('e4_failure_count', 0)}/{ri.get('e4_total_count', 0)}",
        },
        "recommendation_summary": args.recommendation or f"Risk score {eval_rec['composite_risk_score']} — standard review depth.",
        "generated_at": _now(),
        "authority_disclaimer": PACKET_DISCLAIMER,
        "custody": "qa-pilot-local",
        "advisory_only": True,
        "librarian_impact": "none",
    }

    schema_ok, schema_issues = _validate_schema(record, SCHEMA_PACKET_PATH)
    rule_issues = _validate_packet_rules(record)
    all_issues = schema_issues + rule_issues
    if all_issues:
        for i in all_issues:
            print(f"VALIDATION: {i}")

    index = _load_index()
    if pid in index.get("review_packets", []):
        print(f"ERROR: Packet {pid} already exists")
        sys.exit(1)

    _save_record("packets", record, pid)
    index.setdefault("review_packets", []).append(pid)
    _save_index(index)
    print(f"Review packet created: {pid}")
    print(f"  Advisory-only: True")


def cmd_packet_heavy_create(args):
    eval_rec = _load_record("evaluations", args.eval_id)
    if eval_rec is None:
        print(f"ERROR: Evaluation {args.eval_id} not found")
        sys.exit(1)

    ri = eval_rec.get("risk_inputs", {})
    esc = eval_rec.get("escalation_chain", [])

    pid = f"HP-{int(datetime.datetime.utcnow().timestamp()) % 100000:06d}"

    escalation_doc = []
    for rule_id in ["ER-1", "ER-2", "ER-3", "ER-4", "ER-5", "ER-6", "ER-7", "ER-8", "ER-9", "ER-10"]:
        escalation_doc.append({
            "rule_id": rule_id,
            "triggered": rule_id in esc,
            "effect": "Fired" if rule_id in esc else "Not triggered"
        })

    record = {
        "packet_id": pid,
        "source_evaluation_id": eval_rec["evaluation_id"],
        "assigned_depth": "heavy",
        "evidence_bundle_review": args.evidence_review or f"E4 evidence bundle: {ri.get('e4_total_count', 0)} checks, {ri.get('e4_failure_count', 0)} failures. Full trace attached.",
        "per_finding_commentary": [{"finding_ref": "E4-OVERALL", "commentary": "Heavy review: all E4 findings documented with full trace."}],
        "consistency_guard_evaluation": args.consistency_eval or f"RC guards: {ri.get('rc_total_count', 0)} checks, {ri.get('rc_failure_count', 0)} failures. Full evaluation attached.",
        "risk_input_breakdown": {
            "authority_change": ri.get("authority_change", False),
            "production_path_impact": ri.get("production_path_impact", False),
            "ledger_registry_change": ri.get("ledger_registry_change", False),
            "cross_node_involvement": ri.get("cross_node_involvement", False),
            "partial_completion": ri.get("partial_completion", False),
            "incomplete_requirements_count": ri.get("incomplete_requirements", 0),
            "rc_failures": f"{ri.get('rc_failure_count', 0)}/{ri.get('rc_total_count', 0)}",
            "e4_failures": f"{ri.get('e4_failure_count', 0)}/{ri.get('e4_total_count', 0)}",
        },
        "cross_node_involvement_trace": args.cross_node_trace or f"Cross-node: {'yes' if ri.get('cross_node_involvement') else 'no'}. Trace attached.",
        "authority_boundary_assessment": args.authority_assessment or f"Authority boundary: {'changed' if ri.get('authority_change') else 'unchanged'}. QA Pilot advisory-only preserved.",
        "registry_ledger_impact_analysis": args.registry_analysis or f"Registry/ledger impact: {'yes' if ri.get('ledger_registry_change') else 'no'}. Analysis attached.",
        "partial_completion_gap_evaluation": args.partial_eval or f"Partial completion: {'yes' if ri.get('partial_completion') else 'no'}. Gap evaluation attached.",
        "escalation_chain_documentation": escalation_doc,
        "full_evidence_trace": args.evidence_trace or "Full evidence trace attached. All RC and E4 findings documented.",
        "recommendation_summary": args.recommendation or f"Risk score {eval_rec['composite_risk_score']} — heavy review depth. Owner review recommended with full evidence trace.",
        "generated_at": _now(),
        "authority_disclaimer": HEAVY_DISCLAIMER,
        "custody": "qa-pilot-local",
        "advisory_only": True,
        "librarian_impact": "none",
    }

    schema_ok, schema_issues = _validate_schema(record, SCHEMA_HEAVY_PATH)
    rule_issues = _validate_heavy_rules(record)
    all_issues = schema_issues + rule_issues
    if all_issues:
        for i in all_issues:
            print(f"VALIDATION: {i}")

    index = _load_index()
    if pid in index.get("heavy_packets", []):
        print(f"ERROR: Heavy packet {pid} already exists")
        sys.exit(1)

    _save_record("heavy_packets", record, pid)
    index.setdefault("heavy_packets", []).append(pid)
    _save_index(index)
    print(f"Heavy evidence review packet created: {pid}")
    print(f"  Advisory-only: True")


def main():
    parser = argparse.ArgumentParser(description="QA Pilot Risk-Based Review Depth CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # depth-evaluate
    p_ev = sub.add_parser("depth-evaluate")
    p_ev.add_argument("--eval-id")
    p_ev.add_argument("--result-ref")
    p_ev.add_argument("--authority-change", type=lambda x: x.lower() == "true", default=False)
    p_ev.add_argument("--production-path-impact", type=lambda x: x.lower() == "true", default=False)
    p_ev.add_argument("--ledger-registry-change", type=lambda x: x.lower() == "true", default=False)
    p_ev.add_argument("--cross-node-involvement", type=lambda x: x.lower() == "true", default=False)
    p_ev.add_argument("--partial-completion", type=lambda x: x.lower() == "true", default=False)
    p_ev.add_argument("--incomplete-requirements", type=int, default=0)
    p_ev.add_argument("--rc-failure-count", type=int, default=0)
    p_ev.add_argument("--rc-total-count", type=int, default=11)
    p_ev.add_argument("--e4-failure-count", type=int, default=0)
    p_ev.add_argument("--e4-total-count", type=int, default=10)
    p_ev.add_argument("--lightweight-lane", type=lambda x: x.lower() == "true", default=False)
    p_ev.set_defaults(func=cmd_evaluate)

    # depth-read
    p_rd = sub.add_parser("depth-read")
    p_rd.add_argument("eval_id")
    p_rd.set_defaults(func=cmd_read)

    # depth-list
    p_li = sub.add_parser("depth-list")
    p_li.set_defaults(func=cmd_list)

    # depth-validate
    p_va = sub.add_parser("depth-validate")
    p_va.add_argument("--eval-id")
    p_va.add_argument("--eval-file")
    p_va.add_argument("--card-id")
    p_va.add_argument("--card-file")
    p_va.add_argument("--packet-id")
    p_va.add_argument("--packet-file")
    p_va.set_defaults(func=cmd_validate)

    # depth-status
    p_st = sub.add_parser("depth-status")
    p_st.set_defaults(func=cmd_status)

    # card-create
    p_cc = sub.add_parser("card-create")
    p_cc.add_argument("eval_id")
    p_cc.add_argument("--risk-summary")
    p_cc.set_defaults(func=cmd_card_create)

    # packet-create
    p_pc = sub.add_parser("packet-create")
    p_pc.add_argument("eval_id")
    p_pc.add_argument("--evidence-review")
    p_pc.add_argument("--consistency-eval")
    p_pc.add_argument("--recommendation")
    p_pc.set_defaults(func=cmd_packet_create)

    # packet-heavy-create
    p_hc = sub.add_parser("packet-heavy-create")
    p_hc.add_argument("eval_id")
    p_hc.add_argument("--evidence-review")
    p_hc.add_argument("--consistency-eval")
    p_hc.add_argument("--cross-node-trace")
    p_hc.add_argument("--authority-assessment")
    p_hc.add_argument("--registry-analysis")
    p_hc.add_argument("--partial-eval")
    p_hc.add_argument("--evidence-trace")
    p_hc.add_argument("--recommendation")
    p_hc.set_defaults(func=cmd_packet_heavy_create)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
