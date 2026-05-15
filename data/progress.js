/**
 * =============================================================================
 * progress.js — Student Lesson Progress & Quiz Results
 * =============================================================================
 * QA Onboarding Training Platform
 *
 * HOW THIS FILE WORKS:
 * --------------------
 * Tracks each student's progress through the course: which lessons are done,
 * quiz results (right/wrong per question with explanations), and overall
 * completion status.
 *
 * Progress is stored in localStorage under 'qa_progress' as an object where
 * each key is a student's Case ID and the value is their progress record.
 *
 * SCORING PHILOSOPHY (design decision — don't change without updating docs):
 * ---------------------------------------------------------------------------
 * There is NO pass/fail percentage. Instead, the student sees:
 *   - Which questions they got right
 *   - Which questions they got wrong, with the correct answer and an explanation
 * The Admin dashboard shows "areas to concentrate on" per student based on this.
 *
 * STORAGE STRUCTURE:
 * ------------------
 * {
 *   "CASE-00001": { ...progressRecord },
 *   "CASE-00002": { ...progressRecord },
 *   ...
 * }
 *
 * =============================================================================
 */


// ── SECTION 1: DATA SCHEMA ────────────────────────────────────────────────────

/*
PROGRESS RECORD SCHEMA (per student):
{
  caseId:         string  — The student's Case ID. Must match a record in students.js.

  lessonsComplete: Array  — List of lesson IDs the student has fully completed.
                            e.g. ["lesson-1", "lesson-2"]

  currentLesson:  string  — The lesson ID the student is currently on.
                            e.g. "lesson-2"
                            null if the student has not started yet.

  quizResults:    Object  — One entry per lesson that has quiz questions.
                            Key = lesson ID. Value = array of question results.
                            See QUIZ RESULT schema below.

  placementSurvey: Object — Results from the intro skills check survey.
                            See PLACEMENT SURVEY schema below.

  certificateEarned: boolean — true once the student completes the Capstone.

  lastActivity:   string  — ISO datetime of the student's most recent action.
                            e.g. "2026-05-11T14:32:00.000Z"
                            Used for "last active" display in Admin dashboard.
}

QUIZ RESULT SCHEMA (per question, inside quizResults[lessonId]):
{
  questionId:     string  — Unique ID for the question. Matches quiz-questions.js.
  questionText:   string  — The question as it was shown to the student.
  studentAnswer:  string  — The answer the student selected.
  correctAnswer:  string  — The correct answer (for display if student was wrong).
  isCorrect:      boolean — Whether the student got it right.
  explanation:    string  — Why the correct answer is correct.
                            Shown to student after answering, regardless of right/wrong.
}

PLACEMENT SURVEY SCHEMA:
{
  completed:      boolean — Whether the student finished the survey.
  recommendedPath: Array  — Array of lesson IDs in the recommended order.
                            e.g. ["lesson-1", "lesson-2", "lesson-3", "capstone"]
  answers:        Array   — Raw survey answers (for Admin review).
}

EXAMPLE (one student's full progress record):
{
  caseId: "CASE-00001",
  lessonsComplete: ["lesson-1"],
  currentLesson: "lesson-2",
  quizResults: {
    "lesson-1": [
      {
        questionId:    "l1-q1",
        questionText:  "A test case must always include expected results.",
        studentAnswer: "True",
        correctAnswer: "True",
        isCorrect:     true,
        explanation:   "Expected results define what 'correct' looks like. Without them, a tester cannot objectively verify a pass or fail."
      }
    ]
  },
  placementSurvey: {
    completed: true,
    recommendedPath: ["lesson-1", "lesson-2", "lesson-3", "capstone"],
    answers: []
  },
  certificateEarned: false,
  lastActivity: "2026-05-11T14:32:00.000Z"
}
*/


// ── SECTION 2: STORAGE KEY ────────────────────────────────────────────────────

const PROGRESS_STORAGE_KEY = 'qa_progress';


// ── SECTION 3: PROGRESS FUNCTIONS ─────────────────────────────────────────────

/**
 * getAllProgress()
 * Returns the full progress store (all students).
 * Returns an empty object if nothing is saved yet.
 *
 * @returns {Object} Keys are Case IDs, values are progress records.
 */
function getAllProgress() {
  const raw = localStorage.getItem(PROGRESS_STORAGE_KEY);
  if (!raw) return {};
  try {
    return JSON.parse(raw);
  } catch (error) {
    console.warn('qa_progress data is corrupted. Returning empty object.', error);
    return {};
  }
}


/**
 * getStudentProgress(caseId)
 * Gets the progress record for a single student.
 * Creates and saves a blank record if this student has no progress yet.
 *
 * @param {string} caseId - The student's Case ID. e.g. "CASE-00001"
 * @returns {Object} The student's progress record.
 */
function getStudentProgress(caseId) {
  const all = getAllProgress();

  // If this student doesn't have a record yet, create a blank one
  if (!all[caseId]) {
    all[caseId] = createBlankProgressRecord(caseId);
    saveAllProgress(all);
  }

  return all[caseId];
}


/**
 * createBlankProgressRecord(caseId)
 * Creates an empty progress record for a new student.
 * Called automatically by getStudentProgress() for first-time students.
 *
 * @param {string} caseId - The student's Case ID.
 * @returns {Object} A fresh, empty progress record.
 */
function createBlankProgressRecord(caseId) {
  return {
    caseId:             caseId,
    lessonsComplete:    [],          // No lessons done yet
    currentLesson:      null,        // Not started yet
    quizResults:        {},          // No quiz results yet
    placementSurvey: {
      completed:        false,
      recommendedPath:  [],
      answers:          [],
    },
    certificateEarned:  false,
    lastActivity:       new Date().toISOString(),
  };
}


/**
 * saveAllProgress(progressObject)
 * Saves the full progress store to localStorage.
 *
 * @param {Object} progressObject - The complete progress store.
 * @returns {boolean} true if saved, false on error.
 */
function saveAllProgress(progressObject) {
  try {
    localStorage.setItem(PROGRESS_STORAGE_KEY, JSON.stringify(progressObject));
    return true;
  } catch (error) {
    console.error('Failed to save progress to localStorage.', error);
    return false;
  }
}


/**
 * markLessonComplete(caseId, lessonId)
 * Marks a lesson as complete for a student.
 * Updates lessonsComplete array and lastActivity timestamp.
 *
 * @param {string} caseId    - The student's Case ID.
 * @param {string} lessonId  - The lesson ID. e.g. "lesson-1"
 * @returns {boolean} true if saved successfully.
 */
function markLessonComplete(caseId, lessonId) {
  const all = getAllProgress();
  const record = all[caseId] || createBlankProgressRecord(caseId);

  // Only add if not already in the completed list (prevent duplicates)
  if (!record.lessonsComplete.includes(lessonId)) {
    record.lessonsComplete.push(lessonId);
  }

  record.lastActivity = new Date().toISOString();
  all[caseId] = record;
  return saveAllProgress(all);
}


/**
 * saveQuizResults(caseId, lessonId, resultsArray)
 * Saves the quiz results for a specific lesson for a specific student.
 * Each call overwrites the results for that lesson (retakes replace previous).
 *
 * @param {string} caseId        - The student's Case ID.
 * @param {string} lessonId      - The lesson this quiz belongs to.
 * @param {Array}  resultsArray  - Array of question result objects (see schema above).
 * @returns {boolean} true if saved successfully.
 */
function saveQuizResults(caseId, lessonId, resultsArray) {
  const all = getAllProgress();
  const record = all[caseId] || createBlankProgressRecord(caseId);

  record.quizResults[lessonId] = resultsArray;
  record.lastActivity = new Date().toISOString();
  all[caseId] = record;
  return saveAllProgress(all);
}


/**
 * savePlacementSurvey(caseId, recommendedPath, answers)
 * Saves the results of the intro placement skills survey.
 *
 * @param {string} caseId           - The student's Case ID.
 * @param {Array}  recommendedPath  - Array of lesson IDs in recommended order.
 * @param {Array}  answers          - Raw answer data from the survey.
 * @returns {boolean} true if saved successfully.
 */
function savePlacementSurvey(caseId, recommendedPath, answers) {
  const all = getAllProgress();
  const record = all[caseId] || createBlankProgressRecord(caseId);

  record.placementSurvey = {
    completed:        true,
    recommendedPath:  recommendedPath,
    answers:          answers,
  };

  record.lastActivity = new Date().toISOString();
  all[caseId] = record;
  return saveAllProgress(all);
}


/**
 * awardCertificate(caseId)
 * Marks that a student has earned their certificate.
 * Called when the student successfully completes the Capstone.
 *
 * @param {string} caseId - The student's Case ID.
 * @returns {boolean} true if saved successfully.
 */
function awardCertificate(caseId) {
  const all = getAllProgress();
  const record = all[caseId] || createBlankProgressRecord(caseId);

  record.certificateEarned = true;
  record.lastActivity = new Date().toISOString();
  all[caseId] = record;
  return saveAllProgress(all);
}
