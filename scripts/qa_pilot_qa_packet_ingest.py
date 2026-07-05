#!/usr/bin/env python3
"""
QA Pilot QA Packet Ingest — QA-PILOT-QA-PACKET-INGEST-1

QA Pilot-local CLI for validating and ingesting governed Librarian QA export
packets into QA Pilot-local derived storage.

Commands:
    validate <path>    — Validate a packet without storing
    ingest <path>      — Validate and import a packet into local derived store
    list               — List ingested packets
    status             — Show ingestion store status
    clear              — Clear all ingested packets

Authority: advisory-only. No cross-project write authority.
"""

import json
import os
import sys
import datetime
import hashlib
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
INGESTED_DIR = REPO_ROOT / "data" / "packets" / "ingested"
INDEX_FILE = REPO_ROOT / "data" / "packets" / "ingested-index.json"
VALIDATOR = SCRIPT_DIR / "validate-qa-pilot-qa-packet-ingest.py"

KNOWN_PACKET_TYPES = ["qa_claim_registry", "project_state", "milestone_regression", "training_source"]

# ── Helpers ──────────────────────────────────────────────────────────────────

def ensure_dirs():
    """Ensure data directories exist."""
    INGESTED_DIR.mkdir(parents=True, exist_ok=True)


def load_index():
    """Load the ingested packet index."""
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"packets": [], "ingest_count": 0, "last_ingested_at": None}


def save_index(index):
    """Save the ingested packet index."""
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)


def load_packet(path):
    """Load a packet JSON from path."""
    path = Path(path)
    if not path.exists():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_validator(data):
    """Run the validator rules against packet data. Returns (all_pass, results)."""
    schema_valid = True
    schema_results = []
    try:
        import jsonschema
        schema_path = REPO_ROOT / "docs" / "schemas" / "qa-pilot-qa-packet-ingest.schema.json"
        schema = json.loads(schema_path.read_text())
        jsonschema.validate(data, schema)
        schema_results.append(("SCHEMA", True, "Schema validation passed"))
    except ImportError:
        # Basic field check
        required = [
            "packet_type", "source_project", "consumer_project", "authority_status",
            "generated_at", "source_db_revision", "source_packet_hash", "source_docs",
            "allowed_use", "forbidden_use", "owner_decision_required_for_apply"
        ]
        for field in required:
            if field not in data:
                schema_valid = False
                schema_results.append(("SCHEMA", False, f"Missing required field: {field}"))
        if schema_valid:
            schema_results.append(("SCHEMA", True, "All required fields present"))
    except jsonschema.ValidationError as e:
        schema_valid = False
        schema_results.append(("SCHEMA", False, f"Schema validation failed: {e.message}"))
    except Exception as e:
        schema_valid = False
        schema_results.append(("SCHEMA", False, f"Schema check error: {e}"))

    # Run PI rules
    checks = list(schema_results)

    # PI-1: packet_type
    checks.append(("PI-1", data.get("packet_type") in KNOWN_PACKET_TYPES,
                   f"packet_type = '{data.get('packet_type')}'"))

    # PI-2: source_project
    checks.append(("PI-2", data.get("source_project") == "librarian",
                   f"source_project = '{data.get('source_project')}'"))

    # PI-3: consumer_project
    checks.append(("PI-3", data.get("consumer_project") == "qa-pilot",
                   f"consumer_project = '{data.get('consumer_project')}'"))

    # PI-4: authority_status
    valid_statuses = ["authoritative_export", "advisory_copy", "training_simulated"]
    checks.append(("PI-4", data.get("authority_status") in valid_statuses,
                   f"authority_status = '{data.get('authority_status')}'"))

    # PI-5: authoritative_export must have payload
    if data.get("authority_status") == "authoritative_export":
        has_payload = bool(data.get("payload"))
        checks.append(("PI-5", has_payload,
                       "authoritative_export but no payload" if not has_payload else "has payload"))
    else:
        checks.append(("PI-5", True, "Not authoritative_export — skip"))

    # PI-6: generated_at ISO 8601
    import re
    ts = data.get("generated_at", "")
    ts_ok = bool(re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", ts))
    checks.append(("PI-6", ts_ok, f"generated_at = '{ts}'"))

    # PI-7: source_packet_hash SHA-256
    h = data.get("source_packet_hash", "")
    hash_ok = bool(re.match(r"^[a-f0-9]{64}$", h))
    checks.append(("PI-7", hash_ok, f"source_packet_hash = '{h}'"))

    # PI-8: allowed_use no forbidden
    uses = data.get("allowed_use", [])
    forbidden_uses = [u for u in uses if u == "direct_librarian_mutation"]
    checks.append(("PI-8", len(forbidden_uses) == 0,
                   "Contains direct_librarian_mutation" if forbidden_uses else "no forbidden allowed_use"))

    # PI-9: forbidden_use complete
    required_forbidden = ["direct_librarian_mutation", "owner_decision_substitution", "authority_promotion"]
    fu = data.get("forbidden_use", [])
    missing = [r for r in required_forbidden if r not in fu]
    checks.append(("PI-9", len(missing) == 0,
                   f"Missing forbidden_use: {missing}" if missing else "all required present"))

    # PI-10: owner_decision_required_for_apply
    checks.append(("PI-10", data.get("owner_decision_required_for_apply") is True,
                   "owner_decision_required_for_apply is not True"))

    # PI-11: no mutation payload
    payload = data.get("payload", {})
    mutation_keys = ["seal_action", "approve_action", "merge_action"]
    found_mutation = [k for k in mutation_keys if k in payload]
    checks.append(("PI-11", len(found_mutation) == 0,
                   f"Found mutation keys: {found_mutation}" if found_mutation else "no mutation payload"))

    # PI-12: training_simulated restrictions
    if data.get("authority_status") == "training_simulated":
        sim_ok = "simulation" in uses and "qa_regression" not in uses
        checks.append(("PI-12", sim_ok,
                       "training_simulated use restriction violated" if not sim_ok else "training_simulated restrictions ok"))
    else:
        checks.append(("PI-12", True, "Not training_simulated — skip"))

    # PI-13: not future
    if ts_ok:
        try:
            packet_time = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
            now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            future_ok = packet_time <= now + datetime.timedelta(seconds=5)
            checks.append(("PI-13", future_ok, "generated_at is in the future" if not future_ok else "not in future"))
        except ValueError:
            checks.append(("PI-13", True, "Cannot parse — skip"))
    else:
        checks.append(("PI-13", True, "No valid timestamp — skip"))

    all_pass = all(c[1] for c in checks)
    return (all_pass, checks)


# ── Commands ────────────────────────────────────────────────────────────────

def cmd_validate(args):
    """Validate a packet without storing."""
    if len(args) < 1:
        print("Usage: qa_pilot_qa_packet_ingest.py validate <path>")
        sys.exit(1)

    path = args[0]
    data = load_packet(path)
    all_pass, checks = run_validator(data)

    print(f"Validating: {path}")
    print(f"Packet type: {data.get('packet_type', 'unknown')}")
    print(f"Source: {data.get('source_project', '?')} → {data.get('consumer_project', '?')}")
    print(f"Authority: {data.get('authority_status', '?')}")
    print()

    for rule_id, passed, detail in checks:
        prefix = "✅" if passed else "❌"
        print(f"  {prefix} {rule_id}: {detail}")

    print()
    if all_pass:
        print("VALID — Packet passes all ingestion rules ✅")
        return 0
    else:
        print("INVALID — Packet fails ingestion rules ❌")
        return 1


def cmd_ingest(args):
    """Validate and import a packet into local derived store."""
    if len(args) < 1:
        print("Usage: qa_pilot_qa_packet_ingest.py ingest <path>")
        sys.exit(1)

    path = args[0]
    data = load_packet(path)
    all_pass, checks = run_validator(data)

    print(f"Ingesting: {path}")
    print(f"Packet type: {data.get('packet_type', 'unknown')}")
    print(f"Authority: {data.get('authority_status', '?')}")
    print()

    for rule_id, passed, detail in checks:
        prefix = "✅" if passed else "❌"
        print(f"  {prefix} {rule_id}: {detail}")

    print()
    if not all_pass:
        print("REJECTED — Packet does not pass ingestion rules ❌")
        return 1

    # Generate storage ID
    packet_hash = data.get("source_packet_hash", "unknown")
    short_hash = packet_hash[:12] if packet_hash != "unknown" else "unknown"
    packet_type = data.get("packet_type", "unknown")
    ingest_id = f"qpi-{packet_type}-{short_hash}"

    # Store packet
    ensure_dirs()
    store_path = INGESTED_DIR / f"{ingest_id}.json"
    with open(store_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Update index
    index = load_index()
    index["packets"].append({
        "ingest_id": ingest_id,
        "packet_type": packet_type,
        "source_project": data.get("source_project"),
        "authority_status": data.get("authority_status"),
        "generated_at": data.get("generated_at"),
        "source_packet_hash": packet_hash,
        "store_path": str(store_path),
        "ingested_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "advisory": True,
        "cross_project_write_authorized": False,
        "owner_apply_required": True
    })
    index["ingest_count"] = len(index["packets"])
    index["last_ingested_at"] = index["packets"][-1]["ingested_at"]
    save_index(index)

    print(f"IMPORTED — Packet stored as {ingest_id} ✅")
    print(f"  Location: {store_path}")
    print(f"  Classification: {data.get('authority_status', 'unknown')}")
    print(f"  Advisory: True")
    print(f"  Cross-project write: Not authorized")
    print(f"  Owner apply required: True")
    print("DONE")
    return 0


def cmd_list(args):
    """List ingested packets."""
    index = load_index()
    packets = index.get("packets", [])

    if not packets:
        print("No packets ingested.")
        return 0

    print(f"Ingested packets ({len(packets)} total):")
    print()
    for pkt in packets:
        print(f"  {pkt['ingest_id']}")
        print(f"    Type:      {pkt['packet_type']}")
        print(f"    Authority: {pkt['authority_status']}")
        print(f"    Source:    {pkt['source_project']}")
        print(f"    Ingested:  {pkt['ingested_at']}")
        print(f"    Advisory:  {pkt['advisory']}")
        print()
    return 0


def cmd_status(args):
    """Show ingestion store status."""
    index = load_index()
    packets = index.get("packets", [])

    counts = {}
    for pkt in packets:
        t = pkt.get("packet_type", "unknown")
        counts[t] = counts.get(t, 0) + 1

    print("QA Pilot QA Packet Ingest Store")
    print("=================================")
    print(f"Total ingested packets: {len(packets)}")
    print(f"Store path:            {INGESTED_DIR}")
    print(f"Index path:            {INDEX_FILE}")
    print(f"Last ingested:         {index.get('last_ingested_at', 'never')}")
    print()
    if counts:
        print("By type:")
        for t, c in sorted(counts.items()):
            print(f"  {t}: {c}")
    print()
    print("Authority: advisory-only")
    print("Cross-project write: NOT AUTHORIZED")
    print("Owner apply required for all: True")
    print("Status: intake-only — no auto-apply, no Librarian mutation")
    return 0


def cmd_clear(args):
    """Clear all ingested packets."""
    index = load_index()
    count = len(index.get("packets", []))

    # Remove stored files
    for pkt in index.get("packets", []):
        store_path = Path(pkt.get("store_path", ""))
        if store_path.exists():
            store_path.unlink()

    # Reset index
    index["packets"] = []
    index["ingest_count"] = 0
    index["last_ingested_at"] = None
    save_index(index)

    print(f"Cleared {count} ingested packets.")
    print(f"Index reset.")
    print("DONE")
    return 0


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("QA Pilot QA Packet Ingest CLI — QA-PILOT-QA-PACKET-INGEST-1")
        print()
        print("Usage:")
        print("  validate <path>    — Validate a packet without storing")
        print("  ingest <path>      — Validate and import a packet into local derived store")
        print("  list               — List ingested packets")
        print("  status             — Show ingestion store status")
        print("  clear              — Clear all ingested packets")
        print()
        print("Authority: advisory-only. No cross-project write authority.")
        print("All ingested packets: advisory/derived/non-authoritative for source project.")
        return 0

    command = sys.argv[1]
    cmd_args = sys.argv[2:]

    commands = {
        "validate": cmd_validate,
        "ingest": cmd_ingest,
        "list": cmd_list,
        "status": cmd_status,
        "clear": cmd_clear,
    }

    if command not in commands:
        print(f"Unknown command: {command}", file=sys.stderr)
        print(f"Valid commands: {', '.join(commands.keys())}", file=sys.stderr)
        return 1

    return commands[command](cmd_args)


if __name__ == "__main__":
    sys.exit(main())
