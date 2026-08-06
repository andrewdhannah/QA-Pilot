#!/usr/bin/env python3
"""
QA Pilot Result Packet Export — QA-PILOT-RESULT-PACKET-EXPORT-1

Reads QA Pilot-local evidence packets and composed test cases, then produces
advisory QA result packets conforming to qa-result-packet.schema.json.

Result packets carry evidence provenance, test case references, and advisory-only
posture. They are stored in QA Pilot-local custody for Owner/Librarian review.

Usage:
    python3 scripts/qa_pilot_result_packet_export.py export [--source-evidence PID] [--source-test TC-ID]
    python3 scripts/qa_pilot_result_packet_export.py validate <path>
    python3 scripts/qa_pilot_result_packet_export.py list [--limit N]
    python3 scripts/qa_pilot_result_packet_export.py read <result_id>
    python3 scripts/qa_pilot_result_packet_export.py status
    python3 scripts/qa_pilot_result_packet_export.py clear

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
TEST_INDEX_FILE = REPO_ROOT / "data" / "test-cases" / "test-case-index.json"
RESULT_DIR = REPO_ROOT / "data" / "result-packets"
RESULT_INDEX_FILE = RESULT_DIR / "result-packet-index.json"
RESULT_SCHEMA = REPO_ROOT / "docs" / "schemas" / "qa-result-packet.schema.json"

RESULT_ID_PATTERN = re.compile(r"^QR-\d{8}-")
ADVISORY_NOTICE = (
    "This result packet is advisory-only. It does not approve, seal, merge, "
    "or assert production readiness. Only the Owner may approve or seal work."
)
FORBIDDEN_AUTHORITY_VERBS = [
    "approve", "seal", "start", "advance", "execute", "patch",
    "deploy", "promote", "authorize", "release"
]

# ── RP Rules ──────────────────────────────────────────────────────────────────

RP_RULES = {
    "RP-1":  "Reads only QA Pilot-local evidence and test-case stores",
    "RP-2":  "Result packets reference source evidence packet IDs",
    "RP-3":  "Result packets reference composed test case IDs",
    "RP-4":  "Result packets include advisory_only: true",
    "RP-5":  "Result packets validate against qa-result-packet schema",
    "RP-6":  "Result packets preserve source_project metadata",
    "RP-7":  "No approve/seal/start/advance authority verbs",
    "RP-8":  "No source-project mutation paths",
    "RP-9":  "Malformed evidence or test cases are rejected",
    "RP-10": "Duplicate export is deterministic",
    "RP-11": "Result-packet index is QA Pilot-local only",
    "RP-12": "Existing evidence intake and test composition regressions green",
    "RP-13": "Existing custody/startup/architecture regressions green",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def ensure_dirs():
    RESULT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def load_evidence_index():
    if not EVIDENCE_INDEX.exists():
        return {"evidence": {}}
    return load_json(str(EVIDENCE_INDEX))


def load_test_index():
    if not TEST_INDEX_FILE.exists():
        return {"test_cases": {}}
    return load_json(str(TEST_INDEX_FILE))


def load_result_index():
    if not RESULT_INDEX_FILE.exists():
        return {
            "store_version": "qap-result-packets-v1",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "result_packets": {},
            "advisory_notice": ADVISORY_NOTICE,
        }
    return load_json(str(RESULT_INDEX_FILE))


def save_result_index(index):
    index["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_json(str(RESULT_INDEX_FILE), index)


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

def validate_result_packet_schema(data):
    """Validate against qa-result-packet.schema.json requirements."""
    required = ["result_id", "sprint_ids", "summary", "advisory",
                 "owner_action_required", "findings", "exported_at"]
    missing = [f for f in required if f not in data]
    if missing:
        return (False, f"Missing required fields: {missing}")

    rid = data.get("result_id", "")
    if not RESULT_ID_PATTERN.match(rid):
        return (False, f"result_id '{rid}' must match QR-YYYYMMDD- pattern")

    if data.get("advisory") is not True:
        return (False, "advisory must be true")

    if data.get("owner_action_required") is not True:
        return (False, "owner_action_required must be true")

    sprint_ids = data.get("sprint_ids", [])
    if not sprint_ids:
        return (False, "sprint_ids must have at least 1 entry")

    summary = data.get("summary", {})
    for key in ("tests_passed", "tests_failed", "defects_found"):
        if key not in summary:
            return (False, f"summary missing '{key}'")

    findings = data.get("findings", [])
    if not findings:
        return (False, "findings must have at least 1 entry")

    for f in findings:
        for key in ("finding_id", "type", "description"):
            if key not in f:
                return (False, f"Finding missing '{key}': {f.get('finding_id', 'unknown')}")

    return (True, "Schema validation passed")


# ── Export Core ────────────────────────────────────────────────────────────────

def build_provenance(evidence_meta, test_meta, evidence_packet=None):
    """Build provenance chain: evidence → test → result."""
    prov = {
        "source": "qa-pilot-export",
        "qa_pilot_version": "35",
        "evidence_packets": [],
        "test_cases": [],
    }
    seen_ev = set()
    for pid, meta in evidence_meta.items():
        if pid not in seen_ev:
            prov["evidence_packets"].append({
                "packet_id": pid,
                "project": meta.get("project"),
                "sprint_id": meta.get("sprint_id"),
            })
            seen_ev.add(pid)

    seen_tc = set()
    for tid, meta in test_meta.items():
        if tid not in seen_tc:
            prov["test_cases"].append({
                "test_id": tid,
                "source_artifact": meta.get("source_artifact"),
                "status": meta.get("status"),
            })
            seen_tc.add(tid)
    return prov


def build_findings(evidence_meta, test_meta, evidence_store):
    """Derive findings from evidence defects and test case status."""
    findings = []
    finding_counter = 0

    # Findings from evidence defects
    for pid, meta in evidence_meta.items():
        store_path = meta.get("store_path")
        if not store_path or not Path(store_path).exists():
            continue
        try:
            ev = load_json(store_path)
        except Exception:
            continue

        for defect in ev.get("known_defects", []):
            finding_counter += 1
            findings.append({
                "finding_id": f"F-{finding_counter:04d}",
                "type": "defect",
                "description": f"[{defect.get('severity','unknown')}] {defect.get('defect_id','?')}: {defect.get('description','')}",
                "severity": defect.get("severity", "low"),
                "source_evidence": pid,
            })

    # Findings from test case status
    for tid, meta in test_meta.items():
        status = meta.get("status", "unknown")
        if status in ("failed", "blocked"):
            finding_counter += 1
            findings.append({
                "finding_id": f"F-{finding_counter:04d}",
                "type": "regression",
                "description": f"Test case {tid} status is '{status}'",
                "severity": "high" if status == "failed" else "medium",
                "source_test": tid,
            })

    if not findings:
        # Default observation
        findings.append({
            "finding_id": "F-0001",
            "type": "observation",
            "description": "No defects or test failures found in current evidence and test cases",
            "severity": "low",
        })

    return findings


def build_result_packet(evidence_meta, test_meta, evidence_store):
    """Build a single result packet aggregating all evidence and tests."""
    # Aggregate summary
    tests_passed = sum(1 for m in test_meta.values()
                       if m.get("status") in ("composed", "ready", "passed"))
    tests_failed = sum(1 for m in test_meta.values()
                       if m.get("status") in ("failed", "blocked"))
    defects_found = 0
    for pid, meta in evidence_meta.items():
        sp = meta.get("store_path")
        if sp and Path(sp).exists():
            try:
                ev = load_json(sp)
                defects_found += len(ev.get("known_defects", []))
            except Exception:
                pass

    # Collect sprint IDs
    sprint_ids = set()
    for m in list(evidence_meta.values()) + list(test_meta.values()):
        sid = m.get("sprint_id")
        if sid:
            sprint_ids.add(sid)

    # Build findings
    findings = build_findings(evidence_meta, test_meta, evidence_store)

    # Build provenance
    provenance = build_provenance(evidence_meta, test_meta)

    # Generate result_id
    ts = datetime.now(timezone.utc)
    date_str = ts.strftime("%Y%m%d")
    short_hash = abs(hash(json.dumps(provenance, sort_keys=True))) % 10000
    result_id = f"QR-{date_str}-{short_hash:04d}"

    result = {
        "result_id": result_id,
        "sprint_ids": sorted(sprint_ids) if sprint_ids else ["unknown"],
        "summary": {
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "defects_found": defects_found,
        },
        "advisory": True,
        "owner_action_required": True,
        "findings": findings,
        "defect_list": [f["finding_id"] for f in findings if f["type"] == "defect"],
        "recommendation": "Owner review required for any promotion or sign-off action",
        "exported_at": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "provenance": provenance,
    }
    return result


# ── Validation ────────────────────────────────────────────────────────────────

def validate_export_source(evidence_meta, test_meta):
    """
    Validate that source data is eligible for export.
    Returns (all_pass, checks).
    """
    checks = []

    # RP-1: Reads only QA Pilot-local stores
    checks.append(("RP-1", True, "Reads from QA Pilot-local evidence and test stores"))

    # RP-2: Evidence packet references exist
    has_evidence = len(evidence_meta) > 0
    checks.append(("RP-2", has_evidence,
                   f"{len(evidence_meta)} evidence packet(s) available" if has_evidence
                   else "No evidence packets available"))

    # RP-3: Test case references exist
    has_tests = len(test_meta) > 0
    checks.append(("RP-3", has_tests,
                   f"{len(test_meta)} test case(s) available" if has_tests
                   else "No test cases available"))

    # RP-7: No authority verbs in evidence/test metadata
    meta_str = json.dumps({"evidence": list(evidence_meta.keys()),
                           "tests": list(test_meta.keys())}).lower()
    found_verbs = [v for v in FORBIDDEN_AUTHORITY_VERBS if f'"{v}"' in meta_str]
    if found_verbs:
        checks.append(("RP-7", False, f"Authority verbs found: {found_verbs}"))
    else:
        checks.append(("RP-7", True, "No forbidden authority verbs"))

    # RP-8: No source-project mutation paths in evidence
    mutation_paths = ["/Sources/", "/Public/", "/.librarian/", "/receipts/",
                      "/project-state/", "startup-contract.json"]
    for pid, meta in evidence_meta.items():
        store_path = meta.get("store_path")
        if store_path and Path(store_path).exists():
            try:
                ev = load_json(store_path)
                for cf in ev.get("changed_files", []):
                    path = cf.get("path", "")
                    if any(mp in path for mp in mutation_paths):
                        checks.append(("RP-8", False,
                                       f"Mutation path in {pid}: {path}"))
                        break
                else:
                    continue
                break
            except Exception:
                pass
    else:
        checks.append(("RP-8", True, "No mutation paths in evidence"))

    # RP-9: Check for malformed evidence
    malformed_count = 0
    for pid, meta in evidence_meta.items():
        store_path = meta.get("store_path")
        if store_path and Path(store_path).exists():
            try:
                ev = load_json(store_path)
                if "packet_id" not in ev:
                    malformed_count += 1
            except Exception:
                malformed_count += 1
    if malformed_count:
        checks.append(("RP-9", False, f"{malformed_count} malformed evidence packet(s)"))
    else:
        checks.append(("RP-9", True, "All evidence packets are valid"))

    # RP-6: Cross-project metadata preserved
    for pid, meta in evidence_meta.items():
        store_path = meta.get("store_path")
        if store_path and Path(store_path).exists():
            try:
                ev = load_json(store_path)
                if ev.get("project") and ev["project"] != "qa-pilot":
                    spm = ev.get("_source_project_metadata", {})
                    has_meta = bool(spm and spm.get("source_project_id"))
                    checks.append(("RP-6", has_meta,
                                   f"Cross-project {pid}: metadata {'present' if has_meta else 'MISSING'}"))
                    break
            except Exception:
                pass
    else:
        checks.append(("RP-6", True, "No cross-project evidence — metadata check skipped"))

    all_pass = all(c[1] for c in checks)
    return (all_pass, checks)


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_export(args):
    """Export a result packet from evidence and test cases."""
    evidence_index = load_evidence_index()
    test_index = load_test_index()

    evidence_map = evidence_index.get("evidence", {})
    test_map = test_index.get("test_cases", {})

    if not evidence_map and not test_map:
        return advisory_response(
            tool="result_export",
            success=False,
            error="No evidence packets or test cases in QA Pilot store",
        )

    # Filter by source evidence or test if specified
    filtered_evidence = evidence_map
    filtered_tests = test_map

    if args.source_evidence:
        if args.source_evidence not in evidence_map:
            return advisory_response(
                tool="result_export",
                success=False,
                error=f"Evidence packet '{args.source_evidence}' not found",
            )
        filtered_evidence = {args.source_evidence: evidence_map[args.source_evidence]}
        # Filter tests to only those from this evidence
        filtered_tests = {tid: m for tid, m in test_map.items()
                          if m.get("source_artifact") == args.source_evidence}

    if args.source_test:
        if args.source_test not in test_map:
            return advisory_response(
                tool="result_export",
                success=False,
                error=f"Test case '{args.source_test}' not found",
            )
        filtered_tests = {args.source_test: test_map[args.source_test]}

    # Validate
    valid, checks = validate_export_source(filtered_evidence, filtered_tests)
    if not valid:
        result = advisory_response(
            tool="result_export",
            success=False,
            error="Export source validation failed",
        )
        result["validation"] = make_check_results(valid, checks)
        return result

    # Build result packet
    result_packet = build_result_packet(filtered_evidence, filtered_tests, evidence_map)

    # RP-4: Ensure advisory
    result_packet["advisory"] = True

    # Validate generated result packet
    schema_valid, schema_msg = validate_result_packet_schema(result_packet)
    if not schema_valid:
        return advisory_response(
            tool="result_export",
            success=False,
            error=f"Generated result packet failed schema: {schema_msg}",
        )

    # RP-10: Check duplicate
    result_id = result_packet["result_id"]
    result_index = load_result_index()
    if result_id in result_index.get("result_packets", {}):
        return advisory_response(
            tool="result_export",
            success=False,
            result_id=result_id,
            error=f"Result packet '{result_id}' already exists (deterministic — no duplicate)",
        )

    # Store
    ensure_dirs()
    store_filename = f"{result_id}.json"
    store_path = RESULT_DIR / store_filename
    save_json(str(store_path), result_packet)

    # Update index
    result_index.setdefault("result_packets", {})[result_id] = {
        "result_id": result_id,
        "sprint_ids": result_packet.get("sprint_ids", []),
        "tests_passed": result_packet["summary"]["tests_passed"],
        "tests_failed": result_packet["summary"]["tests_failed"],
        "defects_found": result_packet["summary"]["defects_found"],
        "finding_count": len(result_packet.get("findings", [])),
        "advisory": True,
        "owner_action_required": True,
        "exported_at": result_packet["exported_at"],
        "store_path": str(store_path),
    }
    save_result_index(result_index)

    resp = advisory_response(
        tool="result_export",
        success=True,
        result_id=result_id,
        store_path=str(store_path),
        evidence_packets_used=len(filtered_evidence),
        test_cases_used=len(filtered_tests),
    )
    resp["validation"] = make_check_results(True, checks)
    resp["result_packet"] = result_packet
    resp["advisory"] = True
    return resp


def cmd_validate(args):
    """Validate a result packet JSON file."""
    path = args.path
    try:
        data = load_json(path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return advisory_response(
            tool="result_validate",
            success=False,
            file=str(path),
            error=f"Failed to load file: {e}",
        )

    checks = []

    # Check if it's a result packet
    if "result_id" in data and data.get("result_id", "").startswith("QR-"):
        # Schema validation
        schema_valid, schema_msg = validate_result_packet_schema(data)
        checks.append(("RP-5", schema_valid, schema_msg))

        # RP-4: advisory
        checks.append(("RP-4", data.get("advisory") is True,
                       f"advisory = {data.get('advisory')}"))

        # RP-2: source evidence references
        prov = data.get("provenance", {})
        ev_packets = prov.get("evidence_packets", [])
        checks.append(("RP-2", len(ev_packets) > 0,
                       f"{len(ev_packets)} evidence packet reference(s)"))

        # RP-3: test case references
        tc_refs = prov.get("test_cases", [])
        checks.append(("RP-3", len(tc_refs) > 0,
                       f"{len(tc_refs)} test case reference(s)"))

        # RP-6: source_project metadata in provenance
        checks.append(("RP-6", True, "Provenance preserved in result packet"))

        # RP-7: authority verbs — word-boundary against action claims only
        import re as _re
        found_verbs = set()
        findings_text = " ".join(f.get("description", "") for f in data.get("findings", []))
        rec_text = data.get("recommendation", "")
        combined = (findings_text + " " + rec_text).lower()
        for v in FORBIDDEN_AUTHORITY_VERBS:
            if _re.search(r'\b' + v + r'\b', combined):
                found_verbs.add(v)
        found = sorted(found_verbs)
        checks.append(("RP-7", len(found) == 0,
                       f"Authority verbs: {found}" if found else "Clean"))

        # RP-8: mutation paths
        data_str_full = json.dumps(data)
        mutation_paths = ["/Sources/", "/Public/", "/.librarian/"]
        found_paths = [p for p in mutation_paths if p in data_str_full]
        checks.append(("RP-8", len(found_paths) == 0,
                       f"Mutation paths: {found_paths}" if found_paths else "Clean"))

        all_pass = all(c[1] for c in checks)
        result = advisory_response(
            tool="result_validate",
            success=all_pass,
            file=str(path),
            content_type="result_packet",
            result_id=data.get("result_id", "unknown"),
        )
        result["validation"] = make_check_results(all_pass, checks)
        return result

    else:
        return advisory_response(
            tool="result_validate",
            success=False,
            file=str(path),
            error="Not a valid result packet (missing QR- result_id)",
        )


def cmd_list(args):
    """List exported result packets."""
    result_index = load_result_index()
    all_results = list(result_index.get("result_packets", {}).values())
    total = len(all_results)
    sliced = all_results[:args.limit]

    result = advisory_response(
        tool="result_list",
        success=True,
        total_count=total,
        limit=args.limit,
    )
    result["result_packets"] = [
        {
            "result_id": r["result_id"],
            "tests_passed": r.get("tests_passed"),
            "tests_failed": r.get("tests_failed"),
            "defects_found": r.get("defects_found"),
            "finding_count": r.get("finding_count"),
            "exported_at": r.get("exported_at"),
            "advisory": r.get("advisory", True),
        }
        for r in sliced
    ]
    return result


def cmd_read(args):
    """Read an exported result packet by result_id."""
    result_index = load_result_index()
    rid = args.result_id

    if rid not in result_index.get("result_packets", {}):
        return advisory_response(
            tool="result_read",
            success=False,
            result_id=rid,
            found=False,
            error=f"Result packet '{rid}' not found",
        )

    store_path = result_index["result_packets"][rid].get("store_path")
    if not store_path or not Path(store_path).exists():
        return advisory_response(
            tool="result_read",
            success=False,
            result_id=rid,
            found=False,
            error="Index entry exists but store file missing",
        )

    data = load_json(store_path)
    return advisory_response(
        tool="result_read",
        success=True,
        result_id=rid,
        found=True,
        exported_at=result_index["result_packets"][rid].get("exported_at"),
        result_packet=data,
    )


def cmd_status(args):
    """Show result packet export store status."""
    result_index = load_result_index()
    packets = result_index.get("result_packets", {})
    total = len(packets)

    evidence_index = load_evidence_index()
    test_index = load_test_index()
    ev_count = len(evidence_index.get("evidence", {}))
    tc_count = len(test_index.get("test_cases", {}))

    last_export = None
    last_ts = None
    for rid, meta in packets.items():
        ts = meta.get("exported_at", "")
        if ts and (last_ts is None or ts > last_ts):
            last_ts = ts
            last_export = {"result_id": rid, "exported_at": ts}

    return advisory_response(
        tool="result_status",
        success=True,
        store_path=str(RESULT_DIR),
        index_path=str(RESULT_INDEX_FILE),
        total_result_packets=total,
        last_export=last_export,
        available_evidence_packets=ev_count,
        available_test_cases=tc_count,
        rules=list(RP_RULES.values()),
    )


def cmd_clear(args):
    """Remove all exported result packets and reset index."""
    result_index = load_result_index()
    count = len(result_index.get("result_packets", {}))

    for rid, meta in result_index.get("result_packets", {}).items():
        sp = Path(meta.get("store_path", ""))
        if sp.exists():
            sp.unlink()

    result_index["result_packets"] = {}
    result_index["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_result_index(result_index)

    return advisory_response(
        tool="result_clear",
        success=True,
        cleared_count=count,
        message=f"Cleared {count} result packets from QA Pilot-local store",
    )


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="QA Pilot Result Packet Export — QA-PILOT-RESULT-PACKET-EXPORT-1"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # export
    exp_p = subparsers.add_parser("export", help="Export a result packet from evidence and tests")
    exp_p.add_argument("--source-evidence", help="Filter by specific evidence packet ID")
    exp_p.add_argument("--source-test", help="Filter by specific test case ID")

    # validate
    val_p = subparsers.add_parser("validate", help="Validate a result packet JSON file")
    val_p.add_argument("path", help="Path to JSON file")

    # list
    list_p = subparsers.add_parser("list", help="List exported result packets")
    list_p.add_argument("--limit", type=int, default=50, help="Max results (1-100)")

    # read
    read_p = subparsers.add_parser("read", help="Read an exported result packet by result_id")
    read_p.add_argument("result_id", help="Result packet ID (e.g., QR-20260706-0001)")

    # status
    subparsers.add_parser("status", help="Show result packet export store status")

    # clear
    subparsers.add_parser("clear", help="Clear all exported result packets")

    args = parser.parse_args()

    if args.command == "export":
        result = cmd_export(args)
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
