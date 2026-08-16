#!/usr/bin/env python3
"""
Runtime Evidence Qualification Engine — QA-PILOT-RUNTIME-EVIDENCE-QUALIFICATION-1

Evaluates runtime evidence records against 5 qualification checks:
1. Provenance completeness
2. Evidence integrity
3. Evidence usability
4. Freshness semantics
5. Authority boundary

Commands:
  qualify <file>     Qualify a single evidence record
  qualify-all        Qualify all records in the evidence store
  status             Show qualification results summary
"""

import sys
import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# --- Configuration ---

PROJECT_ROOT = Path(__file__).parent.parent
EVIDENCE_STORE = PROJECT_ROOT / "data" / "runtime-evidence"
RECORDS_DIR = EVIDENCE_STORE / "records"
SNAPSHOTS_DIR = EVIDENCE_STORE / "snapshots"
INDEX_FILE = EVIDENCE_STORE / "index.json"
RESULTS_FILE = EVIDENCE_STORE / "qualification-results.json"

# Freshness thresholds (seconds)
RECORD_THRESHOLDS = {
    "current": 60 * 60,      # 60 minutes
    "historical": 4 * 60 * 60,  # 4 hours
}
SNAPSHOT_REFRESH_INTERVAL = 15 * 60  # 15 minutes

# Authority boundary fields (CAG-RUNTIME-008)
AUTHORITY_FIELDS = {"authorization", "dispatch", "executed", "sealed", "approved", "owner_decision"}

# Required provenance fields
REQUIRED_PROVENANCE_FIELDS = [
    ("provenance", "execution_identity", "node_identity", "project_id"),
    ("provenance", "execution_identity", "node_identity", "project_type"),
    ("provenance", "execution_identity", "node_identity", "node_id"),
    ("provenance", "execution_identity", "runtime_identity", "runtime_id"),
    ("provenance", "execution_identity", "runtime_identity", "runtime_type"),
    ("provenance", "execution_identity", "runtime_identity", "runtime_version"),
    ("provenance", "execution_identity", "agent_identity", "agent_id"),
    ("provenance", "execution_identity", "agent_identity", "agent_version"),
    ("provenance", "execution_identity", "model_identity", "provider"),
    ("provenance", "execution_identity", "model_identity", "model"),
    ("provenance", "execution_identity", "session_identity", "session_id"),
    ("provenance", "execution_identity", "session_identity", "started_at"),
    ("provenance", "governance_context", "project_identity", "project_id"),
    ("provenance", "governance_context", "project_identity", "project_type"),
    ("provenance", "governance_context", "authority_scope", "scope"),
    ("provenance", "governance_context", "authority_scope", "constraints"),
]


def load_json(path):
    """Load a JSON file."""
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    """Save data to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def get_nested(obj, *keys):
    """Get a nested field from a dict. Returns None if any key is missing."""
    current = obj
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current


def check_provenance_completeness(record):
    """Check Q1: Provenance completeness."""
    findings = []
    
    for field_path in REQUIRED_PROVENANCE_FIELDS:
        value = get_nested(record, *field_path)
        if value is None:
            findings.append({
                "check": "provenance_completeness",
                "severity": "high",
                "field": ".".join(field_path),
                "message": f"Missing required provenance field: {'.'.join(field_path)}"
            })
        elif isinstance(value, str) and value.strip() == "":
            findings.append({
                "check": "provenance_completeness",
                "severity": "medium",
                "field": ".".join(field_path),
                "message": f"Empty provenance field: {'.'.join(field_path)}"
            })
    
    return {
        "check": "provenance_completeness",
        "passed": len(findings) == 0,
        "findings": findings,
        "fields_checked": len(REQUIRED_PROVENANCE_FIELDS),
        "fields_present": len(REQUIRED_PROVENANCE_FIELDS) - len(findings)
    }


def check_evidence_integrity(record, file_path=None):
    """Check Q2: Evidence integrity."""
    findings = []
    
    # Check evidence_id exists
    evidence_id = record.get("evidence_id")
    if not evidence_id:
        findings.append({
            "check": "evidence_integrity",
            "severity": "high",
            "field": "evidence_id",
            "message": "Missing evidence_id"
        })
    
    # Check schema_version exists
    schema_version = record.get("schema_version")
    if not schema_version:
        findings.append({
            "check": "evidence_integrity",
            "severity": "medium",
            "field": "schema_version",
            "message": "Missing schema_version"
        })
    
    # Check evidence_class exists
    evidence_class = record.get("evidence_class")
    if not evidence_class:
        findings.append({
            "check": "evidence_integrity",
            "severity": "high",
            "field": "evidence_class",
            "message": "Missing evidence_class"
        })
    elif evidence_class not in ("record", "snapshot"):
        findings.append({
            "check": "evidence_integrity",
            "severity": "high",
            "field": "evidence_class",
            "message": f"Invalid evidence_class: {evidence_class}"
        })
    
    # Check timestamps
    freshness = record.get("freshness", {})
    captured_at = freshness.get("captured_at")
    validated_at = freshness.get("validated_at")
    
    if not captured_at:
        findings.append({
            "check": "evidence_integrity",
            "severity": "high",
            "field": "freshness.captured_at",
            "message": "Missing freshness.captured_at"
        })
    
    if not validated_at:
        findings.append({
            "check": "evidence_integrity",
            "severity": "medium",
            "field": "freshness.validated_at",
            "message": "Missing freshness.validated_at"
        })
    
    # Check timestamp consistency (captured_at <= validated_at)
    if captured_at and validated_at:
        try:
            ts_captured = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
            ts_validated = datetime.fromisoformat(validated_at.replace("Z", "+00:00"))
            if ts_captured > ts_validated:
                findings.append({
                    "check": "evidence_integrity",
                    "severity": "high",
                    "field": "freshness.timestamps",
                    "message": "captured_at is after validated_at — timestamp inconsistency"
                })
        except ValueError:
            findings.append({
                "check": "evidence_integrity",
                "severity": "medium",
                "field": "freshness.timestamps",
                "message": "Could not parse timestamps for consistency check"
            })
    
    # Check custody
    custody = record.get("custody", {})
    if not custody.get("origin"):
        findings.append({
            "check": "evidence_integrity",
            "severity": "medium",
            "field": "custody.origin",
            "message": "Missing custody.origin"
        })
    
    return {
        "check": "evidence_integrity",
        "passed": len(findings) == 0,
        "findings": findings
    }


def compute_freshness_label(evidence_class, captured_at_str):
    """Compute the expected freshness label for an evidence record."""
    now = datetime.now(timezone.utc)
    try:
        ts = datetime.fromisoformat(captured_at_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return "unknown"
    
    age_seconds = (now - ts).total_seconds()
    
    if evidence_class == "record":
        if age_seconds < RECORD_THRESHOLDS["current"]:
            return "current"
        elif age_seconds < RECORD_THRESHOLDS["historical"]:
            return "historical"
        else:
            return "archived"
    elif evidence_class == "snapshot":
        if age_seconds < SNAPSHOT_REFRESH_INTERVAL:
            return "current"
        else:
            return "stale"
    else:
        return "unknown"


def check_freshness_semantics(record):
    """Check Q4: Freshness semantics."""
    findings = []
    
    evidence_class = record.get("evidence_class")
    freshness = record.get("freshness", {})
    captured_at = freshness.get("captured_at")
    declared_label = freshness.get("confidence_label")
    
    if not evidence_class:
        findings.append({
            "check": "freshness_semantics",
            "severity": "high",
            "field": "evidence_class",
            "message": "Cannot evaluate freshness without evidence_class"
        })
        return {
            "check": "freshness_semantics",
            "passed": False,
            "findings": findings
        }
    
    if not captured_at:
        findings.append({
            "check": "freshness_semantics",
            "severity": "high",
            "field": "freshness.captured_at",
            "message": "Cannot evaluate freshness without captured_at"
        })
        return {
            "check": "freshness_semantics",
            "passed": False,
            "findings": findings
        }
    
    expected_label = compute_freshness_label(evidence_class, captured_at)
    
    if declared_label != expected_label:
        findings.append({
            "check": "freshness_semantics",
            "severity": "medium",
            "field": "freshness.confidence_label",
            "message": f"Freshness label mismatch: declared='{declared_label}', expected='{expected_label}' (class={evidence_class})"
        })
    
    # Check refresh_expected_at for snapshots
    if evidence_class == "snapshot":
        refresh_expected = freshness.get("refresh_expected_at")
        if refresh_expected is None:
            findings.append({
                "check": "freshness_semantics",
                "severity": "medium",
                "field": "freshness.refresh_expected_at",
                "message": "Snapshot missing refresh_expected_at"
            })
    
    # Verify records don't get "stale" label
    if evidence_class == "record" and declared_label == "stale":
        findings.append({
            "check": "freshness_semantics",
            "severity": "high",
            "field": "freshness.confidence_label",
            "message": "Record has 'stale' label — records should never be stale (only snapshots)"
        })
    
    return {
        "check": "freshness_semantics",
        "passed": len(findings) == 0,
        "findings": findings,
        "expected_label": expected_label,
        "declared_label": declared_label
    }


def check_authority_boundary(record):
    """Check Q5: Authority boundary (CAG-RUNTIME-008)."""
    findings = []
    
    def check_obj(obj, path=""):
        if isinstance(obj, dict):
            for key in obj:
                full_path = f"{path}.{key}" if path else key
                if key in AUTHORITY_FIELDS:
                    findings.append({
                        "check": "authority_boundary",
                        "severity": "critical",
                        "field": full_path,
                        "message": f"Authority field found: {full_path} — CAG-RUNTIME-008 violation"
                    })
                check_obj(obj[key], full_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_obj(item, f"{path}[{i}]")
    
    check_obj(record)
    
    return {
        "check": "authority_boundary",
        "passed": len(findings) == 0,
        "findings": findings
    }


def check_schema_conformance(record):
    """Check Q5: Schema conformance."""
    findings = []
    
    event_type = None
    if record.get("evidence_class") == "record":
        # Determine event type from context
        context = record.get("context", {})
        exec_ctx = context.get("execution_context", {})
        source_schema = exec_ctx.get("source_schema", "")
        if "action" in source_schema:
            event_type = "runtime_action"
        elif "lifecycle" in source_schema:
            event_type = "runtime_lifecycle"
    elif record.get("evidence_class") == "snapshot":
        event_type = "runtime_resource"
    
    # Check required fields based on evidence class
    required_fields = ["evidence_id", "schema_version", "evidence_class", "identity", "observation", "context", "custody", "freshness", "provenance"]
    
    for field in required_fields:
        if field not in record:
            findings.append({
                "check": "schema_conformance",
                "severity": "high",
                "field": field,
                "message": f"Missing required field: {field}"
            })
    
    return {
        "check": "schema_conformance",
        "passed": len(findings) == 0,
        "findings": findings,
        "event_type": event_type
    }


def qualify_record(record, file_path=None):
    """Run all 5 qualification checks against a record."""
    checks = [
        check_provenance_completeness(record),
        check_evidence_integrity(record, file_path),
        check_freshness_semantics(record),
        check_authority_boundary(record),
        check_schema_conformance(record),
    ]
    
    all_passed = all(c["passed"] for c in checks)
    all_findings = []
    for c in checks:
        all_findings.extend(c["findings"])
    
    # Determine disposition
    critical_findings = [f for f in all_findings if f.get("severity") == "critical"]
    high_findings = [f for f in all_findings if f.get("severity") == "high"]
    
    if critical_findings:
        disposition = "FINDING"
        disposition_reason = "critical_authority_violation"
    elif high_findings:
        disposition = "FINDING"
        disposition_reason = "high_severity_findings"
    elif all_findings:
        disposition = "FINDING"
        disposition_reason = "findings_present"
    else:
        disposition = "PASS"
        disposition_reason = "all_checks_pass"
    
    return {
        "evidence_id": record.get("evidence_id", "unknown"),
        "evidence_class": record.get("evidence_class", "unknown"),
        "disposition": disposition,
        "disposition_reason": disposition_reason,
        "checks": checks,
        "total_findings": len(all_findings),
        "findings": all_findings,
        "qualified_at": datetime.now(timezone.utc).isoformat(),
        "qualified_by": "scripts/qualify-runtime-evidence.py",
        "advisory_only": True
    }


def cmd_qualify(args):
    """Qualify a single evidence record."""
    if len(args) < 1:
        print("Usage: qualify <file>")
        sys.exit(1)
    
    filepath = Path(args[0])
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)
    
    record = load_json(filepath)
    result = qualify_record(record, filepath)
    
    print(f"Qualifying: {filepath.name}")
    print(f"Evidence ID: {result['evidence_id']}")
    print(f"Evidence class: {result['evidence_class']}")
    print(f"Disposition: {result['disposition']} ({result['disposition_reason']})")
    print()
    
    for check in result["checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"  [{status}] {check['check']}")
        for f in check["findings"]:
            print(f"         {f['severity'].upper()}: {f['message']}")
    
    print(f"\nTotal findings: {result['total_findings']}")


def cmd_qualify_all(args):
    """Qualify all records in the evidence store."""
    results = []
    total = 0
    passed = 0
    failed = 0
    
    for dir_path in [RECORDS_DIR, SNAPSHOTS_DIR]:
        if not dir_path.exists():
            continue
        for f in sorted(dir_path.glob("*.json")):
            total += 1
            record = load_json(f)
            result = qualify_record(record, f)
            results.append(result)
            
            if result["disposition"] == "PASS":
                passed += 1
            else:
                failed += 1
    
    # Save results
    output = {
        "suite_id": "RUNTIME-EVIDENCE-QUALIFICATION-1",
        "contract_ref": "runtime-evidence-ingestion-contract",
        "start_time": results[0]["qualified_at"] if results else None,
        "end_time": results[-1]["qualified_at"] if results else None,
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "findings": sum(r["total_findings"] for r in results),
        "evidence_records": [r["evidence_id"] for r in results],
        "layers": ["provenance_completeness", "evidence_integrity", "freshness_semantics", "authority_boundary", "schema_conformance"],
        "disposition": "PASS" if failed == 0 else "FINDING",
        "results": results,
        "advisory_only": True,
        "custody": "qa-pilot-local",
        "librarian_impact": "none"
    }
    
    save_json(RESULTS_FILE, output)
    
    print(f"Runtime Evidence Qualification — Suite: RUNTIME-EVIDENCE-QUALIFICATION-1")
    print(f"{'='*60}")
    print(f"Total records:  {total}")
    print(f"Passed:         {passed}")
    print(f"Failed:         {failed}")
    print(f"Findings:       {output['findings']}")
    print(f"Disposition:    {output['disposition']}")
    print()
    
    for r in results:
        status = "PASS" if r["disposition"] == "PASS" else "FAIL"
        print(f"  [{status}] {r['evidence_id']} ({r['evidence_class']})")
        for f in r["findings"]:
            print(f"         {f['severity'].upper()}: {f['message']}")
    
    print(f"\nResults saved to: {RESULTS_FILE}")


def cmd_status(args):
    """Show qualification results summary."""
    if not RESULTS_FILE.exists():
        print("No qualification results found. Run 'qualify-all' first.")
        return
    
    results = load_json(RESULTS_FILE)
    
    print(f"Runtime Evidence Qualification — Suite: {results['suite_id']}")
    print(f"{'='*60}")
    print(f"Contract:       {results['contract_ref']}")
    print(f"Total records:  {results['total_tests']}")
    print(f"Passed:         {results['passed']}")
    print(f"Failed:         {results['failed']}")
    print(f"Findings:       {results['findings']}")
    print(f"Disposition:    {results['disposition']}")
    print(f"Qualified at:   {results['start_time']}")
    print(f"Advisory only:  {results['advisory_only']}")


COMMANDS = {
    "qualify": cmd_qualify,
    "qualify-all": cmd_qualify_all,
    "status": cmd_status,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        print(f"Commands: {', '.join(COMMANDS.keys())}")
        sys.exit(0)
    
    cmd = sys.argv[1]
    args = sys.argv[2:]
    COMMANDS[cmd](args)


if __name__ == "__main__":
    main()
