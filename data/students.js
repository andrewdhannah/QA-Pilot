/**
 * =============================================================================
 * students.js — Student Account Records (LEGACY — localStorage)
 * =============================================================================
 * QA Onboarding Training Platform
 *
 * NOTE: This module uses localStorage and is superseded by js/db.js,
 * which stores data in IndexedDB and handles password hashing via
 * hashPassword() / verifyPassword() (PBKDF2). All pages now load
 * js/db.js instead of this file.
 *
 * HOW THIS FILE WORKS:
 * --------------------
 * This file defines the structure for student accounts and provides the
 * functions to create, find, and update student records in localStorage.
 *
 * Students are stored in localStorage under the key 'qa_students' as an
 * array of student objects.
 *
 * Each new student gets a unique Case ID in the format CASE-00001.
 * The Case ID auto-increments and is checked for duplicates before being
 * assigned. It can never be edited after creation.
 *
 * =============================================================================
 */


// ── SECTION 1: DATA SCHEMA ────────────────────────────────────────────────────
// This is what a single student record looks like.
// See the EXAMPLE at the bottom of this section.

/*
STUDENT RECORD SCHEMA:
{
  caseId:       string  — Auto-generated. Format: "CASE-00001". Read-only after creation.
                          Increments from the highest existing caseId in the store.
                          Duplicate-checked before commit.

  name:         string  — Student's full name. Required. Set by Admin when creating account.

  email:        string  — Student's email address. Used for login. Must be unique.

  password:     string  — PBKDF2 hash in "salt:hash" format (base64).
                           Hashed by hashPassword() in db.js before storage.
                           Never stored as plain text.

  role:         string  — One of: 'junior' | 'senior'
                          Determines which fields are visible/editable on the CRM mock screen.
                          Set by Admin. Cannot be changed by the student.

  dateCreated:  string  — ISO date string (YYYY-MM-DD) when the account was created.
                          Set automatically by the system.

  active:       boolean — Whether the student account is active.
                          Admin can deactivate accounts without deleting them.
}

EXAMPLE:
{
  caseId:       "CASE-00001",
  name:         "Jane Smith",
  email:        "jane.smith@example.com",
  password:     "Welcome1",
  role:         "junior",
  dateCreated:  "2026-05-11",
  active:       true
}
*/


// ── SECTION 2: STORAGE KEY ────────────────────────────────────────────────────
// All student records are stored in localStorage under this key.
// Using a constant prevents typos across files.

const STUDENTS_STORAGE_KEY = 'qa_students';


// ── SECTION 3: STUDENT FUNCTIONS ──────────────────────────────────────────────

/**
 * getAllStudents()
 * Returns the full array of student records from localStorage.
 * Returns an empty array if no students exist yet.
 *
 * @returns {Array} Array of student objects.
 */
function getAllStudents() {
  const raw = localStorage.getItem(STUDENTS_STORAGE_KEY);

  if (!raw) return [];  // No students saved yet — return empty array

  try {
    return JSON.parse(raw);
  } catch (error) {
    console.warn('qa_students data in localStorage is corrupted. Returning empty array.', error);
    return [];
  }
}


/**
 * saveAllStudents(studentsArray)
 * Saves the full students array back to localStorage.
 * Always pass the complete array — this overwrites what's stored.
 *
 * @param {Array} studentsArray - The full array of student objects to save.
 * @returns {boolean} true if saved, false if an error occurred.
 */
function saveAllStudents(studentsArray) {
  try {
    localStorage.setItem(STUDENTS_STORAGE_KEY, JSON.stringify(studentsArray));
    return true;
  } catch (error) {
    console.error('Failed to save students to localStorage.', error);
    return false;
  }
}


/**
 * findStudentByEmail(email)
 * Searches for a student with a matching email address.
 * Used for login and duplicate-checking when creating accounts.
 *
 * @param {string} email - The email address to search for.
 * @returns {Object|null} The student object if found, or null if not found.
 */
function findStudentByEmail(email) {
  const students = getAllStudents();
  // Array.find() returns the first match or undefined; we convert undefined to null
  return students.find(s => s.email.toLowerCase() === email.toLowerCase()) || null;
}


/**
 * findStudentByCaseId(caseId)
 * Searches for a student with a matching Case ID.
 * Used for duplicate detection when generating new Case IDs.
 *
 * @param {string} caseId - The Case ID to search for. e.g. "CASE-00001"
 * @returns {Object|null} The student object if found, or null if not found.
 */
function findStudentByCaseId(caseId) {
  const students = getAllStudents();
  return students.find(s => s.caseId === caseId) || null;
}


/**
 * generateNextCaseId()
 * Generates the next available Case ID in CASE-00001 format.
 *
 * HOW IT WORKS:
 * 1. Gets all existing Case IDs from the student store.
 * 2. Finds the highest numeric value (e.g. CASE-00007 → 7).
 * 3. Adds 1 to get the next number.
 * 4. Checks that the new ID isn't already taken (conflict from imports, etc.)
 * 5. If taken, keeps incrementing until a free one is found.
 *
 * The zero-padding ensures: CASE-00001, not CASE-1.
 * padStart(5, '0') pads the number to 5 digits with leading zeros.
 *
 * @returns {string} A new unique Case ID, e.g. "CASE-00008".
 */
function generateNextCaseId() {
  const students = getAllStudents();

  if (students.length === 0) {
    // No students yet — first Case ID is always CASE-00001
    return 'CASE-00001';
  }

  // Extract the numeric part from each Case ID and find the maximum
  const highestNumber = students.reduce((max, student) => {
    // Split "CASE-00007" on "-" → ["CASE", "00007"]
    // parseInt converts "00007" → 7 (leading zeros are fine for parseInt)
    const numericPart = parseInt(student.caseId.split('-')[1], 10);
    return numericPart > max ? numericPart : max;
  }, 0);

  // Start from one above the highest found
  let nextNumber = highestNumber + 1;

  // Keep incrementing until we find an ID not already in the store
  // This handles the edge case where a record was imported with a non-sequential ID
  while (findStudentByCaseId(`CASE-${String(nextNumber).padStart(5, '0')}`)) {
    nextNumber++;
  }

  // Format: pad the number to 5 digits with leading zeros, prepend "CASE-"
  return `CASE-${String(nextNumber).padStart(5, '0')}`;
}


/**
 * createStudent(name, email, password, role)
 * Creates a new student account and saves it to the store.
 * Validates that the email isn't already taken before creating.
 *
 * NOTE: This legacy function stores the password as-is. The active
 * code path in admin/dashboard.html calls hashPassword() from db.js
 * before calling saveStudent(), so passwords are hashed at rest.
 *
 * @param {string} name     - Student's full name.
 * @param {string} email    - Student's email address. Must be unique.
 * @param {string} password - Account password (hashed by caller via db.js).
 * @param {string} role     - One of: 'junior' | 'senior'
 * @returns {Object} Result object: { success: boolean, student?: Object, error?: string }
 */
function createStudent(name, email, password, role) {
  // Check for duplicate email before proceeding
  if (findStudentByEmail(email)) {
    return { success: false, error: 'A student with this email address already exists.' };
  }

  // Build today's date string in YYYY-MM-DD format
  const today = new Date().toISOString().split('T')[0];

  // Assemble the new student record
  const newStudent = {
    caseId:       generateNextCaseId(),
    name:         name.trim(),
    email:        email.trim().toLowerCase(),
    password:     password,
    role:         role,            // 'junior' or 'senior'
    dateCreated:  today,
    active:       true,
  };

  // Add to the existing students array and save
  const students = getAllStudents();
  students.push(newStudent);
  const saved = saveAllStudents(students);

  if (saved) {
    return { success: true, student: newStudent };
  } else {
    return { success: false, error: 'Failed to save student to local storage.' };
  }
}


/**
 * authenticateStudent(email, password)
 * Checks if the provided email/password match a student record.
 *
 * NOTE: This legacy function uses direct string comparison. The active
 * login code in index.html uses verifyPassword() from db.js, which
 * performs constant-time PBKDF2 verification against the stored hash.
 *
 * @param {string} email    - The email address entered by the student.
 * @param {string} password - The password entered by the student.
 * @returns {Object} Result: { success: boolean, student?: Object, error?: string }
 */
function authenticateStudent(email, password) {
  const student = findStudentByEmail(email);

  // No matching email found
  if (!student) {
    return { success: false, error: 'Email address not found.' };
  }

  // Account is deactivated
  if (!student.active) {
    return { success: false, error: 'This account has been deactivated. Please contact your administrator.' };
  }

  // Password doesn't match
  if (student.password !== password) {
    return { success: false, error: 'Incorrect password.' };
  }

  // All checks passed
  return { success: true, student: student };
}
