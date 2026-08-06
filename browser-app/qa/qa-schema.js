/**
 * =============================================================================
 * qa-schema.js — QA Debugger Schema Definitions
 * =============================================================================
 *
 * PURPOSE:
 * Defines the data structures, constants, and validation rules for the
 * QA-Pilot local debugger. All records follow these shapes.
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
  if (window.QA_SCHEMA) return;

  // ── CONSTANTS ───────────────────────────────────────────────────────────────

  var SEVERITIES = ['blocker', 'high', 'medium', 'low', 'note'];
  var STATUSES = [
    'new',
    'triaged',
    'needs_clarification',
    'ready_for_agent',
    'in_progress',
    'fixed',
    'verified',
    'rejected'
  ];
  var BUG_TYPES = [
    'navigation',
    'content',
    'layout',
    'data',
    'quiz',
    'simulation',
    'accessibility',
    'performance',
    'console_error',
    'other'
  ];
  var APP_CONTEXTS = [
    'standalone',
    'training',
    'assessment',
    'admin',
    'os-desktop',
    'os-app'
  ];

  // ── SCHEMA DEFINITIONS ──────────────────────────────────────────────────────

  var SCHEMA = {
    version: 'qa-bug-report-v1',
    project: 'QA-Pilot Debugger',

    // ── Page Record ───────────────────────────────────────────────────────────
    PageRecord: {
      which_page: { type: 'string', required: true },
      page_id: { type: 'string', required: true },
      module_id: { type: 'string', required: false },
      lesson_id: { type: 'string', required: false },
      page_title: { type: 'string', required: false },
      app_version: { type: 'string', required: false, default: 'v2.0' },
      session_id: { type: 'string', required: false },
      app_context: { type: 'string', required: false, allowed: APP_CONTEXTS },
      url_params: { type: 'object', required: false },
      registered_at: { type: 'string', required: false }
    },

    // ── Bug Record ────────────────────────────────────────────────────────────
    BugRecord: {
      id: { type: 'string', required: true },
      title: { type: 'string', required: true },
      severity: { type: 'string', required: true, allowed: SEVERITIES },
      status: { type: 'string', required: true, allowed: STATUSES },
      bug_type: { type: 'string', required: true, allowed: BUG_TYPES },
      which_page: { type: 'string', required: true },
      page_id: { type: 'string', required: false },
      module_id: { type: 'string', required: false },
      page_title: { type: 'string', required: false },
      app_version: { type: 'string', required: false },
      session_id: { type: 'string', required: false },
      app_context: { type: 'string', required: false, allowed: APP_CONTEXTS },
      observed: { type: 'string', required: true },
      expected: { type: 'string', required: false },
      steps_to_reproduce: { type: 'array', required: true, itemType: 'string' },
      environment: { type: 'object', required: false },
      evidence: { type: 'array', required: false, itemType: 'string' },
      human_clarification_needed: { type: 'boolean', required: false, default: false },
      clarification_question: { type: 'string', required: false },
      agent_instructions: { type: 'string', required: false },
      created_by: { type: 'string', required: false, default: 'tester' },
      created_at: { type: 'string', required: false },
      updated_at: { type: 'string', required: false }
    },

    // ── Session Record ──────────────────────────────────────────────────────
    SessionRecord: {
      session_id: { type: 'string', required: true },
      case_id: { type: 'string', required: false },
      student_name: { type: 'string', required: false },
      student_email: { type: 'string', required: false },
      start_time: { type: 'string', required: false },
      pages_visited: { type: 'array', required: false, itemType: 'string' },
      environment: { type: 'object', required: false }
    },

    // ── Export Payload ──────────────────────────────────────────────────────
    ExportPayload: {
      schemaVersion: { type: 'string', required: true },
      exportedAt: { type: 'string', required: true },
      project: { type: 'object', required: true },
      source: { type: 'object', required: true },
      bugs: { type: 'array', required: true, itemType: 'object' },
      pages: { type: 'array', required: false, itemType: 'object' },
      sessions: { type: 'array', required: false, itemType: 'object' }
    }
  };

  // ── UTILITY FUNCTIONS ─────────────────────────────────────────────────────

  function generateId(prefix) {
    prefix = prefix || 'BUG';
    var now = new Date();
    var dateStr = now.toISOString().split('T')[0].replace(/-/g, '-');
    var random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    return prefix + '-' + dateStr + '-' + random;
  }

  function validateField(value, spec) {
    if (spec.required && (value === undefined || value === null || value === '')) {
      return { valid: false, error: 'Required field is missing' };
    }
    if (value === undefined || value === null) {
      return { valid: true };
    }
    if (spec.type === 'string' && typeof value !== 'string') {
      return { valid: false, error: 'Expected string, got ' + typeof value };
    }
    if (spec.type === 'boolean' && typeof value !== 'boolean') {
      return { valid: false, error: 'Expected boolean, got ' + typeof value };
    }
    if (spec.type === 'array' && !Array.isArray(value)) {
      return { valid: false, error: 'Expected array, got ' + typeof value };
    }
    if (spec.type === 'object' && typeof value !== 'object') {
      return { valid: false, error: 'Expected object, got ' + typeof value };
    }
    if (spec.allowed && value && spec.allowed.indexOf(value) === -1) {
      return { valid: false, error: 'Value "' + value + '" not in allowed list: ' + spec.allowed.join(', ') };
    }
    return { valid: true };
  }

  function validateRecord(record, schemaName) {
    var schema = SCHEMA[schemaName];
    if (!schema) {
      return { valid: false, errors: ['Unknown schema: ' + schemaName] };
    }

    var errors = [];
    var keys = Object.keys(schema);
    for (var i = 0; i < keys.length; i++) {
      var key = keys[i];
      var spec = schema[key];
      var result = validateField(record[key], spec);
      if (!result.valid) {
        errors.push(key + ': ' + result.error);
      }
    }

    return {
      valid: errors.length === 0,
      errors: errors
    };
  }

  function createDefaultBug() {
    var now = new Date().toISOString();
    return {
      id: generateId('BUG'),
      title: '',
      severity: 'medium',
      status: 'new',
      bug_type: 'other',
      which_page: '',
      page_id: '',
      module_id: '',
      page_title: '',
      app_version: 'v2.0',
      session_id: '',
      app_context: 'standalone',
      observed: '',
      expected: '',
      steps_to_reproduce: [],
      environment: {},
      evidence: [],
      human_clarification_needed: false,
      clarification_question: '',
      agent_instructions: '',
      created_by: 'tester',
      created_at: now,
      updated_at: now
    };
  }

  function createDefaultPage() {
    var now = new Date().toISOString();
    return {
      which_page: '',
      page_id: '',
      module_id: '',
      lesson_id: '',
      page_title: '',
      app_version: 'v2.0',
      session_id: '',
      app_context: 'standalone',
      url_params: {},
      registered_at: now
    };
  }

  // ── EXPOSE NAMESPACE ────────────────────────────────────────────────────────

  window.QA_SCHEMA = {
    version: SCHEMA.version,
    project: SCHEMA.project,
    SEVERITIES: SEVERITIES,
    STATUSES: STATUSES,
    BUG_TYPES: BUG_TYPES,
    APP_CONTEXTS: APP_CONTEXTS,
    SCHEMA: SCHEMA,
    validateRecord: validateRecord,
    generateId: generateId,
    createDefaultBug: createDefaultBug,
    createDefaultPage: createDefaultPage
  };

})();
