"""
qa_pilot_model_assisted_assurance.py — Model-Assisted Assurance

Model proposes insights → QA Pilot validates → evidence produced → Owner decides.
"""

import json, os, subprocess
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
QA_PILOT_ROOT = os.path.dirname(PROJECT_ROOT)

def get_changed_source():
    """Get changed source files for model analysis."""
    try:
        diff = subprocess.run(["git", "diff", "--name-only", "HEAD~1"], capture_output=True, text=True, cwd=QA_PILOT_ROOT)
        files = [f.strip() for f in diff.stdout.split("\n") if f.strip()]
        # Return first few source files for analysis
        return [f for f in files if f.endswith(('.py', '.js', '.html', '.css'))][:5]
    except:
        return []

def analyze_intent(file_path):
    """Analyze source file intent (simulated model output)."""
    full_path = os.path.join(QA_PILOT_ROOT, file_path)
    if not os.path.exists(full_path):
        return None
    with open(full_path) as f:
        content = f.read()
    return {
        "file": file_path,
        "size": len(content),
        "lines": content.count('\n'),
        "model_observation": "File modified — review for assurance impact",
        "assurance_relevance": "high" if any(kw in file_path.lower() for kw in ['auth', 'login', 'security', 'privacy', 'data']) else "medium"
    }

def suggest_tests(file_path):
    """Suggest relevant assurance profiles from file change."""
    suggestions = []
    if any(kw in file_path.lower() for kw in ['auth', 'login', 'session']):
        suggestions.extend(["security", "uat"])
    if any(kw in file_path.lower() for kw in ['privacy', 'data', 'consent']):
        suggestions.extend(["privacy", "compliance"])
    if any(kw in file_path.lower() for kw in ['ui', 'view', 'page', 'html']):
        suggestions.extend(["accessibility", "language"])
    if file_path.endswith('.py'):
        suggestions.append("regression")
    return suggestions

def main():
    changed = get_changed_source()
    
    analysis = []
    test_suggestions = {}
    for f in changed:
        intent = analyze_intent(f)
        if intent:
            analysis.append(intent)
        suggestions = suggest_tests(f)
        if suggestions:
            test_suggestions[f] = suggestions
    
    evidence = {
        "artifact": {"identity": f"MODEL-{datetime.now().strftime('%Y%m%d-%H%M%S')}"},
        "intent": "Model-assisted assurance — code intent analysis and test suggestion",
        "classification": "assurance",
        "execution_method": "model_assisted",
        "findings": {
            "files_analyzed": len(changed),
            "analysis": analysis,
            "test_suggestions": test_suggestions,
        },
        "evidence_output": {
            "summary": f"Analyzed {len(changed)} changed files, generated {sum(len(v) for v in test_suggestions.values())} test suggestions across {len(test_suggestions)} files",
            "model_role": "Model proposes → QA Pilot validates → evidence produced → Owner decides"
        },
        "authority_level": "advisory",
        "governance": {
            "model_proposes": True,
            "qa_pilot_validates": True,
            "owner_decides": True,
            "model_does_not_decide": True
        }
    }
    
    print(json.dumps(evidence, indent=2))
    print(f"\nModel-assisted assurance: {len(changed)} files analyzed, {sum(len(v) for v in test_suggestions.values())} suggestions")

    evidence_path = os.path.join(QA_PILOT_ROOT, "data", "model-assisted-evidence.json")
    with open(evidence_path, "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"Evidence written to: {evidence_path}")

if __name__ == "__main__":
    main()
