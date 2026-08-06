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
 * For demo accounts, also resets their progress/enrollment based on settings.
 */
function endSession() {
  var session = getSession();

  // If logging out a demo account, reset their data based on configured reset mode
  if (session) {
    resetDemoAccountIfNeeded(session.caseId).catch(function(error) {
      console.error('Error resetting demo account:', error);
    });
  }

  sessionStorage.removeItem(SESSION_STORAGE_KEY);
  sessionStorage.removeItem('qa_admin');
}

/**
 * isDemoAccount(caseId)
 * Checks if a given case ID matches the configured demo account.
 * @param {string} caseId - The student's case ID
 * @returns {Promise<boolean>} true if this is the demo account
 */
async function isDemoAccount(caseId) {
  console.log('[isDemoAccount] Checking caseId:', caseId);

  if (!caseId) {
    console.log('[isDemoAccount] caseId is empty, returning false');
    return false;
  }

  try {
    // Demo account is identified by email: demo@qapilot.com
    // Fetch the student record to check their email
    var student = await getStudent(caseId);
    console.log('[isDemoAccount] Retrieved student:', student ? { caseId: student.caseId, name: student.name, email: student.email } : 'null');

    var isDemo = student && student.email === 'demo@qapilot.com';
    console.log('[isDemoAccount] Student email:', student ? student.email : 'N/A', '→ isDemo:', isDemo);

    return isDemo;
  } catch (e) {
    console.warn('[isDemoAccount] Error checking if demo account:', e);
    return false;
  }
}

/**
 * resetDemoAccountIfNeeded(caseId)
 * If the logging-out user is the demo account, resets their data.
 * Uses the configured reset mode: 'full' (progress+enrollment) or 'progress-only'
 * @param {string} caseId - The student's case ID
 * @returns {Promise<void>}
 */
async function resetDemoAccountIfNeeded(caseId) {
  console.log('[Demo] resetDemoAccountIfNeeded() called for:', caseId);

  var isDemo = await isDemoAccount(caseId);
  console.log('[Demo] isDemoAccount() returned:', isDemo);

  if (!isDemo) {
    console.log('[Demo] Not a demo account, skipping reset');
    return;
  }

  console.log('[Demo] Resetting demo account:', caseId);

  try {
    var resetMode = await getSetting('demoResetMode');
    console.log('[Demo] Retrieved demoResetMode from settings:', resetMode);

    var mode = resetMode || 'full';
    console.log('[Demo] Using reset mode:', mode);

    if (mode === 'full') {
      // Full reset: clear all progress and remove from all courses
      console.log('[Demo] Starting FULL reset for:', caseId);

      // Clear progress record
      var progress = await getProgress(caseId);
      console.log('[Demo] Retrieved progress:', progress ? 'exists' : 'null/undefined');

      if (progress) {
        console.log('[Demo] Progress before reset:', {
          courses: Object.keys(progress.courses || {}).length,
          enrolledCourses: progress.enrolledCourses ? progress.enrolledCourses.length : 0,
          lessonsComplete: progress.lessonsComplete ? progress.lessonsComplete.length : 0
        });

        // Ensure caseId is set (required for IndexedDB key path)
        progress.caseId = caseId;
        // Clear enrollments
        progress.courses = {};
        progress.enrolledCourses = [];
        progress.lessonsComplete = [];
        progress.quizResults = {};
        progress.certificateAwarded = false;
        progress.certificateEarned = false;
        progress.progressData = {};

        console.log('[Demo] Calling saveProgress() with cleared data...');
        await saveProgress(progress);
        console.log('[Demo] saveProgress() returned successfully');
      } else {
        console.log('[Demo] No progress record found to reset');
      }

      // Also delete all enrollments for this demo account
      console.log('[Demo] Clearing enrollments from IndexedDB...');
      try {
        var enrollments = await getEnrollments(caseId); // Get demo account's enrollments
        console.log('[Demo] Found', enrollments.length, 'enrollments to clear');

        for (var i = 0; i < enrollments.length; i++) {
          var courseId = enrollments[i].courseId;
          await unenrollStudent(caseId, courseId);
          console.log('[Demo] Unenrolled from course:', courseId);
        }
      } catch (e) {
        console.warn('[Demo] Could not clear enrollments:', e);
        // Continue with reset even if enrollment clearing fails
      }

      console.log('[Demo] Full reset complete for:', caseId);
    } else if (mode === 'progress-only') {
      // Progress-only reset: clear scores but keep enrollment
      console.log('[Demo] Starting PROGRESS-ONLY reset for:', caseId);
      var progress = await getProgress(caseId);
      console.log('[Demo] Retrieved progress:', progress ? 'exists' : 'null/undefined');

      if (progress) {
        console.log('[Demo] Progress before reset:', {
          courses: Object.keys(progress.courses || {}).length,
          quizResults: Object.keys(progress.quizResults || {}).length
        });

        // Ensure caseId is set (required for IndexedDB key path)
        progress.caseId = caseId;
        progress.quizResults = {};
        progress.progressData = {};
        progress.certificateAwarded = false;
        progress.certificateEarned = false;
        progress.lessonsComplete = [];

        console.log('[Demo] Calling saveProgress() with cleared scores...');
        await saveProgress(progress);
        console.log('[Demo] saveProgress() returned successfully');
        console.log('[Demo] Progress reset complete for:', caseId);
      } else {
        console.log('[Demo] No progress record found to reset');
      }
    } else {
      console.log('[Demo] Unknown reset mode:', mode);
    }
  } catch (error) {
    console.error('[Demo] Error resetting demo account:', error);
    console.error('[Demo] Error stack:', error.stack);
    // Re-throw to allow caller to handle if needed
    throw error;
  }
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
  
  // Check session expiration (24 hours max)
  const sessionAgeMs = Date.now() - new Date(session.loginTime).getTime();
  const MAX_SESSION_AGE_MS = 24 * 60 * 60 * 1000; // 24 hours
  
  if (sessionAgeMs > MAX_SESSION_AGE_MS) {
    // Session expired, clear it and redirect
    endSession();
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

/**
 * initDemoBanner()
 * Shows a prominent demo mode banner if the logged-in user is the demo account
 * and the admin has enabled the banner display.
 * Should be called on pages that support demo mode (portal, courses, certificate, etc.)
 * Creates and injects a banner at the top of the page if conditions are met.
 */
async function initDemoBanner() {
  try {
    var session = getSession();
    if (!session) return;

    var isDemo = await isDemoAccount(session.caseId);
    var showBanner = await getSetting('demoShowBanner');

    if (!isDemo || showBanner === false) return;

    // Check if banner already exists
    if (document.getElementById('demo-banner')) return;

    // Create banner element
    var banner = document.createElement('div');
    banner.id = 'demo-banner';
    banner.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:100;' +
      'background:linear-gradient(90deg, #f97316, #ea580c);color:white;' +
      'padding:12px 20px;text-align:center;font-weight:bold;font-size:14px;' +
      'box-shadow:0 2px 8px rgba(0,0,0,0.15);';
    banner.textContent = '🎬 DEMO MODE — This account will reset on logout';

    document.body.insertBefore(banner, document.body.firstChild);

    // Add margin to the topbar so content doesn't hide behind banner
    // Check for portal, admin, or OS topbars
    var topBar = document.querySelector('.portal-topbar, .topbar, .os-taskbar, header');
    if (topBar && topBar.style) {
      topBar.style.marginTop = '44px';
    }
    // Also add padding to body if no topbar found
    if (!topBar) {
      document.body.style.paddingTop = '44px';
    }
  } catch (error) {
    console.warn('Error initializing demo banner:', error);
  }
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
