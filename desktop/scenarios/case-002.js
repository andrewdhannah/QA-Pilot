// Scenario registry guard — always required at top of every scenario file
window.SCENARIOS = window.SCENARIOS || {};

/**
 * case-002 — Advanced Scenario: Customer Portal Access Failure
 *
 * Three deliberate bugs hidden in the CRM case for the trainee to discover.
 * This scenario is used by the advanced capstone (capstone-2.html).
 */
window.SCENARIOS["case-002"] = {

  id:          "case-002",
  type:        "case",
  title:       "Customer Portal Access Failure",
  difficulty:  "advanced",
  description: "A business customer cannot access the self-service portal. " +
               "Three AC violations are present in the CRM case data.",

  // ── CRM state — loaded into Dynamics CRM on boot ─────────────────────────
  crmState: {
    caseId:           "CASE-00189",
    caseTitle:        "Business Portal — Login Failure After Password Reset",
    customerName:     "Raj Patel",
    company:          "Northgate Logistics Ltd.",
    priority:         "High",
    status:           "Escalated",         // BUG-A: Junior role has Status set to "Escalated"
    escalationReason: "",                  // BUG-B: Escalation Reason is blank despite status being Escalated
    assignedTo:       "Junior Investigator",
    createdDate:      "+90d",              // BUG-C: Future date relative to today
    dateOpened:       "2026-07-15",        // BUG-C: Future date
    product:          "Customer Self-Service Portal",
    summary:          "Customer reports they are unable to log in to the portal after completing " +
                      "a password reset. Reset email was received and link was clicked, but login " +
                      "page shows 'Invalid credentials' error. Issue began 2026-07-14.",
    environment:      "Production",
    version:          "Portal v4.2.1",
  },

  // ── Acceptance criteria for this scenario ────────────────────────────────
  // The trainee must reference these IDs in their ADO bug reports.
  acceptanceCriteria: [
    { id: "AC-2.1", text: "Junior Investigators cannot set case Status to Escalated or Closed." },
    { id: "AC-3.2", text: "Date Opened must not be a future date." },
    { id: "AC-4.1", text: "Escalation Reason is mandatory when Status is set to Escalated." },
  ],

  // ── Bugs the trainee must discover ───────────────────────────────────────
  expectedBugs: [
    "status-junior-escalated",
    "escalation-reason-blank",
    "future-date-allowed",
  ],

  // Mapping of Bug IDs to their corresponding Acceptance Criteria
  acRefs: {
    "status-junior-escalated":  "AC-2.1",
    "escalation-reason-blank":  "AC-4.1",
    "future-date-allowed":      "AC-3.2",
  },

  // ── Teams thread — loaded into Teams app when scenario starts ─────────────
  teamsThread: [
    {
      sender:    "Elyse Hannah",
      avatar:    "EH",
      avatarBg:  "#0078d4",
      time:      "Today at 8:47 AM",
      body:      "Morning team. New priority case in the queue — CASE-00189. " +
                 "Raj Patel from Northgate Logistics can't access the portal after a password reset. " +
                 "Priority: **High**. Can someone pick this up first thing?",
    },
    {
      sender:    "QA Bot",
      avatar:    "🤖",
      avatarBg:  "#5b5fc7",
      time:      "Today at 8:47 AM",
      isBot:     true,
      body:      "📋 Case CASE-00189 assigned to **Andrew Hannah**. Scenario loaded. Good luck!",
    },
    {
      sender:    "Sam (Senior QA)",
      avatar:    "SQ",
      avatarBg:  "#107c10",
      time:      "Today at 8:51 AM",
      body:      "Heads up — I glanced at the case before it was reassigned. " +
                 "Something looked off with the metadata. Worth checking the AC checklist carefully before you start filing. 🧐",
    },
    {
      sender:    "Elyse Hannah",
      avatar:    "EH",
      avatarBg:  "#0078d4",
      time:      "Today at 9:02 AM",
      body:      "Andrew — reminder that the AC for this product version is in the AC Panel app. " +
                 "Check each field against the acceptance criteria before concluding your review. " +
                 "Sprint review is at end of day.",
    },
  ],

  // Metadata for the Training app selector
  trainingMeta: {
    difficulty: "Advanced",
    apps:       "Dynamics + ADO + Teams",
    bugs:       3,
  },

  // Guided walkthrough steps for the Training app
  trainingSteps: [
    {
      title: "Step 1 — Read your Teams briefing",
      body:  "Open the Teams app from the desktop.\nRead the message from Elyse Hannah (QA Lead).\nA high-priority case has been assigned to you — CASE-00189.",
      hint:  "Pay attention to what Sam (Senior QA) says about the case metadata.",
    },
    {
      title: "Step 2 — Open Dynamics CRM",
      body:  "Open Dynamics CRM from the desktop.\nExamine every field in the case form carefully.\nLook at the Status, Escalation Reason, and Date Opened fields.",
      hint:  "There are 3 bugs to find. The case is already in an escalated state — is that appropriate for a Junior analyst?",
    },
    {
      title: "Step 3 — Check the Status field",
      body:  "Look at the Case Status field.\nNotice it is set to 'Escalated'.\nCheck who this case is assigned to.\nCan a Junior analyst set this status?",
      hint:  "AC-2.1: Junior Investigators cannot set case Status to Escalated or Closed.",
    },
    {
      title: "Step 4 — Check the Escalation Reason",
      body:  "With the Status set to 'Escalated', look at the Escalation Reason field.\nIs it filled in?\nWhat should happen when a case is escalated?",
      hint:  "AC-4.1: Escalation Reason is mandatory when Status is set to Escalated.",
    },
    {
      title: "Step 5 — Check the Date Opened",
      body:  "Look at the Date Opened field.\nWhat date is shown?\nCompare it to today's date.\nCan a case be opened on a date that hasn't happened yet?",
      hint:  "AC-3.2: Date Opened must not be a future date.",
    },
    {
      title: "Step 6 — File your ADO reports",
      body:  "You should have found 3 defects.\nOpen Azure DevOps and file a bug report for each one.\nFor each: clear title, correct severity, AC reference, and steps to reproduce.",
      hint:  "Bug severity mapping: Status violation → High, Blank Escalation Reason → Medium, Future Date → Medium.",
    },
    {
      title: "Step 7 — Submit and review",
      body:  "When you have filed all 3 bug reports, click Submit for Certification in the taskbar.\nYour QA Lead will review your work and give you feedback.",
      hint:  "Make sure each report has a complete set of steps to reproduce before submitting.",
    },
  ],
};
