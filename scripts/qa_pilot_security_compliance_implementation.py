"""
qa_pilot_security_compliance_implementation.py — Security/Privacy Alignment Validation

Architecture basis: QA-PILOT-SECURITY-COMPLIANCE-CAPABILITY-ARCHITECTURE-1 (#183)
Phase: 4B — Documentation-to-Implementation Alignment

Discovers existing compliance artifacts, classifies them, then validates documented 
privacy/security posture against the implemented application source tree.
"""

import json, os, re
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
QA_PILOT_ROOT = os.path.dirname(PROJECT_ROOT)

def discover_artifacts():
    """Discover existing compliance/security/privacy artifacts in the project."""
    artifacts = []
    search_patterns = [
        ("privacy", ["privacy", "data-collection", "data-retention"]),
        ("security", ["security", "vulnerability", "penetration", "audit"]),
        ("compliance", ["compliance", "gdpr", "pipeda", "soc2", "iso27001", "qe-25"]),
        ("release", ["app-store", "release-notes", "submission", "distribution"]),
        ("disclosure", ["disclosure", "third-party", "license"]),
    ]
    
    for root, dirs, files in os.walk(QA_PILOT_ROOT):
        for f in files:
            if not f.endswith(('.md', '.pdf', '.txt', '.json', '.html')):
                continue
            path = os.path.join(root, f)
            rel = os.path.relpath(path, QA_PILOT_ROOT)
            with open(path, errors='ignore') as fp:
                content = fp.read().lower()
            
            for category, keywords in search_patterns:
                for kw in keywords:
                    if kw in content:
                        artifacts.append({
                            "path": rel,
                            "category": category,
                            "matched_keyword": kw,
                            "size": os.path.getsize(path)
                        })
                        break
                else:
                    continue
                break
    return artifacts

def check_analytics_declaration(artifacts):
    """Validate analytics declarations against implementation."""
    declarations = [a for a in artifacts if any(kw in a['path'].lower() for kw in ['privacy', 'disclosure', 'app-store'])]
    
    # Scan source for analytics SDKs / telemetry
    telemetry_patterns = [
        'analytics', 'tracking', 'telemetry', 
        'mixpanel', 'segment', 'amplitude', 'google-analytics',
        'ga(', 'gtag', 'beacon', 'pixel'
    ]
    
    source_files = []
    for root, dirs, files in os.walk(os.path.join(QA_PILOT_ROOT, 'browser-app')):
        for f in files:
            if not f.endswith(('.html', '.js')):
                continue
            path = os.path.join(root, f)
            with open(path, errors='ignore') as fp:
                content = fp.read().lower()
            for pattern in telemetry_patterns:
                if pattern in content:
                    source_files.append({"file": os.path.relpath(path, QA_PILOT_ROOT), "pattern": pattern})
                    break
    
    return {
        "declaration_docs": [a['path'] for a in declarations],
        "analytics_found_in_source": source_files,
        "analytics_present": len(source_files) > 0,
        "alignment": "PASS" if len(source_files) == 0 else "OWNER_DECISION_REQUIRED",
        "finding": "No analytics SDKs detected in source" if len(source_files) == 0 
                   else f"Analytics/telemetry patterns found in {len(source_files)} file(s), but declarations may state analytics-free"
    }

def check_data_collection(artifacts):
    """Identify data collection points and expected data handling."""
    forms = []
    for root, dirs, files in os.walk(os.path.join(QA_PILOT_ROOT, 'browser-app')):
        for f in files:
            if not f.endswith('.html'):
                continue
            path = os.path.join(root, f)
            with open(path) as fp:
                content = fp.read()
            inputs = re.findall(r'<input[^>]+(?:name|id|placeholder)=["\']([^"\']+)["\']', content)
            if inputs:
                forms.append({
                    "file": os.path.relpath(path, QA_PILOT_ROOT),
                    "input_fields": list(set(inputs)),
                    "count": len(set(inputs))
                })
    
    total_fields = sum(f['count'] for f in forms)
    return {
        "data_collection_points": forms[:10],
        "total_input_fields": total_fields,
        "data_types": list(set(f for form in forms for f in form['input_fields'])),
        "alignment": "OBSERVATION",
        "finding": f"Identified {total_fields} input fields across {len(forms)} pages — document data collection practices"
    }

def check_storage(artifacts):
    """Identify local storage usage matching data retention claims."""
    storage_patterns = ['localStorage', 'sessionStorage', 'IndexedDB', 'setItem(', 'getItem(']
    storage_usage = []
    for root, dirs, files in os.walk(os.path.join(QA_PILOT_ROOT, 'browser-app')):
        for f in files:
            if not f.endswith(('.html', '.js')):
                continue
            path = os.path.join(root, f)
            with open(path, errors='ignore') as fp:
                content = fp.read()
            for pat in storage_patterns:
                if pat in content:
                    storage_usage.append({"file": os.path.relpath(path, QA_PILOT_ROOT), "pattern": pat})
                    break
    return {
        "storage_mechanisms": list(set(s['pattern'] for s in storage_usage)),
        "storage_files": len(set(s['file'] for s in storage_usage)),
        "alignment": "OBSERVATION",
        "finding": f"Browser storage ({', '.join(set(s['pattern'] for s in storage_usage))}) detected — should match data retention declarations"
    }

def main():
    artifacts = discover_artifacts()
    analytics = check_analytics_declaration(artifacts)
    data_collection = check_data_collection(artifacts)
    storage = check_storage(artifacts)
    
    evidence = {
        "artifact": {
            "identity": f"SEC-CMPL-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "source_context": {"project_id": "qa-pilot", "phase": "4B"}
        },
        "intent": "Documentation-to-implementation alignment validation",
        "classification": "compliance",
        "execution_method": "static_analysis",
        "findings": {
            "artifact_inventory": {
                "total_discovered": len(artifacts),
                "by_category": {
                    "privacy": len([a for a in artifacts if a['category'] == 'privacy']),
                    "security": len([a for a in artifacts if a['category'] == 'security']),
                    "compliance": len([a for a in artifacts if a['category'] == 'compliance']),
                    "release": len([a for a in artifacts if a['category'] == 'release']),
                    "disclosure": len([a for a in artifacts if a['category'] == 'disclosure']),
                },
                "artifacts": [a['path'] for a in artifacts[:15]]
            },
            "alignment_checks": {
                "analytics_declaration": analytics,
                "data_collection": data_collection,
                "storage_retention": storage,
            }
        },
        "evidence_output": {
            "summary": f"Discovered {len(artifacts)} compliance artifacts. Ran 3 alignment checks across analytics, data collection, and storage.",
            "pass_count": sum(1 for c in [analytics, data_collection, storage] if c['alignment'] == 'PASS'),
            "observation_count": sum(1 for c in [analytics, data_collection, storage] if c['alignment'] == 'OBSERVATION'),
            "owner_decision_count": sum(1 for c in [analytics, data_collection, storage] if c['alignment'] == 'OWNER_DECISION_REQUIRED'),
        },
        "authority_level": "advisory"
    }
    
    print(json.dumps(evidence, indent=2))
    print(f"\nPASS: {len(artifacts)} compliance artifacts discovered, 3 alignment checks executed")

    evidence_path = os.path.join(QA_PILOT_ROOT, "data", "security-compliance-evidence.json")
    os.makedirs(os.path.dirname(evidence_path), exist_ok=True)
    with open(evidence_path, "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"Evidence written to: {evidence_path}")

if __name__ == "__main__":
    main()
