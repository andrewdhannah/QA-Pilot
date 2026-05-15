/**
 * =============================================================================
 * app.js — Shared Application Utilities
 * =============================================================================
 * QA Onboarding Training Platform
 *
 * PURPOSE:
 * This file contains shared helper functions used across multiple pages.
 * Think of it as the "toolbox" — individual pages use these tools, but the
 * tools themselves are defined here so they're not copy-pasted everywhere.
 *
 * LOAD ORDER:
 * This file should be loaded LAST in your HTML script tags, after all data
 * files, so it can reference functions from students.js, progress.js, etc.
 *
 *   <script src="../data/content.js"></script>
 *   <script src="../data/students.js"></script>
 *   <script src="../data/progress.js"></script>
 *   <script src="../data/assignments.js"></script>
 *   <script src="../data/quiz-questions.js"></script>
 *   <script src="../js/app.js"></script>   ← loads last
 *
 * WHAT'S IN HERE:
 * - Session management (who is logged in right now)
 * - Toast notification helper
 * - Form validation helpers
 * - Date utilities
 * - Navigation helpers
 *
 * TODO (Sprint 1):
 * - Complete session management
 * - Complete toast helper
 * - Complete form validation helpers
 *
 * =============================================================================
 */


// ── SECTION 1: SESSION MANAGEMENT ─────────────────────────────────────────────
/*
 * Session = who is currently logged in.
 * We store a minimal session object in localStorage under 'qa_session'.
 * It only holds the Case ID — the full student record is fetched from
 * students.js using that ID when needed.
 *
 * SESSION OBJECT SCHEMA:
 * {
 *   caseId:   string  — The logged-in student's Case ID.
 *   role:     string  — 'junior' or 'senior' (copied at login for quick access)
 *   loginTime: string — ISO datetime of when the session started.
 * }
 */

// The key used to store the student session in sessionStorage.
// sessionStorage automatically clears when the browser tab closes —
// this is intentional. Students should not stay "logged in" across sessions.
const SESSION_STORAGE_KEY = 'qa_session';

/**
 * getSession()
 * Returns the current student session object, or null if no one is logged in.
 * Reads from sessionStorage, which clears automatically when the tab closes.
 *
 * @returns {Object|null} Session object with caseId, role, loginTime — or null.
 */
function getSession() {
  const raw = sessionStorage.getItem(SESSION_STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

/**
 * startSession(student)
 * Creates a student session after a successful login.
 * Stores minimal data in sessionStorage — just enough to identify the user.
 * Full student details (name, etc.) are loaded from IndexedDB when needed.
 *
 * Session object schema:
 *   { caseId: "CASE-00001", role: "junior", loginTime: "ISO string" }
 *
 * @param {Object} student - The authenticated student object from db.js.
 */
function startSession(student) {
  const session = {
    caseId:    student.caseId,
    role:      student.role,
    loginTime: new Date().toISOString(),
  };
  sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
}

/**
 * endSession()
 * Clears the student session. Called on logout.
 * Also removes any admin session, in case both were active.
 */
function endSession() {
  sessionStorage.removeItem(SESSION_STORAGE_KEY);
  sessionStorage.removeItem('qa_admin');
}

/**
 * requireLogin()
 * Page guard — call this at the top of any student page.
 * If no valid session exists, redirects to the login page and returns null.
 * If a session exists, returns the session object so the page can use it.
 *
 * WHY relative path ("index.html") not absolute ("/index.html"):
 * Absolute paths break when the app is opened as a local file (file:// URLs).
 * Relative paths work both locally and on SharePoint.
 *
 * @returns {Object|null} The session object, or null (redirect already fired).
 */
function requireLogin() {
  const session = getSession();
  if (!session) {
    window.location.href = 'index.html';
    return null;
  }
  return session;
}

/**
 * requireAdmin()
 * Page guard for admin pages — call at the top of any admin page.
 * Checks for the admin session flag in sessionStorage.
 * If not set, redirects to the admin login page and returns false.
 *
 * Admin session is set by admin/index.html on successful password entry:
 *   sessionStorage.setItem('qa_admin', 'true')
 *
 * @returns {boolean} true if admin session is valid, false (redirect fired) if not.
 */
function requireAdmin() {
  const isAdmin = sessionStorage.getItem('qa_admin');
  if (!isAdmin) {
    window.location.href = 'index.html';  // relative — works in admin/ subfolder
    return false;
  }
  return true;
}


// ── SECTION 2: TOAST NOTIFICATIONS ────────────────────────────────────────────

/**
 * showToast(message, type, duration)
 * Displays a toast notification at the top-right corner of the page.
 * The toast fades in, stays for `duration` ms, then fades out.
 *
 * Requires a <div id="toast" class="toast"> element in the page HTML.
 * Add the variant class via the `type` parameter.
 *
 * @param {string} message  - The message to display.
 * @param {string} type     - One of: 'default' | 'success' | 'error'
 * @param {number} duration - How long to show the toast in ms. Default: 3000.
 */
function showToast(message, type = 'default', duration = 3000) {
  const toast = document.getElementById('toast');
  if (!toast) {
    // If there's no toast element on this page, just log it and continue
    console.warn('showToast: no element with id="toast" found on this page.');
    return;
  }

  // Set the message text
  toast.textContent = message;

  // Remove any previous type classes before adding the new one
  toast.classList.remove('toast-success', 'toast-error');
  if (type === 'success') toast.classList.add('toast-success');
  if (type === 'error')   toast.classList.add('toast-error');

  // Make it visible (CSS transition handles the fade-in)
  toast.classList.add('toast-visible');

  // After `duration` ms, fade it out
  setTimeout(() => {
    toast.classList.remove('toast-visible');
  }, duration);
}


// ── SECTION 3: FORM VALIDATION HELPERS ────────────────────────────────────────

/**
 * showFieldError(fieldElement, errorElement, message)
 * Marks a form field as invalid and shows its error message.
 * Called by validation logic when a field fails.
 *
 * @param {HTMLElement} fieldElement - The input/select/textarea that failed.
 * @param {HTMLElement} errorElement - The <span> or <p> that holds the error text.
 * @param {string}      message     - The error message to display.
 */
function showFieldError(fieldElement, errorElement, message) {
  fieldElement.classList.add('is-invalid');
  errorElement.textContent = message;
  errorElement.classList.add('visible');
}

/**
 * clearFieldError(fieldElement, errorElement)
 * Removes the invalid state from a form field.
 * Called when a field passes validation, or when the user starts typing.
 *
 * @param {HTMLElement} fieldElement - The input/select/textarea to clear.
 * @param {HTMLElement} errorElement - The error message element to hide.
 */
function clearFieldError(fieldElement, errorElement) {
  fieldElement.classList.remove('is-invalid');
  errorElement.textContent = '';
  errorElement.classList.remove('visible');
}

/**
 * scrollToFirstError()
 * Scrolls the page to the first element with the class .is-invalid.
 * Called after validation runs so the user doesn't have to hunt for errors.
 */
function scrollToFirstError() {
  const firstError = document.querySelector('.is-invalid');
  if (firstError) {
    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    firstError.focus(); // Move focus to the field for accessibility
  }
}


// ── SECTION 4: DATE UTILITIES ──────────────────────────────────────────────────

/**
 * getTodayString()
 * Returns today's date as a YYYY-MM-DD string.
 * Used for default date values and validation comparisons.
 *
 * @returns {string} e.g. "2026-05-11"
 */
function getTodayString() {
  return new Date().toISOString().split('T')[0];
}

/**
 * getNowTimestamp()
 * Returns the current date and time as a formatted string.
 * Used for LAST UPDATED display in the sidebar.
 *
 * @returns {string} e.g. "2026-05-11 14:32"
 */
function getNowTimestamp() {
  const now = new Date();
  const date = now.toISOString().split('T')[0];
  const hours   = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  return `${date} ${hours}:${minutes}`;
}

/**
 * isFutureDate(dateString)
 * Checks whether a date string represents a future date.
 * Used to validate the Date Opened field.
 *
 * @param {string} dateString - A date in YYYY-MM-DD format.
 * @returns {boolean} true if the date is in the future, false if today or past.
 */
function isFutureDate(dateString) {
  const inputDate = new Date(dateString);
  const today     = new Date(getTodayString());
  // Compare date only — strip out time component by using date-only strings
  return inputDate > today;
}


// ── SECTION 5: NAVIGATION HELPERS ─────────────────────────────────────────────

/**
 * navigateTo(path)
 * Redirects the browser to a given path.
 * Centralised here so we can add transition effects later without
 * updating every page that navigates.
 *
 * @param {string} path - The path to navigate to. e.g. "/index.html"
 */
function navigateTo(path) {
  window.location.href = path;
}
