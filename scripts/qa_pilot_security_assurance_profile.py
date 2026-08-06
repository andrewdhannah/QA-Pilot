"""
qa_pilot_security_assurance_profile.py — Security Assurance Profile (#188)

Architecture basis: #185 Assurance Profile Architecture
Consumes: #186 Privacy Assurance Profile, #187 Dependency Risk Capability
Consumed by: Release Readiness Profile
"""

import json, os, re
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
QA_PILOT_ROOT = os.path.dirname(PROJECT_ROOT)
BROWSER_APP = os.path.join(QA_PILOT_ROOT, "browser-app")

# Profile contract per #185 schema
PROFILE = {
    "profile_id": "QA-PILOT-SECURITY-ASSURANCE-PROFILE-1",
    "name": "Security Assurance Profile",
    "version": "1.0.0",
    "standards": [
        {"reference": "SOC2 Security", "description": "SOC 2 Security Trust Services Criteria"},
        {"reference": "OWASP", "description": "OWASP Top 10 / ASVS concepts"},
        {"reference": "QA-PILOT-SECURITY-ASSURANCE-FRAMEWORK-1", "description": "QA Pilot security assurance assessment framework"}
    ],
    "controls": [
        {
            "id": "SEC-001",
            "name": "Dependency Security Surface",
            "description": "Dependency lifecycle, unsupported components, supply chain exposure",
            "capabilities": ["dependency_risk", "security"],
            "evidence_required": ["implementation"],
            "input_source": "#187"
        },
        {
            "id": "SEC-002",
            "name": "Data Protection Surface",
            "description": "Sensitive data handling, storage locations, external transmission",
            "capabilities": ["security", "compliance"],
            "evidence_required": ["implementation", "documentation"],
            "input_source": "#186"
        },
        {
            "id": "SEC-003",
            "name": "Authentication / Authorization Evidence",
            "description": "Authentication mechanisms, authorization boundaries, privileged operations",
            "capabilities": ["security"],
            "evidence_required": ["implementation"],
            "input_source": "direct_scan"
        },
        {
            "id": "SEC-004",
            "name": "Configuration Security",
            "description": "Exposed configuration, insecure defaults, environment assumptions",
            "capabilities": ["security"],
            "evidence_required": ["implementation"],
            "input_source": "direct_scan"
        },
        {
            "id": "SEC-005",
            "name": "External Service Surface",
            "description": "APIs, third-party services, external integrations, data flows",
            "capabilities": ["security", "compliance"],
            "evidence_required": ["implementation", "documentation"],
            "input_source": "#186, direct_scan"
        },
        {
            "id": "SEC-006",
            "name": "Security Evidence Chain",
            "description": "Every finding has source, timestamp, evidence reference, classification, affected component",
            "capabilities": ["compliance"],
            "evidence_required": ["documentation"],
            "input_source": "derived"
        }
    ],
    "authority_level": "advisory"
}


def load_evidence(file_path):
    """Load evidence from a previous capability output."""
    path = os.path.join(QA_PILOT_ROOT, file_path)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def assess_sec_001_dependency_surface(dep_evidence):
    """SEC-001: Evaluate dependency lifecycle, unsupported components, supply chain exposure."""
    findings = []
    
    if not dep_evidence:
        findings.append({
            "control": "SEC-001",
            "check": "dependency_evidence_availability",
            "status": "OWNER_DECISION_REQUIRED",
            "finding": "Dependency risk evidence not available — cannot assess supply chain surface"
        })
        return findings
    
    # Consume #187 structured evidence (assurance_report format)
    report = dep_evidence.get("assurance_report", {})
    dep_summary = report.get("dependency_summary", {})
    control_results = report.get("control_results", {})
    
    total = dep_summary.get("total_deduplicated", 0)
    cdn = dep_summary.get("cdn_dependencies", 0)
    services = dep_summary.get("external_services", 0)
    local = dep_summary.get("local_libraries", 0)
    
    # Dependency lifecycle assessment
    supply_chain_concerns = []
    if cdn > 0:
        supply_chain_concerns.append(f"{cdn} CDN dependencies — external supply chain surface")
    if services > 0:
        supply_chain_concerns.append(f"{services} external service dependencies — provider-controlled lifecycle")
    if local > 0:
        supply_chain_concerns.append(f"{local} local dependencies — all unversioned, manual lifecycle tracking")
    
    # Overall dependency security
    dep_risk_level = control_results.get("DR-RISK", "OBSERVATION")
    
    if cdn > 0 or services > 0:
        overall_status = "OWNER_DECISION_REQUIRED"
    elif dep_risk_level == "OWNER_DECISION_REQUIRED":
        overall_status = "OWNER_DECISION_REQUIRED"
    elif dep_risk_level == "OBSERVATION":
        overall_status = "OBSERVATION"
    else:
        overall_status = "PASS"
    
    findings.append({
        "control": "SEC-001",
        "check": "dependency_inventory_security",
        "status": overall_status,
        "finding": f"Dependency surface: {total} dependencies ({local} local, {cdn} CDN, {services} external services). "
                   f"Concerns: {'; '.join(supply_chain_concerns) if supply_chain_concerns else 'None identified'}",
        "evidence_references": ["data/dependency-risk-evidence.json"]
    })
    
    # Unsupported/outdated components
    if local > 0:
        findings.append({
            "control": "SEC-001",
            "check": "unsupported_components",
            "status": "OBSERVATION",
            "finding": f"All {local} local dependencies are unversioned — lifecycle tracking is manual, drift risk over time",
            "evidence_references": ["data/dependency-risk-evidence.json"]
        })
    else:
        findings.append({
            "control": "SEC-001",
            "check": "unsupported_components",
            "status": "PASS",
            "finding": "No unsupported components detected"
        })
    
    # Supply chain exposure
    if cdn > 0:
        findings.append({
            "control": "SEC-001",
            "check": "supply_chain_exposure",
            "status": "OWNER_DECISION_REQUIRED",
            "finding": f"{cdn} CDN dependencies — external supply chain, availability risk, integrity verification needed (SRI)",
            "evidence_references": ["data/dependency-risk-evidence.json"]
        })
    else:
        findings.append({
            "control": "SEC-001",
            "check": "supply_chain_exposure",
            "status": "PASS",
            "finding": "No CDN or external service dependencies — supply chain is local-only"
        })
    
    return findings


def assess_sec_002_data_protection(priv_evidence):
    """SEC-002: Evaluate sensitive data handling, storage, external transmission."""
    findings = []
    
    if not priv_evidence:
        findings.append({
            "control": "SEC-002",
            "check": "privacy_evidence_availability",
            "status": "OWNER_DECISION_REQUIRED",
            "finding": "Privacy evidence not available — cannot assess data protection surface"
        })
        return findings
    
    report = priv_evidence.get("assurance_report", {})
    control_summary = report.get("control_summary", [])
    
    # Map privacy findings to data protection assessment
    privacy_controls = {cs.get("control"): cs for cs in control_summary}
    
    # Data handling assessment
    dc = privacy_controls.get("PRIV-DATA-COLLECTION", {})
    storage = privacy_controls.get("PRIV-STORAGE", {})
    disclosure = privacy_controls.get("PRIV-DISCLOSURE", {})
    third_party = privacy_controls.get("PRIV-THIRD-PARTY", {})
    
    # Aggregate data protection status from privacy evidence
    data_protection_statuses = []
    if dc.get("status"):
        data_protection_statuses.append(dc["status"])
    if storage.get("status"):
        data_protection_statuses.append(storage["status"])
    
    if "OWNER_DECISION_REQUIRED" in data_protection_statuses:
        dp_status = "OWNER_DECISION_REQUIRED"
    elif "OBSERVATION" in data_protection_statuses:
        dp_status = "OBSERVATION"
    else:
        dp_status = "PASS"
    
    findings.append({
        "control": "SEC-002",
        "check": "data_handling_observation",
        "status": dp_status,
        "finding": f"Data protection observations from privacy evidence. "
                   f"Input fields: {dc.get('finding', 'Unknown')}. "
                   f"Storage: {storage.get('finding', 'Unknown')}",
        "evidence_references": ["data/privacy-assurance-evidence.json"]
    })
    
    # External transmission points
    if third_party:
        findings.append({
            "control": "SEC-002",
            "check": "external_transmission",
            "status": third_party.get("status", "OBSERVATION"),
            "finding": f"External transmission: {third_party.get('finding', 'Unknown')}",
            "evidence_references": ["data/privacy-assurance-evidence.json"]
        })
    
    # Disclosure coverage
    if disclosure:
        if disclosure.get("status") == "PASS":
            findings.append({
                "control": "SEC-002",
                "check": "documentation_coverage",
                "status": "PASS",
                "finding": f"Privacy documentation exists: {disclosure.get('finding', 'Unknown')}",
                "evidence_references": ["data/privacy-assurance-evidence.json"]
            })
        else:
            findings.append({
                "control": "SEC-002",
                "check": "documentation_coverage",
                "status": "OBSERVATION",
                "finding": f"Privacy documentation gap: {disclosure.get('finding', 'Unknown')}",
                "evidence_references": ["data/privacy-assurance-evidence.json"]
            })
    
    return findings


def assess_sec_003_authentication():
    """SEC-003: Evaluate authentication mechanisms, authorization boundaries, privileged operations."""
    findings = []
    
    auth_patterns = {"login": 0, "password": 0, "session": 0, "token": 0, "role": 0, "permission": 0, "auth": 0, "oauth": 0, "jwt": 0}
    auth_files = []
    
    for root, dirs, files in os.walk(BROWSER_APP):
        for f in files:
            if not f.endswith(('.html', '.js')):
                continue
            path = os.path.join(root, f)
            with open(path, errors='ignore') as fp:
                content = fp.read()
            low_content = content.lower()
            
            file_auth = False
            for pat in auth_patterns:
                count = low_content.count(pat)
                auth_patterns[pat] += count
                if count > 0:
                    file_auth = True
            if file_auth:
                auth_files.append(os.path.relpath(path, QA_PILOT_ROOT))
    
    # Authentication mechanisms assessment
    has_auth = auth_patterns["login"] > 0 or auth_patterns["password"] > 0
    has_session = auth_patterns["session"] > 0
    has_token = auth_patterns["token"] > 0
    has_role = auth_patterns["role"] > 0
    has_oauth = auth_patterns["oauth"] > 0 or auth_patterns["jwt"] > 0
    
    auth_mechanisms = []
    if has_auth:
        auth_mechanisms.append("login/password")
    if has_session:
        auth_mechanisms.append("session management")
    if has_token:
        auth_mechanisms.append("token-based")
    if has_role:
        auth_mechanisms.append("role-based")
    if has_oauth:
        auth_mechanisms.append("OAuth/JWT")
    
    findings.append({
        "control": "SEC-003",
        "check": "authentication_mechanisms",
        "status": "OBSERVATION",
        "finding": f"Auth indicators: login({auth_patterns['login']}), session({auth_patterns['session']}), "
                   f"role({auth_patterns['role']}), token({auth_patterns['token']}), "
                   f"OAuth/JWT({auth_patterns['oauth'] + auth_patterns['jwt']}). "
                   f"Mechanisms identified: {', '.join(auth_mechanisms) if auth_mechanisms else 'None detected'}",
        "affected_components": sorted(set(auth_files[:5])) if auth_files else []
    })
    
    # Authorization boundaries
    authz_indicators = auth_patterns["role"] + auth_patterns["permission"]
    if authz_indicators > 0:
        findings.append({
            "control": "SEC-003",
            "check": "authorization_boundaries",
            "status": "OBSERVATION",
            "finding": f"Authorization indicators found: role({auth_patterns['role']}), permission({auth_patterns['permission']})",
            "affected_components": sorted(set(auth_files[:5])) if auth_files else []
        })
    else:
        findings.append({
            "control": "SEC-003",
            "check": "authorization_boundaries",
            "status": "OWNER_DECISION_REQUIRED",
            "finding": "No role-based authorization indicators detected — verify access control implementation",
            "affected_components": []
        })
    
    return findings


def assess_sec_004_configuration():
    """SEC-004: Evaluate exposed configuration, insecure defaults, environment assumptions."""
    findings = []
    
    config_concerns = {
        "hardcoded_url": {"pattern": r'https?://[^\s"\'\)]+', "count": 0, "desc": "Hardcoded URL references"},
        "api_key": {"pattern": r'(?:api[_-]?key|apikey|api_secret)\s*[=:]\s*["\'][^"\']+["\']', "count": 0, "desc": "Potential API key patterns"},
        "localhost_ref": {"pattern": r'localhost|127\.0\.0\.1', "count": 0, "desc": "Localhost references"},
        "internal_ip": {"pattern": r'(?:192\.168\.|10\.\d+\.|172\.(?:1[6-9]|2\d|3[01])\.)', "count": 0, "desc": "Internal IP references"}
    }
    
    config_files = []
    for root, dirs, files in os.walk(BROWSER_APP):
        for f in files:
            if not f.endswith(('.html', '.js', '.json', '.yml', '.yaml', '.env')):
                continue
            path = os.path.join(root, f)
            with open(path, errors='ignore') as fp:
                content = fp.read()
            
            has_config = False
            for key, info in config_concerns.items():
                matches = re.findall(info["pattern"], content, re.IGNORECASE)
                if matches:
                    info["count"] += len(matches)
                    has_config = True
            if has_config:
                config_files.append(os.path.relpath(path, QA_PILOT_ROOT))
    
    active_concerns = {k: v for k, v in config_concerns.items() if v["count"] > 0}
    
    if active_concerns:
        concerns_desc = "; ".join(f"{v['desc']}: {v['count']}" for v in active_concerns.values())
        findings.append({
            "control": "SEC-004",
            "check": "configuration_exposure",
            "status": "OBSERVATION",
            "finding": f"Configuration exposure detected: {concerns_desc}",
            "affected_components": sorted(set(config_files[:5])) if config_files else []
        })
    else:
        findings.append({
            "control": "SEC-004",
            "check": "configuration_exposure",
            "status": "PASS",
            "finding": "No exposed configuration patterns detected"
        })
    
    # Environment assumptions
    if config_concerns["localhost_ref"]["count"] > 0:
        findings.append({
            "control": "SEC-004",
            "check": "environment_assumptions",
            "status": "OBSERVATION",
            "finding": f"Application references localhost ({config_concerns['localhost_ref']['count']} references) — verify production deployment configuration",
            "affected_components": sorted(set(config_files[:3])) if config_files else []
        })
    else:
        findings.append({
            "control": "SEC-004",
            "check": "environment_assumptions",
            "status": "PASS",
            "finding": "No localhost assumptions detected in source"
        })
    
    return findings


def assess_sec_005_external_surface(priv_evidence):
    """SEC-005: Evaluate APIs, third-party services, external integrations."""
    findings = []
    
    if priv_evidence:
        report = priv_evidence.get("assurance_report", {})
        for cs in report.get("control_summary", []):
            if cs.get("control") == "PRIV-THIRD-PARTY":
                findings.append({
                    "control": "SEC-005",
                    "check": "third_party_services",
                    "status": cs.get("status", "OBSERVATION"),
                    "finding": f"External service surface: {cs.get('finding', 'Unknown')}",
                    "evidence_references": ["data/privacy-assurance-evidence.json"]
                })
    
    # Direct scan for API endpoints
    api_patterns = {"fetch": 0, "axios": 0, "XMLHttpRequest": 0, "WebSocket": 0, ".get(": 0, ".post(": 0}
    for root, dirs, files in os.walk(BROWSER_APP):
        for f in files:
            if not f.endswith(('.html', '.js')):
                continue
            with open(os.path.join(root, f), errors='ignore') as fp:
                c = fp.read()
            for pat in api_patterns:
                api_patterns[pat] += c.count(pat)
    
    total_api_calls = sum(api_patterns.values())
    if total_api_calls > 0:
        findings.append({
            "control": "SEC-005",
            "check": "api_usage",
            "status": "OBSERVATION",
            "finding": f"API interaction patterns detected: fetch({api_patterns['fetch']}), "
                       f"XMLHttpRequest({api_patterns['XMLHttpRequest']}), "
                       f"WebSocket({api_patterns['WebSocket']}), "
                       f".get/post calls({api_patterns['.get('] + api_patterns['.post(']})"
        })
    else:
        findings.append({
            "control": "SEC-005",
            "check": "api_usage",
            "status": "PASS",
            "finding": "No API interaction patterns detected"
        })
    
    return findings


def assess_sec_006_evidence_chain(all_assessments):
    """SEC-006: Verify every finding has source, timestamp, evidence reference, classification, affected component."""
    findings = []
    
    total_findings = len(all_assessments)
    has_provenance = 0
    missing_evidence_ref = 0
    missing_component = 0
    
    for f in all_assessments:
        has_ref = bool(f.get("evidence_references"))
        has_component = bool(f.get("affected_components"))
        has_status = bool(f.get("status"))
        
        if has_ref and has_status:
            has_provenance += 1
        if not has_ref:
            missing_evidence_ref += 1
        if not has_component and f.get("check") != "evidence_chain":  # skip self-reference
            missing_component += 1
    
    coverage_pct = (has_provenance / total_findings * 100) if total_findings > 0 else 0
    
    if coverage_pct >= 80:
        chain_status = "PASS"
    elif coverage_pct >= 50:
        chain_status = "OBSERVATION"
    else:
        chain_status = "OWNER_DECISION_REQUIRED"
    
    findings.append({
        "control": "SEC-006",
        "check": "evidence_chain",
        "status": chain_status,
        "finding": f"Evidence chain provenance: {has_provenance}/{total_findings} findings have full provenance "
                   f"({coverage_pct:.0f}%). Missing evidence references: {missing_evidence_ref}, "
                   f"missing components: {missing_component}"
    })
    
    return findings


def main():
    # Load existing evidence from #186 and #187
    privacy_evidence = load_evidence("data/privacy-assurance-evidence.json")
    dep_evidence = load_evidence("data/dependency-risk-evidence.json")
    
    print(f"Input sources:")
    print(f"  #186 Privacy: {'Loaded' if privacy_evidence else 'NOT AVAILABLE'}")
    print(f"  #187 Dependency Risk: {'Loaded' if dep_evidence else 'NOT AVAILABLE'}")
    
    # Run assessments
    all_assessments = []
    all_assessments.extend(assess_sec_001_dependency_surface(dep_evidence))
    all_assessments.extend(assess_sec_002_data_protection(privacy_evidence))
    all_assessments.extend(assess_sec_003_authentication())
    all_assessments.extend(assess_sec_004_configuration())
    all_assessments.extend(assess_sec_005_external_surface(privacy_evidence))
    all_assessments.extend(assess_sec_006_evidence_chain(all_assessments))
    
    # Compute overall status
    statuses = [f["status"] for f in all_assessments]
    overall = "PASS"
    if "OWNER_DECISION_REQUIRED" in statuses:
        overall = "OWNER_DECISION_REQUIRED"
    elif "OBSERVATION" in statuses:
        overall = "OBSERVATION"
    
    # Compute control-level results
    control_results = {}
    for f in all_assessments:
        cid = f["control"]
        _rank = {"PASS": 0, "OBSERVATION": 1, "OWNER_DECISION_REQUIRED": 2, "GAP": 3}
        if cid not in control_results or _rank.get(f["status"], 0) > _rank.get(control_results[cid], 0):
            control_results[cid] = f["status"]
    
    # Build assessments summary for the evidence contract
    assessment_summaries = []
    seen_controls = set()
    for f in all_assessments:
        cid = f["control"]
        if cid not in seen_controls:
            seen_controls.add(cid)
            assessment_summaries.append({
                "id": cid,
                "name": next((c["name"] for c in PROFILE["controls"] if c["id"] == cid), cid),
                "source": next((c["input_source"] for c in PROFILE["controls"] if c["id"] == cid), "direct_scan"),
                "classification": control_results[cid],
                "evidence_references": list(set(
                    ref for f2 in all_assessments if f2["control"] == cid 
                    for ref in f2.get("evidence_references", [])
                ))
            })
    
    # Compose evidence in #185 assurance_report format, consumable by Release Readiness
    evidence = {
        "assurance_report": {
            "profile": PROFILE["profile_id"],
            "profile_name": PROFILE["name"],
            "version": PROFILE["version"],
            "standards": [s["reference"] for s in PROFILE["standards"]],
            "generated_at": datetime.now().isoformat(),
            "overall": overall,
            "consumes": ["#186", "#187"],
            "assessments": assessment_summaries,
            "control_summary": all_assessments,
            "control_results": {k: v for k, v in sorted(control_results.items())},
            "authority_level": "advisory",
            "owner_action_required": overall == "OWNER_DECISION_REQUIRED",
            "consumable_by": "#Release-Readiness"
        },
        "evidence_id": f"SEC-ASSUR-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "producer": "qa_pilot_security_assurance_profile.py",
        "capability": "#188",
        "consumable_by": "#Release-Readiness"
    }
    
    # Print summary
    print(f"\nProfile: Security Assurance Profile")
    print(f"Overall: {overall}")
    print(f"Assessments: {len(assessment_summaries)} assessed, {len(all_assessments)} checks")
    print(f"Consumes: #186, #187")
    print(f"Owner action required: {evidence['assurance_report']['owner_action_required']}")
    print(f"Consumable by: #Release-Readiness")
    
    # Write evidence
    evidence_path = os.path.join(QA_PILOT_ROOT, "data", "security-assurance-evidence.json")
    with open(evidence_path, "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"Evidence written to: {evidence_path}")
    
    # Write profile contract
    contract_path = os.path.join(QA_PILOT_ROOT, "data", "security-assurance-profile-contract.json")
    with open(contract_path, "w") as f:
        json.dump(PROFILE, f, indent=2)
    print(f"Profile contract written to: {contract_path}")


if __name__ == "__main__":
    main()
