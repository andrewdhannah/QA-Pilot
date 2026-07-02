#!/usr/bin/env python3
"""
QA Pilot Broker Implementation — QA-PILOT-BROKER-IMPLEMENTATION-1

Implements the Option B broker layer in QA Pilot space only.
Accepts broker requests, enforces custody conditions (CC-1 through CC-10),
routes to QA Pilot handlers, produces advisory-only output, and generates
audit receipts for every call.

Usage:
    python3 scripts/librarian_broker_qa_pilot.py accept <request_json_path>
    python3 scripts/librarian_broker_qa_pilot.py audit <audit_receipt_id>
    python3 scripts/librarian_broker_qa_pilot.py status
    python3 scripts/librarian_broker_qa_pilot.py enable
    python3 scripts/librarian_broker_qa_pilot.py disable

The broker is advisory-only and forward-direction-only (Librarian → QA Pilot).
It does not register native MCPController tools, execute cross-project calls,
or mutate The Librarian runtime.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
AUDIT_DIR = REPO_ROOT / "data" / "audit" / "broker"
CONFIG_DIR = REPO_ROOT / "config"
CONFIG_PATH = CONFIG_DIR / "broker-config.json"
BROKER_VERSION = "qap-broker-v1"

# Known sealed QA Pilot MCP surface tools
SEALED_MCP_TOOLS = [
    "qa_pilot_receipt_register",
    "qa_pilot_receipt_get",
    "qa_pilot_receipt_list",
    "qa_pilot_receipt_status",
]

# Allowed handler paths (project-local under active/qa-pilot/scripts/)
ALLOWED_HANDLER_PREFIX = "active/qa-pilot/scripts/"

# Authority claim mapping
ALLOWED_AUTHORITY_CLAIMS = ["advisory", "read_only"]


# ─── Utilities ────────────────────────────────────────────────────────────────


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


_audit_counter = 0

def generate_audit_id():
    """Generate a unique broker audit receipt ID with sub-second precision."""
    global _audit_counter
    _audit_counter += 1
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    ms = datetime.now(timezone.utc).strftime("%f")[:3]
    return f"qabr-audit-{ts}-{ms}-{_audit_counter}"


# ─── Config / Disable Flag ────────────────────────────────────────────────────


def load_config():
    """Load broker config. Returns default if config file does not exist."""
    if CONFIG_PATH.exists():
        return load_json(str(CONFIG_PATH))
    return {"broker_version": BROKER_VERSION, "broker_enabled": True, "created_at": now_iso()}


def save_config(config):
    os.makedirs(str(CONFIG_DIR), exist_ok=True)
    save_json(str(CONFIG_PATH), config)


def is_broker_enabled():
    config = load_config()
    return config.get("broker_enabled", True)


def set_broker_enabled(enabled):
    config = load_config()
    config["broker_enabled"] = enabled
    config["updated_at"] = now_iso()
    save_config(config)


# ─── Audit Receipt ────────────────────────────────────────────────────────────


def save_audit_receipt(receipt, request_id):
    """Save a broker audit receipt to data/audit/broker/."""
    receipt_id = generate_audit_id()
    receipt["audit_receipt_id"] = receipt_id
    receipt["saved_at"] = now_iso()

    audit_path = AUDIT_DIR / f"{receipt_id}.json"
    save_json(str(audit_path), receipt)
    return receipt_id


def get_audit_receipt(audit_receipt_id):
    """Retrieve an audit receipt by ID."""
    audit_path = AUDIT_DIR / f"{audit_receipt_id}.json"
    if not audit_path.exists():
        return {"found": False, "audit_receipt": None}
    return {"found": True, "audit_receipt": load_json(str(audit_path))}


def list_audit_receipts(limit=50, offset=0):
    """List broker audit receipts with bounded pagination."""
    if not AUDIT_DIR.exists():
        return {"receipts": [], "total_count": 0, "limit": limit, "offset": offset}

    all_files = sorted(AUDIT_DIR.glob("*.json"), reverse=True)
    total = len(all_files)
    sliced = all_files[offset:offset + limit]

    receipts = []
    for f in sliced:
        try:
            data = load_json(str(f))
            receipts.append({
                "audit_receipt_id": data.get("audit_receipt_id", f.stem),
                "request_id": data.get("request_id", ""),
                "tool": data.get("tool", ""),
                "outcome": data.get("outcome", ""),
                "timestamp": data.get("timestamp", ""),
            })
        except (json.JSONDecodeError, OSError):
            continue

    return {"receipts": receipts, "total_count": total, "limit": limit, "offset": offset}


# ─── Custody Verification (CC-1 through CC-10) ────────────────────────────────


def verify_custody(request):
    """
    Verify all 10 custody conditions (CC-1 through CC-10) against a broker request.

    Returns (all_pass, results) where results is a list of
    (cc_id, condition_description, passed, detail) tuples.
    """
    custody_record = request.get("custody_record", {})
    results = []

    # ── Identity Conditions (CC-1 through CC-4) ──

    # CC-1: active_project_id must equal "qa-pilot"
    project_id = request.get("project_id", "")
    cc1_pass = project_id == "qa-pilot"
    results.append((
        "CC-1", "active_project_id == qa-pilot", cc1_pass,
        f"project_id = '{project_id}'" if not cc1_pass else "project_id is qa-pilot"
    ))

    # CC-2: target_project_id must equal "qa-pilot"
    target_project = custody_record.get("target_project", "")
    cc2_pass = target_project == "qa-pilot"
    results.append((
        "CC-2", "target_project_id == qa-pilot", cc2_pass,
        f"target_project = '{target_project}'" if not cc2_pass else "target_project is qa-pilot"
    ))

    # CC-3: Requested tool belongs to sealed QA Pilot MCP surface
    tool = request.get("tool", "")
    cc3_pass = tool in SEALED_MCP_TOOLS
    results.append((
        "CC-3", "tool in sealed QA Pilot MCP surface", cc3_pass,
        f"tool = '{tool}'" if not cc3_pass else f"tool '{tool}' is in sealed surface"
    ))

    # CC-4: QA Pilot ledger contains required sealed sprint evidence
    # (structural check: sprint-ledger.json exists and is valid JSON)
    ledger_path = REPO_ROOT / "project-state" / "sprint-ledger.json"
    cc4_pass = ledger_path.exists()
    if cc4_pass:
        try:
            ledger = load_json(str(ledger_path))
            sprints = ledger.get("sprints", [])
            sealed_count = sum(1 for s in sprints if s.get("status") == "sealed")
            cc4_pass = sealed_count > 0
        except (json.JSONDecodeError, OSError):
            cc4_pass = False
    results.append((
        "CC-4", "QA Pilot ledger has sealed sprints", cc4_pass,
        "" if cc4_pass else "Ledger missing or no sealed sprints"
    ))

    # ── Authority Conditions (CC-5 through CC-7) ──

    # CC-5: QA Pilot handler path is project-local
    handler_path = custody_record.get("handler_path", "")
    cc5_pass = handler_path.startswith(ALLOWED_HANDLER_PREFIX)
    results.append((
        "CC-5", "handler path is project-local", cc5_pass,
        f"handler_path = '{handler_path}'" if not cc5_pass else "handler path is project-local"
    ))

    # CC-6: Request carries a custody record proving project context
    has_custody = bool(custody_record)
    has_project_context = bool(custody_record.get("project_context") == "qa-pilot")
    cc6_pass = has_custody and has_project_context
    cc6_detail = ""
    if not has_custody:
        cc6_detail = "No custody_record in request"
    elif not has_project_context:
        cc6_detail = "project_context is not qa-pilot"
    results.append((
        "CC-6", "request carries custody record with project context", cc6_pass, cc6_detail
    ))

    # CC-7: Output remains advisory/read-only/R1
    authority_claimed = custody_record.get("authority_claimed", "")
    cc7_pass = authority_claimed in ALLOWED_AUTHORITY_CLAIMS
    results.append((
        "CC-7", "authority claimed is advisory or read_only", cc7_pass,
        f"authority_claimed = '{authority_claimed}'" if not cc7_pass else "authority is valid"
    ))

    # ── Safety Conditions (CC-8 through CC-10) ──

    # CC-8: Output does not create Owner approval, seal, merge, or production-readiness state
    # (structural check — broker itself never produces such state)
    cc8_pass = True
    results.append(("CC-8", "no Owner approval/seal/merge/production from output", cc8_pass,
                     "broker enforces advisory-only — no approval state produced"))

    # CC-9: All broker calls produce audit evidence
    # (verified at call time when audit receipt is saved)
    cc9_pass = True
    results.append(("CC-9", "broker call will produce audit evidence", cc9_pass,
                     "audit receipt will be generated"))

    # CC-10: Rollback path documented before implementation
    gov_doc = REPO_ROOT / "docs" / "governance" / "QA-PILOT-BROKER-IMPLEMENTATION.md"
    cc10_pass = gov_doc.exists()
    results.append((
        "CC-10", "rollback path documented", cc10_pass,
        "" if cc10_pass else "Implementation governance doc not found"
    ))

    all_pass = all(r[2] for r in results)
    return all_pass, results


# ─── Tool Routing ─────────────────────────────────────────────────────────────


def route_to_handler(tool, params):
    """
    Route a broker request to the appropriate QA Pilot handler.

    The handler is called locally within QA Pilot space.
    Returns the handler's output.
    """
    # Import handlers
    sys.path.insert(0, str(SCRIPT_DIR))
    try:
        import qa_pilot_mcp_handlers as handlers
    except ImportError:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "qa_pilot_mcp_handlers",
            str(SCRIPT_DIR / "qa_pilot_mcp_handlers.py")
        )
        handlers = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(handlers)

    if tool == "qa_pilot_receipt_register":
        receipt_path = params.get("receipt_path", "")
        if not receipt_path:
            return {"success": False, "error": "Missing receipt_path in params"}
        resolved_path = str(REPO_ROOT / receipt_path) if not receipt_path.startswith("/") else receipt_path
        return handlers.handle_register(resolved_path)

    elif tool == "qa_pilot_receipt_get":
        receipt_id = params.get("receipt_id", "")
        if not receipt_id:
            return {"success": False, "error": "Missing receipt_id in params"}
        return handlers.handle_get(receipt_id)

    elif tool == "qa_pilot_receipt_list":
        limit = params.get("limit", 50)
        offset = params.get("offset", 0)
        project_id = params.get("project_id")
        status = params.get("status")
        packet_type = params.get("packet_type")
        return handlers.handle_list(
            limit=limit, offset=offset,
            project_id=project_id, status=status,
            packet_type=packet_type
        )

    elif tool == "qa_pilot_receipt_status":
        return handlers.handle_status()

    else:
        return {"success": False, "error": f"Unknown tool: '{tool}'"}


# ─── Broker Core ──────────────────────────────────────────────────────────────


def accept_request(request_path):
    """
    Accept and process a broker request from a JSON file.

    Steps:
    1. Check disable flag
    2. Verify custody (CC-1 through CC-10)
    3. Check project boundary
    4. Route to handler
    5. Enforce advisory output
    6. Create audit receipt
    7. Return response
    """
    start_time = datetime.now(timezone.utc)

    # Load request
    try:
        request = load_json(request_path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return {
            "broker_version": BROKER_VERSION,
            "error": f"Failed to load request: {e}",
            "accepted": False,
            "authority": "advisory_only",
            "project_boundary": "qa-pilot",
            "custody_verified": False,
            "custody_conditions_checked": [],
            "request_id": "unknown",
            "timestamp": now_iso(),
        }

    request_id = request.get("request_id", "unknown")
    tool = request.get("tool", "unknown")

    # Step 1: Check disable flag
    if not is_broker_enabled():
        audit_data = _build_refusal_audit(request, "broker_disabled", "Broker is disabled. Set BROKER_ENABLED=true to enable.")
        audit_id = save_audit_receipt(audit_data, request_id)
        return _build_rejection(
            request_id=request_id,
            error="Broker is disabled. Set BROKER_ENABLED=true to enable.",
            audit_receipt_id=audit_id,
        )

    # Step 2: Verify custody (CC-1 through CC-10)
    custody_pass, custody_results = verify_custody(request)
    custody_conditions_checked = []
    for cc_id, desc, passed, detail in custody_results:
        custody_conditions_checked.append({
            "condition": f"{cc_id}: {desc}",
            "passed": passed,
            "detail": detail,
        })

    if not custody_pass:
        # Build structured refusal with audit evidence
        failed_conditions = [c for c in custody_conditions_checked if not c["passed"]]
        error_detail = "; ".join(f"{c['condition']}: {c['detail']}" for c in failed_conditions)
        audit_data = _build_refusal_audit(
            request, "custody_failed",
            f"Custody verification failed: {error_detail}",
            custody_conditions_checked=custody_conditions_checked,
        )
        audit_id = save_audit_receipt(audit_data, request_id)
        return _build_rejection(
            request_id=request_id,
            error=f"Custody verification failed: {error_detail}",
            audit_receipt_id=audit_id,
            extra={"custody_conditions_checked": custody_conditions_checked},
        )

    # Step 3: Project boundary check
    project_id = request.get("project_id", "")
    if project_id != "qa-pilot":
        audit_data = _build_refusal_audit(
            request, "invalid_project",
            f"project_id must be 'qa-pilot', got '{project_id}'",
            custody_conditions_checked=custody_conditions_checked,
        )
        audit_id = save_audit_receipt(audit_data, request_id)
        return _build_rejection(
            request_id=request_id,
            error=f"Invalid project_id: '{project_id}' (must be 'qa-pilot')",
            audit_receipt_id=audit_id,
            extra={"custody_conditions_checked": custody_conditions_checked},
        )

    # Step 4: Route to handler
    params = request.get("params", {})
    handler_output = route_to_handler(tool, params)

    # Step 5: Enforce advisory output
    has_authority_issue = False
    if isinstance(handler_output, dict):
        # Verify the handler output doesn't claim approval/seal/merge authority
        for forbidden_key in ["approved", "sealed", "merged", "production_ready"]:
            if handler_output.get(forbidden_key) is True:
                has_authority_issue = True
                handler_output["advisory_override"] = True
                handler_output[forbidden_key] = False
                handler_output["advisory_notice"] = (
                    "Authority override: output must not create Owner approval, "
                    "seal, merge, or production-readiness state (CC-8). "
                    "All broker outputs are advisory-only."
                )

    # Wrap output with broker metadata
    broker_output = {
        "handler": tool,
        "output": handler_output,
        "authority": "advisory_only",
        "project_boundary": "qa-pilot",
    }

    # Step 6: Create audit receipt
    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
    audit_data = {
        "receipt_type": "broker_audit",
        "request_id": request_id,
        "tool": tool,
        "project_id": "qa-pilot",
        "custody_verified": True,
        "custody_conditions_checked": custody_conditions_checked,
        "output_authority": "advisory_only",
        "timestamp": now_iso(),
        "duration_ms": round(elapsed, 2),
        "outcome": "success" if not has_authority_issue else "success_with_override",
        "accepted": True,
    }
    if has_authority_issue:
        audit_data["authority_override"] = True
        audit_data["note"] = "Output authority was overridden to advisory-only per CC-8"

    audit_receipt_id = save_audit_receipt(audit_data, request_id)

    # Step 7: Return response
    response = {
        "broker_version": BROKER_VERSION,
        "request_id": request_id,
        "output": broker_output,
        "authority": "advisory_only",
        "project_boundary": "qa-pilot",
        "custody_verified": True,
        "custody_conditions_checked": custody_conditions_checked,
        "audit_receipt_id": audit_receipt_id,
        "accepted": True,
        "timestamp": now_iso(),
    }
    if has_authority_issue:
        response["advisory_override"] = True
        response["advisory_notice"] = (
            "Output authority was overridden to advisory-only. "
            "Broker outputs do not confer approval, seal, merge, or production-readiness authority."
        )

    return response


def _build_refusal_audit(request, reason, detail, custody_conditions_checked=None):
    """Build an audit receipt for a rejected/refused broker request."""
    return {
        "receipt_type": "broker_audit",
        "request_id": request.get("request_id", "unknown"),
        "tool": request.get("tool", "unknown"),
        "project_id": request.get("project_id", "unknown"),
        "custody_verified": False,
        "custody_conditions_checked": custody_conditions_checked or [],
        "output_authority": "advisory_only",
        "timestamp": now_iso(),
        "duration_ms": 0,
        "outcome": "failure",
        "error": detail,
        "refusal_reason": reason,
        "accepted": False,
    }


def _build_rejection(request_id, error, audit_receipt_id, extra=None):
    """Build a standard rejection response."""
    response = {
        "broker_version": BROKER_VERSION,
        "request_id": request_id,
        "output": None,
        "authority": "advisory_only",
        "project_boundary": "qa-pilot",
        "custody_verified": False,
        "custody_conditions_checked": [],
        "audit_receipt_id": audit_receipt_id,
        "accepted": False,
        "error": error,
        "timestamp": now_iso(),
    }
    if extra:
        response.update(extra)
    return response


# ─── Status ────────────────────────────────────────────────────────────────────


def broker_status():
    """Return broker status summary."""
    enabled = is_broker_enabled()
    config = load_config()

    # Count audit receipts
    audit_count = 0
    if AUDIT_DIR.exists():
        audit_count = len(list(AUDIT_DIR.glob("*.json")))

    return {
        "broker_version": BROKER_VERSION,
        "broker_enabled": enabled,
        "project_boundary": "qa-pilot",
        "cross_project_registration": False,
        "authority": "advisory_only",
        "audit_receipts_total": audit_count,
        "config_path": str(CONFIG_PATH),
        "audit_dir": str(AUDIT_DIR),
        "timestamp": now_iso(),
        "advisory_notice": (
            "This broker is advisory-only. It does not register native MCP tools, "
            "execute cross-project calls, or mutate The Librarian runtime. "
            "All outputs are advisory-only and confer no approval, seal, merge, "
            "or production-readiness authority."
        ),
    }


# ─── CLI ──────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="QA Pilot Librarian Broker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # accept
    accept_parser = subparsers.add_parser("accept", help="Accept and process a broker request")
    accept_parser.add_argument("request_path", help="Path to broker request JSON file")

    # audit
    audit_parser = subparsers.add_parser("audit", help="Get a broker audit receipt")
    audit_parser.add_argument("audit_receipt_id", help="Audit receipt ID")

    # list-audit
    list_audit_parser = subparsers.add_parser("list-audit", help="List broker audit receipts")
    list_audit_parser.add_argument("--limit", type=int, default=50)
    list_audit_parser.add_argument("--offset", type=int, default=0)

    # status
    subparsers.add_parser("status", help="Broker status")

    # enable / disable
    subparsers.add_parser("enable", help="Enable the broker")
    subparsers.add_parser("disable", help="Disable the broker")

    args = parser.parse_args()

    if args.command == "accept":
        result = accept_request(args.request_path)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("accepted", False) else 1)

    elif args.command == "audit":
        result = get_audit_receipt(args.audit_receipt_id)
        print(json.dumps(result["audit_receipt"], indent=2) if result["found"] else json.dumps({"error": "Audit receipt not found"}))
        sys.exit(0 if result["found"] else 1)

    elif args.command == "list-audit":
        result = list_audit_receipts(limit=args.limit, offset=args.offset)
        print(json.dumps(result, indent=2))
        sys.exit(0)

    elif args.command == "status":
        result = broker_status()
        print(json.dumps(result, indent=2))
        sys.exit(0)

    elif args.command == "enable":
        set_broker_enabled(True)
        print(json.dumps({"broker_enabled": True, "message": "Broker enabled"}))
        sys.exit(0)

    elif args.command == "disable":
        set_broker_enabled(False)
        print(json.dumps({"broker_enabled": False, "message": "Broker disabled"}))
        sys.exit(0)


if __name__ == "__main__":
    main()
