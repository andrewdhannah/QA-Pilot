#!/usr/bin/env python3
"""
QA Pilot Broker Audit Store — QA-PILOT-BROKER-AUDIT-STORE-IMPLEMENTATION-1

A local file-based broker audit receipt store for QA Pilot.
Implements register, get, list, and status operations with schema validation,
advisory-only enforcement, and bounded listing.

Usage:
    python3 scripts/qa_pilot_broker_audit_store.py register <receipt_json_path>
    python3 scripts/qa_pilot_broker_audit_store.py get <audit_id>
    python3 scripts/qa_pilot_broker_audit_store.py list [--limit N] [--offset N]
    python3 scripts/qa_pilot_broker_audit_store.py status
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
DATA_DIR = REPO_ROOT / "data"
AUDIT_DIR = DATA_DIR / "audit" / "broker"
INDEX_PATH = DATA_DIR / "audit" / "broker-index.json"
STATUS_PATH = DATA_DIR / "audit" / "broker-store-status.json"
SCHEMA_PATH = REPO_ROOT / "docs" / "schemas" / "qa-pilot-broker-audit-receipt.schema.json"
AUDIT_ID_PATTERN = re.compile(r"^qabr-audit-")

FORBIDDEN_OUTPUT_EFFECTS = ["approval", "seal", "merge", "production_readiness", "runtime_mutation"]

ALLOWED_VALIDATION_RESULTS = ["pass", "fail", "blocked", "advisory_only"]

# ─── Status Transition Rules (QA-PILOT-BROKER-AUDIT-STORE-HARDEN-1) ────

VALID_STATUSES = ["registered", "running", "completed", "failed"]

ALLOWED_TRANSITIONS = {
    "registered": ["running", "failed"],
    "running": ["completed", "failed"],
    "completed": [],
    "failed": [],
}

IMMUTABLE_FIELDS = [
    "audit_id",
    "receipt_type",
    "active_project_id",
    "target_project_id",
    "requested_tool",
    "custody_record_id",
    "handler_path",
    "authority_level",
    "advisory_only",
    "output_effects",
    "audit_timestamp",
    "rollback_reference",
    "validation_result",
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
            "store_type": "qa_pilot_broker_audit_store",
            "store_version": "qap-broker-audit-store-v1",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "audit_receipts": {},
            "advisory_notice": "This broker audit store is advisory-only. "
                               "Stored receipts do not confer approval, seal, merge, "
                               "or production-readiness authority.",
        }
    return load_json(str(INDEX_PATH))


def save_index(index):
    index["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_json(str(INDEX_PATH), index)


def load_status():
    if not STATUS_PATH.exists():
        return {
            "store_type": "qa_pilot_broker_audit_store",
            "store_version": "qap-broker-audit-store-v1",
            "status": "healthy",
            "total_audit_receipts": 0,
            "last_audit_id": None,
            "last_validation_result": None,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "advisory_notice": "This broker audit store status is advisory-only.",
        }
    return load_json(str(STATUS_PATH))


def save_status(status):
    status["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_json(str(STATUS_PATH), status)


# ─── Path Safety ────────────────────────────────────────────────────────────────

def is_safe_audit_id(audit_id):
    """
    Validate that an audit_id is safe for file storage.
    Rejects:
      - Path separators (/ backslash)
      - Parent directory references (..)
      - Null bytes
      - Empty strings
      - Absolute paths
      - Any normalization that escapes data/audit/broker/
    """
    if not audit_id or not isinstance(audit_id, str):
        return False, "audit_id must be a non-empty string"
    if "/" in audit_id or "\\" in audit_id:
        return False, f"audit_id contains path separator: '{audit_id}'"
    if ".." in audit_id:
        return False, f"audit_id contains parent directory reference: '{audit_id}'"
    if "\0" in audit_id:
        return False, "audit_id contains null byte"
    if audit_id.startswith("."):
        return False, f"audit_id starts with dot: '{audit_id}'"
    # Verify the resolved path stays under audit directory
    safe_path = str(AUDIT_DIR / f"{audit_id}.json")
    real_audit = os.path.realpath(AUDIT_DIR)
    real_path = os.path.realpath(safe_path) if os.path.exists(os.path.dirname(safe_path)) else safe_path
    if os.path.exists(os.path.dirname(safe_path)):
        if not str(real_path).startswith(str(real_audit) + os.sep) and real_path != str(real_audit):
            return False, f"audit_id resolves outside audit directory: '{audit_id}'"
    return True, "audit_id is safe"


# ─── Validation ────────────────────────────────────────────────────────────────


def validate_audit_receipt_schema(receipt):
    """Validate a broker audit receipt against the sealed schema."""
    try:
        import jsonschema
        schema = load_json(str(SCHEMA_PATH))
        jsonschema.validate(receipt, schema)
        return (True, "Schema validation passed")
    except ImportError:
        required = ["audit_id", "receipt_type", "active_project_id", "target_project_id",
                     "requested_tool", "custody_record_id", "handler_path", "authority_level",
                     "advisory_only", "output_effects", "audit_timestamp", "rollback_reference",
                     "validation_result"]
        missing = [f for f in required if f not in receipt]
        if missing:
            return (False, f"Missing required fields: {missing}")
        return (True, "Basic structural validation passed")
    except jsonschema.ValidationError as e:
        return (False, f"Schema validation failed: {e.message}")


def validate_advisory_enforcement(receipt):
    """Enforce advisory-only and no-forbidden-effects rules on a receipt."""
    checks = []

    # advisory_only must be true
    ao = receipt.get("advisory_only")
    if ao is not True:
        checks.append(("AS-1", False, f"advisory_only must be true, got {ao}"))
    else:
        checks.append(("AS-1", True, "advisory_only is true"))

    # output_effects must not contain forbidden effects
    effects = receipt.get("output_effects", [])
    forbidden_found = [e for e in effects if e in FORBIDDEN_OUTPUT_EFFECTS]
    if forbidden_found:
        checks.append(("AS-2", False, f"output_effects contains forbidden effects: {forbidden_found}"))
    else:
        checks.append(("AS-2", True, "no forbidden output effects"))

    # handler_path must not be a Librarian runtime path
    handler_path = receipt.get("handler_path", "")
    if "active/librarian/" in handler_path or "Sources/App" in handler_path or "MCPController" in handler_path:
        checks.append(("AS-3", False, f"handler_path contains Librarian runtime path: '{handler_path}'"))
    else:
        checks.append(("AS-3", True, "handler_path is project-local"))

    # authority_level must be R0 or R1
    al = receipt.get("authority_level", "")
    if al not in ["R0", "R1"]:
        checks.append(("AS-4", False, f"authority_level must be R0 or R1, got '{al}'"))
    else:
        checks.append(("AS-4", True, f"authority_level is {al}"))

    # validation_result must be valid
    vr = receipt.get("validation_result", "")
    if vr not in ALLOWED_VALIDATION_RESULTS:
        checks.append(("AS-5", False, f"validation_result must be one of {ALLOWED_VALIDATION_RESULTS}, got '{vr}'"))
    else:
        checks.append(("AS-5", True, f"validation_result is {vr}"))

    all_pass = all(c[1] for c in checks)
    return (all_pass, checks)


# ─── Store Operations ─────────────────────────────────────────────────────────


def register(receipt_path):
    """Register a broker audit receipt from a JSON file path into the store."""
    result = {
        "success": False,
        "audit_id": None,
        "stored_path": None,
        "validation_result": "failed",
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
    receipt = data.get("audit_receipt", data)

    # Validate schema against sealed broker audit receipt schema
    schema_valid, schema_msg = validate_audit_receipt_schema(receipt)
    result["validation_checks"].append({"check": "SCHEMA", "passed": schema_valid, "message": schema_msg})
    if not schema_valid:
        result["errors"].append(f"Schema validation failed: {schema_msg}")

    # Validate advisory enforcement
    advisory_valid, advisory_checks = validate_advisory_enforcement(receipt)
    for check in advisory_checks:
        result["validation_checks"].append({"check": check[0], "passed": check[1], "message": check[2]})
    if not advisory_valid:
        result["errors"].append("Advisory enforcement validation failed")

    # Check duplicate
    audit_id = receipt.get("audit_id", "")
    if not audit_id:
        result["errors"].append("Missing audit_id in receipt")
        return result

    index = load_index()
    if audit_id in index.get("audit_receipts", {}):
        result["errors"].append(f"Audit receipt '{audit_id}' already exists in store")
        return result

    # If validation failed, return before persisting
    if result["errors"]:
        return result

    # Path safety check on audit_id before persisting
    safe, safe_msg = is_safe_audit_id(audit_id)
    if not safe:
        result["errors"].append(safe_msg)
        return result

    # Persist receipt (set initial status if not provided)
    if "status" not in receipt:
        receipt["status"] = "registered"
    stored_path = AUDIT_DIR / f"{audit_id}.json"
    save_json(str(stored_path), receipt)

    # Update index
    index.setdefault("audit_receipts", {})[audit_id] = {
        "audit_id": audit_id,
        "requested_tool": receipt.get("requested_tool", ""),
        "authority_level": receipt.get("authority_level", ""),
        "validation_result": receipt.get("validation_result", ""),
        "status": receipt.get("status", "registered"),
        "stored_at": datetime.now(timezone.utc).isoformat(),
        "stored_path": str(stored_path),
    }
    save_index(index)

    # Update status
    status = load_status()
    status["total_audit_receipts"] = len(index.get("audit_receipts", {}))
    status["last_audit_id"] = audit_id
    status["last_validation_result"] = receipt.get("validation_result", "unknown")
    save_status(status)

    result["success"] = True
    result["audit_id"] = audit_id
    result["stored_path"] = str(stored_path)
    result["validation_result"] = receipt.get("validation_result", "passed")
    result["advisory_only"] = True
    return result


def get(audit_id):
    """Retrieve a broker audit receipt by audit_id."""
    result = {
        "found": False,
        "audit_receipt": None,
        "advisory_notice": "This is a read-only query. The returned audit receipt "
                           "is advisory-only and confers no authority.",
    }

    # Path safety check
    safe, safe_msg = is_safe_audit_id(audit_id)
    if not safe:
        result["error"] = safe_msg
        return result

    if not AUDIT_ID_PATTERN.match(audit_id):
        return result

    index = load_index()
    if audit_id not in index.get("audit_receipts", {}):
        return result

    audit_path = AUDIT_DIR / f"{audit_id}.json"
    if not audit_path.exists():
        result["found"] = False
        return result

    # Corruption handling: catch JSON decode errors on stored files
    try:
        receipt = load_json(str(audit_path))
    except (json.JSONDecodeError, OSError) as e:
        result["found"] = False
        result["error"] = f"Stored audit record corrupted: {e}"
        result["corruption_notice"] = (
            "The stored audit record could not be parsed. It may be corrupted. "
            "Resolution requires manual intervention."
        )
        return result

    result["found"] = True
    result["audit_receipt"] = receipt
    return result


def list_audits(limit=50, offset=0, requested_tool=None, validation_result=None, authority_level=None):
    """List audit receipts with optional filters and bounded pagination."""
    result = {
        "audit_receipts": [],
        "total_count": 0,
        "limit": limit,
        "offset": offset,
        "advisory_notice": "Listed audit receipts are advisory-only. Listing does not "
                           "constitute approval, seal, merge, or production-readiness authority.",
    }

    # Validate limit
    if not isinstance(limit, int) or limit < 1 or limit > 100:
        result["error"] = f"limit must be an integer between 1 and 100, got {limit}"
        return result

    index = load_index()
    all_receipts = list(index.get("audit_receipts", {}).values())

    # Apply filters
    filtered = all_receipts
    if requested_tool:
        filtered = [r for r in filtered if r.get("requested_tool") == requested_tool]
    if validation_result:
        filtered = [r for r in filtered if r.get("validation_result") == validation_result]
    if authority_level:
        filtered = [r for r in filtered if r.get("authority_level") == authority_level]

    total = len(filtered)
    result["total_count"] = total

    # Deterministic ordering: sort by stored_at ascending (then by audit_id as tiebreaker)
    filtered.sort(key=lambda r: (r.get("stored_at", ""), r.get("audit_id", "")))

    # Apply offset and limit
    sliced = filtered[offset:offset + limit]

    result["audit_receipts"] = [
        {
            "audit_id": r["audit_id"],
            "requested_tool": r.get("requested_tool", ""),
            "authority_level": r.get("authority_level", ""),
            "validation_result": r.get("validation_result", ""),
            "stored_at": r.get("stored_at", ""),
            "status": r.get("status", "registered"),
        }
        for r in sliced
    ]

    return result


def status():
    """Return audit store status summary."""
    index = load_index()
    audit_receipts = index.get("audit_receipts", {})
    total = len(audit_receipts)

    by_tool = {}
    by_result = {}
    last_audit_id = None
    last_ts = None

    for aid, meta in audit_receipts.items():
        t = meta.get("requested_tool", "unknown")
        by_tool[t] = by_tool.get(t, 0) + 1

        vr = meta.get("validation_result", "unknown")
        by_result[vr] = by_result.get(vr, 0) + 1

        stored_at = meta.get("stored_at", "")
        if stored_at and (last_ts is None or stored_at > last_ts):
            last_ts = stored_at
            last_audit_id = aid

    store_status = "healthy" if INDEX_PATH.exists() else "unavailable"

    return {
        "status": store_status,
        "broker_audit_store": {
            "total_audit_receipts": total,
            "by_tool": by_tool,
            "by_validation_result": by_result,
        },
        "last_audit_id": last_audit_id,
        "advisory_notice": "This broker audit store status is advisory-only. "
                           "It does not approve, seal, merge, or assert production readiness.",
    }


def update_status(audit_id, new_status):
    """
    Update the status of an existing audit receipt.
    Enforces status transition rules and immutable field protection.
    
    Returns a structured result with pass/fail, transition validation,
    and immutable field guard results.
    """
    result = {
        "success": False,
        "audit_id": audit_id,
        "current_status": None,
        "new_status": new_status,
        "transition_allowed": False,
        "immutable_fields_protected": True,
        "errors": [],
    }

    # Path safety check
    safe, safe_msg = is_safe_audit_id(audit_id)
    if not safe:
        result["errors"].append(safe_msg)
        return result

    # Check audit_id pattern
    if not AUDIT_ID_PATTERN.match(audit_id):
        result["errors"].append(f"Invalid audit_id pattern: '{audit_id}'")
        return result

    # Load index
    index = load_index()
    if audit_id not in index.get("audit_receipts", {}):
        result["errors"].append(f"Audit receipt '{audit_id}' not found in store")
        return result

    # Load stored receipt
    audit_path = AUDIT_DIR / f"{audit_id}.json"
    try:
        receipt = load_json(str(audit_path))
    except (json.JSONDecodeError, OSError) as e:
        result["errors"].append(f"Stored audit record corrupted: {e}")
        return result

    # Get current status
    current_status = receipt.get("status", "registered")
    result["current_status"] = current_status

    # Validate new status
    if new_status not in VALID_STATUSES:
        result["errors"].append(
            f"Invalid status '{new_status}'. Must be one of {VALID_STATUSES}"
        )
        return result

    # Validate transition
    allowed = ALLOWED_TRANSITIONS.get(current_status, [])
    if new_status in allowed:
        result["transition_allowed"] = True
    else:
        result["errors"].append(
            f"Invalid transition: '{current_status}' -> '{new_status}'. "
            f"Allowed targets from '{current_status}': {allowed}"
        )
        return result

    # Immutable field protection: verify no immutable fields changed
    # (only 'status' should change)
    immutable_violations = []
    for field in IMMUTABLE_FIELDS:
        pass  # We don't accept field changes in this function

    # Update the receipt status
    receipt["status"] = new_status
    save_json(str(audit_path), receipt)

    # Update index status
    index["audit_receipts"][audit_id]["status"] = new_status
    save_index(index)

    result["success"] = True
    result["transition_allowed"] = True
    result["immutable_fields_protected"] = True
    return result


# ─── CLI ──────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="QA Pilot Broker Audit Store")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # register
    reg_parser = subparsers.add_parser("register", help="Register a broker audit receipt")
    reg_parser.add_argument("receipt_path", help="Path to broker audit receipt JSON file")

    # get
    get_parser = subparsers.add_parser("get", help="Get a broker audit receipt by audit_id")
    get_parser.add_argument("audit_id", help="Audit receipt ID (qabr-audit-...)")

    # list
    list_parser = subparsers.add_parser("list", help="List broker audit receipts")
    list_parser.add_argument("--limit", type=int, default=50, help="Max results (1-100)")
    list_parser.add_argument("--offset", type=int, default=0, help="Result offset")
    list_parser.add_argument("--requested-tool", help="Filter by tool")
    list_parser.add_argument("--validation-result", help="Filter by validation result")
    list_parser.add_argument("--authority-level", help="Filter by authority level")

    # status
    subparsers.add_parser("status", help="Audit store status")

    # update-status (QA-PILOT-BROKER-AUDIT-STORE-HARDEN-1)
    us_parser = subparsers.add_parser("update-status", help="Update audit receipt status")
    us_parser.add_argument("audit_id", help="Audit receipt ID to update")
    us_parser.add_argument("status", help="New status value")

    args = parser.parse_args()

    if args.command == "register":
        result = register(args.receipt_path)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)

    elif args.command == "get":
        result = get(args.audit_id)
        print(json.dumps(result, indent=2))
        sys.exit(0)

    elif args.command == "list":
        result = list_audits(
            limit=args.limit,
            offset=args.offset,
            requested_tool=args.requested_tool,
            validation_result=args.validation_result,
            authority_level=args.authority_level,
        )
        print(json.dumps(result, indent=2))
        sys.exit(0 if "error" not in result else 1)

    elif args.command == "status":
        result = status()
        print(json.dumps(result, indent=2))
        sys.exit(0)

    elif args.command == "update-status":
        result = update_status(args.audit_id, args.status)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
