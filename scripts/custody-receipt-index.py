#!/usr/bin/env python3
"""
custody-receipt-index.py — Read-only custody receipt index

Builds a read-only query/index layer over unified custody receipts from #26,
so Owner review can query by source, decision type, sprint, ledger reference,
violation code, mutation status, approval provenance, and sealed-contract reference.

This script is read/index only. It does NOT mutate receipts, custody behavior,
write enforcement, lifecycle enforcement, or approval semantics.

Modes:
  index    — Build and output the full index
  query    — Filter receipts by criteria
  status   — Summary counts and health
  dry-run  — Build index without output (for validation)

Usage:
  python3 custody-receipt-index.py index
  python3 custody-receipt-index.py query --custody-source write
  python3 custody-receipt-index.py query --decision-type denied
  python3 custody-receipt-index.py query --violation-code WRITE_SCOPE_VIOLATION
  python3 custody-receipt-index.py query --sprint SPRINT-1
  python3 custody-receipt-index.py query --ledger 23
  python3 custody-receipt-index.py query --contract "#23"
  python3 custody-receipt-index.py query --approval-present
  python3 custody-receipt-index.py status
"""

import argparse
import hashlib
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECEIPTS_DIR = os.path.join(PROJECT_ROOT, "receipts", "owner-decision-custody")


def read_receipts(receipts_dir: str = None) -> dict:
    """
    Read all receipts from the custody receipts directory.

    Returns:
      receipts: list of valid receipt dicts
      malformed: list of (filename, error) tuples
      duplicates: list of (receipt_id, count) tuples
      directory_status: "ok" | "missing" | "empty"
    """
    if receipts_dir is None:
        receipts_dir = RECEIPTS_DIR

    if not os.path.isdir(receipts_dir):
        return {
            "receipts": [],
            "malformed": [],
            "duplicates": [],
            "directory_status": "missing",
            "directory_path": receipts_dir,
        }

    files = sorted(os.listdir(receipts_dir))
    json_files = [f for f in files if f.endswith(".json")]

    if not json_files:
        return {
            "receipts": [],
            "malformed": [],
            "duplicates": [],
            "directory_status": "empty",
            "directory_path": receipts_dir,
        }

    receipts = []
    malformed = []
    seen_ids = {}

    for fname in json_files:
        fpath = os.path.join(receipts_dir, fname)
        try:
            with open(fpath) as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            malformed.append((fname, f"parse_error: {e}"))
            continue

        if not isinstance(data, dict):
            malformed.append((fname, "not_an_object"))
            continue

        receipt_id = data.get("receipt_id", "")
        if not receipt_id:
            malformed.append((fname, "missing_receipt_id"))
            continue

        if receipt_id in seen_ids:
            seen_ids[receipt_id].append(fname)
        else:
            seen_ids[receipt_id] = [fname]

        receipts.append(data)

    duplicates = [(rid, len(fnames)) for rid, fnames in seen_ids.items()
                  if len(fnames) > 1]

    return {
        "receipts": receipts,
        "malformed": malformed,
        "duplicates": duplicates,
        "directory_status": "ok",
        "directory_path": receipts_dir,
    }


def deterministic_output(data: list, sort_key: str = "receipt_id") -> str:
    """Produce deterministic JSON output sorted by the given key."""
    sorted_data = sorted(data, key=lambda x: x.get(sort_key, ""))
    return json.dumps(sorted_data, indent=2, sort_keys=True)


def build_index(receipts_dir: str = None) -> dict:
    """Build a full index with summary stats."""
    result = read_receipts(receipts_dir)

    receipts = result["receipts"]
    malformed = result["malformed"]
    duplicates = result["duplicates"]
    dir_status = result["directory_status"]

    # Index by various dimensions
    by_source = {}
    by_decision_type = {}
    by_violation_code = {}
    by_mutation_status = {}
    by_approval = {"present": 0, "absent": 0}
    by_sprint = {}
    by_ledger = {}
    by_contract = {}

    for r in receipts:
        source = r.get("custody_source", "unknown")
        by_source[source] = by_source.get(source, 0) + 1

        dt = r.get("decision_type", "unknown")
        by_decision_type[dt] = by_decision_type.get(dt, 0) + 1

        vc = r.get("enforcement", {}).get("violation_code", "")
        if vc:
            by_violation_code[vc] = by_violation_code.get(vc, 0) + 1

        ms = r.get("mutation_status", "unknown")
        by_mutation_status[ms] = by_mutation_status.get(ms, 0) + 1

        prov = r.get("provenance", {})
        if prov.get("owner_approval_present", False):
            by_approval["present"] += 1
        else:
            by_approval["absent"] += 1

        sprint = r.get("linked_references", {}).get("sprint_id", "")
        if sprint:
            by_sprint[sprint] = by_sprint.get(sprint, 0) + 1

        ledgers = r.get("linked_references", {}).get("ledger_numbers", [])
        for ln in ledgers:
            key = f"#{ln}"
            by_ledger[key] = by_ledger.get(key, 0) + 1

        contracts = r.get("sealed_contracts_referenced", [])
        for c in contracts:
            by_contract[c] = by_contract.get(c, 0) + 1

    return {
        "index_metadata": {
            "schema": "custody-receipt-index-v1",
            "deterministic": True,
            "directory_status": dir_status,
            "directory_path": result["directory_path"],
            "total_receipts": len(receipts),
            "total_malformed": len(malformed),
            "total_duplicate_ids": len(duplicates),
        },
        "summary": {
            "by_custody_source": by_source,
            "by_decision_type": by_decision_type,
            "by_violation_code": by_violation_code,
            "by_mutation_status": by_mutation_status,
            "by_approval_provenance": by_approval,
            "by_sprint": by_sprint,
            "by_ledger": by_ledger,
            "by_sealed_contract": by_contract,
        },
        "malformed": malformed,
        "duplicates": duplicates,
        "receipts": sorted(receipts, key=lambda x: x.get("receipt_id", "")),
    }


def query_index(receipts_dir: str = None, filters: dict = None) -> dict:
    """Query the index with optional filters."""
    result = read_receipts(receipts_dir)
    receipts = result["receipts"]

    if filters is None:
        filters = {}

    filtered = []
    for r in receipts:
        match = True

        # Filter by custody source
        if "custody_source" in filters:
            if r.get("custody_source") != filters["custody_source"]:
                match = False

        # Filter by decision type
        if "decision_type" in filters:
            if r.get("decision_type") != filters["decision_type"]:
                match = False

        # Filter by violation code
        if "violation_code" in filters:
            if r.get("enforcement", {}).get("violation_code") != filters["violation_code"]:
                match = False

        # Filter by mutation status
        if "mutation_status" in filters:
            if r.get("mutation_status") != filters["mutation_status"]:
                match = False

        # Filter by approval present/absent
        if "approval_present" in filters:
            prov = r.get("provenance", {})
            is_present = prov.get("owner_approval_present", False)
            if filters["approval_present"] and not is_present:
                match = False
            if not filters["approval_present"] and is_present:
                match = False

        # Filter by sprint ID (substring match)
        if "sprint" in filters:
            sid = r.get("linked_references", {}).get("sprint_id", "")
            if filters["sprint"] not in sid:
                match = False

        # Filter by ledger reference
        if "ledger" in filters:
            ledgers = r.get("linked_references", {}).get("ledger_numbers", [])
            if filters["ledger"] not in ledgers:
                match = False

        # Filter by sealed-contract reference
        if "contract" in filters:
            contracts = r.get("sealed_contracts_referenced", [])
            if filters["contract"] not in contracts:
                match = False

        if match:
            filtered.append(r)

    return {
        "query": filters,
        "total_matching": len(filtered),
        "receipts": sorted(filtered, key=lambda x: x.get("receipt_id", "")),
        "directory_status": result["directory_status"],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Read-only custody receipt index")

    parser.add_argument("mode", choices=["index", "query", "status", "dry-run"],
                        help="index=full index, query=filtered, status=summary, dry-run=validate")

    # Query filters
    parser.add_argument("--custody-source", type=str, default="",
                        choices=["write", "live", "lifecycle", ""])
    parser.add_argument("--decision-type", type=str, default="",
                        choices=["approved", "denied", "warning", "dry_run", ""])
    parser.add_argument("--violation-code", type=str, default="")
    parser.add_argument("--mutation-status", type=str, default="",
                        choices=["mutated", "blocked", "dry_run_no_mutation", ""])
    parser.add_argument("--approval-present", action="store_true",
                        help="Only receipts with Owner approval present")
    parser.add_argument("--approval-absent", action="store_true",
                        help="Only receipts without Owner approval")
    parser.add_argument("--sprint", type=str, default="")
    parser.add_argument("--ledger", type=int, default=0)
    parser.add_argument("--contract", type=str, default="",
                        help="Sealed contract reference (#23, #24, #25, #26)")
    parser.add_argument("--non-deterministic", action="store_true",
                        help="Allow non-deterministic output (default: rejected)")
    parser.add_argument("--receipts-dir", type=str, default=RECEIPTS_DIR,
                        help="Override receipts directory path")

    args = parser.parse_args()

    # Non-deterministic rejection
    if args.non_deterministic:
        print(json.dumps({
            "error": "Non-deterministic index generation rejected",
            "mode": args.mode,
        }, indent=2))
        return 1

    if args.mode == "status":
        result = read_receipts(args.receipts_dir)
        output = {
            "mode": "status",
            "directory_status": result["directory_status"],
            "directory_path": result["directory_path"],
            "total_receipts": len(result["receipts"]),
            "total_malformed": len(result["malformed"]),
            "total_duplicate_ids": len(result["duplicates"]),
            "malformed": result["malformed"],
            "duplicates": result["duplicates"],
            "deterministic": True,
        }
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0

    if args.mode in ("index", "dry-run"):
        index = build_index(args.receipts_dir)
        if args.mode == "dry-run":
            # Validation mode: just check the index is buildable
            status = index["index_metadata"]["directory_status"]
            total = index["index_metadata"]["total_receipts"]
            malformed = index["index_metadata"]["total_malformed"]
            print(json.dumps({
                "mode": "dry-run",
                "index_buildable": True,
                "directory_status": status,
                "total_receipts": total,
                "total_malformed": malformed,
            }, indent=2))
        else:
            print(json.dumps(index, indent=2, sort_keys=True))
        return 0

    if args.mode == "query":
        filters = {}
        if args.custody_source:
            filters["custody_source"] = args.custody_source
        if args.decision_type:
            filters["decision_type"] = args.decision_type
        if args.violation_code:
            filters["violation_code"] = args.violation_code
        if args.mutation_status:
            filters["mutation_status"] = args.mutation_status
        if args.approval_present and not args.approval_absent:
            filters["approval_present"] = True
        if args.approval_absent and not args.approval_present:
            filters["approval_present"] = False
        if args.sprint:
            filters["sprint"] = args.sprint
        if args.ledger:
            filters["ledger"] = args.ledger
        if args.contract:
            filters["contract"] = args.contract

        result = query_index(args.receipts_dir, filters)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
