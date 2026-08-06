// Scenario registry guard — always required at top of every scenario file
window.SCENARIOS = window.SCENARIOS || {};

/**
 * case-001 — Entry Scenario: Customer Unable to Complete Online Payment
 *
 * Two deliberate bugs hidden in the CRM case for the trainee to discover.
 * This is the introductory scenario used by QA Onboarding Training.
 */
window.SCENARIOS["case-001"] = {
  id:          "case-001",
  type:        "case",
  title:       "Customer unable to complete online payment",
  difficulty:  "beginner",
  description: "A customer reports that payment fails at the final confirmation step. " +
               "Two AC violations are present in the CRM case data.",

  // ── CRM state — loaded into Dynamics CRM on boot ─────────────────────────
  crmState: {
    caseId:           "CASE-00042",
    caseTitle:        "Online Payment — Transaction Fails at Confirmation",
    customerName:     "Maria Santos",
    company:          "Westfield Retail Corp.",
    priority:         "Low",                   // BUG-A: Payment-blocking issue should be High
    status:           "Resolved",              // BUG-B: Status is Resolved but resolution is blank
    escalationReason: "",
    assignedTo:       "Junior Investigator",
    createdDate:      "-2d",
    dateOpened:       "2026-05-24",
    product:          "Online Payment Gateway",
    summary:          "Customer reports multiple failed payment attempts during checkout. " +
                      "Error message: 'Transaction could not be processed. Please try again.' " +
                      "Customer has confirmed sufficient funds. Issue reproducible across " +
                      "Chrome, Firefox, and Safari browsers.",
    environment:      "Production",
    version:          "Payment Gateway v3.1.2",
  },

  // ── Acceptance criteria for this scenario ────────────────────────────────
  // The trainee must reference these IDs in their ADO bug reports.
  acceptanceCriteria: [
    { id: "AC-1.1", text: "Payment-blocking issues must be prioritized as High or Critical." },
    { id: "AC-2.1", text: "Resolved cases must include a resolution description." },
  ],

  // ── Bugs the trainee must discover ───────────────────────────────────────
  expectedBugs: [
    "priority-too-low",
    "resolved-without-resolution",
  ],

  // Mapping of Bug IDs to their corresponding Acceptance Criteria
  acRefs: {
    "priority-too-low":           "AC-1.1",
    "resolved-without-resolution": "AC-2.1",
  },

  // ── QOutlook emails — scenario-relevant messages for the QOutlook inbox ───
  qoutlookEmails: [
    {
      id: 'em-case001-1',
      sender: 'Elyse Hannah',
      from: 'Elyse Hannah <elyse.hannah@qapilot.com>',
      subject: 'RE: Westfield Retail — payment issue',
      to: 'You <trainee@qapilot.com>',
      date: 'Today, 9:15 AM',
      folder: 'inbox',
      unread: true,
      body: "Hi there,\n\nCan you take a look at this Westfield ticket (CASE-00042)? Maria Santos is reporting that her online payments are failing at the final step — she's tried multiple cards and browsers. This has been flagged as urgent by the account manager.\n\nI've assigned it to you. Check the case details in Dynamics and let me know what you find. There's a couple of things that don't look right in the case record.\n\nElyse",
      attachments: false,
    },
    {
      id: 'em-case001-2',
      sender: 'D365 Case Management',
      from: 'D365 Case Management <system@d365.qapilot.com>',
      subject: 'Case #CASE-00042 assigned — Online Payment Failure',
      to: 'You <trainee@qapilot.com>',
      date: 'Today, 9:10 AM',
      folder: 'inbox',
      unread: true,
      body: "Case CASE-00042 has been assigned to you.\n\nCustomer: Maria Santos, Westfield Retail Corp.\nSeverity: D - Low\nTitle: Online Payment — Transaction Fails at Confirmation\n\nPlease investigate and update the case record with your findings.\n\nView in Dynamics CRM: os://app/dynamics",
      attachments: false,
    },
  ],

  // ── Teams thread — loaded into Teams app when scenario starts ─────────────
  teamsThread: [
    {
      sender:    "Elyse Hannah",
      avatar:    "EH",
      avatarBg:  "#0078d4",
      time:      "Today at 9:18 AM",
      body:      "Morning team. Quick one — CASE-00042 just came in. " +
                 "Westfield Retail is seeing payment failures in production. " +
                 "Can someone review the case details and make sure everything is in order?",
    },
    {
      sender:    "Sam (Senior QA)",
      avatar:    "SQ",
      avatarBg:  "#107c10",
      time:      "Today at 9:22 AM",
      body:      "I had a quick look at that case earlier. Something seems off with the metadata. " +
                 "Worth running through the AC checklist before filing anything.",
    },
    {
      sender:    "Elyse Hannah",
      avatar:    "EH",
      avatarBg:  "#0078d4",
      time:      "Today at 9:25 AM",
      body:      "Maria's our contact — she's the IT director at Westfield. " +
                 "She's escalated this to the account manager, so let's treat it with appropriate urgency. " +
                 "Check the acceptance criteria in the AC Panel before concluding your review.",
    },
  ],

  // Metadata for the Training app selector
  trainingMeta: {
    difficulty: "Beginner",
    apps:       "Dynamics + ADO",
    bugs:       2,
  },

  // Guided walkthrough steps for the Training app
  trainingSteps: [
    {
      title: "Step 1 — Read your email briefing",
      body:  "Open the QOutlook app from the desktop.\nRead the email from Elyse Hannah (QA Lead).\nA new case has been assigned to you — CASE-00042.",
      hint:  "Pay attention to what Elyse says about urgency.",
    },
    {
      title: "Step 2 — Open Dynamics CRM",
      body:  "Open Dynamics CRM from the desktop.\nExamine every field in the case form carefully.\nLook at the Priority, Status, and Resolution fields.",
      hint:  "There are 2 bugs to find. Start with the Priority field.",
    },
    {
      title: "Step 3 — Check the Priority field",
      body:  "Look at the Case Priority field.\nWhat is it set to?\nIs this appropriate for a payment-blocking production issue?",
      hint:  "AC-1.1: Payment-blocking issues must be prioritized as High or Critical.",
    },
    {
      title: "Step 4 — Check the Resolution notes",
      body:  "Look at the Case Status — it's set to 'Resolved'.\nNow check the Resolution field.\nIs there any description of what was done to resolve it?",
      hint:  "AC-2.1: Resolved cases must include a resolution description.",
    },
    {
      title: "Step 5 — File your ADO reports",
      body:  "You should have found 2 defects.\nOpen Azure DevOps and file a bug report for each one.\nFor each: clear title, correct severity, AC reference, and steps to reproduce.",
      hint:  "Bug severity mapping: Wrong Priority → Medium, Missing Resolution → Medium.",
    },
    {
      title: "Step 6 — Submit and review",
      body:  "When you have filed both bug reports, click Submit for Certification in the taskbar.\nYour work will be reviewed by the system.",
      hint:  "Double-check each report has an AC reference before submitting.",
    },
  ],
};
