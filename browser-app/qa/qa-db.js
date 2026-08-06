/**
 * =============================================================================
 * qa-db.js — QA Debugger IndexedDB Wrapper
 * =============================================================================
 *
 * PURPOSE:
 * Provides a browser-safe IndexedDB wrapper for the QA-Pilot debugger.
 * Uses a separate database to avoid interfering with QA-Pilot's existing data.
 *
 * DATABASE:
 *   Name: QAPilotDebugger
 *   Version: 1
 *   Stores: workItems, pages, sessions, queries
 *
 * CONSTRAINTS:
 * - Plain JavaScript only.
 * - No dependencies.
 * - Must run under file://.
 * - Does not modify existing QA Pilot files.
 * - Defensive error handling - app continues if storage unavailable.
 * =============================================================================
 */

(function() {
  'use strict';

  // Prevent double-load
  if (window.QA_DB) return;

  // ── DATABASE CONFIG ────────────────────────────────────────────────────────

  var DB_NAME = 'QAPilotDebugger';
  var DB_VERSION = 1;
  var STORE_NAMES = {
    WORKITEMS: 'workItems',
    PAGES: 'pages',
    SESSIONS: 'sessions',
    QUERIES: 'queries'
  };

  // Cached database reference
  var _db = null;
  var _isInitialized = false;
  var _initPromise = null;

  // ── INITIALIZATION ────────────────────────────────────────────────────────

  /**
   * init()
   * Opens the IndexedDB database and creates object stores.
   * @returns {Promise<IDBDatabase>} Resolves with open database connection.
   */
  function init() {
    // Return existing promise if already initializing
    if (_initPromise) return _initPromise;

    // Return existing connection if already open
    if (_db) {
      _initPromise = Promise.resolve(_db);
      return _initPromise;
    }

    _initPromise = new Promise(function(resolve, reject) {
      var request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onupgradeneeded = function(event) {
        var database = event.target.result;

        // Create workItems store
        if (!database.objectStoreNames.contains(STORE_NAMES.WORKITEMS)) {
          var workItemStore = database.createObjectStore(STORE_NAMES.WORKITEMS, {
            keyPath: 'id'
          });
          workItemStore.createIndex('byStatus', 'status', { unique: false });
          workItemStore.createIndex('bySeverity', 'severity', { unique: false });
          workItemStore.createIndex('byAreaPath', 'areaPath', { unique: false });
          workItemStore.createIndex('byIterationPath', 'iterationPath', { unique: false });
          workItemStore.createIndex('byAssignedTo', 'assignedTo', { unique: false });
          workItemStore.createIndex('byCreatedAt', 'createdAt', { unique: false });
        }

        // Create pages store
        if (!database.objectStoreNames.contains(STORE_NAMES.PAGES)) {
          var pageStore = database.createObjectStore(STORE_NAMES.PAGES, {
            keyPath: 'id'
          });
          pageStore.createIndex('byWhichPage', 'which_page', { unique: false });
          pageStore.createIndex('byPageId', 'page_id', { unique: false });
        }

        // Create sessions store
        if (!database.objectStoreNames.contains(STORE_NAMES.SESSIONS)) {
          var sessionStore = database.createObjectStore(STORE_NAMES.SESSIONS, {
            keyPath: 'id'
          });
          sessionStore.createIndex('bySessionId', 'session_id', { unique: false });
          sessionStore.createIndex('byCaseId', 'case_id', { unique: false });
        }

        // Create queries store
        if (!database.objectStoreNames.contains(STORE_NAMES.QUERIES)) {
          var queryStore = database.createObjectStore(STORE_NAMES.QUERIES, {
            keyPath: 'id'
          });
          queryStore.createIndex('byName', 'name', { unique: false });
        }
      };

      request.onsuccess = function(event) {
        _db = event.target.result;
        _isInitialized = true;
        resolve(_db);
      };

      request.onerror = function(event) {
        console.error('[QA_DB] Failed to open IndexedDB:', event.target.error);
        _isInitialized = false;
        reject(event.target.error);
      };

      request.onblocked = function() {
        console.warn('[QA_DB] Database version change blocked. Close other tabs.');
      };
    });

    return _initPromise;
  }

  // ── INTERNAL HELPERS ──────────────────────────────────────────────────────

  function _getTransaction(storeName, mode) {
    if (!_isInitialized || !_db) {
      return Promise.reject(new Error('Database not initialized'));
    }
    return _db.transaction(storeName, mode);
  }

  function _get(storeName, key) {
    return new Promise(function(resolve, reject) {
      _getTransaction(storeName, 'readonly')
        .then(function(tx) {
          var store = tx.objectStore(storeName);
          var request = store.get(key);
          request.onsuccess = function() { resolve(request.result); };
          request.onerror = function() { reject(request.error); };
          tx.onabort = function() { reject(tx.error || new Error('Transaction aborted')); };
        })
        .catch(reject);
    });
  }

  function _getAll(storeName, indexName, keyOrRange) {
    return new Promise(function(resolve, reject) {
      _getTransaction(storeName, 'readonly')
        .then(function(tx) {
          var store = tx.objectStore(storeName);
          var request;
          if (indexName && keyOrRange !== undefined) {
            var index = store.index(indexName);
            request = index.getAll(keyOrRange);
          } else if (indexName) {
            var index = store.index(indexName);
            request = index.getAll();
          } else {
            request = store.getAll();
          }
          request.onsuccess = function() { resolve(request.result || []); };
          request.onerror = function() { reject(request.error); };
          tx.onabort = function() { reject(tx.error || new Error('Transaction aborted')); };
        })
        .catch(reject);
    });
  }

  function _put(storeName, object) {
    return new Promise(function(resolve, reject) {
      _getTransaction(storeName, 'readwrite')
        .then(function(tx) {
          var store = tx.objectStore(storeName);
          var request = store.put(object);
          request.onsuccess = function() { resolve(); };
          request.onerror = function() { reject(request.error); };
          tx.onabort = function() { reject(tx.error || new Error('Transaction aborted')); };
        })
        .catch(reject);
    });
  }

  function _delete(storeName, key) {
    return new Promise(function(resolve, reject) {
      _getTransaction(storeName, 'readwrite')
        .then(function(tx) {
          var store = tx.objectStore(storeName);
          var request = store.delete(key);
          request.onsuccess = function() { resolve(); };
          request.onerror = function() { reject(request.error); };
          tx.onabort = function() { reject(tx.error || new Error('Transaction aborted')); };
        })
        .catch(reject);
    });
  }

  function _clearStore(storeName) {
    return new Promise(function(resolve, reject) {
      _getTransaction(storeName, 'readwrite')
        .then(function(tx) {
          var store = tx.objectStore(storeName);
          var request = store.clear();
          request.onsuccess = function() { resolve(); };
          request.onerror = function() { reject(request.error); };
          tx.onabort = function() { reject(tx.error || new Error('Transaction aborted')); };
        })
        .catch(reject);
    });
  }

  // ── PUBLIC API ────────────────────────────────────────────────────────────

  /**
   * Get database capabilities report
   */
  function getCapabilities() {
    return {
      persistent: true,
      backend: 'indexeddb',
      dbName: DB_NAME,
      dbVersion: DB_VERSION,
      stores: Object.values(STORE_NAMES),
      warnings: []
    };
  }

  // ── WORK ITEM API ────────────────────────────────────────────────────────

  /**
   * Get all work items
   * @returns {Promise<Array>} Array of work item objects
   */
  function getAllWorkItems() {
    return _getAll(STORE_NAMES.WORKITEMS);
  }

  /**
   * Get work item by ID
   * @param {string} id - Work item ID
   * @returns {Promise<Object>} Work item object or undefined
   */
  function getWorkItem(id) {
    return _get(STORE_NAMES.WORKITEMS, id);
  }

  /**
   * Create a new work item
   * @param {Object} workItem - Work item object (must have id)
   * @returns {Promise<void>} Resolves when saved
   */
  function createWorkItem(workItem) {
    if (!workItem || !workItem.id) {
      return Promise.reject(new Error('Work item must have an id'));
    }
    return _put(STORE_NAMES.WORKITEMS, workItem);
  }

  /**
   * Update a work item (merge)
   * @param {string} id - Work item ID
   * @param {Object} patch - Partial work item to merge
   * @returns {Promise<Object>} Updated work item
   */
  function updateWorkItem(id, patch) {
    return getWorkItem(id)
      .then(function(existing) {
        if (!existing) {
          return Promise.reject(new Error('Work item not found: ' + id));
        }
        var updated = Object.assign({}, existing, patch);
        updated.updatedAt = new Date().toISOString();
        return createWorkItem(updated);
      });
  }

  /**
   * Delete a work item
   * @param {string} id - Work item ID
   * @returns {Promise<void>} Resolves when deleted
   */
  function deleteWorkItem(id) {
    return _delete(STORE_NAMES.WORKITEMS, id);
  }

  /**
   * Get work items by status
   * @param {string|Array} status - Status or array of statuses
   * @returns {Promise<Array>} Array of matching work items
   */
  function getWorkItemsByStatus(status) {
    var statusArray = Array.isArray(status) ? status : [status];
    var promises = statusArray.map(function(s) {
      return _getAll(STORE_NAMES.WORKITEMS, 'byStatus', s);
    });
    return Promise.all(promises).then(function(results) {
      // Flatten and deduplicate by id
      var all = [].concat.apply([], results);
      var seen = new Set();
      return all.filter(function(item) {
        if (seen.has(item.id)) return false;
        seen.add(item.id);
        return true;
      });
    });
  }

  /**
   * Get work items by area path
   * @param {string} areaPath - Area path string
   * @returns {Promise<Array>} Array of matching work items
   */
  function getWorkItemsByAreaPath(areaPath) {
    return _getAll(STORE_NAMES.WORKITEMS, 'byAreaPath', areaPath);
  }

  /**
   * Get work items by iteration path
   * @param {string} iterationPath - Iteration path string
   * @returns {Promise<Array>} Array of matching work items
   */
  function getWorkItemsByIterationPath(iterationPath) {
    return _getAll(STORE_NAMES.WORKITEMS, 'byIterationPath', iterationPath);
  }

  /**
   * Get work items assigned to user
   * @param {string} assignedTo - Assigned to string
   * @returns {Promise<Array>} Array of matching work items
   */
  function getWorkItemsByAssignedTo(assignedTo) {
    return _getAll(STORE_NAMES.WORKITEMS, 'byAssignedTo', assignedTo);
  }

  // ── PAGE API ────────────────────────────────────────────────────────────

  /**
   * Get all registered pages
   * @returns {Promise<Array>} Array of page objects
   */
  function getAllPages() {
    return _getAll(STORE_NAMES.PAGES);
  }

  /**
   * Get page by which_page
   * @param {string} which_page - Page identifier
   * @returns {Promise<Object>} Page object or undefined
   */
  function getPage(which_page) {
    return _get(STORE_NAMES.PAGES, which_page);
  }

  /**
   * Register a page
   * @param {Object} pageRecord - Page record object
   * @returns {Promise<void>} Resolves when saved
   */
  function registerPage(pageRecord) {
    if (!pageRecord || !pageRecord.which_page) {
      return Promise.reject(new Error('Page record must have which_page'));
    }
    return _put(STORE_NAMES.PAGES, pageRecord);
  }

  // ── SESSION API ────────────────────────────────────────────────────────

  /**
   * Get all sessions
   * @returns {Promise<Array>} Array of session objects
   */
  function getAllSessions() {
    return _getAll(STORE_NAMES.SESSIONS);
  }

  /**
   * Get session by session_id
   * @param {string} sessionId - Session ID
   * @returns {Promise<Object>} Session object or undefined
   */
  function getSession(sessionId) {
    return _get(STORE_NAMES.SESSIONS, sessionId);
  }

  /**
   * Register a session
   * @param {Object} sessionRecord - Session record object
   * @returns {Promise<void>} Resolves when saved
   */
  function registerSession(sessionRecord) {
    if (!sessionRecord || !sessionRecord.session_id) {
      return Promise.reject(new Error('Session record must have session_id'));
    }
    return _put(STORE_NAMES.SESSIONS, sessionRecord);
  }

  // ── QUERY API ────────────────────────────────────────────────────────────

  /**
   * Get all saved queries
   * @returns {Promise<Array>} Array of query objects
   */
  function getAllQueries() {
    return _getAll(STORE_NAMES.QUERIES);
  }

  /**
   * Get query by ID
   * @param {string} id - Query ID
   * @returns {Promise<Object>} Query object or undefined
   */
  function getQuery(id) {
    return _get(STORE_NAMES.QUERIES, id);
  }

  /**
   * Save a query
   * @param {Object} query - Query object (must have id and name)
   * @returns {Promise<void>} Resolves when saved
   */
  function saveQuery(query) {
    if (!query || !query.id || !query.name) {
      return Promise.reject(new Error('Query must have id and name'));
    }
    return _put(STORE_NAMES.QUERIES, query);
  }

  /**
   * Delete a query
   * @param {string} id - Query ID
   * @returns {Promise<void>} Resolves when deleted
   */
  function deleteQuery(id) {
    return _delete(STORE_NAMES.QUERIES, id);
  }

  // ── UTILITY ──────────────────────────────────────────────────────────────

  /**
   * Clear all data (for testing/reset)
   * @returns {Promise<void>} Resolves when all stores cleared
   */
  function clearAllData() {
    var promises = Object.values(STORE_NAMES).map(function(storeName) {
      return _clearStore(storeName);
    });
    return Promise.all(promises);
  }

  // ── EXPOSE NAMESPACE ──────────────────────────────────────────────────────

  window.QA_DB = {
    // Constants
    DB_NAME: DB_NAME,
    DB_VERSION: DB_VERSION,
    STORE_NAMES: STORE_NAMES,

    // Methods
    init: init,
    getCapabilities: getCapabilities,

    // Work Item API
    getAllWorkItems: getAllWorkItems,
    getWorkItem: getWorkItem,
    createWorkItem: createWorkItem,
    updateWorkItem: updateWorkItem,
    deleteWorkItem: deleteWorkItem,
    getWorkItemsByStatus: getWorkItemsByStatus,
    getWorkItemsByAreaPath: getWorkItemsByAreaPath,
    getWorkItemsByIterationPath: getWorkItemsByIterationPath,
    getWorkItemsByAssignedTo: getWorkItemsByAssignedTo,

    // Page API
    getAllPages: getAllPages,
    getPage: getPage,
    registerPage: registerPage,

    // Session API
    getAllSessions: getAllSessions,
    getSession: getSession,
    registerSession: registerSession,

    // Query API
    getAllQueries: getAllQueries,
    getQuery: getQuery,
    saveQuery: saveQuery,
    deleteQuery: deleteQuery,

    // Utility
    clearAllData: clearAllData
  };

})();
