#!/usr/bin/env python3
"""
owner-decision-custody-receipts.py — Owner-Decision Custody Receipt Normalization

Unifies custody receipts from PROJECT-WIDE-WRITE-CUSTODY-ENFORCEMENT-1 (#23),
LIVE-CUSTODY-INTEGRATION-1 (#24), and LIFECYCLE-CUSTODY-EXTENSION-1 (#25)
into a single Owner-reviewable decision trail.

This is a receipt/evidence normalization sprint only. It does NOT add or change
write authority, live mutation authority, lifecycle authority, approval authority,
or execution authority.

Modes:
  live     — Generate normalized receipts and persist them
  dry-run  — Generate normalized receipts without persisting (advisory only)
  scan     — Scan existing audit directories and generate unified receipts

Usage:
  # Normalize a single custody decision
  python3 owner-decision-custody-receipts.py live --input decision.json

  # Scan existing audit directories
  python3 owner-decision-custody-receipts.py scan

  # Dry-run normalize
  python3 owner-decision-custody-receipts.py dry-run --input decision.json

  # From CLI args
  python3 owner-decision-custody-receipts.py live \
    --custody-source write --decision-type denied \
    --decision BLOCK_WRITE_SCOPE_VIOLATION \
    --blocker-code WRITE_SCOPE_VIOLATION \
    --project qa-pilot --sprint SPRINT-1 \
    --file-path "Sources/unlisted.swift" --reason "Outside scope"
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECEIPTS_DIR = os.path.join(PROJECT_ROOT, "receipts", "owner-decision-custody")
WRITE_AUDIT_DIR = os.path.join(PROJECT_ROOT, "data", "custody-audit")
LIFECYCLE_AUDIT_DIR = os.path.join(PROJECT_ROOT, "data", "lifecycle-custody-audit")

RECEIPT_SCHEMA = "owner-decision-custody-receipt-v1"

VALID_CUSTODY_SOURCES = {"write", "live", "lifecycle"}
VALID_SOURCE_CONTRACTS = {"#23", "#24", "#25", "direct"}
VALID_DECISION_TYPES = {"approved", "denied", "warning", "dry_run"}
VALID_MUTATION_STATUSES = {"mutated", "blocked", "dry_run_no_mutation"}


def generate_receipt_id(content: dict) -> str:
    """Generate deterministic receipt ID from content hash."""
    raw = json.dumps(content, sort_keys=True)
    h = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"odcr-{h}"


def ensure_receipts_dir():
    os.makedirs(RECEIPTS_DIR, exist_ok=True)


def normalize_decision_type(decision: str, mode: str = "live") -> str:
    """Map enforcement decision to normalized decision type."""
    if mode == "dry-run":
        return "dry_run"
    if decision == "ALLOW":
        return "approved"
    if decision in ("BLOCK_WRITE_SCOPE_VIOLATION", "LIFECYCLE_CUSTODY_VIOLATION",
                     "FORBIDDEN_SEALED_EVIDENCE", "FORBIDDEN_POST_RELEASE_ROUTINE_EDIT",
                     "GENERATED_WRITE_ONLY", "GENERATED_LIFECYCLE_ONLY"):
        return "denied"
    if decision == "REQUIRES_OWNER_APPROVAL":
        return "warning"
    return "dry_run"


def normalize_mutation_status(decision: str, mode: str) -> str:
    """Determine mutation status from decision and mode."""
    if mode == "dry-run":
        return "dry_run_no_mutation"
    if decision == "ALLOW":
        return "mutated"
    return "blocked"


def build_receipt(input_data: dict) -> dict:
    """
    Build a normalized Owner-decision custody receipt from input data.

    Input fields (all optional with defaults):
      custody_source: "write" | "live" | "lifecycle"
      source_contract: "#23" | "#24" | "#25" | "direct"
      decision_type: "approved" | "denied" | "warning" | "dry_run"
      decision: enforcement decision code
      blocker_code: violation code
      project_id
      sprint_id
      file_path (write/live) or transition (lifecycle)
      transition_reason
      owner_approval_present
      owner_approval_ref
      owner_approval_is_broad
      mode: "live" | "dry-run"
      ledger_numbers: list of ints
      triggered_rules: list of rule IDs
      deterministic: bool (must be true to generate)
    """
    custody_source = input_data.get("custody_source", "write")
    source_contract = input_data.get("source_contract", "#23")

    # Validate custody source
    if custody_source not in VALID_CUSTODY_SOURCES:
        return {"error": f"Invalid custody_source: {custody_source}. Valid: {VALID_CUSTODY_SOURCES}"}

    if source_contract not in VALID_SOURCE_CONTRACTS:
        return {"error": f"Invalid source_contract: {source_contract}. Valid: {VALID_SOURCE_CONTRACTS}"}

    # Decision mapping
    mode = input_data.get("mode", "live")
    decision = input_data.get("decision", "BLOCK_WRITE_SCOPE_VIOLATION")
    decision_type = input_data.get("decision_type", "") or normalize_decision_type(decision, mode)

    if decision_type not in VALID_DECISION_TYPES:
        return {"error": f"Invalid decision_type: {decision_type}. Valid: {VALID_DECISION_TYPES}"}

    # Mutation status
    mutation_status = input_data.get("mutation_status", "") or normalize_mutation_status(decision, mode)

    if mutation_status not in VALID_MUTATION_STATUSES:
        return {"error": f"Invalid mutation_status: {mutation_status}. Valid: {VALID_MUTATION_STATUSES}"}

    # Cross-project rejection
    project_id = input_data.get("project_id", "qa-pilot")
    if project_id != "qa-pilot":
        return {
            "error": f"Cross-project receipt claim rejected: project_id='{project_id}' (must be 'qa-pilot')",
            "decision": "denied",
            "blocker_code": "CROSS_PROJECT_CLAIM_REJECTED",
        }

    # Broad approval rejection
    owner_approval_is_broad = input_data.get("owner_approval_is_broad", False)
    if owner_approval_is_broad:
        return {
            "error": "Broad project-root receipt approval rejected",
            "decision": "denied",
            "blocker_code": "BROAD_PROJECT_ROOT_APPROVAL",
        }

    # Dry-run receipts cannot be treated as approval evidence
    if mode == "dry-run" and decision_type == "approved":
        return {
            "error": "Dry-run receipts cannot be treated as approval evidence",
            "decision": "denied",
            "blocker_code": "DRY_RUN_NOT_APPROVAL",
        }

    # Warning receipts cannot be treated as approval evidence
    if decision_type == "warning" and input_data.get("treat_as_approval", False):
        return {
            "error": "Warning receipts cannot be treated as approval evidence",
            "decision": "denied",
            "blocker_code": "WARNING_NOT_APPROVAL",
        }

    # Deterministic requirement
    deterministic = input_data.get("deterministic", False)
    if not deterministic:
        return {
            "error": "Non-deterministic receipt generation rejected",
            "decision": "denied",
            "blocker_code": "NON_DETERMINISTIC_GENERATION",
        }

    # Build the receipt content hash
    receipt_content = {
        "schema": RECEIPT_SCHEMA,
        "custody_source": custody_source,
        "source_contract": source_contract,
        "decision_type": decision_type,
        "enforcement_decision": decision,
        "project_id": project_id,
        "sprint_id": input_data.get("sprint_id", ""),
        "mode": mode,
        "mutation_status": mutation_status,
        "blocker_code": input_data.get("blocker_code", ""),
        "triggered_rules": input_data.get("triggered_rules", []),
        "ledger_numbers": input_data.get("ledger_numbers", []),
    }

    receipt_id = generate_receipt_id(receipt_content)

    # Build the full receipt
    receipt = {
        "receipt_id": receipt_id,
        "schema": RECEIPT_SCHEMA,
        "custody_source": custody_source,
        "source_contract": source_contract,
        "decision_type": decision_type,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "deterministic": True,
        "immutable": True,
        "request": {
            "project_id": project_id,
            "sprint_id": input_data.get("sprint_id", ""),
            "file_path": input_data.get("file_path", ""),
            "transition": input_data.get("transition", ""),
            "reason": input_data.get("transition_reason", input_data.get("reason", "")),
        },
        "enforcement": {
            "decision": decision,
            "blocker_code": input_data.get("blocker_code", ""),
            "violation_code": input_data.get("blocker_code", "") if decision_type == "denied" else "",
            "triggered_rules": input_data.get("triggered_rules", []),
        },
        "provenance": {
            "owner_approval_present": input_data.get("owner_approval_present", False),
            "owner_approval_ref": input_data.get("owner_approval_ref", ""),
            "approval_is_broad": owner_approval_is_broad,
        },
        "mutation_status": mutation_status,
        "linked_references": {
            "sprint_id": input_data.get("sprint_id", ""),
            "ledger_numbers": input_data.get("ledger_numbers", []),
            "source_receipt_id": input_data.get("source_receipt_id", ""),
        },
        "sealed_contracts_referenced": determine_contract_refs(custody_source, input_data.get("ledger_numbers", [])),
    }

    return receipt


def determine_contract_refs(custody_source: str, ledger_numbers: list) -> list:
    """Determine which sealed contracts are referenced."""
    refs = set()
    if custody_source == "write" or 23 in ledger_numbers:
        refs.add("#23")
    if custody_source == "live" or 24 in ledger_numbers:
        refs.add("#24")
    if custody_source == "lifecycle" or 25 in ledger_numbers:
        refs.add("#25")
    return sorted(refs)


def persist_receipt(receipt: dict) -> tuple:
    """Persist a normalized receipt. Checks immutability (no overwrite)."""
    if "error" in receipt:
        return False, receipt.get("error", "Unknown error")

    ensure_receipts_dir()
    receipt_path = os.path.join(RECEIPTS_DIR, f"{receipt['receipt_id']}.json")

    # Check immutability: refuse to overwrite existing receipts
    if os.path.exists(receipt_path):
        return False, f"Receipt already exists and is immutable: {receipt['receipt_id']}"

    with open(receipt_path, "w") as f:
        json.dump(receipt, f, indent=2)

    return True, receipt["receipt_id"]


def scan_existing_audits(dry_run: bool = False, deterministic: bool = True) -> list:
    """Scan existing audit directories and produce unified receipts."""
    results = []

    # Scan live custody audit dir (#24)
    if os.path.isdir(WRITE_AUDIT_DIR):
        for fname in sorted(os.listdir(WRITE_AUDIT_DIR)):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(WRITE_AUDIT_DIR, fname)
            try:
                with open(fpath) as f:
                    audit = json.load(f)
            except (json.JSONDecodeError, IOError):
                continue

            receipt = convert_audit_to_receipt(audit, "live", "#24", deterministic)
            if receipt:
                results.append(receipt)

    # Scan lifecycle custody audit dir (#25)
    if os.path.isdir(LIFECYCLE_AUDIT_DIR):
        for fname in sorted(os.listdir(LIFECYCLE_AUDIT_DIR)):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(LIFECYCLE_AUDIT_DIR, fname)
            try:
                with open(fpath) as f:
                    audit = json.load(f)
            except (json.JSONDecodeError, IOError):
                continue

            receipt = convert_audit_to_receipt(audit, "lifecycle", "#25", deterministic)
            if receipt:
                results.append(receipt)

    return results


def convert_audit_to_receipt(audit: dict, custody_source: str, source_contract: str,
                              deterministic: bool) -> dict:
    """Convert an existing audit receipt to unified format."""
    enf = audit.get("enforcement", {})
    req = audit.get("request", {})
    res = audit.get("result", {})

    mode = audit.get("mode", "live")
    decision = enf.get("decision", "UNKNOWN")
    file_path = req.get("file_path", "")
    transition = ""
    if custody_source == "lifecycle":
        transition = f"Phase {audit.get('request', {}).get('current_phase', '?')} → Phase {audit.get('request', {}).get('target_phase', '?')}"

    input_data = {
        "custody_source": custody_source,
        "source_contract": source_contract,
        "decision": decision,
        "blocker_code": enf.get("blocker_code", ""),
        "project_id": audit.get("project_id", req.get("project_id", "qa-pilot")),
        "sprint_id": audit.get("sprint_id", req.get("sprint_id", "")),
        "mode": mode,
        "file_path": file_path,
        "transition": transition,
        "transition_reason": req.get("transition_reason", req.get("requested_action", "")),
        "owner_approval_present": res.get("owner_approval_present", False),
        "owner_approval_ref": res.get("owner_approval_ref", ""),
        "owner_approval_is_broad": False,
        "triggered_rules": enf.get("triggered_rules", []),
        "source_receipt_id": audit.get("receipt_id", ""),
        "deterministic": deterministic,
        "ledger_numbers": [23, 24, 25],
    }

    return build_receipt(input_data)


def main():
    parser = argparse.ArgumentParser(
        description="Owner-decision custody receipt normalization")

    parser.add_argument("mode", choices=["live", "dry-run", "scan"],
                        help="live=persist receipts, dry-run=advisory, scan=scan audits")

    parser.add_argument("--input", "-i", type=str, help="JSON input file")
    parser.add_argument("--non-deterministic", action="store_true",
                        help="Allow non-deterministic generation (default: rejected)")

    # Receipt fields
    parser.add_argument("--custody-source", type=str, default="write",
                        choices=["write", "live", "lifecycle"])
    parser.add_argument("--source-contract", type=str, default="#23",
                        choices=["#23", "#24", "#25", "direct"])
    parser.add_argument("--decision-type", type=str, default="",
                        choices=["approved", "denied", "warning", "dry_run"])
    parser.add_argument("--decision", type=str, default="ALLOW")
    parser.add_argument("--blocker-code", type=str, default="")
    parser.add_argument("--project", type=str, default="qa-pilot")
    parser.add_argument("--sprint", type=str, default="")
    parser.add_argument("--file-path", type=str, default="")
    parser.add_argument("--transition", type=str, default="")
    parser.add_argument("--reason", type=str, default="")
    parser.add_argument("--owner-approved", action="store_true")
    parser.add_argument("--owner-ref", type=str, default="")
    parser.add_argument("--owner-broad", action="store_true")
    parser.add_argument("--ledger-numbers", type=str, default="",
                        help="Comma-separated ledger numbers")
    parser.add_argument("--rules", type=str, default="",
                        help="Comma-separated triggered rule IDs")
    parser.add_argument("--treat-as-approval", action="store_true",
                        help="Treat warning/dry-run as approval (will be rejected)")
    parser.add_argument("--source-receipt", type=str, default="")

    args = parser.parse_args()

    deterministic = not args.non_deterministic

    if args.mode == "scan":
        results = scan_existing_audits(
            dry_run=(args.mode == "dry-run"),
            deterministic=deterministic
        )
        output = {
            "mode": "scan",
            "receipts_scanned": len(results),
            "receipts": results if args.mode == "dry-run" else [],
        }
        if args.mode == "live":
            persisted = []
            errors = []
            for r in results:
                if "error" in r:
                    errors.append(r["error"])
                else:
                    ok, msg = persist_receipt(r)
                    if ok:
                        persisted.append(msg)
                    else:
                        errors.append(msg)
            output["receipts_persisted"] = len(persisted)
            output["errors"] = errors

        print(json.dumps(output, indent=2))
        return 0 if not output.get("errors") else 1

    # Build input from CLI or file
    if args.input:
        try:
            with open(args.input) as f:
                input_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(json.dumps({"error": f"Input error: {e}"}), file=sys.stderr)
            return 2
    elif not sys.stdin.isatty() and not args.custody_source:
        try:
            input_data = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Stdin parse error: {e}"}), file=sys.stderr)
            return 2
    else:
        ledger_nums = [int(x.strip()) for x in args.ledger_numbers.split(",") if x.strip()] if args.ledger_numbers else []
        rules = [r.strip() for r in args.rules.split(",") if r.strip()] if args.rules else []

        input_data = {
            "custody_source": args.custody_source,
            "source_contract": args.source_contract,
            "decision_type": args.decision_type,
            "decision": args.decision,
            "blocker_code": args.blocker_code,
            "project_id": args.project,
            "sprint_id": args.sprint,
            "file_path": args.file_path,
            "transition": args.transition,
            "transition_reason": args.reason,
            "mode": args.mode,
            "owner_approval_present": args.owner_approved,
            "owner_approval_ref": args.owner_ref,
            "owner_approval_is_broad": args.owner_broad,
            "treat_as_approval": args.treat_as_approval,
            "ledger_numbers": ledger_nums,
            "triggered_rules": rules,
            "source_receipt_id": args.source_receipt,
            "deterministic": deterministic,
        }

    receipt = build_receipt(input_data)

    if args.mode == "dry-run":
        output = {
            "mode": "dry-run",
            "receipt": receipt if "error" not in receipt else receipt,
        }
        print(json.dumps(output, indent=2))
        return 0

    # Live mode: persist
    if "error" in receipt:
        print(json.dumps({"error": receipt["error"]}, indent=2))
        return 1

    ok, msg = persist_receipt(receipt)
    if ok:
        output = {
            "mode": "live",
            "receipt_id": msg,
            "receipt_path": os.path.join(RECEIPTS_DIR, f"{msg}.json"),
            "status": "persisted",
        }
        print(json.dumps(output, indent=2))
        return 0
    else:
        print(json.dumps({"error": msg}, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
