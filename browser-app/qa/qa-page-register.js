/**
 * =============================================================================
 * qa-page-register.js — QA Debugger Page Registration
 * =============================================================================
 *
 * PURPOSE:
 * Allows QA-Pilot pages to self-report their identity and context to the
 * debugger's shared data layer. Pages call registerCurrentPage() on load.
 *
 * CONSTRAINTS:
 * - Plain JavaScript only.
 * - No dependencies.
 * - Must run under file://.
 * - Does not modify existing QA Pilot files.
 * - Safe to call multiple times (updates existing record).
 * =============================================================================
 */

(function() {
  'use strict';

  // Prevent double-load
  if (window.QA_PAGE_REGISTER) return;

  // ── DEPENDENCIES ──────────────────────────────────────────────────────────

  if (!window.QA_SCHEMA || !window.QA_DB) {
    console.error('[QA_PAGE_REGISTER] Missing dependencies: QA_SCHEMA or QA_DB');
    return;
  }

  var SCHEMA = window.QA_SCHEMA.SCHEMA;
  var validateRecord = window.QA_SCHEMA.validateRecord;
  var QA_DB = window.QA_DB;

  // ── REGISTRATION LOGIC ────────────────────────────────────────────────────

  /**
   * Registers the current page with the debugger
   * @returns {Promise<Object>} Resolves with the registered page record
   */
  function registerCurrentPage() {
    return _gatherPageMetadata()
      .then(function(pageRecord) {
        // Validate
        var validation = validateRecord(pageRecord, 'PageRecord');
        if (!validation.valid) {
          console.warn('[QA_PAGE_REGISTER] Invalid page record:', validation.errors);
          // Continue anyway - don't break the page
        }
        
        // Save to debugger DB
        return QA_DB.registerPage(pageRecord)
          .then(function() { return pageRecord; });
      })
      .catch(function(error) {
        console.error('[QA_PAGE_REGISTER] Failed to register page:', error);
        // Return a minimal record so the page doesn't break
        return {
          which_page: window.location.pathname,
          page_id: 'unknown',
          registered_at: new Date().toISOString(),
          error: error.message
        };
      });
  }

  /**
   * Gathers metadata about the current page
   * @returns {Promise<Object>} Page record object
   */
  function _gatherPageMetadata() {
    return new Promise(function(resolve) {
      // Basic page info
      var whichPage = window.location.pathname;
      // Remove leading slash and make relative to project root if possible
      if (whichPage.startsWith('/')) {
        whichPage = whichPage.substring(1);
      }
      
      var pageId = '';
      var moduleId = '';
      var lessonId = '';
      var pageTitle = document.title || '';
      var appVersion = '';
      var sessionId = '';
      var appContext = 'standalone';
      var urlParams = {};

      // Try to get session ID from QA-Pilot's session system
      // Look for caseId in various places
      if (window.currentSession && window.currentSession.caseId) {
        sessionId = window.currentSession.caseId;
      } else if (window.parent && window.parent.currentSession && window.parent.currentSession.caseId) {
        sessionId = window.parent.currentSession.caseId;
      }

      // Read data attributes from body
      var body = document.body;
      if (body) {
        pageId = body.getAttribute('data-page-id') || '';
        moduleId = body.getAttribute('data-module-id') || '';
        lessonId = body.getAttribute('data-lesson-id') || '';
        appVersion = body.getAttribute('data-app-version') || '';
        
        // Determine app context from data attributes or URL
        var dataApp = body.getAttribute('data-app-context');
        if (dataApp) {
          appContext = dataApp;
        }
      }

      // Parse URL parameters
      try {
        var search = window.location.search.substring(1);
        if (search) {
          var params = search.split('&');
          for (var i = 0; i < params.length; i++) {
            var pair = params[i].split('=');
            if (pair.length === 2) {
              var key = decodeURIComponent(pair[0]);
              var value = decodeURIComponent(pair[1]);
              urlParams[key] = value;
              
              // Special handling for known QA-Pilot params
              if (key === 'course') {
                moduleId = value; // course ID often doubles as module ID
              }
              if (key === 'courseId') {
                moduleId = value;
              }
              if (key === 'caseId') {
                sessionId = value;
              }
            }
          }
        }
      } catch(e) {
        // Ignore URL parsing errors
      }

      // Determine app context based on URL/path if not set by data attribute
      if (appContext === 'standalone' && !body.getAttribute('data-app-context')) {
        if (whichPage.indexOf('admin/') === 0) {
          appContext = 'admin';
        } else if (whichPage.indexOf('course-view.html') !== -1) {
          appContext = 'training';
        } else if (whichPage.indexOf('capstone-lab.html') !== -1 || 
                   whichPage.indexOf('capstone-2.html') !== -1) {
          appContext = 'assessment';
        } else if (whichPage.indexOf('desktop/') === 0 || 
                   whichPage.indexOf('QASimulator.html') !== -1) {
          appContext = 'os-desktop';
        } else if (whichPage.indexOf('apps/') === 0) {
          appContext = 'os-app';
        } else if (whichPage === 'portal.html' || whichPage === '') {
          appContext = 'standalone';
        } else if (whichPage === 'index.html' || whichPage === 'login.html') {
          appContext = 'standalone';
        } else if (whichPage === 'certificate.html') {
          appContext = 'standalone';
        }
      }

      // Build page record
      var pageRecord = {
        which_page: whichPage,
        page_id: pageId || _extractPageIdFromPath(whichPage),
        module_id: moduleId,
        lesson_id: lessonId,
        page_title: pageTitle,
        app_version: appVersion || 'v2.0',
        session_id: sessionId,
        app_context: appContext,
        url_params: urlParams,
        registered_at: new Date().toISOString()
      };

      resolve(pageRecord);
    });
  }

  /**
   * Extracts a page ID from a path (fallback when no data attribute)
   * @param {string} path - Page path
   * @returns {string} Page ID
   */
  function _extractPageIdFromPath(path) {
    // Remove file extension
    var name = path.replace(/\.[^/.]+$/, '');
    // Take last segment after slashes
    var segments = name.split('/');
    return segments[segments.length - 1] || 'unknown';
  }

  // ── EXPOSE NAMESPACE ──────────────────────────────────────────────────────

  window.QA_PAGE_REGISTER = {
    registerCurrentPage: registerCurrentPage
  };

  // Auto-register when loaded (but don't break if DB not ready yet)
  // We delay registration slightly to allow DB to initialize
  setTimeout(function() {
    if (window.QA_DB && window.QA_DB.init) {
      window.QA_DB.init()
        .then(function() { return window.QA_PAGE_REGISTER.registerCurrentPage(); })
        .catch(function(e) {
          console.warn('[QA_PAGE_REGISTER] Delayed registration failed:', e);
        });
    }
  }, 100);

})();
