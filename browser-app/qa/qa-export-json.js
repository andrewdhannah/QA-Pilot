/**
 * =============================================================================
 * qa-export-json.js — QA Debugger JSON Export
 * =============================================================================
 *
 * PURPOSE:
 * Exports work items, pages, sessions, and queries to JSON for transfer
 * between machines or backup/restore.
 *
 * CONSTRAINTS:
 * - Plain JavaScript only.
 * - No dependencies.
 * - Must run under file://.
 * - Uses browser Blob API for download (no filesystem writes).
 * - Does not modify existing QA Pilot files.
 * =============================================================================
 */

(function() {
  'use strict';

  // Prevent double-load
  if (window.QA_EXPORT_JSON) return;

  // ── DEPENDENCIES ──────────────────────────────────────────────────────────

  if (!window.QA_DB || !window.QA_SCHEMA) {
    console.error('[QA_EXPORT_JSON] Missing dependencies: QA_DB or QA_SCHEMA');
    return;
  }

  var QA_DB = window.QA_DB;
  var SCHEMA = window.QA_SCHEMA.SCHEMA;

  // ── EXPORT FUNCTIONS ──────────────────────────────────────────────────────

  /**
   * Builds the export payload with all data
   * @param {Object} options - Export options (filters, etc.)
   * @returns {Object} Export payload ready for JSON serialization
   */
  function buildExportPayload(options) {
    options = options || {};
    
    return {
      schemaVersion: SCHEMA.version,
      exportedAt: new Date().toISOString(),
      project: {
        name: 'QA-Pilot Debugger',
        version: 'v2.0',
        runMode: window.location.protocol === 'file:' ? 'file://' : 'http(s)'
      },
      source: {
        generatedBy: 'QA Debugger',
        storageBackend: 'indexeddb',
        persistent: true,
        dbName: QA_DB.DB_NAME,
        dbVersion: QA_DB.DB_VERSION
      },
      bugs: [], // Will be filled below
      pages: [],
      sessions: [],
      queries: []
    };
  }

  /**
   * Downloads JSON data as a file
   * @param {string} filename - Name for the downloaded file
   * @param {Object} payload - Data to serialize and download
   */
  function downloadJSON(filename, payload) {
    try {
      var json = JSON.stringify(payload, null, 2);
      var blob = new Blob([json], { type: 'application/json' });
      var url = URL.createObjectURL(blob);
      
      // Create temporary link and trigger download
      var a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      
      // Clean up
      setTimeout(function() { URL.revokeObjectURL(url); }, 100);
    } catch (e) {
      console.error('[QA_EXPORT_JSON] Failed to download JSON:', e);
      throw e;
    }
  }

  /**
   * Exports all work items to JSON
   * @param {string} filename - Optional filename (defaults to timestamped)
   * @returns {Promise<void>} Resolves when download completes
   */
  function exportAllWorkItems(filename) {
    return QA_DB.getAllWorkItems()
      .then(function(workItems) {
        var payload = buildExportPayload();
        payload.bugs = workItems; // Using 'bugs' field for backward compatibility with prompt pack
        
        if (!filename) {
          var date = new Date();
          filename = 'qa-workitems-' + 
            date.getFullYear() + '-' + 
            String(date.getMonth() + 1).padStart(2, '0') + '-' + 
            String(date.getDate()).padStart(2, '0') + '-' + 
            String(date.getHours()).padStart(2, '0') + 
            String(date.getMinutes()).padStart(2, '0') + 
            String(date.getSeconds()).padStart(2, '0') + '.json';
        }
        
        return downloadJSON(filename, payload);
      });
  }

  /**
   * Exports filtered work items to JSON
   * @param {Function} filterFn - Function that returns true for items to include
   * @param {string} filename - Optional filename
   * @returns {Promise<void>} Resolves when download completes
   */
  function exportFilteredWorkItems(filterFn, filename) {
    return QA_DB.getAllWorkItems()
      .then(function(workItems) {
        var filtered = workItems.filter(filterFn);
        var payload = buildExportPayload();
        payload.bugs = filtered;
        
        if (!filename) {
          var date = new Date();
          filename = 'qa-workitems-filtered-' + 
            date.getFullYear() + '-' + 
            String(date.getMonth() + 1).padStart(2, '0') + '-' + 
            String(date.getDate()).padStart(2, '0') + '-' + 
            String(date.getHours()).padStart(2, '0') + 
            String(date.getMinutes()).padStart(2, '0') + 
            String(date.getSeconds()).padStart(2, '0') + '.json';
        }
        
        return downloadJSON(filename, payload);
      });
  }

  /**
   * Exports all data (work items, pages, sessions, queries) to JSON
   * @param {string} filename - Optional filename
   * @returns {Promise<void>} Resolves when download completes
   */
  function exportAllData(filename) {
    return Promise.all([
      QA_DB.getAllWorkItems(),
      QA_DB.getAllPages(),
      QA_DB.getAllSessions(),
      QA_DB.getAllQueries()
    ])
    .then(function(results) {
      var workItems = results[0];
      var pages = results[1];
      var sessions = results[2];
      var queries = results[3];
      
      var payload = buildExportPayload();
      payload.bugs = workItems;
      payload.pages = pages;
      payload.sessions = sessions;
      payload.queries = queries;
      
      if (!filename) {
        var date = new Date();
        filename = 'qa-debugger-export-' + 
          date.getFullYear() + '-' + 
          String(date.getMonth() + 1).padStart(2, '0') + '-' + 
          String(date.getDate()).padStart(2, '0') + '-' + 
          String(date.getHours()).padStart(2, '0') + 
          String(date.getMinutes()).padStart(2, '0') + 
          String(date.getSeconds()).padStart(2, '0') + '.json';
      }
      
      return downloadJSON(filename, payload);
    });
  }

  // ── EXPOSE NAMESPACE ──────────────────────────────────────────────────────

  window.QA_EXPORT_JSON = {
    buildExportPayload: buildExportPayload,
    downloadJSON: downloadJSON,
    exportAllWorkItems: exportAllWorkItems,
    exportFilteredWorkItems: exportFilteredWorkItems,
    exportAllData: exportAllData
  };

})();
