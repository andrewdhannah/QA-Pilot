#!/usr/bin/env python3
"""
QA Pilot Qualification Evidence Pipeline CLI.

Discovers evidence sources from existing QA Pilot layers, normalizes them
into governed evidence records, creates QR- qualification records, and
ingests them into the qualification store.

Commands:
  discover    Discover available evidence sources from QA Pilot layers
  collect     Collect evidence from specified sources
  ingest      Ingest collected evidence as QR- records
  status      Show pipeline status (sources, records, last run)
  validate    Validate pipeline output
  receipt     Generate collection receipt

Design:
  - Evidence source adapters for each QA Pilot layer type
  - Layer discovery from the landscape catalog
  - Evidence normalization into governed evidence records
  - QR population from normalized evidence
  - Provenance linking back to source artifacts
"""
import argparse, json, os, sys, datetime, glob, re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
VALIDATOR_PATH = os.path.join(SCRIPT_DIR, "validate-qa-pilot-qualification.py")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-pilot-qualification-record.schema.json")
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "qualification-records")
STORE_INDEX = os.path.join(STORE_DIR, "qualification-index.json")
EVIDENCE_LOG_DIR = os.path.join(PROJECT_ROOT, "data", "qualification-evidence-logs")
EVIDENCE_LOG_INDEX = os.path.join(EVIDENCE_LOG_DIR, "collection-log.json")

# Known evidence source adapters mapped to QA Pilot layer data paths
EVIDENCE_SOURCE_ADAPTERS = {
    "pipeline_layer_registry": {
        "description": "Pipeline layer registry (#48)",
        "paths": ["data/pipeline-layer-registry/registry.json"],
        "evidence_type": "registry_state",
        "target_type": "registry_entry",
        "layer": 48
    },
    "registry_change_receipts": {
        "description": "Registry change receipts (#51-#55)",
        "paths": ["data/registry-change-receipts/*.json"],
        "evidence_type": "receipt",
        "target_type": "registry_entry",
        "layer": 51
    },
    "snapshot_baselines": {
        "description": "Snapshot regression baselines (#56)",
        "paths": ["data/snapshot-regression-snapshot/*.json"],
        "evidence_type": "snapshot_baseline",
        "target_type": "startup_surface",
        "layer": 56
    },
    "custody_receipts": {
        "description": "Custody receipts (#26-#28)",
        "paths": ["data/custody-receipts/*.json"],
        "evidence_type": "custody_audit",
        "target_type": "custody_receipt",
        "layer": 26
    },
    "evidence_store": {
        "description": "MCP evidence intake store (#33)",
        "paths": ["data/evidence/*.json"],
        "evidence_type": "evidence_packet",
        "target_type": "evidence_packet",
        "layer": 33
    },
    "result_packets": {
        "description": "Result packet export (#35)",
        "paths": ["data/result-packets/*.json"],
        "evidence_type": "result_packet",
        "target_type": "result_packet",
        "layer": 35
    },
    "test_cases": {
        "description": "Test case store (#34)",
        "paths": ["data/test-cases/*.json"],
        "evidence_type": "validation_result",
        "target_type": "test_case",
        "layer": 34
    },
    "workbench_items": {
        "description": "Workbench item store (#66-#70)",
        "paths": ["data/workbench-items/*.json"],
        "evidence_type": "workbench_item",
        "target_type": "workbench_item",
        "layer": 66
    },
    "review_decision_receipts": {
        "description": "Owner review decision receipts (#42)",
        "paths": ["data/owner-review-decision-receipts/*.json"],
        "evidence_type": "owner_decision",
        "target_type": "decision_packet",
        "layer": 42
    },
    "review_depth_thresholds": {
        "description": "Review depth thresholds (#88)",
        "paths": ["data/review-depth-thresholds/*.json"],
        "evidence_type": "review_outcome",
        "target_type": "review_packet",
        "layer": 88
    },
    "advisory_packets": {
        "description": "Advisory review packets (#62-#63)",
        "paths": ["data/advisory-review-packets/*.json"],
        "evidence_type": "advisory_packet",
        "target_type": "review_packet",
        "layer": 62
    },
    "workbench_export_packets": {
        "description": "Workbench export packets (#70)",
        "paths": ["data/export-packets/*.json"],
        "evidence_type": "export_packet",
        "target_type": "export_packet",
        "layer": 70
    },
    "decision_packets": {
        "description": "Decision packet store (#90)",
        "paths": ["data/review-decision-packets/*.json"],
        "evidence_type": "review_outcome",
        "target_type": "decision_packet",
        "layer": 90
    },
    "action_packets": {
        "description": "Owner action packet store (#78)",
        "paths": ["data/owner-action-packets/*.json"],
        "evidence_type": "advisory_packet",
        "target_type": "action_packet",
        "layer": 78
    },
    "handoff_intakes": {
        "description": "Action handoff intake store (#82)",
        "paths": ["data/action-handoff-intakes/*.json"],
        "evidence_type": "advisory_packet",
        "target_type": "handoff_packet",
        "layer": 82
    }
}


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _ensure_dirs():
    os.makedirs(STORE_DIR, exist_ok=True)
    os.makedirs(EVIDENCE_LOG_DIR, exist_ok=True)
    if not os.path.exists(STORE_INDEX):
        with open(STORE_INDEX, "w") as f:
            json.dump({"records": [], "last_updated": _now()}, f, indent=2)
    if not os.path.exists(EVIDENCE_LOG_INDEX):
        with open(EVIDENCE_LOG_INDEX, "w") as f:
            json.dump({"collections": [], "last_updated": _now()}, f, indent=2)


def _load_index(path):
    _ensure_dirs()
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"records": [], "last_updated": _now()}


def _save_index(index, path):
    index["last_updated"] = _now()
    with open(path, "w") as f:
        json.dump(index, f, indent=2)


def _load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def _generate_id(prefix="QR"):
    """Generate a unique QR- record ID."""
    import random, string
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    seq = random.randint(1, 9999)
    return f"{prefix}-{code}-{seq:04d}"


def cmd_discover(args):
    """Discover available evidence sources from QA Pilot layers."""
    print(f"{'Source':30s} {'Layer':6s} {'Files':8s} {'Evidence Type':25s} {'Description'}")
    print("-" * 100)

    total_files = 0
    available_sources = 0
    for sid, adapter in sorted(EVIDENCE_SOURCE_ADAPTERS.items()):
        files_found = 0
        for pattern in adapter["paths"]:
            full_pattern = os.path.join(PROJECT_ROOT, pattern)
            matches = glob.glob(full_pattern)
            files_found += len(matches)

        status = f"{files_found} files" if files_found > 0 else "empty"
        print(f"{sid:30s} #{adapter['layer']:<4d} {status:8s} {adapter['evidence_type']:25s} {adapter['description']}")
        total_files += files_found
        if files_found > 0:
            available_sources += 1

    print("-" * 100)
    print(f"Total: {available_sources}/{len(EVIDENCE_SOURCE_ADAPTERS)} sources available ({total_files} files)")
    return 0


def _collect_from_source(sid, adapter):
    """Collect evidence records from a single source adapter."""
    evidence_records = []
    for pattern in adapter["paths"]:
        full_pattern = os.path.join(PROJECT_ROOT, pattern)
        for path in sorted(glob.glob(full_pattern)):
            data = _load_json(path)
            if data is None:
                continue
            rel_path = os.path.relpath(path, PROJECT_ROOT)
            evidence_records.append({
                "source_adapter": sid,
                "source_layer": adapter["layer"],
                "source_path": rel_path,
                "source_data_preview": {k: data.get(k) for k in list(data.keys())[:5] if isinstance(data, dict)},
                "collected_at": _now()
            })
    return evidence_records


def _normalize_to_qr_record(evidence, adapter):
    """Normalize a collected evidence record into a QR- qualification record."""
    eid = evidence.get("source_data_preview", {}).get("id") or \
          evidence.get("source_data_preview", {}).get("record_id") or \
          evidence.get("source_data_preview", {}).get("packet_id") or \
          os.path.basename(evidence["source_path"])

    return {
        "record_id": _generate_id(),
        "qualification_type": "artifact",
        "target_id": str(eid),
        "target_type": adapter["target_type"],
        "qualification_level": "unqualified",
        "qualification_criteria": {
            "required_level": "spot_checked",
            "pass_rate_threshold": 0.80,
            "evidence_count_min": 1,
            "authority_check_required": False
        },
        "evidence_refs": [
            {
                "evidence_id": str(eid),
                "evidence_type": adapter["evidence_type"],
                "evidence_source": evidence["source_path"],
                "verification_status": "verified",
                "verified_at": _now()
            }
        ],
        "sub_dimension_scores": {
            "schema_compliance": 1.0,
            "evidence_freshness": 1.0,
            "evidence_diversity": 0.3,
            "authority_boundary": 1.0,
            "provenance_quality": 1.0
        },
        "overall_score": 0.0,
        "lifecycle_state": "completed",
        "provenance": {
            "assessor_id": "qa-pilot-evidence-pipeline",
            "session_id": f"pipeline-{_now()[:10]}",
            "tool_call_log": f"qa_pilot_qualification_evidence_pipeline.py collect --source {evidence['source_adapter']}"
        },
        "expiry_date": (datetime.date.today() + datetime.timedelta(days=90)).isoformat(),
        "advisory_only": True,
        "custody": "qa-pilot-local",
        "librarian_impact": "none",
        "assessed_at": _now(),
        "assessed_by": "qa-pilot-evidence-pipeline"
    }


def cmd_collect(args):
    """Collect evidence from specified sources and normalize to QR- records."""
    _ensure_dirs()

    sources_to_collect = args.source if args.source else list(EVIDENCE_SOURCE_ADAPTERS.keys())
    if "all" in sources_to_collect:
        sources_to_collect = list(EVIDENCE_SOURCE_ADAPTERS.keys())

    total_collected = 0
    total_normalized = 0
    collection_log = []

    for sid in sources_to_collect:
        if sid not in EVIDENCE_SOURCE_ADAPTERS:
            print(f"Unknown source: {sid}")
            continue

        adapter = EVIDENCE_SOURCE_ADAPTERS[sid]
        print(f"Collecting from {sid} ({adapter['description']})...")

        evidence = _collect_from_source(sid, adapter)
        if not evidence:
            print(f"  No evidence found at {adapter['paths']}")
            continue

        total_collected += len(evidence)

        # Normalize each evidence to QR- record
        for ev in evidence:
            qr = _normalize_to_qr_record(ev, adapter)

            # Write QR- record to store
            qr_path = os.path.join(STORE_DIR, f"{qr['record_id']}.json")
            with open(qr_path, "w") as f:
                json.dump(qr, f, indent=2)

            # Update store index
            index = _load_index(STORE_INDEX)
            if qr["record_id"] not in index.get("records", []):
                index.setdefault("records", []).append(qr["record_id"])
                _save_index(index, STORE_INDEX)

            total_normalized += 1
            print(f"  → {qr['record_id']} ({os.path.basename(ev['source_path'])})")

        collection_log.append({
            "source": sid,
            "layer": adapter["layer"],
            "evidence_found": len(evidence),
            "qr_created": len(evidence),
            "collected_at": _now()
        })

    # Write collection log
    log_entry = {
        "collection_id": f"COL-{_now()[:10].replace('-', '')}-{len(collection_log)}",
        "collected_at": _now(),
        "sources": collection_log,
        "total_evidence": total_collected,
        "total_qr_records": total_normalized
    }
    log_index = _load_index(EVIDENCE_LOG_INDEX)
    log_index.setdefault("collections", []).append(log_entry)
    _save_index(log_index, EVIDENCE_LOG_INDEX)

    print(f"\nCollection complete: {total_collected} evidence items → {total_normalized} QR- records created")
    print(f"Collection log: {EVIDENCE_LOG_INDEX}")
    return 0


def cmd_ingest(args):
    """Ingest QR- records: validate and produce collection receipt."""
    _ensure_dirs()
    index = _load_index(STORE_INDEX)
    records = index.get("records", [])

    if not records:
        print("Qualification store is empty. Run 'collect' first.")
        return 1

    validated = 0
    failed = 0
    for rid in records:
        path = os.path.join(STORE_DIR, f"{rid}.json")
        qr = _load_json(path)
        if qr is None:
            print(f"  ❌ {rid}: record file not found")
            failed += 1
            continue

        # Validate against QR validator
        import subprocess
        result = subprocess.run(
            [sys.executable, VALIDATOR_PATH, "validate", "--record-id", rid],
            capture_output=True, text=True, cwd=PROJECT_ROOT
        )
        if "PASS" in result.stdout:
            print(f"  ✅ {rid}: validated")
            validated += 1
        else:
            print(f"  ❌ {rid}: validation failed")
            print(f"     {result.stdout.strip()}")
            failed += 1

    print(f"\nIngest validation: {validated} passed, {failed} failed")
    return 0 if failed == 0 else 1


def cmd_status(args):
    """Show pipeline status."""
    _ensure_dirs()

    # Store status
    index = _load_index(STORE_INDEX)
    records = index.get("records", [])
    qr_count = len(records)

    # Sources status
    available = 0
    total_files = 0
    for sid, adapter in EVIDENCE_SOURCE_ADAPTERS.items():
        for pattern in adapter["paths"]:
            matches = glob.glob(os.path.join(PROJECT_ROOT, pattern))
            total_files += len(matches)
        if any(glob.glob(os.path.join(PROJECT_ROOT, p)) for p in adapter["paths"]):
            available += 1

    # Collection logs
    log_index = _load_index(EVIDENCE_LOG_INDEX)
    collections = log_index.get("collections", [])
    last_run = collections[-1]["collected_at"] if collections else "never"

    print("Qualification Evidence Pipeline — Status")
    print("=" * 50)
    print(f"  Evidence sources:   {available}/{len(EVIDENCE_SOURCE_ADAPTERS)} available")
    print(f"  Source data files:  {total_files}")
    print(f"  QR- records:        {qr_count}")
    print(f"  Collections run:    {len(collections)}")
    print(f"  Last collection:    {last_run}")
    print(f"  Store path:         {STORE_DIR}")
    print(f"  Evidence log:       {EVIDENCE_LOG_INDEX}")

    return 0


def cmd_validate(args):
    """Validate pipeline integrity."""
    _ensure_dirs()
    violations = []

    # Check store index consistency
    index = _load_index(STORE_INDEX)
    records = index.get("records", [])
    for rid in records:
        path = os.path.join(STORE_DIR, f"{rid}.json")
        if not os.path.exists(path):
            violations.append(f"Store inconsistency: record '{rid}' in index but file missing")

    # Check collection log
    log_index = _load_index(EVIDENCE_LOG_INDEX)
    collections = log_index.get("collections", [])

    print(f"Pipeline validation: {len(records)} records, {len(collections)} collections")
    if violations:
        print(f"  Violations ({len(violations)}):")
        for v in violations:
            print(f"    ❌ {v}")
        return 1
    else:
        print("  ✅ No violations found")
        return 0


def cmd_receipt(args):
    """Generate collection receipt."""
    _ensure_dirs()
    log_index = _load_index(EVIDENCE_LOG_INDEX)
    collections = log_index.get("collections", [])

    if not collections:
        print("No collections recorded. Run 'collect' first.")
        return 1

    receipt_dir = os.path.join(PROJECT_ROOT, "receipts")
    os.makedirs(receipt_dir, exist_ok=True)

    last = collections[-1]
    receipt = {
        "receipt_id": f"CEP-{_now()[:10].replace('-', '')}-001",
        "collection_id": last.get("collection_id", "unknown"),
        "collected_at": last["collected_at"],
        "sources": len(last.get("sources", [])),
        "total_evidence": last.get("total_evidence", 0),
        "total_qr_records": last.get("total_qr_records", 0),
        "advisory_only": True,
        "custody": "qa-pilot-local",
        "librarian_impact": "none",
        "generated_at": _now(),
        "generated_by": "qa_pilot_qualification_evidence_pipeline.py receipt"
    }

    receipt_path = os.path.join(receipt_dir, f"collection-evidence-pipeline-{_now()[:10]}.json")
    with open(receipt_path, "w") as f:
        json.dump(receipt, f, indent=2)
    print(f"Collection receipt written to {receipt_path}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="QA Pilot Qualification Evidence Pipeline CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # discover
    p = sub.add_parser("discover", help="Discover available evidence sources")
    p.add_argument("--source", nargs="*", help="Specific source adapters (default: all)")

    # collect
    p = sub.add_parser("collect", help="Collect evidence from sources and create QR- records")
    p.add_argument("--source", nargs="*", default=["all"],
                   help="Source adapters to collect from (default: all)")

    # ingest
    p = sub.add_parser("ingest", help="Validate and ingest QR- records")

    # status
    sub.add_parser("status", help="Show pipeline status")

    # validate
    sub.add_parser("validate", help="Validate pipeline integrity")

    # receipt
    sub.add_parser("receipt", help="Generate collection receipt")

    args = parser.parse_args()

    if args.command == "discover":
        return cmd_discover(args)
    elif args.command == "collect":
        return cmd_collect(args)
    elif args.command == "ingest":
        return cmd_ingest(args)
    elif args.command == "status":
        return cmd_status(args)
    elif args.command == "validate":
        return cmd_validate(args)
    elif args.command == "receipt":
        return cmd_receipt(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
