#!/usr/bin/env python3
"""
Predictive Readiness Assessment — QA-PILOT-ASSURANCE-PREDICTIVE-READINESS-1

Validates substrate readiness for predictive assurance.

Commands:
  assess               Full readiness assessment
  data-quality         Verify historical data quality
  signals              Measure signal availability
  features             Identify predictive features
  status               Show readiness status
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
PROJECTS_DIR = EVIDENCE_STORE / "projects"
READINESS_DIR = DATA_DIR / "predictive-readiness"


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


def assess_data_quality():
    """Assess historical data quality."""
    checks = []
    
    # Check qualification history
    qual_file = EVIDENCE_STORE / "qualification-history.json"
    if qual_file.exists():
        qual = load_json(qual_file)
        checks.append({
            "data_source": "qualification_history",
            "available": True,
            "complete": qual.get("total_runs", 0) > 0,
            "record_count": qual.get("total_runs", 0),
            "quality": "good" if qual.get("total_runs", 0) > 0 else "insufficient"
        })
    else:
        checks.append({
            "data_source": "qualification_history",
            "available": False,
            "complete": False,
            "record_count": 0,
            "quality": "missing"
        })
    
    # Check risk assessments
    risk_file = EVIDENCE_STORE / "risk-assessments.json"
    if risk_file.exists():
        risk = load_json(risk_file)
        checks.append({
            "data_source": "risk_assessments",
            "available": True,
            "complete": len(risk.get("projects", [])) > 0,
            "record_count": len(risk.get("projects", [])),
            "quality": "good" if len(risk.get("projects", [])) > 0 else "insufficient"
        })
    else:
        checks.append({
            "data_source": "risk_assessments",
            "available": False,
            "complete": False,
            "record_count": 0,
            "quality": "missing"
        })
    
    # Check planning accuracy
    intents_dir = DATA_DIR / "planning-intents"
    outcomes_dir = DATA_DIR / "execution-outcomes"
    intents_count = len(list(intents_dir.glob("*.json"))) if intents_dir.exists() else 0
    outcomes_count = len(list(outcomes_dir.glob("*.json"))) if outcomes_dir.exists() else 0
    
    checks.append({
        "data_source": "planning_accuracy",
        "available": intents_count > 0,
        "complete": outcomes_count > 0,
        "record_count": intents_count + outcomes_count,
        "quality": "good" if outcomes_count > 0 else ("partial" if intents_count > 0 else "insufficient")
    })
    
    # Check capability discoveries
    discoveries_dir = DATA_DIR / "capability-discoveries"
    discoveries_count = len(list(discoveries_dir.glob("*.json"))) if discoveries_dir.exists() else 0
    
    checks.append({
        "data_source": "capability_discoveries",
        "available": discoveries_count > 0,
        "complete": discoveries_count > 0,
        "record_count": discoveries_count,
        "quality": "good" if discoveries_count > 0 else "insufficient"
    })
    
    # Check economics reports
    economics_dir = DATA_DIR / "economics-reports"
    economics_count = len(list(economics_dir.glob("*.json"))) if economics_dir.exists() else 0
    
    checks.append({
        "data_source": "economics_reports",
        "available": economics_count > 0,
        "complete": economics_count > 0,
        "record_count": economics_count,
        "quality": "good" if economics_count > 0 else "insufficient"
    })
    
    # Check trend records
    trends_dir = DATA_DIR / "trend-records"
    trends_count = len(list(trends_dir.glob("*.json"))) if trends_dir.exists() else 0
    
    checks.append({
        "data_source": "trend_records",
        "available": trends_count > 0,
        "complete": trends_count >= 3,  # Need multiple for trends
        "record_count": trends_count,
        "quality": "good" if trends_count >= 3 else ("partial" if trends_count > 0 else "insufficient")
    })
    
    # Compute overall quality
    quality_scores = {"good": 1.0, "partial": 0.5, "insufficient": 0.2, "missing": 0.0}
    avg_quality = sum(quality_scores.get(c["quality"], 0) for c in checks) / len(checks)
    
    return {
        "checks": checks,
        "overall_quality": round(avg_quality, 2),
        "data_sources_available": sum(1 for c in checks if c["available"]),
        "data_sources_complete": sum(1 for c in checks if c["complete"]),
        "total_records": sum(c["record_count"] for c in checks)
    }


def measure_signal_availability():
    """Measure predictive signal availability."""
    signals = []
    
    # Risk signals
    risk_file = EVIDENCE_STORE / "risk-assessments.json"
    signals.append({
        "signal": "risk_score_changes",
        "available": risk_file.exists(),
        "predictive_value": "high",
        "source": "risk_engine"
    })
    
    # Qualification signals
    qual_file = EVIDENCE_STORE / "qualification-history.json"
    signals.append({
        "signal": "qualification_findings",
        "available": qual_file.exists(),
        "predictive_value": "high",
        "source": "qualification_engine"
    })
    
    # Planning variance signals
    variances_dir = DATA_DIR / "variance-analyses"
    signals.append({
        "signal": "planning_variance",
        "available": variances_dir.exists() and len(list(variances_dir.glob("*.json"))) > 0,
        "predictive_value": "medium",
        "source": "planning_accuracy"
    })
    
    # Capability gap signals
    discoveries_dir = DATA_DIR / "capability-discoveries"
    signals.append({
        "signal": "capability_gaps",
        "available": discoveries_dir.exists() and len(list(discoveries_dir.glob("*.json"))) > 0,
        "predictive_value": "medium",
        "source": "capability_discovery"
    })
    
    # Evidence freshness signals
    discovery_file = EVIDENCE_STORE / "discovery-projection.json"
    signals.append({
        "signal": "evidence_freshness",
        "available": discovery_file.exists(),
        "predictive_value": "medium",
        "source": "fleet_freshness"
    })
    
    # Change frequency signals
    signals.append({
        "signal": "change_frequency",
        "available": True,  # Can compute from evidence count
        "predictive_value": "low-medium",
        "source": "evidence_store"
    })
    
    available_count = sum(1 for s in signals if s["available"])
    
    return {
        "signals": signals,
        "total_signals": len(signals),
        "available_signals": available_count,
        "availability_ratio": round(available_count / len(signals), 2)
    }


def identify_predictive_features():
    """Identify predictive features."""
    features = [
        {
            "feature": "rapid_capability_growth",
            "description": "Project adding capabilities quickly",
            "source": "onboarding_history",
            "prediction_target": "future_evidence_gaps",
            "current_availability": "partial"
        },
        {
            "feature": "low_evidence_coverage",
            "description": "Insufficient evidence for declared capabilities",
            "source": "fleet_freshness",
            "prediction_target": "future_qualification_findings",
            "current_availability": "available"
        },
        {
            "feature": "high_change_frequency",
            "description": "Frequent changes in evidence or capabilities",
            "source": "evidence_store",
            "prediction_target": "future_risk_increases",
            "current_availability": "available"
        },
        {
            "feature": "planning_variance",
            "description": "Estimates significantly different from actuals",
            "source": "planning_accuracy",
            "prediction_target": "future_effort_overruns",
            "current_availability": "available"
        },
        {
            "feature": "historical_findings",
            "description": "Previous findings in similar context",
            "source": "qualification_history",
            "prediction_target": "future_findings",
            "current_availability": "available"
        }
    ]
    
    available_count = sum(1 for f in features if f["current_availability"] == "available")
    
    return {
        "features": features,
        "total_features": len(features),
        "available_features": available_count,
        "feature_coverage": round(available_count / len(features), 2)
    }


def cmd_assess(args):
    """Full readiness assessment."""
    data_quality = assess_data_quality()
    signals = measure_signal_availability()
    features = identify_predictive_features()
    
    # Compute overall readiness
    readiness_score = (
        data_quality["overall_quality"] * 0.4 +
        signals["availability_ratio"] * 0.3 +
        features["feature_coverage"] * 0.3
    )
    
    readiness_level = "not_ready"
    if readiness_score >= 0.8:
        readiness_level = "ready"
    elif readiness_score >= 0.6:
        readiness_level = "mostly_ready"
    elif readiness_score >= 0.4:
        readiness_level = "partially_ready"
    
    assessment = {
        "assessment_id": generate_id("PRA"),
        "assessed_at": datetime.now(timezone.utc).isoformat(),
        "readiness_score": round(readiness_score, 2),
        "readiness_level": readiness_level,
        "data_quality": data_quality,
        "signal_availability": signals,
        "predictive_features": features,
        "recommendations": [],
        "advisory_only": True
    }
    
    # Generate recommendations
    if data_quality["overall_quality"] < 0.7:
        assessment["recommendations"].append("Improve historical data quality before prediction")
    if signals["availability_ratio"] < 0.7:
        assessment["recommendations"].append("Increase signal availability")
    if features["feature_coverage"] < 0.7:
        assessment["recommendations"].append("Expand predictive feature set")
    
    # Save assessment
    save_json(READINESS_DIR / f"{assessment['assessment_id']}.json", assessment)
    
    print(f"Predictive Readiness Assessment: {assessment['assessment_id']}")
    print("=" * 60)
    print(f"  Readiness Score: {assessment['readiness_score']:.0%}")
    print(f"  Readiness Level: {assessment['readiness_level']}")
    print()
    print("  Data Quality:")
    print(f"    Sources available: {data_quality['data_sources_available']}/{len(data_quality['checks'])}")
    print(f"    Sources complete: {data_quality['data_sources_complete']}/{len(data_quality['checks'])}")
    print(f"    Total records: {data_quality['total_records']}")
    print(f"    Quality score: {data_quality['overall_quality']:.0%}")
    print()
    print("  Signal Availability:")
    print(f"    Available: {signals['available_signals']}/{signals['total_signals']}")
    print(f"    Ratio: {signals['availability_ratio']:.0%}")
    print()
    print("  Predictive Features:")
    print(f"    Available: {features['available_features']}/{features['total_features']}")
    print(f"    Coverage: {features['feature_coverage']:.0%}")
    print()
    if assessment["recommendations"]:
        print("  Recommendations:")
        for r in assessment["recommendations"]:
            print(f"    - {r}")
    print()
    print("  This is a readiness assessment, not a prediction.")
    print("  Actual prediction requires Phase 6.")


def cmd_data_quality(args):
    """Verify historical data quality."""
    data_quality = assess_data_quality()
    
    print("Data Quality Assessment")
    print("=" * 60)
    
    for check in data_quality["checks"]:
        status = "✓" if check["quality"] == "good" else ("~" if check["quality"] == "partial" else "✗")
        print(f"  [{status}] {check['data_source']}")
        print(f"      Records: {check['record_count']}, Quality: {check['quality']}")
    
    print(f"\nOverall quality: {data_quality['overall_quality']:.0%}")


def cmd_signals(args):
    """Measure signal availability."""
    signals = measure_signal_availability()
    
    print("Signal Availability")
    print("=" * 60)
    
    for signal in signals["signals"]:
        status = "✓" if signal["available"] else "✗"
        print(f"  [{status}] {signal['signal']}")
        print(f"      Value: {signal['predictive_value']}, Source: {signal['source']}")
    
    print(f"\nAvailable: {signals['available_signals']}/{signals['total_signals']}")


def cmd_features(args):
    """Identify predictive features."""
    features = identify_predictive_features()
    
    print("Predictive Features")
    print("=" * 60)
    
    for feature in features["features"]:
        status = "✓" if feature["current_availability"] == "available" else "~"
        print(f"  [{status}] {feature['feature']}")
        print(f"      Target: {feature['prediction_target']}")
    
    print(f"\nAvailable: {features['available_features']}/{features['total_features']}")


def cmd_status(args):
    """Show readiness status."""
    assessments = list(READINESS_DIR.glob("*.json")) if READINESS_DIR.exists() else []
    
    print("Predictive Readiness Status")
    print("=" * 60)
    print(f"  Assessments: {len(assessments)}")


COMMANDS = {
    "assess": cmd_assess,
    "data-quality": cmd_data_quality,
    "signals": cmd_signals,
    "features": cmd_features,
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
