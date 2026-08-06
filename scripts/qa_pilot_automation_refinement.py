"""
qa_pilot_automation_refinement.py — Automation Refinement

Reduces noise, correlates findings, detects duplicates, optimizes freshness.
"""

import json, os
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
QA_PILOT_ROOT = os.path.dirname(PROJECT_ROOT)

def load_evidence(rel_path):
    path = os.path.join(QA_PILOT_ROOT, rel_path)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def main():
    # Load current risk and evidence data
    risk = load_evidence("data/risk-prioritization-evidence.json")
    lineage = load_evidence("data/evidence-lineage.json")
    history = load_evidence("data/assurance-history.json")
    
    refinements = {}
    
    # 1. MONITOR consolidation — identify low-signal items
    if risk:
        monitor = risk.get("assurance_attention", {}).get("prioritization", {}).get("monitor", [])
        capability_sources = [m for m in monitor if "capability" in m.get("category", "")]
        evidence_sources = [m for m in monitor if m not in capability_sources]
        
        refinements["monitor_reduction"] = {
            "before": len(monitor),
            "capability_based": len(capability_sources),
            "evidence_based": len(evidence_sources),
            "consolidation_note": f"{len(capability_sources)} capability-based MONITOR items can be aggregated into profile-level view",
            "reduced_to": len(capability_sources) + 1 if evidence_sources else len(capability_sources)
        }
    
    # 2. Finding correlation — count findings linked to same source
    correlated = 0
    if lineage:
        findings = lineage.get("lineage", {}).get("current_findings", [])
        seen = set()
        for f in findings:
            ev_file = f.get("evidence_file", "")
            if ev_file in seen:
                correlated += 1
            seen.add(ev_file)
        refinements["finding_correlation"] = {
            "total_findings": len(findings),
            "unique_evidence_sources": len(seen),
            "correlated_findings": correlated,
            "note": f"{correlated} finding(s) share evidence sources with another finding"
        }
    
    # 3. Duplicate detection
    duplicates = 0
    if lineage:
        seen_findings = set()
        for f in findings:
            key = f"{f.get('profile','')}:{f.get('overall','')}"
            if key in seen_findings:
                duplicates += 1
            seen_findings.add(key)
        refinements["duplicate_detection"] = {
            "duplicates_found": duplicates,
            "note": "Duplicates are expected across repeated assurance runs; flag for consolidation"
        }
    
    # 4. Profile selection accuracy
    refinements["profile_selection_accuracy"] = {
        "note": "Current impact mapping uses 8 file patterns → profile relationships. Accuracy improves with usage history.",
        "suggested_refinement": "Add usage frequency tracking to deprioritize profiles that consistently return no new findings"
    }
    
    # 5. Evidence freshness
    evidence_dir = os.path.join(QA_PILOT_ROOT, "data")
    fresh_files = []
    if os.path.exists(evidence_dir):
        now = datetime.now()
        for f in sorted(os.listdir(evidence_dir)):
            if not f.endswith(".json"):
                continue
            path = os.path.join(evidence_dir, f)
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            age_hours = (now - mtime).total_seconds() / 3600
            fresh_files.append({"file": f, "age_hours": round(age_hours, 1)})
    refinements["evidence_freshness"] = {
        "total_files": len(fresh_files),
        "fresh_under_1h": sum(1 for f in fresh_files if f["age_hours"] < 1),
        "stale_over_24h": sum(1 for f in fresh_files if f["age_hours"] > 24),
        "all_fresh": all(f["age_hours"] < 24 for f in fresh_files)
    }
    
    evidence = {
        "artifact": {
            "identity": f"AUTO-REFINE-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        },
        "intent": "Automation refinement — signal quality improvement",
        "classification": "assurance",
        "execution_method": "static_analysis",
        "findings": refinements,
        "evidence_output": {
            "summary": f"MONITOR: {refinements.get('monitor_reduction',{}).get('before',0)}→{refinements.get('monitor_reduction',{}).get('reduced_to',0)} | "
                       f"Correlated: {refinements.get('finding_correlation',{}).get('correlated_findings',0)} | "
                       f"Duplicates: {refinements.get('duplicate_detection',{}).get('duplicates_found',0)} | "
                       f"Freshness: {'ALL CURRENT' if refinements.get('evidence_freshness',{}).get('all_fresh') else 'STALE FOUND'}"
        },
        "authority_level": "advisory"
    }
    
    print(json.dumps(evidence, indent=2))
    print(f"\nRefinement results:")
    for area, detail in refinements.items():
        summary = detail.get("note") or detail.get("consolidation_note") or f"{detail}"
        print(f"  {area}: {summary[:80]}")

    evidence_path = os.path.join(QA_PILOT_ROOT, "data", "automation-refinement-evidence.json")
    with open(evidence_path, "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"\nEvidence written to: {evidence_path}")

if __name__ == "__main__":
    main()
