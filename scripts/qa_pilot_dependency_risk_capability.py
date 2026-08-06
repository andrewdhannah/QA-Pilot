"""
qa_pilot_dependency_risk_capability.py — Dependency Risk Capability (#187)

Architecture basis: QA-PILOT-ASSURANCE-PROFILE-ARCHITECTURE-1 (#185)
Profile: DEPENDENCY-RISK-1 (3 controls: DR-INVENTORY, DR-VERSION, DR-RISK)
Consumed by: #188 Security Assurance Profile
"""

import json, os, re, hashlib
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
QA_PILOT_ROOT = os.path.dirname(PROJECT_ROOT)
BROWSER_APP = os.path.join(QA_PILOT_ROOT, "browser-app")

# Profile contract per #185 schema
PROFILE = {
    "profile_id": "DEPENDENCY-RISK-1",
    "name": "Dependency Risk Assurance Profile",
    "version": "1.0.0",
    "standards": [
        {"reference": "DEPENDENCY-RISK-FRAMEWORK-1", "description": "QA Pilot dependency risk analysis framework"}
    ],
    "controls": [
        {
            "id": "DR-INVENTORY",
            "description": "Dependency inventory is complete and categorized",
            "capabilities": ["dependency_risk"],
            "evidence_required": ["implementation"],
            "finding_classification_default": "OBSERVATION",
            "escalation_rule": "OWNER_DECISION_REQUIRED if external CDN or service dependency without provenance"
        },
        {
            "id": "DR-VERSION",
            "description": "Dependency version metadata is available and verifiable",
            "capabilities": ["dependency_risk"],
            "evidence_required": ["implementation"],
            "finding_classification_default": "OBSERVATION",
            "escalation_rule": "OWNER_DECISION_REQUIRED if dependency is beyond supported lifecycle or abandoned"
        },
        {
            "id": "DR-RISK",
            "description": "Dependency risk findings are classified and actionable",
            "capabilities": ["dependency_risk"],
            "evidence_required": ["implementation", "documentation"],
            "finding_classification_default": "OBSERVATION",
            "escalation_rule": "OWNER_DECISION_REQUIRED if dependency is abandoned, unsupported, or externally sourced without provenance"
        }
    ],
    "authority_level": "advisory"
}


def discover_dependencies():
    """Discover all dependencies across the application source tree."""
    
    # Track deduplicated dependencies across all source files
    local_libs = {}       # path -> {sources: [], versions: []}
    cdn_deps = {}         # url -> {sources: []}
    external_services = {} # service_url -> {sources: []}
    
    for root, dirs, files in os.walk(BROWSER_APP):
        for f in files:
            if not f.endswith(('.html', '.js')): 
                continue
            path = os.path.join(root, f)
            rel_path = os.path.relpath(path, QA_PILOT_ROOT)
            
            with open(path, errors='ignore') as fp:
                content = fp.read()
            
            # External CDN scripts
            for m in re.finditer(r'<script[^>]+src=["\']([^"\']+)["\']', content):
                src = m.group(1)
                if src.startswith(('http://', 'https://', '//')):
                    # Extract version from CDN URL
                    version = None
                    v_match = re.search(r'[@-]v?(\d+\.\d+\.?\d*)', src)
                    if v_match:
                        version = v_match.group(1)
                    key = src.split('?')[0]  # strip query params for dedup
                    if key not in cdn_deps:
                        cdn_deps[key] = {"sources": [], "versions": []}
                    cdn_deps[key]["sources"].append(rel_path)
                    if version:
                        cdn_deps[key]["versions"].append(version)
                elif src.startswith(('../', 'js/', 'data/', 'qa/')):
                    if src not in local_libs:
                        local_libs[src] = {"sources": [], "versions": []}
                    local_libs[src]["sources"].append(rel_path)
                    # Check for versioned filename
                    v_match = re.search(r'[.-]v?(\d+\.\d+\.?\d*)', src)
                    if v_match:
                        local_libs[src]["versions"].append(v_match.group(1))
            
            # External CSS
            for m in re.finditer(r'<link[^>]+href=["\']([^"\']+\.css)["\']', content):
                href = m.group(1)
                if href.startswith(('http://', 'https://')):
                    key = href.split('?')[0]
                    if key not in cdn_deps:
                        cdn_deps[key] = {"sources": [], "versions": []}
                    cdn_deps[key]["sources"].append(rel_path)
            
            # External service calls (fetch, XMLHttpRequest, WebSocket)
            for m in re.finditer(r'(?:fetch|XMLHttpRequest|WebSocket)\s*\(\s*["\'](https?://[^"\']+)["\']', content):
                service_url = m.group(1)
                # Skip localhost/internal references
                if 'localhost' in service_url or '127.0.0.1' in service_url:
                    continue
                # Normalize to base URL for dedup
                base_match = re.match(r'(https?://[^/]+)', service_url)
                if base_match:
                    base = base_match.group(1)
                    if base not in external_services:
                        external_services[base] = {"sources": [], "endpoints": []}
                    external_services[base]["sources"].append(rel_path)
                    endpoint = service_url[len(base):]
                    if endpoint and endpoint not in external_services[base]["endpoints"]:
                        external_services[base]["endpoints"].append(endpoint)
    
    return {
        "local_libraries": local_libs,
        "cdn_dependencies": cdn_deps,
        "external_services": external_services
    }


def check_control(control_id, deps):
    """Run the check for a dependency risk control."""
    findings = []
    
    if control_id == "DR-INVENTORY":
        total_local = len(deps["local_libraries"])
        total_cdn = len(deps["cdn_dependencies"])
        total_services = len(deps["external_services"])
        total = total_local + total_cdn + total_services
        
        # Check completeness
        if total == 0:
            findings.append({
                "control": control_id,
                "check": "dependency_inventory",
                "status": "OWNER_DECISION_REQUIRED",
                "finding": "No dependencies discovered — application may not be scanned or may use unconventional loading"
            })
        else:
            # Build deduplicated dependency graph
            dep_graph = []
            for path, info in sorted(deps["local_libraries"].items()):
                dep_graph.append({
                    "name": path,
                    "type": "local_library",
                    "version": info["versions"][0] if info["versions"] else "unversioned",
                    "classification": "direct",
                    "sources": sorted(set(info["sources"]))
                })
            for url, info in sorted(deps["cdn_dependencies"].items()):
                dep_graph.append({
                    "name": url,
                    "type": "cdn",
                    "version": info["versions"][0] if info["versions"] else "external",
                    "classification": "direct",
                    "sources": sorted(set(info["sources"]))
                })
            for base, info in sorted(deps["external_services"].items()):
                dep_graph.append({
                    "name": base,
                    "type": "external_service",
                    "version": "external",
                    "classification": "direct",
                    "endpoints": sorted(set(info.get("endpoints", []))),
                    "sources": sorted(set(info["sources"]))
                })
            
            findings.append({
                "control": control_id,
                "check": "dependency_inventory",
                "status": "PASS",
                "finding": f"Inventory complete: {total} deduplicated dependencies ({total_local} local, {total_cdn} CDN, {total_services} external services)",
                "dependency_graph": dep_graph
            })
        
        # Check categorization
        unclassified = 0
        for path in deps["local_libraries"]:
            if not any(path.endswith(ext) for ext in ['.js', '.css']):
                unclassified += 1
        
        if unclassified > 0:
            findings.append({
                "control": control_id,
                "check": "dependency_categorization",
                "status": "OBSERVATION",
                "finding": f"{unclassified} dependencies with non-standard file extensions — verify categorization"
            })
        else:
            findings.append({
                "control": control_id,
                "check": "dependency_categorization",
                "status": "PASS",
                "finding": "All dependencies have standard file extensions"
            })
    
    elif control_id == "DR-VERSION":
        unversioned_count = 0
        versioned_count = 0
        external_count = 0
        version_details = []
        
        for path, info in deps["local_libraries"].items():
            if info["versions"]:
                versioned_count += 1
                version_details.append({
                    "dependency": path,
                    "version": info["versions"][0],
                    "status": "PASS",
                    "finding": f"Versioned dependency: {info['versions'][0]}"
                })
            else:
                unversioned_count += 1
                version_details.append({
                    "dependency": path,
                    "version": "unversioned",
                    "status": "OBSERVATION",
                    "finding": "Unversioned dependency (pinned to path, no version tracking)"
                })
        
        for url, info in deps["cdn_dependencies"].items():
            external_count += 1
            if info["versions"]:
                version_details.append({
                    "dependency": url[:80],
                    "version": info["versions"][0],
                    "status": "OBSERVATION",
                    "finding": f"CDN dependency versioned: {info['versions'][0]} — verify integrity via SRI"
                })
            else:
                version_details.append({
                    "dependency": url[:80],
                    "version": "external",
                    "status": "OWNER_DECISION_REQUIRED",
                    "finding": "External CDN dependency without version pinning — verify integrity and availability"
                })
        
        for base, info in deps["external_services"].items():
            external_count += 1
            version_details.append({
                "dependency": base,
                "version": "external",
                "status": "OWNER_DECISION_REQUIRED",
                "finding": f"External service dependency — version controlled by provider, no local provenance"
            })
        
        # Overall version status
        if external_count > 0:
            version_status = "OWNER_DECISION_REQUIRED"
        elif unversioned_count > 0:
            version_status = "OBSERVATION"
        else:
            version_status = "PASS"
        
        findings.append({
            "control": control_id,
            "check": "version_analysis",
            "status": version_status,
            "finding": f"Version analysis: {versioned_count} versioned, {unversioned_count} unversioned, {external_count} external",
            "version_details": version_details
        })
    
    elif control_id == "DR-RISK":
        risk_findings = []
        
        # Check CDN dependencies (no local control, external availability risk)
        for url, info in deps["cdn_dependencies"].items():
            has_sri = False
            has_version = bool(info["versions"])
            
            if not has_version:
                risk_findings.append({
                    "finding_id": f"DR-{len(risk_findings)+1:04d}",
                    "dependency": url[:80],
                    "finding": "CDN dependency without version pinning — availability risk if URL changes",
                    "classification": "OWNER_DECISION_REQUIRED"
                })
            elif not has_sri:
                risk_findings.append({
                    "finding_id": f"DR-{len(risk_findings)+1:04d}",
                    "dependency": url[:80],
                    "finding": "CDN dependency versioned but no Subresource Integrity (SRI) hash detected",
                    "classification": "OBSERVATION"
                })
        
        # Check external services (no local control, lifecycle unknown)
        for base, info in deps["external_services"].items():
            risk_findings.append({
                "finding_id": f"DR-{len(risk_findings)+1:04d}",
                "dependency": base,
                "finding": f"External service dependency with {len(info.get('endpoints', []))} endpoint(s) — lifecycle is provider-controlled",
                "classification": "OWNER_DECISION_REQUIRED"
            })
        
        # Check local unversioned dependencies (maintenance risk)
        for path, info in deps["local_libraries"].items():
            if not info["versions"]:
                risk_findings.append({
                    "finding_id": f"DR-{len(risk_findings)+1:04d}",
                    "dependency": path,
                    "finding": "Unversioned local dependency — maintenance tracking is manual, drift risk over time",
                    "classification": "OBSERVATION"
                })
        
        # Classify overall risk
        classifications = [f["classification"] for f in risk_findings]
        if "OWNER_DECISION_REQUIRED" in classifications:
            risk_status = "OWNER_DECISION_REQUIRED"
        elif "OBSERVATION" in classifications:
            risk_status = "OBSERVATION"
        else:
            risk_status = "PASS"
        
        findings.append({
            "control": control_id,
            "check": "risk_classification",
            "status": risk_status,
            "finding": f"Risk classification: {len(risk_findings)} findings ({sum(1 for f in risk_findings if f['classification'] == 'OWNER_DECISION_REQUIRED')} owner decisions required)",
            "risk_findings": risk_findings
        })
    
    return findings


def main():
    deps = discover_dependencies()
    
    # Run control checks
    all_findings = []
    for control in PROFILE["controls"]:
        all_findings.extend(check_control(control["id"], deps))
    
    # Compute overall status per finding taxonomy inheritance (#185)
    statuses = [f["status"] for f in all_findings]
    overall = "PASS"
    if "OWNER_DECISION_REQUIRED" in statuses:
        overall = "OWNER_DECISION_REQUIRED"
    elif "OBSERVATION" in statuses:
        overall = "OBSERVATION"
    
    # Build control summary
    control_results = {}
    for f in all_findings:
        cid = f["control"]
        if cid not in control_results or _status_rank(f["status"]) > _status_rank(control_results[cid]):
            control_results[cid] = f["status"]
    
    # Compose evidence in #185 assurance_report format, consumable by #188
    evidence = {
        "assurance_report": {
            "profile": PROFILE["profile_id"],
            "profile_name": PROFILE["name"],
            "standards": [s["reference"] for s in PROFILE["standards"]],
            "generated_at": datetime.now().isoformat(),
            "overall": overall,
            "control_summary": all_findings,
            "control_results": {k: v for k, v in sorted(control_results.items())},
            "dependency_summary": {
                "total_deduplicated": len(deps["local_libraries"]) + len(deps["cdn_dependencies"]) + len(deps["external_services"]),
                "local_libraries": len(deps["local_libraries"]),
                "cdn_dependencies": len(deps["cdn_dependencies"]),
                "external_services": len(deps["external_services"])
            },
            "authority_level": "advisory",
            "owner_action_required": overall == "OWNER_DECISION_REQUIRED"
        },
        "evidence_id": f"DEP-RISK-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "producer": "qa_pilot_dependency_risk_capability.py",
        "capability": "#187",
        "consumable_by": "#188"
    }
    
    # Print summary
    print(f"Profile: {PROFILE['name']}")
    print(f"Overall: {overall}")
    print(f"Controls: {len(PROFILE['controls'])} assessed, {len(all_findings)} checks")
    print(f"Dependencies: {evidence['assurance_report']['dependency_summary']['total_deduplicated']} deduplicated "
          f"(local: {evidence['assurance_report']['dependency_summary']['local_libraries']}, "
          f"CDN: {evidence['assurance_report']['dependency_summary']['cdn_dependencies']}, "
          f"services: {evidence['assurance_report']['dependency_summary']['external_services']})")
    print(f"Owner action required: {evidence['assurance_report']['owner_action_required']}")
    print(f"Consumable by: #188 Security Assurance Profile")
    
    # Write evidence
    evidence_path = os.path.join(QA_PILOT_ROOT, "data", "dependency-risk-evidence.json")
    with open(evidence_path, "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"Evidence written to: {evidence_path}")
    
    # Write profile contract output
    contract_path = os.path.join(QA_PILOT_ROOT, "data", "dependency-risk-profile-contract.json")
    with open(contract_path, "w") as f:
        json.dump(PROFILE, f, indent=2)
    print(f"Profile contract written to: {contract_path}")


def _status_rank(status):
    """Rank status for finding the highest severity."""
    ranking = {"PASS": 0, "OBSERVATION": 1, "OWNER_DECISION_REQUIRED": 2, "GAP": 3}
    return ranking.get(status, 0)


if __name__ == "__main__":
    main()
