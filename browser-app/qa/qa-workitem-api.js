/**
 * =============================================================================
 * qa-workitem-api.js — QA Debugger Work Item API
 * =============================================================================
 *
 * PURPOSE:
 * Provides Azure DevOps-style work item creation, validation, and management.
 * Includes ADO-style fields: Area Path, Iteration Path, Assigned To, Priority,
 * Severity, Acceptance Criteria, Discussion, Tags, etc.
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
  if (window.QA_WORKITEM_API) return;

  // ── DEPENDENCIES ──────────────────────────────────────────────────────────

  // Use existing QA_SCHEMA and QA_DB namespaces
  if (!window.QA_SCHEMA || !window.QA_DB) {
    console.error('[QA_WORKITEM_API] Missing dependencies: QA_SCHEMA or QA_DB');
    return;
  }

  var SCHEMA = window.QA_SCHEMA.SCHEMA;
  var validateRecord = window.QA_SCHEMA.validateRecord;
  var generateId = window.QA_SCHEMA.generateId;
  var QA_DB = window.QA_DB;

  // ── CONSTANTS ───────────────────────────────────────────────────────────────

  // ADO-style work item types
  var WORK_ITEM_TYPES = [
    'Bug',
    'Task',
    'Test Case',
    'User Story',
    'Feature',
    'Issue'
  ];

  // ADO-style states (simplified)
  var STATES = [
    'New',
    'Active',
    'Resolved',
    'Closed'
  ];

  // ADO-style priority (1-4, 1=highest)
  var PRIORITIES = [1, 2, 3, 4];

  // ADO-style severity (1-4, 1=critical/highest)
  var SEVERITIES = [1, 2, 3, 4];

  // Common area paths for QA-Pilot
  var DEFAULT_AREA_PATHS = [
    'QA Pilot',
    'QA Pilot\\Desktop OS',
    'QA Pilot\\Training',
    'QA Pilot\\Capstone',
    'QA Pilot\\Admin',
    'QA Pilot\\Portal',
    'QA Pilot\\Apps\\Dynamics',
    'QA Pilot\\Apps\\ADO',
    'QA Pilot\\Apps\\Teams',
    'QA Pilot\\Apps\\Browser',
    'QA Pilot\\Apps\\Outlook',
    'QA Pilot\\Apps\\Training App'
  ];

  // ── WORK ITEM SCHEMA EXTENSION ────────────────────────────────────────────

  // Extends the base BugRecord with ADO-style fields
  var WORK_ITEM_SCHEMA = {
    // Core identity
    id: { type: 'string', required: true },
    workItemType: { type: 'string', required: true, allowed: WORK_ITEM_TYPES },
    title: { type: 'string', required: true },

    // ADO-style fields
    state: { type: 'string', required: true, allowed: STATES, default: 'New' },
    areaPath: { type: 'string', required: false, allowed: DEFAULT_AREA_PATHS },
    iterationPath: { type: 'string', required: false },
    assignedTo: { type: 'string', required: false },
    priority: { type: 'number', required: false, min: 1, max: 4, default: 2 },
    severity: { type: 'number', required: false, min: 1, max: 4, default: 2 },

    // Description fields
    description: { type: 'string', required: false },
    stepsToReproduce: { type: 'array', required: false, itemType: 'string' },
    acceptanceCriteria: { type: 'array', required: false, itemType: 'string' },

    // Context
    whichPage: { type: 'string', required: false },
    pageId: { type: 'string', required: false },
    moduleId: { type: 'string', required: false },
    pageTitle: { type: 'string', required: false },
    appVersion: { type: 'string', required: false },
    sessionId: { type: 'string', required: false },
    appContext: { type: 'string', required: false },

    // Environment & reproduction
    environment: { type: 'object', required: false },
    systemInfo: { type: 'object', required: false },

    // Tracking
    tags: { type: 'array', required: false, itemType: 'string' },
    createdBy: { type: 'string', required: false, default: 'tester' },
    createdAt: { type: 'string', required: false },
    updatedAt: { type: 'string', required: false },

    // Collaboration
    discussion: { type: 'array', required: false, itemType: 'object' }, // { author, text, timestamp }
    relatedLinks: { type: 'array', required: false, itemType: 'object' }, // { label, url, type }

    // QA-Pilot specific
    evidence: { type: 'array', required: false, itemType: 'string' },
    humanClarificationNeeded: { type: 'boolean', required: false, default: false },
    clarificationQuestion: { type: 'string', required: false },
    agentInstructions: { type: 'string', required: false }
  };

  // ── VALIDATION & NORMALIZATION ────────────────────────────────────────────

  /**
   * Validates a work item against the schema.
   * NOTE: QA_SCHEMA only has BugRecord/PageRecord/SessionRecord.
   * WorkItem uses its own ADO-extended shape so we validate inline
   * against WORK_ITEM_SCHEMA's required fields rather than delegating
   * to the generic validateRecord() helper.
   * @param {Object} workItem - Work item to validate
   * @returns {Object} { valid: boolean, errors: Array<string> }
   */
  function validateWorkItem(workItem) {
    var errors = [];
    if (!workItem) {
      return { valid: false, errors: ['Work item is null or undefined'] };
    }
    if (!workItem.id) {
      errors.push('id: Required field is missing');
    }
    if (!workItem.title || workItem.title.trim() === '') {
      errors.push('title: Required field is missing');
    }
    if (!workItem.workItemType || WORK_ITEM_TYPES.indexOf(workItem.workItemType) === -1) {
      errors.push('workItemType: must be one of ' + WORK_ITEM_TYPES.join(', '));
    }
    if (!workItem.state || STATES.indexOf(workItem.state) === -1) {
      errors.push('state: must be one of ' + STATES.join(', '));
    }
    return { valid: errors.length === 0, errors: errors };
  }

  /**
   * Normalizes a work item by applying defaults and converting types
   * @param {Object} workItem - Raw work item input
   * @returns {Object} Normalized work item
   */
  function normalizeWorkItem(workItem) {
    if (!workItem) workItem = {};

    // Generate ID if missing
    if (!workItem.id) {
      workItem.id = generateId('WI');
    }

    // Set defaults
    workItem.workItemType = workItem.workItemType || 'Bug';
    workItem.state = workItem.state || 'New';
    workItem.priority = workItem.priority !== undefined ? workItem.priority : 2;
    workItem.severity = workItem.severity !== undefined ? workItem.severity : 2;
    workItem.createdBy = workItem.createdBy || 'tester';
    workItem.createdAt = workItem.createdAt || new Date().toISOString();
    workItem.updatedAt = workItem.updatedAt || new Date().toISOString();

    // Ensure arrays are arrays
    workItem.stepsToReproduce = Array.isArray(workItem.stepsToReproduce) ? workItem.stepsToReproduce : [];
    workItem.acceptanceCriteria = Array.isArray(workItem.acceptanceCriteria) ? workItem.acceptanceCriteria : [];
    workItem.tags = Array.isArray(workItem.tags) ? workItem.tags : [];
    workItem.discussion = Array.isArray(workItem.discussion) ? workItem.discussion : [];
    workItem.relatedLinks = Array.isArray(workItem.relatedLinks) ? workItem.relatedLinks : [];
    workItem.evidence = Array.isArray(workItem.evidence) ? workItem.evidence : [];

    // Ensure objects are objects
    workItem.environment = typeof workItem.environment === 'object' && workItem.environment !== null ? workItem.environment : {};
    workItem.systemInfo = typeof workItem.systemInfo === 'object' && workItem.systemInfo !== null ? workItem.systemInfo : {};

    // Trim strings
    if (workItem.title) workItem.title = workItem.title.trim();
    if (workItem.description) workItem.description = workItem.description.trim();
    if (workItem.areaPath) workItem.areaPath = workItem.areaPath.trim();
    if (workItem.iterationPath) workItem.iterationPath = workItem.iterationPath.trim();
    if (workItem.assignedTo) workItem.assignedTo = workItem.assignedTo.trim();
    if (workItem.clarificationQuestion) workItem.clarificationQuestion = workItem.clarificationQuestion.trim();
    if (workItem.agentInstructions) workItem.agentInstructions = workItem.agentInstructions.trim();

    return workItem;
  }

  /**
   * Creates a work item from current page context
   * @param {Object} input - Partial work item data (title, description, etc.)
   * @returns {Promise<Object>} Created work item
   */
  function createFromCurrentPage(input) {
    return QA_DB.getAllPages()
      .then(function(pages) {
        // Find the most recently registered page as current context
        var currentPage = null;
        if (pages.length > 0) {
          // Sort by registeredAt descending
          var sorted = pages.slice().sort(function(a, b) {
            return new Date(b.registeredAt) - new Date(a.registeredAt);
          });
          currentPage = sorted[0];
        }

        // Build work item from input + page context
        var workItem = normalizeWorkItem(Object.assign({}, input, {
          title: input.title || '',
          description: input.description || '',
          stepsToReproduce: input.stepsToReproduce || [],
          acceptanceCriteria: input.acceptanceCriteria || [],
          whichPage: currentPage ? currentPage.which_page : '',
          pageId: currentPage ? currentPage.page_id : '',
          moduleId: currentPage ? currentPage.module_id : '',
          pageTitle: currentPage ? currentPage.page_title : '',
          appVersion: currentPage ? currentPage.app_version : '',
          sessionId: currentPage ? currentPage.session_id : '',
          appContext: currentPage ? currentPage.app_context : '',
          environment: input.environment || {},
          systemInfo: input.systemInfo || {}
        }));

        // Validate
        var validation = validateWorkItem(workItem);
        if (!validation.valid) {
          return Promise.reject(new Error('Invalid work item: ' + validation.errors.join(', ')));
        }

        // Save
        return QA_DB.createWorkItem(workItem)
          .then(function() { return workItem; });
      });
  }

  /**
   * Updates a work item's state (with validation)
   * @param {string} id - Work item ID
   * @param {string} newState - New state value
   * @returns {Promise<Object>} Updated work item
   */
  function updateState(id, newState) {
    if (!STATES.includes(newState)) {
      return Promise.reject(new Error('Invalid state: ' + newState));
    }
    return QA_DB.updateWorkItem(id, { state: newState, updatedAt: new Date().toISOString() });
  }

  /**
   * Adds a discussion comment to a work item
   * @param {string} id - Work item ID
   * @param {string} author - Comment author
   * @param {string} text - Comment text
   * @returns {Promise<Object>} Updated work item
   */
  function addDiscussion(id, author, text) {
    return QA_DB.getWorkItem(id)
      .then(function(workItem) {
        if (!workItem) {
          return Promise.reject(new Error('Work item not found: ' + id));
        }
        var comment = {
          author: author || 'unknown',
          text: text || '',
          timestamp: new Date().toISOString()
        };
        var discussion = Array.isArray(workItem.discussion) ? workItem.discussion : [];
        discussion.push(comment);
        return QA_DB.updateWorkItem(id, {
          discussion: discussion,
          updatedAt: new Date().toISOString()
        });
      });
  }

  /**
   * Adds acceptance criteria to a work item
   * @param {string} id - Work item ID
   * @param {Array<string>} criteria - Array of acceptance criteria strings
   * @returns {Promise<Object>} Updated work item
   */
  function addAcceptanceCriteria(id, criteria) {
    if (!Array.isArray(criteria)) {
      return Promise.reject(new Error('Acceptance criteria must be an array'));
    }
    return QA_DB.getWorkItem(id)
      .then(function(workItem) {
        if (!workItem) {
          return Promise.reject(new Error('Work item not found: ' + id));
        }
        var ac = Array.isArray(workItem.acceptanceCriteria) ? workItem.acceptanceCriteria : [];
        // Avoid duplicates
        criteria.forEach(function(c) {
          if (ac.indexOf(c) === -1) {
            ac.push(c);
          }
        });
        return QA_DB.updateWorkItem(id, {
          acceptanceCriteria: ac,
          updatedAt: new Date().toISOString()
        });
      });
  }

  /**
   * Gets environment info (browser, viewport, etc.)
   * @returns {Object} Environment information
   */
  function getEnvironmentInfo() {
    var ua = navigator.userAgent;
    var viewport = {
      width: window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth,
      height: window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight
    };

    return {
      browser: ua,
      viewport: viewport.width + 'x' + viewport.height,
      runMode: window.location.protocol === 'file:' ? 'file://' : 'http(s)',
      timestamp: new Date().toISOString(),
      url: window.location.href,
      referrer: document.referrer || ''
    };
  }

  // ── EXPOSE NAMESPACE ──────────────────────────────────────────────────────

  window.QA_WORKITEM_API = {
    // Constants
    WORK_ITEM_TYPES: WORK_ITEM_TYPES,
    STATES: STATES,
    PRIORITIES: PRIORITIES,
    SEVERITIES: SEVERITIES,
    DEFAULT_AREA_PATHS: DEFAULT_AREA_PATHS,

    // Methods
    validateWorkItem: validateWorkItem,
    normalizeWorkItem: normalizeWorkItem,
    createFromCurrentPage: createFromCurrentPage,
    updateState: updateState,
    addDiscussion: addDiscussion,
    addAcceptanceCriteria: addAcceptanceCriteria,
    getEnvironmentInfo: getEnvironmentInfo
  };

})();
