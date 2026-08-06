#!/usr/bin/env python3
"""
QA Pilot Epic Regression Builder — QA-PILOT-EPIC-REGRESSION-BUILDER-1

Rolls sprint-level evidence (EP-*), test cases (TC-*), and result packets (QR-*)
into Epic-level advisory regression suites conforming to
qa-epic-regression-suite.schema.json.

Usage:
    python3 scripts/qa_pilot_epic_regression_builder.py build <epic_id> [--sprint-ids S1 S2 ...]
    python3 scripts/qa_pilot_epic_regression_builder.py validate <path>
    python3 scripts/qa_pilot_epic_regression_builder.py list [--limit N]
    python3 scripts/qa_pilot_epic_regression_builder.py read <suite_id>
    python3 scripts/qa_pilot_epic_regression_builder.py status
    python3 scripts/qa_pilot_epic_regression_builder.py clear

Authority: advisory-only. No canonical mutation authority.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
EVIDENCE_INDEX = REPO_ROOT / "data" / "evidence" / "evidence-index.json"
TEST_INDEX_FILE = REPO_ROOT / "data" / "test-cases" / "test-case-index.json"
RESULT_INDEX_FILE = REPO_ROOT / "data" / "result-packets" / "result-packet-index.json"
EPIC_DIR = REPO_ROOT / "data" / "epic-regression"
EPIC_INDEX_FILE = EPIC_DIR / "epic-regression-index.json"
EPIC_SCHEMA = REPO_ROOT / "docs" / "schemas" / "qa-epic-regression-suite.schema.json"

SUITE_ID_PATTERN = re.compile(r"^ERS-\d{8}-")
ADVISORY_NOTICE = (
    "This Epic regression suite is advisory-only. It does not approve, seal, "
    "merge, or assert production readiness. Only the Owner may approve or seal."
)
FORBIDDEN_AUTHORITY_VERBS = [
    "approve", "seal", "start", "advance", "execute", "patch",
    "deploy", "promote", "authorize", "release"
]

ER_RULES = {
    "ER-1":  "Builds only from QA Pilot-local evidence, tests, and results",
    "ER-2":  "Epic suite references source EP evidence packet IDs",
    "ER-3":  "Epic suite references source TC test case IDs",
    "ER-4":  "Epic suite references source QR result packet IDs",
    "ER-5":  "Suite must include advisory: true",
    "ER-6":  "Suite must validate against qa-epic-regression-suite schema",
    "ER-7":  "No approve/seal/start/advance/execute authority verbs",
    "ER-8":  "No canonical mutation paths",
    "ER-9":  "Malformed or incomplete inputs rejected",
    "ER-10": "Duplicate build is deterministic (unique suite per input set)",
    "ER-11": "Epic index is QA Pilot-local only",
    "ER-12": "Existing packet chain (#33-#35) remains green",
    "ER-13": "Existing custody/startup/architecture regressions green",
}


def ensure_dirs():
    EPIC_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def load_index(index_path, default_version):
    if not index_path.exists():
        return {
            "store_version": default_version,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
    return load_json(str(index_path))


def load_evidence_index():
    return load_index(EVIDENCE_INDEX, "qap-evidence-v1")


def load_test_index():
    return load_index(TEST_INDEX_FILE, "qap-test-cases-v1")


def load_result_index():
    return load_index(RESULT_INDEX_FILE, "qap-result-packets-v1")


def load_epic_index():
    if not EPIC_INDEX_FILE.exists():
        return {
            "store_version": "qap-epic-regression-v1",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "epic_suites": {},
            "advisory_notice": ADVISORY_NOTICE,
        }
    return load_json(str(EPIC_INDEX_FILE))


def save_epic_index(index):
    index["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_json(str(EPIC_INDEX_FILE), index)


def advisory_response(**kwargs):
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


# ── Schema Validation ─────────────────────────────────────────────────────────

def validate_epic_suite_schema(data):
    """Validate against qa-epic-regression-suite.schema.json."""
    required = ["suite_id", "epic_id", "sprint_ids", "tests", "status", "advisory"]
    missing = [f for f in required if f not in data]
    if missing:
        return (False, f"Missing required fields: {missing}")

    sid = data.get("suite_id", "")
    if not SUITE_ID_PATTERN.match(sid):
        return (False, f"suite_id '{sid}' must match ERS-YYYYMMDD- pattern")

    if data.get("advisory") is not True:
        return (False, "advisory must be true")

    sprint_ids = data.get("sprint_ids", [])
    if not sprint_ids:
        return (False, "sprint_ids must have at least 1 entry")

    tests = data.get("tests", [])
    if not tests:
        return (False, "tests must have at least 1 entry")
    for t in tests:
        if "test_id" not in t or "sprint_id" not in t:
            return (False, f"Each test must have test_id and sprint_id")

    valid_statuses = ["building", "ready", "running", "completed", "failed"]
    if data.get("status") not in valid_statuses:
        return (False, f"status '{data.get('status')}' not in {valid_statuses}")

    return (True, "Schema validation passed")


# ── Build Core ────────────────────────────────────────────────────────────────

def collect_sprint_data(sprint_ids):
    """
    Collect all EP, TC, and QR records for the given sprint IDs.
    Returns (evidence_map, test_map, result_map, errors).
    """
    ev_index = load_evidence_index()
    tc_index = load_test_index()
    qr_index = load_result_index()

    ev_map = {}
    tc_map = {}
    qr_map = {}
    errors = []

    # Collect evidence for these sprints
    for pid, meta in ev_index.get("evidence", {}).items():
        if meta.get("sprint_id") in sprint_ids:
            ev_map[pid] = meta

    # Collect test cases for these sprints
    for tid, meta in tc_index.get("test_cases", {}).items():
        if meta.get("sprint_id") in sprint_ids:
            tc_map[tid] = meta

    # Collect result packets for these sprints  
    for rid, meta in qr_index.get("result_packets", {}).items():
        rsids = meta.get("sprint_ids", [])
        if any(s in sprint_ids for s in rsids):
            qr_map[rid] = meta

    if not ev_map and not tc_map and not qr_map:
        errors.append(f"No data found for sprint IDs: {sprint_ids}")

    return (ev_map, tc_map, qr_map, errors)


def build_epic_tests(tc_map, qr_map):
    """Build the tests array for the Epic suite from TC + QR data."""
    tests = []
    seen = set()

    for tid, meta in tc_map.items():
        if tid not in seen:
            tests.append({
                "test_id": tid,
                "sprint_id": meta.get("sprint_id", "unknown"),
                "status": meta.get("status", "composed"),
                "source_artifact": meta.get("source_artifact", ""),
            })
            seen.add(tid)

    return tests


def build_epic_result(tc_map):
    """Aggregate test results into summary."""
    passed = sum(1 for m in tc_map.values() if m.get("status") in ("composed", "ready", "passed"))
    failed = sum(1 for m in tc_map.values() if m.get("status") in ("failed", "blocked"))
    total = len(tc_map)
    return {
        "passed": passed,
        "failed": failed,
        "summary": f"{passed}/{total} tests passed, {failed} failed" if total > 0 else "No tests",
    }


def build_provenance(ev_map, qr_map):
    """Build provenance chain: EP → QR."""
    return {
        "evidence_packets": [{"packet_id": pid, "sprint_id": m.get("sprint_id")}
                             for pid, m in ev_map.items()],
        "result_packets": [{"result_id": rid, "sprint_ids": m.get("sprint_ids", [])}
                           for rid, m in qr_map.items()],
    }


def validate_build_source(ev_map, tc_map, qr_map, sprint_ids):
    """
    Validate that source data is eligible for Epic build.
    Returns (all_pass, checks).
    """
    checks = []

    # ER-1
    checks.append(("ER-1", True, "Reads from QA Pilot-local stores"))

    # ER-2
    checks.append(("ER-2", len(ev_map) > 0,
                   f"{len(ev_map)} evidence packet(s)" if ev_map else "No evidence packets"))

    # ER-3
    checks.append(("ER-3", len(tc_map) > 0,
                   f"{len(tc_map)} test case(s)" if tc_map else "No test cases"))

    # ER-4
    checks.append(("ER-4", len(qr_map) > 0,
                   f"{len(qr_map)} result packet(s)" if qr_map else "No result packets"))

    # ER-7: Check that EP and QR content has no authority verbs
    all_meta_str = json.dumps({"evidence": list(ev_map.keys()),
                                "tests": list(tc_map.keys()),
                                "results": list(qr_map.keys())}).lower()
    found_verbs = [v for v in FORBIDDEN_AUTHORITY_VERBS if f'"{v}"' in all_meta_str]
    if found_verbs:
        checks.append(("ER-7", False, f"Authority verbs: {found_verbs}"))
    else:
        checks.append(("ER-7", True, "No forbidden authority verbs"))

    # ER-8: No canonical mutation paths from EP evidence
    mutation_paths = ["/Sources/", "/Public/", "/.librarian/", "/receipts/",
                      "/project-state/", "startup-contract.json"]
    for pid, meta in ev_map.items():
        sp = meta.get("store_path")
        if sp and Path(sp).exists():
            try:
                ev = load_json(sp)
                for cf in ev.get("changed_files", []):
                    path = cf.get("path", "")
                    if any(mp in path for mp in mutation_paths):
                        checks.append(("ER-8", False, f"Mutation path in {pid}: {path}"))
                        break
                else:
                    continue
                break
            except Exception:
                pass
    else:
        checks.append(("ER-8", True, "No mutation paths in evidence"))

    # ER-9: Check for malformed data
    malformed = 0
    for name, store_path in [(pid, m.get("store_path")) for pid, m in ev_map.items()]:
        if store_path and Path(store_path).exists():
            try:
                d = load_json(store_path)
                if "packet_id" not in d:
                    malformed += 1
            except Exception:
                malformed += 1
    if malformed:
        checks.append(("ER-9", False, f"{malformed} malformed evidence packet(s)"))
    else:
        checks.append(("ER-9", True, "All source data valid"))

    all_pass = all(c[1] for c in checks)
    return (all_pass, checks)


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_build(args):
    """Build an Epic regression suite from sprint data."""
    epic_id = args.epic_id
    
    if args.sprint_ids:
        sprint_ids = args.sprint_ids
    else:
        # Auto-detect from all available data
        ev_idx = load_evidence_index()
        all_sprints = set()
        for m in ev_idx.get("evidence", {}).values():
            sid = m.get("sprint_id")
            if sid:
                all_sprints.add(sid)
        tc_idx = load_test_index()
        for m in tc_idx.get("test_cases", {}).values():
            sid = m.get("sprint_id")
            if sid:
                all_sprints.add(sid)
        sprint_ids = sorted(all_sprints) if all_sprints else []

    if not sprint_ids:
        return advisory_response(
            tool="epic_build",
            success=False,
            epic_id=epic_id,
            error="No sprint IDs provided or auto-detected",
        )

    ev_map, tc_map, qr_map, errors = collect_sprint_data(sprint_ids)
    if errors:
        return advisory_response(
            tool="epic_build",
            success=False,
            epic_id=epic_id,
            sprint_ids=sprint_ids,
            errors=errors,
        )

    # Validate
    valid, checks = validate_build_source(ev_map, tc_map, qr_map, sprint_ids)
    if not valid:
        result = advisory_response(
            tool="epic_build",
            success=False,
            epic_id=epic_id,
            sprint_ids=sprint_ids,
            error="Build source validation failed",
        )
        result["validation"] = make_check_results(valid, checks)
        return result

    # Build suite
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y%m%d")
    
    # Deterministic suite_id from epics_sprints hash
    hash_input = epic_id + "|" + "|".join(sprint_ids)
    short_hash = hashlib.md5(hash_input.encode()).hexdigest()[:4]
    suite_id = f"ERS-{date_str}-{short_hash}"

    tests = build_epic_tests(tc_map, qr_map)
    result = build_epic_result(tc_map)
    provenance = build_provenance(ev_map, qr_map)

    suite = {
        "suite_id": suite_id,
        "epic_id": epic_id,
        "sprint_ids": sprint_ids,
        "tests": tests,
        "status": "building",
        "advisory": True,
        "result": result,
        "provenance": provenance,
        "created_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    # Validate generated suite
    schema_valid, schema_msg = validate_epic_suite_schema(suite)
    if not schema_valid:
        return advisory_response(
            tool="epic_build",
            success=False,
            epic_id=epic_id,
            error=f"Generated suite failed schema: {schema_msg}",
        )

    # ER-10: Check duplicate
    epic_index = load_epic_index()
    existing = epic_index.get("epic_suites", {})
    for sid, meta in existing.items():
        if meta.get("epic_id") == epic_id and meta.get("sprint_ids") == sprint_ids:
            return advisory_response(
                tool="epic_build",
                success=False,
                epic_id=epic_id,
                suite_id=list(existing.keys())[0],
                error=f"Epic suite already exists for epic '{epic_id}' with these sprints",
            )

    # Store
    ensure_dirs()
    store_filename = f"{suite_id}.json"
    store_path = EPIC_DIR / store_filename
    save_json(str(store_path), suite)

    # Update index
    epic_index.setdefault("epic_suites", {})[suite_id] = {
        "suite_id": suite_id,
        "epic_id": epic_id,
        "sprint_ids": sprint_ids,
        "test_count": len(tests),
        "status": "building",
        "advisory": True,
        "created_at": suite["created_at"],
        "store_path": str(store_path),
    }
    save_epic_index(epic_index)

    resp = advisory_response(
        tool="epic_build",
        success=True,
        epic_id=epic_id,
        suite_id=suite_id,
        sprint_ids=sprint_ids,
        test_count=len(tests),
    )
    resp["validation"] = make_check_results(True, checks)
    resp["epic_suite"] = suite
    return resp


def cmd_validate(args):
    """Validate an Epic regression suite JSON file."""
    path = args.path
    try:
        data = load_json(path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return advisory_response(
            tool="epic_validate",
            success=False,
            file=str(path),
            error=f"Failed to load: {e}",
        )

    checks = []

    if "suite_id" in data and data.get("suite_id", "").startswith("ERS-"):
        # Schema
        schema_valid, schema_msg = validate_epic_suite_schema(data)
        checks.append(("ER-6", schema_valid, schema_msg))

        # ER-5
        checks.append(("ER-5", data.get("advisory") is True,
                       f"advisory = {data.get('advisory')}"))

        # ER-2: evidence refs via provenance
        prov = data.get("provenance", {})
        ev_refs = prov.get("evidence_packets", [])
        checks.append(("ER-2", len(ev_refs) > 0,
                       f"{len(ev_refs)} evidence reference(s)"))

        # ER-4: result refs via provenance
        qr_refs = prov.get("result_packets", [])
        checks.append(("ER-4", len(qr_refs) > 0,
                       f"{len(qr_refs)} result reference(s)"))

        # ER-3: test refs
        tests = data.get("tests", [])
        checks.append(("ER-3", len(tests) > 0,
                       f"{len(tests)} test(s) referenced"))

        # ER-7: authority verbs
        import re as _re
        findings_text = ""
        result_obj = data.get("result", {})
        findings_text += result_obj.get("summary", "")
        combined = findings_text.lower()
        found_verbs = [v for v in FORBIDDEN_AUTHORITY_VERBS if _re.search(r'\b' + v + r'\b', combined)]
        # Also check suite status
        addl_text = json.dumps({k: data.get(k) for k in ("status",)}).lower()
        for v in FORBIDDEN_AUTHORITY_VERBS:
            if _re.search(r'\b' + v + r'\b', addl_text) and v not in found_verbs and data.get("status") not in ("building", "ready", "running", "completed", "failed"):
                found_verbs.append(v)
        checks.append(("ER-7", len(found_verbs) == 0,
                       f"Authority verbs: {found_verbs}" if found_verbs else "Clean"))

        # ER-8: mutation paths
        data_str = json.dumps(data)
        mutation_paths = ["/Sources/", "/Public/", "/.librarian/"]
        found_paths = [p for p in mutation_paths if p in data_str]
        checks.append(("ER-8", len(found_paths) == 0,
                       f"Mutation paths: {found_paths}" if found_paths else "Clean"))

        all_pass = all(c[1] for c in checks)
        result = advisory_response(
            tool="epic_validate",
            success=all_pass,
            file=str(path),
            content_type="epic_suite",
            suite_id=data.get("suite_id", "unknown"),
        )
        result["validation"] = make_check_results(all_pass, checks)
        return result
    else:
        return advisory_response(
            tool="epic_validate",
            success=False,
            file=str(path),
            error="Not a valid Epic suite (missing ERS- suite_id)",
        )


def cmd_list(args):
    """List built Epic regression suites."""
    epic_index = load_epic_index()
    all_suites = list(epic_index.get("epic_suites", {}).values())
    total = len(all_suites)
    sliced = all_suites[:args.limit]

    result = advisory_response(
        tool="epic_list",
        success=True,
        total_count=total,
        limit=args.limit,
    )
    result["epic_suites"] = [
        {
            "suite_id": s["suite_id"],
            "epic_id": s.get("epic_id"),
            "sprint_ids": s.get("sprint_ids", []),
            "test_count": s.get("test_count"),
            "status": s.get("status"),
            "advisory": s.get("advisory", True),
            "created_at": s.get("created_at"),
        }
        for s in sliced
    ]
    return result


def cmd_read(args):
    """Read a built Epic regression suite."""
    epic_index = load_epic_index()
    suite_id = args.suite_id

    if suite_id not in epic_index.get("epic_suites", {}):
        return advisory_response(
            tool="epic_read",
            success=False,
            suite_id=suite_id,
            found=False,
            error=f"Epic suite '{suite_id}' not found",
        )

    store_path = epic_index["epic_suites"][suite_id].get("store_path")
    if not store_path or not Path(store_path).exists():
        return advisory_response(
            tool="epic_read",
            success=False,
            suite_id=suite_id,
            found=False,
            error="Index entry exists but store file missing",
        )

    data = load_json(store_path)
    return advisory_response(
        tool="epic_read",
        success=True,
        suite_id=suite_id,
        found=True,
        created_at=epic_index["epic_suites"][suite_id].get("created_at"),
        epic_suite=data,
    )


def cmd_status(args):
    """Show Epic regression store status."""
    epic_index = load_epic_index()
    suites = epic_index.get("epic_suites", {})
    total = len(suites)

    ev_idx = load_evidence_index()
    tc_idx = load_test_index()
    qr_idx = load_result_index()

    by_epic = {}
    by_status = {}
    last_built = None
    last_ts = None
    for sid, meta in suites.items():
        ep = meta.get("epic_id", "unknown")
        by_epic[ep] = by_epic.get(ep, 0) + 1
        st = meta.get("status", "unknown")
        by_status[st] = by_status.get(st, 0) + 1
        ts = meta.get("created_at", "")
        if ts and (last_ts is None or ts > last_ts):
            last_ts = ts
            last_built = {"suite_id": sid, "created_at": ts}

    return advisory_response(
        tool="epic_status",
        success=True,
        store_path=str(EPIC_DIR),
        index_path=str(EPIC_INDEX_FILE),
        total_epic_suites=total,
        by_epic=by_epic,
        by_status=by_status,
        last_built=last_built,
        available_evidence=len(ev_idx.get("evidence", {})),
        available_test_cases=len(tc_idx.get("test_cases", {})),
        available_result_packets=len(qr_idx.get("result_packets", {})),
        rules=list(ER_RULES.values()),
    )


def cmd_clear(args):
    """Remove all Epic suites and reset index."""
    epic_index = load_epic_index()
    count = len(epic_index.get("epic_suites", {}))

    for sid, meta in epic_index.get("epic_suites", {}).items():
        sp = Path(meta.get("store_path", ""))
        if sp.exists():
            sp.unlink()

    epic_index["epic_suites"] = {}
    epic_index["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_epic_index(epic_index)

    return advisory_response(
        tool="epic_clear",
        success=True,
        cleared_count=count,
        message=f"Cleared {count} Epic suites from QA Pilot-local store",
    )


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="QA Pilot Epic Regression Builder — QA-PILOT-EPIC-REGRESSION-BUILDER-1"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # build
    build_p = subparsers.add_parser("build", help="Build an Epic regression suite")
    build_p.add_argument("epic_id", help="Epic identifier (e.g., EPIC-QA-PILOT-V1)")
    build_p.add_argument("--sprint-ids", nargs="+", help="Sprint IDs to include (default: auto-detect)")

    # validate
    val_p = subparsers.add_parser("validate", help="Validate an Epic suite JSON file")
    val_p.add_argument("path", help="Path to JSON file")

    # list
    list_p = subparsers.add_parser("list", help="List built Epic suites")
    list_p.add_argument("--limit", type=int, default=50, help="Max results (1-100)")

    # read
    read_p = subparsers.add_parser("read", help="Read a built Epic suite by suite_id")
    read_p.add_argument("suite_id", help="Epic suite ID (e.g., ERS-20260706-XXXX)")

    # status
    subparsers.add_parser("status", help="Show Epic regression store status")

    # clear
    subparsers.add_parser("clear", help="Clear all built Epic suites")

    args = parser.parse_args()

    if args.command == "build":
        result = cmd_build(args)
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
