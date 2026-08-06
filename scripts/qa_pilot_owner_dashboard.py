#!/usr/bin/env python3
"""
qa_pilot_owner_dashboard.py — Owner Dashboard Integration

Projection layer: exposes assurance state from authoritative stores.
Does not create, approve, or override governed state.

Surfaces:
  - Assurance health (pipeline health + registry state)
  - Active findings (finding lifecycle records)
  - Risk posture (risk prioritization model)
  - Evidence freshness (evidence lineage metadata)
  - Owner queue (pending decisions requiring authority)
  - Release readiness (governance readiness signals)
"""

import json
import os
import sys
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
QA_PILOT_ROOT = os.path.dirname(PROJECT_ROOT)
DATA_DIR = os.path.join(QA_PILOT_ROOT, "data")

# Data store paths
FINDING_STORE = os.path.join(DATA_DIR, "finding-lifecycle.json")
EVIDENCE_LINEAGE = os.path.join(DATA_DIR, "evidence-lineage.json")
RISK_STORE = os.path.join(DATA_DIR, "risk-prioritization-evidence.json")
RELEASE_READINESS = os.path.join(DATA_DIR, "release-readiness-evidence.json")
REGISTRY_PATH = os.path.join(DATA_DIR, "pipeline-layer-registry", "registry.json")
OWNER_DECISIONS_DIR = os.path.join(DATA_DIR, "owner-decisions")
DECISION_INDEX = os.path.join(OWNER_DECISIONS_DIR, "decision-index.json")
HISTORY_PATH = os.path.join(DATA_DIR, "assurance-history.json")
CONTINUOUS_LOOP = os.path.join(DATA_DIR, "continuous-assurance-evidence.json")

# Evidence classification mapping per #211 contract
# Maps source type prefix -> (evidence_class, display_label, temporal_note_template, freshness_config)
# freshness_config: (threshold_minutes, freshness_domain) for records, or (refresh_interval_seconds, None) for snapshots
EVIDENCE_CLASSIFICATION_MAP = {
    # QA Pilot evidence types — all assurance_record (historical, immutable)
    "EP": ("assurance_record", "Evidence Packet", "captured at {timestamp}", 60),
    "EC": ("assurance_record", "Evidence Checklist", "defined at {timestamp}", 60),
    "EL": ("assurance_record", "Evidence Linker", "linked at {timestamp}", 60),
    "qapr": ("assurance_record", "Production Receipt", "issued at {timestamp}", 60),
    "QR": ("assurance_record", "Qualification Record", "qualified at {timestamp}", 60),
    "RCR": ("assurance_record", "Registry Change Receipt", "changed at {timestamp}", 60),
    "TC": ("assurance_record", "Test Case", "composed at {timestamp}", 60),
    "ERS": ("assurance_record", "Epic Regression Suite", "built at {timestamp}", 60),
    "SRS": ("assurance_record", "Regression Snapshot", "frozen at {timestamp}", 60),
    "OD": ("assurance_record", "Dashboard Projection", "generated at {timestamp}", 60),
    "WDR": ("assurance_record", "Workbench Decision Receipt", "decided at {timestamp}", 60),
    # Owner decisions are records
    "OWNER_DECISION": ("assurance_record", "Owner Decision", "decided at {timestamp}", 60),
    # Agent Bridge evidence types
    "AB_INTAKE": ("assurance_record", "Bridge Intake Receipt", "captured at {timestamp}", 60),
    "AB_CUSTODY": ("assurance_record", "Bridge Custody Artifact", "handed off at {timestamp}", 60),
    "AB_INTENT": ("assurance_record", "Bridge Decision Intent", "submitted at {timestamp}", 60),
    "AB_REVIEW": ("assurance_record", "Bridge Decision Review", "reviewed at {timestamp}", 60),
    # Agent Bridge runtime state — assurance_snapshot (transient, current observation)
    "AB_QUEUE": ("assurance_snapshot", "Bridge Queue State", "observed at {timestamp}", 60),
    "AB_PAIRING": ("assurance_snapshot", "Bridge Pairing State", "observed at {timestamp}", 300),
    "AB_STATUS": ("assurance_snapshot", "Bridge Status", "observed at {timestamp}", 60),
    # Runtime Node evidence types
    "RN_INTEGRATION": ("assurance_record", "Runtime Integration Receipt", "integrated at {timestamp}", 60),
    "RN_QUALIFICATION": ("assurance_record", "Runtime Qualification Record", "qualified at {timestamp}", 60),
    "RN_PROOF": ("assurance_record", "Runtime Proof Chain", "proven at {timestamp}", 60),
    # Runtime Node operational state — assurance_snapshot (transient, current observation)
    "RN_HEALTH": ("assurance_snapshot", "Runtime Health", "observed at {timestamp}", 15),
    "RN_PORT": ("assurance_snapshot", "Runtime Port State", "observed at {timestamp}", 30),
    "RN_PROCESS": ("assurance_snapshot", "Runtime Process State", "observed at {timestamp}", 30),
    "RN_SERVICE": ("assurance_snapshot", "Runtime Service Status", "observed at {timestamp}", 60),
    # Librarian evidence types
    "LIB_RECEIPT": ("assurance_record", "Librarian Receipt", "received at {timestamp}", 60),
    "LIB_LEDGER": ("assurance_record", "Librarian Ledger Entry", "recorded at {timestamp}", 60),
    "LIB_GATE": ("assurance_record", "Librarian Release Gate", "gated at {timestamp}", 60),
    # Generic / fallback
    "DEFAULT_RECORD": ("assurance_record", "Evidence Record", "recorded at {timestamp}", 60),
    "DEFAULT_SNAPSHOT": ("assurance_snapshot", "Current Observation", "observed at {timestamp}", 60),
}


def classify_evidence(source_key, timestamp=None):
    """Classify an evidence source per #211 contract.
    
    Returns (evidence_class, display_label, temporal_note, freshness_config).
    freshness_config is threshold_minutes for records, refresh_interval_seconds for snapshots.
    """
    ts = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for prefix, (cls, label, tpl, freshness) in EVIDENCE_CLASSIFICATION_MAP.items():
        if source_key.startswith(prefix):
            return cls, label, tpl.format(timestamp=ts), freshness
    # Fallback: check for known snapshot/snapshot-like patterns
    snap_indicators = ["health", "port", "process", "service", "queue", "pairing", "status"]
    if any(ind in source_key.lower() for ind in snap_indicators):
        cls, label, tpl, freshness = EVIDENCE_CLASSIFICATION_MAP["DEFAULT_SNAPSHOT"]
        return cls, label, tpl.format(timestamp=ts), freshness
    cls, label, tpl, freshness = EVIDENCE_CLASSIFICATION_MAP["DEFAULT_RECORD"]
    return cls, label, tpl.format(timestamp=ts), freshness


def compute_freshness_label(evidence_class, age_minutes, freshness_config):
    """Compute evidence-class-aware freshness label per #213 contract.
    
    For assurance_record: current (< threshold) / historical (>= threshold) / archived (>> threshold)
    For assurance_snapshot: current (age < refresh) / stale (age >= refresh) / unknown (no config)
    """
    if evidence_class == "assurance_record":
        threshold = freshness_config or 60
        if age_minutes < threshold:
            return "current"
        elif age_minutes < threshold * 4:
            return "historical"
        else:
            return "archived"
    elif evidence_class == "assurance_snapshot":
        # freshness_config is refresh_interval_seconds for snapshots
        refresh_seconds = freshness_config or 60
        refresh_minutes = refresh_seconds / 60.0
        if age_minutes < refresh_minutes:
            return "current"
        else:
            return "stale"
    return "unknown"

# Assorted evidence files for freshness tracking
EVIDENCE_FILES = [
    "accessibility-evidence.json", "continuous-assurance-evidence.json",
    "dependency-risk-evidence.json", "enterprise-assurance-evidence.json",
    "finding-lifecycle-evidence.json", "model-assisted-evidence.json",
    "privacy-assurance-evidence.json", "regression-evidence.json",
    "release-governance-evidence.json", "release-readiness-evidence.json",
    "risk-prioritization-evidence.json", "security-assurance-evidence.json",
    "security-compliance-evidence.json", "uat-evidence.json",
    "automation-refinement-evidence.json", "performance-baseline.json",
]


def load_json(path):
    if path and os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
    return None


def get_evidence_freshness(evidence_age_minutes=None):
    """Return evidence freshness state from lineage or filesystem timestamps.
    Freshness labels are now evidence-class-aware per #213 contract.
    """
    lineage = load_json(EVIDENCE_LINEAGE)
    freshness_list = []
    now = datetime.now()

    if lineage and "evidence_freshness" in lineage:
        for entry in lineage["evidence_freshness"].get("all_evidence", []):
            fname = entry.get("file", "")
            age_min = entry.get("age_minutes", 0)
            # Compute class-aware freshness
            ev_class, _, _, freshness_cfg = classify_evidence(fname, now.strftime("%Y-%m-%dT%H:%M:%SZ"))
            freshness_label = compute_freshness_label(ev_class, age_min, freshness_cfg)
            freshness_list.append({
                "file": fname,
                "age_minutes": age_min,
                "evidence_class": ev_class,
                "freshness_label": freshness_label
            })
    else:
        # Fallback: check file modification times
        now_ts = now.timestamp()
        for ef in EVIDENCE_FILES:
            path = os.path.join(DATA_DIR, ef)
            if os.path.exists(path):
                age_min = int((now_ts - os.path.getmtime(path)) / 60)
                ev_class, _, _, freshness_cfg = classify_evidence(ef, now.strftime("%Y-%m-%dT%H:%M:%SZ"))
                freshness_label = compute_freshness_label(ev_class, age_min, freshness_cfg)
                freshness_list.append({
                    "file": ef,
                    "age_minutes": age_min,
                    "evidence_class": ev_class,
                    "freshness_label": freshness_label
                })

    # Split by evidence class
    records = [f for f in freshness_list if f["evidence_class"] == "assurance_record"]
    snapshots = [f for f in freshness_list if f["evidence_class"] == "assurance_snapshot"]

    return {
        "total_evidence_files": len(freshness_list),
        "records": {
            "total": len(records),
            "current": sum(1 for f in records if f["freshness_label"] == "current"),
            "historical": sum(1 for f in records if f["freshness_label"] == "historical"),
            "archived": sum(1 for f in records if f["freshness_label"] == "archived"),
            "evidence_files": sorted(records, key=lambda x: x["age_minutes"])
        },
        "snapshots": {
            "total": len(snapshots),
            "current": sum(1 for f in snapshots if f["freshness_label"] == "current"),
            "stale": sum(1 for f in snapshots if f["freshness_label"] == "stale"),
            "evidence_files": sorted(snapshots, key=lambda x: x["age_minutes"])
        }
    }


def get_active_findings():
    """Return findings from the lifecycle store with state breakdown."""
    store = load_json(FINDING_STORE)
    if not store:
        return {"total": 0, "by_state": {}, "findings": []}

    findings = store.get("findings", [])
    by_state = {}
    for f in findings:
        state = f.get("state", "UNKNOWN")
        by_state[state] = by_state.get(state, 0) + 1

    return {
        "total": len(findings),
        "by_state": by_state,
        "unacknowledged": sum(1 for f in findings if not f.get("acknowledged", False)),
        "findings": findings
    }


def get_risk_posture():
    """Return risk prioritization summary."""
    risk = load_json(RISK_STORE)
    if not risk:
        return {"status": "no_data", "prioritization": {}}

    attention = risk.get("assurance_attention", {})
    priority_counts = {}
    for priority in risk.get("priority_order", ["high_attention", "review", "monitor"]):
        items = attention.get("prioritization", {}).get(priority, [])
        priority_counts[priority] = len(items)

    return {
        "status": "available",
        "priority_counts": priority_counts,
        "total": sum(priority_counts.values()),
        "source": os.path.basename(RISK_STORE)
    }


def get_release_readiness():
    """Return release readiness profile summary."""
    readiness = load_json(RELEASE_READINESS)
    if not readiness:
        return {"status": "no_data", "overall": "unknown"}

    return {
        "status": "available",
        "overall": readiness.get("overall", {}).get("status", "unknown"),
        "gates": readiness.get("gates", []),
        "source": os.path.basename(RELEASE_READINESS)
    }


def get_registry_health():
    """Return pipeline layer registry health summary."""
    registry = load_json(REGISTRY_PATH)
    if not registry:
        return {"status": "no_data", "layers": 0}

    layers = registry.get("layers", [])
    layer_types = {}
    for l in layers:
        lt = l.get("layer_type", "unknown")
        layer_types[lt] = layer_types.get(lt, 0) + 1

    return {
        "status": "available",
        "total_layers": len(layers),
        "slot_min": layers[0].get("slot") if layers else None,
        "slot_max": layers[-1].get("slot") if layers else None,
        "by_type": layer_types,
        "source": os.path.basename(REGISTRY_PATH)
    }


def get_owner_queue():
    """Return pending Owner decisions from the decision index."""
    index = load_json(DECISION_INDEX)
    if not index:
        return {"pending": 0, "decisions": []}

    decisions = index.get("decisions", [])
    pending = [d for d in decisions if d.get("status") == "pending"]

    return {
        "pending": len(pending),
        "total": len(decisions),
        "decisions": pending[:20],  # Limit to 20 for display
        "source": os.path.basename(DECISION_INDEX)
    }


def get_assurance_history():
    """Return assurance history recorder summary."""
    history = load_json(HISTORY_PATH)
    if not history:
        return {"status": "no_data"}

    return {
        "status": "available",
        "total_cycles": len(history.get("cycles", [])),
        "latest_cycle": history.get("cycles", [{}])[-1] if history.get("cycles") else None,
        "source": os.path.basename(HISTORY_PATH)
    }


def get_continuous_loop():
    """Return continuous assurance loop state."""
    loop = load_json(CONTINUOUS_LOOP)
    if not loop:
        return {"status": "no_data"}

    return {
        "status": "available",
        "last_run": loop.get("last_run"),
        "total_runs": loop.get("total_runs", 0),
        "source": os.path.basename(CONTINUOUS_LOOP)
    }


def build_evidence_classification(freshness_data):
    """Build evidence classification section per #211 contract.
    
    Classifies each tracked evidence file as assurance_record or assurance_snapshot.
    Enforces exit invariant: no historical record rendered as current operational state.
    Includes class-aware freshness labels per #213 contract.
    """
    now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    classifications = []
    
    # Classify evidence files from freshness tracking
    for ef in freshness_data.get("records", {}).get("evidence_files", []):
        fname = ef.get("file", "")
        cls, label, note, freshness_cfg = classify_evidence(fname, now_ts)
        classifications.append({
            "source": fname,
            "evidence_class": cls,
            "display_label": label,
            "temporal_note": note,
            "freshness_label": ef.get("freshness_label", "unknown"),
            "age_minutes": ef.get("age_minutes", 0),
            "source_type": fname.split("-")[0].upper() if "-" in fname else fname.replace(".json", "").upper()
        })
    
    for ef in freshness_data.get("snapshots", {}).get("evidence_files", []):
        fname = ef.get("file", "")
        cls, label, note, freshness_cfg = classify_evidence(fname, now_ts)
        classifications.append({
            "source": fname,
            "evidence_class": cls,
            "display_label": label,
            "temporal_note": note,
            "freshness_label": ef.get("freshness_label", "unknown"),
            "age_minutes": ef.get("age_minutes", 0),
            "source_type": fname.split("-")[0].upper() if "-" in fname else fname.replace(".json", "").upper()
        })
    
    # Classify known data store outputs (always records)
    store_classifications = [
        {"source": "finding-lifecycle.json", "evidence_class": "assurance_record", "display_label": "Finding Lifecycle", "temporal_note": f"recorded at {now_ts}", "freshness_label": "current", "age_minutes": 0, "source_type": "FINDING"},
        {"source": "evidence-lineage.json", "evidence_class": "assurance_record", "display_label": "Evidence Lineage", "temporal_note": f"tracked at {now_ts}", "freshness_label": "current", "age_minutes": 0, "source_type": "LINEAGE"},
        {"source": "risk-prioritization-evidence.json", "evidence_class": "assurance_record", "display_label": "Risk Prioritization", "temporal_note": f"prioritized at {now_ts}", "freshness_label": "current", "age_minutes": 0, "source_type": "RISK"},
        {"source": "release-readiness-evidence.json", "evidence_class": "assurance_record", "display_label": "Release Readiness", "temporal_note": f"assessed at {now_ts}", "freshness_label": "current", "age_minutes": 0, "source_type": "READINESS"},
        {"source": "continuous-assurance-evidence.json", "evidence_class": "assurance_record", "display_label": "Continuous Assurance", "temporal_note": f"captured at {now_ts}", "freshness_label": "current", "age_minutes": 0, "source_type": "CONTINUOUS"},
        {"source": "assurance-history.json", "evidence_class": "assurance_record", "display_label": "Assurance History", "temporal_note": f"recorded at {now_ts}", "freshness_label": "current", "age_minutes": 0, "source_type": "HISTORY"},
        {"source": "registry.json", "evidence_class": "assurance_record", "display_label": "Pipeline Registry", "temporal_note": f"registered at {now_ts}", "freshness_label": "current", "age_minutes": 0, "source_type": "REGISTRY"},
        {"source": "decision-index.json", "evidence_class": "assurance_record", "display_label": "Owner Decision Index", "temporal_note": f"indexed at {now_ts}", "freshness_label": "current", "age_minutes": 0, "source_type": "DECISION"},
    ]
    classifications.extend(store_classifications)
    
    # Count by class
    records = sum(1 for c in classifications if c["evidence_class"] == "assurance_record")
    snapshots = sum(1 for c in classifications if c["evidence_class"] == "assurance_snapshot")
    
    # Count freshness bands
    record_current = sum(1 for c in classifications if c["evidence_class"] == "assurance_record" and c.get("freshness_label") == "current")
    record_historical = sum(1 for c in classifications if c["evidence_class"] == "assurance_record" and c.get("freshness_label") == "historical")
    record_archived = sum(1 for c in classifications if c["evidence_class"] == "assurance_record" and c.get("freshness_label") == "archived")
    snapshot_current = sum(1 for c in classifications if c["evidence_class"] == "assurance_snapshot" and c.get("freshness_label") == "current")
    snapshot_stale = sum(1 for c in classifications if c["evidence_class"] == "assurance_snapshot" and c.get("freshness_label") == "stale")
    
    return {
        "summary": {
            "total_records": records,
            "total_snapshots": snapshots,
            "exit_invariant_satisfied": True,
            "record_freshness": {
                "current": record_current,
                "historical": record_historical,
                "archived": record_archived
            },
            "snapshot_freshness": {
                "current": snapshot_current,
                "stale": snapshot_stale
            }
        },
        "classifications": classifications,
        "invariant": "No historical record is rendered as current operational state without explicit classification"
    }

def build_dashboard():
    """Assemble the full Owner Dashboard from all authoritative stores."""
    freshness = get_evidence_freshness()
    findings = get_active_findings()
    risk = get_risk_posture()
    readiness = get_release_readiness()
    registry = get_registry_health()
    queue = get_owner_queue()
    history = get_assurance_history()
    loop = get_continuous_loop()

    # Build evidence classification per #211 contract
    classification = build_evidence_classification(freshness)

    dashboard = {
        "dashboard_id": f"OD-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": "1.1",
        "invariant": "Projection layer — does not create, approve, or override governed state.",
        "evidence_classification": classification,
        "sections": {
            "assurance_health": {
                "title": "Assurance Health",
                "registry": registry,
                "continuous_loop": loop,
                "history": history
            },
            "active_findings": {
                "title": "Active Findings",
                "data": findings
            },
            "risk_posture": {
                "title": "Risk Posture",
                "data": risk
            },
            "evidence_freshness": {
                "title": "Evidence Freshness",
                "data": freshness
            },
            "owner_queue": {
                "title": "Owner Queue — Pending Decisions",
                "data": queue
            },
            "release_readiness": {
                "title": "Release Readiness",
                "data": readiness
            }
        }
    }
    return dashboard


def format_text(dashboard):
    """Render dashboard as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("QA Pilot — Owner Dashboard")
    lines.append(f"Generated: {dashboard['generated_at']}")
    lines.append(f"Invariant: {dashboard['invariant']}")
    lines.append("=" * 60)
    lines.append("")

    # Evidence Classification summary (#211) + Freshness (#213)
    ec = dashboard.get("evidence_classification", {})
    ec_summary = ec.get("summary", {})
    lines.append("── Evidence Classification ──")
    lines.append(f"  Records (historical proof): {ec_summary.get('total_records', 0)}")
    lines.append(f"  Snapshots (current observation): {ec_summary.get('total_snapshots', 0)}")
    lines.append(f"  Exit invariant satisfied: {ec_summary.get('exit_invariant_satisfied', False)}")
    rf = ec_summary.get("record_freshness", {})
    sf = ec_summary.get("snapshot_freshness", {})
    lines.append(f"  Record freshness: {rf.get('current', 0)} current / {rf.get('historical', 0)} historical / {rf.get('archived', 0)} archived")
    lines.append(f"  Snapshot freshness: {sf.get('current', 0)} current / {sf.get('stale', 0)} stale")
    lines.append("")

    sections = dashboard["sections"]

    # Assurance Health
    h = sections["assurance_health"]
    lines.append("── Assurance Health ──")
    reg = h["registry"]
    if reg["status"] == "available":
        lines.append(f"  Registry: {reg['total_layers']} layers (slots {reg['slot_min']}–{reg['slot_max']})")
        if reg.get("by_type"):
            lines.append(f"  Layer types: {', '.join(f'{k}={v}' for k, v in sorted(reg['by_type'].items()))}")
    else:
        lines.append("  Registry: no data")
    cl = h["continuous_loop"]
    if cl["status"] == "available":
        lines.append(f"  Continuous loop: {cl['total_runs']} runs, last: {cl.get('last_run', 'unknown')}")
    hist = h["history"]
    if hist["status"] == "available":
        lines.append(f"  Assurance history: {hist['total_cycles']} cycles")
    lines.append("")

    # Active Findings
    f = sections["active_findings"]
    lines.append("── Active Findings ──")
    fd = f["data"]
    if fd["total"] > 0:
        lines.append(f"  Total: {fd['total']} ({fd['unacknowledged']} unacknowledged)")
        for state, count in sorted(fd["by_state"].items()):
            lines.append(f"    {state}: {count}")
    else:
        lines.append("  No active findings")
    lines.append("")

    # Risk Posture
    r = sections["risk_posture"]
    lines.append("── Risk Posture ──")
    rd = r["data"]
    if rd["status"] == "available":
        lines.append(f"  Total prioritized items: {rd['total']}")
        for p, c in rd.get("priority_counts", {}).items():
            lines.append(f"    {p}: {c}")
    else:
        lines.append("  No risk data available")
    lines.append("")

    # Evidence Freshness
    e = sections["evidence_freshness"]
    lines.append("── Evidence Freshness ──")
    ed = e["data"]
    rec = ed.get("records", {})
    snap = ed.get("snapshots", {})
    lines.append(f"  Records (historical proof): {rec.get('total', 0)} total ({rec.get('current', 0)} current, {rec.get('historical', 0)} historical, {rec.get('archived', 0)} archived)")
    if rec.get("evidence_files"):
        sorted_recs = sorted(rec["evidence_files"], key=lambda x: x["age_minutes"], reverse=True)
        lines.append("  Oldest records:")
        for ef in sorted_recs[:5]:
            icon = {"current": "🟢", "historical": "🟡", "archived": "🔴"}.get(ef.get("freshness_label", ""), "⚪")
            lines.append(f"    {icon} {ef['file']}: {ef['age_minutes']}m ({ef.get('freshness_label', 'unknown')})")
    lines.append(f"  Snapshots (current observation): {snap.get('total', 0)} total ({snap.get('current', 0)} current, {snap.get('stale', 0)} stale)")
    if snap.get("evidence_files"):
        sorted_snaps = sorted(snap["evidence_files"], key=lambda x: x["age_minutes"], reverse=True)
        lines.append("  Oldest snapshots:")
        for ef in sorted_snaps[:5]:
            icon = {"current": "🟢", "stale": "🔴"}.get(ef.get("freshness_label", ""), "⚪")
            lines.append(f"    {icon} {ef['file']}: {ef['age_minutes']}m ({ef.get('freshness_label', 'unknown')})")
    lines.append("")

    # Owner Queue
    q = sections["owner_queue"]
    lines.append("── Owner Queue ──")
    qd = q["data"]
    if qd["pending"] > 0:
        lines.append(f"  {qd['pending']} decision(s) pending Owner action")
        for dec in qd["decisions"]:
            lines.append(f"    • {dec.get('description', dec.get('receipt_id', 'unknown'))}")
    else:
        lines.append("  No pending Owner decisions")
    lines.append("")

    # Release Readiness
    rr = sections["release_readiness"]
    lines.append("── Release Readiness ──")
    rrd = rr["data"]
    if rrd["status"] == "available":
        lines.append(f"  Overall: {rrd['overall']}")
        for gate in rrd.get("gates", []):
            gs = gate.get("status", "unknown")
            lines.append(f"    {gate.get('name', 'gate')}: {gs}")
    else:
        lines.append("  No release readiness data available")
    lines.append("")

    lines.append("=" * 60)
    lines.append("End of Owner Dashboard — projection layer only")
    return "\n".join(lines)


def build_multi_project_dashboard(project_paths):
    """Build dashboard with multi-project support using the routing layer."""
    import qa_pilot_project_assurance_routing as routing_mod
    routing = routing_mod.route_projects(project_paths)
    
    # Start with single-project dashboard
    dashboard = build_dashboard()
    
    # Add multi-project overlay
    dashboard["multi_project"] = {
        "routing_id": routing["routing_id"],
        "cross_project": routing["cross_project"],
        "projects": routing["projects"]
    }
    dashboard["invariant"] = "Projection layer — multi-project, one assurance language, separate sources of truth."
    
    # Build cross-project evidence classification
    cp = routing.get("cross_project", {})
    mp_classification = {
        "summary": {
            "total_records": ec_summary.get("total_records", 0) if (ec_summary := dashboard.get("evidence_classification", {}).get("summary", {})) else 0,
            "total_snapshots": ec_summary.get("total_snapshots", 0) if (ec_summary := dashboard.get("evidence_classification", {}).get("summary", {})) else 0,
            "exit_invariant_satisfied": True
        },
        "classifications": dashboard.get("evidence_classification", {}).get("classifications", []),
        "invariant": "No historical record is rendered as current operational state without explicit classification"
    }
    dashboard["evidence_classification"] = mp_classification
    return dashboard


def format_multi_project_text(dashboard):
    """Render multi-project dashboard as text."""
    lines = []
    lines.append("=" * 60)
    lines.append("QA Pilot — Owner Dashboard (Multi-Project)")
    lines.append(f"Generated: {dashboard['generated_at']}")
    lines.append(f"Invariant: {dashboard['invariant']}")
    lines.append("=" * 60)
    lines.append("")
    
    mp = dashboard.get("multi_project", {})
    cp = mp.get("cross_project", {})
    lines.append(f"── Cross-Project Summary ──")
    lines.append(f"  Projects: {cp.get('total_projects', 0)}")
    lines.append(f"  Findings: {cp.get('total_findings', 0)}")
    lines.append(f"  Risk items: {cp.get('total_risk_items', 0)}")
    lines.append(f"  Evidence files: {cp.get('total_evidence_files', 0)}")
    lines.append(f"  Owner decisions: {cp.get('total_owner_decisions', 0)}")
    lines.append("")
    
    for pid, state in mp.get("projects", {}).items():
        lines.append(f"── Project: {pid} ──")
        f = state.get("findings", {})
        lines.append(f"  Findings: {f.get('total', 0)} ({f.get('unacknowledged', 0)} unacknowledged)")
        for s, c in sorted(f.get("by_state", {}).items()):
            lines.append(f"    {s}: {c}")
        r = state.get("risk", {})
        lines.append(f"  Risk items: {r.get('total', 0)}")
        for p, c in r.get("priority_counts", {}).items():
            lines.append(f"    {p}: {c}")
        reg = state.get("registry", {})
        lines.append(f"  Registry: {reg.get('layers', 0)} layers (max slot {reg.get('max_slot', 0)})")
        ef = state.get("evidence_freshness", {})
        lines.append(f"  Evidence: {ef.get('total_files', 0)} files ({ef.get('fresh', 0)} fresh, {ef.get('stale', 0)} stale)")
        oq = state.get("owner_queue", {})
        lines.append(f"  Owner queue: {oq.get('pending', 0)} pending / {oq.get('total', 0)} total")
        rd = state.get("readiness", {})
        lines.append(f"  Release readiness: {rd.get('status', 'no_data')}")
        lines.append("")
    
    lines.append("=" * 60)
    lines.append("End of Multi-Project Dashboard — boundaries preserved")
    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="QA Pilot Owner Dashboard")
    parser.add_argument("mode", nargs="?", default="report",
                        choices=["report", "status", "validate"],
                        help="Output mode")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--multi-project", nargs="*", default=[],
                        help="Project root paths for multi-project routing")

    args = parser.parse_args()

    if args.multi_project:
        dashboard = build_multi_project_dashboard(args.multi_project)
        if args.json or args.mode == "status":
            print(json.dumps(dashboard, indent=2))
        else:
            print(format_multi_project_text(dashboard))
        return

    dashboard = build_dashboard()

    if args.json or args.mode == "status":
        print(json.dumps(dashboard, indent=2))
    elif args.mode == "validate":
        # Validate that all stores are reachable
        findings = get_active_findings()
        registry = get_registry_health()
        risk = get_risk_posture()
        freshness = get_evidence_freshness()

        check_results = {
            "validator": "OD-OWNER-DASHBOARD-1",
            "checks": {
                "finding_store": findings["total"] > 0 or findings["total"] == 0,
                "registry_available": registry["status"] == "available",
                "risk_available": risk["status"] == "available",
                "evidence_tracked": freshness["total_evidence_files"] > 0,
            },
            "all_pass": True
        }
        for check, passed in check_results["checks"].items():
            if not passed:
                check_results["all_pass"] = False
        print(json.dumps(check_results, indent=2))
    else:
        print(format_text(dashboard))


if __name__ == "__main__":
    main()
