#!/usr/bin/env python3
"""
QA Pilot Qualification Execution Engine CLI.

Evaluates QR- records against qualification rules, manages lifecycle
states, generates qualification results, and produces execution receipts.

Commands:
  evaluate    Evaluate a single QR- record and generate qualification result
  batch       Batch-evaluate all QR- records in the store
  status      Show execution engine status
  lifecycle   Manage qualification record lifecycle state
  validate    Validate execution engine integrity
  receipt     Generate execution receipt

Pipeline:
  Evidence
     |
     v
  Evaluation Rules (QR-1 through QR-25)
     |
     v
  Qualification Result (pass/fail/advisory + level)
     |
     v
  Decision Artifact (execution receipt)
"""
import argparse, json, os, sys, datetime, glob, re, math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
VALIDATOR_PATH = os.path.join(SCRIPT_DIR, "validate-qa-pilot-qualification.py")
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "qualification-records")
STORE_INDEX = os.path.join(STORE_DIR, "qualification-index.json")
EXECUTION_LOG_DIR = os.path.join(PROJECT_ROOT, "data", "qualification-execution-logs")
EXECUTION_LOG_INDEX = os.path.join(EXECUTION_LOG_DIR, "execution-log.json")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "data", "qualification-results")
RESULTS_INDEX = os.path.join(RESULTS_DIR, "results-index.json")

# Scoring weights (from architecture doc Part III §3.3)
SCORE_WEIGHTS = {
    "schema_compliance": 0.25,
    "evidence_freshness": 0.20,
    "evidence_diversity": 0.15,
    "authority_boundary": 0.25,
    "provenance_quality": 0.15
}

# Level thresholds (from architecture doc Part I §1.3)
LEVEL_THRESHOLDS = [
    ("audited", 0.95, 3),
    ("peer_reviewed", 0.90, 2),
    ("spot_checked", 0.80, 1),
    ("unqualified", 0.0, 0)
]

# Lifecycle allowed transitions
LIFECYCLE_TRANSITIONS = {
    "proposed": ["in_progress"],
    "in_progress": ["completed", "proposed"],
    "completed": ["expired", "superseded", "revoked"],
    "expired": ["in_progress", "revoked"],
    "superseded": ["revoked"],
    "revoked": []
}


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _today():
    return datetime.date.today().isoformat()


def _ensure_dirs():
    os.makedirs(STORE_DIR, exist_ok=True)
    os.makedirs(EXECUTION_LOG_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    for path, default in [
        (STORE_INDEX, {"records": [], "last_updated": _now()}),
        (EXECUTION_LOG_INDEX, {"executions": [], "last_updated": _now()}),
        (RESULTS_INDEX, {"results": [], "last_updated": _now()})
    ]:
        if not os.path.exists(path):
            with open(path, "w") as f:
                json.dump(default, f, indent=2)


def _load_index(path):
    _ensure_dirs()
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"records": [], "last_updated": _now()}


def _save_index(index, path):
    index["last_updated"] = _now()
    with open(path, "w") as f:
        json.dump(index, f, indent=2)


def _load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def _load_qr_record(rid):
    path = os.path.join(STORE_DIR, f"{rid}.json")
    return _load_json(path)


def _call_validator(record):
    """Call the QR- validator on a record dict and return rule violations."""
    import subprocess, tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(record, f)
        tmp_path = f.name
    try:
        # Use the validator's internal validate_single function via subprocess
        result = subprocess.run(
            [sys.executable, VALIDATOR_PATH, "validate", "--record-id", record.get("record_id", "unknown")],
            capture_output=True, text=True, cwd=PROJECT_ROOT
        )
        violations = []
        if "FAIL" in result.stdout:
            for line in result.stdout.split("\n"):
                line = line.strip()
                if line.startswith("- "):
                    violations.append(line[2:])
                elif line.startswith("  - "):
                    violations.append(line[4:])
        return violations
    finally:
        os.unlink(tmp_path)


def _map_level(overall_score, evidence_count, authority_ok=True):
    """Map overall_score and evidence_count to qualification level."""
    for level, threshold, min_evidence in LEVEL_THRESHOLDS:
        if overall_score >= threshold and evidence_count >= min_evidence:
            if level == "audited" and evidence_count < 3:
                continue
            if level == "peer_reviewed" and evidence_count < 2:
                continue
            # Authority boundary check caps at spot_checked
            if not authority_ok and level in ("audited", "peer_reviewed"):
                return "spot_checked"
            return level
    return "unqualified"


def _compute_sub_dimensions(record, violations):
    """Compute sub-dimension scores from rule violations."""
    violation_text = " ".join(v.lower() for v in violations)
    scores = {}

    # schema_compliance: QR-1 through QR-5
    schema_rules = [f"QR-{i}" for i in range(1, 6)]
    schema_violations = sum(1 for v in violations if any(r in v for r in schema_rules))
    scores["schema_compliance"] = max(0.0, 1.0 - (schema_violations * 0.2))

    # evidence_freshness: QR-11, QR-14, QR-18
    fresh_violations = sum(1 for v in violations if any(r in v for r in ["QR-11", "QR-14", "QR-18"]))
    scores["evidence_freshness"] = max(0.0, 1.0 - (fresh_violations * 0.25))

    # evidence_diversity: based on evidence_refs count and types
    refs = record.get("evidence_refs", [])
    if isinstance(refs, list) and len(refs) > 0:
        types = set(r.get("evidence_type", "") for r in refs if isinstance(r, dict))
        diversity = min(1.0, len(types) / 5.0)
        scores["evidence_diversity"] = diversity
    else:
        scores["evidence_diversity"] = 0.0

    # authority_boundary: QR-6, QR-7, QR-8, QR-9
    auth_violations = sum(1 for v in violations if any(r in v for r in ["QR-6", "QR-7", "QR-8", "QR-9"]))
    scores["authority_boundary"] = max(0.0, 1.0 - (auth_violations * 0.25))

    # provenance_quality: QR-21, QR-22, QR-23, QR-24
    prov_violations = sum(1 for v in violations if any(r in v for r in ["QR-21", "QR-22", "QR-23", "QR-24"]))
    scores["provenance_quality"] = max(0.0, 1.0 - (prov_violations * 0.25))

    return scores


def _compute_overall_score(scores):
    """Compute weighted overall score from sub-dimension scores."""
    total = 0.0
    for dim, weight in SCORE_WEIGHTS.items():
        total += scores.get(dim, 0.0) * weight
    return round(total, 4)


def cmd_evaluate(args):
    """Evaluate a single QR- record and generate qualification result."""
    _ensure_dirs()

    record = _load_qr_record(args.record_id)
    if record is None:
        print(f"Record '{args.record_id}' not found.")
        return 1

    # Step 1: Run QR- rules against the record
    import subprocess
    result = subprocess.run(
        [sys.executable, VALIDATOR_PATH, "validate", "--record-id", args.record_id],
        capture_output=True, text=True, cwd=PROJECT_ROOT
    )

    # Parse violations from validator output
    violations = []
    if "FAIL" in result.stdout:
        for line in result.stdout.split("\n"):
            ls = line.strip()
            if ls.startswith("- "):
                violations.append(ls[2:])

    # Step 2: Compute sub-dimension scores
    sub_scores = _compute_sub_dimensions(record, violations)

    # Step 3: Compute overall score
    overall_score = _compute_overall_score(sub_scores)

    # Step 4: Check authority boundary
    authority_ok = sub_scores.get("authority_boundary", 0) >= 0.90

    # Step 5: Map to qualification level
    evidence_count = len(record.get("evidence_refs", []))
    level = _map_level(overall_score, evidence_count, authority_ok)

    # Step 6: Generate qualification result
    result_id = f"QRX-{args.record_id[3:]}"
    assessment = "pass" if level in ("audited", "peer_reviewed") else \
                 "advisory" if level == "spot_checked" else \
                 "fail"

    qr_result = {
        "result_id": result_id,
        "source_record": args.record_id,
        "target_id": record.get("target_id", "unknown"),
        "target_type": record.get("target_type", "unknown"),
        "qualification_type": record.get("qualification_type", "unknown"),
        "assessment": assessment,
        "qualification_level": level,
        "sub_dimension_scores": sub_scores,
        "overall_score": overall_score,
        "evidence_count": evidence_count,
        "violations": violations,
        "violation_count": len(violations),
        "authority_boundary_respected": authority_ok,
        "evaluated_at": _now(),
        "evaluated_by": "qa-pilot-qualification-execution"
    }

    # Write result
    result_path = os.path.join(RESULTS_DIR, f"{result_id}.json")
    with open(result_path, "w") as f:
        json.dump(qr_result, f, indent=2)

    # Update results index
    idx = _load_index(RESULTS_INDEX)
    if result_id not in idx.get("results", []):
        idx.setdefault("results", []).append(result_id)
        _save_index(idx, RESULTS_INDEX)

    # Update the QR- record's lifecycle state
    record["lifecycle_state"] = "completed"
    record["overall_score"] = overall_score
    record["sub_dimension_scores"] = sub_scores
    record["qualification_level"] = level
    qr_path = os.path.join(STORE_DIR, f"{args.record_id}.json")
    with open(qr_path, "w") as f:
        json.dump(record, f, indent=2)

    # Log execution
    log_idx = _load_index(EXECUTION_LOG_INDEX)
    log_entry = {
        "execution_id": result_id,
        "record_id": args.record_id,
        "level": level,
        "assessment": assessment,
        "overall_score": overall_score,
        "violations": len(violations),
        "evaluated_at": _now()
    }
    log_idx.setdefault("executions", []).append(log_entry)
    _save_index(log_idx, EXECUTION_LOG_INDEX)

    # Print result
    print(f"Evaluation: {args.record_id}")
    print(f"  Target:          {record.get('target_id')} ({record.get('target_type')})")
    print(f"  Level:           {level}")
    print(f"  Assessment:      {assessment}")
    print(f"  Overall score:   {overall_score:.4f}")
    print(f"  Evidence count:  {evidence_count}")
    print(f"  Violations:      {len(violations)}")
    print(f"  Authority OK:    {authority_ok}")
    print(f"  Result:          {result_id}")
    print(f"  Lifecycle:       completed")

    return 0


def cmd_batch(args):
    """Batch-evaluate all QR- records in the store."""
    _ensure_dirs()
    index = _load_index(STORE_INDEX)
    records = index.get("records", [])

    if not records:
        print("No QR- records in store.")
        return 0

    results_summary = {"pass": 0, "advisory": 0, "fail": 0, "total": 0}
    for rid in records:
        record = _load_qr_record(rid)
        if record is None:
            continue

        # Skip already evaluated records if --re-evaluate not set
        if record.get("lifecycle_state") == "completed" and not args.re_evaluate:
            ls = record.get("qualification_level", "unknown")
            if ls == "audited" or ls == "peer_reviewed":
                results_summary["pass"] += 1
            elif ls == "spot_checked":
                results_summary["advisory"] += 1
            else:
                results_summary["fail"] += 1
            results_summary["total"] += 1
            continue

        # Evaluate
        eval_args = argparse.Namespace(record_id=rid)
        code = cmd_evaluate(eval_args)
        if code != 0:
            continue

        # Read back the result
        record2 = _load_qr_record(rid)
        if record2:
            ls = record2.get("qualification_level", "unqualified")
            if ls in ("audited", "peer_reviewed"):
                results_summary["pass"] += 1
            elif ls == "spot_checked":
                results_summary["advisory"] += 1
            else:
                results_summary["fail"] += 1
            results_summary["total"] += 1

    print(f"\nBatch complete: {results_summary}")
    return 0


def cmd_status(args):
    """Show execution engine status."""
    _ensure_dirs()
    index = _load_index(STORE_INDEX)
    results_idx = _load_index(RESULTS_INDEX)
    exec_idx = _load_index(EXECUTION_LOG_INDEX)

    qr_count = len(index.get("records", []))
    result_count = len(results_idx.get("results", []))
    exec_count = len(exec_idx.get("executions", []))
    last_exec = exec_idx["executions"][-1]["evaluated_at"] if exec_idx.get("executions") else "never"

    # Level distribution
    levels = {"audited": 0, "peer_reviewed": 0, "spot_checked": 0, "unqualified": 0, "exempt": 0}
    lifecycles = {}
    for rid in index.get("records", []):
        rec = _load_qr_record(rid)
        if rec:
            lv = rec.get("qualification_level", "unqualified")
            levels[lv] = levels.get(lv, 0) + 1
            lc = rec.get("lifecycle_state", "unknown")
            lifecycles[lc] = lifecycles.get(lc, 0) + 1

    print("Qualification Execution Engine — Status")
    print("=" * 50)
    print(f"  QR- records:      {qr_count}")
    print(f"  Results:          {result_count}")
    print(f"  Executions:       {exec_count}")
    print(f"  Last execution:   {last_exec}")
    print(f"  Level distribution:")
    for lv, count in sorted(levels.items()):
        bar = "█" * min(count, 30)
        print(f"    {lv:16s} {count:3d} {bar}")
    print(f"  Lifecycle states: {lifecycles}")
    print(f"  Result store:     {RESULTS_DIR}")
    print(f"  Execution log:    {EXECUTION_LOG_INDEX}")

    return 0


def cmd_lifecycle(args):
    """Manage qualification record lifecycle state."""
    _ensure_dirs()

    if args.action == "list":
        index = _load_index(STORE_INDEX)
        print(f"{'Record ID':25s} {'Current State':16s} {'Target':20s} {'Type':20s}")
        print("-" * 85)
        for rid in index.get("records", []):
            rec = _load_qr_record(rid)
            if rec:
                print(f"{rid:25s} {rec.get('lifecycle_state','?'):16s} "
                      f"{rec.get('target_id','?'):20s} {rec.get('target_type','?'):20s}")
        return 0

    elif args.action == "transition":
        record = _load_qr_record(args.record_id)
        if record is None:
            print(f"Record '{args.record_id}' not found.")
            return 1

        current = record.get("lifecycle_state", "proposed")
        target = args.target_state

        allowed = LIFECYCLE_TRANSITIONS.get(current, [])
        if target not in allowed:
            print(f"Cannot transition {args.record_id}: {current} → {target}")
            print(f"  Allowed transitions from '{current}': {allowed}")
            return 1

        record["lifecycle_state"] = target
        if "lifecycle_notes" not in record:
            record["lifecycle_notes"] = []
        record["lifecycle_notes"].append({
            "from": current,
            "to": target,
            "reason": args.reason or f"transitioned at {_now()}",
            "timestamp": _now()
        })

        qr_path = os.path.join(STORE_DIR, f"{args.record_id}.json")
        with open(qr_path, "w") as f:
            json.dump(record, f, indent=2)

        print(f"Transitioned {args.record_id}: {current} → {target}")
        return 0

    else:
        print(f"Unknown lifecycle command: {args.action}")
        return 1


def cmd_validate(args):
    """Validate execution engine integrity."""
    _ensure_dirs()
    violations = []

    # Check result index consistency
    results_idx = _load_index(RESULTS_INDEX)
    for rid in results_idx.get("results", []):
        path = os.path.join(RESULTS_DIR, f"{rid}.json")
        if not os.path.exists(path):
            violations.append(f"Result '{rid}' in index but file missing")

    # Check execution log consistency
    exec_idx = _load_index(EXECUTION_LOG_INDEX)
    for entry in exec_idx.get("executions", []):
        rid = entry.get("record_id", "")
        if rid and not os.path.exists(os.path.join(STORE_DIR, f"{rid}.json")):
            violations.append(f"Execution references record '{rid}' but file missing")

    # Check level-score consistency for all evaluated records
    index = _load_index(STORE_INDEX)
    for rid in index.get("records", []):
        rec = _load_qr_record(rid)
        if rec and rec.get("lifecycle_state") == "completed":
            level = rec.get("qualification_level", "")
            score = rec.get("overall_score", 0)
            evidence = len(rec.get("evidence_refs", []))
            expected = _map_level(score, evidence)
            if level != expected and level != "exempt":
                violations.append(f"{rid}: level '{level}' does not match score {score} (expected '{expected}')")

    if violations:
        print(f"Integrity violations ({len(violations)}):")
        for v in violations:
            print(f"  ❌ {v}")
        return 1
    else:
        print("✅ Execution engine integrity: OK")
        return 0


def cmd_receipt(args):
    """Generate execution receipt."""
    _ensure_dirs()
    exec_idx = _load_index(EXECUTION_LOG_INDEX)
    executions = exec_idx.get("executions", [])

    if not executions:
        print("No executions recorded.")
        return 1

    results_idx = _load_index(RESULTS_INDEX)
    result_count = len(results_idx.get("results", []))

    # Count by assessment
    by_assessment = {"pass": 0, "advisory": 0, "fail": 0}
    for entry in executions:
        by_assessment[entry.get("assessment", "fail")] = \
            by_assessment.get(entry.get("assessment", "fail"), 0) + 1

    receipt = {
        "receipt_id": f"EXR-{_now()[:10].replace('-', '')}-001",
        "execution_count": len(executions),
        "result_count": result_count,
        "by_assessment": by_assessment,
        "last_execution": executions[-1]["evaluated_at"] if executions else _now(),
        "advisory_only": True,
        "custody": "qa-pilot-local",
        "librarian_impact": "none",
        "generated_at": _now(),
        "generated_by": "qa_pilot_qualification_execution.py receipt"
    }

    receipt_dir = os.path.join(PROJECT_ROOT, "receipts")
    os.makedirs(receipt_dir, exist_ok=True)
    receipt_path = os.path.join(receipt_dir, f"execution-{_now()[:10]}.json")
    with open(receipt_path, "w") as f:
        json.dump(receipt, f, indent=2)

    print(f"Execution receipt: {receipt_path}")
    print(f"  Total executions: {len(executions)}")
    print(f"  Results:          {result_count}")
    print(f"  Assessment dist:  {by_assessment}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="QA Pilot Qualification Execution Engine CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # evaluate
    p = sub.add_parser("evaluate", help="Evaluate a single QR- record")
    p.add_argument("--record-id", required=True, help="QR- record ID to evaluate")

    # batch
    p = sub.add_parser("batch", help="Batch-evaluate all QR- records")
    p.add_argument("--re-evaluate", action="store_true", help="Re-evaluate already-completed records")

    # status
    sub.add_parser("status", help="Show execution engine status")

    # lifecycle
    p = sub.add_parser("lifecycle", help="Manage lifecycle states")
    p.add_argument("action", choices=["list", "transition"],
                   help="Lifecycle action: list records or transition state")
    p.add_argument("--record-id", help="QR- record ID")
    p.add_argument("--target-state",
                   choices=["proposed", "in_progress", "completed", "expired", "superseded", "revoked"],
                   help="Target lifecycle state")
    p.add_argument("--reason", help="Reason for transition")

    # validate
    sub.add_parser("validate", help="Validate execution engine integrity")

    # receipt
    sub.add_parser("receipt", help="Generate execution receipt")

    args = parser.parse_args()

    if args.command == "evaluate":
        return cmd_evaluate(args)
    elif args.command == "batch":
        return cmd_batch(args)
    elif args.command == "status":
        return cmd_status(args)
    elif args.command == "lifecycle":
        return cmd_lifecycle(args)
    elif args.command == "validate":
        return cmd_validate(args)
    elif args.command == "receipt":
        return cmd_receipt(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
