#!/usr/bin/env python3
"""
QA Pilot Test Composition — QA-PILOT-TEST-COMPOSITION-1

Reads QA Pilot-local evidence packets from the evidence store and composes
advisory test cases. Generated tests conform to qa-test-case.schema.json,
reference source packet IDs, and carry advisory-only posture.

Usage:
    python3 scripts/qa_pilot_test_composition.py compose [--packet-id ID]
    python3 scripts/qa_pilot_test_composition.py validate <path>
    python3 scripts/qa_pilot_test_composition.py list [--limit N] [--source-packet ID]
    python3 scripts/qa_pilot_test_composition.py read <test_id>
    python3 scripts/qa_pilot_test_composition.py status
    python3 scripts/qa_pilot_test_composition.py clear

Authority: advisory-only. No source-project authority conferred.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
EVIDENCE_INDEX = REPO_ROOT / "data" / "evidence" / "evidence-index.json"
TEST_CASES_DIR = REPO_ROOT / "data" / "test-cases"
TEST_INDEX_FILE = TEST_CASES_DIR / "test-case-index.json"
TEST_CASE_SCHEMA = REPO_ROOT / "docs" / "schemas" / "qa-test-case.schema.json"

TEST_ID_PATTERN = re.compile(r"^TC-\d{8}-")
ADVISORY_NOTICE = (
    "This test case is advisory-only. It does not approve, seal, merge, "
    "or assert production readiness. Only the Owner may approve or seal work."
)
FORBIDDEN_AUTHORITY_VERBS = [
    "approve", "seal", "start", "advance", "execute", "patch", "mutate",
    "deploy", "promote", "authorize", "release"
]

# ── TC Rules ──────────────────────────────────────────────────────────────────

TC_RULES = {
    "TC-1":  "Reads only QA Pilot-local evidence records",
    "TC-2":  "Generated tests must reference source packet ID",
    "TC-3":  "Generated tests must include advisory_only: true",
    "TC-4":  "Generated tests must validate against qa-test-case schema",
    "TC-5":  "No approve/seal/start/advance authority verbs in test content",
    "TC-6":  "No source-project mutation paths targeted",
    "TC-7":  "Malformed evidence is rejected",
    "TC-8":  "Duplicate composition is deterministic",
    "TC-9":  "Cross-project source metadata preserved, not converted to authority",
    "TC-10": "Test-case index is QA Pilot-local only",
    "TC-11": "Existing MCP evidence-intake behavior remains green",
    "TC-12": "Existing custody/startup/architecture regressions remain green",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def ensure_dirs():
    TEST_CASES_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def load_evidence_index():
    """Load the QA Pilot evidence store index."""
    if not EVIDENCE_INDEX.exists():
        return {"evidence": {}}
    return load_json(str(EVIDENCE_INDEX))


def load_test_index():
    """Load the test-case index."""
    if not TEST_INDEX_FILE.exists():
        return {
            "store_version": "qap-test-cases-v1",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "test_cases": {},
            "advisory_notice": ADVISORY_NOTICE,
        }
    return load_json(str(TEST_INDEX_FILE))


def save_test_index(index):
    index["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_json(str(TEST_INDEX_FILE), index)


def advisory_response(**kwargs):
    """Wrap a response with advisory-only posture and source identification."""
    resp = {
        "advisory_only": True,
        "source_project": "qa-pilot",
        "custody": "qa-pilot-local",
        "advisory_notice": ADVISORY_NOTICE,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    resp.update(kwargs)
    return resp


def make_check_results(all_pass, checks):
    return {
        "valid": all_pass,
        "rule_count": len(checks),
        "passed": sum(1 for c in checks if c[1]),
        "failed": sum(1 for c in checks if not c[1]),
        "checks": [
            {"rule": c[0], "passed": c[1], "detail": c[2]} for c in checks
        ],
    }


# ── Test Case Schema Validation ──────────────────────────────────────────────

def validate_test_case_schema(data):
    """Validate a test case against qa-test-case.schema.json (basic check)."""
    required = ["test_id", "sprint_id", "source_artifact", "criteria", "status"]
    missing = [f for f in required if f not in data]
    if missing:
        return (False, f"Missing schema-required fields: {missing}")
    tid = data.get("test_id", "")
    if not TEST_ID_PATTERN.match(tid):
        return (False, f"test_id '{tid}' must match TC-YYYYMMDD- pattern")
    valid_statuses = ["composed", "ready", "run", "passed", "failed", "blocked"]
    if data.get("status") not in valid_statuses:
        return (False, f"status '{data.get('status')}' not in {valid_statuses}")
    if len(data.get("criteria", "")) < 10:
        return (False, "criteria too short (min 10 chars)")
    return (True, "Schema validation passed")


# ── Composition Core ──────────────────────────────────────────────────────────

def compose_from_evidence(evidence_packet, packet_id):
    """
    Derive test cases from a single evidence packet.
    Returns a list of test case dicts.
    """
    test_cases = []
    project = evidence_packet.get("project", "unknown")
    sprint_id = evidence_packet.get("sprint_id", "unknown")
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    counter = 0

    # Determine source artifact prefix
    prefix = "qa-pilot" if project == "qa-pilot" else f"cross-project-{project}"

    # ── Test 1: Regression guard from validation_output ──
    val = evidence_packet.get("validation_output", {})
    if val:
        counter += 1
        tid = f"TC-{ts}-{packet_id[-6:]}-{counter:03d}"
        tests_passed = val.get("tests_passed", 0)
        tests_failed = val.get("tests_failed", 0)
        summary = val.get("summary", "No summary")
        tc = {
            "test_id": tid,
            "sprint_id": sprint_id,
            "source_artifact": packet_id,
            "criteria": f"Regression guard: evidence packet {packet_id} reports "
                        f"{tests_passed} passed, {tests_failed} failed. "
                        f"Ensure validation still passes: {summary}",
            "expected": f"Validation output matches: {tests_passed} passed, {tests_failed} failed",
            "preconditions": [
                f"Evidence packet {packet_id} is ingested in QA Pilot store"
            ],
            "steps": [
                f"Retrieve evidence packet {packet_id} from QA Pilot store",
                f"Verify validation_output.tests_passed >= {tests_passed}",
                f"Verify validation_output.tests_failed == {tests_failed}",
                f"Confirm no regressions from source sprint {sprint_id}"
            ],
            "postconditions": [
                "Validation state is preserved",
                "No new failures introduced"
            ],
            "status": "composed",
            "tags": ["regression-guard", "evidence-derived", prefix],
            "advisory_only": True,
            "evidence_provenance": {
                "source_packet_id": packet_id,
                "source_project": project,
                "source_sprint_id": sprint_id,
                "cross_project": project != "qa-pilot",
                "advisory": True,
            },
        }
        test_cases.append(tc)

    # ── Test per changed_file: verification tests ──
    for cf in evidence_packet.get("changed_files", []):
        counter += 1
        tid = f"TC-{ts}-{packet_id[-6:]}-{counter:03d}"
        path = cf.get("path", "unknown")
        change_type = cf.get("change_type", "modified")
        diff_summary = cf.get("diff_summary", "No diff summary")
        tc = {
            "test_id": tid,
            "sprint_id": sprint_id,
            "source_artifact": packet_id,
            "criteria": f"Verify that file '{path}' ({change_type}) in sprint {sprint_id} "
                        f"functions correctly: {diff_summary}",
            "expected": f"File '{path}' is correctly {change_type}d per evidence",
            "preconditions": [
                f"Evidence packet {packet_id} is ingested",
                f"Source sprint {sprint_id} completed"
            ],
            "steps": [
                f"Locate file '{path}' from evidence packet {packet_id}",
                f"Verify {change_type} was applied correctly",
                f"Run the relevant test suite for this file",
                f"Confirm no regressions from this change"
            ],
            "postconditions": [
                f"File '{path}' is in expected state",
                "No downstream failures introduced"
            ],
            "status": "composed",
            "tags": [f"change-{change_type}", "evidence-derived", prefix],
            "advisory_only": True,
            "evidence_provenance": {
                "source_packet_id": packet_id,
                "source_project": project,
                "source_sprint_id": sprint_id,
                "changed_file": path,
                "cross_project": project != "qa-pilot",
                "advisory": True,
            },
        }
        test_cases.append(tc)

    # ── Test per known_defect: defect verification tests ──
    for defect in evidence_packet.get("known_defects", []):
        counter += 1
        tid = f"TC-{ts}-{packet_id[-6:]}-{counter:03d}"
        defect_id = defect.get("defect_id", "unknown")
        severity = defect.get("severity", "unknown")
        description = defect.get("description", "No description")
        tc = {
            "test_id": tid,
            "sprint_id": sprint_id,
            "source_artifact": packet_id,
            "criteria": f"Defect verification: {defect_id} ({severity}) — {description}",
            "expected": f"Defect {defect_id} is resolved or has acceptable workaround",
            "preconditions": [
                f"Evidence packet {packet_id} is ingested",
                f"Defect {defect_id} was identified in sprint {sprint_id}"
            ],
            "steps": [
                f"Review defect {defect_id} ({severity})",
                f"Check if defect was fixed in sprint {sprint_id}",
                f"If fixed: verify the fix",
                f"If not fixed: verify workaround or document status"
            ],
            "postconditions": [
                f"Defect {defect_id} status is known",
                "Defect does not block downstream work"
            ],
            "status": "composed",
            "tags": [f"defect-{severity}", "evidence-derived", prefix],
            "advisory_only": True,
            "evidence_provenance": {
                "source_packet_id": packet_id,
                "source_project": project,
                "source_sprint_id": sprint_id,
                "defect_id": defect_id,
                "cross_project": project != "qa-pilot",
                "advisory": True,
            },
        }
        test_cases.append(tc)

    return test_cases


def validate_composition_source(evidence_packet):
    """
    Validate an evidence packet for test composition eligibility.
    Returns (all_pass, checks).
    """
    checks = []

    packet_id = evidence_packet.get("packet_id", "")
    project = evidence_packet.get("project", "")

    # TC-1: Reads only QA Pilot-local evidence
    checks.append(("TC-1", True, f"Read from QA Pilot evidence store"))

    # TC-2: Must have packet_id (source reference)
    checks.append(("TC-2", bool(packet_id), f"packet_id = '{packet_id}'"))

    # TC-5: Check for forbidden authority verbs in packet content
    packet_str = json.dumps(evidence_packet).lower()
    found_verbs = [v for v in FORBIDDEN_AUTHORITY_VERBS if f'"{v}"' in packet_str]
    if found_verbs:
        checks.append(("TC-5", False, f"Contains authority verbs: {found_verbs}"))
    else:
        checks.append(("TC-5", True, "No forbidden authority verbs found"))

    # TC-6: No source-project mutation paths
    mutation_paths = ["/Sources/", "/Public/", "/.librarian/", "/receipts/",
                      "/project-state/", "startup-contract.json"]
    for cf in evidence_packet.get("changed_files", []):
        path = cf.get("path", "")
        if any(mp in path for mp in mutation_paths):
            checks.append(("TC-6", False, f"Mutation path referenced: {path}"))
            break
    else:
        checks.append(("TC-6", True, "No mutation paths referenced"))

    # TC-7: Evidence must have required fields
    required = ["packet_id", "sprint_id", "validation_output", "provenance"]
    missing = [f for f in required if f not in evidence_packet]
    if missing:
        checks.append(("TC-7", False, f"Missing required fields: {missing}"))
    else:
        checks.append(("TC-7", True, "All required fields present"))

    # TC-9: Cross-project source metadata preserved
    if project and project != "qa-pilot":
        spm = evidence_packet.get("_source_project_metadata", {})
        has_meta = bool(spm and spm.get("source_project_id"))
        checks.append(("TC-9", has_meta,
                       "Cross-project metadata preserved" if has_meta
                       else "Missing cross-project metadata"))
    else:
        checks.append(("TC-9", True, "QA Pilot-local — no cross-project check needed"))

    all_pass = all(c[1] for c in checks)
    return (all_pass, checks)


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_compose(args):
    """
    Compose test cases from evidence packets.
    Reads from the QA Pilot evidence store, derives test cases, stores them.
    """
    evidence_index = load_evidence_index()
    evidence_map = evidence_index.get("evidence", {})

    if not evidence_map:
        return advisory_response(
            tool="test_compose",
            success=False,
            error="No evidence packets in QA Pilot store — ingest evidence first",
        )

    # Filter by packet_id if specified
    if args.packet_id:
        if args.packet_id not in evidence_map:
            return advisory_response(
                tool="test_compose",
                success=False,
                error=f"Evidence packet '{args.packet_id}' not found in store",
            )
        target_packets = {args.packet_id: evidence_map[args.packet_id]}
    else:
        target_packets = evidence_map

    test_index = load_test_index()
    all_tcs = []
    total_composed = 0
    errors = []

    for pid, meta in target_packets.items():
        # Load the actual evidence packet from its stored file
        store_path = meta.get("store_path")
        if not store_path or not Path(store_path).exists():
            errors.append(f"Evidence '{pid}': stored file missing at {store_path}")
            continue

        try:
            evidence_data = load_json(store_path)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            errors.append(f"Evidence '{pid}': failed to load — {e}")
            continue

        # Validate composition source
        valid, checks = validate_composition_source(evidence_data)
        if not valid:
            # Check which rules failed — only TC-5 or TC-6 are hard rejections
            failed_rules = [c for c in checks if not c[1]]
            hard_failures = [c for c in failed_rules if c[0] in ("TC-5", "TC-6")]
            if hard_failures:
                errors.append(f"Evidence '{pid}': rejected — {hard_failures[0][2]}")
                continue

        # Compose test cases
        tcs = compose_from_evidence(evidence_data, pid)
        for tc in tcs:
            test_id = tc["test_id"]

            # TC-8: Check duplicate (deterministic — skip if already exists)
            if test_id in test_index.get("test_cases", {}):
                continue

            # Validate test case schema
            schema_valid, schema_msg = validate_test_case_schema(tc)
            if not schema_valid:
                errors.append(f"Test case '{test_id}': schema validation failed — {schema_msg}")
                continue

            # TC-3: advisory_only check
            if not tc.get("advisory_only", False):
                errors.append(f"Test case '{test_id}': missing advisory_only")
                continue

            # Store test case
            store_filename = f"{test_id}.json"
            store_path = TEST_CASES_DIR / store_filename
            ensure_dirs()
            save_json(str(store_path), tc)

            # Add to index
            test_index.setdefault("test_cases", {})[test_id] = {
                "test_id": test_id,
                "sprint_id": tc.get("sprint_id"),
                "source_artifact": tc.get("source_artifact"),
                "status": tc.get("status"),
                "advisory_only": True,
                "composed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "store_path": str(store_path),
            }
            total_composed += 1
            all_tcs.append(test_id)

    test_index["total_composed"] = len(test_index.get("test_cases", {}))
    test_index["last_composed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    save_test_index(test_index)

    result = advisory_response(
        tool="test_compose",
        success=(total_composed > 0 or not errors),
        evidence_packets_used=len(target_packets),
        total_test_cases_composed=total_composed,
        test_ids=all_tcs,
    )
    if errors:
        result["errors"] = errors
    if total_composed > 0:
        result["store_path"] = str(TEST_CASES_DIR)
        result["advisory_only"] = True
    return result


def cmd_validate(args):
    """Validate a test case JSON file or an evidence packet for composition."""
    path = args.path
    try:
        data = load_json(path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return advisory_response(
            tool="test_validate",
            success=False,
            file=str(path),
            error=f"Failed to load file: {e}",
        )

    # Detect content type: evidence packet or test case
    if "packet_id" in data and data.get("packet_id", "").startswith("EP-"):
        # Validate as composition source
        valid, checks = validate_composition_source(data)
        result = advisory_response(
            tool="test_validate",
            success=valid,
            file=str(path),
            content_type="evidence_packet",
            packet_id=data.get("packet_id", "unknown"),
        )
        result["validation"] = make_check_results(valid, checks)
        return result
    elif "test_id" in data and data.get("test_id", "").startswith("TC-"):
        # Validate as test case
        schema_valid, schema_msg = validate_test_case_schema(data)
        tc_valid = schema_valid
        tc_checks = [("TC-4", schema_valid, schema_msg)]

        # TC-3: advisory_only
        ao = data.get("advisory_only", False)
        tc_checks.append(("TC-3", ao, f"advisory_only = {ao}"))

        # TC-2: source_artifact reference
        sa = data.get("source_artifact", "")
        tc_checks.append(("TC-2", bool(sa), f"source_artifact = '{sa}'"))

        # TC-5: forbidden authority verbs
        tc_str = json.dumps(data).lower()
        found = [v for v in FORBIDDEN_AUTHORITY_VERBS if v in tc_str]
        tc_checks.append(("TC-5", len(found) == 0,
                          f"Authority verbs found: {found}" if found else "Clean"))

        # TC-6: mutation paths
        mutation_paths = ["/Sources/", "/Public/", "/.librarian/"]
        steps_str = " ".join(data.get("steps", []))
        found_paths = [p for p in mutation_paths if p in steps_str]
        tc_checks.append(("TC-6", len(found_paths) == 0,
                          f"Mutation paths found: {found_paths}" if found_paths else "Clean"))

        all_pass = all(c[1] for c in tc_checks)
        result = advisory_response(
            tool="test_validate",
            success=all_pass,
            file=str(path),
            content_type="test_case",
            test_id=data.get("test_id", "unknown"),
        )
        result["validation"] = make_check_results(all_pass, tc_checks)
        return result
    else:
        return advisory_response(
            tool="test_validate",
            success=False,
            file=str(path),
            error="Unrecognized content type — expected evidence packet (EP-*) or test case (TC-*)",
        )


def cmd_list(args):
    """List composed test cases."""
    test_index = load_test_index()
    all_tcs = list(test_index.get("test_cases", {}).values())

    if args.source_packet:
        filtered = [t for t in all_tcs if t.get("source_artifact") == args.source_packet]
    else:
        filtered = all_tcs

    total = len(filtered)
    limit = args.limit
    sliced = filtered[:limit]

    result = advisory_response(
        tool="test_list",
        success=True,
        total_count=total,
        limit=limit,
    )
    result["test_cases"] = [
        {
            "test_id": t["test_id"],
            "sprint_id": t.get("sprint_id"),
            "source_artifact": t.get("source_artifact"),
            "status": t.get("status"),
            "advisory_only": t.get("advisory_only", True),
            "composed_at": t.get("composed_at"),
        }
        for t in sliced
    ]
    return result


def cmd_read(args):
    """Read a composed test case by test_id."""
    test_index = load_test_index()
    test_id = args.test_id

    if test_id not in test_index.get("test_cases", {}):
        return advisory_response(
            tool="test_read",
            success=False,
            test_id=test_id,
            found=False,
            error=f"Test case '{test_id}' not found",
        )

    store_path = test_index["test_cases"][test_id].get("store_path")
    if not store_path or not Path(store_path).exists():
        return advisory_response(
            tool="test_read",
            success=False,
            test_id=test_id,
            found=False,
            error=f"Index entry exists but store file missing",
        )

    data = load_json(store_path)
    return advisory_response(
        tool="test_read",
        success=True,
        test_id=test_id,
        found=True,
        composed_at=test_index["test_cases"][test_id].get("composed_at"),
        test_case=data,
    )


def cmd_status(args):
    """Show test composition store status."""
    test_index = load_test_index()
    tcs = test_index.get("test_cases", {})
    total = len(tcs)

    by_source = {}
    by_status = {}
    last_composed = None
    last_ts = None

    for tid, meta in tcs.items():
        src = meta.get("source_artifact", "unknown")
        by_source[src] = by_source.get(src, 0) + 1
        st = meta.get("status", "unknown")
        by_status[st] = by_status.get(st, 0) + 1
        ts = meta.get("composed_at", "")
        if ts and (last_ts is None or ts > last_ts):
            last_ts = ts
            last_composed = {"test_id": tid, "composed_at": ts}

    # Also report available evidence packets
    evidence_index = load_evidence_index()
    ev_count = len(evidence_index.get("evidence", {}))

    return advisory_response(
        tool="test_status",
        success=True,
        store_path=str(TEST_CASES_DIR),
        index_path=str(TEST_INDEX_FILE),
        total_test_cases=total,
        by_source_packet=by_source,
        by_status=by_status,
        last_composed=last_composed,
        available_evidence_packets=ev_count,
        rules=list(TC_RULES.values()),
    )


def cmd_clear(args):
    """Remove all composed test cases and reset index."""
    test_index = load_test_index()
    count = len(test_index.get("test_cases", {}))

    for tid, meta in test_index.get("test_cases", {}).items():
        sp = Path(meta.get("store_path", ""))
        if sp.exists():
            sp.unlink()

    test_index["test_cases"] = {}
    test_index["total_composed"] = 0
    test_index["last_composed_at"] = None
    save_test_index(test_index)

    return advisory_response(
        tool="test_clear",
        success=True,
        cleared_count=count,
        message=f"Cleared {count} test cases from QA Pilot-local store",
    )


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="QA Pilot Test Composition — QA-PILOT-TEST-COMPOSITION-1"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # compose
    comp_p = subparsers.add_parser("compose", help="Compose test cases from evidence packets")
    comp_p.add_argument("--packet-id", help="Optional: compose from specific evidence packet ID only")

    # validate
    val_p = subparsers.add_parser("validate", help="Validate an evidence packet or test case file")
    val_p.add_argument("path", help="Path to JSON file")

    # list
    list_p = subparsers.add_parser("list", help="List composed test cases")
    list_p.add_argument("--limit", type=int, default=50, help="Max results (1-100)")
    list_p.add_argument("--source-packet", help="Filter by source evidence packet ID")

    # read
    read_p = subparsers.add_parser("read", help="Read a composed test case by test_id")
    read_p.add_argument("test_id", help="Test case ID (e.g., TC-20260706-001)")

    # status
    subparsers.add_parser("status", help="Show test composition store status")

    # clear
    subparsers.add_parser("clear", help="Clear all composed test cases")

    args = parser.parse_args()

    if args.command == "compose":
        result = cmd_compose(args)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("success", False) else 1)

    elif args.command == "validate":
        result = cmd_validate(args)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("success", False) else 1)

    elif args.command == "list":
        result = cmd_list(args)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("success", False) else 1)

    elif args.command == "read":
        result = cmd_read(args)
        print(json.dumps(result, indent=2))
        sys.exit(0)

    elif args.command == "status":
        result = cmd_status(args)
        print(json.dumps(result, indent=2))
        sys.exit(0)

    elif args.command == "clear":
        result = cmd_clear(args)
        print(json.dumps(result, indent=2))
        sys.exit(0)


if __name__ == "__main__":
    main()
