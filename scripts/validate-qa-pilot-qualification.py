#!/usr/bin/env python3
"""
QA Pilot Qualification Validator — QR-1 through QR-25 rules.

Modes:
  fixture   Validate fixture files against schema + rules
  live      Validate live qualification store
  validate  Validate a specific qualification record
  chain     Run all upstream validators for regression
"""
import argparse, json, os, sys, datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-pilot-qualification-record.schema.json")
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "qualification-records")
STORE_INDEX = os.path.join(STORE_DIR, "qualification-index.json")
FIXTURE_DIR = os.path.join(PROJECT_ROOT, "docs", "examples", "qa-pilot-qualification")

DISCLAIMER = (
    "This is an advisory-only qualification record. "
    "It does not authorize implementation, seal, ledger mutation, "
    "or cross-project writes. Custody is qa-pilot-local. "
    "Librarian impact is none."
)

VALID_QUALIFICATION_TYPES = ["artifact", "process", "reviewer"]
VALID_TARGET_TYPES = [
    "workbench_item", "evidence_packet", "test_case", "result_packet",
    "epic_suite", "checklist", "review_packet", "decision_packet",
    "sprint", "startup_surface", "registry_entry", "custody_receipt",
    "pipeline_layer", "export_packet", "action_packet", "handoff_packet",
    "review_outcome", "readiness_posture"
]
VALID_QUALIFICATION_LEVELS = ["unqualified", "spot_checked", "peer_reviewed", "audited", "exempt"]
VALID_LIFECYCLE_STATES = ["proposed", "in_progress", "completed", "expired", "superseded", "revoked"]
VALID_EVIDENCE_TYPES = [
    "receipt", "validation_result", "test_result", "custody_audit",
    "drift_check", "pipeline_health", "registry_state", "snapshot_baseline",
    "owner_decision", "review_outcome", "advisory_packet", "export_packet",
    "workbench_item", "evidence_packet", "checklist_result", "linker_result",
    "result_packet"
]
VALID_VERIFICATION_STATUSES = ["verified", "stale", "missing", "corrupted"]

FORBIDDEN_FIELD_SUBSTRINGS = [
    "auto_accept", "auto_acceptance", "auto_reject", "auto_rejection",
    "executed_", "execution_result", "authorizes_execution",
    "seal_", "sealed", "approval_status", "approved_by",
    "evidence_verified", "items_closed", "mutates_evidence",
    "mutates_bundle", "mutates_packet"
]

FORBIDDEN_TERMS_IN_RATIONALE = [
    "auto-accepted", "auto-accept", "auto-rejected", "auto-reject",
    "executed", "authorizes", "seal", "approved", "verified", "closed",
    "defect accepted"
]


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _load_schema():
    """Load QR- schema from canonical path."""
    if not os.path.exists(SCHEMA_PATH):
        return None, f"schema not found at {SCHEMA_PATH}"
    try:
        with open(SCHEMA_PATH) as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"schema JSON error: {e}"


def _ensure_store():
    """Ensure qualification store and index exist."""
    os.makedirs(STORE_DIR, exist_ok=True)
    if not os.path.exists(STORE_INDEX):
        with open(STORE_INDEX, "w") as f:
            json.dump({"records": [], "last_updated": _now()}, f, indent=2)


def _load_index():
    _ensure_store()
    try:
        with open(STORE_INDEX) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"records": [], "last_updated": _now()}


def _save_index(index):
    index["last_updated"] = _now()
    with open(STORE_INDEX, "w") as f:
        json.dump(index, f, indent=2)


def _load_record(rid):
    path = os.path.join(STORE_DIR, f"{rid}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def _load_fixtures():
    """Load all fixture files from fixture directory."""
    if not os.path.exists(FIXTURE_DIR):
        return []
    fixtures = []
    for root, dirs, files in os.walk(FIXTURE_DIR):
        for fn in sorted(files):
            if fn.endswith(".json"):
                path = os.path.join(root, fn)
                is_valid = "valid" in root.split(os.sep)
                try:
                    with open(path) as f:
                        data = json.load(f)
                    fixtures.append({
                        "path": path,
                        "filename": fn,
                        "data": data,
                        "expected_valid": is_valid
                    })
                except json.JSONDecodeError as e:
                    fixtures.append({
                        "path": path,
                        "filename": fn,
                        "error": str(e),
                        "expected_valid": False
                    })
    return fixtures


def validate_schema(record):
    """Validate a record against the QR- JSON Schema."""
    schema, err = _load_schema()
    if err:
        return False, [f"schema_load_error: {err}"]
    try:
        import jsonschema
        try:
            jsonschema.validate(record, schema)
            return True, []
        except jsonschema.exceptions.ValidationError as e:
            return False, [f"schema violation: {e.message}"]
    except ImportError:
        # Fallback: basic field validation without jsonschema
        return validate_rules(record)


def validate_rules(record):
    """Apply QR-1 through QR-25 business rules."""
    violations = []

    # QR-1: Must be valid JSON (caller responsibility)
    # QR-2: Required fields checked by schema
    # QR-3: record_id pattern
    rid = record.get("record_id", "")
    import re
    if not re.match(r"^QR-[A-Z0-9]{4,12}-[0-9]{4}$", rid):
        violations.append("QR-3: record_id must match pattern QR-[A-Z0-9]{8}-[0-9]{4}")

    # QR-4: qualification_type
    qtype = record.get("qualification_type", "")
    if qtype not in VALID_QUALIFICATION_TYPES:
        violations.append(f"QR-4: qualification_type must be one of {VALID_QUALIFICATION_TYPES}")

    # QR-5: target_type
    ttype = record.get("target_type", "")
    if ttype not in VALID_TARGET_TYPES:
        violations.append(f"QR-5: target_type must be one of {VALID_TARGET_TYPES}")

    # QR-6: advisory_only
    if record.get("advisory_only") is not True:
        violations.append("QR-6: advisory_only must be true")

    # QR-7: custody
    if record.get("custody") != "qa-pilot-local":
        violations.append("QR-7: custody must be qa-pilot-local")

    # QR-8: librarian_impact
    if record.get("librarian_impact") != "none":
        violations.append("QR-8: librarian_impact must be 'none'")

    # QR-9: No forbidden authority-claiming fields
    for key in record:
        kl = key.lower()
        for p in FORBIDDEN_FIELD_SUBSTRINGS:
            if p in kl:
                violations.append(f"QR-9: forbidden field '{key}' claims authority")

    # QR-10: qualification_level
    qlevel = record.get("qualification_level", "")
    if qlevel not in VALID_QUALIFICATION_LEVELS:
        violations.append(f"QR-10: qualification_level must be one of {VALID_QUALIFICATION_LEVELS}")

    # QR-11: evidence_refs minItems
    evidence_refs = record.get("evidence_refs", [])
    if not isinstance(evidence_refs, list) or len(evidence_refs) < 1:
        violations.append("QR-11: evidence_refs must have at least 1 item")

    # QR-12: Each evidence_ref has evidence_id
    for i, ref in enumerate(evidence_refs if isinstance(evidence_refs, list) else []):
        if not ref.get("evidence_id"):
            violations.append(f"QR-12: evidence_refs[{i}] missing evidence_id")

    # QR-13: Each evidence_ref has verification_status
    for i, ref in enumerate(evidence_refs if isinstance(evidence_refs, list) else []):
        vs = ref.get("verification_status")
        if vs not in VALID_VERIFICATION_STATUSES:
            violations.append(f"QR-13: evidence_refs[{i}] verification_status must be one of {VALID_VERIFICATION_STATUSES}")

    # QR-14: No stale evidence (>90d)
    for i, ref in enumerate(evidence_refs if isinstance(evidence_refs, list) else []):
        va = ref.get("verified_at")
        if va:
            try:
                vd = datetime.datetime.fromisoformat(va.replace("Z", "+00:00"))
                age = datetime.datetime.now(datetime.timezone.utc) - vd
                if age.days > 90:
                    violations.append(f"QR-14: evidence_refs[{i}] evidence is stale (>90d)")
            except (ValueError, TypeError):
                violations.append(f"QR-14: evidence_refs[{i}] verified_at is not valid date-time")

    # QR-15: evidence_source path must exist (live mode only - skip for fixtures)
    # QR-16: overall_score range
    score = record.get("overall_score")
    if score is not None:
        if not isinstance(score, (int, float)) or score < 0.0 or score > 1.0:
            violations.append("QR-16: overall_score must be 0.0-1.0")

    # QR-17: level matches score range
    if score is not None and isinstance(score, (int, float)):
        if qlevel == "audited" and score < 0.95:
            violations.append("QR-17: audited level requires overall_score >= 0.95")
        elif qlevel == "peer_reviewed" and score < 0.90:
            violations.append("QR-17: peer_reviewed level requires overall_score >= 0.90")
        elif qlevel == "spot_checked" and score < 0.80:
            violations.append("QR-17: spot_checked level requires overall_score >= 0.80")

    # QR-18: audited requires >= 3 evidence_refs
    if qlevel == "audited":
        if not isinstance(evidence_refs, list) or len(evidence_refs) < 3:
            violations.append("QR-18: audited level requires >= 3 evidence_refs")

    # QR-19: expiry_date must be in the future
    expiry = record.get("expiry_date")
    if expiry:
        try:
            ed = datetime.date.fromisoformat(expiry)
            if ed < datetime.date.today():
                violations.append("QR-19: expiry_date is in the past")
        except (ValueError, TypeError):
            violations.append("QR-19: expiry_date is not valid date")

    # QR-20: If superseded_by set, target must exist
    sb = record.get("superseded_by")
    if sb:
        superseded = _load_record(sb)
        if superseded is None:
            violations.append(f"QR-20: superseded_by '{sb}' record not found")

    # QR-21: assessed_at must be valid date-time
    aa = record.get("assessed_at")
    if aa:
        try:
            datetime.datetime.fromisoformat(aa.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            violations.append("QR-21: assessed_at is not valid date-time")

    # QR-22: assessed_by must be non-empty
    ab = record.get("assessed_by")
    if not ab or (isinstance(ab, str) and not ab.strip()):
        violations.append("QR-22: assessed_by must be non-empty")

    # QR-23: provenance.assessor_id present
    prov = record.get("provenance", {})
    if not prov.get("assessor_id"):
        violations.append("QR-23: provenance.assessor_id must be present")

    # QR-24: provenance.session_id present
    if not prov.get("session_id"):
        violations.append("QR-24: provenance.session_id must be present")

    # QR-25: reviewer type must include owner_decision evidence
    if qtype == "reviewer":
        has_owner_dec = any(
            ref.get("evidence_type") == "owner_decision"
            for ref in (evidence_refs if isinstance(evidence_refs, list) else [])
        )
        if not has_owner_dec:
            violations.append("QR-25: reviewer qualification must include owner_decision evidence")

    return violations


def validate_single(record, check_paths=True):
    """Validate a single qualification record against schema + rules."""
    all_violations = []

    # Schema validation
    schema_ok, schema_errs = validate_schema(record)
    if not schema_ok:
        all_violations.extend(schema_errs)

    # Business rules
    rule_violations = validate_rules(record)
    all_violations.extend(rule_violations)

    # QR-15: evidence_source path must exist
    if check_paths:
        evidence_refs = record.get("evidence_refs", [])
        if isinstance(evidence_refs, list):
            for i, ref in enumerate(evidence_refs):
                src = ref.get("evidence_source", "")
                if src and not os.path.exists(os.path.join(PROJECT_ROOT, src)):
                    if not src.startswith("data/qualification"):
                        all_violations.append(f"QR-15: evidence_refs[{i}] source '{src}' not found")

    return all_violations


def cmd_fixture(args):
    """Validate all fixtures in the fixture directory."""
    fixtures = _load_fixtures()
    if not fixtures:
        print("No fixtures found.")
        return 0 if args.pass_on_empty else 1

    results = {"pass": 0, "fail": 0, "skipped": 0, "details": []}
    for fx in fixtures:
        if "error" in fx:
            results["fail"] += 1
            results["details"].append({
                "fixture": fx["filename"],
                "expected": "invalid",
                "actual": "invalid (parse error)",
                "violations": [f"JSON parse error: {fx['error']}"],
                "match": True
            })
            continue

        violations = validate_single(fx["data"], check_paths=False)
        is_valid = len(violations) == 0
        match = is_valid == fx["expected_valid"]

        if match:
            results["pass"] += 1
        else:
            results["fail"] += 1

        results["details"].append({
            "fixture": fx["filename"],
            "expected": "valid" if fx["expected_valid"] else "invalid",
            "actual": "valid" if is_valid else "invalid",
            "violations": violations,
            "match": match
        })

    print(f"Fixtures: {results['pass']} pass, {results['fail']} fail, {results['skipped']} skipped\n")
    for d in results["details"]:
        status = "✅ PASS" if d["match"] else "❌ FAIL"
        print(f"  {status} {d['fixture']} (expected={d['expected']}, actual={d['actual']})")
        if not d["match"] and d["violations"]:
            for v in d["violations"]:
                print(f"       - {v}")

    return 0 if results["fail"] == 0 else 1


def cmd_live(args):
    """Validate all records in the live qualification store."""
    index = _load_index()
    records = index.get("records", [])
    if not records:
        print("Qualification store is empty.")
        return 0 if args.pass_on_empty else 1

    results = {"pass": 0, "fail": 0, "details": []}
    for rid in records:
        record = _load_record(rid)
        if record is None:
            results["fail"] += 1
            results["details"].append({
                "record": rid,
                "status": "fail",
                "violations": [f"record '{rid}' referenced in index but not found in store"]
            })
            continue
        violations = validate_single(record, check_paths=True)
        if violations:
            results["fail"] += 1
        else:
            results["pass"] += 1
        results["details"].append({
            "record": rid,
            "status": "pass" if not violations else "fail",
            "violations": violations
        })

    print(f"Live store: {results['pass']} pass, {results['fail']} fail\n")
    for d in results["details"]:
        status = "✅" if d["status"] == "pass" else "❌"
        print(f"  {status} {d['record']}")
        for v in d.get("violations", []):
            print(f"       - {v}")

    return 0 if results["fail"] == 0 else 1


def cmd_validate(args):
    """Validate a specific qualification record by ID."""
    record = _load_record(args.record_id)
    if record is None:
        print(f"Record '{args.record_id}' not found.")
        return 1

    violations = validate_single(record, check_paths=True)
    if violations:
        print(f"❌ {args.record_id}: FAIL")
        for v in violations:
            print(f"  - {v}")
        return 1
    else:
        print(f"✅ {args.record_id}: PASS")
        return 0


def cmd_chain(args):
    """Run upstream validators for regression (placeholder for future integration)."""
    print("Chain validation: QR- validator self-check")
    print(f"Schema: {'✅' if os.path.exists(SCHEMA_PATH) else '❌'} {SCHEMA_PATH}")
    print(f"Store:  {'✅' if os.path.exists(STORE_DIR) else '⚠️'} {STORE_DIR}")
    print(f"Index:  {'✅' if os.path.exists(STORE_INDEX) else '⚠️'} {STORE_INDEX}")

    # Run self-test on a minimal valid record
    minimal = {
        "record_id": "QR-SELFTEST-0001",

        "qualification_type": "artifact",
        "target_id": "self-test",
        "target_type": "workbench_item",
        "qualification_level": "spot_checked",
        "evidence_refs": [{
            "evidence_id": "SELFTEST-EVIDENCE-001",
            "evidence_type": "validation_result",
            "evidence_source": "scripts/validate-qa-pilot-qualification.py",
            "verification_status": "verified",
            "verified_at": _now()
        }],
        "overall_score": 0.85,
        "sub_dimension_scores": {"test": 0.85},
        "lifecycle_state": "completed",
        "provenance": {
            "assessor_id": "self-test",
            "session_id": "self-test",
            "tool_call_log": "self-test"
        },
        "advisory_only": True,
        "custody": "qa-pilot-local",
        "librarian_impact": "none",
        "assessed_at": _now(),
        "assessed_by": "self-test"
    }

    violations = validate_single(minimal, check_paths=False)
    print(f"Self-test:    {'✅ PASS' if not violations else '❌ FAIL'}")
    for v in violations:
        print(f"  - {v}")

    return 0 if not violations else 1


def main():
    parser = argparse.ArgumentParser(description="QA Pilot Qualification Validator")
    parser.add_argument("mode", choices=["fixture", "live", "validate", "chain"],
                        help="Validation mode")
    parser.add_argument("--record-id", help="Record ID for validate mode")
    parser.add_argument("--pass-on-empty", action="store_true", default=True,
                        help="Return 0 when store/fixtures are empty")
    parser.add_argument("--fail-on-empty", action="store_false", dest="pass_on_empty",
                        help="Return 1 when store/fixtures are empty")

    args = parser.parse_args()

    if args.mode == "fixture":
        return cmd_fixture(args)
    elif args.mode == "live":
        return cmd_live(args)
    elif args.mode == "validate":
        if not args.record_id:
            print("Error: --record-id required for validate mode")
            return 1
        return cmd_validate(args)
    elif args.mode == "chain":
        return cmd_chain(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
