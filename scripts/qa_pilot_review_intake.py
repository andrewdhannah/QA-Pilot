#!/usr/bin/env python3
"""
QA Pilot Workbench Review Intake CLI.

Commands:
  intake-register   Register an export packet as a review intake record
  intake-read       Read a stored intake record by ID
  intake-list       List stored intake records
  intake-validate   Validate an intake record against schema + rules
  intake-triage     Mark an intake as triaged (advisory)
  intake-summary    Summarize all intake records
  summary-create    Create a review decision summary from an intake record
  summary-read      Read a stored decision summary by ID
  summary-list      List stored decision summaries
  summary-validate  Validate a decision summary against schema + DS rules
  summary-report    Produce a human-readable report from a summary
  summary-export    Export a summary as JSON

Authority boundaries:
  - Intake does not approve packet contents
  - Intake does not verify item correctness
  - Intake does not accept defects
  - Intake does not seal or close anything
  - Intake does not mutate source packets
  - Intake does not mutate Librarian
  - Summary does not approve intake
  - Summary does not verify evidence
  - Summary does not accept defects
  - Summary does not close items
  - Summary does not seal anything
  - Summary does not mutate intake or source packets
  - Summary does not mutate Librarian
"""

import argparse, json, os, sys, datetime, glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "review-intake")
STORE_INDEX = os.path.join(STORE_DIR, "intake-index.json")
PACKET_STORE_DIR = os.path.join(PROJECT_ROOT, "data", "export-packets")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-workbench-review-intake.schema.json")
SUMMARY_SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-workbench-review-decision-summary.schema.json")
SUMMARY_STORE_DIR = os.path.join(PROJECT_ROOT, "data", "review-decision-summaries")
SUMMARY_STORE_INDEX = os.path.join(SUMMARY_STORE_DIR, "summary-index.json")
WB_STORE_DIR = os.path.join(PROJECT_ROOT, "data", "workbench-items")

DISCLAIMER = "This review intake record is advisory-only. It does not approve packet contents, verify item correctness, accept defects, or close/seal/promote anything. Custody is qa-pilot-local. Librarian impact is none."
SUMMARY_DISCLAIMER = "This review decision summary is advisory-only. It does not approve the intake, verify evidence, accept defects, close items, or seal anything. It does not mutate intake records, source packets, or Librarian. Custody is qa-pilot-local. Librarian impact is none."

ADVISORY_NEXT_ACTIONS = [
    "review_needs_review_items",
    "review_deferred_items",
    "review_resolved_locally_items",
    "assign_severity_priority",
    "collect_evidence",
    "triage_intake",
    "create_review_packet",
    "export_for_owner_review",
    "no_action_required",
]

VALID_STATUSES = ["draft", "open", "triaged", "evidence_attached", "needs_review", "deferred", "resolved_locally"]
VALID_SEVERITIES = ["low", "medium", "high", "critical"]


def _now():
    return datetime.datetime.utcnow().isoformat() + "Z"


def _ensure_store():
    os.makedirs(STORE_DIR, exist_ok=True)
    if not os.path.exists(STORE_INDEX):
        with open(STORE_INDEX, "w") as f:
            json.dump({"records": [], "last_updated": _now()}, f, indent=2)


def _load_index():
    _ensure_store()
    with open(STORE_INDEX) as f:
        return json.load(f)


def _save_index(index):
    index["last_updated"] = _now()
    with open(STORE_INDEX, "w") as f:
        json.dump(index, f, indent=2)


def _load_packet(packet_id):
    path = os.path.join(PACKET_STORE_DIR, f"{packet_id}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def _load_intake(intake_id):
    path = os.path.join(STORE_DIR, f"{intake_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def _save_intake(record):
    path = os.path.join(STORE_DIR, f"{record['intake_id']}.json")
    with open(path, "w") as f:
        json.dump(record, f, indent=2)


def _validate_schema(record):
    try:
        import jsonschema
        with open(SCHEMA_PATH) as f:
            schema = json.load(f)
        try:
            jsonschema.validate(record, schema)
            return True, []
        except jsonschema.exceptions.ValidationError as e:
            return False, [f"schema violation: {e.message}"]
    except ImportError:
        return True, []


def _validate_intake_rules(record):
    violations = []
    
    # IR-1: advisory_only
    if not record.get("advisory_only", False):
        violations.append("IR-1: intake record advisory_only must be True")
    
    # IR-2: custody
    if record.get("custody", "") != "qa-pilot-local":
        violations.append("IR-2: intake record custody must be qa-pilot-local")
    
    # IR-3: librarian_impact
    if record.get("librarian_impact", "") != "none":
        violations.append("IR-3: intake record librarian_impact must be 'none'")
    
    # IR-4: authority_disclaimer must match
    if record.get("authority_disclaimer", "") != DISCLAIMER:
        violations.append("IR-4: intake record authority_disclaimer mismatch")
    
    # IR-5: source_packet_id must start with XPK-
    pid = record.get("source_packet_id", "")
    if not pid.startswith("XPK-"):
        violations.append("IR-5: source_packet_id must start with XPK-")
    
    # IR-6: included_item_ids must be present
    if not record.get("included_item_ids"):
        violations.append("IR-6: included_item_ids is empty")
    
    # IR-7: no registry/RCR/SRS fields
    for key in record:
        kl = key.lower()
        if any(kw in kl for kw in ["registry", "rcr_", "srs_"]):
            violations.append(f"IR-7: intake record has registry/RCR/SRS field ('{key}')")
    
    return violations


def cmd_register(args):
    """Register an export packet as a review intake record."""
    _ensure_store()
    
    # Load source packet
    packet = None
    packet_id = None
    packet_path = None
    
    if args.packet_id:
        packet_id = args.packet_id
        packet = _load_packet(packet_id)
        if packet is None:
            print(f"ERROR: Packet {packet_id} not found in export packet store."); sys.exit(1)
    elif args.packet_file:
        packet_path = args.packet_file
        with open(packet_path) as f:
            packet = json.load(f)
        packet_id = packet.get("packet_id", "unknown")
    else:
        print("ERROR: Provide either --packet-id or --packet-file."); sys.exit(1)
    
    # Validate source packet basics
    if packet.get("advisory_only") is not True:
        print("ERROR: Source packet must be advisory_only=True"); sys.exit(1)
    if packet.get("custody", "") != "qa-pilot-local":
        print("ERROR: Source packet custody must be qa-pilot-local"); sys.exit(1)
    
    # Build intake record
    included_items = packet.get("included_items", [])
    item_ids = [i.get("qa_item_id", "?") for i in included_items]
    
    intake_id = args.intake_id or f"IR-REVIEW-{packet_id.split('-')[-1]}"
    
    record = {
        "intake_id": intake_id,
        "source_packet_id": packet_id,
        "source_project": args.source_project or "qa-pilot",
        "intake_status": "received",
        "received_at": _now(),
        "included_item_ids": item_ids,
        "item_count": len(item_ids),
        "evidence_summary": packet.get("evidence_links_aggregate", {"total_links": 0, "by_type": {}}),
        "lifecycle_summary": packet.get("lifecycle_summary", {"total_transitions": 0, "by_status": {}}),
        "owner_decision_state": "pending",
        "authority_disclaimer": DISCLAIMER,
        "custody": "qa-pilot-local",
        "advisory_only": True,
        "librarian_impact": "none"
    }
    
    # Validate
    schema_ok, schema_issues = _validate_schema(record)
    rule_issues = _validate_intake_rules(record)
    if schema_issues or rule_issues:
        for i in schema_issues + rule_issues:
            print(f"VALIDATION: {i}")
    
    # Check for duplicate
    index = _load_index()
    if intake_id in index.get("records", []):
        print(f"ERROR: Intake {intake_id} already exists"); sys.exit(1)
    
    _save_intake(record)
    index.setdefault("records", []).append(intake_id)
    _save_index(index)
    
    print(f"Intake registered: {intake_id}")
    print(f"  Source packet: {packet_id}")
    print(f"  Items: {record['item_count']}")
    print(f"  Status: {record['intake_status']}")
    print(f"  Advisory: True")


def cmd_read(args):
    """Read a stored intake record by ID."""
    record = _load_intake(args.intake_id)
    if record is None: print(f"ERROR: Intake {args.intake_id} not found"); sys.exit(1)
    print(json.dumps(record, indent=2))


def cmd_list(args):
    """List stored intake records."""
    index = _load_index()
    records = index.get("records", [])
    if not records:
        print("No intake records."); return
    
    print(f"Review Intake Records ({len(records)}):")
    print("=" * 100)
    for rid in records:
        rec = _load_intake(rid)
        if rec is None: print(f"  {rid}: MISSING"); continue
        src = rec.get("source_packet_id", "?")
        status = rec.get("intake_status", "?")
        count = rec.get("item_count", 0)
        ts = rec.get("received_at", "?")[:19]
        print(f"  {rid:24s} [{status:10s}] {count:2d} items  src={src:24s} [{ts}]")


def cmd_validate(args):
    """Validate an intake record against schema + rules."""
    if args.intake_id:
        record = _load_intake(args.intake_id)
        if record is None: print(f"ERROR: Intake {args.intake_id} not found"); sys.exit(1)
    else:
        with open(args.intake_file) as f:
            record = json.load(f)
    
    schema_ok, schema_issues = _validate_schema(record)
    rule_issues = _validate_intake_rules(record)
    all_issues = schema_issues + rule_issues
    
    rid = record.get("intake_id", "?")
    if not all_issues:
        print(f"VALID: {rid}"); print("ALL CHECKS PASS")
    else:
        print(f"INVALID: {rid}")
        for i in all_issues: print(f"  {i}")
        sys.exit(1)


def cmd_triage(args):
    """Mark an intake as triaged (advisory)."""
    record = _load_intake(args.intake_id)
    if record is None: print(f"ERROR: Intake {args.intake_id} not found"); sys.exit(1)
    
    if record["intake_status"] not in ("received", "validated"):
        print(f"ERROR: Intake {args.intake_id} is in status '{record['intake_status']}' — can only triage received/validated records")
        sys.exit(1)
    
    record["intake_status"] = "triaged"
    _save_intake(record)
    print(f"Triaged: {args.intake_id}")
    print(f"  Note: Triaging does not imply approval or defect acceptance.")


def cmd_summary(args):
    """Summarize all intake records."""
    index = _load_index()
    records = index.get("records", [])
    
    if not records:
        print("No intake records."); return
    
    by_status = {}
    total_items = 0
    for rid in records:
        rec = _load_intake(rid)
        if rec is None: continue
        s = rec.get("intake_status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1
        total_items += rec.get("item_count", 0)
    
    print(f"Review Intake Summary")
    print("=" * 60)
    print(f"  Total intakes:    {len(records)}")
    print(f"  Total items:      {total_items}")
    print(f"  By status:")
    for s in ["received", "validated", "triaged", "in_review", "completed", "deferred"]:
        c = by_status.get(s, 0)
        if c > 0: print(f"    {s:12s}: {c}")
    print(f"  Advisory-only:    True")
    print(f"  Custody:          qa-pilot-local")
    print(f"  Authority note:   Intake records are advisory-only.")


# ── Decision Summary Commands ──────────────────────────────────────────────


def _ensure_summary_store():
    os.makedirs(SUMMARY_STORE_DIR, exist_ok=True)
    if not os.path.exists(SUMMARY_STORE_INDEX):
        with open(SUMMARY_STORE_INDEX, "w") as f:
            json.dump({"records": [], "last_updated": _now()}, f, indent=2)


def _load_summary_index():
    _ensure_summary_store()
    with open(SUMMARY_STORE_INDEX) as f:
        return json.load(f)


def _save_summary_index(index):
    index["last_updated"] = _now()
    with open(SUMMARY_STORE_INDEX, "w") as f:
        json.dump(index, f, indent=2)


def _load_summary(summary_id):
    path = os.path.join(SUMMARY_STORE_DIR, f"{summary_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def _save_summary(record):
    path = os.path.join(SUMMARY_STORE_DIR, f"{record['summary_id']}.json")
    with open(path, "w") as f:
        json.dump(record, f, indent=2)


def _load_wb_item(item_id):
    """Load a workbench item by ID from the workbench store."""
    path = os.path.join(WB_STORE_DIR, f"{item_id}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def _compute_status_counts(items):
    counts = {s: 0 for s in VALID_STATUSES}
    for item in items:
        s = item.get("status", "unknown")
        if s in counts:
            counts[s] += 1
    return {k: v for k, v in counts.items() if v > 0}


def _compute_severity_counts(items):
    counts = {s: 0 for s in VALID_SEVERITIES}
    for item in items:
        s = item.get("severity", "unknown")
        if s in counts:
            counts[s] += 1
    return {k: v for k, v in counts.items() if v > 0}


def _compute_evidence_summary(items):
    total = 0
    by_type = {}
    found = 0
    missing = 0
    stale = 0
    for item in items:
        links = item.get("evidence_links", [])
        total += len(links)
        for link in links:
            etype = link.get("evidence_type", "unknown")
            by_type[etype] = by_type.get(etype, 0) + 1
        # count evidence_refs without links as missing
        refs = item.get("evidence_refs", [])
        missing += max(0, len(refs) - len(links))
    return {
        "total_links": total,
        "by_type": by_type,
        "found": total,
        "missing": missing,
        "stale": stale,
    }


def _compute_lifecycle_summary(items):
    total = 0
    by_status = {}
    for item in items:
        history = item.get("lifecycle_history", [])
        total += len(history)
        for entry in history:
            s = entry.get("to_status", "unknown")
            by_status[s] = by_status.get(s, 0) + 1
    return {"total_transitions": total, "by_status": by_status}


def _categorize_items(items):
    unresolved = []
    needs_review = []
    deferred = []
    resolved = []
    for item in items:
        entry = {"qa_item_id": item.get("qa_item_id", "?"), "status": item.get("status", "?"), "severity": item.get("severity", "?")}
        s = item.get("status", "")
        if s in ("draft", "open", "triaged", "evidence_attached"):
            unresolved.append(entry)
        if s == "needs_review":
            needs_review.append(entry)
        if s == "deferred":
            deferred.append(entry)
        if s == "resolved_locally":
            resolved.append(entry)
    return unresolved, needs_review, deferred, resolved


def _determine_advisory_actions(items):
    """Derive advisory next actions from item analysis."""
    actions = set()
    has_unresolved = False
    has_needs_review = False
    has_deferred = False
    has_resolved = False
    needs_evidence = False
    needs_triage = False

    for item in items:
        s = item.get("status", "")
        if s in ("draft", "open"):
            needs_triage = True
            has_unresolved = True
        elif s == "triaged" and not item.get("evidence_links"):
            needs_evidence = True
            has_unresolved = True
        elif s == "evidence_attached":
            has_unresolved = True
        elif s == "needs_review":
            has_needs_review = True
        elif s == "deferred":
            has_deferred = True
        elif s == "resolved_locally":
            has_resolved = True

    if has_needs_review:
        actions.add("review_needs_review_items")
    if has_deferred:
        actions.add("review_deferred_items")
    if has_resolved:
        actions.add("review_resolved_locally_items")
    if needs_triage:
        actions.add("triage_intake")
    if needs_evidence:
        actions.add("collect_evidence")
    if has_unresolved and not has_needs_review and not needs_triage:
        actions.add("create_review_packet")
    if has_needs_review or has_deferred:
        actions.add("export_for_owner_review")
    if not actions:
        actions.add("no_action_required")

    return sorted(actions)


def _validate_summary_schema(record):
    try:
        import jsonschema
        with open(SUMMARY_SCHEMA_PATH) as f:
            schema = json.load(f)
        try:
            jsonschema.validate(record, schema)
            return True, []
        except jsonschema.exceptions.ValidationError as e:
            return False, [f"schema violation: {e.message}"]
    except ImportError:
        return True, []


def _validate_summary_rules(record):
    """Validate a decision summary against DS rules."""
    violations = []

    # DS-1: summary must be read-only (no status changes, no seal, no approval)
    if record.get("intake_status") is not None:
        violations.append("DS-1: summary must not carry intake status (read-only)")
    if record.get("sealed", False):
        violations.append("DS-1: summary must not claim seal state")

    # DS-2: summary must be advisory-only
    if not record.get("advisory_only", False):
        violations.append("DS-2: summary advisory_only must be True")

    # DS-3: summary must preserve intake/source packet identity
    iid = record.get("intake_id", "")
    if not iid.startswith("IR-"):
        violations.append("DS-3: intake_id must start with IR-")
    pid = record.get("source_packet_id", "")
    if not pid.startswith("XPK-"):
        violations.append("DS-3: source_packet_id must start with XPK-")

    # DS-4: summary counts must be consistent
    sc = record.get("status_counts", {})
    total_from_status = sum(sc.values()) if sc else 0
    item_count = record.get("item_count", 0)
    if total_from_status != item_count:
        violations.append(f"DS-4: status_counts sum ({total_from_status}) != item_count ({item_count})")

    # DS-5: advisory next actions must be bounded
    actions = record.get("advisory_next_actions", [])
    for a in actions:
        if a not in ADVISORY_NEXT_ACTIONS:
            violations.append(f"DS-5: unbounded advisory next action '{a}'")

    # DS-6: summary cannot claim approval, verification, seal, closure, or defect acceptance
    text = json.dumps(record).lower()
    for kw in ["approved", "verified", "sealed", "closed", "defect accepted", "accepted"]:
        if kw in text and kw not in ["advisory_only"]:
            # Only flag if not in the disclaimer or standard fields
            if record.get("authority_disclaimer", "").lower().find(kw) < 0:
                violations.append(f"DS-6: summary contains forbidden term '{kw}'")

    # DS-7: summary cannot include lifecycle/intake status mutation fields
    if record.get("new_status") is not None:
        violations.append("DS-7: summary must not carry new_status (would mutate lifecycle)")
    if record.get("new_intake_status") is not None:
        violations.append("DS-7: summary must not carry new_intake_status (would mutate intake)")

    # DS-8: summary cannot include Librarian paths or impact
    if record.get("librarian_impact", "") != "none":
        violations.append("DS-8: summary librarian_impact must be 'none'")
    if record.get("custody", "") != "qa-pilot-local":
        violations.append("DS-8: summary custody must be qa-pilot-local")
    for kw in ["librarian/", "/librarian", "active/librarian"]:
        if kw in json.dumps(record):
            violations.append(f"DS-8: summary contains Librarian path reference ('{kw}')")

    return violations


def cmd_summary_create(args):
    """Create a review decision summary from an intake record."""
    _ensure_summary_store()

    # Load intake record
    record = _load_intake(args.intake_id)
    if record is None:
        print(f"ERROR: Intake {args.intake_id} not found"); sys.exit(1)

    # Load items from workbench store for each included_item_id
    item_ids = record.get("included_item_ids", [])
    items = []
    for iid in item_ids:
        item = _load_wb_item(iid)
        if item is not None:
            items.append(item)
        else:
            # Create a minimal placeholder
            items.append({"qa_item_id": iid, "status": "open", "severity": "info"})

    # Compute summary fields
    status_counts = _compute_status_counts(items)
    severity_counts = _compute_severity_counts(items)
    evidence_summary = _compute_evidence_summary(items)
    lifecycle_summary = _compute_lifecycle_summary(items)
    unresolved, needs_review, deferred, resolved = _categorize_items(items)
    advisory_actions = _determine_advisory_actions(items)

    summary_id = args.summary_id or f"DS-REVIEW-{record['intake_id'].split('-')[-1]}"

    summary = {
        "summary_id": summary_id,
        "intake_id": record["intake_id"],
        "source_packet_id": record["source_packet_id"],
        "item_count": record.get("item_count", len(item_ids)),
        "status_counts": status_counts,
        "severity_counts": severity_counts,
        "evidence_summary": evidence_summary,
        "lifecycle_summary": lifecycle_summary,
        "unresolved_items": unresolved,
        "needs_review_items": needs_review,
        "deferred_items": deferred,
        "resolved_locally_items": resolved,
        "advisory_next_actions": advisory_actions,
        "authority_disclaimer": SUMMARY_DISCLAIMER,
        "custody": "qa-pilot-local",
        "advisory_only": True,
        "librarian_impact": "none",
    }

    # Validate
    schema_ok, schema_issues = _validate_summary_schema(summary)
    rule_issues = _validate_summary_rules(summary)
    if schema_issues or rule_issues:
        for i in schema_issues + rule_issues:
            print(f"VALIDATION: {i}")
        if args.strict:
            print("ERROR: Strict mode – rejecting invalid summary"); sys.exit(1)

    # Check for duplicate
    sindex = _load_summary_index()
    if summary_id in sindex.get("records", []):
        print(f"ERROR: Summary {summary_id} already exists"); sys.exit(1)

    _save_summary(summary)
    sindex.setdefault("records", []).append(summary_id)
    _save_summary_index(sindex)

    print(f"Summary created: {summary_id}")
    print(f"  Intake:         {summary['intake_id']}")
    print(f"  Source packet:  {summary['source_packet_id']}")
    print(f"  Items:          {summary['item_count']}")
    print(f"  Statuses:       {json.dumps(status_counts)}")
    print(f"  Advisory next:  {advisory_actions}")
    print(f"  Advisory-only:  True")


def cmd_summary_read(args):
    """Read a stored summary by ID."""
    summary = _load_summary(args.summary_id)
    if summary is None: print(f"ERROR: Summary {args.summary_id} not found"); sys.exit(1)
    print(json.dumps(summary, indent=2))


def cmd_summary_list(args):
    """List stored summaries."""
    sindex = _load_summary_index()
    records = sindex.get("records", [])
    if not records:
        print("No decision summaries."); return

    print(f"Review Decision Summaries ({len(records)}):")
    print("=" * 100)
    for sid in records:
        s = _load_summary(sid)
        if s is None: print(f"  {sid}: MISSING"); continue
        intake = s.get("intake_id", "?")
        count = s.get("item_count", 0)
        actions = ", ".join(s.get("advisory_next_actions", []))
        print(f"  {sid:28s} intake={intake:20s} items={count:2d}  next={actions}")


def cmd_summary_validate(args):
    """Validate a summary against schema + DS rules."""
    if args.summary_id:
        summary = _load_summary(args.summary_id)
        if summary is None: print(f"ERROR: Summary {args.summary_id} not found"); sys.exit(1)
    else:
        with open(args.summary_file) as f:
            summary = json.load(f)

    schema_ok, schema_issues = _validate_summary_schema(summary)
    rule_issues = _validate_summary_rules(summary)
    all_issues = schema_issues + rule_issues

    sid = summary.get("summary_id", "?")
    if not all_issues:
        print(f"VALID: {sid}"); print("ALL CHECKS PASS")
    else:
        print(f"INVALID: {sid}")
        for i in all_issues: print(f"  {i}")
        sys.exit(1)


def cmd_summary_report(args):
    """Produce a human-readable report from a summary."""
    summary = _load_summary(args.summary_id)
    if summary is None: print(f"ERROR: Summary {args.summary_id} not found"); sys.exit(1)

    sid = summary["summary_id"]
    intake = summary["intake_id"]
    packet = summary["source_packet_id"]
    count = summary["item_count"]
    sc = summary.get("status_counts", {})
    sev = summary.get("severity_counts", {})
    ev = summary.get("evidence_summary", {})
    lc = summary.get("lifecycle_summary", {})
    unresolved = summary.get("unresolved_items", [])
    needs_review = summary.get("needs_review_items", [])
    deferred = summary.get("deferred_items", [])
    resolved = summary.get("resolved_locally_items", [])
    actions = summary.get("advisory_next_actions", [])

    print(f"{'=' * 72}")
    print(f"  Review Decision Summary: {sid}")
    print(f"{'=' * 72}")
    print(f"  Intake:            {intake}")
    print(f"  Source packet:     {packet}")
    print(f"  Total items:       {count}")
    print()
    print(f"  Status breakdown:")
    for s in VALID_STATUSES:
        c = sc.get(s, 0)
        if c > 0: print(f"    {s:22s}: {c}")
    print()
    print(f"  Severity breakdown:")
    for s in VALID_SEVERITIES:
        c = sev.get(s, 0)
        if c > 0: print(f"    {s:22s}: {c}")
    print()
    print(f"  Evidence:          {ev.get('total_links', 0)} total links, {ev.get('found', 0)} found, {ev.get('missing', 0)} missing")
    print(f"  Lifecycle:         {lc.get('total_transitions', 0)} total transitions")
    print()
    print(f"  Unresolved items:  {len(unresolved)}")
    for u in unresolved:
        print(f"    - {u.get('qa_item_id','?'):20s} [{u.get('status','?'):20s}] severity={u.get('severity','?')}")
    print(f"  Needs review:      {len(needs_review)}")
    for n in needs_review:
        print(f"    - {n.get('qa_item_id','?'):20s} [{n.get('status','?'):20s}] severity={n.get('severity','?')}")
    print(f"  Deferred:          {len(deferred)}")
    for d in deferred:
        print(f"    - {d.get('qa_item_id','?'):20s} [{d.get('status','?'):20s}] severity={d.get('severity','?')}")
    print(f"  Resolved locally:  {len(resolved)}")
    for r in resolved:
        print(f"    - {r.get('qa_item_id','?'):20s} [{r.get('status','?'):20s}] severity={r.get('severity','?')}")
    print()
    print(f"  Advisory next actions:")
    for a in actions:
        print(f"    -> {a}")
    print()
    print(f"  {SUMMARY_DISCLAIMER}")


def cmd_summary_export(args):
    """Export a summary as JSON to stdout or file."""
    summary = _load_summary(args.summary_id)
    if summary is None:
        print(f"ERROR: Summary {args.summary_id} not found"); sys.exit(1)

    output = json.dumps(summary, indent=2)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Exported: {args.summary_id} -> {args.output}")
    else:
        print(output)


def main():
    parser = argparse.ArgumentParser(description="QA Pilot Review Intake CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    
    p_reg = sub.add_parser("intake-register")
    p_reg.add_argument("--packet-id"); p_reg.add_argument("--packet-file"); p_reg.add_argument("--intake-id"); p_reg.add_argument("--source-project")
    p_reg.set_defaults(func=cmd_register)
    
    p_rd = sub.add_parser("intake-read"); p_rd.add_argument("intake_id"); p_rd.set_defaults(func=cmd_read)
    p_li = sub.add_parser("intake-list"); p_li.set_defaults(func=cmd_list)
    p_va = sub.add_parser("intake-validate"); p_va.add_argument("intake_id", nargs="?"); p_va.add_argument("--intake-file"); p_va.set_defaults(func=cmd_validate)
    p_tr = sub.add_parser("intake-triage"); p_tr.add_argument("intake_id"); p_tr.set_defaults(func=cmd_triage)
    p_su = sub.add_parser("intake-summary"); p_su.set_defaults(func=cmd_summary)
    
    # Decision summary commands
    p_sc = sub.add_parser("summary-create"); p_sc.add_argument("intake_id"); p_sc.add_argument("--summary-id"); p_sc.add_argument("--strict", action="store_true"); p_sc.set_defaults(func=cmd_summary_create)
    p_sr = sub.add_parser("summary-read"); p_sr.add_argument("summary_id"); p_sr.set_defaults(func=cmd_summary_read)
    p_sl = sub.add_parser("summary-list"); p_sl.set_defaults(func=cmd_summary_list)
    p_sv = sub.add_parser("summary-validate"); p_sv.add_argument("summary_id", nargs="?"); p_sv.add_argument("--summary-file"); p_sv.set_defaults(func=cmd_summary_validate)
    p_srp = sub.add_parser("summary-report"); p_srp.add_argument("summary_id"); p_srp.set_defaults(func=cmd_summary_report)
    p_se = sub.add_parser("summary-export"); p_se.add_argument("summary_id"); p_se.add_argument("--output"); p_se.set_defaults(func=cmd_summary_export)
    
    args = parser.parse_args(); args.func(args)


if __name__ == "__main__":
    main()
