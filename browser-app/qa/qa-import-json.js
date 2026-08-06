/**
 * =============================================================================
 * qa-import-json.js — QA Debugger JSON Import
 * =============================================================================
 *
 * PURPOSE:
 * Imports work items, pages, sessions, and queries from JSON for transfer
 * between machines or restore from backup.
 *
 * CONSTRAINTS:
 * - Plain JavaScript only.
 * - No dependencies.
 * - Must run under file://.
 * - Does not modify existing QA Pilot files.
 * - Safe merging - preserves existing data unless overwrite specified.
 * =============================================================================
 */

(function() {
  'use strict';

  // Prevent double-load
  if (window.QA_IMPORT_JSON) return;

  // ── DEPENDENCIES ──────────────────────────────────────────────────────────

  if (!window.QA_DB || !window.QA_SCHEMA || !window.QA_WORKITEM_API) {
    console.error('[QA_IMPORT_JSON] Missing dependencies: QA_DB, QA_SCHEMA, or QA_WORKITEM_API');
    return;
  }

  var QA_DB = window.QA_DB;
  var SCHEMA = window.QA_SCHEMA.SCHEMA;
  var WORKITEM_API = window.QA_WORKITEM_API;

  // ── IMPORT FUNCTIONS ──────────────────────────────────────────────────────

  /**
   * Parses an imported file (File object from input[type="file"])
   * @param {File} file - Selected file object
   * @returns {Promise<Object>} Parsed JSON payload
   */
  function parseImportedFile(file) {
    return new Promise(function(resolve, reject) {
      var reader = new FileReader();
      reader.onload = function(event) {
        try {
          var data = JSON.parse(event.target.result);
          resolve(data);
        } catch (e) {
          reject(new Error('Invalid JSON: ' + e.message));
        }
      };
      reader.onerror = function() {
        reject(new Error('Failed to read file'));
      };
      reader.readAsText(file);
    });
  }

  /**
   * Validates an import payload
   * @param {Object} payload - Import payload to validate
   * @returns {Object} { valid: boolean, errors: Array<string> }
   */
  function validatePayload(payload) {
    var errors = [];
    
    // Check required top-level fields
    if (!payload || typeof payload !== 'object') {
      errors.push('Payload must be a JSON object');
      return { valid: false, errors: errors };
    }
    
    if (!payload.schemaVersion) {
      errors.push('Missing schemaVersion');
    } else if (payload.schemaVersion !== SCHEMA.version) {
      errors.push('Schema version mismatch: expected ' + SCHEMA.version + ', got ' + payload.schemaVersion);
    }
    
    if (!payload.project) {
      errors.push('Missing project object');
    }
    
    if (!payload.source) {
      errors.push('Missing source object');
    }
    
    if (payload.bugs !== undefined && !Array.isArray(payload.bugs)) {
      errors.push('bugs must be an array');
    }
    
    if (payload.pages !== undefined && !Array.isArray(payload.pages)) {
      errors.push('pages must be an array');
    }
    
    if (payload.sessions !== undefined && !Array.isArray(payload.sessions)) {
      errors.push('sessions must be an array');
    }
    
    if (payload.queries !== undefined && !Array.isArray(payload.queries)) {
      errors.push('queries must be an array');
    }
    
    // Validate each work item if present
    if (payload.bugs && Array.isArray(payload.bugs)) {
      for (var i = 0; i < payload.bugs.length; i++) {
        var validation = WORKITEM_API.validateWorkItem(payload.bugs[i]);
        if (!validation.valid) {
          errors.push('Work item at index ' + i + ': ' + validation.errors.join(', '));
        }
      }
    }
    
    return {
      valid: errors.length === 0,
      errors: errors
    };
  }

  /**
   * Imports a payload into the debugger database
   * @param {Object} payload - Validated import payload
   * @param {Object} options - Import options (merge strategy, etc.)
   * @returns {Promise<Object>} Import summary
   */
  function importPayload(payload, options) {
    options = options || {};
    var overwrite = options.overwrite === true;

    // validatePayload is synchronous — do NOT call .then() on it
    var validation = validatePayload(payload);
    if (!validation.valid) {
      return Promise.reject(new Error('Invalid payload: ' + validation.errors.join(', ')));
    }

    var summary = {
      imported: 0,
      skipped: 0,
      updated: 0,
      errors: []
    };

    // Chain imports sequentially so summary counts are accurate
    var chain = Promise.resolve();

    if (payload.bugs && Array.isArray(payload.bugs)) {
      chain = chain.then(function() {
        return _importWorkItems(payload.bugs, overwrite, summary);
      });
    }
    if (payload.pages && Array.isArray(payload.pages)) {
      chain = chain.then(function() {
        return _importPages(payload.pages, overwrite, summary);
      });
    }
    if (payload.sessions && Array.isArray(payload.sessions)) {
      chain = chain.then(function() {
        return _importSessions(payload.sessions, overwrite, summary);
      });
    }
    if (payload.queries && Array.isArray(payload.queries)) {
      chain = chain.then(function() {
        return _importQueries(payload.queries, overwrite, summary);
      });
    }

    return chain.then(function() { return summary; });
  }

  /**
   * Imports work items with merge logic
   * @param {Array} items - Array of work item objects
   * @param {boolean} overwrite - Whether to overwrite existing items
   * @param {Object} summary - Import summary to update
   * @returns {Promise<void>} Resolves when import completes
   */
  function _importWorkItems(items, overwrite, summary) {
    return QA_DB.getAllWorkItems()
      .then(function(existingItems) {
        var existingMap = {};
        existingItems.forEach(function(item) {
          existingMap[item.id] = item;
        });
        
        var promises = items.map(function(item) {
          // Ensure item has an ID
          if (!item.id) {
            item.id = WORKITEM_API.generateId('WI');
            summary.imported++;
            return QA_DB.createWorkItem(item);
          }
          
          if (existingMap[item.id]) {
            if (overwrite) {
              summary.updated++;
              return QA_DB.updateWorkItem(item.id, item);
            } else {
              summary.skipped++;
              return Promise.resolve(); // Skip
            }
          } else {
            summary.imported++;
            return QA_DB.createWorkItem(item);
          }
        });
        
        return Promise.all(promises);
      });
  }

  /**
   * Imports pages with merge logic
   * @param {Array} items - Array of page objects
   * @param {boolean} overwrite - Whether to overwrite existing items
   * @param {Object} summary - Import summary to update
   * @returns {Promise<void>} Resolves when import completes
   */
  function _importPages(items, overwrite, summary) {
    return QA_DB.getAllPages()
      .then(function(existingItems) {
        var existingMap = {};
        existingItems.forEach(function(item) {
          existingMap[item.which_page] = item;
        });
        
        var promises = items.map(function(item) {
          var key = item.which_page;
          if (!key) {
            // Generate key if missing
            key = item.which_page || 'page-' + Date.now() + '-' + Math.random();
            item.which_page = key;
          }
          
          if (existingMap[key]) {
            if (overwrite) {
              summary.updated++;
              return QA_DB.registerPage(item); // registerPage acts as update
            } else {
              summary.skipped++;
              return Promise.resolve(); // Skip
            }
          } else {
            summary.imported++;
            return QA_DB.registerPage(item);
          }
        });
        
        return Promise.all(promises);
      });
  }

  /**
   * Imports sessions with merge logic
   * @param {Array} items - Array of session objects
   * @param {boolean} overwrite - Whether to overwrite existing items
   * @param {Object} summary - Import summary to update
   * @returns {Promise<void>} Resolves when import completes
   */
  function _importSessions(items, overwrite, summary) {
    return QA_DB.getAllSessions()
      .then(function(existingItems) {
        var existingMap = {};
        existingItems.forEach(function(item) {
          existingMap[item.session_id] = item;
        });
        
        var promises = items.map(function(item) {
          var key = item.session_id;
          if (!key) {
            // Generate key if missing
            key = 'session-' + Date.now() + '-' + Math.random();
            item.session_id = key;
          }
          
          if (existingMap[key]) {
            if (overwrite) {
              summary.updated++;
              // registerSession uses _put so it acts as upsert
              return QA_DB.registerSession(item);
            } else {
              summary.skipped++;
              return Promise.resolve(); // Skip existing
            }
          } else {
            summary.imported++;
            return QA_DB.registerSession(item);
          }
        });
        
        return Promise.all(promises);
      });
  }

  /**
   * Imports queries with merge logic
   * @param {Array} items - Array of query objects
   * @param {boolean} overwrite - Whether to overwrite existing items
   * @param {Object} summary - Import summary to update
   * @returns {Promise<void>} Resolves when import completes
   */
  function _importQueries(items, overwrite, summary) {
    return QA_DB.getAllQueries()
      .then(function(existingItems) {
        var existingMap = {};
        existingItems.forEach(function(item) {
          existingMap[item.id] = item;
        });
        
        var promises = items.map(function(item) {
          var key = item.id;
          if (!key) {
            // Generate key if missing
            key = 'query-' + Date.now() + '-' + Math.random();
            item.id = key;
          }
          
          if (existingMap[key]) {
            if (overwrite) {
              summary.updated++;
              return QA_DB.saveQuery(item);
            } else {
              summary.skipped++;
              return Promise.resolve(); // Skip
            }
          } else {
            summary.imported++;
            return QA_DB.saveQuery(item);
          }
        });
        
        return Promise.all(promises);
      });
  }

  // ── EXPOSE NAMESPACE ──────────────────────────────────────────────────────

  window.QA_IMPORT_JSON = {
    parseImportedFile: parseImportedFile,
    validatePayload: validatePayload,
    importPayload: importPayload
  };

})();
