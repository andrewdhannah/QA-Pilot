#!/usr/bin/env python3
"""
QA Pilot MCP Handlers — QA-PILOT-MCP-HANDLER-REGISTRATION-1

QA Pilot-owned local MCP handler stubs that wrap the QA Pilot receipt store.
These handlers implement the four MCP surface tools (register, get, list, status)
by calling the receipt store directly — without registering in The Librarian's
MCP runtime, without mutating The Librarian source code.

Usage:
    python3 scripts/qa_pilot_mcp_handlers.py register <receipt_json_path>
    python3 scripts/qa_pilot_mcp_handlers.py get <receipt_id>
    python3 scripts/qa_pilot_mcp_handlers.py list --limit N [--offset N] [options]
    python3 scripts/qa_pilot_mcp_handlers.py status
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Import the receipt store
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    import qa_pilot_receipt_store as store
except ImportError:
    # Fallback: direct import by path
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "qa_pilot_receipt_store",
        str(SCRIPT_DIR / "qa_pilot_receipt_store.py")
    )
    store = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(store)

RECEIPT_ID_PATTERN = re.compile(r"^qapr-\d{8}-\d{3,}$")
PROJECT_BOUNDARY = "qa-pilot"
STORE_INTEGRATION = "qa_pilot_receipt_store"


# ─── Handler Functions ────────────────────────────────────────────────────────


def handle_register(receipt_path):
    """
    QA Pilot receipt register handler (R1 advisory).

    Calls QA Pilot receipt store register behavior.
    Validates receipt, enforces advisory-only, persists to store.
    Returns receipt_id, stored_path, validation result, advisory_only=true.
    Must not approve, seal, merge, or mark production readiness.
    """
    result = store.register(receipt_path)

    # Wrap store result with handler-level metadata
    handler_result = {
        "handler": "qa_pilot_receipt_register",
        "project_boundary": PROJECT_BOUNDARY,
        "store_integration": STORE_INTEGRATION,
        "cross_project_registration": False,
        "success": result.get("success", False),
        "receipt_id": result.get("receipt_id"),
        "stored_path": result.get("stored_path"),
        "validation_status": result.get("validation_status", "failed"),
        "advisory_only": result.get("advisory_only", False),
        "advisory_notice": "This receipt is registered as advisory evidence only. "
                           "It does not approve, seal, merge, or assert production readiness. "
                           "Only the Owner may approve, seal, or promote this work.",
        "validation_checks": result.get("validation_checks", []),
    }

    if not result.get("success", False):
        handler_result["errors"] = result.get("errors", ["Registration failed"])

    return handler_result


def handle_get(receipt_id):
    """
    QA Pilot receipt get handler (R0 read-only).

    Calls QA Pilot receipt store get behavior.
    Returns receipt or not_found.
    """
    if not RECEIPT_ID_PATTERN.match(str(receipt_id)):
        return {
            "handler": "qa_pilot_receipt_get",
            "project_boundary": PROJECT_BOUNDARY,
            "store_integration": STORE_INTEGRATION,
            "cross_project_registration": False,
            "found": False,
            "receipt": None,
            "advisory_notice": "This is a read-only query. The returned receipt "
                               "is advisory-only and confers no authority.",
            "error": f"Invalid receipt_id format: '{receipt_id}'",
        }

    store_result = store.get(receipt_id)

    return {
        "handler": "qa_pilot_receipt_get",
        "project_boundary": PROJECT_BOUNDARY,
        "store_integration": STORE_INTEGRATION,
        "cross_project_registration": False,
        "found": store_result.get("found", False),
        "receipt": store_result.get("receipt"),
        "advisory_notice": store_result.get(
            "advisory_notice",
            "This is a read-only query. The returned receipt "
            "is advisory-only and confers no authority.",
        ),
    }


def handle_list(limit=50, offset=0, project_id=None, status=None, packet_type=None):
    """
    QA Pilot receipt list handler (R0 read-only).

    Calls QA Pilot receipt store list behavior.
    Enforces bounded limit 1-100.
    """
    # Validate limit first
    if not isinstance(limit, int) or limit < 1 or limit > 100:
        return {
            "handler": "qa_pilot_receipt_list",
            "project_boundary": PROJECT_BOUNDARY,
            "store_integration": STORE_INTEGRATION,
            "cross_project_registration": False,
            "receipts": [],
            "total_count": 0,
            "limit": limit,
            "offset": offset,
            "advisory_notice": "Listed receipts are advisory-only. Listing does not "
                               "constitute approval, seal, merge, or production-readiness authority.",
            "error": f"limit must be an integer between 1 and 100, got {limit}",
        }

    store_result = store.list_receipts(
        limit=limit,
        offset=offset,
        project_id=project_id,
        status=status,
        packet_type=packet_type,
    )

    return {
        "handler": "qa_pilot_receipt_list",
        "project_boundary": PROJECT_BOUNDARY,
        "store_integration": STORE_INTEGRATION,
        "cross_project_registration": False,
        "receipts": store_result.get("receipts", []),
        "total_count": store_result.get("total_count", 0),
        "limit": store_result.get("limit", limit),
        "offset": store_result.get("offset", offset),
        "advisory_notice": store_result.get(
            "advisory_notice",
            "Listed receipts are advisory-only. Listing does not "
            "constitute approval, seal, merge, or production-readiness authority.",
        ),
        "error": store_result.get("error"),
    }


def handle_status():
    """
    QA Pilot receipt status handler (R0 read-only).

    Calls QA Pilot receipt store status behavior.
    Returns counts/status/advisory notice.
    """
    store_result = store.status()

    return {
        "handler": "qa_pilot_receipt_status",
        "project_boundary": PROJECT_BOUNDARY,
        "store_integration": STORE_INTEGRATION,
        "cross_project_registration": False,
        "status": store_result.get("status", "unavailable"),
        "receipt_store": store_result.get("receipt_store", {}),
        "last_registration": store_result.get("last_registration"),
        "last_validation": store_result.get("last_validation"),
        "advisory_notice": store_result.get(
            "advisory_notice",
            "This status report is advisory-only. It does not approve, "
            "seal, merge, or assert production readiness.",
        ),
    }


# ─── CLI ──────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="QA Pilot MCP Handlers")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # register
    reg = subparsers.add_parser("register", help="Register a receipt via handler")
    reg.add_argument("receipt_path", help="Path to receipt JSON file")

    # get
    get = subparsers.add_parser("get", help="Get a receipt via handler")
    get.add_argument("receipt_id", help="Receipt ID (qapr-YYYYMMDD-NNN)")

    # list
    lst = subparsers.add_parser("list", help="List receipts via handler")
    lst.add_argument("--limit", type=int, default=50)
    lst.add_argument("--offset", type=int, default=0)
    lst.add_argument("--project-id")
    lst.add_argument("--status")
    lst.add_argument("--packet-type")

    # status
    subparsers.add_parser("status", help="Store status via handler")

    args = parser.parse_args()

    if args.command == "register":
        result = handle_register(args.receipt_path)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("success", False) else 1)

    elif args.command == "get":
        result = handle_get(args.receipt_id)
        print(json.dumps(result, indent=2))
        sys.exit(0)

    elif args.command == "list":
        result = handle_list(
            limit=args.limit,
            offset=args.offset,
            project_id=args.project_id,
            status=args.status,
            packet_type=args.packet_type,
        )
        print(json.dumps(result, indent=2))
        sys.exit(0 if "error" not in result or not result["error"] else 1)

    elif args.command == "status":
        result = handle_status()
        print(json.dumps(result, indent=2))
        sys.exit(0)


if __name__ == "__main__":
    main()
