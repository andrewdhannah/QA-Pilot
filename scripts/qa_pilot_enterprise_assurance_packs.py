"""
qa_pilot_enterprise_assurance_packs.py — Enterprise Assurance Packs

Creates reusable enterprise assurance profiles per #185 architecture.
"""

import json, os
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
QA_PILOT_ROOT = os.path.dirname(PROJECT_ROOT)

PROFILES = [
    {
        "profile_id": "SOC2-SECURITY-ENTERPRISE-1",
        "name": "SOC 2 Security Enterprise Profile",
        "standards": [{"reference": "SOC 2 TSC", "description": "Security Trust Services Criteria"}],
        "controls": [
            {"id": "SOC2-CC6.1", "description": "Logical and physical access controls", "capabilities": ["security"], "evidence_required": ["implementation", "documentation"]},
            {"id": "SOC2-CC7.1", "description": "Monitoring of security events", "capabilities": ["security"], "evidence_required": ["implementation"]},
            {"id": "SOC2-CC8.1", "description": "Change management", "capabilities": ["regression"], "evidence_required": ["test_result"]},
        ]
    },
    {
        "profile_id": "ISO27001-ISMS-1",
        "name": "ISO 27001 ISMS Profile",
        "standards": [{"reference": "ISO/IEC 27001", "description": "Information security management"}],
        "controls": [
            {"id": "ISO-A.9", "description": "Access control", "capabilities": ["security"], "evidence_required": ["implementation", "documentation"]},
            {"id": "ISO-A.12", "description": "Operations security", "capabilities": ["security", "regression"], "evidence_required": ["implementation", "test_result"]},
            {"id": "ISO-A.16", "description": "Incident management", "capabilities": ["compliance"], "evidence_required": ["documentation"]},
        ]
    },
    {
        "profile_id": "GDPR-EXTENDED-ENTERPRISE-1",
        "name": "GDPR Extended Enterprise Profile",
        "standards": [{"reference": "GDPR", "description": "EU General Data Protection Regulation — Extended"}],
        "controls": [
            {"id": "GDPR-ART5", "description": "Lawfulness, fairness, transparency", "capabilities": ["privacy", "language"], "evidence_required": ["documentation"]},
            {"id": "GDPR-ART17", "description": "Right to erasure", "capabilities": ["privacy"], "evidence_required": ["implementation", "documentation"]},
            {"id": "GDPR-ART32", "description": "Security of processing", "capabilities": ["security", "privacy"], "evidence_required": ["implementation", "documentation"]},
        ]
    },
]

def main():
    report = {
        "enterprise_profiles": {
            "generated_at": datetime.now().isoformat(),
            "profiles_created": len(PROFILES),
            "architecture_basis": "#185",
            "profiles": [],
        }
    }
    
    for profile in PROFILES:
        report["enterprise_profiles"]["profiles"].append({
            "profile_id": profile["profile_id"],
            "name": profile["name"],
            "standards": [s["reference"] for s in profile["standards"]],
            "controls": len(profile["controls"]),
            "capabilities_used": list(set(c for ctrl in profile["controls"] for c in ctrl["capabilities"])),
            "authority_level": "advisory"
        })
    
    print(json.dumps(report, indent=2))
    print(f"\nEnterprise packs: {len(PROFILES)} profiles created")
    for p in report["enterprise_profiles"]["profiles"]:
        print(f"  {p['name']}: {p['controls']} controls, {len(p['capabilities_used'])} capabilities")

    evidence_path = os.path.join(QA_PILOT_ROOT, "data", "enterprise-assurance-evidence.json")
    with open(evidence_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nEvidence written to: {evidence_path}")

if __name__ == "__main__":
    main()
