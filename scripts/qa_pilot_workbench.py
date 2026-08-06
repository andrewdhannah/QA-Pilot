#!/usr/bin/env python3
"""
QA Pilot Workbench — bounded QA workbench capability layer.

CLI operations:
  create            Create a new QA workbench item
  list              List QA workbench items with optional filters
  read              Read a single QA workbench item by ID
  validate          Validate a QA workbench item against schema + business rules
  triage            Mark a QA item as triaged (does not imply Owner approval)
  attach            Attach a structured evidence link to an existing QA item
  detach            Detach an evidence link from a QA item
  list-refs         List evidence links attached to a QA item
  validate-refs     Validate all evidence links on an item
  summarize         Summarize evidence posture for a QA item
  status            Show current status and lifecycle summary
  transition        Transition item to a new status (governed transitions)
  history           Show append-only lifecycle history
  reopen            Reopen a resolved item (requires reason)
  validate-transition  Check whether a transition would be allowed

Authority boundaries:
  - All states are advisory-local — no status implies Owner approval, defect
    acceptance, verification, or seal authority.
  - resolved_locally does not mean Owner-approved
  - triaged does not mean defect accepted
  - evidence_attached does not mean verified
  - needs_review does not force Owner action
  - No status transition seals, approves, verifies, or mutates governance state
  - QA item creation does not imply defect acceptance
  - Evidence attachment does not prove defect validity
  - No auto-seal, no ledger mutation, no Librarian mutation

Usage:
  python3 scripts/qa_pilot_workbench.py create <json-file>
  python3 scripts/qa_pilot_workbench.py list [--status S] [--severity S] [--source S]
  python3 scripts/qa_pilot_workbench.py read <qa-item-id>
  python3 scripts/qa_pilot_workbench.py validate [<json-file>]
  python3 scripts/qa_pilot_workbench.py triage <qa-item-id> [--reason REASON]
  python3 scripts/qa_pilot_workbench.py attach <qa-item-id> <evidence-link-json>
  python3 scripts/qa_pilot_workbench.py detach <qa-item-id> <evidence-link-id>
  python3 scripts/qa_pilot_workbench.py list-refs <qa-item-id>
  python3 scripts/qa_pilot_workbench.py validate-refs <qa-item-id>
  python3 scripts/qa_pilot_workbench.py summarize <qa-item-id>
  python3 scripts/qa_pilot_workbench.py status <qa-item-id>
  python3 scripts/qa_pilot_workbench.py transition <qa-item-id> <to-status> --reason REASON
  python3 scripts/qa_pilot_workbench.py history <qa-item-id>
  python3 scripts/qa_pilot_workbench.py reopen <qa-item-id> --reason REASON
  python3 scripts/qa_pilot_workbench.py validate-transition <qa-item-id> <to-status>
"""

import argparse
import json
import os
import sys
import datetime
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STORE_DIR = os.path.join(PROJECT_ROOT, "data", "workbench-items")
STORE_INDEX = os.path.join(STORE_DIR, "workbench-index.json")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-workbench-item.schema.json")
EVIDENCE_LINK_SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "schemas", "qa-workbench-evidence-link.schema.json")

VALID_STATUSES = ["draft", "open", "triaged", "evidence_attached", "needs_review", "deferred", "resolved_locally"]

# Allowed transitions: {from_status: [to_status, ...]}
ALLOWED_TRANSITIONS = {
    "draft": ["open"],
    "open": ["triaged"],
    "triaged": ["evidence_attached"],
    "evidence_attached": ["needs_review"],
    "needs_review": ["deferred", "resolved_locally"],
    "deferred": ["open"],
    "resolved_locally": ["open"],  # reopen requires reason
}


def _ensure_store():
    os.makedirs(STORE_DIR, exist_ok=True)
    if not os.path.exists(STORE_INDEX):
        with open(STORE_INDEX, "w") as f:
            json.dump({"items": [], "last_updated": datetime.datetime.utcnow().isoformat() + "Z"}, f, indent=2)


def _load_index():
    _ensure_store()
    with open(STORE_INDEX) as f:
        return json.load(f)


def _save_index(index):
    index["last_updated"] = datetime.datetime.utcnow().isoformat() + "Z"
    with open(STORE_INDEX, "w") as f:
        json.dump(index, f, indent=2)


def _load_item(item_id):
    path = os.path.join(STORE_DIR, f"{item_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def _save_item(item):
    path = os.path.join(STORE_DIR, f"{item['qa_item_id']}.json")
    with open(path, "w") as f:
        json.dump(item, f, indent=2)


def _now():
    return datetime.datetime.utcnow().isoformat() + "Z"


def _validate_schema(item, schema_path=None):
    try:
        import jsonschema
    except ImportError:
        return True, "jsonschema not available"
    with open(schema_path or SCHEMA_PATH) as f:
        schema = json.load(f)
    try:
        jsonschema.validate(item, schema)
        return True, "schema valid"
    except jsonschema.exceptions.ValidationError as e:
        return False, f"schema violation: {e.message}"


def _validate_evidence_link_schema(link):
    return _validate_schema(link, EVIDENCE_LINK_SCHEMA_PATH)


def _add_lifecycle_entry(item, from_status, to_status, reason, actor=None, evidence_refs=None):
    """Append a lifecycle history entry to an item."""
    entry = {
        "from_status": from_status,
        "to_status": to_status,
        "transition_reason": reason,
        "timestamp": _now(),
        "advisory_only": True,
    }
    if actor:
        entry["actor"] = actor
    if evidence_refs:
        entry["evidence_refs"] = evidence_refs
    item.setdefault("lifecycle_history", []).append(entry)
    item["status"] = to_status
    item["updated_at"] = _now()


def _check_transition_allowed(item, to_status):
    """Check if a transition is allowed. Returns (allowed, message)."""
    from_status = item.get("status", "draft")
    
    if to_status not in VALID_STATUSES:
        return False, f"Invalid target status '{to_status}'. Valid: {', '.join(VALID_STATUSES)}"
    
    allowed = ALLOWED_TRANSITIONS.get(from_status, [])
    if to_status not in allowed:
        return False, f"Transition '{from_status}' → '{to_status}' is not allowed. Allowed: {', '.join(allowed) if allowed else 'none'}"
    
    return True, None


def _validate_business_rules(item):
    """Validate business rules for QA workbench items."""
    violations = []
    
    # WB-1: advisory_only must be True
    if not item.get("advisory_only", False):
        violations.append("WB-1: advisory_only must be True")
    
    # WB-2: custody
    if item.get("custody", "") != "qa-pilot-local":
        violations.append("WB-2: custody must be qa-pilot-local")
    
    # WB-3: librarian_impact
    if item.get("librarian_impact", "") != "none":
        violations.append("WB-3: librarian_impact must be 'none'")
    
    # WB-5: authority claims
    authority_patterns = [
        "this item is approved", "this item is sealed",
        "claims approval authority", "claims seal authority",
        "seal authority over", "approved and verified",
        "this item has authority",
    ]
    for key in ["title", "description"]:
        val = str(item.get(key, "")).lower()
        for pattern in authority_patterns:
            if pattern in val:
                violations.append(f"WB-5: item {key} must not claim authority ('{pattern}')")
    
    # WB-7: accepted requires ref
    if item.get("owner_decision_state") == "accepted" and not item.get("owner_decision_ref"):
        violations.append("WB-7: accepted owner_decision_state requires an owner_decision_ref")
    
    # WB-8: no registry/RCR/SRS fields
    for key in item:
        kl = key.lower()
        if any(kw in kl for kw in ["registry", "rcr_", "srs_"]):
            violations.append(f"WB-8: item must not contain registry/RCR/SRS fields ({key})")
    
    # Evidence link rules
    for link in item.get("evidence_links", []):
        lid = link.get("evidence_link_id", "?")
        link_ok, link_msg = _validate_evidence_link_schema(link)
        if not link_ok:
            violations.append(f"WB-9: evidence_link '{lid}': {link_msg}")
        reason = str(link.get("attachment_reason", "")).lower()
        for p in ["proves defect", "confirms defect", "is approved for", "confer seal", "has authority"]:
            if p in reason:
                violations.append(f"WB-10: evidence_link '{lid}' reason claims authority ('{p}')")
        ref = link.get("evidence_ref", "")
        if ref.startswith("LIB-") or "/librarian/" in str(link.get("source_path", "")).lower():
            violations.append(f"WB-11: evidence_link '{lid}' must not reference Librarian paths")
        for lk in link:
            lkl = lk.lower()
            if any(kw in lkl for kw in ["registry", "rcr_", "srs_"]):
                violations.append(f"WB-12: evidence_link '{lid}' contains registry/RCR/SRS field ('{lk}')")
    
    # WL-1: lifecycle_history entries must have valid from/to statuses
    for entry in item.get("lifecycle_history", []):
        fs = entry.get("from_status", "")
        ts = entry.get("to_status", "")
        if fs not in VALID_STATUSES and fs != "__init__":
            violations.append(f"WL-1: lifecycle entry has invalid from_status '{fs}'")
        if ts not in VALID_STATUSES:
            violations.append(f"WL-1: lifecycle entry has invalid to_status '{ts}'")
    
    # WL-2: advisory_only on lifecycle entries
    for entry in item.get("lifecycle_history", []):
        if not entry.get("advisory_only", False):
            violations.append(f"WL-2: lifecycle entry advisory_only must be True")
    
    # WL-3: transition_reason required
    for entry in item.get("lifecycle_history", []):
        if not entry.get("transition_reason") or len(entry.get("transition_reason", "")) < 3:
            violations.append(f"WL-3: lifecycle entry missing transition_reason")
    
    # WL-4: authority claims in transition reasons
    for entry in item.get("lifecycle_history", []):
        reason = str(entry.get("transition_reason", "")).lower()
        for p in ["approved", "verified", "sealed", "defect accepted"]:
            if p in reason:
                violations.append(f"WL-4: lifecycle reason claims '{p}' authority")
    
    # WL-5: resolved_locally must not claim Owner approval
    if item.get("status") == "resolved_locally":
        for entry in item.get("lifecycle_history", []):
            if entry.get("to_status") == "resolved_locally":
                reason = str(entry.get("transition_reason", "")).lower()
                if "owner" in reason and ("accept" in reason or "approv" in reason):
                    violations.append("WL-5: resolved_locally reason must not claim Owner approval")
    
    # WL-6: lifecycle_history must maintain chronological order
    # (Soft check — assumes append-only)
    
    return violations


def _validate_lifecycle_rules(item):
    """Validate lifecycle-specific business rules."""
    violations = []
    history = item.get("lifecycle_history", [])
    
    # Check that the current status matches the last entry
    if history:
        last_entry = history[-1]
        if last_entry.get("to_status") != item.get("status"):
            violations.append(f"WL-6: final history entry status '{last_entry.get('to_status')}' != item status '{item.get('status')}'")
    
    # Check transition order validity within history
    for i, entry in enumerate(history):
        if i == 0 and entry.get("from_status") == "__init__":
            continue  # creation entry
        if i == 0:
            continue
        prev = history[i-1]
        expected_from = prev.get("to_status")
        actual_from = entry.get("from_status")
        if expected_from != actual_from:
            violations.append(f"WL-7: lifecycle history gap at entry {i}: expected from_status '{expected_from}', got '{actual_from}'")
    
    return violations


# ─── Command implementations ────────────────────────────────────────────────

def cmd_create(args):
    _ensure_store()
    with open(args.json_file) as f:
        item = json.load(f)
    
    now = _now()
    item.setdefault("created_at", now)
    item.setdefault("updated_at", now)
    item.setdefault("advisory_only", True)
    item.setdefault("custody", "qa-pilot-local")
    item.setdefault("librarian_impact", "none")
    item.setdefault("owner_decision_state", "pending")
    item.setdefault("evidence_refs", [])
    item.setdefault("validator_refs", [])
    item.setdefault("evidence_links", [])
    item.setdefault("lifecycle_history", [])
    
    # Add initial lifecycle entry if item has a status and no history
    status = item.get("status", "draft")
    if not item["lifecycle_history"] and status in VALID_STATUSES:
        _add_lifecycle_entry(item, "__init__", status, "Item created", actor="CLI")
    
    schema_ok, schema_msg = _validate_schema(item)
    if not schema_ok:
        print(f"VALIDATION FAILED: {schema_msg}"); sys.exit(1)
    
    violations = _validate_business_rules(item)
    if violations:
        for v in violations: print(f"VALIDATION FAILED: {v}")
        sys.exit(1)
    
    index = _load_index()
    if item["qa_item_id"] in index.get("items", []):
        print(f"ERROR: Item {item['qa_item_id']} already exists"); sys.exit(1)
    
    _save_item(item)
    if item["qa_item_id"] not in index.get("items", []):
        index.setdefault("items", []).append(item["qa_item_id"])
    _save_index(index)
    
    print(f"Created QA item: {item['qa_item_id']}")
    print(f"  Title: {item['title']}")
    print(f"  Status: {item['status']}")
    print(f"  Advisory: {item['advisory_only']}")


def _query_items(index_items, args):
    """Filter items by args. Returns list of item dicts."""
    result = []
    for item_id in index_items:
        item = _load_item(item_id)
        if item is None: continue
        if getattr(args, 'status', None) and item.get("status") != args.status: continue
        if getattr(args, 'severity', None) and item.get("severity") != args.severity: continue
        if getattr(args, 'category', None) and item.get("category") != args.category: continue
        if getattr(args, 'source', None) and item.get("source") != args.source: continue
        if getattr(args, 'evidence_type', None):
            etypes = [l.get("evidence_type", "") for l in item.get("evidence_links", [])]
            if args.evidence_type not in etypes: continue
        if getattr(args, 'has_evidence', False) and len(item.get("evidence_links", [])) == 0: continue
        if getattr(args, 'needs_review', False) and item.get("status") != "needs_review": continue
        if getattr(args, 'deferred', False) and item.get("status") != "deferred": continue
        if getattr(args, 'resolved_locally', False) and item.get("status") != "resolved_locally": continue
        created_after = getattr(args, 'created_after', None)
        if created_after:
            try:
                if item.get("created_at", "") < created_after: continue
            except: pass
        created_before = getattr(args, 'created_before', None)
        if created_before:
            try:
                if item.get("created_at", "") > created_before: continue
            except: pass
        result.append(item)
    return result


def cmd_list(args):
    index = _load_index()
    result = _query_items(index.get("items", []), args)
    
    if not result:
        print("No QA items found matching filters."); return
    
    print(f"QA Workbench Items ({len(result)}):")
    print("=" * 100)
    for item in result:
        links = len(item.get("evidence_links", []))
        print(f"  {item['qa_item_id']:20s} [{item.get('status','?'):18s}] {item.get('severity','?'):6s} {item.get('category','?'):14s} links={links}")
        print(f"  {'':20s} {item.get('title', 'untitled')[:60]}")
        print()


def cmd_read(args):
    item = _load_item(args.item_id)
    if item is None: print(f"ERROR: Item {args.item_id} not found"); sys.exit(1)
    print(json.dumps(item, indent=2))


def cmd_validate(args):
    _ensure_store()
    if args.json_file:
        with open(args.json_file) as f:
            item = json.load(f)
        schema_ok, schema_msg = _validate_schema(item)
        violations = _validate_business_rules(item) + _validate_lifecycle_rules(item)
        if schema_ok and not violations:
            print(f"VALID: {item.get('qa_item_id', 'unknown')}"); print("ALL CHECKS PASS")
        else:
            print(f"INVALID: {item.get('qa_item_id', 'unknown')}")
            if not schema_ok: print(f"  Schema: {schema_msg}")
            for v in violations: print(f"  Rule: {v}")
            sys.exit(1)
    else:
        index = _load_index()
        items = index.get("items", [])
        all_ok = True
        for item_id in items:
            item = _load_item(item_id)
            if item is None: print(f"MISSING: {item_id}"); all_ok = False; continue
            schema_ok, schema_msg = _validate_schema(item)
            violations = _validate_business_rules(item) + _validate_lifecycle_rules(item)
            status = "PASS" if (schema_ok and not violations) else "FAIL"
            if status == "FAIL": all_ok = False
            print(f"{item_id:20s} [{status}]")
            if not schema_ok: print(f"  Schema: {schema_msg}")
            for v in violations: print(f"  Rule: {v}")
        if all_ok:
            print(f"\nALL CHECKS PASS — {len(items)} items validated")
        else:
            print(f"\nSOME CHECKS FAILED"); sys.exit(1)


def cmd_triage(args):
    """Mark a QA item as triaged. Shortcut for transition to triaged."""
    item = _load_item(args.item_id)
    if item is None: print(f"ERROR: Item {args.item_id} not found"); sys.exit(1)
    
    allowed, msg = _check_transition_allowed(item, "triaged")
    if not allowed:
        print(f"ERROR: {msg}"); sys.exit(1)
    
    reason = args.reason or "Triaged via CLI"
    _add_lifecycle_entry(item, item["status"], "triaged", reason)
    _save_item(item)
    print(f"Triaged: {args.item_id}")
    print(f"  Reason: {reason}")
    print(f"  Note: Triaging does not imply Owner approval or defect acceptance.")


def cmd_attach(args):
    item = _load_item(args.item_id)
    if item is None: print(f"ERROR: Item {args.item_id} not found"); sys.exit(1)
    
    with open(args.evidence_link_json) as f:
        link = json.load(f)
    
    schema_ok, schema_msg = _validate_evidence_link_schema(link)
    if not schema_ok: print(f"VALIDATION FAILED: {schema_msg}"); sys.exit(1)
    
    existing_ids = [l.get("evidence_link_id") for l in item.get("evidence_links", [])]
    if link.get("evidence_link_id") in existing_ids:
        print(f"ERROR: evidence_link_id '{link.get('evidence_link_id')}' already exists"); sys.exit(1)
    
    link.setdefault("attached_at", _now())
    link.setdefault("advisory_only", True)
    link.setdefault("custody", "qa-pilot-local")
    link.setdefault("authority_note", "Evidence attachment does not prove defect validity or imply Owner approval.")
    
    item.setdefault("evidence_links", []).append(link)
    item["updated_at"] = _now()
    _save_item(item)
    
    print(f"Attached evidence link '{link['evidence_link_id']}' to {args.item_id}")
    print(f"  Type: {link['evidence_type']}")
    print(f"  Total evidence links: {len(item['evidence_links'])}")


def cmd_detach(args):
    item = _load_item(args.item_id)
    if item is None: print(f"ERROR: Item {args.item_id} not found"); sys.exit(1)
    
    links = item.get("evidence_links", [])
    before = len(links)
    item["evidence_links"] = [l for l in links if l.get("evidence_link_id") != args.evidence_link_id]
    if before == len(item["evidence_links"]):
        print(f"ERROR: evidence_link_id '{args.evidence_link_id}' not found"); sys.exit(1)
    
    item["updated_at"] = _now()
    _save_item(item)
    print(f"Detached evidence link '{args.evidence_link_id}' from {args.item_id}")
    print(f"  Note: Detaching evidence does not alter item status.")


def cmd_list_refs(args):
    item = _load_item(args.item_id)
    if item is None: print(f"ERROR: Item {args.item_id} not found"); sys.exit(1)
    links = item.get("evidence_links", [])
    if not links: print(f"No evidence links attached to {args.item_id}."); return
    
    print(f"Evidence Links on {args.item_id}:")
    print("=" * 100)
    for link in links:
        prod = link.get("producing_validator", link.get("producing_command", "N/A"))
        reason = link.get("attachment_reason", "")[:50]
        print(f"  {link['evidence_link_id']:24s} [{link['evidence_type']:22s}] {link['evidence_ref']:20s}")
        print(f"  {'':24s} Produced by: {prod}")
        print(f"  {'':24s} Reason: {reason}")
        print()


def cmd_validate_refs(args):
    item = _load_item(args.item_id)
    if item is None: print(f"ERROR: Item {args.item_id} not found"); sys.exit(1)
    links = item.get("evidence_links", [])
    if not links: print(f"No evidence links on {args.item_id}."); return
    
    all_ok = True
    for link in links:
        lid = link.get("evidence_link_id", "?")
        schema_ok, schema_msg = _validate_evidence_link_schema(link)
        if schema_ok:
            print(f"[PASS] {lid}")
        else:
            all_ok = False; print(f"[FAIL] {lid}: {schema_msg}")
    
    if all_ok:
        print(f"\nALL EVIDENCE LINKS VALID — {len(links)} links")
    else:
        print(f"\nSOME LINKS FAILED"); sys.exit(1)


def cmd_summarize(args):
    item = _load_item(args.item_id)
    if item is None: print(f"ERROR: Item {args.item_id} not found"); sys.exit(1)
    
    links = item.get("evidence_links", [])
    history = item.get("lifecycle_history", [])
    type_counts = {}
    validators = set()
    for link in links:
        type_counts[link.get("evidence_type", "unknown")] = type_counts.get(link.get("evidence_type", "unknown"), 0) + 1
        v = link.get("producing_validator", "")
        if v: validators.add(v)
    
    print(f"QA Item Summary: {args.item_id}")
    print(f"  Title: {item.get('title', 'untitled')}")
    print(f"  Status: {item.get('status', 'unknown')}")
    print(f"  Severity: {item.get('severity', '?')}")
    print(f"  Category: {item.get('category', '?')}")
    print(f"  Evidence links: {len(links)}")
    print(f"  Lifecycle transitions: {len(history)}")
    print(f"  Unique validators: {len(validators)}")
    if history:
        print(f"  Last transition: {history[-1].get('from_status')} → {history[-1].get('to_status')}")
    print(f"  Advisory-only: True")
    print(f"  Custody: qa-pilot-local")


def cmd_status(args):
    """Show current status and lifecycle summary."""
    item = _load_item(args.item_id)
    if item is None: print(f"ERROR: Item {args.item_id} not found"); sys.exit(1)
    
    history = item.get("lifecycle_history", [])
    last_entry = history[-1] if history else None
    
    print(f"Status: {item['status']}")
    print(f"  Item: {args.item_id}")
    print(f"  Title: {item.get('title', 'untitled')}")
    print(f"  Severity: {item.get('severity', '?')}")
    print(f"  Category: {item.get('category', '?')}")
    print(f"  Updated: {item.get('updated_at', '?')}")
    print(f"  Lifecycle transitions: {len(history)}")
    if last_entry:
        print(f"  Last transition: {last_entry.get('from_status')} → {last_entry.get('to_status')}")
        print(f"  Reason: {last_entry.get('transition_reason', '?')}")
    
    # Show allowed transitions
    allowed = ALLOWED_TRANSITIONS.get(item["status"], [])
    if allowed:
        print(f"  Allowed transitions: {', '.join(allowed)}")
    else:
        print(f"  Allowed transitions: none (terminal state)")
    print(f"  Advisory-only: True")


def cmd_transition(args):
    """Transition item to a new status."""
    item = _load_item(args.item_id)
    if item is None: print(f"ERROR: Item {args.item_id} not found"); sys.exit(1)
    
    to_status = args.to_status
    reason = args.reason
    
    if not reason:
        print("ERROR: --reason is required for transitions"); sys.exit(1)
    
    # Check authority claims in reason
    for p in ["approved", "verified", "sealed", "defect accepted"]:
        if p in reason.lower():
            print(f"ERROR: Transition reason must not claim '{p}' authority"); sys.exit(1)
    
    allowed, msg = _check_transition_allowed(item, to_status)
    if not allowed:
        print(f"ERROR: {msg}"); sys.exit(1)
    
    # Special check: reopening resolved items requires explicit reason
    if item["status"] == "resolved_locally" and to_status == "open":
        if "reopen" not in reason.lower() and len(reason) < 10:
            print("ERROR: Reopening a resolved item requires a substantive reason (min 10 chars)"); sys.exit(1)
    
    from_status = item["status"]
    actor = f"CLI-{os.environ.get('USER', 'unknown')}"
    _add_lifecycle_entry(item, from_status, to_status, reason, actor=actor)
    _save_item(item)
    
    print(f"Transitioned: {args.item_id}: {from_status} → {to_status}")
    print(f"  Reason: {reason}")
    print(f"  Note: '{to_status}' does not imply Owner approval, verification, or seal authority.")


def cmd_history(args):
    """Show append-only lifecycle history."""
    item = _load_item(args.item_id)
    if item is None: print(f"ERROR: Item {args.item_id} not found"); sys.exit(1)
    
    history = item.get("lifecycle_history", [])
    if not history:
        print(f"No lifecycle history for {args.item_id}."); return
    
    print(f"Lifecycle History for {args.item_id}:")
    print("=" * 80)
    for i, entry in enumerate(history):
        fs = entry.get("from_status", "?")
        ts = entry.get("to_status", "?")
        reason = entry.get("transition_reason", "?")
        ts_str = entry.get("timestamp", "?")[:19]
        actor = entry.get("actor", "")
        print(f"  {i+1}. {fs:20s} → {ts:20s} [{ts_str}]")
        print(f"     Reason: {reason}")
        if actor:
            print(f"     Actor: {actor}")
        print()


def cmd_reopen(args):
    """Reopen a resolved item."""
    item = _load_item(args.item_id)
    if item is None: print(f"ERROR: Item {args.item_id} not found"); sys.exit(1)
    
    if item["status"] not in ("resolved_locally", "deferred"):
        print(f"ERROR: Only resolved_locally or deferred items can be reopened (current: {item['status']})"); sys.exit(1)
    
    reason = args.reason
    if not reason or len(reason) < 10:
        print("ERROR: Reopen requires a substantive reason (min 10 chars)"); sys.exit(1)
    
    allowed, msg = _check_transition_allowed(item, "open")
    if not allowed:
        print(f"ERROR: {msg}"); sys.exit(1)
    
    from_status = item["status"]
    _add_lifecycle_entry(item, from_status, "open", f"REOPEN: {reason}", actor="CLI-reopen")
    _save_item(item)
    
    print(f"Reopened: {args.item_id}: {from_status} → open")
    print(f"  Reason: {reason}")
    print(f"  Note: Reopening does not imply the original assessment was wrong.")
    print(f"        It simply records that the item is being revisited.")


def cmd_validate_transition(args):
    """Check whether a transition would be allowed (read-only)."""
    item = _load_item(args.item_id)
    if item is None: print(f"ERROR: Item {args.item_id} not found"); sys.exit(1)
    
    to_status = args.to_status
    allowed, msg = _check_transition_allowed(item, to_status)
    
    if allowed:
        print(f"VALID TRANSITION: {item['status']} → {to_status}")
    else:
        print(f"INVALID TRANSITION: {msg}")
        sys.exit(1)


def cmd_query(args):
    """Rich query interface with all available filters."""
    index = _load_index()
    result = _query_items(index.get("items", []), args)
    
    if args.format == "json":
        print(json.dumps(result, indent=2))
        return
    
    if not result:
        print("No QA items found matching filters."); return
    
    print(f"Query results ({len(result)} items):")
    print("=" * 100)
    for item in result:
        links = len(item.get("evidence_links", []))
        print(f"  {item['qa_item_id']:20s} [{item.get('status','?'):18s}] {item.get('severity','?'):6s} {item.get('category','?'):14s} links={links}")
        print(f"  {'':20s} {item.get('title', 'untitled')[:60]}")
        print()
    
    print(f"  Advisory: Results are read-only and do not imply validation or approval.")


def cmd_count(args):
    """Count items matching filters, with optional group-by."""
    index = _load_index()
    all_items = [_load_item(i) for i in index.get("items", []) if _load_item(i) is not None]
    
    if not all_items:
        print("No items in workbench.")
        return
    
    filtered = _query_items(index.get("items", []), args)
    
    print(f"QA Workbench Count:")
    print(f"  Total items: {len(all_items)}")
    print(f"  Matching filters: {len(filtered)}")
    print()
    
    if args.group:
        if args.group == "status":
            counts = {}
            for item in filtered:
                s = item.get("status", "unknown")
                counts[s] = counts.get(s, 0) + 1
            print(f"  By status:")
            for s in sorted(counts): print(f"    {s:22s}: {counts[s]}")
        elif args.group == "severity":
            counts = {}
            for item in filtered:
                s = item.get("severity", "unknown")
                counts[s] = counts.get(s, 0) + 1
            print(f"  By severity:")
            for s in sorted(counts): print(f"    {s:22s}: {counts[s]}")
        elif args.group == "category":
            counts = {}
            for item in filtered:
                c = item.get("category", "unknown")
                counts[c] = counts.get(c, 0) + 1
            print(f"  By category:")
            for c in sorted(counts): print(f"    {c:22s}: {counts[c]}")
    
    print(f"  Advisory: Counts are advisory-only and do not imply Owner approval.")


def cmd_report(args):
    """Produce a cross-item summary of the entire workbench."""
    index = _load_index()
    all_items = [_load_item(i) for i in index.get("items", []) if _load_item(i) is not None]
    
    if not all_items:
        print("No items in workbench.")
        return
    
    # Aggregations
    by_status = {}; by_severity = {}; by_category = {}
    with_evidence = 0; needs_review = 0; deferred = 0; resolved = 0
    total = len(all_items)
    
    for item in all_items:
        s = item.get("status", "unknown"); by_status[s] = by_status.get(s, 0) + 1
        sev = item.get("severity", "unknown"); by_severity[sev] = by_severity.get(sev, 0) + 1
        cat = item.get("category", "unknown"); by_category[cat] = by_category.get(cat, 0) + 1
        if item.get("evidence_links"): with_evidence += 1
        if s == "needs_review": needs_review += 1
        if s == "deferred": deferred += 1
        if s == "resolved_locally": resolved += 1
    
    print(f"QA Workbench Summary Report")
    print("=" * 60)
    print(f"  Total items:          {total}")
    print(f"  With evidence links:  {with_evidence}")
    print(f"  Needing review:       {needs_review}")
    print(f"  Deferred:             {deferred}")
    print(f"  Resolved locally:     {resolved}")
    print()
    print(f"  By status:")
    for s in ["draft","open","triaged","evidence_attached","needs_review","deferred","resolved_locally"]:
        c = by_status.get(s, 0)
        if c > 0: print(f"    {s:22s}: {c}")
    print()
    print(f"  By severity:")
    for s in ["critical","high","medium","low","info"]:
        c = by_severity.get(s, 0)
        if c > 0: print(f"    {s:22s}: {c}")
    print()
    print(f"  By category:")
    for c in sorted(by_category):
        print(f"    {c:22s}: {by_category[c]}")
    print()
    print(f"  Advisory: This summary is advisory-only. Counts do not imply")
    print(f"  validation, Owner approval, verification, or seal authority.")


def cmd_export_summary(args):
    """Export current workbench summary as JSON."""
    index = _load_index()
    all_items = [_load_item(i) for i in index.get("items", []) if _load_item(i) is not None]
    
    by_status = {}; by_severity = {}; by_category = {}
    with_evidence = 0; needs_review = 0; deferred = 0; resolved = 0
    
    for item in all_items:
        s = item.get("status", "unknown"); by_status[s] = by_status.get(s, 0) + 1
        sev = item.get("severity", "unknown"); by_severity[sev] = by_severity.get(sev, 0) + 1
        cat = item.get("category", "unknown"); by_category[cat] = by_category.get(cat, 0) + 1
        if item.get("evidence_links"): with_evidence += 1
        if s == "needs_review": needs_review += 1
        if s == "deferred": deferred += 1
        if s == "resolved_locally": resolved += 1
    
    summary = {
        "total_items": len(all_items),
        "with_evidence_links": with_evidence,
        "needs_review": needs_review,
        "deferred": deferred,
        "resolved_locally": resolved,
        "by_status": by_status,
        "by_severity": by_severity,
        "by_category": by_category,
        "advisory_only": True,
        "custody": "qa-pilot-local",
        "librarian_impact": "none",
        "authority_note": "This summary is advisory-only. Counts do not imply validation, Owner approval, verification, or seal authority."
    }
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"Summary exported to {args.output}")
    else:
        print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser(description="QA Pilot Workbench CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    
    p_create = sub.add_parser("create"); p_create.add_argument("json_file"); p_create.set_defaults(func=cmd_create)
    
    p_list = sub.add_parser("list")
    p_list.add_argument("--status"); p_list.add_argument("--severity"); p_list.add_argument("--category"); p_list.add_argument("--source")
    p_list.add_argument("--evidence-type"); p_list.add_argument("--has-evidence", action="store_true")
    p_list.add_argument("--needs-review", action="store_true"); p_list.add_argument("--deferred", action="store_true")
    p_list.add_argument("--resolved-locally", action="store_true")
    p_list.set_defaults(func=cmd_list)
    
    p_read = sub.add_parser("read"); p_read.add_argument("item_id"); p_read.set_defaults(func=cmd_read)
    
    p_val = sub.add_parser("validate"); p_val.add_argument("json_file", nargs="?", default=None); p_val.set_defaults(func=cmd_validate)
    
    p_tri = sub.add_parser("triage"); p_tri.add_argument("item_id"); p_tri.add_argument("--reason", default=None); p_tri.set_defaults(func=cmd_triage)
    
    p_att = sub.add_parser("attach"); p_att.add_argument("item_id"); p_att.add_argument("evidence_link_json"); p_att.set_defaults(func=cmd_attach)
    p_det = sub.add_parser("detach"); p_det.add_argument("item_id"); p_det.add_argument("evidence_link_id"); p_det.set_defaults(func=cmd_detach)
    p_lr = sub.add_parser("list-refs"); p_lr.add_argument("item_id"); p_lr.set_defaults(func=cmd_list_refs)
    p_vr = sub.add_parser("validate-refs"); p_vr.add_argument("item_id"); p_vr.set_defaults(func=cmd_validate_refs)
    p_sum = sub.add_parser("summarize"); p_sum.add_argument("item_id"); p_sum.set_defaults(func=cmd_summarize)
    
    # New lifecycle commands
    p_st = sub.add_parser("status"); p_st.add_argument("item_id"); p_st.set_defaults(func=cmd_status)
    p_tr = sub.add_parser("transition"); p_tr.add_argument("item_id"); p_tr.add_argument("to_status"); p_tr.add_argument("--reason", required=True); p_tr.set_defaults(func=cmd_transition)
    p_hi = sub.add_parser("history"); p_hi.add_argument("item_id"); p_hi.set_defaults(func=cmd_history)
    p_re = sub.add_parser("reopen"); p_re.add_argument("item_id"); p_re.add_argument("--reason", required=True); p_re.set_defaults(func=cmd_reopen)
    p_vt = sub.add_parser("validate-transition"); p_vt.add_argument("item_id"); p_vt.add_argument("to_status"); p_vt.set_defaults(func=cmd_validate_transition)
    
    # Query / listing commands
    p_q = sub.add_parser("query")
    p_q.add_argument("--status"); p_q.add_argument("--severity"); p_q.add_argument("--category"); p_q.add_argument("--source")
    p_q.add_argument("--evidence-type"); p_q.add_argument("--has-evidence", action="store_true")
    p_q.add_argument("--needs-review", action="store_true"); p_q.add_argument("--deferred", action="store_true")
    p_q.add_argument("--resolved-locally", action="store_true")
    p_q.add_argument("--created-after"); p_q.add_argument("--created-before")
    p_q.add_argument("--format", choices=["text", "json"], default="text")
    p_q.set_defaults(func=cmd_query)
    
    p_cnt = sub.add_parser("count")
    p_cnt.add_argument("--status"); p_cnt.add_argument("--severity"); p_cnt.add_argument("--category"); p_cnt.add_argument("--source")
    p_cnt.add_argument("--evidence-type"); p_cnt.add_argument("--has-evidence", action="store_true")
    p_cnt.add_argument("--needs-review", action="store_true"); p_cnt.add_argument("--deferred", action="store_true")
    p_cnt.add_argument("--resolved-locally", action="store_true")
    p_cnt.add_argument("--created-after"); p_cnt.add_argument("--created-before")
    p_cnt.add_argument("--group", choices=["status", "severity", "category"])
    p_cnt.set_defaults(func=cmd_count)
    
    p_rpt = sub.add_parser("report"); p_rpt.set_defaults(func=cmd_report)
    
    p_exp = sub.add_parser("export-summary"); p_exp.add_argument("--output", default=None); p_exp.set_defaults(func=cmd_export_summary)
    
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
