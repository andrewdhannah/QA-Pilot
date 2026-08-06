#!/usr/bin/env python3
"""
QA Pilot Work Queue — diagnostic-to-repair pipeline

Manages the governed work queue. QA-Pilot produces diagnostic reports from
validation failures. The queue organizes them into a repair workflow:
  OPEN → TRIAGED → APPROVED → IN_PROGRESS → FIXED → VERIFIED → CLOSED

Authority: advisory-only. QA-Pilot diagnoses. Librarian authorizes.
Agents execute. Validation confirms. Humans decide.
"""

import datetime
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
QUEUE_DIR = REPO_ROOT / "data" / "work-queue"
DIAG_DIR = REPO_ROOT / "data" / "diagnostics"

QUEUE_VERSION = "qa-pilot-work-queue-v1"
VALID_STATUSES = ["OPEN", "TRIAGED", "APPROVED", "IN_PROGRESS", "FIXED", "VERIFIED", "CLOSED", "REJECTED"]
VALID_RESOLUTIONS = ["fixed", "won_t_fix", "duplicate", "not_reproducible", "deferred"]


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_item(path):
    with open(path, "r") as f:
        return json.load(f)


def _save_item(item):
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    path = QUEUE_DIR / f"{item['item_id']}.json"
    with open(path, "w") as f:
        json.dump(item, f, indent=2)
    return path


def _load_all_items():
    items = []
    if QUEUE_DIR.exists():
        for f in sorted(QUEUE_DIR.glob("QA-*.json")):
            try:
                items.append(_load_item(f))
            except Exception:
                pass
    return items


def _save_index(items):
    index = {
        "queue_version": QUEUE_VERSION,
        "generated_at": now_utc(),
        "total_items": len(items),
        "by_status": {},
        "items": [],
    }
    for item in items:
        entry = {k: item.get(k) for k in ["item_id", "status", "severity", "domain", "title", "created_at"]}
        index["items"].append(entry)
        s = item.get("status", "UNKNOWN")
        index["by_status"][s] = index["by_status"].get(s, 0) + 1
    
    with open(QUEUE_DIR / "index.json", "w") as f:
        json.dump(index, f, indent=2)


def _generate_id(domain):
    domain_prefix = {"regression": "REG", "security": "SEC", "uat": "UAT",
                     "accessibility": "A11Y", "performance": "PERF",
                     "ai": "AI", "compliance": "COMPL"}.get(domain, "GEN")
    existing = _load_all_items()
    seq = len(existing) + 1
    return f"QA-{domain_prefix}-{seq:04d}"


def cmd_list(args):
    """List all queue items."""
    items = _load_all_items()
    status_filter = args[0] if args else None
    
    by_status = {}
    for item in items:
        s = item.get("status", "UNKNOWN")
        by_status[s] = by_status.get(s, 0) + 1
    
    print(f"Work Queue — {len(items)} items")
    print(f"Generated: {now_utc()}")
    print()
    print(f"{'ID':<20} {'Status':<14} {'Sev':<6} {'Domain':<14} Title")
    print("-" * 90)
    
    for item in items:
        if status_filter and item.get("status") != status_filter:
            continue
        iid = item.get("item_id", "?")
        st = item.get("status", "?")
        sv = item.get("severity", "?")
        dm = item.get("domain", "?")
        tl = item.get("title", "?")[:45]
        print(f"{iid:<20} {st:<14} {sv:<6} {dm:<14} {tl}")
    
    print()
    print("By status:")
    for s in VALID_STATUSES:
        if s in by_status:
            print(f"  {s}: {by_status[s]}")


def cmd_create(args):
    """Create a queue item from a diagnostic report or directly."""
    if not args:
        print("Usage: work_queue.py create <diagnostic-report-json-path>", file=sys.stderr)
        return 1
    
    diag_path = Path(args[0])
    if not diag_path.exists():
        print(f"Diagnostic report not found: {diag_path}", file=sys.stderr)
        return 1
    
    with open(diag_path, "r") as f:
        diag = json.load(f)
    
    item = {
        "item_id": _generate_id(diag.get("domain", "regression")),
        "status": "OPEN",
        "diagnostic_ref": diag.get("report_id", diag_path.name),
        "severity": diag.get("severity", "MEDIUM"),
        "title": f"Validation failure: {diag.get('test_id', 'unknown')}",
        "description": f"Expected: {diag.get('failure', {}).get('expected', '?')[:100]}",
        "domain": diag.get("domain", "regression"),
        "assigned_to": None,
        "created_at": now_utc(),
        "updated_at": now_utc(),
        "closed_at": None,
        "resolution": None,
        "work_packet_ref": None,
        "constraints": diag.get("constraints", {}),
        "provenance": {
            "advisory": True,
            "no_authority_conferred": True,
            "detected_by": diag.get("provenance", {}).get("detected_by", "qa-pilot-pipeline"),
            "validated_by": None,
            "approved_by": None,
        },
    }
    
    path = _save_item(item)
    _save_index(_load_all_items())
    print(f"Created: {item['item_id']} -> {path}")
    return 0


def cmd_transition(args):
    """Transition a queue item's status.
    
    Usage: work_queue.py transition <item-id> <new-status> [--assign <who>]
    """
    if len(args) < 2:
        print("Usage: work_queue.py transition <item-id> <new-status> [--assign <who>]", file=sys.stderr)
        return 1
    
    item_id = args[0]
    new_status = args[1].upper()
    
    if new_status not in VALID_STATUSES:
        print(f"Invalid status: {new_status}. Valid: {VALID_STATUSES}", file=sys.stderr)
        return 1
    
    item_path = QUEUE_DIR / f"{item_id}.json"
    if not item_path.exists():
        print(f"Item not found: {item_id}", file=sys.stderr)
        return 1
    
    item = _load_item(item_path)
    old_status = item.get("status")
    item["status"] = new_status
    item["updated_at"] = now_utc()
    
    if new_status == "CLOSED":
        item["closed_at"] = now_utc()
    
    # Check for --assign
    if "--assign" in args:
        idx = args.index("--assign")
        if idx + 1 < len(args):
            item["assigned_to"] = args[idx + 1]
    
    _save_item(item)
    _save_index(_load_all_items())
    print(f"Transitioned: {item_id} {old_status} -> {new_status}")
    return 0


def cmd_show(args):
    """Show a single queue item in detail."""
    if not args:
        print("Usage: work_queue.py show <item-id>", file=sys.stderr)
        return 1
    
    item_path = QUEUE_DIR / f"{args[0]}.json"
    if not item_path.exists():
        print(f"Item not found: {args[0]}", file=sys.stderr)
        return 1
    
    item = _load_item(item_path)
    print(json.dumps(item, indent=2))
    return 0


def cmd_status(args):
    """Show queue status summary."""
    items = _load_all_items()
    
    by_status = {}
    by_severity = {}
    by_domain = {}
    
    for item in items:
        s = item.get("status", "UNKNOWN")
        by_status[s] = by_status.get(s, 0) + 1
        sv = item.get("severity", "UNKNOWN")
        by_severity[sv] = by_severity.get(sv, 0) + 1
        dm = item.get("domain", "UNKNOWN")
        by_domain[dm] = by_domain.get(dm, 0) + 1
    
    output = {
        "queue_version": QUEUE_VERSION,
        "generated_at": now_utc(),
        "total_items": len(items),
        "by_status": by_status,
        "by_severity": by_severity,
        "by_domain": by_domain,
        "open_count": by_status.get("OPEN", 0) + by_status.get("TRIAGED", 0),
        "in_progress_count": by_status.get("APPROVED", 0) + by_status.get("IN_PROGRESS", 0),
        "resolved_count": by_status.get("CLOSED", 0) + by_status.get("REJECTED", 0),
        "provenance": {
            "advisory": True,
            "no_authority_conferred": True,
        },
    }
    
    print(json.dumps(output, indent=2))
    return 0


def cmd_diagnose(args):
    """Generate a diagnostic report from a validation result.
    
    Usage: work_queue.py diagnose <test-id> <domain> <expected> <actual>
    """
    if len(args) < 4:
        print("Usage: work_queue.py diagnose <test-id> <domain> <expected> <actual>", file=sys.stderr)
        return 1
    
    test_id = args[0]
    domain = args[1]
    
    diag = {
        "report_id": f"DIAG-{test_id.split('-')[0] if '-' in test_id else 'GEN'}-{len(list(DIAG_DIR.glob('*.json')))+1:04d}",
        "generated_at": now_utc(),
        "test_id": test_id,
        "domain": domain,
        "severity": "MEDIUM",
        "failure": {
            "expected": args[2],
            "actual": args[3],
            "reproduction": f"Run validation domain '{domain}'",
        },
        "constraints": {
            "must_not_modify": ["evidence_store", "authority_records"],
            "required_validation": [test_id],
        },
        "provenance": {
            "advisory": True,
            "no_authority_conferred": True,
            "detected_by": "qa-pilot-pipeline",
        },
    }
    
    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    path = DIAG_DIR / f"{diag['report_id']}.json"
    with open(path, "w") as f:
        json.dump(diag, f, indent=2)
    
    print(f"Diagnostic report created: {path}")
    print(f"Report ID: {diag['report_id']}")
    print(f"To queue: work_queue.py create {path}")
    return 0


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("QA Pilot Work Queue — QA-PILOT-DIAGNOSTIC-TO-WORK-PACKET-CONTRACT")
        print()
        print("Usage:")
        print("  list [status]              — List queue items")
        print("  create <diag-path>         — Create queue item from diagnostic report")
        print("  transition <id> <status>   — Transition item status")
        print("  show <id>                  — Show item details")
        print("  status                     — Queue status summary")
        print("  diagnose <tid> <dom> <exp> <act>  — Create diagnostic report")
        print()
        print("Authority: advisory-only. QA-Pilot diagnoses. Librarian authorizes.")

    command = sys.argv[1]
    cmd_args = sys.argv[2:]

    commands = {
        "list": cmd_list,
        "create": cmd_create,
        "transition": cmd_transition,
        "show": cmd_show,
        "status": cmd_status,
        "diagnose": cmd_diagnose,
    }

    if command not in commands:
        print(f"Unknown command: {command}", file=sys.stderr)
        return 1

    return commands[command](cmd_args)


if __name__ == "__main__":
    sys.exit(main())
