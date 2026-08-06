"""
qa_pilot_continuous_assurance_loop.py — Continuous Assurance Loop

Moves QA Pilot from event-driven assessment to continuous assurance.
Detects changes, selects affected profiles, runs targeted validation,
updates evidence, and flags staleness.
"""

import json, os, subprocess
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
QA_PILOT_ROOT = os.path.dirname(PROJECT_ROOT)
STALENESS_THRESHOLD_HOURS = 24

# Map file change patterns to affected assurance profiles
IMPACT_MAP = {
    "browser-app/": ["accessibility", "language", "uat"],
    "browser-app/js/": ["language", "dependency_risk"],
    "browser-app/admin/": ["accessibility", "uat"],
    "browser-app/apps/": ["accessibility", "uat"],
    "scripts/": ["regression"],
    "docs/": ["privacy", "security"],
    "project-state/": ["regression"],
    "data/": ["privacy", "security"],
}

PROFILE_SCRIPTS = {
    "regression": "qa_pilot_regression_capability.py",
    "uat": "qa_pilot_uat_capability.py",
    "accessibility": "qa_pilot_accessibility_capability.py",
    "performance": "qa_pilot_performance_capability.py",
    "language": None,
    "privacy": "qa_pilot_privacy_assurance_profile.py",
    "dependency_risk": "qa_pilot_dependency_risk_capability.py",
    "security": "qa_pilot_security_assurance_profile.py",
    "release": "qa_pilot_release_readiness_profile.py",
}

def detect_changes():
    """Detect changed files since last known state using git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1"],
            capture_output=True, text=True, cwd=QA_PILOT_ROOT
        )
        if result.returncode == 0:
            return [f.strip() for f in result.stdout.split("\n") if f.strip()]
        return []
    except:
        return []

def map_impact(changed_files):
    """Map changed files to affected assurance profiles."""
    affected = set()
    for f in changed_files:
        for prefix, profiles in IMPACT_MAP.items():
            if f.startswith(prefix):
                affected.update(profiles)
    return affected

def run_profile(profile_name):
    """Run a single assurance profile script if available."""
    script = PROFILE_SCRIPTS.get(profile_name)
    if not script or profile_name == "release":
        return None
    path = os.path.join(PROJECT_ROOT, script)
    if not os.path.exists(path):
        return None
    try:
        result = subprocess.run(
            ["python3", path],
            capture_output=True, text=True, cwd=QA_PILOT_ROOT, timeout=120
        )
        return {"profile": profile_name, "exit_code": result.returncode, "ran": True}
    except:
        return {"profile": profile_name, "exit_code": -1, "ran": False}

def check_staleness():
    """Check evidence staleness against threshold."""
    stale = []
    evidence_dir = os.path.join(QA_PILOT_ROOT, "data")
    if not os.path.exists(evidence_dir):
        return stale
    now = datetime.now()
    for f in os.listdir(evidence_dir):
        if not f.endswith(".json"):
            continue
        path = os.path.join(evidence_dir, f)
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        age_hours = (now - mtime).total_seconds() / 3600
        if age_hours > STALENESS_THRESHOLD_HOURS:
            stale.append({"file": f, "age_hours": round(age_hours, 1), "threshold": STALENESS_THRESHOLD_HOURS})
    return stale

def main():
    changed = detect_changes()
    affected = map_impact(changed) if changed else set()
    
    # If no git changes detected, fall back to full run
    if not affected:
        affected = {"regression", "uat", "accessibility", "performance", "privacy", "dependency_risk", "security"}
    
    results = []
    for profile in affected:
        r = run_profile(profile)
        if r:
            results.append(r)
    
    stale = check_staleness()
    
    # Always run release readiness aggregation after targeted profiles
    release_path = os.path.join(PROJECT_ROOT, "qa_pilot_release_readiness_profile.py")
    if os.path.exists(release_path):
        subprocess.run(["python3", release_path], cwd=QA_PILOT_ROOT, capture_output=True, text=True, timeout=120)
    
    evidence = {
        "continuous_assurance": {
            "loop_id": f"CA-{datetime.now().strftime('%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "change_detection": {
                "files_changed": len(changed),
                "affected_profiles": list(affected) if affected else ["full_suite"],
                "files": changed[:10]
            },
            "execution": {
                "profiles_run": len(results),
                "results": results
            },
            "staleness": {
                "threshold_hours": STALENESS_THRESHOLD_HOURS,
                "stale_evidence": stale
            },
            "authority_level": "advisory"
        }
    }
    
    print(json.dumps(evidence, indent=2))
    print(f"\nContinuous Assurance Loop: {len(changed)} changed file(s), {len(results)} profile(s) executed, {len(stale)} stale evidence file(s)")

    evidence_path = os.path.join(QA_PILOT_ROOT, "data", "continuous-assurance-evidence.json")
    with open(evidence_path, "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"Evidence written to: {evidence_path}")

if __name__ == "__main__":
    main()
