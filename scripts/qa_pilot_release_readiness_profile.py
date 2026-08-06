"""
qa_pilot_release_readiness_profile.py — Release Readiness Profile

Composition layer — aggregates existing QA Pilot capability evidence (#179–#188)
into an Owner-facing readiness view.

Core invariant: Release Readiness Assessment ≠ Release Decision ≠ Authorization ≠ Deployment Execution
"""

import json, os
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
QA_PILOT_ROOT = os.path.dirname(PROJECT_ROOT)

# All input capabilities with their evidence file paths
# Only capabilities with structured evidence output are included
INPUT_CAPABILITIES = [
    {"capability": "#179", "name": "Regression",         "file": "data/regression-evidence.json"},
    {"capability": "#180", "name": "UAT",                "file": "data/uat-evidence.json"},
    {"capability": "#181", "name": "Accessibility",      "file": "data/accessibility-evidence.json"},
    {"capability": "#182", "name": "Performance",        "file": "data/performance-baseline.json"},
    {"capability": "#186", "name": "Privacy Assurance",  "file": "data/privacy-assurance-evidence.json"},
    {"capability": "#187", "name": "Dependency Risk",    "file": "data/dependency-risk-evidence.json"},
    {"capability": "#188", "name": "Security Assurance", "file": "data/security-assurance-evidence.json"},
]


def load_evidence_file(file_path):
    """Load a JSON evidence file. Returns (data, status, error_message)."""
    path = os.path.join(QA_PILOT_ROOT, file_path)
    if not os.path.exists(path):
        return None, "MISSING", f"Evidence file not found: {file_path}"
    try:
        with open(path) as f:
            data = json.load(f)
        
        # Check freshness
        gen_at = None
        if isinstance(data, dict):
            report = data.get("assurance_report", data)
            gen_at = report.get("generated_at") or data.get("generated_at") or data.get("timestamp")
        
        if gen_at:
            try:
                gen_time = datetime.fromisoformat(gen_at)
                now = datetime.now(timezone.utc) if gen_at.endswith(('Z', '+00:00')) else datetime.now()
                age_days = (now - gen_time).total_seconds() / 86400
                if age_days > 7:
                    return data, "STALE", f"Evidence age: {age_days:.1f} days (threshold: 7 days)"
            except (ValueError, TypeError):
                pass  # Can't parse timestamp — treat as available
        
        return data, "AVAILABLE", None
    except json.JSONDecodeError as e:
        return None, "ERROR", f"Evidence file unparseable: {e}"
    except Exception as e:
        return None, "ERROR", f"Error reading evidence: {e}"


def extract_capability_status(data, file_path):
    """Extract the overall status and finding count from a capability's evidence.
    
    Handles two evidence formats:
    1. #185 assurance_report format (used by #186, #187, #188)
    2. Legacy capability format (used by #179, #180, #181, #182)
    """
    if not data:
        return None, 0, []
    
    overall = None
    control_summary = []
    
    if not isinstance(data, dict):
        return None, 0, []
    
    # Format 1: #185 assurance_report format
    if "assurance_report" in data:
        report = data["assurance_report"]
        overall = report.get("overall", "OBSERVATION")
        control_summary = report.get("control_summary") or report.get("assessments") or []
    
    # Format 2: Legacy capability format (#179, #180, #181)
    elif "findings" in data or "scenarios" in data:
        # Evidence exists and loaded successfully — classify as OBSERVATION
        # (evidence present, but no formal PASS/OBSERVATION/ODR assertion)
        overall = "OBSERVATION"
        
        findings_data = data.get("findings", data.get("scenarios", []))
        if isinstance(findings_data, dict):
            # Flatten dict-based findings (e.g., {'summary': ..., 'inventory': ...})
            control_summary = [{"check": k, "finding": str(v)[:200] if isinstance(v, (dict, list)) else str(v)} 
                              for k, v in findings_data.items()]
        elif isinstance(findings_data, list):
            control_summary = [{"check": str(f).split(":")[0] if isinstance(f, str) else f.get("id", f.get("check", "finding")),
                               "finding": str(f)[:200]} for f in findings_data[:50]]
    
    # Format 3: Performance results format (#182)
    elif "results" in data:
        results = data["results"]
        overall = "OBSERVATION"
        if isinstance(results, list):
            control_summary = [{"check": r.get("metric", r.get("name", "result")), 
                               "finding": r.get("value", r.get("finding", str(r)[:200]))} 
                              for r in results[:50] if isinstance(r, dict)]
        elif isinstance(results, dict):
            control_summary = [{"check": k, "finding": str(v)[:200]} for k, v in results.items()]
    
    # Unknown format — evidence exists but unclassifiable
    else:
        overall = "OBSERVATION"
        # Extract any meaningful top-level string fields
        control_summary = [{"check": k, "finding": str(v)[:200]} 
                          for k, v in data.items() 
                          if isinstance(v, str) and k not in ('artifact', 'evidence_id', 'producer')]
    
    # Count findings
    finding_count = len(control_summary) if control_summary else 1
    
    return overall, finding_count, control_summary


def collect_owner_decisions(control_summary, source_capability, source_name, source_file):
    """Extract OWNER_DECISION_REQUIRED findings from control summaries."""
    decisions = []
    if not control_summary:
        return decisions
    
    for finding in control_summary:
        status = finding.get("status") or finding.get("classification")
        if status == "OWNER_DECISION_REQUIRED":
            decisions.append({
                "source": source_capability,
                "source_name": source_name,
                "finding": finding.get("finding", finding.get("check", "Unknown finding")),
                "classification": "OWNER_DECISION_REQUIRED",
                "evidence_reference": source_file
            })
        
        # Also check nested risk_findings (for #187)
        risk_findings = finding.get("risk_findings") or finding.get("version_details") or []
        for rf in risk_findings:
            rf_status = rf.get("classification") or rf.get("status") or rf.get("risk")
            if rf_status == "OWNER_DECISION_REQUIRED":
                decisions.append({
                    "source": source_capability,
                    "source_name": source_name,
                    "finding": rf.get("finding", "Risk finding"),
                    "classification": "OWNER_DECISION_REQUIRED",
                    "evidence_reference": source_file
                })
    
    return decisions


def main():
    now = datetime.now().isoformat()
    
    coverage_results = []
    all_findings = []  # Flat list of all findings across all capabilities
    all_owner_decisions = []
    status_counts = {"PASS": 0, "OBSERVATION": 0, "OWNER_DECISION_REQUIRED": 0}
    capabilities_available = 0
    capabilities_missing = 0
    capabilities_stale = 0
    capabilities_error = 0
    total_finding_count = 0
    
    for cap in INPUT_CAPABILITIES:
        data, status, error_msg = load_evidence_file(cap["file"])
        
        # Extract capability status from evidence
        cap_overall, finding_count, control_summary = extract_capability_status(data, cap["file"])
        
        # If evidence is MISSING or ERROR, we don't have a status
        if status not in ("AVAILABLE", "STALE"):
            cap_overall = cap_overall or status  # MISSING or ERROR
            finding_count = 0
        
        total_finding_count += finding_count
        
        # Track counts
        if status == "AVAILABLE":
            capabilities_available += 1
        elif status == "MISSING":
            capabilities_missing += 1
        elif status == "STALE":
            capabilities_stale += 1
        elif status == "ERROR":
            capabilities_error += 1
        
        # Track status counts from available evidence
        if cap_overall and cap_overall in status_counts:
            status_counts[cap_overall] += 1
        
        # Collect owner decisions from available evidence
        if data:
            decisions = collect_owner_decisions(control_summary, cap["capability"], cap["name"], cap["file"])
            all_owner_decisions.extend(decisions)
        
        # Collect individual findings for traceability
        if control_summary:
            for f in control_summary:
                finding_status = f.get("status") or f.get("classification")
                if finding_status and finding_status in ("PASS", "OBSERVATION", "OWNER_DECISION_REQUIRED", "MISSING"):
                    all_findings.append({
                        "source": cap["capability"],
                        "source_name": cap["name"],
                        "check": f.get("check", f.get("id", "unknown")),
                        "finding": f.get("finding", ""),
                        "classification": finding_status,
                        "evidence_reference": cap["file"]
                    })
        
        # Compute generated_at from evidence if available
        generated_at = None
        if data:
            report = data.get("assurance_report", data)
            generated_at = report.get("generated_at") or data.get("generated_at") or data.get("timestamp")
        
        coverage_results.append({
            "capability": cap["capability"],
            "name": cap["name"],
            "status": status,
            "overall": cap_overall if cap_overall else status,
            "generated_at": generated_at,
            "findings_count": finding_count,
            "evidence_file": cap["file"],
            "error": error_msg if status in ("MISSING", "ERROR") else None
        })
    
    # Compute overall — highest severity across inputs
    overall = "PASS"
    if status_counts["OWNER_DECISION_REQUIRED"] > 0 or len(all_owner_decisions) > 0:
        overall = "OWNER_DECISION_REQUIRED"
    elif status_counts["OBSERVATION"] > 0:
        overall = "OBSERVATION"
    
    owner_action_required = overall == "OWNER_DECISION_REQUIRED"
    
    # Compose evidence in assurance_report format
    evidence = {
        "assurance_report": {
            "profile": "release-readiness",
            "profile_name": "Release Readiness Profile",
            "version": "1.0.0",
            "generated_at": now,
            
            "inputs": [
                {
                    "capability": cap["capability"],
                    "name": cap["name"],
                    "file": cap["evidence_file"],
                    "status": cap["status"],
                    "generated_at": cap["generated_at"]
                }
                for cap in coverage_results
            ],
            
            "summary": {
                "capabilities_total": len(INPUT_CAPABILITIES),
                "capabilities_available": capabilities_available,
                "capabilities_missing": capabilities_missing,
                "capabilities_stale": capabilities_stale,
                "capabilities_error": capabilities_error,
                "total_findings": total_finding_count,
                "pass": status_counts["PASS"],
                "observations": status_counts["OBSERVATION"],
                "owner_decision_required": status_counts["OWNER_DECISION_REQUIRED"],
                "overall": overall
            },
            
            "coverage": coverage_results,
            
            "owner_decisions": all_owner_decisions,
            
            "authority_level": "advisory",
            "owner_action_required": owner_action_required
        },
        
        "evidence_id": f"RR-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "producer": "qa_pilot_release_readiness_profile.py",
        "capability": "Release Readiness",
        "consumable_by": "governance_view"
    }
    
    # Print summary
    print("=" * 60)
    print("RELEASE READINESS PROFILE")
    print("=" * 60)
    print(f"Generated: {now}")
    print(f"Overall:   {overall}")
    print()
    print("Coverage:")
    for c in coverage_results:
        icon = {"AVAILABLE": "✅", "STALE": "⚠️", "MISSING": "❌", "ERROR": "💥"}
        print(f"  {icon.get(c['status'], '❓')} {c['capability']:6s} {c['name']:20s} {c['status']:10s} overall={c['overall'] or 'N/A'}")
    print()
    print(f"Summary:")
    print(f"  Capabilities: {capabilities_available} available, {capabilities_stale} stale, {capabilities_missing} missing, {capabilities_error} error")
    print(f"  Total findings: {total_finding_count}")
    print(f"  PASS: {status_counts['PASS']}  OBSERVATION: {status_counts['OBSERVATION']}  OWNER_DECISION_REQUIRED: {status_counts['OWNER_DECISION_REQUIRED']}")
    print(f"  Owner decisions required: {len(all_owner_decisions)}")
    print(f"  Owner action required: {owner_action_required}")
    print()
    if all_owner_decisions:
        print("Owner Decisions:")
        for d in all_owner_decisions[:5]:  # Show first 5
            print(f"  [{d['source']}] {d['finding'][:80]}")
        if len(all_owner_decisions) > 5:
            print(f"  ... and {len(all_owner_decisions) - 5} more")
    print()
    print(f"Authority level: advisory")
    print(f"Consumable by: governance_view")
    print()
    print("Core invariant preserved: Release Readiness Assessment ≠ Release Decision ≠ Authorization ≠ Deployment Execution")
    
    # Write evidence
    evidence_path = os.path.join(QA_PILOT_ROOT, "data", "release-readiness-evidence.json")
    with open(evidence_path, "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"\nEvidence written to: {evidence_path}")


if __name__ == "__main__":
    main()
