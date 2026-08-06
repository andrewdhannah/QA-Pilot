#!/usr/bin/env python3
"""
live-custody-integration.py — Live Write-Custody Integration

Integrates the sealed PROJECT-WIDE-WRITE-CUSTODY-ENFORCEMENT-1 (ledger #23)
into QA Pilot's live write path. Every write attempt passes through project-wide
write custody enforcement before mutation.

Modes:
  live     — Evaluate custody, write if allowed, produce audit receipt
  dry-run  — Evaluate custody, return decision, do NOT write

Exit codes:
  0 — Write allowed (in live mode: file written; in dry-run: would be written)
  1 — Write denied by custody policy
  2 — Input error

Usage:
  # Live write with CLI args
  python3 live-custody-integration.py live --path "docs/foo.md" --content "# New doc" \
    --sprint SPRINT-1 --project qa-pilot --allowlisted

  # Dry-run evaluation
  python3 live-custody-integration.py dry-run --path "startup-contract.json" \
    --content "{}" --project qa-pilot --sprint NONE

  # With owner approval
  python3 live-custody-integration.py live --path "startup-contract.json" \
    --content "{}" --project qa-pilot --sprint SPRINT-1 \
    --owner-approved --owner-approval-ref "OD-SOME-SEAL-1"

  # From JSON input
  python3 live-custody-integration.py live --input request.json

  # From stdin
  echo '{"file_path":"...","content":"..."}' | python3 live-custody-integration.py live

Authority source: docs/governance/PROJECT-WIDE-WRITE-CUSTODY-ENFORCEMENT.md (sealed #23)
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENFORCER_PATH = os.path.join(PROJECT_ROOT, "scripts", "enforce-project-wide-write-custody.py")
AUDIT_DIR = os.path.join(PROJECT_ROOT, "data", "custody-audit")

# ── Audit receipt helpers ──────────────────────────────────────────────────


def ensure_audit_dir():
    """Create audit directory if it doesn't exist."""
    os.makedirs(AUDIT_DIR, exist_ok=True)


def generate_receipt_id(mode: str) -> str:
    """Generate a unique receipt ID."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"ci-{mode}-{ts}"


def produce_audit_receipt(
    receipt_id: str,
    mode: str,
    file_path: str,
    decision: str,
    blocker_code: str,
    decision_rationale: str,
    custody_class: str,
    triggered_rules: list,
    project_id: str,
    sprint_id: str,
    owner_approval_ref: str = "",
    warning_emitted: bool = False,
    write_executed: bool = False,
    content_hash: str = "",
    dry_run_decision: str = "",
) -> dict:
    """Create and persist an audit receipt."""
    receipt = {
        "receipt_id": receipt_id,
        "receipt_type": "custody_integration_audit",
        "mode": mode,
        "enforcement_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project_id": project_id,
        "sprint_id": sprint_id,
        "request": {
            "file_path": file_path,
            "content_hash": content_hash,
        },
        "enforcement": {
            "decision": decision,
            "blocker_code": blocker_code,
            "decision_rationale": decision_rationale,
            "custody_class": custody_class,
            "triggered_rules": triggered_rules,
        },
        "result": {
            "write_executed": write_executed,
            "warning_emitted": warning_emitted,
            "owner_approval_ref": owner_approval_ref,
        },
    }

    if dry_run_decision:
        receipt["result"]["dry_run_decision"] = dry_run_decision

    # Persist
    ensure_audit_dir()
    receipt_path = os.path.join(AUDIT_DIR, f"{receipt_id}.json")
    with open(receipt_path, "w") as f:
        json.dump(receipt, f, indent=2)

    return receipt


def content_sha256(content: str) -> str:
    """Compute SHA-256 of content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# ── Enforcement integration ────────────────────────────────────────────────


def run_enforcement(enforcer_path: str, request: dict) -> dict:
    """Run the enforcement script with the given request and parse the result."""
    import subprocess

    # Write request to temp file for the enforcer
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(request, f)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, enforcer_path, "--input", tmp_path],
            capture_output=True, text=True, timeout=30
        )
        # Parse JSON from first JSON block in stdout
        stdout = result.stdout
        # Find the first complete JSON object
        depth = 0
        start = -1
        for i, ch in enumerate(stdout):
            if ch == "{":
                if start < 0:
                    start = i
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0 and start >= 0:
                    try:
                        return json.loads(stdout[start:i + 1])
                    except json.JSONDecodeError:
                        break
        return {
            "decision": "UNKNOWN",
            "blocker_code": "",
            "decision_rationale": f"Failed to parse enforcement output: {stdout[:200]}",
            "custody_class": "UNKNOWN",
            "triggered_rules": [],
            "warning": "",
        }
    except Exception as e:
        return {
            "decision": "UNKNOWN",
            "blocker_code": "",
            "decision_rationale": f"Enforcement execution error: {e}",
            "custody_class": "UNKNOWN",
            "triggered_rules": [],
            "warning": "",
        }
    finally:
        os.unlink(tmp_path)


def do_write(file_path: str, content: str, project_root: str) -> tuple:
    """
    Perform the actual file write.

    Returns (success: bool, error_msg: str).
    Path is relative to project_root for safety.
    """
    # Safety: prevent path traversal
    normalized = os.path.normpath(file_path)
    if normalized.startswith(".."):
        return False, f"Path traversal detected: {file_path}"

    full_path = os.path.join(project_root, normalized)
    parent = os.path.dirname(full_path)

    try:
        os.makedirs(parent, exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        return True, ""
    except (OSError, IOError) as e:
        return False, str(e)


# ── Main logic ──────────────────────────────────────────────────────────────


def process_write_request(request: dict, mode: str, project_root: str) -> dict:
    """
    Process a single write request through the custody pipeline.

    Returns a dict with the full result including audit receipt.
    """
    file_path = request.get("file_path", "")
    content = request.get("content", "")
    project_id = request.get("project_id", "unknown")
    sprint_id = request.get("sprint_id", "unknown")
    owner_approval_present = request.get("owner_approval_present", False)
    owner_approval_ref = request.get("owner_approval_ref", "")
    owner_approval_is_broad = request.get("owner_approval_is_broad", False)

    content_hash = content_sha256(content)
    receipt_id = generate_receipt_id(mode)

    # Build enforcement request
    enforcement_request = {
        "project_id": project_id,
        "sprint_id": sprint_id,
        "file_path": file_path,
        "requested_action": request.get("requested_action", "write"),
        "custody_class": request.get("custody_class", ""),
        "release_state": request.get("release_state", "pre_release"),
        "sealed_evidence": request.get("sealed_evidence", False),
        "generated_by_tool": request.get("generated_by_tool", False),
        "tool_is_deterministic": request.get("tool_is_deterministic", False),
        "owner_approval_present": owner_approval_present,
        "owner_approval_is_broad": owner_approval_is_broad,
        "sprint_allowlisted": request.get("sprint_allowlisted", False),
        "write_authority_source": request.get("write_authority_source", "none"),
        "is_cleanup": request.get("is_cleanup", False),
        "is_formatting": request.get("is_formatting", False),
    }

    # Run enforcement
    enforcement_result = run_enforcement(ENFORCER_PATH, enforcement_request)
    decision = enforcement_result.get("decision", "UNKNOWN")
    blocker_code = enforcement_result.get("blocker_code", "")
    decision_rationale = enforcement_result.get("decision_rationale", "")
    custody_class = enforcement_result.get("custody_class", "")
    triggered_rules = enforcement_result.get("triggered_rules", [])
    warning_text = enforcement_result.get("warning", "")
    custody_class = enforcement_result.get("custody_class", "")
    triggered_rules = enforcement_result.get("triggered_rules", [])

    # If enforcement doesn't include warning in JSON, generate it ourselves
    if not warning_text and custody_class == "OWNER_APPROVAL_REQUIRED" and decision != "ALLOW":
        warning_text = (
            "WRITE AUTHORITY WARNING\n"
            "\n"
            f"Requested file:\n"
            f"{file_path}\n"
            "\n"
            f"Current custody class:\n"
            f"{custody_class}\n"
            "\n"
            f"Reason for requested write:\n"
            f"{request.get('requested_action', 'write')}\n"
            "\n"
            "Risk:\n"
            "Authority/configuration file — unintended changes may affect project governance.\n"
            "\n"
            "Required action:\n"
            "Explicit Owner approval naming this file/path/class.\n"
        )

    warning_emitted = bool(warning_text)

    # Determine action based on decision and mode
    if mode == "dry-run":
        # Dry-run: never write
        receipt = produce_audit_receipt(
            receipt_id=receipt_id, mode=mode, file_path=file_path,
            decision=decision, blocker_code=blocker_code,
            decision_rationale=decision_rationale, custody_class=custody_class,
            triggered_rules=triggered_rules, project_id=project_id,
            sprint_id=sprint_id, owner_approval_ref=owner_approval_ref,
            warning_emitted=warning_emitted, write_executed=False,
            content_hash=content_hash, dry_run_decision=decision,
        )
        return {
            "receipt_id": receipt_id,
            "mode": mode,
            "decision": decision,
            "blocker_code": blocker_code,
            "decision_rationale": decision_rationale,
            "custody_class": custody_class,
            "triggered_rules": triggered_rules,
            "write_executed": False,
            "warning": warning_text,
            "audit_receipt": receipt,
        }

    # Live mode
    if decision in ("ALLOW",):
        # Perform the write
        write_executed, write_error = do_write(file_path, content, project_root)

        if not write_executed:
            # Write failed at filesystem level
            pass  # receipt still records the attempt

        receipt = produce_audit_receipt(
            receipt_id=receipt_id, mode=mode, file_path=file_path,
            decision=decision, blocker_code=blocker_code,
            decision_rationale=decision_rationale, custody_class=custody_class,
            triggered_rules=triggered_rules, project_id=project_id,
            sprint_id=sprint_id, owner_approval_ref=owner_approval_ref,
            warning_emitted=warning_emitted, write_executed=write_executed,
            content_hash=content_hash,
        )

        result = {
            "receipt_id": receipt_id,
            "mode": mode,
            "decision": decision,
            "blocker_code": blocker_code,
            "decision_rationale": decision_rationale,
            "custody_class": custody_class,
            "triggered_rules": triggered_rules,
            "write_executed": write_executed,
            "write_error": write_error,
            "warning": warning_text if warning_emitted else "",
            "audit_receipt": receipt,
        }
        return result

    else:
        # Decision is not ALLOW — block the write
        receipt = produce_audit_receipt(
            receipt_id=receipt_id, mode=mode, file_path=file_path,
            decision=decision, blocker_code=blocker_code,
            decision_rationale=decision_rationale, custody_class=custody_class,
            triggered_rules=triggered_rules, project_id=project_id,
            sprint_id=sprint_id, owner_approval_ref=owner_approval_ref,
            warning_emitted=warning_emitted, write_executed=False,
            content_hash=content_hash,
        )

        return {
            "receipt_id": receipt_id,
            "mode": mode,
            "decision": decision,
            "blocker_code": blocker_code,
            "decision_rationale": decision_rationale,
            "custody_class": custody_class,
            "triggered_rules": triggered_rules,
            "write_executed": False,
            "write_error": f"Custody blocked: {decision}",
            "warning": warning_text,
            "audit_receipt": receipt,
        }


def main():
    parser = argparse.ArgumentParser(
        description="Live write-custody integration")

    parser.add_argument("mode", choices=["live", "dry-run"],
                        help="live = write if allowed; dry-run = evaluate only")

    # Input source
    parser.add_argument("--input", "-i", type=str,
                        help="JSON input file")

    # CLI args
    parser.add_argument("--project", type=str, default="qa-pilot")
    parser.add_argument("--sprint", type=str, default="unknown")
    parser.add_argument("--path", type=str, default="",
                        help="File path to write (relative to project root)")
    parser.add_argument("--content", type=str, default="",
                        help="File content to write")
    parser.add_argument("--action", type=str, default="write",
                        help="Description of write action")
    parser.add_argument("--custody-class", type=str, default="",
                        help="Override custody class")
    parser.add_argument("--release-state", type=str, default="pre_release")
    parser.add_argument("--allowlisted", action="store_true")
    parser.add_argument("--owner-approved", action="store_true")
    parser.add_argument("--owner-approval-ref", type=str, default="",
                        help="Reference to Owner approval decision")
    parser.add_argument("--owner-broad", action="store_true")
    parser.add_argument("--sealed", action="store_true")
    parser.add_argument("--generated", action="store_true")
    parser.add_argument("--tool-deterministic", action="store_true")
    parser.add_argument("--write-source", type=str, default="none")
    parser.add_argument("--cleanup", action="store_true")
    parser.add_argument("--formatting", action="store_true")

    args = parser.parse_args()

    # Build request
    if args.input:
        try:
            with open(args.input) as f:
                request = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(json.dumps({"error": f"Input error: {e}"}), file=sys.stderr)
            return 2
    elif not sys.stdin.isatty() and not args.path:
        try:
            request = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Stdin parse error: {e}"}), file=sys.stderr)
            return 2
    else:
        request = {
            "project_id": args.project,
            "sprint_id": args.sprint,
            "file_path": args.path,
            "content": args.content,
            "requested_action": args.action,
            "custody_class": args.custody_class,
            "release_state": args.release_state,
            "sealed_evidence": args.sealed,
            "generated_by_tool": args.generated,
            "tool_is_deterministic": args.tool_deterministic,
            "owner_approval_present": args.owner_approved,
            "owner_approval_ref": args.owner_approval_ref,
            "owner_approval_is_broad": args.owner_broad,
            "sprint_allowlisted": args.allowlisted,
            "write_authority_source": args.write_source,
            "is_cleanup": args.cleanup,
            "is_formatting": args.formatting,
        }

    result = process_write_request(request, args.mode, PROJECT_ROOT)

    # Output — include warning in JSON output for non-allow cases
    output = {
        "mode": result["mode"],
        "receipt_id": result["receipt_id"],
        "decision": result["decision"],
        "blocker_code": result["blocker_code"],
        "decision_rationale": result["decision_rationale"],
        "custody_class": result["custody_class"],
        "triggered_rules": result["triggered_rules"],
        "write_executed": result["write_executed"],
        "write_error": result.get("write_error", ""),
        "warning": result.get("warning", ""),
    }

    print(json.dumps(output, indent=2))

    # Exit code: 0 = allowed, 1 = denied
    if result["decision"] == "ALLOW":
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
