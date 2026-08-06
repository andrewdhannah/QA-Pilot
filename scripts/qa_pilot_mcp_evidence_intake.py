#!/usr/bin/env python3
"""
QA Pilot MCP Evidence Intake — QA-PILOT-MCP-EVIDENCE-INTAKE-1

QA Pilot-local standalone MCP evidence-intake surface for bounded evidence packets.
Implements four MCP tools: qa_evidence_ingest, qa_evidence_validate,
qa_evidence_list, qa_evidence_read.

Authority: advisory-only. All responses include advisory-only posture.
No source-project mutation is possible through these tools.
All stored records are QA Pilot-local only.

Usage:
    python3 scripts/qa_pilot_mcp_evidence_intake.py ingest <path>
    python3 scripts/qa_pilot_mcp_evidence_intake.py validate <path>
    python3 scripts/qa_pilot_mcp_evidence_intake.py list [--limit N] [--project X]
    python3 scripts/qa_pilot_mcp_evidence_intake.py read <packet_id>
    python3 scripts/qa_pilot_mcp_evidence_intake.py status
    python3 scripts/qa_pilot_mcp_evidence_intake.py clear
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
EVIDENCE_DIR = REPO_ROOT / "data" / "evidence"
INDEX_FILE = EVIDENCE_DIR / "evidence-index.json"
SCHEMA_PATH = REPO_ROOT / "docs" / "schemas" / "qa-evidence-packet.schema.json"

PACKET_ID_PATTERN = re.compile(r"^EP-\d{8}-")
KNOWN_PROJECTS = ["librarian", "qa-pilot"]

ADVISORY_NOTICE = (
    "This response is advisory-only. It does not approve, seal, merge, "
    "or assert production readiness. Only the Owner may approve or seal work."
)

# ── Evidence Rules (EM-1 through EM-12) ──────────────────────────────────────

EVIDENCE_RULES = {
    "EM-1": "Evidence packets must conform to qa-evidence-packet.schema.json",
    "EM-2": "Ingested evidence is advisory-only — no approval/seal authority",
    "EM-3": "No source-project file mutation through evidence intake",
    "EM-4": "Duplicate packet_ids are rejected",
    "EM-5": "Cross-project evidence requires explicit _source_project_metadata",
    "EM-6": "Timestamps in the future are rejected (stale detection)",
    "EM-7": "boundary_assertions must have librarian_impact field",
    "EM-8": "Evidence packet hash must be present",
    "EM-9": "List/read operations are read-only — must not mutate store",
    "EM-10": "All responses include advisory-only posture",
    "EM-11": "Responses identify source project and QA Pilot-local custody",
    "EM-12": "Evidence cannot authorize Librarian mutation",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def ensure_dirs():
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def load_index():
    if not INDEX_FILE.exists():
        return {
            "store_version": "qap-evidence-v1",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "evidence": {},
            "advisory_notice": ADVISORY_NOTICE,
        }
    return load_json(str(INDEX_FILE))


def save_index(index):
    index["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_json(str(INDEX_FILE), index)


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


# ── Core Validation ───────────────────────────────────────────────────────────

def validate_evidence_packet(data):
    """
    Validate an evidence packet against all EM rules.
    Returns (all_pass, checks_list).
    """
    checks = []

    # EM-1: Schema conformance (basic structural check)
    schema_valid = True
    schema_required = [
        "packet_id", "project", "sprint_id", "source_ledger",
        "changed_files", "validation_output", "receipt_references",
        "boundary_assertions", "provenance", "hash"
    ]
    missing = [f for f in schema_required if f not in data]
    if missing:
        schema_valid = False
        checks.append(("EM-1", False, f"Missing schema-required fields: {missing}"))
    else:
        checks.append(("EM-1", True, "All schema-required fields present"))

    # EM-7: boundary_assertions must have librarian_impact
    ba = data.get("boundary_assertions", {})
    if "librarian_impact" in ba:
        li = ba["librarian_impact"]
        valid_impacts = ["none", "read_only", "advisory"]
        if li in valid_impacts:
            checks.append(("EM-7", True, f"boundary_assertions.librarian_impact = '{li}'"))
        else:
            checks.append(("EM-7", False, f"Invalid librarian_impact '{li}', must be one of {valid_impacts}"))
    else:
        checks.append(("EM-7", False, "boundary_assertions missing librarian_impact"))

    # EM-2: Advisory-only (no authority claims)
    auth_claims = ["seal", "approve", "authoritative", "production_ready"]
    found_claims = []
    for claim in auth_claims:
        if data.get("_authority_claim") == claim:
            found_claims.append(claim)
        if claim in str(data.get("_authority_claim", "")):
            found_claims.append(claim)
    # Also check top-level fields for authority stance
    if found_claims:
        checks.append(("EM-2", False, f"Evidence contains authority claim: {found_claims}"))
    else:
        checks.append(("EM-2", True, "No authority claims in evidence packet"))

    # EM-3: No source-project mutation (for cross-project librarian evidence)
    if data.get("project") == "librarian":
        for cf in data.get("changed_files", []):
            path = cf.get("path", "")
            # Any path that tries to mutate Librarian source
            if any(p in path for p in ["/Sources/", "/Public/", "/receipts/",
                                         "/project-state/", "/.librarian/",
                                         "startup-contract.json"]):
                checks.append(("EM-3", False, f"Evidence references Librarian mutation path: {path}"))
                break
        else:
            checks.append(("EM-3", True, "No Librarian mutation paths referenced"))
    else:
        checks.append(("EM-3", True, "Project is qa-pilot — no cross-project check needed"))

    # EM-5: Cross-project evidence requires _source_project_metadata
    if data.get("project") != "qa-pilot":
        spm = data.get("_source_project_metadata", {})
        if spm and spm.get("source_project_id"):
            checks.append(("EM-5", True,
                          f"Cross-project metadata present: source_project_id='{spm['source_project_id']}'"))
        else:
            checks.append(("EM-5", False, "Cross-project evidence missing _source_project_metadata"))
    else:
        checks.append(("EM-5", True, "QA Pilot-local evidence — no cross-project check needed"))

    # EM-6: Stale/future timestamp detection
    ts = data.get("provenance", {}).get("timestamp", "")
    ts_ok = False
    if ts:
        try:
            packet_time = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            if packet_time <= now + timedelta(seconds=5):
                ts_ok = True
                checks.append(("EM-6", True, f"Timestamp '{ts}' is valid"))
            else:
                checks.append(("EM-6", False, f"Timestamp '{ts}' is in the future (stale)"))
        except ValueError:
            checks.append(("EM-6", False, f"Timestamp '{ts}' is not valid ISO 8601"))
    else:
        checks.append(("EM-6", False, "Missing provenance.timestamp"))

    # EM-8: Hash must be present
    h = data.get("hash", "")
    if h and len(h) >= 16:
        checks.append(("EM-8", True, f"Hash present ({len(h)} chars)"))
    else:
        checks.append(("EM-8", False, "Hash missing or too short"))

    # EM-12: No Librarian mutation authority
    # Check for any claim that this evidence authorizes Librarian changes
    if "_authority_claim" in data:
        checks.append(("EM-12", False, f"Evidence contains _authority_claim field"))
    else:
        checks.append(("EM-12", True, "No Librarian mutation authority claimed"))

    # EM-4: Duplicate check is done at ingest time (not in validate), but
    # we check packet_id format
    pid = data.get("packet_id", "")
    if PACKET_ID_PATTERN.match(pid):
        checks.append(("EM-4", True, f"packet_id '{pid}' has valid format"))
    else:
        checks.append(("EM-4", False, f"packet_id '{pid}' has invalid format"))

    all_pass = all(c[1] for c in checks)
    return (all_pass, checks)


# ── MCP Tool Implementations ──────────────────────────────────────────────────

def tool_validate(packet_path):
    """
    qa_evidence_validate — Validate an evidence packet without storing.
    Returns validation results with all EM rule checks.
    """
    try:
        data = load_json(packet_path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return advisory_response(
            tool="qa_evidence_validate",
            success=False,
            packet_path=str(packet_path),
            error=f"Failed to load packet: {e}",
        )

    all_pass, checks = validate_evidence_packet(data)

    result = advisory_response(
        tool="qa_evidence_validate",
        success=all_pass,
        packet_path=str(packet_path),
        packet_id=data.get("packet_id", "unknown"),
        project=data.get("project", "unknown"),
    )
    result["validation"] = make_check_results(all_pass, checks)
    return result


def tool_ingest(packet_path):
    """
    qa_evidence_ingest — Validate and store an evidence packet.
    Rejects: invalid packets, duplicate packet_ids, stale timestamps,
    cross-project without metadata, forbidden mutation claims.
    """
    try:
        data = load_json(packet_path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return advisory_response(
            tool="qa_evidence_ingest",
            success=False,
            packet_path=str(packet_path),
            error=f"Failed to load packet: {e}",
        )

    # Validate
    all_pass, checks = validate_evidence_packet(data)
    if not all_pass:
        result = advisory_response(
            tool="qa_evidence_ingest",
            success=False,
            packet_path=str(packet_path),
            packet_id=data.get("packet_id", "unknown"),
            error="Evidence packet failed validation — not ingested",
        )
        result["validation"] = make_check_results(all_pass, checks)
        return result

    # EM-4: Duplicate check
    packet_id = data["packet_id"]
    index = load_index()
    if packet_id in index.get("evidence", {}):
        return advisory_response(
            tool="qa_evidence_ingest",
            success=False,
            packet_path=str(packet_path),
            packet_id=packet_id,
            error=f"Duplicate packet_id '{packet_id}' — already ingested",
        )

    # Generate unique storage ID
    short_hash = data.get("hash", "unknown")[:12]
    store_filename = f"{packet_id}-{short_hash}.json"
    store_path = EVIDENCE_DIR / store_filename

    # Persist
    ensure_dirs()
    save_json(str(store_path), data)

    # Update index
    index.setdefault("evidence", {})[packet_id] = {
        "packet_id": packet_id,
        "project": data.get("project"),
        "sprint_id": data.get("sprint_id"),
        "source_ledger": data.get("source_ledger"),
        "hash": data.get("hash"),
        "stored_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "store_path": str(store_path),
        "advisory": True,
        "cross_project_write_authorized": False,
    }
    save_index(index)

    result = advisory_response(
        tool="qa_evidence_ingest",
        success=True,
        packet_path=str(packet_path),
        packet_id=packet_id,
        stored_path=str(store_path),
        stored_at=index["evidence"][packet_id]["stored_at"],
    )
    result["validation"] = make_check_results(True, checks)
    result["advisory_only"] = True
    return result


def tool_list(limit=50, project=None):
    """
    qa_evidence_list — List ingested evidence packets with optional project filter.
    Bounded (1-100). Read-only. Advisory-only posture.
    """
    # Validate limit
    if not isinstance(limit, int) or limit < 1 or limit > 100:
        return advisory_response(
            tool="qa_evidence_list",
            success=False,
            limit=limit,
            error=f"limit must be an integer between 1 and 100, got {limit}",
        )

    index = load_index()
    all_evidence = list(index.get("evidence", {}).values())

    # Apply project filter
    if project:
        filtered = [e for e in all_evidence if e.get("project") == project]
    else:
        filtered = all_evidence

    total = len(filtered)
    sliced = filtered[:limit]

    result = advisory_response(
        tool="qa_evidence_list",
        success=True,
        total_count=total,
        limit=limit,
        evidence_count=len(sliced),
    )
    result["evidence"] = [
        {
            "packet_id": e["packet_id"],
            "project": e.get("project"),
            "sprint_id": e.get("sprint_id"),
            "stored_at": e.get("stored_at"),
            "advisory": e.get("advisory", True),
        }
        for e in sliced
    ]
    return result


def tool_read(packet_id):
    """
    qa_evidence_read — Read a stored evidence packet by packet_id.
    Read-only. Advisory-only posture.
    """
    index = load_index()
    if packet_id not in index.get("evidence", {}):
        return advisory_response(
            tool="qa_evidence_read",
            success=False,
            packet_id=packet_id,
            found=False,
            error=f"Evidence packet '{packet_id}' not found",
        )

    store_path = index["evidence"][packet_id].get("store_path")
    if not store_path or not Path(store_path).exists():
        return advisory_response(
            tool="qa_evidence_read",
            success=False,
            packet_id=packet_id,
            found=False,
            error=f"Evidence packet '{packet_id}' index entry exists but store file missing",
        )

    data = load_json(store_path)
    return advisory_response(
        tool="qa_evidence_read",
        success=True,
        packet_id=packet_id,
        found=True,
        stored_at=index["evidence"][packet_id]["stored_at"],
        packet=data,
    )


def tool_status():
    """
    Status — Return store summary.
    Advisory-only. No authority.
    """
    index = load_index()
    evidence = index.get("evidence", {})
    total = len(evidence)

    by_project = {}
    for pid, meta in evidence.items():
        p = meta.get("project", "unknown")
        by_project[p] = by_project.get(p, 0) + 1

    last_stored = None
    last_ts = None
    for pid, meta in evidence.items():
        ts = meta.get("stored_at", "")
        if ts and (last_ts is None or ts > last_ts):
            last_ts = ts
            last_stored = {"packet_id": pid, "stored_at": ts}

    return advisory_response(
        tool="qa_evidence_status",
        success=True,
        store_path=str(EVIDENCE_DIR),
        index_path=str(INDEX_FILE),
        total_evidence=total,
        by_project=by_project,
        last_stored=last_stored,
        rules=list(EVIDENCE_RULES.values()),
    )


def tool_clear():
    """
    Clear — Remove all ingested evidence and reset index.
    """
    index = load_index()
    count = len(index.get("evidence", {}))

    for pid, meta in index.get("evidence", {}).items():
        store_path = Path(meta.get("store_path", ""))
        if store_path.exists():
            store_path.unlink()

    index["evidence"] = {}
    index["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_index(index)

    return advisory_response(
        tool="qa_evidence_clear",
        success=True,
        cleared_count=count,
        message=f"Cleared {count} evidence packets from QA Pilot-local store",
    )


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="QA Pilot MCP Evidence Intake — QA-PILOT-MCP-EVIDENCE-INTAKE-1"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ingest
    ingest_p = subparsers.add_parser("ingest", help="Validate and ingest an evidence packet")
    ingest_p.add_argument("packet_path", help="Path to evidence packet JSON file")

    # validate
    validate_p = subparsers.add_parser("validate", help="Validate an evidence packet without storing")
    validate_p.add_argument("packet_path", help="Path to evidence packet JSON file")

    # list
    list_p = subparsers.add_parser("list", help="List ingested evidence packets")
    list_p.add_argument("--limit", type=int, default=50, help="Max results (1-100)")
    list_p.add_argument("--project", help="Filter by project (librarian, qa-pilot)")

    # read
    read_p = subparsers.add_parser("read", help="Read a stored evidence packet by packet_id")
    read_p.add_argument("packet_id", help="Evidence packet ID (e.g., EP-20260706-001)")

    # status
    subparsers.add_parser("status", help="Show evidence store status")

    # clear
    subparsers.add_parser("clear", help="Clear all ingested evidence")

    args = parser.parse_args()

    if args.command == "ingest":
        result = tool_ingest(args.packet_path)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("success", False) else 1)

    elif args.command == "validate":
        result = tool_validate(args.packet_path)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("success", False) else 1)

    elif args.command == "list":
        result = tool_list(limit=args.limit, project=args.project)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("success", False) else 1)

    elif args.command == "read":
        result = tool_read(args.packet_id)
        print(json.dumps(result, indent=2))
        sys.exit(0)

    elif args.command == "status":
        result = tool_status()
        print(json.dumps(result, indent=2))
        sys.exit(0)

    elif args.command == "clear":
        result = tool_clear()
        print(json.dumps(result, indent=2))
        sys.exit(0)


if __name__ == "__main__":
    main()
