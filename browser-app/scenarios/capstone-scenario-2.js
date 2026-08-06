/**
 * =============================================================================
 * capstone-scenario-2.js — Capstone 2 Scenario Data
 * =============================================================================
 * QA Pilot Advanced Capstone
 *
 * PURPOSE:
 * Central data file for the Advanced Capstone (Capstone 2) exercise.
 * Defines the full Sprint 14 scenario: characters, bugs, user stories,
 * stages with scripted messages, and the scoring rubric.
 * Every Capstone 2 app (Teams, ADO, Dynamics, QOutlook) reads from this object.
 *
 * HOW TO USE THIS FILE:
 * Load this file as a <script> tag before any app or the OS engine.
 * It declares a single global: SCENARIO_C2 — access it as window.SCENARIO_C2
 * or just SCENARIO_C2 from any script loaded after this one.
 *
 * WHAT'S IN HERE:
 * - Section 1: meta — scenario identity and metadata
 * - Section 2: characters — simulated teammates with avatar info
 * - Section 3: bugs — intentional defects seeded in the scenario
 * - Section 4: userStories — AC-linked stories on the ADO sprint board
 * - Section 5: stages — 6-stage progression with scripted messages
 * - Section 6: scoring — point values and pass threshold
 *
 * READS FROM:   Nothing — this is pure data
 * WRITES TO:    window.SCENARIO_C2
 *
 * =============================================================================
 */

// ── SCENARIO_C2 — ROOT SCENARIO OBJECT ─────────────────────────────────────────

var SCENARIO_C2 = {

  // ── SECTION 1: META ─────────────────────────────────────────────────────────
  // Basic scenario identity. Read by the OS engine to label the capstone
  // and load the correct scenario when capstone-2.html boots.
  meta: {
    id:          'capstone-2',
    title:       'Sprint 14 — Customer Portal v2.1 Validation',
    company:     'Northgate Logistics',
    team:        'Scrum Team Delta — Customer Experience Squad',
    sprint:      'Sprint 14',
    sprintGoal:  'Validate the new Customer Portal v2.1 release before production',
    traineeRole: 'Junior QA Analyst',
    passingScore: 80,
    totalPoints:  130,
  },

  // ── SECTION 2: CHARACTERS ───────────────────────────────────────────────────
  // Simulated teammates. Avatar colours match the --team-avatar-* CSS
  // variables already defined in teams.html. Used by Teams, QOutlook.
  characters: {
    sarah: {
      id:          'sarah',
      name:        'Sarah Chen',
      role:        'QA Lead / Scrum Master',
      initials:    'SC',
      avatarColor: 'blue',       // maps to --team-avatar-blue in teams.html
      primaryApp:  'teams',
    },
    marcus: {
      id:          'marcus',
      name:        'Marcus Webb',
      role:        'Product Owner',
      initials:    'MW',
      avatarColor: 'orange',
      primaryApp:  'teams',
    },
    jamie: {
      id:          'jamie',
      name:        'Jamie Torres',
      role:        'Developer',
      initials:    'JT',
      avatarColor: 'green',
      primaryApp:  'teams',
    },
    priya: {
      id:          'priya',
      name:        'Priya Patel',
      role:        'Senior QA Analyst',
      initials:    'PP',
      avatarColor: 'purple',
      primaryApp:  'teams',
    },
  },

  // ── SECTION 3: BUGS ─────────────────────────────────────────────────────────
  // Intentional defects seeded by the Bug Lab. Each maps to a bug in
  // the OS scenario configuration. The panel value tells dynamics.html
  // which test panel to show the bug in. storyId links to a user story.
  bugs: {
    'BUG-C2-01': {
      id:          'BUG-C2-01',
      title:       'Login email field accepts invalid format',
      location:    'Customer Portal — Login',
      description: 'Email field accepts invalid format (e.g. "user@" passes validation)',
      severity:    'High',
      difficulty:  'Easy',
      panel:       'login',           // dynamics.html panel id
      storyId:     'US-C2-001',       // the user story this bug belongs to
      acRef:       'AC-C2-001-3',     // the AC clause it violates
    },
    'BUG-C2-02': {
      id:          'BUG-C2-02',
      title:       'Password reset link expires in 2 minutes instead of 24 hours',
      location:    'Customer Portal — Password Reset',
      description: 'Reset link expires in 2 minutes instead of 24 hours',
      severity:    'Medium',
      difficulty:  'Medium',
      panel:       'password-reset',
      storyId:     'US-C2-002',
      acRef:       'AC-C2-002-2',
    },
    'BUG-C2-03': {
      id:          'BUG-C2-03',
      title:       'Customer name truncates at 30 characters without ellipsis',
      location:    'Dynamics CRM — Case View',
      description: 'Customer name truncates at 30 characters with no ellipsis or tooltip',
      severity:    'Low',
      difficulty:  'Hard',
      panel:       'case-detail',
      storyId:     'US-C2-003',
      acRef:       'AC-C2-003-1',
    },
  },

  // ── SECTION 4: USER STORIES ─────────────────────────────────────────────────
  // Pre-loaded into the ADO sprint board. AC is shown in story detail.
  // assignee is always the trainee — shown as "You" in the UI.
  userStories: [
    {
      id:         'US-C2-001',
      title:      'Customer can log in to the portal with a valid email address',
      status:     'Active',
      assignee:   'trainee',
      linkedBugs: ['BUG-C2-01'],
      ac: [
        'AC-C2-001-1: Login form accepts email addresses matching RFC 5322 format.',
        'AC-C2-001-2: Login form rejects empty email field with inline error message.',
        'AC-C2-001-3: Login form rejects malformed email addresses (e.g. missing domain, missing @) with inline error message.',
        'AC-C2-001-4: Successful login redirects user to the portal dashboard within 3 seconds.',
      ],
    },
    {
      id:         'US-C2-002',
      title:      'Customer can reset their password via email link',
      status:     'Active',
      assignee:   'trainee',
      linkedBugs: ['BUG-C2-02'],
      ac: [
        'AC-C2-002-1: "Forgot Password" link is visible on the login page.',
        'AC-C2-002-2: Password reset link sent to the registered email address expires after 24 hours.',
        'AC-C2-002-3: Expired link shows a clear error message with instructions to request a new one.',
        'AC-C2-002-4: Successful password reset redirects to login page with a success message.',
      ],
    },
    {
      id:         'US-C2-003',
      title:      'CRM case view displays full customer name without truncation',
      status:     'Active',
      assignee:   'trainee',
      linkedBugs: ['BUG-C2-03'],
      ac: [
        'AC-C2-003-1: Customer name displays in full regardless of character length.',
        'AC-C2-003-2: If name must be truncated due to layout constraints, an ellipsis (…) is shown.',
        'AC-C2-003-3: Hovering over a truncated name shows the full name in a tooltip.',
      ],
    },
  ],

  // ── SECTION 5: STAGES ───────────────────────────────────────────────────────
  // The sprint is divided into 6 sequential stages. The orchestration
  // engine in os-core.js advances stages by checking unlockConditions.
  // Messages are delivered to the correct app when the stage activates.
  stages: [
    {
      id:              'stage-1',
      name:            'Sprint Kickoff',
      unlockCondition: 'CAPSTONE_2_LOADED',  // fires automatically on boot
      messages: [
        {
          app:       'qoutlook',
          channel:   'inbox',
          from:      'sarah',
          subject:   'Sprint 14 Kickoff — Your Testing Assignment',
          time:      '8:30 AM',
          body:      'Hi,\n\nWelcome to your first sprint with Team Delta! Sprint 14 kicks off today.\n\nSprint Goal: Validate Customer Portal v2.1 before it goes to production.\n\nYour assignment is waiting for you in the #sprint-14-delta channel in Teams. Head there to see your specific testing tasks, then check the ADO sprint board to review the user stories and acceptance criteria.\n\nIf you run into anything unclear, ping me or Priya in Teams.\n\nGood luck!\nSarah Chen\nQA Lead, Scrum Team Delta',
        },
        {
          app:            'teams',
          channel:        'sprint-14-delta',
          from:           'sarah',
          body:           'Hey team! Sprint 14 is live. 👋\n\nFor our new team member — your testing tasks are below. You\'ve got three user stories assigned to you in ADO. Review the acceptance criteria for each one before you start testing.\n\nThe staging build is ready. Jamie deployed it this morning.\n\nClick **Acknowledge** below when you\'ve read this and are ready to start.',
          hasAcknowledge: true,  // Sprint C renders a button for this
        },
      ],
    },
    {
      id:              'stage-2',
      name:            'Review Sprint Board',
      unlockCondition: 'STAGE_1_ACKNOWLEDGED',
      messages: [
        {
          app:     'teams',
          channel: 'sprint-14-delta',
          from:    'jamie',
          body:    'Hey, I just deployed the latest build to staging. Let me know if anything looks off.',
        },
      ],
    },
    {
      id:              'stage-3',
      name:            'Day 1 Testing',
      unlockCondition: 'ALL_STORIES_REVIEWED',
      messages: [],    // No new messages — trainee goes to Dynamics and tests
    },
    {
      id:              'stage-4',
      name:            'Standup Update',
      unlockCondition: 'BUG_FILED_MINIMUM_ONE',
      messages: [
        {
          app:              'teams',
          channel:          'standup',
          from:             'sarah',
          body:             'Reminder: async standup update due by EOD. Drop your update in the thread. 👇',
          isStandupPrompt:  true,  // Sprint C renders the standup input form after this
        },
      ],
    },
    {
      id:              'stage-5',
      name:            'Day 2 Testing',
      unlockCondition: 'STANDUP_POSTED',
      messages: [
        {
          app:     'teams',
          channel: 'standup',
          from:    'marcus',
          body:    'Good progress. The login bug is a blocker for go-live if it\'s real. Make sure the repro is solid.',
          condition: null,  // always shown
        },
        {
          app:       'teams',
          channel:   'standup',
          from:      'priya',
          body:      'Nice find. Did you check the password reset flow against the AC? That one\'s worth a look.',
          condition: 'BUG_C2_02_NOT_FILED',  // Only shown if BUG-C2-02 has NOT been filed
        },
        {
          app:     'teams',
          channel: 'sprint-14-delta',
          from:    'sarah',
          body:    'Sprint review is tomorrow. Start wrapping up your testing and get your bugs documented.',
        },
        {
          app:       'teams',
          channel:   'sprint-14-delta',
          from:      'jamie',
          body:      'I\'ve been looking at the login validation — can you share your repro steps? I want to check if it\'s the same issue I fixed last sprint.',
          condition: 'BUG_C2_01_FILED',  // Only shown if BUG-C2-01 was filed
        },
      ],
    },
    {
      id:              'stage-6',
      name:            'Sprint Review',
      unlockCondition: 'BUG_FILED_MINIMUM_TWO',
      messages: [
        {
          app:     'qoutlook',
          channel: 'inbox',
          from:    'sarah',
          subject: 'Sprint 14 Review — You\'re Invited',
          time:    '8:00 AM',
          body:    'Hi,\n\nThe Sprint 14 Review is today. Please prepare a brief summary of your QA findings to share with the team.\n\nHead to the #sprint-review channel in Teams when you\'re ready. Your filed bugs will be summarised there automatically.\n\nThanks!\nSarah',
        },
        {
          app:              'teams',
          channel:          'sprint-review',
          from:             'sarah',
          body:             'Sprint 14 Review is now open. Team, please add your summaries below. QA — your bugs are summarised in this thread. Add your overall QA verdict when ready.',
          isReviewThread:   true,  // Sprint C renders the QA summary input here
        },
      ],
    },
  ],

  // ── SECTION 6: SCORING ───────────────────────────────────────────────────────
  // Sprint G reads this object to score the trainee's work.
  // Points are per-bug unless noted otherwise.
  scoring: {
    bugFound:             20,    // per bug found (max 3 bugs x 20 = 60 pts)
    titleDescriptive:      5,    // per bug: title is not blank/generic
    severityCorrect:       5,    // per bug: severity matches expected value
    reproStepsComplete:   10,    // per bug: repro steps filled (minimum 2)
    expectedActualFilled:  5,    // per bug: both expected and actual result present
    standupCompleted:     10,    // flat bonus for posting standup update
    sprintReviewSubmitted: 10,   // flat bonus for submitting sprint review summary
    passingThreshold:     80,    // minimum score to pass
    totalPossible:        130,
  },

  // ── SECTION 7: TRAINING — Guided practice for the capstone ───────────────────
  // Optional section for the Training app. If present, the training app will
  // load this scenario as a practice exercise before the live assessment.
  trainingMeta: {
    title: "Advanced Capstone 2 — Sprint 14 Preparation",
    difficulty: "Intermediate",
    description:
      "Practice the Sprint 14 scenario in a guided environment. Review the user stories, acceptance criteria, and bugs before attempting the graded capstone.",
    estimatedMins: 15,
  },

  trainingSteps: [
    {
      title: "Step 1 of 6 — Understand the Assignment",
      body: "Open the Capstone Brief. You've been assigned to validate the Customer Portal v2.1 release for Sprint 14. Your role is Junior QA Analyst on Scrum Team Delta. The goal is to ensure the portal meets all acceptance criteria before production deployment.",
    },
    {
      title: "Step 2 of 6 — Review the User Stories",
      body: "Open Azure DevOps (ADO). You have three user stories assigned:\n\n- US-C2-001: Login functionality\n- US-C2-002: Password reset flow\n- US-C2-003: CRM case view display\n\nReview each story's acceptance criteria carefully. These define what 'done' means for each feature.",
    },
    {
      title: "Step 3 of 6 — Identify the Bugs",
      body: "Open the Bug Lab or ADO to see the seeded bugs. There are three intentional defects:\n\n- BUG-C2-01: Login email validation issue\n- BUG-C2-02: Password reset link expiration\n- BUG-C2-03: Customer name truncation\n\nEach bug links to a specific user story and acceptance criterion.",
    },
    {
      title: "Step 4 of 6 — Explore the Dynamics CRM",
      body: "Open Dynamics CRM. Navigate to the Case View and inspect the customer name display. Check if long names are truncated. Also verify that the case status and date fields are populated correctly.",
    },
    {
      title: "Step 5 of 6 — Practice Filing a Bug",
      body: "Open Azure DevOps and create a test bug. Fill in the required fields: Title, Steps to Reproduce, Expected Result, Actual Result, and link it to the appropriate user story and acceptance criterion. This will prepare you for the actual assessment.",
    },
    {
      title: "Step 6 of 6 — Training Complete",
      body: "You've completed the guided training for Capstone 2. You should now be familiar with the scenario layout, the bugs to find, and the tools you'll use. When you're ready, return to the Academy and start the live graded capstone.",
    },
  ],

};  // end SCENARIO_C2
