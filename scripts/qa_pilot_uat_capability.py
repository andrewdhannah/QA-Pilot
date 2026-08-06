"""
qa_pilot_uat_capability.py — UAT Scenario Generation Capability

Architecture basis: QA-PILOT-TESTING-CAPABILITY-ARCHITECTURE-1 (#178)
Phase: 1 — Core Validation
Pattern: Generate → Validate → Execute → Capture → Classify → Output

Consumes:
  - Requirements from work items / sprint intent
  - Acceptance criteria (from seeded examples)
  - User workflow definitions

Produces:
  - Generated UAT scenarios
  - Expected outcomes
  - Execution evidence
"""

import json, os
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
QA_PILOT_ROOT = os.path.dirname(PROJECT_ROOT)

# Example requirement and acceptance criteria for demonstration
EXAMPLE_REQUIREMENTS = [
    {
        "id": "REQ-001",
        "title": "Student Login",
        "description": "Student can sign in with email and password",
        "acceptance_criteria": [
            "Valid email and password grant access",
            "Invalid credentials show error message",
            "Empty fields show validation message",
        ]
    },
    {
        "id": "REQ-002",
        "title": "Course Enrollment",
        "description": "Student can browse and enroll in courses",
        "acceptance_criteria": [
            "Available courses are displayed in a catalog",
            "Enrolling in a course updates the student's course list",
            "Duplicate enrollment is prevented",
        ]
    },
    {
        "id": "REQ-003",
        "title": "Language Toggle",
        "description": "User can switch between EN and FR languages",
        "acceptance_criteria": [
            "Language toggle is visible on core pages",
            "Switching language reloads page with translated text",
            "Selected language persists across pages (localStorage)",
        ]
    },
]

def generate_scenario(requirement, criterion):
    """Generate a UAT scenario from a requirement + acceptance criterion."""
    req_id = requirement["id"]
    criterion_short = criterion.split(" ")[0].lower()
    
    return {
        "scenario_id": f"UAT-{req_id}-{criterion_short}-{datetime.now().strftime('%H%M%S')}",
        "source_requirement": req_id,
        "title": f"{requirement['title']}: {criterion}",
        "steps": [
            f"Navigate to the {requirement['title'].lower()} page",
            f"Perform action: {criterion}",
            "Observe the system response",
        ],
        "expected_outcome": criterion,
        "pass_criteria": "System responds as described in acceptance criteria",
        "fail_criteria": "System responds with error or unexpected state",
    }

def generate_uat_suite(requirements=None):
    """Generate a full UAT suite from requirements list."""
    if requirements is None:
        requirements = EXAMPLE_REQUIREMENTS
    
    suite = {
        "artifact": {
            "identity": f"UAT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "source_context": {
                "project_id": "qa-pilot",
                "source": "seeded example requirements"
            }
        },
        "intent": "UAT scenario generation from requirements and acceptance criteria",
        "classification": "uat",
        "execution_method": "guided",
        "scenarios": [],
        "evidence_output": {
            "summary": f"Generated {sum(len(r['acceptance_criteria']) for r in requirements)} scenarios from {len(requirements)} requirements",
        },
        "authority_level": "advisory"
    }
    
    for req in requirements:
        for ac in req["acceptance_criteria"]:
            scenario = generate_scenario(req, ac)
            suite["scenarios"].append(scenario)
    
    return suite

def main():
    suite = generate_uat_suite()
    print(json.dumps(suite, indent=2))
    print(f"\nPASS: {len(suite['scenarios'])} UAT scenarios generated from {len(EXAMPLE_REQUIREMENTS)} requirements")

    # Write evidence
    evidence_path = os.path.join(QA_PILOT_ROOT, "data", "uat-evidence.json")
    os.makedirs(os.path.dirname(evidence_path), exist_ok=True)
    with open(evidence_path, "w") as f:
        json.dump(suite, f, indent=2)
    print(f"\nEvidence written to: {evidence_path}")

if __name__ == "__main__":
    main()
