/**
 * =============================================================================
 * qa-templates.js — QA Debugger Work Item Templates
 * =============================================================================
 *
 * PURPOSE:
 * Provides pre-defined templates for different work item types (Bug, Task, Test Case, etc.)
 * to help users create consistent work items quickly.
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
  if (window.QA_TEMPLATES) return;

  // ── DEPENDENCIES ──────────────────────────────────────────────────────────

  if (!window.QA_WORKITEM_API) {
    console.error('[QA_TEMPLATES] Missing dependency: QA_WORKITEM_API');
    return;
  }

  var WORKITEM_API = window.QA_WORKITEM_API;

  // ── TEMPLATES ───────────────────────────────────────────────────────────────

  var TEMPLATES = {
    // Bug template
    Bug: {
      workItemType: 'Bug',
      state: 'New',
      priority: 2,
      severity: 2,
      areaPath: 'QA Pilot',
      iterationPath: '',
      assignedTo: '',
      description: '',
      stepsToReproduce: [
        'Step 1: ',
        'Step 2: ',
        'Step 3: '
      ],
      acceptanceCriteria: [
        'Given [context], when [action], then [expected result]'
      ],
      tags: [],
      environment: {},
      systemInfo: {},
      evidence: [],
      humanClarificationNeeded: false,
      clarificationQuestion: '',
      agentInstructions: ''
    },

    // Task template
    Task: {
      workItemType: 'Task',
      state: 'New',
      priority: 2,
      severity: 2,
      areaPath: 'QA Pilot',
      iterationPath: '',
      assignedTo: '',
      description: '',
      stepsToReproduce: [],
      acceptanceCriteria: [],
      tags: [],
      environment: {},
      systemInfo: {},
      evidence: [],
      humanClarificationNeeded: false,
      clarificationQuestion: '',
      agentInstructions: ''
    },

    // Test Case template
    'Test Case': {
      workItemType: 'Test Case',
      state: 'New',
      priority: 2,
      severity: 2,
      areaPath: 'QA Pilot',
      iterationPath: '',
      assignedTo: '',
      description: '',
      stepsToReproduce: [
        'Precondition: ',
        'Test Steps: ',
        'Expected Result: '
      ],
      acceptanceCriteria: [
        'Test passes when all steps execute as expected'
      ],
      tags: ['test'],
      environment: {},
      systemInfo: {},
      evidence: [],
      humanClarificationNeeded: false,
      clarificationQuestion: '',
      agentInstructions: ''
    },

    // User Story template
    'User Story': {
      workItemType: 'User Story',
      state: 'New',
      priority: 2,
      severity: 2,
      areaPath: 'QA Pilot',
      iterationPath: '',
      assignedTo: '',
      description: '',
      stepsToReproduce: [],
      acceptanceCriteria: [
        'As a [user type], I want [goal] so that [benefit]'
      ],
      tags: ['story'],
      environment: {},
      systemInfo: {},
      evidence: [],
      humanClarificationNeeded: false,
      clarificationQuestion: '',
      agentInstructions: ''
    },

    // Feature template
    Feature: {
      workItemType: 'Feature',
      state: 'New',
      priority: 2,
      severity: 2,
      areaPath: 'QA Pilot',
      iterationPath: '',
      assignedTo: '',
      description: '',
      stepsToReproduce: [],
      acceptanceCriteria: [],
      tags: ['feature'],
      environment: {},
      systemInfo: {},
      evidence: [],
      humanClarificationNeeded: false,
      clarificationQuestion: '',
      agentInstructions: ''
    },

    // Issue template
    Issue: {
      workItemType: 'Issue',
      state: 'New',
      priority: 2,
      severity: 2,
      areaPath: 'QA Pilot',
      iterationPath: '',
      assignedTo: '',
      description: '',
      stepsToReproduce: [],
      acceptanceCriteria: [],
      tags: ['issue'],
      environment: {},
      systemInfo: {},
      evidence: [],
      humanClarificationNeeded: false,
      clarificationQuestion: '',
      agentInstructions: ''
    }
  };

  // ── TEMPLATE FUNCTIONS ────────────────────────────────────────────────────

  /**
   * Gets a template for a work item type
   * @param {string} type - Work item type (Bug, Task, Test Case, etc.)
   * @returns {Object} Template object (deep copy)
   */
  function getTemplate(type) {
    var template = TEMPLATES[type] || TEMPLATES.Bug;
    // Return a deep copy
    return JSON.parse(JSON.stringify(template));
  }

  /**
   * Gets all available template types
   * @returns {Array} Array of template type strings
   */
  function getTemplateTypes() {
    return Object.keys(TEMPLATES);
  }

  /**
   * Creates a work item from a template and input data
   * @param {string} templateType - Type of template to use
   * @param {Object} inputData - Data to override in template
   * @returns {Object} New work item based on template
   */
  function createFromTemplate(templateType, inputData) {
    var template = getTemplate(templateType);
    var workItem = WORKITEM_API.normalizeWorkItem(
      Object.assign({}, template, inputData || {})
    );
    // Ensure ID is generated
    if (!workItem.id) {
      workItem.id = WORKITEM_API.generateId('WI');
    }
    return workItem;
  }

  // ── EXPOSE NAMESPACE ──────────────────────────────────────────────────────

  window.QA_TEMPLATES = {
    // Constants
    TEMPLATES: TEMPLATES,

    // Methods
    getTemplate: getTemplate,
    getTemplateTypes: getTemplateTypes,
    createFromTemplate: createFromTemplate
  };

})();
