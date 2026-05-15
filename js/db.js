/**
 * =============================================================================
 * db.js — IndexedDB Database Module
 * =============================================================================
 * QA Onboarding Training Platform
 *
 * PURPOSE:
 * This is the ONLY file that reads from or writes to IndexedDB.
 * No other file should touch IndexedDB directly. All other files call
 * the functions in this file to read or save data.
 *
 * HOW TO USE THIS FILE:
 * Every page that needs data must:
 *   1. Load this file in a <script> tag.
 *   2. Call initDB() and wait for it to finish before calling anything else.
 * All functions are ASYNCHRONOUS — they return Promises.
 *
 * WHAT'S IN HERE:
 * - Section 1: Database constants
 * - Section 2: Database initialisation (initDB)
 * - Section 3: Internal helper functions (_get, _getAll, _put)
 * - Section 4: Student functions
 * - Section 5: Progress functions
 * - Section 6: Assignment functions
 * - Section 7: Settings functions
 *
 * READS FROM:   IndexedDB
 * WRITES TO:    IndexedDB
 * =============================================================================
 */

// ── SECTION 1: DATABASE CONSTANTS ─────────────────────────────────────────────

const DB_NAME = 'qa_onboarding_db';
const DB_VERSION = 1;
let _db = null;

// ── SECTION 2: DATABASE INITIALISATION ────────────────────────────────────────

/**
 * initDB()
 * Opens the IndexedDB database and creates all object stores on first run.
 * Must be called on every page load before any other db function is used.
 *
 * @returns {Promise<IDBDatabase>} Resolves with the open database connection.
 */
function initDB() {
  return new Promise(function(resolve, reject) {
    if (_db) {
      resolve(_db);
      return;
    }

    var request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = function(event) {
      var database = event.target.result;

      if (!database.objectStoreNames.contains('students')) {
        database.createObjectStore('students', { keyPath: 'caseId' });
      }
      if (!database.objectStoreNames.contains('progress')) {
        database.createObjectStore('progress', { keyPath: 'caseId' });
      }
      if (!database.objectStoreNames.contains('assignments')) {
        database.createObjectStore('assignments', { keyPath: 'caseId' });
      }
      if (!database.objectStoreNames.contains('settings')) {
        database.createObjectStore('settings', { keyPath: 'key' });
      }
    };

    request.onsuccess = function(event) {
      _db = event.target.result;
      resolve(_db);
    };

    request.onerror = function(event) {
      console.error('db.js: Failed to open IndexedDB.', event.target.error);
      reject(event.target.error);
    };
  });
}

// ── SECTION 3: INTERNAL HELPER FUNCTIONS ──────────────────────────────────────

/**
 * _get(storeName, key)
 * Fetches a single record from a store by its primary key.
 *
 * @param {string} storeName - Which store to read from.
 * @param {string} key       - The key to look up.
 * @returns {Promise<Object|undefined>} The record, or undefined if not found.
 */
function _get(storeName, key) {
  return new Promise(function(resolve, reject) {
    var tx = _db.transaction(storeName, 'readonly'); // 'readonly' is safer and faster for fetches
    var store = tx.objectStore(storeName);
    var request = store.get(key);
    request.onsuccess = function() { resolve(request.result); };
    request.onerror = function() { reject(request.error); };
  });
}

/**
 * _getAll(storeName)
 * Fetches all records from a store.
 *
 * @param {string} storeName - Which store to read from.
 * @returns {Promise<Array>} Array of all records.
 */
function _getAll(storeName) {
  return new Promise(function(resolve, reject) {
    var tx = _db.transaction(storeName, 'readonly');
    var store = tx.objectStore(storeName);
    var request = store.getAll();
    request.onsuccess = function() { resolve(request.result || []); };
    request.onerror = function() { reject(request.error); };
  });
}

/**
 * _put(storeName, object)
 * Saves or updates a record in a store.
 *
 * @param {string} storeName - Which store to write to.
 * @param {Object} object    - The record to save.
 * @returns {Promise<void>} Resolves when the write is complete.
 */
function _put(storeName, object) {
  return new Promise(function(resolve, reject) {
    var tx = _db.transaction(storeName, 'readwrite'); // requires 'readwrite' to modify data
    var store = tx.objectStore(storeName);
    var request = store.put(object);
    request.onsuccess = function() { resolve(); };
    request.onerror = function() { reject(request.error); };
  });
}

// ── SECTION 4: STUDENT FUNCTIONS ──────────────────────────────────────────────

function getStudent(caseId) { return _get('students', caseId); }
function getAllStudents() { return _getAll('students'); }
function saveStudent(studentObject) { return _put('students', studentObject); }

/**
 * findStudentByEmail(email)
 * Performs a case-insensitive search for a student email.
 * 
 * @param {string} email - The email to search for.
 * @returns {Promise<Object|null>} The student record or null.
 */
function findStudentByEmail(email) {
  return getAllStudents().then(function(students) {
    var match = students.find(function(s) {
      return s.email.toLowerCase() === email.toLowerCase();
    });
    return match || null;
  });
}

/**
 * generateNextCaseId()
 * Calculates the next sequential Case ID based on current maximum.
 * 
 * @returns {Promise<string>} Formatted ID e.g. 'CASE-00005'.
 */
function generateNextCaseId() {
  return getAllStudents().then(function(students) {
    if (students.length === 0) return 'CASE-00001';
    var highest = students.reduce(function(max, student) {
      var numericPart = parseInt(student.caseId.split('-')[1], 10);
      return numericPart > max ? numericPart : max;
    }, 0);
    var next = highest + 1;
    var existingIds = students.map(function(s) { return s.caseId; });
    while (existingIds.includes('CASE-' + String(next).padStart(5, '0'))) {
      next++;
    }
    return 'CASE-' + String(next).padStart(5, '0');
  });
}

// ── SECTION 5: PROGRESS FUNCTIONS ─────────────────────────────────────────────

function getProgress(caseId) { return _get('progress', caseId); }
function saveProgress(progressObject) { return _put('progress', progressObject); }

/**
 * saveChapterRead(caseId, lessonId, chapterId)
 * Marks a single lesson chapter as read in the student's progress record.
 * Safe to call multiple times — only adds the chapterId if not already present.
 *
 * @param {string} caseId     - Student's Case ID. e.g. 'CASE-00001'
 * @param {string} lessonId   - e.g. 'lesson-1'
 * @param {string} chapterId  - e.g. 'chapter-3'
 * @returns {Promise<void>}
 */
async function saveChapterRead(caseId, lessonId, chapterId) {
  const progress = await getProgress(caseId) || { caseId: caseId };
  
  // Ensure the nesting exists to avoid "cannot set property of undefined" errors
  if (!progress.chaptersRead) progress.chaptersRead = {};
  if (!progress.chaptersRead[lessonId]) progress.chaptersRead[lessonId] = [];
  
  // Only add the chapter if it isn't already recorded
  if (!progress.chaptersRead[lessonId].includes(chapterId)) {
    progress.chaptersRead[lessonId].push(chapterId);
  }
  return saveProgress(progress);
}

/**
 * addTimeSpent(caseId, lessonId, seconds)
 * Adds elapsed seconds to the student's running total for a lesson.
 * Accumulates across multiple sessions — never overwrites.
 *
 * @param {string} caseId    - Student's Case ID
 * @param {string} lessonId  - e.g. 'lesson-1'
 * @param {number} seconds   - Seconds to add to the running total
 * @returns {Promise<void>}
 */
async function addTimeSpent(caseId, lessonId, seconds) {
  const progress = await getProgress(caseId) || { caseId: caseId };
  
  // Initialize timeSpent map if it's the student's first time in any lesson
  if (!progress.timeSpent) progress.timeSpent = {};
  
  // Add to existing value, or start at 0 if this is the first time in this specific lesson
  progress.timeSpent[lessonId] = (progress.timeSpent[lessonId] || 0) + seconds;
  
  return saveProgress(progress);
}

/**
 * saveQuizResults(caseId, lessonId, results)
 * Saves the score and completion status for a specific assessment.
 * Accepts 'lesson-1' through 'lesson-4' as well as 'capstone'.
 * 
 * @param {string} caseId    - Student's Case ID.
 * @param {string} lessonId  - e.g. 'capstone'
 * @param {Object} results   - { score, maxScore, percentage, passed, completedAt }
 * @returns {Promise<void>}
 */
async function saveQuizResults(caseId, lessonId, results) {
  const progress = await getProgress(caseId) || { caseId: caseId };
  if (!progress.quizResults) progress.quizResults = {};
  
  progress.quizResults[lessonId] = results;
  return saveProgress(progress);
}

/**
 * awardCertificate(caseId)
 * Marks the student as having earned their certificate and sets the date.
 * Called by capstone.html after a successful final submission.
 * 
 * @param {string} caseId - Student's Case ID.
 * @returns {Promise<void>}
 */
async function awardCertificate(caseId) {
  const progress = await getProgress(caseId) || { caseId: caseId };
  // Write both field names so every page works regardless of which it reads.
  // certificate.html reads certificateAwarded; admin dashboard reads certificateEarned.
  progress.certificateAwarded = true;
  progress.certificateEarned  = true;
  progress.certificateDate = new Date().toISOString();
  return saveProgress(progress);
}

// ── SECTION 6: ASSIGNMENT FUNCTIONS ───────────────────────────────────────────

function getAssignment(caseId) { return _get('assignments', caseId); }
function saveAssignment(assignmentObject) { return _put('assignments', assignmentObject); }
function getAllProgressRecords() { return _getAll('progress'); }

// ── SECTION 7: SETTINGS FUNCTIONS ─────────────────────────────────────────────

/**
 * getSetting(key)
 * Reads a single admin-editable setting by its key name.
 * 
 * @param {string} key - The setting name.
 * @returns {Promise<string|undefined>} The setting value, or undefined.
 */
function getSetting(key) {
  return _get('settings', key).then(function(record) {
    return record ? record.value : undefined;
  });
}

/**
 * saveSetting(key, value)
 * Saves a single admin-editable setting.
 * 
 * @param {string} key   - The setting name.
 * @param {string} value - The value to save.
 * @returns {Promise<void>} Resolves when saved.
 */
function saveSetting(key, value) {
  return _put('settings', { key: key, value: value });
}

/**
 * getAdminPassword()
 * Retrieves the admin password from the IndexedDB settings store.
 * 
 * @returns {Promise<string|undefined>} The stored password, or undefined.
 */
function getAdminPassword() {
  return getSetting('adminPassword');
}

/**
 * setAdminPassword(newPassword)
 * Saves a new admin password to the IndexedDB settings store.
 * 
 * @param {string} newPassword - The new password to store.
 * @returns {Promise<void>} Resolves when the save is complete.
 */
function setAdminPassword(newPassword) {
  return saveSetting('adminPassword', newPassword);
}

/**
 * getBugToggles()
 * Returns all bug toggle states as a plain object.
 * Keys match the bug IDs stored in the 'settings' store.
 * Returns empty object if no toggles have been set (all bugs off = safe default).
 *
 * @returns {Promise<Object>} e.g. { 'status-junior-close': true, 'future-date-allowed': false }
 */
function getBugToggles() {
  // BUG FIX (key): Admin Bug Lab saves under key 'activeBugs', not 'bugToggles'.
  // BUG FIX (shape): getSetting() returns the unwrapped .value, not the raw
  //   IDB record { key, value }.  Using getSetting() here fixes both in one call.
  // Returns a plain object e.g. { 'status-junior-close': true, 'future-date-allowed': false }
  // or {} if no toggles have ever been configured (all bugs off is the safe default).
  return getSetting('activeBugs').then(function(raw) {
    if (!raw) return {};
    try {
      var parsed = (typeof raw === 'string') ? JSON.parse(raw) : raw;
      return (parsed && typeof parsed === 'object') ? parsed : {};
    } catch (e) {
      return {};
    }
  });
}
