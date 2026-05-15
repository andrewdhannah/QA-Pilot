/**
 * =============================================================================
 * quiz-questions.js — All Quiz Questions, Answers & Explanations
 * =============================================================================
 * QA Onboarding Training Platform
 *
 * PURPOSE:
 * Central repository for all lesson assessments. Organized by lesson ID.
 * Each question contains the correct answer and a detailed explanation to
 * provide immediate educational feedback.
 *
 * HOW TO USE:
 * Use getQuestionsForLesson(lessonId) to retrieve the bank for a specific page.
 * 
 * READS FROM:   N/A (Static Data)
 * WRITES TO:    N/A (Static Data)
 * =============================================================================
 */

// ── SECTION 1: DATA SCHEMA ────────────────────────────────────────────────────

/*
QUESTION SCHEMA:
{
  questionId:     string  — Unique identifier (e.g., "l2-q1").
  type:           string  — 'true-false' | 'multiple-choice' | 'scenario'
  questionText:   string  — The question as displayed to the student.
  options:        Array   — Set of possible answers.
  correctAnswer:  string  — Must exactly match one string in the options array.
  explanation:    string  — The "Why". Shown after the student answers.
  lessonContext:  string  — Optional scenario text shown above the question.
}
*/

// ── SECTION 2: QUESTIONS BY LESSON ───────────────────────────────────────────

const QUIZ_QUESTIONS = {

  // ---------------------------------------------------------------------------
  // LESSON 1 — Testing 101
  // ---------------------------------------------------------------------------
  'lesson-1': [
    {
      questionId:   'l1-q1',
      type:         'true-false',
      questionText: 'A test case must always include expected results.',
      options:      ['True', 'False'],
      correctAnswer: 'True',
      explanation:  'Expected results define what "correct" looks like. Without them, a tester cannot objectively verify a pass or fail.',
      lessonContext: '',
    },
    {
      questionId:   'l1-q2',
      type:         'true-false',
      questionText: 'A bug report is complete once you describe what went wrong.',
      options:      ['True', 'False'],
      correctAnswer: 'False',
      explanation:  'A complete report requires repro steps, expected results (AC reference), actual results, and environment details.',
      lessonContext: '',
    },
    {
      questionId:   'l1-q3',
      type:         'true-false',
      questionText: 'Testing only happens at the end of a project, after development is complete.',
      options:      ['True', 'False'],
      correctAnswer: 'False',
      explanation:  'In Agile, testing is continuous. QA is involved from the start of the sprint to identify risks early.',
      lessonContext: '',
    },
    {
      questionId:   'l1-q4',
      type:         'true-false',
      questionText: 'A tester\'s goal is to find as many bugs as possible.',
      options:      ['True', 'False'],
      correctAnswer: 'False',
      explanation:  'The goal is to provide an honest signal of quality and verify the product meets the agreed acceptance criteria.',
      lessonContext: '',
    },
    {
      questionId:   'l1-q5',
      type:         'true-false',
      questionText: 'Given / When / Then format is used in acceptance criteria to describe testable system behaviour.',
      options:      ['True', 'False'],
      correctAnswer: 'True',
      explanation:  'This format ensures the precondition, action, and outcome are explicitly defined, making it directly testable.',
      lessonContext: '',
    },
  ],

  // ---------------------------------------------------------------------------
  // LESSON 2 — Acceptance Criteria (NEW)
  // ---------------------------------------------------------------------------
  'lesson-2': [
    {
      questionId:   'l2-q1',
      type:         'multiple-choice',
      questionText: 'In Given/When/Then format, what does the "Given" clause represent?',
      options: [
        'The action the user takes',
        'The expected outcome after the action',
        'The precondition — the state the system must be in before the test begins',
        'The bug that was found during testing',
      ],
      correctAnswer: 'The precondition — the state the system must be in before the test begins',
      explanation: '"Given" establishes your starting conditions. Without a defined starting state, two testers running the same steps might get different results.',
      lessonContext: '',
    },
    {
      questionId:   'l2-q2',
      type:         'multiple-choice',
      questionText: 'You are testing a feature and find behaviour that is not covered by any Acceptance Criterion. What should you do?',
      options: [
        'File a bug — if it looks wrong, it probably is',
        'Ignore it — if it is not in the AC, it is not your concern',
        'Flag the gap to the product owner with a specific question, and do not file a bug without an AC reference',
        'Ask a developer what the intended behaviour should be, then test against that',
      ],
      correctAnswer: 'Flag the gap to the product owner with a specific question, and do not file a bug without an AC reference',
      explanation: 'A bug is a deviation from a defined expectation. If there is no AC, there is no defined expectation. You must first get the gap documented.',
      lessonContext: '',
    },
    {
      questionId:   'l2-q3',
      type:         'multiple-choice',
      questionText: 'An AC states: "The Case Title field is required. Maximum 120 characters." What is the minimum number of test cases this single AC generates?',
      options: [
        'One — test that a valid title saves successfully',
        'Two — test valid input and empty input',
        'Three or more — happy path, empty field rejection, and boundary values',
        'It depends on the developer\'s implementation',
      ],
      correctAnswer: 'Three or more — happy path, empty field rejection, and boundary values',
      explanation: 'One AC covers multiple scenarios: the happy path (valid), the unhappy path (empty), and boundary tests (exactly 120 and 121 characters).',
      lessonContext: '',
    },
    {
      questionId:   'l2-q4',
      type:         'multiple-choice',
      questionText: 'What is the difference between a Requirement and an Acceptance Criterion?',
      options: [
        'They are the same thing — different teams use different names',
        'A requirement defines what to build. An AC defines how you will verify it was built correctly.',
        'Requirements are written by developers. AC are written by testers.',
        'Requirements cover functional behaviour. AC cover non-functional behaviour like performance.',
      ],
      correctAnswer: 'A requirement defines what to build. An AC defines how you will verify it was built correctly.',
      explanation: 'Requirements are the "what". AC are the "how we know it is done". If an AC is not testable with a pass/fail result, it is poorly written.',
      lessonContext: '',
    },
    {
      questionId:   'l2-q5',
      type:         'multiple-choice',
      questionText: 'A developer marks your bug as "Resolved." What is your immediate next action?',
      options: [
        'Close the bug — if the developer says it is fixed, trust them',
        'Re-open the bug — Resolved always means something went wrong',
        'Verify the fix yourself using the original repro steps before closing the bug',
        'Ask the developer to demonstrate the fix in a meeting',
      ],
      correctAnswer: 'Verify the fix yourself using the original repro steps before closing the bug',
      explanation: '"Resolved" is a claim by the developer. It is not a fact until QA verifies it in the environment using the original reproduction steps.',
      lessonContext: '',
    },
  ],

  // ---------------------------------------------------------------------------
  // LESSON 3 — Dynamics CRM Mock (Renamed from Lesson 2)
  // ---------------------------------------------------------------------------
  'lesson-3': [
    {
      questionId:   'l3-q1',
      type:         'multiple-choice',
      questionText: 'A Junior Investigator opens a case and attempts to set Status to "Closed". According to the acceptance criteria, what should happen?',
      options: [
        'The status changes to Closed and the record saves.',
        'The save is blocked and a validation message appears on the Status field.',
        'The Closed option is hidden from the Status dropdown for Junior Investigators.',
        'A confirmation dialog appears asking the Junior to confirm.',
      ],
      correctAnswer: 'The save is blocked and a validation message appears on the Status field.',
      explanation: 'AC-4.6 states that Junior Investigators cannot save as Resolved or Closed. The option is visible, but the save action must be blocked with an inline error.',
      lessonContext: '',
    },
    {
      questionId:   'l3-q2',
      type:         'multiple-choice',
      questionText: 'You are testing the Outcome / Resolution field. You log in as a Junior Investigator, inspect the page source, and find the field in the HTML — but it has a CSS class of "hidden". Should you log a bug?',
      options: [
        'No — the field is hidden with CSS, so it is not visible to the user.',
        'No — only Senior Investigators need to test this field.',
        'Yes — the acceptance criteria requires the field to be absent from the DOM entirely, not just hidden with CSS.',
        'Yes — the hidden class might not work in all browsers.',
      ],
      correctAnswer: 'Yes — the acceptance criteria requires the field to be absent from the DOM entirely, not just hidden with CSS.',
      explanation: 'AC-4.1 specifies that the field must be absent from the DOM. A "hidden" CSS class still leaves the data in the HTML, which is a security/requirement failure.',
      lessonContext: '',
    },
    {
      questionId:   'l3-q3',
      type:         'multiple-choice',
      questionText: 'The Case Title field has a maximum of 120 characters. You type exactly 120 characters. What should happen when you type the 121st character?',
      options: [
        'A validation error appears below the field.',
        'The field border turns red.',
        'The character is not accepted — input simply stops at 120.',
        'A modal appears warning the user they have reached the limit.',
      ],
      correctAnswer: 'The character is not accepted — input simply stops at 120.',
      explanation: 'AC-3.2 specifies that the field must not accept characters beyond 120. The input simply stops, rather than allowing the text and showing an error later.',
      lessonContext: '',
    },
    {
      questionId:   'l3-q4',
      type:         'multiple-choice',
      questionText: 'You check the Escalated checkbox. The Escalation Reason dropdown does NOT appear. You confirm this happens every time you test it. What type of bug is this?',
      options: [
        'A cosmetic bug. Report the screenshot only.',
        'A functional bug. Report: role active, exact repro steps, expected result (AC-3.4), and actual result.',
        'A performance bug. Report: how long it took to appear.',
        'An environment bug. Report: which browser you are using only.',
      ],
      correctAnswer: 'A functional bug. Report: role active, exact repro steps, expected result (AC-3.4), and actual result.',
      explanation: 'This is a failure of the conditional logic defined in AC-3.4. Because it blocks a required user action, it is a functional defect.',
      lessonContext: '',
    },
    {
      questionId:   'l3-q5',
      type:         'multiple-choice',
      questionText: 'You save a case and the Last Updated timestamp in the sidebar does not change. What criterion covers this, and is this a bug?',
      options: [
        'This is covered by AC-5.2. Yes, this is a bug — Last Updated must reflect the current timestamp after every save.',
        'This is not covered by the acceptance criteria. No bug should be raised.',
        'This is covered by AC-5.2. No, it is expected behaviour.',
        'This is a cosmetic issue. Log it as low priority only.',
      ],
      correctAnswer: 'This is covered by AC-5.2. Yes, this is a bug — Last Updated must reflect the current timestamp after every save.',
      explanation: 'AC-5.2 explicitly requires the timestamp to update on every successful save. A failure to do so is a functional bug.',
      lessonContext: '',
    },
  ],

  // ---------------------------------------------------------------------------
  // LESSON 4 — Azure DevOps (NEW)
  // ---------------------------------------------------------------------------
  'lesson-4': [
    {
      questionId:   'l4-q1',
      type:         'scenario',
      questionText: 'You have found a defect. A developer asks for the "repro steps." What should you provide?',
      options: [
        'A description of what the feature is supposed to do',
        'A numbered list of exact actions, starting from login, that reproduce the issue every time',
        'A screenshot of the error message',
        'Your assessment of why the bug probably occurred',
      ],
      correctAnswer: 'A numbered list of exact actions, starting from login, that reproduce the issue every time',
      explanation: 'Repro steps must be an exact manual. If a developer can follow your list and see the bug on their first attempt without asking a question, the report is successful.',
      lessonContext: 'You are working in Azure DevOps and need to file a complete bug report.',
    },
    {
      questionId:   'l4-q2',
      type:         'scenario',
      questionText: 'A developer marks your bug as "Resolved." What is your immediate next action?',
      options: [
        'Close the bug — the developer has confirmed it is fixed',
        'Re-open the bug — Resolved usually means something went wrong',
        'Verify the fix yourself in the correct environment using the original repro steps',
        'Ask the developer to show you the fix in a code review',
      ],
      correctAnswer: 'Verify the fix yourself in the correct environment using the original repro steps',
      explanation: '"Resolved" is the developer\'s assertion. QA must verify the fix independently in the environment using the original steps before closing.',
      lessonContext: '',
    },
    {
      questionId:   'l4-q3',
      type:         'scenario',
      questionText: 'A Junior Investigator can set Status to "Closed" without any validation error, which contradicts AC-4.2. What severity level should you assign this bug?',
      options: [
        'Low — it is a minor permission issue that can be worked around',
        'Medium — it affects functionality but data is not at risk',
        'High — a core feature is broken and there is a permission/security implication',
        'Critical — the system is unusable',
      ],
      correctAnswer: 'High — a core feature is broken and there is a permission/security implication',
      explanation: 'Role-based permissions are a core security feature. Allowing an unauthorized user to close a case is a high-severity failure of the business rules.',
      lessonContext: '',
    },
    {
      questionId:   'l4-q4',
      type:         'scenario',
      questionText: 'You write a bug report with the title "Login doesn\'t work." A developer asks for clarification. What is wrong with this title?',
      options: [
        'It is too short — bug titles must be at least 10 words',
        'It does not specify the action, the object, or the unexpected outcome — a developer cannot begin investigating without asking follow-up questions',
        'It should reference the AC number instead',
        'Bug titles should not mention the feature name',
      ],
      correctAnswer: 'It does not specify the action, the object, or the unexpected outcome — a developer cannot begin investigating without asking follow-up questions',
      explanation: 'A good title follows: [Action] + [Object] + [Unexpected Outcome]. Example: "Login page does not redirect to dashboard after valid credentials entered."',
      lessonContext: '',
    },
    {
      questionId:   'l4-q5',
      type:         'scenario',
      questionText: 'You are re-opening a bug. What must your re-open comment include?',
      options: [
        'Only the statement "still broken"',
        'Your opinion on why the developer\'s fix was insufficient',
        'What you tested, in which build, the exact steps you followed, and what specifically still fails or newly fails',
        'A request for a meeting to discuss the issue',
      ],
      correctAnswer: 'What you tested, in which build, the exact steps you followed, and what specifically still fails or newly fails',
      explanation: 'A re-open comment must be evidence-based. You must state the build number, the role used, and the exact step where the failure recurred to avoid "it works on my machine" disputes.',
      lessonContext: '',
    },
  ],

  // ---------------------------------------------------------------------------
  // CAPSTONE — Full Scenario Assessment
  // ---------------------------------------------------------------------------
  'capstone': [
    {
      questionId:   'cap-q1',
      type:         'scenario',
      questionText: 'You are a Junior Investigator. You open CASE-00042. You fill in the Case Title, set Status to "Resolved", and click Save. What do you expect to happen, and what would you write in your bug report if it saves successfully?',
      options: [
        'It should save. No bug — Resolved is a valid status.',
        'It should be blocked with a validation message. If it saves, report: the save completed without error when it should have been blocked, referencing AC-4.6 as the expected behaviour.',
        'It should redirect to the case list. If it saves, report: wrong navigation behaviour.',
        'It should show a modal. If it saves, report: modal did not appear.',
      ],
      correctAnswer: 'It should be blocked with a validation message. If it saves, report: the save completed without error when it should have been blocked, referencing AC-4.6 as the expected behaviour.',
      explanation: 'AC-4.6 explicitly blocks Juniors from saving Resolved/Closed cases. If a save succeeds, the role-based restriction is broken.',
      lessonContext: 'Capstone Assessment: Full System Simulation.',
    },
  ],

};

// ── SECTION 3: UTILITY FUNCTIONS ──────────────────────────────────────────────

/**
 * getQuestionsForLesson(lessonId)
 * Returns the array of questions for a given lesson.
 * 
 * @param {string} lessonId - The lesson ID. e.g. "lesson-1"
 * @returns {Array} Array of question objects for that lesson.
 */
function getQuestionsForLesson(lessonId) {
  return QUIZ_QUESTIONS[lessonId] || [];
}

/**
 * getQuestionById(lessonId, questionId)
 * Finds a specific question within a lesson by its ID.
 * 
 * @param {string} lessonId   - The lesson the question belongs to.
 * @param {string} questionId - The question's unique ID.
 * @returns {Object|null} The question object, or null.
 */
function getQuestionById(lessonId, questionId) {
  const questions = getQuestionsForLesson(lessonId);
  return questions.find(q => q.questionId === questionId) || null;
}