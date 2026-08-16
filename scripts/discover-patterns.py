#!/usr/bin/env python3
"""
Historical Pattern Discovery Engine — QA-PILOT-HISTORICAL-PATTERN-MODELING-1

Identifies repeatable relationships in assurance history.

Commands:
  discover-patterns       Discover patterns from historical data
  list-patterns           List discovered patterns
  explain-pattern <id>    Explain a specific pattern
  validate-pattern <id>   Validate pattern against current data
  status                  Show pattern discovery status
"""

import sys
import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# --- Configuration ---

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "assurance"
EVIDENCE_STORE = PROJECT_ROOT / "data" / "runtime-evidence"
PATTERNS_DIR = DATA_DIR / "historical-patterns"
DISCOVERIES_DIR = DATA_DIR / "capability-discoveries"
INTENTS_DIR = DATA_DIR / "planning-intents"
OUTCOMES_DIR = DATA_DIR / "execution-outcomes"


def load_json(path):
    """Load a JSON file."""
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    """Save data to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def generate_id(prefix):
    """Generate a unique ID with prefix."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    h = hashlib.sha256(f"{prefix}{ts}".encode()).hexdigest()[:8]
    return f"{prefix}-{ts}-{h}"


def compute_confidence(sample_size, contradictions=0):
    """Compute confidence level."""
    if sample_size < 3:
        return "insufficient"
    
    if sample_size >= 10:
        level = "high"
    elif sample_size >= 5:
        level = "medium"
    else:
        level = "low"
    
    # Apply contradiction penalty
    if contradictions > 0:
        levels = ["high", "medium", "low", "insufficient"]
        idx = levels.index(level)
        level = levels[min(idx + 1, len(levels) - 1)]
    
    return level


def discover_evidence_patterns():
    """Discover evidence-related patterns."""
    patterns = []
    
    # Pattern: Stale evidence → qualification findings
    # Check qualification history for findings
    qual_file = EVIDENCE_STORE / "qualification-history.json"
    if qual_file.exists():
        qual = load_json(qual_file)
        finding_runs = [r for r in qual.get("runs", []) if r.get("result", {}).get("disposition") == "FINDING"]
        
        if len(finding_runs) > 0:
            patterns.append({
                "pattern_id": generate_id("PAT"),
                "pattern_name": "Evidence Finding Association",
                "pattern_category": "evidence",
                "observations": ["qualification_finding_detected"],
                "historical_outcome": "qualification_finding",
                "sample_size": len(finding_runs),
                "positive_cases": len(finding_runs),
                "confidence": compute_confidence(len(finding_runs)),
                "observation_window": "all_history",
                "contradictions": 0,
                "evidence_refs": [],
                "explanation": f"Observed {len(finding_runs)} qualification findings in history. Projects with findings tend to have evidence quality issues.",
                "advisory_only": True
            })
    
    # Pattern: Capability gaps → coverage issues
    if DISCOVERIES_DIR.exists():
        discoveries = []
        for f in DISCOVERIES_DIR.glob("*.json"):
            disc = load_json(f)
            if disc:
                discoveries.append(disc)
        
        findings_count = sum(d.get("summary", {}).get("total_findings", 0) for d in discoveries)
        
        if findings_count > 0:
            patterns.append({
                "pattern_id": generate_id("PAT"),
                "pattern_name": "Capability Gap Pattern",
                "pattern_category": "capability",
                "observations": ["capability_gaps_detected"],
                "historical_outcome": "coverage_gap",
                "sample_size": len(discoveries),
                "positive_cases": sum(1 for d in discoveries if d.get("summary", {}).get("total_findings", 0) > 0),
                "confidence": compute_confidence(len(discoveries)),
                "observation_window": "all_history",
                "contradictions": 0,
                "evidence_refs": [],
                "explanation": f"Observed {len(discoveries)} capability discoveries with {findings_count} total findings. Capability gaps tend to persist without attention.",
                "advisory_only": True
            })
    
    return patterns


def discover_planning_patterns():
    """Discover planning-related patterns."""
    patterns = []
    
    # Pattern: Planning variance → estimation issues
    if INTENTS_DIR.exists() and OUTCOMES_DIR.exists():
        intents = [load_json(f) for f in INTENTS_DIR.glob("*.json")]
        outcomes = [load_json(f) for f in OUTCOMES_DIR.glob("*.json")]
        
        if len(outcomes) > 0:
            # Compute variance
            variances = []
            for outcome in outcomes:
                intent_id = outcome.get("intent_id")
                intent = next((i for i in intents if i.get("intent_id") == intent_id), None)
                if intent:
                    estimated = intent.get("estimates", {}).get("effort_days", 0)
                    actual = outcome.get("actual", {}).get("effort_days", 0)
                    if estimated > 0:
                        variance = abs(actual - estimated) / estimated * 100
                        variances.append(variance)
            
            if variances:
                avg_variance = sum(variances) / len(variances)
                patterns.append({
                    "pattern_id": generate_id("PAT"),
                    "pattern_name": "Planning Variance Pattern",
                    "pattern_category": "planning",
                    "observations": ["planning_variance_detected"],
                    "historical_outcome": "estimation_adjustment_needed",
                    "sample_size": len(variances),
                    "positive_cases": sum(1 for v in variances if v > 50),
                    "confidence": compute_confidence(len(variances)),
                    "observation_window": "all_history",
                    "contradictions": 0,
                    "evidence_refs": [],
                    "explanation": f"Observed {len(variances)} planning records with average variance {avg_variance:.0f}%. Projects with high variance may benefit from estimation review.",
                    "advisory_only": True
                })
    
    return patterns


def discover_patterns():
    """Discover all patterns from historical data."""
    patterns = []
    patterns.extend(discover_evidence_patterns())
    patterns.extend(discover_planning_patterns())
    
    return patterns


def cmd_discover_patterns(args):
    """Discover patterns from historical data."""
    patterns = discover_patterns()
    
    # Save patterns
    for pattern in patterns:
        save_json(PATTERNS_DIR / f"{pattern['pattern_id']}.json", pattern)
    
    print(f"Pattern Discovery")
    print("=" * 60)
    print(f"  Patterns found: {len(patterns)}")
    print()
    
    for pattern in patterns:
        print(f"  {pattern['pattern_id']}: {pattern['pattern_name']}")
        print(f"    Category: {pattern['pattern_category']}")
        print(f"    Sample: {pattern['sample_size']}")
        print(f"    Confidence: {pattern['confidence']}")
        print(f"    {pattern['explanation'][:80]}...")
        print()


def cmd_list_patterns(args):
    """List discovered patterns."""
    if not PATTERNS_DIR.exists():
        print("No patterns discovered yet.")
        return
    
    patterns = []
    for f in sorted(PATTERNS_DIR.glob("*.json")):
        patterns.append(load_json(f))
    
    print(f"Discovered Patterns ({len(patterns)})")
    print("=" * 60)
    
    for p in patterns:
        print(f"\n  [{p['confidence'].upper()}] {p['pattern_id']}")
        print(f"    {p['pattern_name']}")
        print(f"    Category: {p['pattern_category']}")
        print(f"    Sample: {p['sample_size']}, Positive: {p['positive_cases']}")


def cmd_explain_pattern(args):
    """Explain a specific pattern."""
    if len(args) < 1:
        print("Usage: explain-pattern <pattern_id>")
        sys.exit(1)
    
    pattern_id = args[0]
    pattern_file = PATTERNS_DIR / f"{pattern_id}.json"
    
    if not pattern_file.exists():
        print(f"Pattern not found: {pattern_id}")
        return
    
    pattern = load_json(pattern_file)
    
    print(f"Pattern Explanation: {pattern_id}")
    print("=" * 60)
    print(f"  Name: {pattern['pattern_name']}")
    print(f"  Category: {pattern['pattern_category']}")
    print(f"  Confidence: {pattern['confidence']}")
    print()
    print("  Observations:")
    for obs in pattern["observations"]:
        print(f"    - {obs}")
    print()
    print(f"  Historical Outcome: {pattern['historical_outcome']}")
    print(f"  Sample Size: {pattern['sample_size']}")
    print(f"  Positive Cases: {pattern['positive_cases']}")
    print()
    print("  Explanation:")
    print(f"    {pattern['explanation']}")
    print()
    print("  This is an observed pattern, not a prediction.")
    print("  Association does not imply causation.")


def cmd_validate_pattern(args):
    """Validate pattern against current data."""
    if len(args) < 1:
        print("Usage: validate-pattern <pattern_id>")
        sys.exit(1)
    
    pattern_id = args[0]
    pattern_file = PATTERNS_DIR / f"{pattern_id}.json"
    
    if not pattern_file.exists():
        print(f"Pattern not found: {pattern_id}")
        return
    
    pattern = load_json(pattern_file)
    
    # Validate minimum sample
    valid = pattern["sample_size"] >= 3
    
    print(f"Pattern Validation: {pattern_id}")
    print("=" * 60)
    print(f"  Minimum sample: {'PASS' if valid else 'FAIL'} ({pattern['sample_size']})")
    print(f"  Confidence: {pattern['confidence']}")
    print(f"  Valid: {'Yes' if valid else 'No (insufficient data)'}")


def cmd_status(args):
    """Show pattern discovery status."""
    patterns = list(PATTERNS_DIR.glob("*.json")) if PATTERNS_DIR.exists() else []
    
    print("Historical Pattern Discovery Status")
    print("=" * 60)
    print(f"  Patterns: {len(patterns)}")


COMMANDS = {
    "discover-patterns": cmd_discover_patterns,
    "list-patterns": cmd_list_patterns,
    "explain-pattern": cmd_explain_pattern,
    "validate-pattern": cmd_validate_pattern,
    "status": cmd_status,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        print(f"Commands: {', '.join(COMMANDS.keys())}")
        sys.exit(0)
    
    cmd = sys.argv[1]
    args = sys.argv[2:]
    COMMANDS[cmd](args)


if __name__ == "__main__":
    main()
