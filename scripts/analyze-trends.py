#!/usr/bin/env python3
"""
Assurance Trend Analysis Engine — QA-PILOT-ASSURANCE-TREND-ANALYSIS-1

Historical interpretation of assurance state.

Commands:
  trend-project <project_id>    Show trends for a project
  trend-fleet                   Show fleet-wide trends
  history                       Show trend history
  explain <trend_id>            Explain a trend
  status                        Show trend analysis status
"""

import sys
import os
import json
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

# --- Configuration ---

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "assurance"
EVIDENCE_STORE = PROJECT_ROOT / "data" / "runtime-evidence"
PROJECTS_DIR = EVIDENCE_STORE / "projects"
OBSERVATORY_DIR = DATA_DIR / "observatory-reports"
DISCOVERIES_DIR = DATA_DIR / "capability-discoveries"
TRENDS_DIR = DATA_DIR / "trend-records"
HISTORY_FILE = DATA_DIR / "trend-history.json"


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


def get_historical_observations(project_id, metric, days=30):
    """Get historical observations for a metric."""
    observations = []
    
    # Check observatory reports
    if OBSERVATORY_DIR.exists():
        for f in sorted(OBSERVATORY_DIR.glob("*.json")):
            report = load_json(f)
            if report:
                generated_at = report.get("generated_at")
                if generated_at:
                    ts = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
                    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
                    if ts >= cutoff:
                        for project in report.get("projects", []):
                            if project.get("project_id") == project_id:
                                if metric == "risk_score":
                                    observations.append({
                                        "timestamp": generated_at,
                                        "value": project.get("risk_score", 0)
                                    })
                                elif metric == "evidence_coverage":
                                    coverage = project.get("evidence_coverage", "unknown")
                                    coverage_value = {"none": 0, "minimal": 1, "partial": 2, "full": 3, "unknown": -1}.get(coverage, -1)
                                    observations.append({
                                        "timestamp": generated_at,
                                        "value": coverage_value
                                    })
                                elif metric == "capability_gaps":
                                    observations.append({
                                        "timestamp": generated_at,
                                        "value": project.get("capability_gaps", 0)
                                    })
    
    return observations


def compute_trend(observations):
    """Compute trend from observations."""
    if len(observations) < 2:
        return {
            "direction": "insufficient_data",
            "confidence": "low",
            "delta": 0,
            "delta_pct": 0,
            "previous_value": observations[0]["value"] if observations else None,
            "current_value": observations[-1]["value"] if observations else None
        }
    
    previous = observations[-2]["value"]
    current = observations[-1]["value"]
    
    delta = current - previous
    delta_pct = (delta / previous * 100) if previous != 0 else 0
    
    # Determine direction
    if abs(delta_pct) < 5:
        direction = "stable"
    elif delta < 0:
        direction = "improving" if metric_decreases_are_good(metric_from_observations(observations)) else "degrading"
    else:
        direction = "degrading" if metric_decreases_are_good(metric_from_observations(observations)) else "improving"
    
    # Determine confidence
    if len(observations) >= 3:
        confidence = "high"
    elif len(observations) >= 2:
        confidence = "medium"
    else:
        confidence = "low"
    
    return {
        "direction": direction,
        "confidence": confidence,
        "delta": delta,
        "delta_pct": round(delta_pct, 1),
        "previous_value": previous,
        "current_value": current
    }


def metric_decreases_are_good(metric):
    """Check if decreasing metric value is good."""
    # For these metrics, lower is better
    good_when_lower = ["risk_score", "capability_gaps"]
    return metric in good_when_lower


def metric_from_observations(observations):
    """Infer metric from observations (simplified)."""
    # In real system, would track metric name
    return "risk_score"


def analyze_project_trends(project_id):
    """Analyze trends for a project."""
    metrics = ["risk_score", "evidence_coverage", "capability_gaps"]
    trends = []
    
    for metric in metrics:
        observations = get_historical_observations(project_id, metric)
        trend_data = compute_trend(observations)
        
        trend = {
            "trend_id": generate_id("TR"),
            "project_id": project_id,
            "metric": metric,
            "window_start": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
            "window_end": datetime.now(timezone.utc).isoformat(),
            "previous_value": trend_data["previous_value"],
            "current_value": trend_data["current_value"],
            "direction": trend_data["direction"],
            "confidence": trend_data["confidence"],
            "delta": trend_data["delta"],
            "delta_pct": trend_data["delta_pct"],
            "evidence_refs": [],
            "advisory_only": True
        }
        
        trends.append(trend)
    
    return trends


def cmd_trend_project(args):
    """Show trends for a project."""
    if len(args) < 1:
        print("Usage: trend-project <project_id>")
        sys.exit(1)
    
    project_id = args[0]
    trends = analyze_project_trends(project_id)
    
    # Save trends
    for trend in trends:
        save_json(TRENDS_DIR / f"{trend['trend_id']}.json", trend)
    
    print(f"Assurance Trends: {project_id}")
    print("=" * 60)
    
    for trend in trends:
        print(f"\n  {trend['metric']}:")
        print(f"    Direction: {trend['direction']}")
        print(f"    Previous: {trend['previous_value']}")
        print(f"    Current: {trend['current_value']}")
        print(f"    Delta: {trend['delta']} ({trend['delta_pct']}%)")
        print(f"    Confidence: {trend['confidence']}")


def cmd_trend_fleet(args):
    """Show fleet-wide trends."""
    if not PROJECTS_DIR.exists():
        print("No projects found.")
        return
    
    print("Fleet Assurance Trends")
    print("=" * 60)
    
    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if project_dir.is_dir():
            trends = analyze_project_trends(project_dir.name)
            
            # Save trends
            for trend in trends:
                save_json(TRENDS_DIR / f"{trend['trend_id']}.json", trend)
            
            print(f"\n  {project_dir.name}:")
            for trend in trends:
                direction_icon = "↑" if trend["direction"] == "improving" else ("↓" if trend["direction"] == "degrading" else "→")
                print(f"    {trend['metric']}: {direction_icon} {trend['direction']} ({trend['confidence']})")


def cmd_history(args):
    """Show trend history."""
    if not TRENDS_DIR.exists():
        print("No trend history yet.")
        return
    
    trends = []
    for f in sorted(TRENDS_DIR.glob("*.json")):
        trends.append(load_json(f))
    
    print(f"Trend History ({len(trends)})")
    print("=" * 60)
    
    for t in trends[-10:]:  # Show last 10
        print(f"\n  [{t['direction']}] {t['trend_id']}")
        print(f"    Project: {t['project_id']}")
        print(f"    Metric: {t['metric']}")
        print(f"    {t['previous_value']} → {t['current_value']} ({t['delta_pct']}%)")


def cmd_explain(args):
    """Explain a trend."""
    if len(args) < 1:
        print("Usage: explain <trend_id>")
        sys.exit(1)
    
    trend_id = args[0]
    trend_file = TRENDS_DIR / f"{trend_id}.json"
    
    if not trend_file.exists():
        print(f"Trend not found: {trend_id}")
        return
    
    trend = load_json(trend_file)
    
    print(f"Trend Explanation: {trend_id}")
    print("=" * 60)
    print(f"  Project: {trend['project_id']}")
    print(f"  Metric: {trend['metric']}")
    print(f"  Direction: {trend['direction']}")
    print(f"  Previous: {trend['previous_value']}")
    print(f"  Current: {trend['current_value']}")
    print(f"  Delta: {trend['delta']} ({trend['delta_pct']}%)")
    print(f"  Confidence: {trend['confidence']}")
    print()
    
    # Explain what this means
    if trend["direction"] == "improving":
        print("  This metric is improving over time.")
    elif trend["direction"] == "degrading":
        print("  This metric is degrading over time.")
    elif trend["direction"] == "stable":
        print("  This metric is stable.")
    else:
        print("  Insufficient data to determine trend.")
    
    print()
    print("  This is an observation, not a recommendation.")
    print("  Owner decides what action to take.")


def cmd_status(args):
    """Show trend analysis status."""
    trends = list(TRENDS_DIR.glob("*.json")) if TRENDS_DIR.exists() else []
    
    print("Assurance Trend Analysis Status")
    print("=" * 60)
    print(f"  Trend records: {len(trends)}")


COMMANDS = {
    "trend-project": cmd_trend_project,
    "trend-fleet": cmd_trend_fleet,
    "history": cmd_history,
    "explain": cmd_explain,
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
