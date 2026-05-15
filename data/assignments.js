/**
 * =============================================================================
 * assignments.js — Admin Lesson Assignments Per Student
 * =============================================================================
 * QA Onboarding Training Platform
 *
 * HOW THIS FILE WORKS:
 * --------------------
 * The Admin can assign specific lessons to each student, in a specific order.
 * A student only sees lessons they have been assigned — they cannot self-enrol.
 *
 * The placement skills survey recommends a path, but the Admin can override
 * it using the assign.html panel. This file tracks those assignments.
 *
 * Assignments are stored in localStorage under 'qa_assignments' as an object
 * where each key is a student's Case ID and the value is their assignment record.
 *
 * STORAGE STRUCTURE:
 * ------------------
 * {
 *   "CASE-00001": { ...assignmentRecord },
 *   "CASE-00002": { ...assignmentRecord },
 *   ...
 * }
 *
 * =============================================================================
 */


// ── SECTION 1: DATA SCHEMA ────────────────────────────────────────────────────

/*
ASSIGNMENT RECORD SCHEMA (per student):
{
  caseId:           string  — The student's Case ID. Must match a record in students.js.

  assignedLessons:  Array   — Ordered list of lesson IDs assigned to this student.
                              The order matters — students must complete them in sequence.
                              e.g. ["lesson-1", "lesson-2", "lesson-3", "capstone"]

  adminOverride:    boolean — true if an Admin manually set the path (overriding
                              the placement survey recommendation).
                              false if the path was set by the survey or is default.

  assignedBy:       string  — The admin who made the assignment (for audit trail).
                              Currently stores "admin" — could store admin username later.

  assignedDate:     string  — ISO date string (YYYY-MM-DD) when the assignment was made.

  notes:            string  — Optional Admin notes about this student's assignment.
                              e.g. "Skipping Lesson 1 — student has prior QA experience."
}

EXAMPLE:
{
  caseId:           "CASE-00001",
  assignedLessons:  ["lesson-2", "lesson-3", "capstone"],
  adminOverride:    true,
  assignedBy:       "admin",
  assignedDate:     "2026-05-11",
  notes:            "Student has prior QA experience. Starting from Lesson 2."
}
*/


// ── SECTION 2: DEFAULT LESSON ORDER ───────────────────────────────────────────
// When an assignment is created without a specific path (e.g. from the survey),
// this is the default full course sequence.

const DEFAULT_LESSON_ORDER = [
  'lesson-1',   // Testing 101 — T/F quiz
  'lesson-2',   // Dynamics CRM Mock — multiple-choice quiz
  'lesson-3',   // Azure DevOps Mock — scenario quiz
  'capstone',   // Capstone Assessment — full scenario + certificate
];


// ── SECTION 3: STORAGE KEY ────────────────────────────────────────────────────

const ASSIGNMENTS_STORAGE_KEY = 'qa_assignments';


// ── SECTION 4: ASSIGNMENT FUNCTIONS ───────────────────────────────────────────

/**
 * getAllAssignments()
 * Returns the full assignments store (all students).
 * Returns an empty object if nothing is saved yet.
 *
 * @returns {Object} Keys are Case IDs, values are assignment records.
 */
function getAllAssignments() {
  const raw = localStorage.getItem(ASSIGNMENTS_STORAGE_KEY);
  if (!raw) return {};
  try {
    return JSON.parse(raw);
  } catch (error) {
    console.warn('qa_assignments data is corrupted. Returning empty object.', error);
    return {};
  }
}


/**
 * getStudentAssignment(caseId)
 * Gets the assignment record for a single student.
 * Returns null if no assignment exists (Admin hasn't assigned yet).
 *
 * @param {string} caseId - The student's Case ID.
 * @returns {Object|null} The assignment record, or null if none set.
 */
function getStudentAssignment(caseId) {
  const all = getAllAssignments();
  return all[caseId] || null;
}


/**
 * saveAllAssignments(assignmentsObject)
 * Saves the full assignments store to localStorage.
 *
 * @param {Object} assignmentsObject - The complete assignments store.
 * @returns {boolean} true if saved, false on error.
 */
function saveAllAssignments(assignmentsObject) {
  try {
    localStorage.setItem(ASSIGNMENTS_STORAGE_KEY, JSON.stringify(assignmentsObject));
    return true;
  } catch (error) {
    console.error('Failed to save assignments to localStorage.', error);
    return false;
  }
}


/**
 * assignLessons(caseId, lessonIds, adminOverride, notes)
 * Creates or updates the lesson assignment for a student.
 * Called from the Admin assign.html panel.
 *
 * @param {string}  caseId        - The student's Case ID.
 * @param {Array}   lessonIds     - Ordered array of lesson IDs to assign.
 *                                  e.g. ["lesson-1", "lesson-2", "capstone"]
 * @param {boolean} adminOverride - true if Admin is manually overriding the survey path.
 * @param {string}  notes         - Optional admin notes for this student.
 * @returns {boolean} true if saved successfully.
 */
function assignLessons(caseId, lessonIds, adminOverride = false, notes = '') {
  const all = getAllAssignments();
  const today = new Date().toISOString().split('T')[0];

  all[caseId] = {
    caseId:           caseId,
    assignedLessons:  lessonIds,
    adminOverride:    adminOverride,
    assignedBy:       'admin',
    assignedDate:     today,
    notes:            notes,
  };

  return saveAllAssignments(all);
}


/**
 * assignDefaultPath(caseId)
 * Assigns the full default course sequence to a student.
 * Used when the placement survey completes and recommends the full path,
 * or as a fallback when no survey was taken.
 *
 * @param {string} caseId - The student's Case ID.
 * @returns {boolean} true if saved successfully.
 */
function assignDefaultPath(caseId) {
  return assignLessons(caseId, DEFAULT_LESSON_ORDER, false, '');
}


/**
 * getNextLesson(caseId, completedLessons)
 * Determines which lesson the student should do next.
 * Compares their assigned path against their completed lessons.
 *
 * @param {string} caseId            - The student's Case ID.
 * @param {Array}  completedLessons  - Array of lesson IDs the student has finished.
 * @returns {string|null} The ID of the next lesson, or null if all are complete.
 */
function getNextLesson(caseId, completedLessons) {
  const assignment = getStudentAssignment(caseId);

  // If no assignment exists, fall back to the default order
  const assignedPath = assignment ? assignment.assignedLessons : DEFAULT_LESSON_ORDER;

  // Find the first lesson in the assigned path that is NOT in completedLessons
  const nextLesson = assignedPath.find(lessonId => !completedLessons.includes(lessonId));

  return nextLesson || null;  // null means all assigned lessons are done
}
