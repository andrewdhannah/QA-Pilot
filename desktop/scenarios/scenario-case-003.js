/**
 * =============================================================================
 * scenarios-case-003.js — Scenario Data: Invoice Processing Failure
 * =============================================================================
 * QA Onboarding Training Platform
 *
 * PURPOSE:
 * Defines the data for Case-003, an expert-level scenario. This scenario
 * requires the trainee to cross-reference a Teams briefing, the AC Panel,
 * and Dynamics CRM to identify 4 specific data defects.
 *
 * HOW TO USE THIS FILE:
 * This file is automatically bundled by build.js. The OS engine accesses
 * this data via window.SCENARIOS["case-003"].
 *
 * READS FROM:   N/A (Static Data)
 * WRITES TO:    window.SCENARIOS
 *
 * =============================================================================
 */

window.SCENARIOS = window.SCENARIOS || {};

window.SCENARIOS["case-003"] = {
  id: "case-003",
  title: "CASE-00247 — Invoice Processing Failure",
  company: "Northgate Logistics",
  role: "junior",

  // The bugs the user must identify and log in ADO to pass
  expectedBugs: [
    "status-junior-closed",
    "priority-mismatch",
    "future-date-allowed",
    "owner-unassigned"
  ],

  // Mapping of Bug IDs to their corresponding Acceptance Criteria
  acRefs: {
    "status-junior-closed": "AC-2.1",
    "priority-mismatch": "AC-3.2",
    "future-date-allowed": "AC-1.3",
    "owner-unassigned": "AC-1.1"
  },

  // Brief shown in the OS overlay when starting the scenario
  brief: "The QA Lead has assigned you CASE-00247 via Teams.\n\nA finance team member has raised a high-priority support ticket:\n'Invoice #INV-8821 for £42,000 cannot be processed — the portal is returning a permission error.'\n\nThe case has been logged in Dynamics CRM. Your job is to examine the case data and identify all defects before the finance team escalates to the vendor.",

  // Teams message content for the Teams app
  teamsThread: [
    {
      sender: "Sarah Chen (QA Lead)",
      text: "Hi,\n\nPlease pick up CASE-00247 — Invoice Processing Failure at Northgate.\n\nFinance have flagged this as urgent. The invoice value is £42,000 and the portal is throwing permission errors.\n\nI've pre-loaded the case in Dynamics. Have a look and file ADO reports for anything you find wrong with the case data before we escalate.\n\nKey ACs to check: AC-1.1, AC-1.3, AC-2.1, AC-3.2.\n\nLet me know when you've submitted.\n\n— Sarah",
      timestamp: "10:15 AM"
    }
  ],

  // Initial field values for the Dynamics CRM app
  crmState: {
    caseId:            "CASE-00247",
    caseTitle:         "Invoice Processing Failure",
    status:            "Closed",         // Bug: Junior can't close cases (AC-2.1)
    priority:          "Low",            // Bug: should be Critical for £42k financial case (AC-3.2)
    createdDate:       "+3d",             // Bug: 3 days in the future (AC-1.3)
    owner:             "",               // Bug: blank owner not permitted (AC-1.1)
    description:       "Finance team reports invoice INV-8821 (£42,000) cannot be processed due to a portal permission error. High-priority — finance team has escalated.",
    escalationReason:  "",
    category:          "Financial Processing",
    channel:           "Internal — Finance",
  },

  // Control which bugs are actually present (all true = all 4 are present)
  bugToggles: {
    "status-junior-closed": true,
    "priority-mismatch": true,
    "future-date-allowed": true,
    "owner-unassigned": true
  },

  // Metadata for the Training app selector
  trainingMeta: {
    difficulty: "Expert",
    apps:       "Dynamics + ADO + Teams",
    bugs:       4,
  },

  // Guided walkthrough steps for the Training app
  trainingSteps: [
    {
      title: "Step 1 — Read your Teams briefing",
      body:  "Open the Teams app from the desktop.\nRead the message from Sarah Chen (QA Lead).\nNote the AC references she has flagged: AC-1.1, AC-1.3, AC-2.1, AC-3.2.",
      hint:  "Sarah has given you exactly the ACs to check. Open the AC Panel alongside Dynamics to reference them.",
    },
    {
      title: "Step 2 — Open the AC Panel",
      body:  "Open the Acceptance Criteria app from the desktop.\nFind the rules for AC-1.1, AC-1.3, AC-2.1, and AC-3.2.\nKeep this open as you work through the case.",
      hint:  "Having both the AC Panel and Dynamics open at the same time (using snap layout) is the most efficient approach.",
    },
    {
      title: "Step 3 — Examine the Case Owner field",
      body:  "Open Dynamics CRM from the desktop.\nLook at the Case Owner field.\nIs it filled in?",
      hint:  "AC-1.1: All cases must have a named Case Owner on creation. A blank owner is a defect.",
    },
    {
      title: "Step 4 — Check the Case Status",
      body:  "Look at the Case Status field in Dynamics.\nWhat is the current value?\nIs this permitted for a Junior analyst?",
      hint:  "AC-2.1: Junior analysts may not set Status to Closed or Escalated.",
    },
    {
      title: "Step 5 — Check the Priority",
      body:  "Read the case description carefully.\nNote the invoice value and how the finance team described the urgency.\nNow look at the Priority field — does it match?",
      hint:  "AC-3.2: Cases with financial impact of £10,000+ must be Priority: Critical. The description says £42,000.",
    },
    {
      title: "Step 6 — Check the Created Date",
      body:  "Look at the Created Date field in Dynamics.\nCompare it to today's date.\nCan a case be created in the future?",
      hint:  "AC-1.3: Created Date must not be in the future. This is the same bug type as in Case 001.",
    },
    {
      title: "Step 7 — File your ADO reports",
      body:  "You should have found 4 defects.\nOpen Azure DevOps and file a separate bug report for each one.\nFor each report: clear title, correct severity, AC reference, and steps to reproduce.",
      hint:  "Bug priority/severity mapping: Blank Owner → High, Closed Status → High, Wrong Priority → Medium, Future Date → Medium.",
    },
  ],
};
