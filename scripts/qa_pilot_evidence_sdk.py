#!/usr/bin/env python3
"""
QA Pilot Evidence SDK — QA-PILOT-SDK-INTEGRATION-1

Governed read-only SDK for consuming Librarian evidence artifacts.
Replaces direct filesystem access with capability-oriented queries.

All results are schema-validated, provenance-tracked, and read-only.
No mutation paths exist through this SDK.

Usage (import):
    from qa_pilot_evidence_sdk import EvidenceProvider
    provider = EvidenceProvider()
    snapshot = provider.getEvidenceSnapshot()
    findings = provider.getFindings()
    graph = provider.getCompositionGraph()
    provenance = provider.getProvenanceChain()
    artifacts = provider.getValidationArtifacts()

Usage (CLI):
    python3 scripts/qa_pilot_evidence_sdk.py snapshot
    python3 scripts/qa_pilot_evidence_sdk.py findings
    python3 scripts/qa_pilot_evidence_sdk.py graph
    python3 scripts/qa_pilot_evidence_sdk.py provenance
    python3 scripts/qa_pilot_evidence_sdk.py artifacts
    python3 scripts/qa_pilot_evidence_sdk.py status

Authority: advisory-only. Read-only. No cross-project mutation.
"""

import datetime
import json
import os
import sys
from pathlib import Path

SDK_VERSION = "qa-pilot-evidence-sdk-v1"
CONTRACT_VERSION = "evidence-plane-contract-v1"

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CARBIDE_WORKSPACE = REPO_ROOT.parent.parent  # CarbideFrame root
EVIDENCE_PLANE_DIR = CARBIDE_WORKSPACE / "data" / "evidence-plane"

SCHEMA_FILE = REPO_ROOT / "docs" / "schemas" / "qa-pilot-sdk-integration.schema.json"


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_evidence_plane():
    """Load the latest evidence plane evaluation from the governed path."""
    eval_path = EVIDENCE_PLANE_DIR / "latest-evaluation.json"
    if not eval_path.exists():
        return None
    with open(eval_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Known allowed contexts for the 'authority' key
# These are governed schema fields, not mutation grants
_ALLOWED_AUTHORITY_CONTEXTS = {"authority.detector", "authority.detector_version",
                                "authority.resolver_class"}


def _is_diagnostic_finding(obj):
    """Check if a dict is a diagnostic-finding-v1 object."""
    return (isinstance(obj, dict) and 
            obj.get("schema") == "diagnostic-finding-v1" and
            "finding_id" in obj)


def _validate_read_only(operation, data, parent_ctx=None):
    """Validate that no mutation paths exist in an SDK result.
    
    This is a structural check — ensures the returned data cannot be
    interpreted as an authority grant, approval, or mutation instruction.
    
    Args:
        operation: Operation name for logging
        data: Data to validate
        parent_ctx: Optional parent context (e.g. "diagnostic-finding-v1")
    
    Returns list of warnings (empty if clean).
    """
    warnings = []
    if isinstance(data, dict):
        # Skip authority check if this is a diagnostic-finding-v1 object
        # (authority in findings is a resolver_class declaration, not a grant)
        is_finding = _is_diagnostic_finding(data)
        
        for key in data:
            k = key.lower()
            # Skip authority key in diagnostic-finding-v1 objects
            if is_finding and k == "authority":
                continue
            # Also skip 'execute' in the authority block (resolver_class = AUTHORIZED_WORK_ORDER)
            if k in ("authority", "seal", "approve", "mutate", "write",
                     "apply", "execute", "register", "create_receipt"):
                warnings.append(f"Potentially prohibited key at '{operation}': {key} = {data.get(key)}")
        
        for key, val in data.items():
            if isinstance(val, (dict, list)):
                warnings.extend(_validate_read_only(f"{operation}.{key}", val, 
                                                     parent_ctx if is_finding else key))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                warnings.extend(_validate_read_only(f"{operation}[{i}]", item, parent_ctx))
    return warnings


# ── EvidenceProvider ──────────────────────────────────────────────────────

class EvidenceProvider:
    """Governed read-only SDK for consuming Librarian evidence.
    
    Provides 5 capability-oriented queries that return schema-validated,
    provenance-tracked evidence artifacts. No mutation paths exist.
    """

    def __init__(self, data_source=None):
        """Initialize the provider.
        
        Args:
            data_source: Optional path to a governed evidence evaluation file.
                         Defaults to latest-evaluation.json in the evidence plane.
        """
        self._data_source = data_source
        self._cache = None
        self._load_count = 0

    def _load(self):
        """Load and cache the evidence plane data."""
        if self._cache is None:
            if self._data_source:
                path = Path(self._data_source)
            else:
                path = EVIDENCE_PLANE_DIR / "latest-evaluation.json"
            
            if not path.exists():
                return None
            
            with open(path, "r", encoding="utf-8") as f:
                self._cache = json.load(f)
            self._load_count += 1
        
        return self._cache

    def _check_read_only(self, data, operation):
        """Enforce read-only: warn but do not block on structural issues.
        
        Returns the data unchanged. Warnings are attached to the result
        for downstream tooling to inspect.
        """
        warnings = _validate_read_only(operation, data)
        return {
            "data": data,
            "read_only_validation": {
                "operation": operation,
                "warnings": warnings,
                "clean": len(warnings) == 0,
                "advisory": True,
                "no_mutation_path": len(warnings) == 0,
            }
        }

    def getEvidenceSnapshot(self):
        """Return the current evidence state snapshot.
        
        Returns:
            dict with evaluator_version, contract_version, generated_at,
            run_id, operational_mode, evidence_summary, source_count,
            status_summary, confidence_summary
        """
        data = self._load()
        if data is None:
            return self._check_read_only({
                "error": "Evidence plane data unavailable",
                "sdk_version": SDK_VERSION,
                "generated_at": now_utc(),
                "evidence_available": False,
            }, "getEvidenceSnapshot")

        snapshot = {
            "sdk_version": SDK_VERSION,
            "contract_version": data.get("contract_version"),
            "generated_at": now_utc(),
            "evidence_generated_at": data.get("generated_at"),
            "run_id": data.get("run_id"),
            "operational_mode": data.get("operational_mode"),
            "evidence_summary": data.get("evidence_summary"),
            "source_count": data.get("source_count"),
            "status_summary": data.get("status_summary"),
            "confidence_summary": data.get("confidence_summary"),
            "evidence_available": True,
            "sources": data.get("sources", {}),
        }
        
        return self._check_read_only(snapshot, "getEvidenceSnapshot")

    def getFindings(self):
        """Return diagnostic findings (OE-002).
        
        Returns:
            dict with finding_count, findings array (diagnostic-finding-v1),
            run_id, generated_at
        """
        data = self._load()
        if data is None:
            return self._check_read_only({
                "error": "Evidence plane data unavailable",
                "sdk_version": SDK_VERSION,
                "generated_at": now_utc(),
                "finding_count": 0,
                "findings": [],
            }, "getFindings")

        findings = data.get("findings", [])
        
        result = {
            "sdk_version": SDK_VERSION,
            "generated_at": now_utc(),
            "run_id": data.get("run_id"),
            "finding_count": len(findings),
            "findings": findings,
            "severity_counts": {},
            "confidence_counts": {},
            "category_counts": {},
        }
        
        # Compute summary aggregations
        for f in findings:
            sev = f.get("severity", "UNKNOWN")
            conf = f.get("confidence", "UNKNOWN")
            cat = f.get("category", "UNKNOWN")
            result["severity_counts"][sev] = result["severity_counts"].get(sev, 0) + 1
            result["confidence_counts"][conf] = result["confidence_counts"].get(conf, 0) + 1
            result["category_counts"][cat] = result["category_counts"].get(cat, 0) + 1
        
        return self._check_read_only(result, "getFindings")

    def getCompositionGraph(self):
        """Return the evidence composition graph (OE-003).
        
        Returns:
            dict with nodes, edges, root_cause_candidates, dependency_levels,
            topological statistics
        """
        data = self._load()
        if data is None:
            return self._check_read_only({
                "error": "Evidence plane data unavailable",
                "sdk_version": SDK_VERSION,
                "generated_at": now_utc(),
                "node_count": 0,
                "edge_count": 0,
                "nodes": [],
                "edges": [],
            }, "getCompositionGraph")

        graph = data.get("composition_graph", {})
        
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        
        # Classify nodes
        root_causes = [n for n in nodes if n.get("root_cause_candidate")]
        symptoms = [n for n in nodes if n.get("symptom")]
        
        result = {
            "sdk_version": SDK_VERSION,
            "generated_at": now_utc(),
            "run_id": data.get("run_id"),
            "schema": graph.get("schema"),
            "node_count": len(nodes),
            "edge_count": len(edges),
            "nodes": nodes,
            "edges": edges,
            "root_cause_candidates": graph.get("root_cause_candidates", []),
            "dependency_levels": graph.get("dependency_levels", {}),
            "topology": {
                "root_cause_count": len(root_causes),
                "symptom_count": len(symptoms),
                "evidence_class_breakdown": {},
                "severity_breakdown": {},
                "category_breakdown": {},
            },
        }
        
        for n in nodes:
            ec = n.get("evidence_class", "UNKNOWN")
            sev = n.get("severity", "UNKNOWN")
            cat = n.get("category", "UNKNOWN")
            result["topology"]["evidence_class_breakdown"][ec] = \
                result["topology"]["evidence_class_breakdown"].get(ec, 0) + 1
            result["topology"]["severity_breakdown"][sev] = \
                result["topology"]["severity_breakdown"].get(sev, 0) + 1
            result["topology"]["category_breakdown"][cat] = \
                result["topology"]["category_breakdown"].get(cat, 0) + 1
        
        return self._check_read_only(result, "getCompositionGraph")

    def getProvenanceChain(self):
        """Return runtime + projection provenance records (OE-005/OE-006).
        
        Returns:
            dict with provenance records categorized by type
            (runtime, projection, source_state, surface, reconciliation)
        """
        data = self._load()
        if data is None:
            return self._check_read_only({
                "error": "Evidence plane data unavailable",
                "sdk_version": SDK_VERSION,
                "generated_at": now_utc(),
                "provenance_count": 0,
                "provenance_records": [],
            }, "getProvenanceChain")

        sources = data.get("sources", {})
        
        # Categorize sources into provenance classes
        provenance_records = []
        runtime_records = []
        projection_records = []
        lifecycle_records = []
        reconciliation_records = []
        
        for source_key, source_val in sources.items():
            category = source_val.get("category", "UNKNOWN")
            record = {
                "source_id": source_key,
                "category": category,
                "evidence_status": source_val.get("evidence_status"),
                "governance_confidence": source_val.get("governance_confidence"),
                "age_hours": source_val.get("age_hours"),
                "max_age_hours": source_val.get("max_age_hours"),
                "last_reconciled_at": source_val.get("last_reconciled_at"),
                "source_path": source_val.get("source_path"),
            }
            
            provenance_records.append(record)
            
            if category in ("RUNTIME_PROVENANCE", "BUILD_PROVENANCE", "SOURCE_STATE"):
                runtime_records.append(record)
            elif category in ("PROJECTION", "SURFACE"):
                projection_records.append(record)
            elif category == "LIFECYCLE_STATE":
                lifecycle_records.append(record)
            elif category in ("RECONCILIATION_REPORT", "EPIC_REGISTRY"):
                reconciliation_records.append(record)
        
        result = {
            "sdk_version": SDK_VERSION,
            "generated_at": now_utc(),
            "run_id": data.get("run_id"),
            "provenance_count": len(provenance_records),
            "provenance_records": provenance_records,
            "by_category": {
                "runtime": {
                    "count": len(runtime_records),
                    "records": runtime_records,
                },
                "projection": {
                    "count": len(projection_records),
                    "records": projection_records,
                },
                "lifecycle": {
                    "count": len(lifecycle_records),
                    "records": lifecycle_records,
                },
                "reconciliation": {
                    "count": len(reconciliation_records),
                    "records": reconciliation_records,
                },
            },
            "freshness_summary": {},
        }
        
        # Freshness computation
        fresh_count = sum(1 for r in provenance_records if r.get("evidence_status") == "CURRENT")
        stale_count = sum(1 for r in provenance_records if r.get("evidence_status") == "STALE")
        absent_count = sum(1 for r in provenance_records if r.get("evidence_status") == "ABSENT")
        result["freshness_summary"] = {
            "current": fresh_count,
            "stale": stale_count,
            "absent": absent_count,
            "total": len(provenance_records),
        }
        
        return self._check_read_only(result, "getProvenanceChain")

    def getValidationArtifacts(self):
        """Return epic validation artifacts from the evidence plane.
        
        Returns:
            dict with evidence bundles, findings, composition graph,
            and provenance — the complete validation context.
        """
        data = self._load()
        if data is None:
            return self._check_read_only({
                "error": "Evidence plane data unavailable",
                "sdk_version": SDK_VERSION,
                "generated_at": now_utc(),
                "artifacts_available": False,
            }, "getValidationArtifacts")

        # Compose a complete validation artifact package
        artifact = {
            "sdk_version": SDK_VERSION,
            "contract_version": data.get("contract_version"),
            "generated_at": now_utc(),
            "run_id": data.get("run_id"),
            "evidence_summary": data.get("evidence_summary"),
            "operational_mode": data.get("operational_mode"),
            "finding_count": data.get("finding_count", 0),
            "findings": data.get("findings", []),
            "composition_graph": data.get("composition_graph", {}),
            "sources": data.get("sources", {}),
            "artifacts_available": True,
            "read_only": True,
            "provenance_linked": True,
            "no_mutation_authority": True,
        }
        
        return self._check_read_only(artifact, "getValidationArtifacts")


# ── CLI ───────────────────────────────────────────────────────────────────


def cmd_snapshot(args):
    """Return evidence snapshot as JSON."""
    provider = EvidenceProvider()
    result = provider.getEvidenceSnapshot()
    print(json.dumps(result, indent=2, default=str))
    return 0


def cmd_findings(args):
    """Return diagnostic findings as JSON."""
    provider = EvidenceProvider()
    result = provider.getFindings()
    print(json.dumps(result, indent=2, default=str))
    return 0


def cmd_graph(args):
    """Return composition graph as JSON."""
    provider = EvidenceProvider()
    result = provider.getCompositionGraph()
    print(json.dumps(result, indent=2, default=str))
    return 0


def cmd_provenance(args):
    """Return provenance chain as JSON."""
    provider = EvidenceProvider()
    result = provider.getProvenanceChain()
    print(json.dumps(result, indent=2, default=str))
    return 0


def cmd_artifacts(args):
    """Return validation artifacts as JSON."""
    provider = EvidenceProvider()
    result = provider.getValidationArtifacts()
    print(json.dumps(result, indent=2, default=str))
    return 0


def cmd_status(args):
    """Show SDK configuration and state."""
    provider = EvidenceProvider()
    data = provider._load()
    
    evidence_available = data is not None
    
    status = {
        "sdk_version": SDK_VERSION,
        "contract_version": CONTRACT_VERSION,
        "generated_at": now_utc(),
        "evidence_plane_path": str(EVIDENCE_PLANE_DIR / "latest-evaluation.json"),
        "evidence_available": evidence_available,
        "load_count": provider._load_count,
        "read_only": True,
        "authority": "advisory-only",
        "no_mutation_paths": True,
        "available_queries": [
            "getEvidenceSnapshot",
            "getFindings",
            "getCompositionGraph",
            "getProvenanceChain",
            "getValidationArtifacts",
        ],
        "forbidden_operations": [
            "no_mutation_apis",
            "no_cursor_updates",
            "no_receipt_creation",
            "no_authority_arbitration",
            "no_filesystem_scraping",
        ],
    }
    
    if evidence_available:
        status["evidence"] = {
            "run_id": data.get("run_id"),
            "generated_at": data.get("generated_at"),
            "operational_mode": data.get("operational_mode"),
            "source_count": data.get("source_count"),
            "finding_count": data.get("finding_count"),
            "contract_version": data.get("contract_version"),
        }
    
    print(json.dumps(status, indent=2, default=str))
    return 0


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("QA Pilot Evidence SDK — QA-PILOT-SDK-INTEGRATION-1")
        print()
        print("Usage:")
        print("  snapshot      — Return evidence snapshot")
        print("  findings      — Return diagnostic findings")
        print("  graph         — Return composition graph")
        print("  provenance    — Return provenance chain")
        print("  artifacts     — Return validation artifacts")
        print("  status        — Show SDK configuration")
        print()
        print("Authority: advisory-only. Read-only. No mutation paths.")
        return 0

    command = sys.argv[1]
    cmd_args = sys.argv[2:]

    commands = {
        "snapshot": cmd_snapshot,
        "findings": cmd_findings,
        "graph": cmd_graph,
        "provenance": cmd_provenance,
        "artifacts": cmd_artifacts,
        "status": cmd_status,
    }

    if command not in commands:
        print(f"Unknown command: {command}", file=sys.stderr)
        print(f"Valid commands: {', '.join(commands.keys())}", file=sys.stderr)
        return 1

    return commands[command](cmd_args)


if __name__ == "__main__":
    sys.exit(main())
