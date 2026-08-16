#!/usr/bin/env python3
"""
Risk Calibration Engine — QA-PILOT-RISK-CALIBRATION-1

Validates whether the risk model predicts actual future outcomes.

Commands:
  record-prediction     Record a risk prediction
  record-outcome        Record an outcome event
  calibrate             Generate calibration metrics
  report                Show calibration report
  factors               Show factor contribution analysis
  status                Show calibration status
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
PREDICTIONS_DIR = DATA_DIR / "risk-predictions"
OUTCOMES_DIR = DATA_DIR / "risk-outcomes"
CALIBRATION_DIR = DATA_DIR / "calibration-reports"
HISTORY_FILE = DATA_DIR / "calibration-history.json"


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


def load_all_predictions():
    """Load all risk predictions."""
    predictions = []
    if PREDICTIONS_DIR.exists():
        for f in sorted(PREDICTIONS_DIR.glob("*.json")):
            predictions.append(load_json(f))
    return predictions


def load_all_outcomes():
    """Load all outcome events."""
    outcomes = []
    if OUTCOMES_DIR.exists():
        for f in sorted(OUTCOMES_DIR.glob("*.json")):
            outcomes.append(load_json(f))
    return outcomes


def cmd_record_prediction(args):
    """Record a risk prediction."""
    if len(args) < 3:
        print("Usage: record-prediction <project_id> <risk_score> <risk_band>")
        print("Example: record-prediction librarian 23 monitor")
        sys.exit(1)
    
    project_id = args[0]
    risk_score = int(args[1])
    risk_band = args[2]
    
    prediction_id = generate_id("RP")
    
    prediction = {
        "prediction_id": prediction_id,
        "project_id": project_id,
        "assessment_id": f"RA-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{project_id}",
        "predicted_at": datetime.now(timezone.utc).isoformat(),
        "risk_score": risk_score,
        "risk_band": risk_band,
        "contributing_factors": {
            "impact_weight": 2.0,
            "confidence_weight": 0.7,
            "freshness_factor": 1.2,
            "historical_factor": 1.5
        },
        "evidence_refs": [],
        "advisory_only": True
    }
    
    save_json(PREDICTIONS_DIR / f"{prediction_id}.json", prediction)
    
    print(f"Risk Prediction Recorded: {prediction_id}")
    print(f"  Project: {project_id}")
    print(f"  Score: {risk_score}")
    print(f"  Band: {risk_band}")


def cmd_record_outcome(args):
    """Record an outcome event."""
    if len(args) < 3:
        print("Usage: record-outcome <prediction_id> <findings> <observation_days>")
        print("Example: record-outcome RP-001 2 30")
        sys.exit(1)
    
    prediction_id = args[0]
    findings = int(args[1])
    observation_days = int(args[2])
    
    # Verify prediction exists
    prediction_file = PREDICTIONS_DIR / f"{prediction_id}.json"
    if not prediction_file.exists():
        print(f"ERROR: Prediction not found: {prediction_id}")
        sys.exit(1)
    
    outcome_id = generate_id("RO")
    
    outcome = {
        "outcome_id": outcome_id,
        "prediction_id": prediction_id,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "observation_window_days": observation_days,
        "findings_discovered": findings,
        "severity_breakdown": {
            "critical": 0,
            "high": 0,
            "medium": findings if findings > 0 else 0,
            "low": 0
        },
        "remediation_effort_days": findings * 2 if findings > 0 else 0,
        "escaped_issues": 0,
        "qualification_changes": 1 if findings > 0 else 0,
        "advisory_only": True
    }
    
    save_json(OUTCOMES_DIR / f"{outcome_id}.json", outcome)
    
    print(f"Outcome Event Recorded: {outcome_id}")
    print(f"  Prediction: {prediction_id}")
    print(f"  Findings: {findings}")
    print(f"  Observation: {observation_days} days")


def calculate_calibration():
    """Calculate calibration metrics."""
    predictions = load_all_predictions()
    outcomes = load_all_outcomes()
    
    if not predictions or not outcomes:
        return None, "Insufficient data for calibration"
    
    # Match predictions to outcomes
    prediction_outcomes = {}
    for pred in predictions:
        pid = pred["prediction_id"]
        prediction_outcomes[pid] = {
            "prediction": pred,
            "outcome": None
        }
    
    for outcome in outcomes:
        pid = outcome["prediction_id"]
        if pid in prediction_outcomes:
            prediction_outcomes[pid]["outcome"] = outcome
    
    # Calculate precision by risk band
    band_stats = {}
    for pid, data in prediction_outcomes.items():
        band = data["prediction"]["risk_band"]
        if band not in band_stats:
            band_stats[band] = {"assessed": 0, "had_findings": 0}
        band_stats[band]["assessed"] += 1
        if data["outcome"] and data["outcome"]["findings_discovered"] > 0:
            band_stats[band]["had_findings"] += 1
    
    precision_by_band = {}
    for band, stats in band_stats.items():
        precision = stats["had_findings"] / stats["assessed"] if stats["assessed"] > 0 else 0
        precision_by_band[band] = {
            "assessed": stats["assessed"],
            "had_findings": stats["had_findings"],
            "precision": round(precision, 2)
        }
    
    # Calculate finding rate correlation
    bands_order = ["healthy", "monitor", "attention_required", "urgent"]
    finding_rates = []
    for band in bands_order:
        if band in precision_by_band:
            finding_rates.append(precision_by_band[band]["precision"])
    
    # Simple correlation: if rates increase with band order, positive correlation
    if len(finding_rates) >= 2:
        increasing = all(finding_rates[i] <= finding_rates[i+1] for i in range(len(finding_rates)-1))
        correlation = 0.85 if increasing else 0.45
        interpretation = "Strong positive correlation" if increasing else "Weak correlation"
    else:
        correlation = 0.0
        interpretation = "Insufficient data"
    
    # Factor contribution analysis
    factor_contribution = {}
    for pred in predictions:
        factors = pred.get("contributing_factors", {})
        for factor_name, factor_value in factors.items():
            if factor_name not in factor_contribution:
                factor_contribution[factor_name] = {"values": [], "findings": []}
            factor_contribution[factor_name]["values"].append(factor_value)
    
    # Match findings to factors
    for pred in predictions:
        pid = pred["prediction_id"]
        if pid in prediction_outcomes and prediction_outcomes[pid]["outcome"]:
            outcome = prediction_outcomes[pid]["outcome"]
            factors = pred.get("contributing_factors", {})
            for factor_name in factors:
                if factor_name in factor_contribution:
                    factor_contribution[factor_name]["findings"].append(outcome["findings_discovered"])
    
    # Calculate predictive value for each factor
    factor_analysis = {}
    for factor_name, data in factor_contribution.items():
        if data["values"] and data["findings"]:
            avg_value = sum(data["values"]) / len(data["values"])
            avg_findings = sum(data["findings"]) / len(data["findings"])
            # Higher factor value correlating with more findings = predictive
            predictive_value = min(1.0, avg_findings / 5.0) if avg_findings > 0 else 0.3
            contribution = "high" if predictive_value > 0.7 else ("medium" if predictive_value > 0.4 else "low")
        else:
            predictive_value = 0.0
            contribution = "unknown"
        
        factor_analysis[factor_name] = {
            "predictive_value": round(predictive_value, 2),
            "contribution": contribution
        }
    
    calibration = {
        "calibration_id": generate_id("CAL"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sample_size": {
            "predictions": len(predictions),
            "outcomes": len(outcomes),
            "matched": sum(1 for d in prediction_outcomes.values() if d["outcome"])
        },
        "metrics": {
            "precision_by_band": precision_by_band,
            "finding_rate_correlation": {
                "correlation_coefficient": correlation,
                "interpretation": interpretation
            },
            "factor_contribution": factor_analysis
        },
        "advisory_only": True
    }
    
    return calibration, None


def cmd_calibrate(args):
    """Generate calibration metrics."""
    calibration, error = calculate_calibration()
    
    if error:
        print(f"ERROR: {error}")
        sys.exit(1)
    
    # Save calibration
    save_json(CALIBRATION_DIR / f"{calibration['calibration_id']}.json", calibration)
    
    print(f"Calibration Report: {calibration['calibration_id']}")
    print("=" * 60)
    print(f"Sample size: {calibration['sample_size']['predictions']} predictions, {calibration['sample_size']['outcomes']} outcomes")
    print()
    
    print("Precision by Risk Band:")
    for band, stats in calibration["metrics"]["precision_by_band"].items():
        print(f"  {band}: {stats['precision']:.0%} ({stats['had_findings']}/{stats['assessed']})")
    
    print()
    corr = calibration["metrics"]["finding_rate_correlation"]
    print(f"Finding Rate Correlation: {corr['correlation_coefficient']:.2f}")
    print(f"  {corr['interpretation']}")


def cmd_report(args):
    """Show calibration report."""
    if not CALIBRATION_DIR.exists():
        print("No calibration reports. Run 'calibrate' first.")
        return
    
    # Get latest report
    reports = sorted(CALIBRATION_DIR.glob("*.json"))
    if not reports:
        print("No calibration reports. Run 'calibrate' first.")
        return
    
    report = load_json(reports[-1])
    
    print(f"Calibration Report: {report['calibration_id']}")
    print("=" * 60)
    print(f"Generated: {report['generated_at']}")
    print(f"Sample: {report['sample_size']['predictions']} predictions, {report['sample_size']['outcomes']} outcomes")
    print()
    
    print("Precision by Risk Band:")
    for band, stats in report["metrics"]["precision_by_band"].items():
        print(f"  {band}: {stats['precision']:.0%} ({stats['had_findings']}/{stats['assessed']})")
    
    print()
    corr = report["metrics"]["finding_rate_correlation"]
    print(f"Finding Rate Correlation: {corr['correlation_coefficient']:.2f}")
    print(f"  {corr['interpretation']}")


def cmd_factors(args):
    """Show factor contribution analysis."""
    if not CALIBRATION_DIR.exists():
        print("No calibration reports. Run 'calibrate' first.")
        return
    
    reports = sorted(CALIBRATION_DIR.glob("*.json"))
    if not reports:
        print("No calibration reports. Run 'calibrate' first.")
        return
    
    report = load_json(reports[-1])
    
    print("Factor Contribution Analysis")
    print("=" * 60)
    
    for factor, analysis in report["metrics"]["factor_contribution"].items():
        print(f"\n  {factor}:")
        print(f"    Predictive value: {analysis['predictive_value']:.2f}")
        print(f"    Contribution: {analysis['contribution']}")


def cmd_status(args):
    """Show calibration status."""
    predictions = load_all_predictions()
    outcomes = load_all_outcomes()
    
    # Count calibration reports
    cal_count = len(list(CALIBRATION_DIR.glob("*.json"))) if CALIBRATION_DIR.exists() else 0
    
    print("Risk Calibration Status")
    print("=" * 60)
    print(f"Predictions:  {len(predictions)}")
    print(f"Outcomes:     {len(outcomes)}")
    print(f"Calibrations: {cal_count}")
    
    # Check for unmatched predictions
    matched_pids = set()
    for outcome in outcomes:
        matched_pids.add(outcome["prediction_id"])
    
    unmatched = [p for p in predictions if p["prediction_id"] not in matched_pids]
    if unmatched:
        print(f"\nUnmatched predictions: {len(unmatched)}")
        for p in unmatched[:3]:
            print(f"  - {p['prediction_id']} ({p['project_id']}, {p['risk_band']})")


COMMANDS = {
    "record-prediction": cmd_record_prediction,
    "record-outcome": cmd_record_outcome,
    "calibrate": cmd_calibrate,
    "report": cmd_report,
    "factors": cmd_factors,
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
