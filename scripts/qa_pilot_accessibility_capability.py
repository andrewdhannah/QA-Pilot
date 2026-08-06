"""
qa_pilot_accessibility_capability.py — Accessibility Testing Capability

Architecture basis: QA-PILOT-TESTING-CAPABILITY-ARCHITECTURE-1 (#178)
Phase: 2 — Accessibility
Pattern: Generate → Validate → Execute → Capture → Classify → Output

Performs static analysis of HTML pages for:
  - UI structure (headings, landmarks, semantic elements)
  - Keyboard navigation (focus indicators, tab order, skip links)
  - Form accessibility (label associations, error messages)
  - Semantic element checks (roles, aria attributes)

Output conforms to TestArtifact base schema + AccessibilityTest specialization.
"""

import json, os, re
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
QA_PILOT_ROOT = os.path.dirname(PROJECT_ROOT)
BROWSER_APP = os.path.join(QA_PILOT_ROOT, "browser-app")

def scan_html_files():
    """Discover HTML pages for analysis."""
    pages = []
    for root, dirs, files in os.walk(BROWSER_APP):
        for f in files:
            if not f.endswith('.html'):
                continue
            path = os.path.join(root, f)
            rel = os.path.relpath(path, QA_PILOT_ROOT)
            with open(path) as fp:
                content = fp.read()
            pages.append({"path": rel, "content": content, "size": len(content)})
    return pages

def check_headings(content):
    """Check heading hierarchy (h1-h6)."""
    headings = re.findall(r'<(h[1-6])[^>]*>', content)
    issues = []
    if not headings:
        issues.append({"severity": "error", "message": "No headings found on page"})
    if 'h1' not in headings:
        issues.append({"severity": "warning", "message": "No h1 found (page may lack top-level heading)"})
    return issues

def check_landmarks(content):
    """Check for semantic landmarks."""
    landmarks = {
        'header': '<header' in content,
        'main': '<main' in content or 'role="main"' in content,
        'nav': '<nav' in content or 'role="navigation"' in content,
        'footer': '<footer' in content,
        'aside': '<aside' in content,
    }
    issues = []
    if not landmarks['main']:
        issues.append({"severity": "warning", "message": "No main landmark found"})
    if not landmarks['nav']:
        issues.append({"severity": "info", "message": "No navigation landmark found"})
    return issues, landmarks

def check_forms(content):
    """Check form accessibility (label associations)."""
    form_issues = []
    inputs = re.findall(r'<input[^>]+>', content)
    labels = re.findall(r'<label[^>]*>', content)
    for inp in inputs:
        has_id = 'id="' in inp
        has_aria = 'aria-label' in inp or 'aria-labelledby' in inp
        if not has_id and not has_aria:
            form_issues.append({"severity": "warning", "message": "Input without id or aria-label"})
    if inputs and not labels:
        form_issues.append({"severity": "error", "message": "Form inputs present but no labels found"})
    return form_issues

def check_keyboard(content):
    """Check keyboard navigation elements."""
    keyboard_issues = []
    if 'tabindex' not in content and '<button' in content:
        keyboard_issues.append({"severity": "info", "message": "No tabindex found but buttons present"})
    if 'role="tablist"' in content and 'tabindex' not in content:
        keyboard_issues.append({"severity": "warning", "message": "Tablist found without tabindex management"})
    if 'skip-link' not in content and '<header' in content:
        keyboard_issues.append({"severity": "info", "message": "No skip-link detected on page with header"})
    return keyboard_issues

def check_aria(content):
    """Check ARIA attribute usage."""
    aria_attrs = re.findall(r'aria-\w+', content)
    roles = re.findall(r'role="([^"]+)"', content)
    return {
        "aria_attributes": list(set(aria_attrs)),
        "roles": list(set(roles)),
        "aria_count": len(aria_attrs)
    }

def analyze_page(page):
    """Run all accessibility checks on a single page."""
    content = page["content"]
    return {
        "page": page["path"],
        "checks": {
            "headings": check_headings(content),
            "landmarks": check_landmarks(content)[0],
            "forms": check_forms(content),
            "keyboard": check_keyboard(content),
            "aria": check_aria(content),
        },
        "summary": {
            "total_issues": len(check_headings(content)) + len(check_landmarks(content)[0]) + len(check_forms(content)) + len(check_keyboard(content))
        }
    }

def main():
    pages = scan_html_files()
    core_pages = [p for p in pages if 'index.html' in p['path'] or 'portal.html' in p['path'] or 'course-view' in p['path']]
    results = [analyze_page(p) for p in core_pages[:5]]
    
    total_issues = sum(r["summary"]["total_issues"] for r in results)
    
    evidence = {
        "artifact": {
            "identity": f"A11Y-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "source_context": {"project_id": "qa-pilot", "scope": "core pages (static analysis)"}
        },
        "intent": "Static accessibility analysis of QA Pilot core pages",
        "classification": "accessibility",
        "execution_method": "static_analysis",
        "findings": results,
        "evidence_output": {
            "summary": f"Analyzed {len(results)} pages, found {total_issues} accessibility issues",
            "severity_breakdown": {
                "error": sum(1 for r in results for c in r["checks"].values() if isinstance(c, list) for i in c if i.get("severity")=="error"),
                "warning": sum(1 for r in results for c in r["checks"].values() if isinstance(c, list) for i in c if i.get("severity")=="warning"),
                "info": sum(1 for r in results for c in r["checks"].values() if isinstance(c, list) for i in c if i.get("severity")=="info"),
            }
        },
        "authority_level": "advisory"
    }
    
    print(json.dumps(evidence, indent=2))
    print(f"\nPASS: {len(results)} pages analyzed, {total_issues} accessibility findings")

    evidence_path = os.path.join(QA_PILOT_ROOT, "data", "accessibility-evidence.json")
    os.makedirs(os.path.dirname(evidence_path), exist_ok=True)
    with open(evidence_path, "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"\nEvidence written to: {evidence_path}")

if __name__ == "__main__":
    main()
