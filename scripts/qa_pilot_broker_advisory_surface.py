#!/usr/bin/env python3
"""
QA Pilot Broker MCP Advisory Surface — QA-PILOT-BROKER-MCP-ADVISORY-SURFACE-1

A QA Pilot-local advisory surface around the sealed broker implementation.
Provides structured command names that delegate to the sealed broker module.
These are NOT native MCP registrations — they are QA Pilot-local CLI adapters.

All commands:
  - Remain advisory-only
  - Delegate to sealed broker (not duplicate policy)
  - Produce structured advisory surface response format
  - Reference broker audit evidence
  - Refuse unsupported commands/authority/paths

Usage:
    python3 scripts/qa_pilot_broker_advisory_surface.py accept <request_json_path>
    python3 scripts/qa_pilot_broker_advisory_surface.py audit <audit_receipt_id>
    python3 scripts/qa_pilot_broker_advisory_surface.py list-audit [--limit N] [--offset N]
    python3 scripts/qa_pilot_broker_advisory_surface.py status
    python3 scripts/qa_pilot_broker_advisory_surface.py enable
    python3 scripts/qa_pilot_broker_advisory_surface.py disable
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SURFACE_VERSION = "qap-broker-v1"
SURFACE_ID = "qa_pilot_broker_advisory_surface"
LIMITATIONS_NOTICE = (
    "This advisory surface is QA Pilot-local only. It does not register native MCP tools, "
    "execute cross-project calls, or mutate The Librarian runtime. "
    "All outputs are advisory-only and confer no approval, seal, merge, "
    "or production-readiness authority."
)

# ─── Broker Import ─────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

broker = None

def get_broker():
    """Import and return the sealed broker module."""
    global broker
    if broker is not None:
        return broker
    try:
        import librarian_broker_qa_pilot as b
        broker = b
        return broker
    except ImportError:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "librarian_broker_qa_pilot",
            str(SCRIPT_DIR / "librarian_broker_qa_pilot.py")
        )
        b = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(b)
        broker = b
        return broker


# ─── Surface Response Builder ──────────────────────────────────────────────────


def build_surface_response(command, accepted, custody_verified=False,
                            audit_receipt_id=None, refusal_code=None,
                            error=None, output=None, extra=None):
    """Build a standard advisory surface response with required fields."""
    response = {
        "surface": SURFACE_ID,
        "command": command,
        "project_id": "qa-pilot",
        "authority": "advisory_only",
        "accepted": accepted,
        "custody_verified": custody_verified,
        "audit_receipt_id": audit_receipt_id or "",
        "broker_commit_or_version": SURFACE_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "limitations": LIMITATIONS_NOTICE,
    }
    if refusal_code:
        response["refusal_code"] = refusal_code
    if error:
        response["error"] = error
    if output is not None:
        response["output"] = output
    if extra:
        response.update(extra)
    return response


# ─── Command Handlers ──────────────────────────────────────────────────────────


def handle_accept(request_path):
    """qa_pilot_broker_accept: Delegate to broker.accept_request()."""
    try:
        b = get_broker()
        broker_result = b.accept_request(request_path)
        accepted = broker_result.get("accepted", False)
        custody_verified = broker_result.get("custody_verified", False)
        audit_receipt_id = broker_result.get("audit_receipt_id", "")

        if not accepted:
            error_text = broker_result.get("error", "")
            if "Failed to load" in error_text or "Failed to read" in error_text:
                refusal_code = "parse_error"
            elif "Custody verification failed" in error_text:
                refusal_code = "custody_failed"
            elif "Invalid project_id" in error_text:
                refusal_code = "invalid_project"
            elif "Broker is disabled" in error_text:
                refusal_code = "broker_disabled"
            else:
                refusal_code = "refused"
            return build_surface_response(
                command="qa_pilot_broker_accept",
                accepted=False,
                custody_verified=custody_verified,
                audit_receipt_id=audit_receipt_id,
                refusal_code=refusal_code,
                error=error_text,
                output=broker_result,
            )

        return build_surface_response(
            command="qa_pilot_broker_accept",
            accepted=True,
            custody_verified=True,
            audit_receipt_id=audit_receipt_id,
            output=broker_result.get("output", broker_result),
        )
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return build_surface_response(
            command="qa_pilot_broker_accept",
            accepted=False,
            refusal_code="parse_error",
            error=f"Failed to read request: {e}",
        )
    except Exception as e:
        return build_surface_response(
            command="qa_pilot_broker_accept",
            accepted=False,
            refusal_code="internal_error",
            error=f"Broker error: {e}",
        )


def handle_audit(audit_receipt_id):
    """qa_pilot_broker_audit: Delegate to broker.get_audit_receipt()."""
    try:
        b = get_broker()
        result = b.get_audit_receipt(audit_receipt_id)

        if result.get("found"):
            return build_surface_response(
                command="qa_pilot_broker_audit",
                accepted=True,
                custody_verified=True,
                audit_receipt_id=audit_receipt_id,
                output=result["audit_receipt"],
            )
        else:
            return build_surface_response(
                command="qa_pilot_broker_audit",
                accepted=False,
                refusal_code="not_found",
                error=f"Audit receipt '{audit_receipt_id}' not found",
            )
    except Exception as e:
        return build_surface_response(
            command="qa_pilot_broker_audit",
            accepted=False,
            refusal_code="internal_error",
            error=f"Audit lookup error: {e}",
        )


def handle_list_audit(limit=50, offset=0):
    """qa_pilot_broker_list_audit: Delegate to broker.list_audit_receipts()."""
    try:
        b = get_broker()
        result = b.list_audit_receipts(limit=limit, offset=offset)
        return build_surface_response(
            command="qa_pilot_broker_list_audit",
            accepted=True,
            custody_verified=True,
            output=result,
        )
    except Exception as e:
        return build_surface_response(
            command="qa_pilot_broker_list_audit",
            accepted=False,
            refusal_code="internal_error",
            error=f"List audit error: {e}",
        )


def handle_status():
    """qa_pilot_broker_status: Delegate to broker.broker_status()."""
    try:
        b = get_broker()
        result = b.broker_status()
        return build_surface_response(
            command="qa_pilot_broker_status",
            accepted=True,
            custody_verified=True,
            output=result,
        )
    except Exception as e:
        return build_surface_response(
            command="qa_pilot_broker_status",
            accepted=False,
            refusal_code="internal_error",
            error=f"Status error: {e}",
        )


def handle_enable():
    """qa_pilot_broker_enable: Delegate to broker.set_broker_enabled(True)."""
    try:
        b = get_broker()
        b.set_broker_enabled(True)
        return build_surface_response(
            command="qa_pilot_broker_enable",
            accepted=True,
            custody_verified=True,
            output={"broker_enabled": True},
        )
    except Exception as e:
        return build_surface_response(
            command="qa_pilot_broker_enable",
            accepted=False,
            refusal_code="internal_error",
            error=f"Enable error: {e}",
        )


def handle_disable():
    """qa_pilot_broker_disable: Delegate to broker.set_broker_enabled(False)."""
    try:
        b = get_broker()
        b.set_broker_enabled(False)
        return build_surface_response(
            command="qa_pilot_broker_disable",
            accepted=True,
            custody_verified=True,
            output={"broker_enabled": False},
        )
    except Exception as e:
        return build_surface_response(
            command="qa_pilot_broker_disable",
            accepted=False,
            refusal_code="internal_error",
            error=f"Disable error: {e}",
        )


# ─── CLI ──────────────────────────────────────────────────────────────────────


# ─── CLI ──────────────────────────────────────────────────────────────────────


SUPPORTED_COMMANDS = [
    "accept", "audit", "list-audit", "status", "enable", "disable",
]

def main():
    parser = argparse.ArgumentParser(description="QA Pilot Broker Advisory Surface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # accept
    acc = subparsers.add_parser("accept", help="Accept and process a broker request via advisory surface")
    acc.add_argument("request_path", help="Path to broker request JSON file")

    # audit
    aud = subparsers.add_parser("audit", help="Get a broker audit receipt via advisory surface")
    aud.add_argument("audit_receipt_id", help="Audit receipt ID")

    # list-audit
    lst = subparsers.add_parser("list-audit", help="List broker audit receipts via advisory surface")
    lst.add_argument("--limit", type=int, default=50)
    lst.add_argument("--offset", type=int, default=0)

    # status
    subparsers.add_parser("status", help="Broker status via advisory surface")

    # enable / disable
    subparsers.add_parser("enable", help="Enable the broker via advisory surface")
    subparsers.add_parser("disable", help="Disable the broker via advisory surface")

    args = parser.parse_args()
    command = args.command

    # Call the right handler directly based on command
    if command == "accept":
        result = handle_accept(args.request_path)
    elif command == "audit":
        result = handle_audit(args.audit_receipt_id)
    elif command == "list-audit":
        result = handle_list_audit(limit=args.limit, offset=args.offset)
    elif command == "status":
        result = handle_status()
    elif command == "enable":
        result = handle_enable()
    elif command == "disable":
        result = handle_disable()
    else:
        result = build_surface_response(
            command=command,
            accepted=False,
            refusal_code="unsupported_command",
            error=f"Unsupported advisory surface command: '{command}'. "
                  f"Supported: {', '.join(sorted(SUPPORTED_COMMANDS))}",
        )

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("accepted", False) else 1)


if __name__ == "__main__":
    main()
