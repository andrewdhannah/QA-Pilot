/**
 * =============================================================================
 * scoring.js — Capstone Assessment Scoring Engine
 * =============================================================================
 * QA Onboarding Training Platform — Modular OS v4
 *
 * PURPOSE:
 * Evaluates the student's performance in the capstone assessment.
 * Called by os-core.js when the student clicks "Submit for Certification".
 *
 * HOW TO USE:
 * The OS shell calls:
 *   var result = window.evaluateSubmission(scenarioId, bugsFound, bugsLogged);
 * where:
 *   scenarioId  {string}  — e.g. 'capstone-001'
 *   bugsFound   {Array}   — bugIds the student triggered in Dynamics (from BUG_FOUND messages)
 *   bugsLogged  {Array}   — objects from BUG_LOGGED messages: { title, severity, acRef, hasSteps }
 *
 * RETURNS: { score, maxScore, percentage, passed, missedBugs, badReports, summary }
 *
 * READS FROM:  window.SCENARIOS
 * WRITES TO:   nothing (pure function — caller handles persistence)
 * =============================================================================
 */


// ── SECTION 1: MAIN EVALUATION FUNCTION ───────────────────────────────────────

function evalPassed(scenario, percentage) {
  var mode = (scenario && scenario.passMode) || "audit";
  if (mode === "audit") return true;
  if (mode === "pass-fail") return percentage > 0;
  return percentage >= ((scenario && scenario.passingScore) || 80);
}

window.evaluateSubmission = function(scenarioId, bugsFound, bugsLogged) {

  var scenario = window.SCENARIOS && window.SCENARIOS[scenarioId];
  if (!scenario) {
    return { score: 0, maxScore: 0, percentage: 0, passed: false,
             missedBugs: [], badReports: [], summary: 'Scenario not found.' };
  }

  var expected    = scenario.expectedBugs || [];
  var acRefs      = scenario.acRefs       || {};
  var maxScore    = expected.length * 3;
  var score       = 0;
  var missedBugs  = [];
  var badReports  = [];

  // ── 1 point for each expected bug found in Dynamics ─────────────────────────
  expected.forEach(function(bugId) {
    var wasFound = bugsFound.indexOf(bugId) !== -1;
    if (wasFound) score += 1;
    else missedBugs.push(bugId);
  });

  // ── 1 point for complete ADO report + 1 point for correct AC ref ───────────
  bugsLogged.forEach(function(report) {

    var isComplete = report.title    && report.title.trim()    !== '' &&
                     report.severity && report.severity.trim() !== '' &&
                     report.acRef    && report.acRef.trim()    !== '' &&
                     report.hasSteps === true;

    if (isComplete) {
      score += 1;

      var refMatchesExpected = false;
      expected.forEach(function(bugId) {
        if (acRefs[bugId] &&
            acRefs[bugId].toLowerCase() === report.acRef.trim().toLowerCase()) {
          refMatchesExpected = true;
        }
      });

      if (refMatchesExpected) score += 1;

    } else {
      badReports.push(report.title || '(untitled)');
    }
  });

  var percentage = maxScore > 0 ? Math.round((score / maxScore) * 100) : 0;
  var passed     = evalPassed(scenario, percentage);

  var summary = buildSummary(score, maxScore, percentage, missedBugs, badReports);

  return {
    score:      score,
    maxScore:   maxScore,
    percentage: percentage,
    passed:     passed,
    missedBugs: missedBugs,
    badReports: badReports,
    summary:    summary
  };
};


// ── SECTION 2: SUMMARY BUILDER ────────────────────────────────────────────────

function buildSummary(score, maxScore, percentage, missedBugs, badReports) {
  var lines = [];

  lines.push('Score: ' + score + ' / ' + maxScore + ' (' + percentage + '%)');
  lines.push('');

  if (missedBugs.length === 0) {
    lines.push('✓ All defects found in the CRM.');
  } else {
    lines.push('✗ Defects not found: ' + missedBugs.join(', '));
  }

  if (badReports.length === 0 && score > 0) {
    lines.push('✓ All ADO reports were complete.');
  } else if (badReports.length > 0) {
    lines.push('✗ Incomplete ADO reports: ' + badReports.join(', '));
  }

  return lines.join('\n');
}
