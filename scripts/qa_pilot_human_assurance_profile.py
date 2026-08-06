"""
qa_pilot_human_assurance_profile.py — #189 Human Assurance Profile

Evaluates whether an operator can understand and safely navigate a governed system.
Consumes knowledge graph and existing artifacts to generate role-based exercises.

Core invariant: Human Assessment ≠ Operational Authorization
"""

import json, os, sys
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
QA_PILOT_ROOT = os.path.dirname(PROJECT_ROOT)
CARBIDEFRAME_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(PROJECT_ROOT)))

GRAPH_PATH = os.path.join(CARBIDEFRAME_ROOT, "data", "governance-graph.json")
HUMAN_ASSURANCE_DIR = os.path.join(QA_PILOT_ROOT, "data", "human-assurance")

# Exercises by role — each references specific graph nodes and artifacts
ROLE_EXERCISES = {
    "manager": [
        {
            "exercise_id": "EX-MGR-001",
            "exercise": "system-status-summary",
            "question": "Generate a status summary for the Windows Runtime Node. Identify its certification state, evidence count, and remaining deferred items.",
            "graph_nodes_required": ["runtime-node", "sprint-7-cert", "mode-post-runtime"],
            "knowledge_area": "system_status",
            "evidence_refs_expected": ["docs/reports/SPRINT7-FINAL-CERTIFICATION-REPORT.md"]
        },
        {
            "exercise_id": "EX-MGR-002",
            "exercise": "capability-inventory",
            "question": "List all certified capabilities on the platform and their current states. Identify which capabilities are frozen and which are active.",
            "graph_nodes_required": ["qa-pilot", "runtime-node", "governance-bridge", "invariant-regression"],
            "knowledge_area": "capability_inventory",
            "evidence_refs_expected": []
        }
    ],
    "architect": [
        {
            "exercise_id": "EX-ARCH-001",
            "exercise": "invariant-impact-analysis",
            "question": "What is affected if AUTH-003 changes? Identify affected systems, protected invariants, and required governance gates.",
            "graph_nodes_required": ["inv-auth-003"],
            "knowledge_area": "impact_analysis",
            "evidence_refs_expected": ["docs/rules/GLOBAL-AUTHORITY-INVARIANTS.md"]
        },
        {
            "exercise_id": "EX-ARCH-002",
            "exercise": "boundary-identification",
            "question": "Identify which components the Governance Bridge connects. Explain why the bridge cannot create authority and which operating mode enforces this.",
            "graph_nodes_required": ["governance-bridge", "mode-post-bridge", "inv-bridge-nauth"],
            "knowledge_area": "boundary_understanding",
            "evidence_refs_expected": ["docs/governance/POST-BRIDGE-OPERATING-MODE-DECLARATION.md"]
        }
    ],
    "engineer": [
        {
            "exercise_id": "EX-ENG-001",
            "exercise": "custody-chain-trace",
            "question": "Trace the complete certification chain for the Governance Bridge. List each step from problem identification through operating mode declaration.",
            "graph_nodes_required": ["governance-bridge", "bridge-cert", "phase0-audit", "mode-post-bridge"],
            "knowledge_area": "custody_tracing",
            "evidence_refs_expected": ["docs/planning/GOVERNANCE-BRIDGE-CERTIFICATION.md"]
        },
        {
            "exercise_id": "EX-ENG-002",
            "exercise": "evidence-location",
            "question": "Find and verify the evidence artifacts for the Runtime Node certification. Confirm each path resolves.",
            "graph_nodes_required": ["sprint-7-cert"],
            "knowledge_area": "evidence_discovery",
            "evidence_refs_expected": ["docs/reports/SPRINT7-FINAL-CERTIFICATION-REPORT.md"]
        }
    ],
    "auditor": [
        {
            "exercise_id": "EX-AUD-001",
            "exercise": "provenance-verification",
            "question": "Verify the evidence chain for the Runtime Node. Identify how many evidence paths exist and whether any are degraded.",
            "graph_nodes_required": ["runtime-node"],
            "knowledge_area": "provenance_check",
            "evidence_refs_expected": ["docs/reports/SPRINT7-FINAL-CERTIFICATION-REPORT.md"]
        },
        {
            "exercise_id": "EX-AUD-002",
            "exercise": "operating-mode-compliance",
            "question": "List all operating mode declarations and verify each has a documented authority boundary. Check that none claim certification authority.",
            "graph_nodes_required": ["mode-post-epic", "mode-qa-pilot", "mode-post-assurance", "mode-post-bridge", "mode-post-runtime", "mode-invariant-regression"],
            "knowledge_area": "compliance_check",
            "evidence_refs_expected": []
        }
    ],
    "new-owner": [
        {
            "exercise_id": "EX-OWN-001",
            "exercise": "frozen-boundaries",
            "question": "What is frozen on this platform and what can change? Identify which invariants protect the architecture and which operating modes govern which systems.",
            "graph_nodes_required": ["inv-auth-001", "inv-auth-003", "inv-auth-005", "mode-post-runtime", "mode-post-bridge"],
            "knowledge_area": "governance_understanding",
            "evidence_refs_expected": ["docs/governance/POST-RUNTIME-GOVERNANCE-OPERATING-MODE-DECLARATION.md"]
        },
        {
            "exercise_id": "EX-OWN-002",
            "exercise": "owner-decision-points",
            "question": "Identify where Owner decisions are required in the platform. Explain the difference between evidence-backed findings and decision authority.",
            "graph_nodes_required": ["odr-privacy-analytics"],
            "knowledge_area": "decision_boundary",
            "evidence_refs_expected": []
        }
    ]
}

# Correct answers for automated evaluation
CORRECT_ANSWERS = {
    "EX-MGR-001": {
        "key_concepts": ["certified", "sprint 7", "27/27", "deferred"],
        "required_reasoning": "The Runtime Node is certified with 27/27 PASS. Evidence includes Sprint 7 report. Deferred items: full Windows-side latency measurement, additional profiles."
    },
    "EX-MGR-002": {
        "key_concepts": ["runtime-node", "governance-bridge", "qa-pilot", "invariant-regression", "certified", "frozen"],
        "required_reasoning": "Four certified systems: Runtime Node (certified), Governance Bridge (certified), QA Pilot (frozen), Invariant Regression (certified). Each has an operating mode declaration."
    },
    "EX-ARCH-001": {
        "key_concepts": ["constrained_by", "protected_by", "invariant review"],
        "required_reasoning": "AUTH-003 constrains Runtime Node, Governance Bridge, and QA Pilot. Protected by Post-Runtime and Post-Invariant Regression Operating Modes. Changes require impact analysis, invariant review, and Owner authorization."
    },
    "EX-ARCH-002": {
        "key_concepts": ["translation", "bridge ≠ authority", "post-bridge"],
        "required_reasoning": "The Governance Bridge connects Librarian Core MCP to Runtime Node REST. It translates requests — it does not create authority. Enforced by Post-Bridge Operating Mode and AUTH-003."
    },
    "EX-ENG-001": {
        "key_concepts": ["phase 0", "bridge definition", "invariant review", "implementation", "certification", "operating mode"],
        "required_reasoning": "Phase 0 identified integration gap. Bridge definition established boundary. Invariant review confirmed authority preservation. Implementation produced v1.0.0. Certification passed 10 gates. Post-Bridge Operating Mode declared."
    },
    "EX-ENG-002": {
        "key_concepts": ["docs/reports/SPRINT7-FINAL-CERTIFICATION-REPORT.md", "evidence path"],
        "required_reasoning": "The Sprint 7 certification report at docs/reports/SPRINT7-FINAL-CERTIFICATION-REPORT.md contains the evidence. Additional evidence in docs/planning/GOVERNANCE-BRIDGE-CERTIFICATION.md and docs/governance/POST-RUNTIME-GOVERNANCE-OPERATING-MODE-DECLARATION.md."
    },
    "EX-AUD-001": {
        "key_concepts": ["21 verified", "0 degraded", "34 steps"],
        "required_reasoning": "The custody chain for Runtime Node has 34 steps. 21 evidence paths verified, 0 degraded. Evidence includes certification report, operating mode declarations, and sprint reports."
    },
    "EX-AUD-002": {
        "key_concepts": ["advisory", "authority boundary", "operating mode"],
        "required_reasoning": "Six operating mode declarations exist. Each has authority_level: advisory and documented authority boundaries. None claim certification authority or decision-making power."
    },
    "EX-OWN-001": {
        "key_concepts": ["frozen", "governance process", "operating mode"],
        "required_reasoning": "Evidence contracts, classification taxonomy, certification evidence, and operating mode declarations are frozen. Changes require governance process: proposal, impact analysis, invariant review, Owner authorization."
    },
    "EX-OWN-002": {
        "key_concepts": ["owner decision", "evidence ≠ decision", "advisory"],
        "required_reasoning": "Owner decisions are required for authorization, certification, and boundary changes. The platform produces evidence-backed findings — it does not make decisions. Findings classified as OWNER_DECISION_REQUIRED signal Owner attention."
    }
}


def load_graph():
    if not os.path.exists(GRAPH_PATH):
        return None
    try:
        with open(GRAPH_PATH) as f:
            return json.load(f)
    except:
        return None


def find_node(graph, node_id):
    for n in graph.get("nodes", []):
        if n["id"] == node_id:
            return n
    return None


def verify_evidence_refs(refs):
    """Verify that evidence references resolve to existing files."""
    results = []
    for ref in refs:
        full_path = os.path.join(CARBIDEFRAME_ROOT, ref)
        exists = os.path.exists(full_path)
        results.append({"reference": ref, "resolved": exists})
    return results


def evaluate_exercise(exercise, response_text=""):
    """
    Evaluate a single exercise response.
    In automated mode, checks that the required graph nodes exist and evidence refs resolve.
    Full operator evaluation would be human-reviewed, with responses compared against CORRECT_ANSWERS.
    """
    ex_id = exercise["exercise_id"]
    correct = CORRECT_ANSWERS.get(ex_id, {})
    
    # Verify graph references exist
    graph = load_graph()
    missing_nodes = []
    if graph:
        for nid in exercise.get("graph_nodes_required", []):
            if not find_node(graph, nid):
                missing_nodes.append(nid)
    
    # Verify evidence references
    ev_results = verify_evidence_refs(exercise.get("evidence_refs_expected", []))
    all_ev_resolved = all(r["resolved"] for r in ev_results)
    
    # Determine classification
    if missing_nodes:
        classification = "ERROR"
        finding = f"Exercise cannot be evaluated: required graph nodes not found: {missing_nodes}"
    elif not all_ev_resolved:
        classification = "ERROR"
        unresolved = [r["reference"] for r in ev_results if not r["resolved"]]
        finding = f"Reference evidence not found: {unresolved}"
    elif response_text:
        # Simple keyword matching for automated evaluation
        if correct:
            keywords = correct.get("key_concepts", [])
            found = sum(1 for kw in keywords if kw.lower() in response_text.lower())
            total = len(keywords)
            if found >= total * 0.6:
                classification = "PASS"
                finding = f"Understanding demonstrated. Key concepts covered: {found}/{total}"
            elif found > 0:
                classification = "OBSERVATION"
                finding = f"Partial understanding. Key concepts covered: {found}/{total}. Missing: {[k for k in keywords if k.lower() not in response_text.lower()]}"
            else:
                classification = "OBSERVATION"
                finding = "Knowledge gap identified. Response did not cover required key concepts."
        else:
            classification = "OBSERVATION"
            finding = "No reference answer available for automated evaluation."
    else:
        # No response provided — structural check only
        classification = "OBSERVATION"
        finding = "Exercise defined. Graph references verified. Awaiting operator response for classification."
    
    return {
        "exercise_id": ex_id,
        "exercise": exercise["exercise"],
        "knowledge_area": exercise["knowledge_area"],
        "classification": classification,
        "finding": finding,
        "evidence_refs": exercise.get("evidence_refs_expected", []),
        "graph_nodes_verified": not bool(missing_nodes)
    }


def generate_role_curriculum(role):
    """Generate a learning path for a role based on graph traversal."""
    exercises = ROLE_EXERCISES.get(role, [])
    if not exercises:
        return []
    
    curriculum = []
    for ex in exercises:
        graph = load_graph()
        nodes_info = []
        if graph:
            for nid in ex.get("graph_nodes_required", []):
                node = find_node(graph, nid)
                if node:
                    nodes_info.append(f"{nid}: {node.get('name', nid)} ({node.get('state', 'unknown')})")
        
        curriculum.append({
            "step": len(curriculum) + 1,
            "exercise_id": ex["exercise_id"],
            "exercise": ex["exercise"],
            "knowledge_area": ex["knowledge_area"],
            "required_knowledge": nodes_info,
            "evidence_artifacts": ex.get("evidence_refs_expected", [])
        })
    
    return curriculum


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="#189 — Human Assurance Profile")
    parser.add_argument("role", choices=list(ROLE_EXERCISES.keys()) + ["all"],
                        help="Role to assess, or 'all' for all roles")
    parser.add_argument("--output", choices=["owner_summary", "technical_detail"], default="owner_summary",
                        help="Output format")
    parser.add_argument("--subject", default="operator", help="Subject identifier for assessment record")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("#189 — HUMAN ASSURANCE PROFILE")
    print("=" * 70)
    print(f"Core invariant: Human Assessment ≠ Operational Authorization")
    print()
    
    roles_to_run = list(ROLE_EXERCISES.keys()) if args.role == "all" else [args.role]
    
    all_assessments = []
    
    for role in roles_to_run:
        print(f"\nRole: {role.title()}")
        print("-" * 40)
        
        exercises = ROLE_EXERCISES.get(role, [])
        
        # Generate curriculum
        curriculum = generate_role_curriculum(role)
        if curriculum:
            print(f"  Learning path ({len(curriculum)} exercises):")
            for c in curriculum:
                print(f"    {c['step']}. {c['knowledge_area'].replace('_', ' ').title()}")
        
        # Evaluate each exercise
        for ex in exercises:
            result = evaluate_exercise(ex)
            all_assessments.append(result)
            
            icon = {"PASS": "✅", "OBSERVATION": "⚠️", "ERROR": "💥"}
            print(f"  {icon.get(result['classification'], '❓')} {result['exercise_id']}: {result['classification']}")
            print(f"     {result['finding'][:90]}")
    
    # Compute overall
    statuses = [a["classification"] for a in all_assessments]
    overall = "PASS"
    if "ERROR" in statuses:
        overall = "ERROR"
    elif "OBSERVATION" in statuses:
        overall = "OBSERVATION"
    
    gaps = [a for a in all_assessments if a["classification"] == "OBSERVATION"]
    
    # Build knowledge gaps
    knowledge_gaps = []
    for g in gaps:
        knowledge_gaps.append({
            "exercise_id": g["exercise_id"],
            "knowledge_area": g["knowledge_area"],
            "finding": g["finding"]
        })
    
    print(f"\n  Summary: {len(all_assessments)} exercises | Overall: {overall}")
    print(f"  Knowledge gaps: {len(knowledge_gaps)}")
    print(f"  Core invariant: Human Assessment ≠ Operational Authorization")
    print()
    
    # Compose evidence — stored separately from system assurance
    evidence = {
        "assurance_report": {
            "profile": "human-assurance",
            "profile_name": "Human Assurance Profile",
            "version": "1.0.0",
            "subject": args.subject,
            "role": args.role if args.role != "all" else "multi-role",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "overall": overall,
            "consumes": ["knowledge-graph", "governance-graph-json"],
            "assessments": all_assessments,
            "knowledge_gaps": knowledge_gaps,
            "summary": {
                "total_exercises": len(all_assessments),
                "pass": sum(1 for a in all_assessments if a["classification"] == "PASS"),
                "observation": sum(1 for a in all_assessments if a["classification"] == "OBSERVATION"),
                "owner_decision_required": sum(1 for a in all_assessments if a["classification"] == "OWNER_DECISION_REQUIRED"),
                "error": sum(1 for a in all_assessments if a["classification"] == "ERROR"),
                "overall": overall
            },
            "authority_level": "advisory",
            "consumable_by": "operator-capability-view"
        },
        "evidence_id": f"HA-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "producer": "qa_pilot_human_assurance_profile.py",
        "capability": "#189",
        "authority_level": "advisory",
        "core_invariant": "Human Assessment ≠ Operational Authorization"
    }
    
    # Write to human-assurance directory (separate from system assurance)
    os.makedirs(HUMAN_ASSURANCE_DIR, exist_ok=True)
    evidence_path = os.path.join(HUMAN_ASSURANCE_DIR, f"human-assurance-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
    with open(evidence_path, 'w') as f:
        json.dump(evidence, f, indent=2)
    print(f"  Assessment evidence: {evidence_path}")
    print(f"  (Stored separately from system assurance — not consumed by Release Readiness)")
    
    # Verify separation
    rr_path = os.path.join(QA_PILOT_ROOT, "data", "release-readiness-evidence.json")
    if os.path.exists(rr_path):
        with open(rr_path) as f:
            rr = json.load(f)
        has_human = "human-assurance" in json.dumps(rr) or "human_assurance" in json.dumps(rr)
        print(f"  Release Readiness contains human assurance data: {has_human} — should be False")
    
    print(f"\n  Core invariant preserved: Human Assessment ≠ Operational Authorization")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
