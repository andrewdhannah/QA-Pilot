/**
 * =============================================================================
 * i18n.js — Internationalisation Engine
 * =============================================================================
 * QA Pilot — Bilingual (EN/FR) Translation System
 *
 * PURPOSE:
 * Provides the __() translation function and language management for the entire
 * platform. Supports English (en) and French (fr) — Québec French where there
 * is a distinction.
 *
 * HOW IT WORKS:
 * 1. LANG_EN and LANG_FR are defined in lang-en.js and lang-fr.js respectively.
 * 2. i18n.js initialises by reading the saved language preference from
 *    localStorage under 'qa_lang'. Defaults to 'en'.
 * 3. The active language dictionary is referenced via the global `LANG` variable.
 * 4. The __('key') function looks up a key in the active dictionary. If the key
 *    is missing, it returns the key itself (graceful fallback).
 * 5. Simple interpolation: __('Hello {0}', name) substitutes {0} with the first
 *    argument, {1} with the second, etc.
 * 6. Course content localisation: getLocalizedContent() returns French course
 *    content when available, falling back to English COURSE_CONTENT.
 *
 * LANGUAGE TOGGLE:
 * A small EN/FR toggle button is rendered by renderLangToggle(container).
 * On click, it saves the choice to localStorage and reloads the page so all
 * strings re-render with the new language.
 *
 * SCRIPT LOAD ORDER (in every page):
 *   <script src="data/content.js"></script>
 *   <script src="data/quiz-questions.js"></script>
 *   <script src="js/db.js"></script>
 *   <script src="js/app.js"></script>
 *   <script src="js/i18n.js"></script>       ← i18n engine
 *   <script src="js/lang-en.js"></script>     ← English strings
 *   <script src="js/lang-fr.js"></script>     ← French strings
 *
 * =============================================================================
 */

// ── SUPPORTED LANGUAGES ────────────────────────────────────────────────────────

var LANGUAGES = {
  en: { label: 'EN', full: 'English' },
  fr: { label: 'FR', full: 'Fran\u00e7ais' },
};

// Active language code (initialised by initI18n)
var currentLang = 'en';

// Active language dictionary — re-assigned on language switch
var LANG = {};

// Storage key
var QA_LANG_KEY = 'qa_lang';

// ── HTML ESCAPE UTILITY FOR SAFE INTERPOLATION ────────────────────────────────
/**
 * escapeHtml(str)
 * Escapes HTML special characters to prevent XSS attacks in interpolated strings.
 * Only escapes the dangerous characters that could break the page.
 *
 * @param {string} str - The string to escape.
 * @returns {string} Escaped string safe for HTML interpolation.
 */
function escapeHtml(str) {
  if (typeof str !== 'string') {
    return String(str);
  }
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}


// ── CORE TRANSLATION FUNCTION ──────────────────────────────────────────────────

/**
 * __(key, ...args)
 * Translates the given key using the active language dictionary.
 * If the key is not found, returns the key itself (graceful fallback).
 * Supports {0}, {1}, ... placeholder substitution.
 * 
 * SECURITY: All interpolated arguments are automatically HTML-escaped to prevent
 * XSS attacks. Never pass untrusted user input directly as translation arguments.
 *
 * @param {string} key - The translation key.
 * @param {...any} args - Optional values to substitute into {0}, {1}, etc.
 *                        All arguments are HTML-escaped for safety.
 * @returns {string} The translated string, or the key if not found.
 *
 * @example
 *   __('sign_in')           → "Sign in" / "Se connecter"
 *   __('welcome_user', name) → "Welcome, Jane!" / "Bienvenue, Jane !"
 *   __('error_msg', userInput) → "Error: X" (X is escaped)
 */
function __(key) {
  if (!key) return '';

  var str = LANG[key];
  if (str === undefined || str === null) {
    // Fallback: try English
    if (typeof LANG_EN !== 'undefined' && LANG_EN[key]) {
      str = LANG_EN[key];
    }
  }
  if (str === undefined || str === null) {
    // SECURITY FIX (2026-05-22): Escape the fallback key in case it contains
    // HTML from a dynamic/user-controlled source. Translation keys are normally
    // hardcoded, but this defends against the edge case where a key is built
    // from untrusted input (e.g. __('error_' + userInput)).
    str = escapeHtml(key);
  }

   // Substitute {0}, {1}, etc. with positional arguments
   // NOTE: args are escaped to prevent XSS when user data is passed to translations
   var args = Array.prototype.slice.call(arguments, 1);
   if (args.length > 0) {
     for (var i = 0; i < args.length; i++) {
       str = String(str).replace(new RegExp('\\{' + i + '\\}', 'g'), escapeHtml(args[i]));
     }
   }

   return str;
}


// ── LANGUAGE MANAGEMENT ────────────────────────────────────────────────────────

/**
 * getLanguage()
 * Returns the current active language code.
 *
 * @returns {string} 'en' or 'fr'
 */
function getLanguage() {
  return currentLang;
}

/**
 * getLanguageLabel()
 * Returns the short label for the current language (e.g. 'EN').
 *
 * @returns {string} e.g. 'EN' or 'FR'
 */
function getLanguageLabel() {
  return LANGUAGES[currentLang] ? LANGUAGES[currentLang].label : 'EN';
}

/**
 * getOtherLanguage()
 * Returns the code of the language NOT currently active.
 *
 * @returns {string} 'en' or 'fr'
 */
function getOtherLanguage() {
  return currentLang === 'en' ? 'fr' : 'en';
}

/**
 * getOtherLanguageLabel()
 * Returns the short label of the non-active language.
 *
 * @returns {string} e.g. 'FR' or 'EN'
 */
function getOtherLanguageLabel() {
  var other = getOtherLanguage();
  return LANGUAGES[other] ? LANGUAGES[other].label : 'FR';
}

/**
 * setLanguage(lang, reload)
 * Switches the active language, saves to localStorage, and optionally reloads
 * the page so all strings re-render.
 *
 * @param {string} lang - 'en' or 'fr'
 * @param {boolean} doReload - Whether to reload the page after switching (default: true)
 */
function setLanguage(lang, doReload) {
  if (!LANGUAGES[lang]) return;

  currentLang = lang;
  localStorage.setItem(QA_LANG_KEY, lang);

  // Update the active dictionary
  if (lang === 'fr' && typeof LANG_FR !== 'undefined') {
    LANG = LANG_FR;
  } else {
    LANG = LANG_EN;
  }

  // Dispatch a custom event so pages can react without a reload
  var event;
  try {
    event = new CustomEvent('languageChanged', { detail: { lang: lang } });
  } catch (e) {
    // Fallback for older browsers
    event = document.createEvent('CustomEvent');
    event.initCustomEvent('languageChanged', true, false, { lang: lang });
  }
  document.dispatchEvent(event);

  // Reload the page to re-render all strings (cleanest for file://)
  if (doReload !== false) {
    window.location.reload();
  }
}


// ── INITIALISATION ─────────────────────────────────────────────────────────────

/**
 * initI18n()
 * Initialises the i18n system. Call after LANG_EN and LANG_FR are loaded.
 * Reads saved language preference from localStorage, defaults to 'en'.
 */
function initI18n() {
  var saved = localStorage.getItem(QA_LANG_KEY) || 'en';

  // Validate saved value — fall back to 'en' if invalid
  if (saved !== 'en' && saved !== 'fr') {
    saved = 'en';
  }

  currentLang = saved;

  // Set the active dictionary
  if (saved === 'fr' && typeof LANG_FR !== 'undefined') {
    LANG = LANG_FR;
  } else {
    LANG = LANG_EN;
  }

  // Update the <html> lang attribute
  document.documentElement.setAttribute('lang', saved);

  // Update <title> if it uses translatable content
  var titleEl = document.querySelector('title');
  if (titleEl && LANG['page_title_' + window.location.pathname.split('/').pop()]) {
    titleEl.textContent = LANG['page_title_' + window.location.pathname.split('/').pop()];
  }
}


// ── LANGUAGE TOGGLE WIDGET ─────────────────────────────────────────────────────

/**
 * renderLangToggle(containerId)
 * Renders the EN/FR language toggle button inside the given container element.
 * The toggle shows the OTHER language (clicking it switches to that language).
 *
 * @param {string} containerId - The id of the container element.
 */
function renderLangToggle(containerId) {
  var container = document.getElementById(containerId);
  if (!container) {
    // Try as a fallback — maybe it's a CSS selector
    container = document.querySelector(containerId);
  }
  if (!container) return;

  var otherLabel = getOtherLanguageLabel();
  var otherCode  = getOtherLanguage();
  var currentLabel = getLanguageLabel();

  container.innerHTML =
    '<button class="lang-toggle" onclick="setLanguage(\'' + otherCode + '\')" ' +
      'title="Switch to ' + LANGUAGES[otherCode].full + '" ' +
      'aria-label="Switch language to ' + LANGUAGES[otherCode].full + '">' +
      '<span class="lang-toggle-current">' + currentLabel + '</span>' +
      '<span class="lang-toggle-divider">|</span>' +
      '<span class="lang-toggle-other">' + otherLabel + '</span>' +
    '</button>';
}


// ── LOCALISED COURSE CONTENT ───────────────────────────────────────────────────

/**
 * getLocalizedContent(courseId, subModuleId)
 * Returns course content in the active language.
 * - If French is active and French content exists, returns LANG_CONTENT_FR.
 * - Otherwise falls back to COURSE_CONTENT (English, the default).
 *
 * @param {string} courseId    - The course ID (e.g. 'qa-onboarding')
 * @param {string} subModuleId - The sub-module ID (e.g. 'mod-1-1')
 * @returns {string|null} HTML content string, or null if not found.
 */
function getLocalizedContent(courseId, subModuleId) {
  // French-specific course content
  if (currentLang === 'fr' && typeof LANG_CONTENT_FR !== 'undefined') {
    if (LANG_CONTENT_FR[courseId] && LANG_CONTENT_FR[courseId][subModuleId]) {
      return LANG_CONTENT_FR[courseId][subModuleId];
    }
  }

  // Fall back to the default COURSE_CONTENT (English)
  if (typeof COURSE_CONTENT !== 'undefined' &&
      COURSE_CONTENT[courseId] &&
      COURSE_CONTENT[courseId][subModuleId]) {
    return COURSE_CONTENT[courseId][subModuleId];
  }

  return null;
}


// ── AUTO-INIT ──────────────────────────────────────────────────────────────────
// Initialise i18n as soon as the script loads (LANG_EN and LANG_FR are defined
// in separate files that must be loaded AFTER this one).
// The actual init is deferred to happen after both lang files are loaded.
// Each page should call initI18n() explicitly after all scripts are loaded.
