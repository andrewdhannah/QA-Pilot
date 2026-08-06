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
const DB_VERSION = 2;
const PBKDF2_ITERATIONS = 100000;

// Cached database reference. Stored here after initDB() opens the connection
// so we don't have to re-open it on every function call.
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

    // onupgradeneeded fires when:
    //   - The database is being created for the first time (new install)
    //   - DB_VERSION has been incremented (schema change)
    // This is the ONLY place where you can create or delete object stores.
    // The `contains()` checks below are safe-guards — if upgrading from v1 to v2,
    // existing stores are skipped and only new stores are created.
    request.onupgradeneeded = function(event) {
      var database = event.target.result;

      // V1 STORES — created on first install (version 1)
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

      // V2 STORES — added in version 2 for multi-course platform
      if (!database.objectStoreNames.contains('courses')) {
        // Stores one course definition per record. Key = courseId (e.g. 'agile-scrum-dev').
        // Contains modules, sub-modules, quiz references, and metadata.
        database.createObjectStore('courses', { keyPath: 'courseId' });
      }
      if (!database.objectStoreNames.contains('enrollments')) {
        // Tracks which students are enrolled in which courses.
        // Key = compound string: `${caseId}::${courseId}` (e.g. 'CASE-00001::agile-scrum-dev').
        // This allows looking up a specific enrollment or all enrollments for a student.
        database.createObjectStore('enrollments', { keyPath: 'enrollmentId' });
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
    tx.onerror = function() { reject(tx.error); };
    tx.onabort = function() { reject(tx.error || new Error('Transaction aborted')); };
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
    tx.onerror = function() { reject(tx.error); };
    tx.onabort = function() { reject(tx.error || new Error('Transaction aborted')); };
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
    tx.onerror = function() { reject(tx.error); };
    tx.onabort = function() { reject(tx.error || new Error('Transaction aborted')); };
  });
}

/**
 * _delete(storeName, key)
 * Deletes a record from a store by its primary key.
 *
 * @param {string} storeName - Which store to delete from.
 * @param {string} key       - The key to delete.
 * @returns {Promise<void>} Resolves when the delete is complete.
 */
function _delete(storeName, key) {
  return new Promise(function(resolve, reject) {
    var tx = _db.transaction(storeName, 'readwrite');
    var store = tx.objectStore(storeName);
    var request = store.delete(key);
    request.onsuccess = function() { resolve(); };
    request.onerror = function() { reject(request.error); };
    tx.onerror = function() { reject(tx.error); };
    tx.onabort = function() { reject(tx.error || new Error('Transaction aborted')); };
  });
}

// ── SECTION 3.5: PASSWORD HASHING ──────────────────────────────────────────────

/**
 * _bufToBase64(buf)
 * Converts a Uint8Array to a base64-encoded string.
 * Used internally by hashPassword() and verifyPassword().
 *
 * @param {Uint8Array} buf - The byte array to encode.
 * @returns {string} Base64-encoded string.
 */
function _bufToBase64(buf) {
  var binary = '';
  for (var i = 0; i < buf.length; i++) {
    binary += String.fromCharCode(buf[i]);
  }
  return btoa(binary);
}

/**
 * hashPassword(password)
 * Hashes a plaintext password using PBKDF2 with a random salt.
 * Returns a combined "salt:hash" string (both base64-encoded) for storage.
 *
 * Uses 100 000 iterations of PBKDF2 with SHA-256 and a 16-byte salt,
 * producing a 256-bit derived key. This provides strong protection
 * against offline brute-force attacks on the stored password data.
 *
 * @param {string} password - The plaintext password to hash.
 * @returns {Promise<string>} "base64(salt):base64(hash)" combined string.
 */
function hashPassword(password) {
  var salt = crypto.getRandomValues(new Uint8Array(16));
  return crypto.subtle.importKey('raw', new TextEncoder().encode(password), 'PBKDF2', false, ['deriveBits'])
    .then(function(key) {
      return crypto.subtle.deriveBits(
        { name: 'PBKDF2', salt: salt, iterations: PBKDF2_ITERATIONS, hash: 'SHA-256' },
        key,
        256
      );
    })
    .then(function(hashBuffer) {
      var hashArray = new Uint8Array(hashBuffer);
      var saltB64 = _bufToBase64(salt);
      var hashB64 = _bufToBase64(hashArray);
      return saltB64 + ':' + hashB64;
    });
}

/**
 * verifyPassword(password, storedString)
 * Verifies a plaintext password against a stored "salt:hash" string
 * produced by hashPassword(). If the stored string is in legacy plaintext
 * format (no colon separator), falls back to direct string comparison
 * for backwards compatibility.
 *
 * @param {string} password     - The plaintext password to check.
 * @param {string} storedString - The stored "salt:hash" or legacy plaintext.
 * @returns {Promise<boolean>} True if the password matches.
 */
function verifyPassword(password, storedString) {
  if (!storedString) return Promise.resolve(false);
  if (storedString.indexOf(':') === -1) {
    return Promise.resolve(storedString === password);
  }
  var parts = storedString.split(':');
  var saltB64 = parts[0];
  var storedHashB64 = parts.slice(1).join(':');
  var salt;
  try {
    var saltBinary = atob(saltB64);
    salt = new Uint8Array(saltBinary.length);
    for (var i = 0; i < saltBinary.length; i++) {
      salt[i] = saltBinary.charCodeAt(i);
    }
  } catch (e) {
    return Promise.resolve(false);
  }
  return crypto.subtle.importKey('raw', new TextEncoder().encode(password), 'PBKDF2', false, ['deriveBits'])
    .then(function(key) {
      return crypto.subtle.deriveBits(
        { name: 'PBKDF2', salt: salt, iterations: PBKDF2_ITERATIONS, hash: 'SHA-256' },
        key,
        256
      );
    })
    .then(function(hashBuffer) {
      var hashArray = new Uint8Array(hashBuffer);
      var computedB64 = _bufToBase64(hashArray);
      return computedB64 === storedHashB64;
    })
    .catch(function() {
      return false;
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
      return s.email && email && s.email.toLowerCase() === email.toLowerCase();
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
 * Uses optimistic concurrency control to prevent race conditions.
 *
 * @param {string} caseId     - Student's Case ID. e.g. 'CASE-00001'
 * @param {string} lessonId   - e.g. 'lesson-1'
 * @param {string} chapterId  - e.g. 'chapter-3'
 * @returns {Promise<void>}
 */
async function saveChapterRead(caseId, lessonId, chapterId) {
  // Create a unique key for this specific read operation to prevent duplicates
  const readKey = `${lessonId}::${chapterId}`;
  
  const progress = await getProgress(caseId) || { caseId: caseId };
  
  // Ensure the nesting exists to avoid "cannot set property of undefined" errors
  if (!progress.chaptersRead) progress.chaptersRead = {};
  if (!progress.chaptersRead[lessonId]) progress.chaptersRead[lessonId] = [];
  
  // Check for duplicate using binary search on sorted array (more efficient than includes)
  const chapterArray = progress.chaptersRead[lessonId];
  let left = 0;
  let right = chapterArray.length - 1;
  let found = false;
  
  while (left <= right) {
    const mid = Math.floor((left + right) / 2);
    if (chapterArray[mid] === chapterId) {
      found = true;
      break;
    } else if (chapterArray[mid] < chapterId) {
      left = mid + 1;
    } else {
      right = mid - 1;
    }
  }
  
  // Only add the chapter if it isn't already recorded
  if (!found) {
    // Insert in sorted order for efficient duplicate checking
    chapterArray.push(chapterId);
    chapterArray.sort();
  }
  
  // Save the updated progress record
  // NOTE (2026-05-22): Removed the "optimistic concurrency control" code that
  // was added in a previous session. It used Date.now() comparisons that could
  // never match (Date.now() returns a new timestamp on every call), making the
  // revert logic dead code. IndexedDB put() is atomic per transaction; the
  // read-modify-write pattern here is sufficient for this use case because
  // JavaScript is single-threaded and IndexedDB serializes transactions.
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
 * Hashes and saves a new admin password to the IndexedDB settings store.
 * The plaintext is never stored — only the PBKDF2 hash (salt:hash format).
 *
 * @param {string} newPassword - The new password to hash and store.
 * @returns {Promise<void>} Resolves when the save is complete.
 */
function setAdminPassword(newPassword) {
  return hashPassword(newPassword).then(function(hashed) {
    return saveSetting('adminPassword', hashed);
  });
}

/**
 * getBugToggles(caseId)
 * Returns the active bug toggles for a given student as an array of
 * semantic bug key strings (e.g. ['status-junior-close', 'future-date-allowed']).
 *
 * If caseId is provided, reads the student record's 'bugs' field (array of
 * admin Lab IDs like ['BUG-03', 'BUG-08']) and translates each via BUG_MAP
 * to the corresponding semantic keys that the Dynamics CRM app checks.
 *
 * If no caseId is provided, falls back to the global 'activeBugs' setting
 * (legacy admin-wide bug config).
 *
 * Returns an empty array if no bugs are configured (all bugs off = safe default).
 *
 * @param {string} [caseId] - Optional student caseId for per-student bugs.
 * @returns {Promise<string[]>} Array of semantic bug key strings.
 */
function getBugToggles(caseId) {
  if (caseId) {
    // Per-student bug lookup
    return getStudent(caseId).then(function(student) {
      if (!student || !student.bugs || !student.bugs.length) return [];
      var adminIds = student.bugs;  // e.g. ['BUG-03', 'BUG-08']
      var _BUG_MAP = (window.BUG_MAP || {});
      var semanticKeys = [];
      adminIds.forEach(function(id) {
        var mapped = _BUG_MAP[id];
        if (mapped && mapped.length) {
          mapped.forEach(function(k) { semanticKeys.push(k); });
        }
      });
      return semanticKeys;
    });
  }

  // Legacy fallback: read global 'activeBugs' setting
  return getSetting('activeBugs').then(function(raw) {
    if (!raw) return [];
    try {
      var parsed = (typeof raw === 'string') ? JSON.parse(raw) : raw;
      if (Array.isArray(parsed)) {
        // Translate admin Lab IDs to semantic keys via BUG_MAP
        var _BUG_MAP = (window.BUG_MAP || {});
        var semanticKeys = [];
        parsed.forEach(function(id) {
          var mapped = _BUG_MAP[id];
          if (mapped && mapped.length) {
            mapped.forEach(function(k) { semanticKeys.push(k); });
          }
        });
        return semanticKeys;
      }
      return [];
    } catch (e) {
      return [];
    }
  });
}


// ── SECTION 8: COURSE FUNCTIONS ─────────────────────────────────────────────
// Course definitions are stored in the 'courses' IndexedDB store.
// Each course record contains the full module/sub-module structure, metadata,
// and quiz references. Courses are seeded from data/content.js on first load.

function getCourse(courseId) { return _get('courses', courseId); }
function getAllCourses() { return _getAll('courses'); }
function saveCourse(courseObject) { return _put('courses', courseObject); }

/**
 * getDefaultCourses()
 * Returns the built-in course definitions from data/content.js.
 * These are the "factory default" courses that ship with the platform.
 * Admin can override individual course fields via the admin panel.
 *
 * @returns {Array} Array of course definition objects.
 */
function getDefaultCourses() {
  // COURSE_DEFINITIONS is defined in data/content.js.
  // If it's not loaded (old page still using the file), return an empty array.
  if (typeof COURSE_DEFINITIONS !== 'undefined' && Array.isArray(COURSE_DEFINITIONS)) {
    return COURSE_DEFINITIONS;
  }
  return [];
}

/**
 * seedCourses()
 * Ensures all built-in courses from content.js exist in IndexedDB with
 * the latest module definitions. Overwrites existing course records so
 * that when new modules or sub-modules are added to COURSE_DEFINITIONS,
 * existing students see them too (not just newly enrolled students).
 *
 * Only the course structure (modules, sub-modules) is overwritten.
 * Per-student data (enrollments, progress, quiz results) is untouched.
 * Admin-edited fields like certificate issuer name are stored separately
 * in the content settings store, not in the course object.
 *
 * @returns {Promise<void>} Resolves once all courses are up to date.
 */
async function seedCourses() {
  var defaults = getDefaultCourses();
  if (defaults.length === 0) return;  // No built-in courses to seed

  for (var i = 0; i < defaults.length; i++) {
    var course = defaults[i];
    await saveCourse(course);  // Always overwrite — keeps course structure current
  }
}


// ── SECTION 9: ENROLLMENT FUNCTIONS ─────────────────────────────────────────
// Enrollments track which students are in which courses.
// Key is a compound string: `${caseId}::${courseId}`.
// This structure allows fast lookups by student or by course.

/**
 * enrollStudent(caseId, courseId)
 * Creates an enrollment record linking a student to a course.
 * Does nothing if the student is already enrolled (idempotent).
 * Also seeds the course's initial progress entry.
 *
 * @param {string} caseId   - Student's Case ID. e.g. 'CASE-00001'
 * @param {string} courseId - Course ID. e.g. 'agile-scrum-dev'
 * @returns {Promise<boolean>} True if enrolled, false if already enrolled.
 */
async function enrollStudent(caseId, courseId) {
  var enrollmentId = caseId + '::' + courseId;
  var existing = await _get('enrollments', enrollmentId);
  if (existing) return false;  // Already enrolled — no-op

  var enrollment = {
    enrollmentId: enrollmentId,
    caseId:       caseId,
    courseId:     courseId,
    enrolledDate: new Date().toISOString(),
    completedDate: null,
    status:       'active',  // active, completed, dropped
  };

  await _put('enrollments', enrollment);

  // Seed initial progress entry for this course
  await initCourseProgress(caseId, courseId);
  return true;
}

/**
 * getEnrollments(caseId)
 * Returns all enrollment records for a given student.
 * Used by portal.html to show "My Learning" section.
 *
 * @param {string} caseId - Student's Case ID.
 * @returns {Promise<Array>} Array of enrollment records.
 */
async function getEnrollments(caseId) {
  var all = await _getAll('enrollments');
  // Filter by matching caseId — IndexedDB doesn't support secondary indexes natively
  // without creating indices, so we filter in JS. Performance is fine for <1000 records.
  return all.filter(function(e) { return e.caseId === caseId; });
}

/**
 * getEnrollment(caseId, courseId)
 * Returns a single enrollment record, or null if the student is not enrolled.
 *
 * @param {string} caseId   - Student's Case ID.
 * @param {string} courseId - Course ID.
 * @returns {Promise<Object|null>} The enrollment record, or null.
 */
function getEnrollment(caseId, courseId) {
  return _get('enrollments', caseId + '::' + courseId);
}

/**
 * getAllEnrollments()
 * Returns every enrollment record across all students and courses.
 * Used by the admin dashboard for multi-course reporting.
 *
 * @returns {Promise<Array>} Array of all enrollment records.
 */
function getAllEnrollments() { return _getAll('enrollments'); }

/**
 * saveEnrollment(enrollmentData)
 * Creates or updates an enrollment record. Used during demo login to enroll
 * the demo student in the configured course.
 *
 * @param {Object} enrollmentData - Enrollment object with enrollmentId, caseId, courseId, etc.
 * @returns {Promise<void>} Resolves when the enrollment is saved.
 */
function saveEnrollment(enrollmentData) {
  return _put('enrollments', enrollmentData);
}

/**
 * completeCourse(caseId, courseId)
 * Marks a course as completed and records the completion date.
 * Called when the student passes the final assessment.
 *
 * @param {string} caseId   - Student's Case ID.
 * @param {string} courseId - Course ID.
 * @returns {Promise<void>}
 */
async function completeCourse(caseId, courseId) {
  var enrollment = await getEnrollment(caseId, courseId);
  if (!enrollment) return;  // Not enrolled — nothing to complete

  enrollment.status = 'completed';
  enrollment.completedDate = new Date().toISOString();
  return _put('enrollments', enrollment);
}

/**
 * saveEnrollmentModules(caseId, courseId, assignedModules)
 * Restricts a student's course access to specific modules.
 * Pass an empty array or null to give full access to all modules.
 * Storage happens inside the existing enrollment record.
 *
 * @param {string} caseId          - Student's Case ID.
 * @param {string} courseId        - Course ID.
 * @param {string[]|null} assignedModules - Array of moduleIds, or null for full access.
 * @returns {Promise<void>}
 */
async function saveEnrollmentModules(caseId, courseId, assignedModules) {
  var enrollment = await getEnrollment(caseId, courseId);
  if (!enrollment) return;  // Not enrolled — nothing to restrict

  if (assignedModules && Array.isArray(assignedModules) && assignedModules.length > 0) {
    enrollment.assignedModules = assignedModules;
  } else {
    // null/empty = full access to all modules
    delete enrollment.assignedModules;
  }
  return _put('enrollments', enrollment);
}

/**
 * unenrollStudent(caseId, courseId)
 * Removes a student's enrollment and progress for a specific course.
 * Does NOT delete the student record itself.
 *
 * @param {string} caseId   - Student's Case ID.
 * @param {string} courseId - Course ID.
 * @returns {Promise<void>}
 */
async function unenrollStudent(caseId, courseId) {
  var enrollmentId = caseId + '::' + courseId;

  // Remove enrollment record
  await _delete('enrollments', enrollmentId);

  // Clean up progress for this course
  var progress = await getProgress(caseId);
  if (progress && progress.courses && progress.courses[courseId]) {
    delete progress.courses[courseId];
    await saveProgress(progress);
  }
}


// ── SECTION 10: MULTI-COURSE PROGRESS FUNCTIONS ─────────────────────────────
// Progress for the multi-course platform is stored inside the existing progress
// record under the `courses` key. Each course gets its own sub-object keyed by
// courseId. This keeps backward compatibility — the old QA Onboarding fields
// (lessonsComplete, quizResults) remain untouched.

/**
 * initCourseProgress(caseId, courseId)
 * Seeds a blank progress sub-object for a course inside the student's
 * existing progress record. Called automatically by enrollStudent().
 * Safe to call multiple times — only creates if not already present.
 *
 * @param {string} caseId   - Student's Case ID.
 * @param {string} courseId - Course ID.
 * @returns {Promise<void>}
 */
async function initCourseProgress(caseId, courseId) {
  var progress = await getProgress(caseId) || { caseId: caseId };
  if (!progress.courses) progress.courses = {};

  // Only create the entry if it doesn't already exist (preserve existing progress)
  if (!progress.courses[courseId]) {
    progress.courses[courseId] = {
      modulesComplete:    [],
      subModulesComplete: [],
      currentModule:      null,
      currentSubModule:   null,
      quizResults:        {},
      certificateEarned:  false,
      enrolledDate:       new Date().toISOString(),
      lastActivity:       new Date().toISOString(),
    };
  }

  return saveProgress(progress);
}

/**
 * getCourseProgress(caseId, courseId)
 * Reads the progress sub-object for a specific course from the student's
 * overall progress record. Returns null if no progress exists yet.
 *
 * @param {string} caseId   - Student's Case ID.
 * @param {string} courseId - Course ID.
 * @returns {Promise<Object|null>} The course progress object, or null.
 */
async function getCourseProgress(caseId, courseId) {
  var progress = await getProgress(caseId);
  if (!progress || !progress.courses || !progress.courses[courseId]) return null;
  return progress.courses[courseId];
}

/**
 * saveCourseProgress(caseId, courseId, courseProgress)
 * Saves the full progress sub-object for a specific course.
 * Overwrites the existing entry for that courseId inside the progress record.
 *
 * @param {string} caseId          - Student's Case ID.
 * @param {string} courseId        - Course ID.
 * @param {Object} courseProgress  - The updated course progress object.
 * @returns {Promise<void>}
 */
async function saveCourseProgress(caseId, courseId, courseProgress) {
  var progress = await getProgress(caseId) || { caseId: caseId };
  if (!progress.courses) progress.courses = {};
  progress.courses[courseId] = courseProgress;
  progress.lastActivity = new Date().toISOString();
  return saveProgress(progress);
}

/**
 * markSubModuleComplete(caseId, courseId, subModuleId)
 * Marks a single sub-module as completed for a student in a course.
 * Safe to call multiple times — only adds if not already present.
 * Also updates currentSubModule to the next uncompleted one.
 *
 * @param {string} caseId       - Student's Case ID.
 * @param {string} courseId     - Course ID.
 * @param {string} subModuleId  - e.g. 'mod-1-1'
 * @returns {Promise<void>}
 */
async function markSubModuleComplete(caseId, courseId, subModuleId) {
  var progress = await getCourseProgress(caseId, courseId);
  if (!progress) return;  // Not enrolled — nothing to mark

  // Only add if not already marked (prevent duplicates from page refreshes)
  if (!progress.subModulesComplete.includes(subModuleId)) {
    progress.subModulesComplete.push(subModuleId);
  }

  progress.lastActivity = new Date().toISOString();
  return saveCourseProgress(caseId, courseId, progress);
}

/**
 * markModuleComplete(caseId, courseId, moduleId)
 * Marks an entire module as completed.
 * This is usually called after the module quiz is passed.
 *
 * @param {string} caseId   - Student's Case ID.
 * @param {string} courseId - Course ID.
 * @param {string} moduleId - e.g. 'mod-1'
 * @returns {Promise<void>}
 */
async function markModuleComplete(caseId, courseId, moduleId) {
  var progress = await getCourseProgress(caseId, courseId);
  if (!progress) return;

  if (!progress.modulesComplete.includes(moduleId)) {
    progress.modulesComplete.push(moduleId);
  }

  progress.lastActivity = new Date().toISOString();
  return saveCourseProgress(caseId, courseId, progress);
}

/**
 * saveCourseQuizResults(caseId, courseId, moduleId, results)
 * Saves quiz results for a specific module within a course.
 * Each call overwrites the results for that module (retakes replace previous).
 *
 * @param {string} caseId    - Student's Case ID.
 * @param {string} courseId  - Course ID.
 * @param {string} moduleId  - e.g. 'mod-1'
 * @param {Object} results   - { score, maxScore, percentage, passed, completedAt }
 * @returns {Promise<void>}
 */
async function saveCourseQuizResults(caseId, courseId, moduleId, results) {
  var progress = await getCourseProgress(caseId, courseId);
  if (!progress) return;

  progress.quizResults[moduleId] = results;
  progress.lastActivity = new Date().toISOString();
  return saveCourseProgress(caseId, courseId, progress);
}

/**
 * deleteStudent(caseId)
 * Permanently removes a student and all associated data:
 * - Student record from students store
 * - Progress record from progress store
 * - All enrollment records from enrollments store
 * - Assignment record from assignments store
 *
 * @param {string} caseId - The student's case ID to delete.
 * @returns {Promise<void>}
 */
async function deleteStudent(caseId) {
  // 1. Remove all enrollments for this student
  var enrollments = await getEnrollments(caseId);
  for (var i = 0; i < enrollments.length; i++) {
    var enrollmentId = caseId + '::' + enrollments[i].courseId;
    await _delete('enrollments', enrollmentId);
  }

  // 2. Remove progress record
  await _delete('progress', caseId);

  // 3. Remove assignment record (legacy)
  await _delete('assignments', caseId);

  // 4. Remove student record
  await _delete('students', caseId);
}

/**
 * awardCourseCertificate(caseId, courseId)
 * Marks a course certificate as earned for the student.
 * Called when the student passes the final course exam.
 * Uses atomic transaction to ensure consistency between course-level and top-level records.
 *
 * @param {string} caseId   - Student's Case ID.
 * @param {string} courseId - Course ID.
 * @returns {Promise<void>}
 */
async function awardCourseCertificate(caseId, courseId) {
  var progress = await getCourseProgress(caseId, courseId);
  if (!progress) return;

  // Write both field names so every page works regardless of which it reads.
  // certificate.html reads certificateAwarded; admin dashboard reads certificateEarned.
  // Dual-write required per CLAUDE.md gotcha — awardCourseCertificate() was missing this.
  progress.certificateAwarded = true;
  progress.certificateEarned  = true;
  progress.certificateDate = new Date().toISOString();
  progress.lastActivity = new Date().toISOString();
  await saveCourseProgress(caseId, courseId, progress);

  // Also mirror certificate fields to the TOP-LEVEL progress record for
  // backward compatibility. certificate.html (legacy path and
  // courseId === 'qa-onboarding' path) reads from top-level fields.
  // Use a transaction-like approach to ensure consistency
  var fullProgress = await getProgress(caseId);
  if (fullProgress) {
    fullProgress.certificateAwarded = true;
    fullProgress.certificateEarned  = true;
    fullProgress.certificateDate    = progress.certificateDate;
    fullProgress.lastActivity       = progress.lastActivity;
    await saveProgress(fullProgress);
  }

  // Also mark the overall enrollment as completed
  await completeCourse(caseId, courseId);
}
