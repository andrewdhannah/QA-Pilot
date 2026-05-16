// Scenario registry guard — always required at top of every scenario file
window.SCENARIOS = window.SCENARIOS || {};

/**
 * capstone-001 — The Capstone Assessment Scenario
 *
 * This scenario defines:
 *   - brief:        Text shown to the student at the start of the capstone
 *   - crmState:     Pre-populated field values for the Dynamics mock
 *   - expectedBugs: Array of bug IDs the student is expected to find and report
 *   - acRefs:       Map of bugId → correct AC Reference string
 */
window.SCENARIOS['capstone-001'] = {

  id: 'capstone-001',
  type: 'capstone',
  title: 'Payment Processing — Live Investigation',

  // ── Teams narrative thread ─────────────────────────────────────────────
  // Rendered in the Teams app when this scenario loads. Each entry in the
  // array is a thread: a channel context + an array of messages.
  // Message types: 'system' (centered italic), 'chat' (default bubble),
  // 'review' (Sprint Review bubble).
  teamsThread: [
    {
      channel: 'qa-team',
      messages: [
        { author: 'system',  text: 'Case #0047 has been assigned to the QA team.',                        timestamp: '09:00 AM' },
        { author: 'Pete (QA Lead)', text: 'Team, priority case from Contoso — payment failures in prod. Triage by EOD.', timestamp: '09:02 AM' },
        { author: 'Sarah (PO)',     text: 'This is blocking the release. Need clear bug reports with AC references.',    timestamp: '09:03 AM' },
        { author: 'Alex (Junior)',  text: 'I\'ll start investigating in Dynamics.',                                     timestamp: '09:05 AM' },
      ]
    },
    {
      channel: 'qa-team',
      messages: [
        { author: 'Pete (QA Lead)', text: 'Daily stand-up — what are you working on today?',               timestamp: '09:30 AM' },
      ]
    }
  ],

  brief: [
    'You are a Junior QA Investigator on the Payments team.',
    'A batch of customer complaints has come in about failed transactions.',
    'A case has been opened in Dynamics 365 and assigned to your queue.',
    '',
    'Your task:',
    '1. Open the Dynamics CRM case and investigate the issue.',
    '2. Review the Acceptance Criteria document to understand what correct behaviour looks like.',
    '3. Identify any defects — places where the system does not match the AC.',
    '4. File a bug report in Azure DevOps for each defect you find.',
    '',
    'When you are finished, click "Submit for Certification" in the taskbar.',
    '',
    'Good luck.'
  ].join('\n'),

  crmState: {
    caseTitle:     'Customer unable to complete online payment',
    customerName:  'Maria Chen',
    caseId:        'CASE-00142',
    priority:      'Medium',
    status:        'Active',
    summary:       'Customer reports payment fails at the final confirmation step. Issue is intermittent but reproducible.',
    product:       'Online Payments Portal',
    assignedTo:    'Junior Investigator'
  },

  expectedBugs: [
    'status-junior-close',
    'future-date-allowed'
  ],

  acRefs: {
    'status-junior-close': 'AC-2.1',
    'future-date-allowed': 'AC-3.2'
  }

};
