/**
 * =============================================================================
 * qa-queries.js — QA Debugger Query Builder
 * =============================================================================
 *
 * PURPOSE:
 * Provides Azure DevOps-style query capabilities for filtering work items.
 * Supports flat list queries (WHERE clauses) that can be saved and reused.
 *
 * CONSTRAINTS:
 * - Plain JavaScript only.
 * - No dependencies.
 * - Must run under file://.
 * - Does not modify existing QA Pilot files.
 * =============================================================================
 */

(function() {
  'use strict';

  // Prevent double-load
  if (window.QA_QUERIES) return;

  // ── DEPENDENCIES ──────────────────────────────────────────────────────────

  if (!window.QA_DB) {
    console.error('[QA_QUERIES] Missing dependency: QA_DB');
    return;
  }

  var QA_DB = window.QA_DB;

  // ── QUERY OPERATORS ────────────────────────────────────────────────────────

  var OPERATORS = {
    // String operators
    '=': function(field, value) { return function(item) { return String(item[field]) === String(value); }; },
    '!=': function(field, value) { return function(item) { return String(item[field]) !== String(value); }; },
    'contains': function(field, value) { return function(item) { return String(item[field] || '').indexOf(String(value)) !== -1; }; },
    'notContains': function(field, value) { return function(item) { return String(item[field] || '').indexOf(String(value)) === -1; }; },
    'startsWith': function(field, value) { return function(item) { return String(item[field] || '').startsWith(String(value)); }; },
    'endsWith': function(field, value) { return function(item) { return String(item[field] || '').endsWith(String(value)); }; },
    
    // Number operators
    '>': function(field, value) { return function(item) { return Number(item[field]) > Number(value); }; },
    '>=': function(field, value) { return function(item) { return Number(item[field]) >= Number(value); }; },
    '<': function(field, value) { return function(item) { return Number(item[field]) < Number(value); }; },
    '<=': function(field, value) { return function(item) { return Number(item[field]) <= Number(value); }; },
    
    // Date operators (ISO strings)
    'after': function(field, value) { return function(item) { return new Date(item[field]) > new Date(value); }; },
    'onOrAfter': function(field, value) { return function(item) { return new Date(item[field]) >= new Date(value); }; },
    'before': function(field, value) { return function(item) { return new Date(item[field]) < new Date(value); }; },
    'onOrBefore': function(field, value) { return function(item) { return new Date(item[field]) <= new Date(value); }; },
    
    // Array operators
    'has': function(field, value) { return function(item) { 
      var arr = Array.isArray(item[field]) ? item[field] : [];
      return arr.indexOf(value) !== -1; 
    }; },
    'doesNotHave': function(field, value) { return function(item) { 
      var arr = Array.isArray(item[field]) ? item[field] : [];
      return arr.indexOf(value) === -1; 
    }; },
    
    // Boolean operators
    '=': function(field, value) { return function(item) { return !!item[field] === !!value; }; },
    '!=': function(field, value) { return function(item) { return !!item[field] !== !!value; }; },
    
    // Special operators
    'in': function(field, values) { 
      if (!Array.isArray(values)) values = [values];
      return function(item) { 
        return values.indexOf(item[field]) !== -1; 
      }; 
    },
    'notIn': function(field, values) { 
      if (!Array.isArray(values)) values = [values];
      return function(item) { 
        return values.indexOf(item[field]) === -1; 
      }; 
    },
    'empty': function(field, value) { return function(item) { 
      var val = item[field];
      return val === null || val === undefined || val === '' || (Array.isArray(val) && val.length === 0);
    }; },
    'notEmpty': function(field, value) { return function(item) { 
      var val = item[field];
      return val !== null && val !== undefined && val !== '' && !(Array.isArray(val) && val.length === 0);
    }; }
  };

  // ── QUERY BUILDER ────────────────────────────────────────────────────────

  /**
   * Creates a new query builder
   * @returns {Object} Query builder instance
   */
  function createQueryBuilder() {
    var clauses = [];
    
    return {
      /**
       * Adds a WHERE clause
       * @param {string} field - Field name
       * @param {string} operator - Operator from OPERATORS
       * @param {*} value - Value to compare
       * @returns {Object} This builder (for chaining)
       */
      where: function(field, operator, value) {
        if (!OPERATORS[operator]) {
          throw new Error('Unknown operator: ' + operator);
        }
        clauses.push({ field: field, operator: operator, value: value });
        return this;
      },
      
      /**
       * Builds the query function
       * @returns {Function} Function that takes an item and returns boolean
       */
      build: function() {
        if (clauses.length === 0) {
          return function() { return true; }; // Match all
        }
        
        return function(item) {
          return clauses.every(function(clause) {
            var operatorFn = OPERATORS[clause.operator];
            if (!operatorFn) return false;
            return operatorFn(clause.field, clause.value)(item);
          });
        };
      },
      
      /**
       * Clears all clauses
       * @returns {Object} This builder (for chaining)
       */
      clear: function() {
        clauses = [];
        return this;
      },
      
      /**
       * Gets a copy of current clauses
       * @returns {Array} Array of clause objects
       */
      getClauses: function() {
        return clauses.slice();
      },
      
      /**
       * Sets clauses from array
       * @param {Array} clauseArray - Array of clause objects
       * @returns {Object} This builder (for chaining)
       */
      setClauses: function(clauseArray) {
        clauses = clauseArray.slice();
        return this;
      }
    };
  }

  // ── QUERY EXECUTION ────────────────────────────────────────────────────────

  /**
   * Executes a query against work items
   * @param {Function} queryFn - Function that returns true for matching items
   * @returns {Promise<Array>} Array of matching work items
   */
  function executeQuery(queryFn) {
    return QA_DB.getAllWorkItems()
      .then(function(items) {
        return items.filter(queryFn);
      });
  }

  /**
   * Executes a saved query by ID
   * @param {string} queryId - Query ID
   * @returns {Promise<Array>} Array of matching work items
   */
  function executeSavedQuery(queryId) {
    return QA_DB.getQuery(queryId)
      .then(function(queryDoc) {
        if (!queryDoc) {
          return Promise.reject(new Error('Query not found: ' + queryId));
        }
        var queryFn = buildQueryFromDoc(queryDoc);
        return executeQuery(queryFn);
      });
  }

  /**
   * Builds a query function from a query document
   * @param {Object} queryDoc - Query document from DB
   * @returns {Function} Query function
   */
  function buildQueryFromDoc(queryDoc) {
    var builder = createQueryBuilder();
    
    if (queryDoc.filters && Array.isArray(queryDoc.filters)) {
      queryDoc.filters.forEach(function(filter) {
        builder.where(filter.field, filter.operator, filter.value);
      });
    }
    
    return builder.build();
  }

  // ── EXPOSE NAMESPACE ──────────────────────────────────────────────────────

  window.QA_QUERIES = {
    // Constants
    OPERATORS: OPERATORS,
    
    // Methods
    createQueryBuilder: createQueryBuilder,
    executeQuery: executeQuery,
    executeSavedQuery: executeSavedQuery,
    buildQueryFromDoc: buildQueryFromDoc
  };

})();
