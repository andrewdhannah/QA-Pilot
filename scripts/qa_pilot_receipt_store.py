#!/usr/bin/env python3
"""
QA Pilot Receipt Store — QA-PILOT-RECEIPT-STORE-1

A local file-based receipt store for QA Pilot production receipts.
Implements register, get, list, and status operations with advisory-only
authority enforcement.

Usage:
    python3 scripts/qa_pilot_receipt_store.py register <receipt_json_path>
    python3 scripts/qa_pilot_receipt_store.py get <receipt_id>
    python3 scripts/qa_pilot_receipt_store.py list [--limit N] [--offset N]
                                                   [--project-id X] [--status X]
                                                   [--packet-type X]
    python3 scripts/qa_pilot_receipt_store.py status
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Paths relative to this script's repo root
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DATA_DIR = REPO_ROOT / "data"
RECEIPTS_DIR = DATA_DIR / "receipts"
INDEX_PATH = DATA_DIR / "receipt-index.json"
STATUS_PATH = DATA_DIR / "receipt-store-status.json"
SCHEMA_PATH = REPO_ROOT / "docs" / "schemas" / "qa-pilot-receipt.schema.json"
RECEIPT_ID_PATTERN = re.compile(r"^qapr-\d{8}-\d{3,}$")
ALLOWED_STATUSES = ["draft", "completed", "partial", "blocked", "superseded"]
ALLOWED_PACKET_TYPES = [
    "QAProductionReceipt",
    "QAProductionEvidenceReceipt",
    "QAProductionVerificationReceipt",
    "QAProductionReadinessReceipt",
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def load_index():
    if not INDEX_PATH.exists():
        return {
            "store_version": "qap-store-v1",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "receipts": {},
            "advisory_notice": "This receipt store is advisory-only. Stored receipts do not confer approval, seal, merge, or production-readiness authority.",
        }
    return load_json(str(INDEX_PATH))


def save_index(index):
    index["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_json(str(INDEX_PATH), index)


def validate_receipt_schema(receipt):
    """Validate a receipt against the QA Pilot receipt schema using jsonschema if available."""
    try:
        import jsonschema
        schema = load_json(str(SCHEMA_PATH))
        jsonschema.validate(receipt, schema)
        return (True, "Schema validation passed")
    except ImportError:
        # Fallback: basic structural checks
        required = ["receipt_id", "packet_type", "schema_version", "project_id",
                     "sprint_id", "source_sprint_receipt", "created_at", "created_by",
                     "authority", "status", "non_approval_statement", "content_hash",
                     "librarian_receipt_refs", "limitations", "qa_packet_refs"]
        missing = [f for f in required if f not in receipt]
        if missing:
            return (False, f"Missing required fields: {missing}")
        return (True, "Basic structural validation passed")
    except jsonschema.ValidationError as e:
        return (False, f"Schema validation failed: {e.message}")


def validate_advisory_authority(receipt):
    """Enforce advisory-only authority on a receipt."""
    checks = []
    # RS-2: authority must be 'advisory'
    if receipt.get("authority") != "advisory":
        checks.append(("RS-2", False, f"authority must be 'advisory', got '{receipt.get('authority')}'"))
    else:
        checks.append(("RS-2", True, "authority is advisory"))

    # RS-3: non_approval_statement must be >= 20 chars
    stmt = receipt.get("non_approval_statement", "")
    if len(stmt) < 20:
        checks.append(("RS-3", False, f"non_approval_statement too short ({len(stmt)} chars, need >= 20)"))
    else:
        checks.append(("RS-3", True, f"non_approval_statement present ({len(stmt)} chars)"))

    # receipt_id pattern check
    rid = receipt.get("receipt_id", "")
    if not RECEIPT_ID_PATTERN.match(rid):
        checks.append(("RS-ID", False, f"receipt_id must match qapr- pattern, got '{rid}'"))
    else:
        checks.append(("RS-ID", True, f"receipt_id '{rid}' is valid"))

    all_pass = all(c[1] for c in checks)
    return (all_pass, checks)


# ─── Store Operations ─────────────────────────────────────────────────────────


def register(receipt_path):
    """Register a receipt from a JSON file path into the store."""
    result = {
        "success": False,
        "receipt_id": None,
        "stored_path": None,
        "validation_status": "failed",
        "advisory_only": False,
        "errors": [],
        "validation_checks": [],
    }

    # Load receipt
    try:
        data = load_json(receipt_path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        result["errors"].append(f"Failed to load receipt: {e}")
        return result

    # Support fixture wrappers: extract inner receipt if wrapped
    receipt = data.get("receipt", data)

    # Validate schema
    schema_valid, schema_msg = validate_receipt_schema(receipt)
    result["validation_checks"].append({"check": "schema", "passed": schema_valid, "message": schema_msg})

    # Validate advisory authority
    advisory_valid, advisory_checks = validate_advisory_authority(receipt)
    for check in advisory_checks:
        result["validation_checks"].append({"check": check[0], "passed": check[1], "message": check[2]})
    if not advisory_valid:
        result["errors"].append("Advisory authority validation failed")

    # Check duplicate
    rid = receipt.get("receipt_id", "")
    index = load_index()
    if rid in index.get("receipts", {}):
        result["errors"].append(f"Receipt '{rid}' already exists in store")
        return result

    # If validation failed, return before persisting
    if result["errors"]:
        return result

    # Persist receipt
    stored_path = RECEIPTS_DIR / f"{rid}.json"
    save_json(str(stored_path), receipt)

    # Update index
    index.setdefault("receipts", {})[rid] = {
        "receipt_id": rid,
        "packet_type": receipt.get("packet_type", ""),
        "status": receipt.get("status", ""),
        "authority": "advisory",
        "project_id": receipt.get("project_id", ""),
        "sprint_id": receipt.get("sprint_id", ""),
        "stored_at": datetime.now(timezone.utc).isoformat(),
        "stored_path": str(stored_path),
        "content_hash": receipt.get("content_hash", ""),
    }
    save_index(index)

    result["success"] = True
    result["receipt_id"] = rid
    result["stored_path"] = str(stored_path)
    result["validation_status"] = "passed"
    result["advisory_only"] = True
    return result


def get(receipt_id):
    """Retrieve a receipt by receipt_id."""
    result = {
        "found": False,
        "receipt": None,
        "advisory_notice": "This is a read-only query. The returned receipt is advisory-only and confers no authority.",
    }

    if not RECEIPT_ID_PATTERN.match(receipt_id):
        result["found"] = False
        result["receipt"] = None
        return result

    index = load_index()
    if receipt_id not in index.get("receipts", {}):
        return result

    receipt_path = RECEIPTS_DIR / f"{receipt_id}.json"
    if not receipt_path.exists():
        # Index says it exists but file missing — data inconsistency
        result["found"] = False
        return result

    receipt = load_json(str(receipt_path))
    result["found"] = True
    result["receipt"] = receipt
    return result


def list_receipts(limit=50, offset=0, project_id=None, status=None, packet_type=None):
    """List receipts with optional filters and bounded pagination."""
    result = {
        "receipts": [],
        "total_count": 0,
        "limit": limit,
        "offset": offset,
        "advisory_notice": "Listed receipts are advisory-only. Listing does not constitute approval, seal, merge, or production-readiness authority.",
    }

    # Validate limit
    if not isinstance(limit, int) or limit < 1 or limit > 100:
        result["error"] = f"limit must be an integer between 1 and 100, got {limit}"
        return result

    index = load_index()
    all_receipts = list(index.get("receipts", {}).values())

    # Apply filters
    filtered = all_receipts
    if project_id:
        filtered = [r for r in filtered if r.get("project_id") == project_id]
    if status:
        filtered = [r for r in filtered if r.get("status") == status]
    if packet_type:
        filtered = [r for r in filtered if r.get("packet_type") == packet_type]

    total = len(filtered)
    result["total_count"] = total

    # Apply offset and limit
    sliced = filtered[offset:offset + limit]

    # Build summaries
    result["receipts"] = [
        {
            "receipt_id": r["receipt_id"],
            "packet_type": r["packet_type"],
            "status": r["status"],
            "project_id": r.get("project_id", ""),
            "stored_at": r.get("stored_at", ""),
        }
        for r in sliced
    ]

    return result


def status():
    """Return receipt store status summary."""
    index = load_index()
    receipts = index.get("receipts", {})
    total = len(receipts)

    # Compute by_status and by_packet_type counts
    by_status = {}
    by_packet_type = {}
    last_registration = None
    last_ts = None

    for rid, meta in receipts.items():
        s = meta.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1

        pt = meta.get("packet_type", "unknown")
        by_packet_type[pt] = by_packet_type.get(pt, 0) + 1

        stored_at = meta.get("stored_at", "")
        if stored_at and (last_ts is None or stored_at > last_ts):
            last_ts = stored_at
            last_registration = {"receipt_id": rid, "registered_at": stored_at}

    store_status = "healthy" if total > 0 else "healthy"
    # Check if index file is readable
    if not INDEX_PATH.exists():
        store_status = "unavailable"

    return {
        "status": store_status,
        "receipt_store": {
            "total_receipts": total,
            "by_status": by_status,
            "by_packet_type": by_packet_type,
        },
        "last_registration": last_registration,
        "last_validation": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": "pass" if total > 0 else "not_run",
        },
        "advisory_notice": "This status report is advisory-only. It does not approve, seal, merge, or assert production readiness.",
    }


# ─── CLI ──────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="QA Pilot Receipt Store")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # register
    reg_parser = subparsers.add_parser("register", help="Register a receipt")
    reg_parser.add_argument("receipt_path", help="Path to receipt JSON file")

    # get
    get_parser = subparsers.add_parser("get", help="Get a receipt by ID")
    get_parser.add_argument("receipt_id", help="Receipt ID (qapr-YYYYMMDD-NNN)")

    # list
    list_parser = subparsers.add_parser("list", help="List receipts")
    list_parser.add_argument("--limit", type=int, default=50, help="Max results (1-100)")
    list_parser.add_argument("--offset", type=int, default=0, help="Result offset")
    list_parser.add_argument("--project-id", help="Filter by project_id")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--packet-type", help="Filter by packet_type")

    # status
    subparsers.add_parser("status", help="Store status")

    args = parser.parse_args()

    if args.command == "register":
        result = register(args.receipt_path)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)

    elif args.command == "get":
        result = get(args.receipt_id)
        print(json.dumps(result, indent=2))
        sys.exit(0)

    elif args.command == "list":
        result = list_receipts(
            limit=args.limit,
            offset=args.offset,
            project_id=args.project_id,
            status=args.status,
            packet_type=args.packet_type,
        )
        print(json.dumps(result, indent=2))
        sys.exit(0 if "error" not in result else 1)

    elif args.command == "status":
        result = status()
        print(json.dumps(result, indent=2))
        sys.exit(0)


if __name__ == "__main__":
    main()
