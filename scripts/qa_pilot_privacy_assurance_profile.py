"""
qa_pilot_privacy_assurance_profile.py — Privacy Assurance Profile

Architecture basis: QA-PILOT-ASSURANCE-PROFILE-ARCHITECTURE-1 (#185)
Profile: Privacy (GDPR/PIPEDA/Apple)
First assurance profile pack.
"""

import json, os, re
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
QA_PILOT_ROOT = os.path.dirname(PROJECT_ROOT)

# Profile contract per #185 schema
PROFILE = {
    "profile_id": "QA-PILOT-PRIVACY-ASSURANCE-PROFILE-1",
    "name": "Privacy Assurance Profile",
    "version": "1.0.0",
    "standards": [
        {"reference": "GDPR", "description": "EU General Data Protection Regulation"},
        {"reference": "PIPEDA", "description": "Canadian Personal Information Protection and Electronic Documents Act"},
        {"reference": "Apple Privacy", "description": "Apple App Store Privacy Nutrition Labels"}
    ],
    "controls": [
        {"id": "PRIV-DATA-COLLECTION", "description": "Data collection practices match declared posture", "capabilities": ["compliance", "security"], "evidence_required": ["implementation", "documentation"], "escalation_rule": "drift = OWNER_DECISION_REQUIRED"},
        {"id": "PRIV-STORAGE", "description": "Data storage locations and mechanisms identified", "capabilities": ["compliance"], "evidence_required": ["implementation"]},
        {"id": "PRIV-RETENTION", "description": "Data retention practices match declared policy", "capabilities": ["compliance"], "evidence_required": ["documentation", "implementation"]},
        {"id": "PRIV-DISCLOSURE", "description": "Privacy documentation exists and covers required topics", "capabilities": ["compliance", "language"], "evidence_required": ["documentation"]},
        {"id": "PRIV-THIRD-PARTY", "description": "Third-party services and data sharing identified", "capabilities": ["compliance", "security"], "evidence_required": ["documentation", "implementation"]},
        {"id": "PRIV-CONSENT", "description": "User consent mechanisms exist where required", "capabilities": ["uat"], "evidence_required": ["implementation"]}
    ],
    "authority_level": "advisory"
}

def check_control(control_id):
    """Run the appropriate check for each privacy control."""
    findings = []
    
    if control_id == "PRIV-DATA-COLLECTION":
        # Check analytics declaration alignment
        analytics_found = []
        telemetry = ['analytics', 'tracking', 'telemetry', 'ga(', 'gtag']
        for root, dirs, files in os.walk(os.path.join(QA_PILOT_ROOT, 'browser-app')):
            for f in files:
                if not f.endswith(('.html', '.js')): continue
                path = os.path.join(root, f)
                with open(path, errors='ignore') as fp:
                    content = fp.read().lower()
                for pat in telemetry:
                    if pat in content:
                        analytics_found.append(os.path.relpath(path, QA_PILOT_ROOT))
                        break
        findings.append({
            "control": control_id,
            "check": "analytics_declaration_vs_source",
            "status": "OWNER_DECISION_REQUIRED" if analytics_found else "PASS",
            "finding": f"Analytics patterns found in {len(analytics_found)} file(s)" if analytics_found else "No analytics detected"
        })
        
        # Check input field inventory  
        total_inputs = 0
        for root, dirs, files in os.walk(os.path.join(QA_PILOT_ROOT, 'browser-app')):
            for f in files:
                if not f.endswith('.html'): continue
                with open(os.path.join(root, f)) as fp:
                    inputs = re.findall(r'<input[^>]+(?:name|id|placeholder)=', fp.read())
                    total_inputs += len(inputs)
        findings.append({
            "control": control_id,
            "check": "data_collection_inventory",
            "status": "OBSERVATION",
            "finding": f"Identified {total_inputs} input fields across application — data collection purposes should be documented"
        })
    
    elif control_id == "PRIV-STORAGE":
        storage = {'localStorage': 0, 'sessionStorage': 0, 'IndexedDB': 0}
        for root, dirs, files in os.walk(os.path.join(QA_PILOT_ROOT, 'browser-app')):
            for f in files:
                if not f.endswith(('.html', '.js')): continue
                with open(os.path.join(root, f), errors='ignore') as fp:
                    c = fp.read()
                for s in storage:
                    storage[s] += c.count(s)
        findings.append({
            "control": control_id,
            "check": "storage_mechanisms",
            "status": "OBSERVATION",
            "finding": f"Storage: localStorage({storage['localStorage']}), sessionStorage({storage['sessionStorage']}), IndexedDB({storage['IndexedDB']}) — storage documented?"
        })
    
    elif control_id == "PRIV-DISCLOSURE":
        privacy_docs = []
        for root, dirs, files in os.walk(QA_PILOT_ROOT):
            for f in files:
                if not f.endswith(('.md', '.txt', '.pdf')): continue
                with open(os.path.join(root, f), errors='ignore') as fp:
                    c = fp.read().lower()
                if any(kw in c for kw in ['privacy', 'gdpr', 'pipeda', 'data collection', 'personal information']):
                    privacy_docs.append(os.path.relpath(os.path.join(root, f), QA_PILOT_ROOT))
        
        coverage = "PASS" if len(privacy_docs) >= 3 else ("OBSERVATION" if len(privacy_docs) >= 1 else "GAP")
        findings.append({
            "control": control_id,
            "check": "privacy_documentation_coverage",
            "status": coverage,
            "finding": f"Found {len(privacy_docs)} privacy-related documents" if privacy_docs else "No privacy documentation found"
        })
    
    elif control_id == "PRIV-THIRD-PARTY":
        third_party = []
        patterns = ['cdn.', 'api.', 'https://', 'http://']
        for root, dirs, files in os.walk(os.path.join(QA_PILOT_ROOT, 'browser-app')):
            for f in files:
                if not f.endswith(('.html', '.js')): continue
                path = os.path.join(root, f)
                with open(path, errors='ignore') as fp:
                    content = fp.read()
                for pat in patterns:
                    matches = re.findall(r'https?://[^"\'\s]+', content)
                    for m in matches:
                        if m not in third_party:
                            third_party.append(m)
        findings.append({
            "control": control_id,
            "check": "third_party_services",
            "status": "OBSERVATION",
            "finding": f"Discovered {len(third_party)} external service references — verify third-party data sharing disclosures"
        })
    
    elif control_id == "PRIV-CONSENT":
        consent_mechanisms = []
        for root, dirs, files in os.walk(os.path.join(QA_PILOT_ROOT, 'browser-app')):
            for f in files:
                if not f.endswith('.html'): continue
                path = os.path.join(root, f)
                with open(path) as fp:
                    c = fp.read()
                if any(kw in c.lower() for kw in ['consent', 'agree', 'accept', 'opt-in', 'opt-out', 'cookie']):
                    consent_mechanisms.append(os.path.relpath(path, QA_PILOT_ROOT))
        findings.append({
            "control": control_id,
            "check": "consent_mechanisms",
            "status": "OBSERVATION" if consent_mechanisms else "GAP",
            "finding": f"Consent-related UI found in {len(consent_mechanisms)} page(s)" if consent_mechanisms else "No consent mechanisms detected"
        })
    
    return findings

def main():
    all_findings = []
    for control in PROFILE["controls"]:
        all_findings.extend(check_control(control["id"]))
    
    statuses = [f["status"] for f in all_findings]
    overall = "PASS"
    if "OWNER_DECISION_REQUIRED" in statuses:
        overall = "OWNER_DECISION_REQUIRED"
    elif "GAP" in statuses:
        overall = "OWNER_DECISION_REQUIRED"
    elif "OBSERVATION" in statuses:
        overall = "OBSERVATION"
    
    evidence = {
        "assurance_report": {
            "profile": PROFILE["profile_id"],
            "standards": [s["reference"] for s in PROFILE["standards"]],
            "generated_at": datetime.now().isoformat(),
            "overall": overall,
            "control_summary": all_findings,
            "authority_level": "advisory",
            "owner_action_required": overall == "OWNER_DECISION_REQUIRED"
        }
    }
    
    print(json.dumps(evidence, indent=2))
    print(f"\nProfile: {PROFILE['name']}")
    print(f"Overall: {overall}")
    print(f"Controls: {len(set(f['control'] for f in all_findings))} assessed, {len(all_findings)} individual checks")

    evidence_path = os.path.join(QA_PILOT_ROOT, "data", "privacy-assurance-evidence.json")
    with open(evidence_path, "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"Evidence written to: {evidence_path}")

if __name__ == "__main__":
    main()
