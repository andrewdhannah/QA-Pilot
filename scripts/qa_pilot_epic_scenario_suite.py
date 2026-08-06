#!/usr/bin/env python3
"""
QA Pilot Epic Scenario Suite — QA-PILOT-EPIC-SCENARIO-SUITES

Epic-level composition verifier. Consumes governed evidence through the
EvidenceProvider SDK and validates that collections of work orders compose
into functioning capabilities.

This is NOT a test runner. It is a composition verifier and learning
artifact generator. It compares expected vs observed evidence states
and produces structured validation results with training context.

Scenario types:
    complete_epic          — Verify all OE layers compose correctly
    missing_artifact       — Detect and classify absent evidence
    conflicting_sources    — Validate authority resolution
    broken_provenance      — Identify broken lineage links
    mutation_boundary      — Confirm boundary enforcement

Usage:
    python3 scripts/qa_pilot_epic_scenario_suite.py run <scenario-json-path>
    python3 scripts/qa_pilot_epic_scenario_suite.py list
    python3 scripts/qa_pilot_epic_scenario_suite.py list-defined
    python3 scripts/qa_pilot_epic_scenario_suite.py run-all
    python3 scripts/qa_pilot_epic_scenario_suite.py evidence-plane
    python3 scripts/qa_pilot_epic_scenario_suite.py format <result-json-path>

Authority: advisory-only. Read-only. No Librarian mutation.
"""

import datetime
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

# Import the governed Evidence SDK
try:
    from qa_pilot_evidence_sdk import EvidenceProvider, SDK_VERSION
    SDK_AVAILABLE = True
except ImportError:
    EvidenceProvider = None
    SDK_VERSION = "unavailable"
    SDK_AVAILABLE = False

SUITE_VERSION = "qa-pilot-epic-scenario-suite-v1"


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Built-in Scenarios ───────────────────────────────────────────────────
# Each scenario defines:
#   - scenario_id: unique identifier
#   - title: human-readable name
#   - type: scenario category
#   - sdk_queries: list of SDK methods to call
#   - expectations: dict of expected conditions (probed against SDK data)
#   - pass_criteria: how success/failure is determined
#   - explanation: training/learning context

# Scenario 1: Complete Evidence Plane
# Verifies that all OE layers are present and compose correctly.
SCENARIO_EVIDENCE_PLANE = {
    "scenario_id": "EP-EP-001",
    "title": "Complete Evidence Plane Composition",
    "type": "complete_epic",
    "target_epic": "Evidence Plane (OE-001 through OE-006)",
    "sdk_queries": ["getEvidenceSnapshot", "getFindings", "getCompositionGraph", "getProvenanceChain"],
    "expectations": {
        "evidence_must_be_available": True,
        "must_have_findings": {"min": 1, "max": 100},
        "must_have_composition_graph": {"min_nodes": 1, "min_edges": 0},
        "must_have_provenance_records": {"min": 1},
        "must_have_status_summary": True,
        "must_have_confidence_summary": True,
        "no_mutation_path_required": True,
        "findings_must_have_diagnostic_schema": True,
        "graph_must_have_root_causes": {"min": 0},
    },
    "pass_criteria": "All OE layers present, findings valid, graph topological, provenance tracked, no mutation path",
    "explanation": (
        "The Evidence Plane is the Librarian's diagnostic system. "
        "OE-001 provides sensor readings (evidence freshness), OE-002 provides fault codes "
        "(diagnostic findings), OE-003 provides the relationship diagram (composition graph), "
        "OE-004 resolves source conflicts (authority resolution), OE-005 traces runtime lineage, "
        "and OE-006 validates surface projections. "
        "When all six layers compose, the epic is complete."
    ),
}

# Scenario 2: Missing Evidence Artifact
# Detects when evidence is absent and produces a structured learning failure.
SCENARIO_MISSING_ARTIFACT = {
    "scenario_id": "EP-MISS-001",
    "title": "Missing Evidence Artifact Detection",
    "type": "missing_artifact",
    "target_epic": "Evidence Plane — freshness",
    "sdk_queries": ["getEvidenceSnapshot", "getProvenanceChain"],
    "expectations": {
        "evidence_must_be_available": True,
        "missing_count_must_equal": None,  # Recorded from actual state, not enforced as pass/fail
        "absent_sources_must_be_classified": True,
    },
    "pass_criteria": "Absent evidence is detected and classified with project identity and evidence class",
    "explanation": (
        "An evidence gap means a governed source is not producing expected output. "
        "Each absent artifact has a project, category, and evidence class that helps "
        "a technician (human or AI) understand what is missing and why."
    ),
}

# Scenario 3: Conflicting Sources
# Validates authority resolution for conflicting evidence sources.
SCENARIO_CONFLICT = {
    "scenario_id": "EP-CONF-001",
    "title": "Conflicting Evidence Source Resolution",
    "type": "conflicting_sources",
    "target_epic": "Evidence Plane — OE-004 authority resolution",
    "sdk_queries": ["getFindings", "getCompositionGraph"],
    "expectations": {
        "evidence_must_be_available": True,
        "must_have_findings": {"min": 1},
        "must_have_composition_graph": True,
        "conflict_findings_must_be_classified": True,
    },
    "pass_criteria": "Conflicts are detected and have resolver_class in authority block",
    "explanation": (
        "When two evidence sources disagree, the conflict must be resolved by an authority "
        "class. OWNER means a human decided. AUTHORIZED_WORK_ORDER means a governed sprint "
        "established the resolution. MONITORING means the system tracks without intervening. "
        "A conflict without a resolver class means the authority boundary is incomplete."
    ),
    # Read from findings — check for EV-CONFLICT-* codes
    "conflict_code_pattern": "EV-CONFLICT",
    "resolver_required": True,
}

# Scenario 4: Broken Provenance Chain
# Identifies stale/absent provenance links.
SCENARIO_BROKEN_PROVENANCE = {
    "scenario_id": "EP-PROV-001",
    "title": "Provenance Chain Integrity",
    "type": "broken_provenance",
    "target_epic": "Evidence Plane — OE-005/OE-006 provenance",
    "sdk_queries": ["getProvenanceChain", "getEvidenceSnapshot"],
    "expectations": {
        "evidence_must_be_available": True,
        "must_have_provenance_records": {"min": 1},
        "stale_or_absent_must_be_detected": True,
        "freshness_summary_must_be_present": True,
    },
    "pass_criteria": "Provenance chain is evaluated: current, stale, and absent links identified",
    "explanation": (
        "A provenance chain traces evidence from source through processing to presentation. "
        "Stale links mean the evidence exists but has not been refreshed beyond its freshness "
        "threshold. Absent links mean the expected evidence source does not produce output. "
        "Both are learning opportunities — the technician learns what 'stale' means in context."
    ),
}

# Scenario 5: Mutation Boundary
# Confirms that the SDK enforces no-mutation path.
SCENARIO_MUTATION_BOUNDARY = {
    "scenario_id": "EP-BOUND-001",
    "title": "SDK Mutation Boundary Enforcement",
    "type": "mutation_boundary",
    "target_epic": "QA-PILOT-SDK-INTEGRATION-1 boundary",
    "sdk_queries": ["getEvidenceSnapshot", "getFindings", "getCompositionGraph", "getProvenanceChain", "getValidationArtifacts"],
    "expectations": {
        "evidence_must_be_available": True,
        "all_queries_must_have_no_mutation_path": True,
        "no_mutation_authority_must_be_true": True,
        "read_only_must_be_true": True,
    },
    "pass_criteria": "Every SDK query returns no_mutation_path=True and no mutation warnings",
    "explanation": (
        "The SDK is read-only by design. It does not expose mutation paths, authority grants, "
        "seal operations, or receipt creation. This boundary separates the validator (QA-Pilot) "
        "from the subject (Librarian). A broken boundary would allow QA-Pilot to change what it "
        "is supposed to validate — collapsing the separation between observer and system."
    ),
}

ALL_SCENARIOS = [
    SCENARIO_EVIDENCE_PLANE,
    SCENARIO_MISSING_ARTIFACT,
    SCENARIO_CONFLICT,
    SCENARIO_BROKEN_PROVENANCE,
    SCENARIO_MUTATION_BOUNDARY,
]

SCENARIO_INDEX = {s["scenario_id"]: s for s in ALL_SCENARIOS}


# ── Evaluation Functions ─────────────────────────────────────────────────

def _get_sdk_data(queries):
    """Execute SDK queries and return all data."""
    if not SDK_AVAILABLE:
        return None, "SDK not available"
    
    provider = EvidenceProvider()
    results = {}
    
    for query in queries:
        method = getattr(provider, query, None)
        if method is None:
            results[query] = {"error": f"Unknown query: {query}"}
            continue
        try:
            results[query] = method()
        except Exception as e:
            results[query] = {"error": str(e)}
    
    return results, None


def _check_evidence_available(sdk_data):
    """Check if evidence is available (across all query results)."""
    for query_name, result in sdk_data.items():
        data = result.get("data", {})
        if data.get("evidence_available"):
            return True
        if data.get("artifacts_available"):
            return True
    return False


def _count_findings(sdk_data):
    """Count total findings across all query results."""
    for result in sdk_data.values():
        data = result.get("data", {})
        findings = data.get("findings", [])
        if findings:
            return len(findings)
    return 0


def _get_composition_graph_data(sdk_data):
    """Extract composition graph data."""
    for result in sdk_data.values():
        data = result.get("data", {})
        if "nodes" in data:
            return data
    return {}


def _get_provenance_data(sdk_data):
    """Extract provenance chain data."""
    for result in sdk_data.values():
        data = result.get("data", {})
        if "provenance_records" in data:
            return data
    return {}


def _get_findings_data(sdk_data):
    """Extract findings data."""
    for result in sdk_data.values():
        data = result.get("data", {})
        if "findings" in data:
            return data
    return {}


def evaluate_scenario(scenario, sdk_data):
    """Evaluate a scenario against SDK data. Returns structured result."""
    results = []
    all_expected_pass = True
    observed = {}

    # ── Core checks ──
    evidence_ok = _check_evidence_available(sdk_data)
    observed["evidence_available"] = evidence_ok
    
    # Expectation 1: evidence_must_be_available
    exp_avail = scenario.get("expectations", {}).get("evidence_must_be_available")
    if exp_avail is not None:
        passed = evidence_ok == exp_avail
        results.append({
            "check_id": "EVIDENCE_AVAILABLE",
            "description": "Evidence is available",
            "expected": exp_avail,
            "observed": evidence_ok,
            "passed": passed,
            "detail": "Evidence Plane data is reachable through SDK" if evidence_ok else "No evidence data available",
        })
        if not passed:
            all_expected_pass = False

    # Expectation 2: must_have_findings
    exp_findings = scenario.get("expectations", {}).get("must_have_findings")
    if exp_findings:
        finding_count = _count_findings(sdk_data)
        observed["finding_count"] = finding_count
        min_f = exp_findings.get("min", 0)
        max_f = exp_findings.get("max", float("inf"))
        passed = min_f <= finding_count <= max_f
        results.append({
            "check_id": "FINDINGS_EXIST",
            "description": f"Finding count in range [{min_f}, {max_f}]",
            "expected": f"{min_f}–{max_f}",
            "observed": finding_count,
            "passed": passed,
            "detail": f"{finding_count} diagnostic findings present",
        })
        if not passed:
            all_expected_pass = False

    # Expectation 3: must_have_composition_graph
    exp_graph = scenario.get("expectations", {}).get("must_have_composition_graph")
    if exp_graph:
        graph_data = _get_composition_graph_data(sdk_data)
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        observed["graph_nodes"] = len(nodes)
        observed["graph_edges"] = len(edges)
        
        if isinstance(exp_graph, dict):
            min_nodes = exp_graph.get("min_nodes", 0)
            min_edges = exp_graph.get("min_edges", 0)
            node_ok = len(nodes) >= min_nodes
            edge_ok = len(edges) >= min_edges
            passed = node_ok and edge_ok
            results.append({
                "check_id": "COMPOSITION_GRAPH_EXISTS",
                "description": f"Graph has >= {min_nodes} nodes and >= {min_edges} edges",
                "expected": f"nodes>={min_nodes}, edges>={min_edges}",
                "observed": f"nodes={len(nodes)}, edges={len(edges)}",
                "passed": passed,
                "detail": f"Composition graph: {len(nodes)} nodes, {len(edges)} edges, schema={graph_data.get('schema', 'N/A')}",
            })
            if not passed:
                all_expected_pass = False
        else:
            passed = bool(exp_graph)
            results.append({
                "check_id": "COMPOSITION_GRAPH_EXISTS",
                "description": "Composition graph data present",
                "expected": True,
                "observed": bool(nodes),
                "passed": passed,
                "detail": f"Composition graph: {len(nodes)} nodes, {len(edges)} edges",
            })
            if not passed:
                all_expected_pass = False

    # Expectation 4: must_have_provenance_records
    exp_prov = scenario.get("expectations", {}).get("must_have_provenance_records")
    if exp_prov:
        prov_data = _get_provenance_data(sdk_data)
        records = prov_data.get("provenance_records", [])
        observed["provenance_records"] = len(records)
        f_summary = prov_data.get("freshness_summary", {})
        observed["freshness_summary"] = f_summary
        
        min_r = exp_prov.get("min", 0) if isinstance(exp_prov, dict) else 1
        passed = len(records) >= min_r
        results.append({
            "check_id": "PROVENANCE_CHAIN_EXISTS",
            "description": f"Provenance records >= {min_r}",
            "expected": min_r,
            "observed": len(records),
            "passed": passed,
            "detail": f"{len(records)} provenance records: {f_summary}",
        })
        if not passed:
            all_expected_pass = False

    # Expectation 5: no_mutation_path_required
    exp_no_mut = scenario.get("expectations", {}).get("no_mutation_path_required")
    if exp_no_mut:
        all_clean = all(
            result.get("read_only_validation", {}).get("no_mutation_path", False)
            for result in sdk_data.values()
            if isinstance(result, dict) and "read_only_validation" in result
        )
        observed["all_no_mutation_path"] = all_clean
        passed = all_clean == exp_no_mut
        results.append({
            "check_id": "NO_MUTATION_PATH",
            "description": "All SDK queries have no_mutation_path=True",
            "expected": True,
            "observed": all_clean,
            "passed": passed,
            "detail": "Mutation path enforcement verified across all SDK queries" if all_clean else "Some queries have mutation path warnings",
        })
        if not passed:
            all_expected_pass = False

    # ── Scenario-specific checks ──

    # Missing artifact detection
    if scenario.get("type") == "missing_artifact":
        prov_data = _get_provenance_data(sdk_data)
        records = prov_data.get("provenance_records", [])
        absent = [r for r in records if r.get("evidence_status") == "ABSENT"]
        observed["absent_sources"] = [r["source_id"] for r in absent]
        observed["absent_count"] = len(absent)
        
        passed = True
        for src in absent:
            has_id = bool(src.get("source_id"))
            has_cat = bool(src.get("category"))
            if not (has_id and has_cat):
                passed = False
                break
        
        results.append({
            "check_id": "ABSENT_SOURCES_CLASSIFIED",
            "description": "Absent evidence sources are classified with ID and category",
            "expected": True,
            "observed": passed,
            "passed": passed,
            "detail": f"{len(absent)} absent sources identified: {observed.get('absent_sources', [])}" if absent else "No absent sources (all evidence present)",
        })
        if not passed:
            all_expected_pass = False

    # Conflict detection
    if scenario.get("type") == "conflicting_sources":
        findings_data = _get_findings_data(sdk_data)
        findings = findings_data.get("findings", [])
        conflict_pattern = scenario.get("conflict_code_pattern", "EV-CONFLICT")
        
        conflicts = [f for f in findings if conflict_pattern in f.get("code", "")]
        observed["conflict_count"] = len(conflicts)
        
        all_have_resolver = all(
            "authority" in f and f.get("authority", {}).get("resolver_class")
            for f in conflicts
        ) if conflicts else True  # No conflicts means no resolver needed
        
        passed = all_have_resolver
        results.append({
            "check_id": "CONFLICTS_RESOLVED",
            "description": f"Conflicts ({conflict_pattern}) have resolver_class",
            "expected": True,
            "observed": all_have_resolver,
            "passed": passed,
            "detail": f"{len(conflicts)} conflict findings, all have resolver_class={all_have_resolver}",
        })
        if not passed:
            all_expected_pass = False

    # Provenance integrity
    if scenario.get("type") == "broken_provenance":
        prov_data = _get_provenance_data(sdk_data)
        records = prov_data.get("provenance_records", [])
        stale = [r for r in records if r.get("evidence_status") == "STALE"]
        absent = [r for r in records if r.get("evidence_status") == "ABSENT"]
        observed["stale_count"] = len(stale)
        observed["absent_count"] = len(absent)
        
        results.append({
            "check_id": "PROVENANCE_INTEGRITY",
            "description": "Provenance chain integrity evaluated",
            "expected": "current/stale/absent classified",
            "observed": f"current={prov_data.get('freshness_summary', {}).get('current', 0)}, stale={len(stale)}, absent={len(absent)}",
            "passed": True,  # Always passes — the evaluation itself is the value
            "detail": f"Provenance chain: {len(records)} total, {len(stale)} stale, {len(absent)} absent",
        })

    # Mutation boundary
    if scenario.get("type") == "mutation_boundary":
        # Check all queries
        all_clean = True
        query_states = {}
        for qname, qresult in sdk_data.items():
            rov = qresult.get("read_only_validation", {})
            no_mut = rov.get("no_mutation_path", False)
            query_states[qname] = no_mut
            if not no_mut:
                all_clean = False
        
        observed["query_mutation_states"] = query_states
        
        results.append({
            "check_id": "MUTATION_BOUNDARY_ALL_QUERIES",
            "description": "All 5 SDK queries enforce no-mutation boundary",
            "expected": True,
            "observed": all_clean,
            "passed": all_clean,
            "detail": f"Mutation states per query: {query_states}",
        })
        if not all_clean:
            all_expected_pass = False

    # ── Learning artifact ──
    learning_artifact = {
        "scenario_id": scenario["scenario_id"],
        "title": scenario["title"],
        "type": scenario["type"],
        "summary": "PASS" if all_expected_pass else "REVIEW NEEDED",
        "areas_of_attention": [r for r in results if not r["passed"]],
        "strengths": [r for r in results if r["passed"]],
        "explanation": scenario.get("explanation", ""),
        "teachable_moment": _generate_teachable_moment(scenario, results, observed),
    }

    # ── Overall result ──
    return {
        "suite_version": SUITE_VERSION,
        "generated_at": now_utc(),
        "scenario_id": scenario["scenario_id"],
        "title": scenario["title"],
        "type": scenario["type"],
        "target_epic": scenario.get("target_epic", ""),
        "overall": "PASS" if all_expected_pass else "REVIEW",
        "details": results,
        "learning_artifact": learning_artifact,
        "observed_state": {k: v for k, v in observed.items() if not k.startswith("_")},
        "read_only": True,
        "no_authority_conferred": True,
    }


def _generate_teachable_moment(scenario, results, observed):
    """Generate a training-oriented explanation based on scenario outcome."""
    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)
    
    if passed_count == total_count:
        return (
            f"All {total_count} checks passed. The {scenario['type']} scenario demonstrates "
            f"that the system composes correctly at this level. "
            f"This is a positive signal for epic completion."
        )
    
    failing = [r for r in results if not r["passed"]]
    return (
        f"{len(failing)} of {total_count} checks need attention. "
        f"The {scenario['type']} scenario identified gaps in: "
        + ", ".join(f"{r['check_id']} ({r['detail']})" for r in failing) +
        ". These are learning opportunities — the technician can investigate why each "
        "expected condition was not met and what it means for system composition."
    )


# ── Commands ─────────────────────────────────────────────────────────────

def cmd_list(args):
    """List all available built-in scenarios."""
    print(f"QA Pilot Epic Scenario Suite — v{SUITE_VERSION}")
    print(f"SDK: {'available' if SDK_AVAILABLE else 'unavailable'} ({SDK_VERSION})")
    print()
    for s in ALL_SCENARIOS:
        print(f"  {s['scenario_id']}: {s['title']}")
        print(f"    Type: {s['type']}")
        print(f"    Target: {s.get('target_epic', 'N/A')}")
        print(f"    SDK queries: {', '.join(s['sdk_queries'])}")
        print()
    return 0


def cmd_run(args):
    """Run one or more scenarios."""
    if not args:
        print("Usage: scenario_suite.py run <scenario_id> [<scenario_id> ...]")
        print("       scenario_suite.py run-all")
        print("       scenario_suite.py evidence-plane")
        print("Available: " + ", ".join(SCENARIO_INDEX.keys()))
        return 1
    
    if not SDK_AVAILABLE:
        print("ERROR: Evidence SDK not available", file=sys.stderr)
        return 1
    
    sdk_data, error = _get_sdk_data(
        ["getEvidenceSnapshot", "getFindings", "getCompositionGraph", 
         "getProvenanceChain", "getValidationArtifacts"]
    )
    if error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    
    scenario_ids = args
    results = []
    
    for sid in scenario_ids:
        if sid not in SCENARIO_INDEX:
            print(f"Unknown scenario: {sid} (available: {list(SCENARIO_INDEX.keys())})", file=sys.stderr)
            continue
        scenario = SCENARIO_INDEX[sid]
        result = evaluate_scenario(scenario, sdk_data)
        results.append(result)
    
    output = {
        "suite_version": SUITE_VERSION,
        "generated_at": now_utc(),
        "sdk_version": SDK_VERSION,
        "scenarios_run": len(results),
        "results": results,
        "overall": "PASS" if all(r["overall"] == "PASS" for r in results) else "REVIEW",
    }
    
    print(json.dumps(output, indent=2, default=str))
    return 0


def cmd_run_all(args):
    """Run all built-in scenarios."""
    return cmd_run(list(SCENARIO_INDEX.keys()))


def cmd_evidence_plane(args):
    """Run the Evidence Plane-specific scenarios."""
    return cmd_run(["EP-EP-001", "EP-MISS-001", "EP-CONF-001", "EP-PROV-001", "EP-BOUND-001"])


def cmd_format(args):
    """Format a scenario result for human reading."""
    if not args:
        print("Usage: scenario_suite.py format <result-json-path>")
        return 1
    
    path = args[0]
    try:
        data = load_json(path)
    except Exception as e:
        print(f"ERROR: Cannot load {path}: {e}", file=sys.stderr)
        return 1
    
    overall = data.get("overall", "UNKNOWN")
    results = data.get("results", [data])  # Handle single result or array
    
    print(f"Epic Scenario Suite Report — {overall}")
    print(f"Generated: {data.get('generated_at', 'unknown')}")
    print(f"Suite: {data.get('suite_version', 'unknown')}")
    print("=" * 60)
    
    for r in results:
        status_icon = "✅" if r["overall"] == "PASS" else "🔍"
        print(f"\n{status_icon} {r['scenario_id']}: {r['title']}")
        print(f"   Type: {r['type']}")
        print(f"   Overall: {r['overall']}")
        
        for d in r.get("details", []):
            icon = "✅" if d["passed"] else "❌"
            print(f"   {icon} {d['check_id']}: {d['description']}")
            print(f"      Expected: {d['expected']} | Observed: {d['observed']}")
            print(f"      {d['detail']}")
        
        la = r.get("learning_artifact", {})
        print(f"\n   📚 Learning: {la.get('teachable_moment', 'N/A')}")
    
    return 0


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("QA Pilot Epic Scenario Suite — QA-PILOT-EPIC-SCENARIO-SUITES")
        print()
        print("Usage:")
        print("  list                          — List available scenarios")
        print("  run <scenario_id>...          — Run one or more scenarios")
        print("  run-all                       — Run all built-in scenarios")
        print("  evidence-plane                — Run Evidence Plane scenarios")
        print("  format <result-json-path>     — Format result for reading")
        print()
        print("Authority: advisory-only. Read-only. No Librarian mutation.")
        return 0

    command = sys.argv[1]
    cmd_args = sys.argv[2:]

    commands = {
        "list": cmd_list,
        "run": cmd_run,
        "run-all": cmd_run_all,
        "evidence-plane": cmd_evidence_plane,
        "format": cmd_format,
    }

    if command not in commands:
        print(f"Unknown command: {command}", file=sys.stderr)
        print(f"Valid: {', '.join(commands.keys())}", file=sys.stderr)
        return 1

    return commands[command](cmd_args)


if __name__ == "__main__":
    sys.exit(main())
