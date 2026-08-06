/**
 * =============================================================================
 * qa-export-md.js — QA Debugger Markdown Export
 * =============================================================================
 *
 * PURPOSE:
 * Exports work items to agent-ready Markdown for transfer to local coding agents.
 * Includes explicit instructions not to guess unclear behavior and follows
 * Azure DevOps-style formatting.
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
  if (window.QA_EXPORT_MD) return;

  // ── DEPENDENCIES ──────────────────────────────────────────────────────────

  if (!window.QA_DB || !window.QA_WORKITEM_API) {
    console.error('[QA_EXPORT_MD] Missing dependencies: QA_DB or QA_WORKITEM_API');
    return;
  }

  var QA_DB = window.QA_DB;
  var WORKITEM_API = window.QA_WORKITEM_API;

  // ── MARKDOWN GENERATION ────────────────────────────────────────────────────

  /**
   * Builds Markdown from work items or payload
   * @param {Object|Array} data - Work items array or export payload
   * @param {Object} options - Export options
   * @returns {string} Markdown content
   */
  function buildMarkdown(data, options) {
    options = options || {};
    
    // Extract work items from data
    var workItems = [];
    if (Array.isArray(data)) {
      workItems = data;
    } else if (data && Array.isArray(data.bugs)) {
      workItems = data.bugs;
    } else if (data && Array.isArray(data)) {
      workItems = data;
    }
    
    // Apply filters if specified
    if (options.filterFn && typeof options.filterFn === 'function') {
      workItems = workItems.filter(options.filterFn);
    }
    
    // Sort by creation date (newest first) unless specified otherwise
    if (options.sortBy !== 'createdAtAsc') {
      workItems.sort(function(a, b) {
        return new Date(b.createdAt) - new Date(a.createdAt);
      });
    } else {
      workItems.sort(function(a, b) {
        return new Date(a.createdAt) - new Date(b.createdAt);
      });
    }
    
    // Build markdown
    var lines = [];
    
    // Header
    lines.push('# QA-Pilot Work Item Report — Agent Handoff');
    lines.push('');
    
    // Project constraints
    lines.push('## Project Constraints');
    lines.push('');
    lines.push('- Must run under `file://`');
    lines.push('- No external dependencies');
    lines.push('- No server required');
    lines.push('- Do not modify `js/db.js` or `js/app.js` without explicit approval');
    lines.push('- Prefer isolated fixes; modify shared logic only when proven defective');
    lines.push('');
    
    // Human-in-the-loop rule
    lines.push('## Human-in-the-Loop Rule');
    lines.push('');
    lines.push('If expected behavior is unclear, the agent must STOP and mark the work item as NEEDS_CLARIFICATION.');
    lines.push('Do not invent missing requirements. Do not guess.');
    lines.push('The human remains the final authority on expected behavior.');
    lines.push('');
    
    // Work item counts by state
    var stateCounts = {};
    workItems.forEach(function(item) {
      var state = item.state || 'Unknown';
      stateCounts[state] = (stateCounts[state] || 0) + 1;
    });
    
    lines.push('## Work Item Summary');
    lines.push('');
    lines.push('| State | Count |');
    lines.push('|-------|-------|');
    Object.keys(stateCounts).sort().forEach(function(state) {
      lines.push('| ' + state + ' | ' + stateCounts[state] + ' |');
    });
    lines.push('');
    
    // Ready for agent
    var readyItems = workItems.filter(function(item) {
      return item.state === 'Resolved' || item.state === 'Closed';
    });
    
    if (readyItems.length > 0) {
      lines.push('## Ready for Agent (' + readyItems.length + ' work items)');
      lines.push('');
      readyItems.forEach(function(item) {
        lines.push('### ' + formatWorkItemTitle(item));
        lines.push('');
        appendWorkItemDetails(lines, item);
        lines.push('');
      });
    }
    
    // Needs clarification
    var needsClarificationItems = workItems.filter(function(item) {
      return item.humanClarificationNeeded === true;
    });
    
    if (needsClarificationItems.length > 0) {
      lines.push('## Needs Clarification (' + needsClarificationItems.length + ' work items)');
      lines.push('');
      needsClarificationItems.forEach(function(item) {
        lines.push('### ' + formatWorkItemTitle(item));
        lines.push('');
        appendWorkItemDetails(lines, item);
        lines.push('**Question for human:** ' + (item.clarificationQuestion || '[No question provided]'));
        lines.push('');
      });
    }
    
    // Active work
    var activeItems = workItems.filter(function(item) {
      return item.state === 'New' || item.state === 'Active';
    });
    
    if (activeItems.length > 0) {
      lines.push('## Active Work (' + activeItems.length + ' work items)');
      lines.push('');
      activeItems.forEach(function(item) {
        lines.push('### ' + formatWorkItemTitle(item));
        lines.push('');
        appendWorkItemDetails(lines, item);
        lines.push('');
      });
    }
    
    // Other states
    var otherItems = workItems.filter(function(item) {
      return !(item.state === 'New' || item.state === 'Active' || 
               item.state === 'Resolved' || item.state === 'Closed' ||
               item.humanClarificationNeeded === true);
    });
    
    if (otherItems.length > 0) {
      lines.push('## Other States (' + otherItems.length + ' work items)');
      lines.push('');
      otherItems.forEach(function(item) {
        lines.push('### ' + formatWorkItemTitle(item));
        lines.push('');
        appendWorkItemDetails(lines, item);
        lines.push('');
      });
    }
    
    // Footer
    lines.push('---');
    lines.push('');
    lines.push('*Generated by QA-Pilot Debugger on ' + new Date().toLocaleString() + '*');
    lines.push('');
    
    return lines.join('\n');
  }

  /**
   * Formats a work item title for markdown heading
   * @param {Object} item - Work item
   * @returns {string} Formatted title string
   */
  function formatWorkItemTitle(item) {
    var id = item.id || 'UNKNOWN';
    var title = item.title || '[No title]';
    var type = item.workItemType || 'Work Item';
    return id + ' — ' + title + ' (' + type + ')';
  }

  /**
   * Appends work item details to markdown lines array
   * @param {Array} lines - Lines array to append to
   * @param {Object} item - Work item to format
   */
  function appendWorkItemDetails(lines, item) {
    // Basic info
    lines.push('**ID:** ' + (item.id || ''));
    lines.push('**Type:** ' + (item.workItemType || ''));
    lines.push('**State:** ' + (item.state || ''));
    lines.push('**Area Path:** ' + (item.areaPath || ''));
    lines.push('**Iteration Path:** ' + (item.iterationPath || ''));
    lines.push('**Assigned To:** ' + (item.assignedTo || '[Unassigned]'));
    lines.push('**Priority:** ' + (item.priority || ''));
    lines.push('**Severity:** ' + (item.severity || ''));
    lines.push('');
    
    // Description
    if (item.description) {
      lines.push('**Description**');
      lines.push('');
      lines.push(item.description);
      lines.push('');
    }
    
    // Steps to reproduce
    if (item.stepsToReproduce && item.stepsToReproduce.length > 0) {
      lines.push('**Steps to Reproduce**');
      lines.push('');
      item.stepsToReproduce.forEach(function(step, index) {
        lines.push((index + 1) + '. ' + step);
      });
      lines.push('');
    }
    
    // Acceptance criteria
    if (item.acceptanceCriteria && item.acceptanceCriteria.length > 0) {
      lines.push('**Acceptance Criteria**');
      lines.push('');
      item.acceptanceCriteria.forEach(function(criteria, index) {
        lines.push((index + 1) + '. ' + criteria);
      });
      lines.push('');
    }
    
    // Tags
    if (item.tags && item.tags.length > 0) {
      lines.push('**Tags:** ' + item.tags.join(', '));
      lines.push('');
    }
    
    // Environment
    if (item.environment && Object.keys(item.environment).length > 0) {
      lines.push('**Environment**');
      lines.push('');
      lines.push('```json');
      lines.push(JSON.stringify(item.environment, null, 2));
      lines.push('```');
      lines.push('');
    }
    
    // System info
    if (item.systemInfo && Object.keys(item.systemInfo).length > 0) {
      lines.push('**System Info**');
      lines.push('');
      lines.push('```json');
      lines.push(JSON.stringify(item.systemInfo, null, 2));
      lines.push('```');
      lines.push('');
    }
    
    // Evidence
    if (item.evidence && item.evidence.length > 0) {
      lines.push('**Evidence**');
      lines.push('');
      item.evidence.forEach(function(evidence) {
        lines.push('- ' + evidence);
      });
      lines.push('');
    }
    
    // Agent instructions
    if (item.agentInstructions) {
      lines.push('**Agent Instructions**');
      lines.push('');
      lines.push(item.agentInstructions);
      lines.push('');
    }
    
    // Clarification question
    if (item.clarificationQuestion) {
      lines.push('**Clarification Question**');
      lines.push('');
      lines.push(item.clarificationQuestion);
      lines.push('');
    }
    
    // Related links
    if (item.relatedLinks && item.relatedLinks.length > 0) {
      lines.push('**Related Links**');
      lines.push('');
      item.relatedLinks.forEach(function(link) {
        lines.push('- [' + (link.label || 'Link') + '](' + (link.url || '#') + ')');
      });
      lines.push('');
    }
    
    // Discussion
    if (item.discussion && item.discussion.length > 0) {
      lines.push('**Discussion**');
      lines.push('');
      item.discussion.forEach(function(comment) {
        lines.push('*[' + (comment.author || 'unknown') + ' - ' + 
                  new Date(comment.timestamp).toLocaleString() + ']*');
        lines.push('');
        lines.push(comment.text);
        lines.push('');
      });
    }
    
    // Timestamps
    lines.push('*Created: ' + (item.createdAt ? new Date(item.createdAt).toLocaleString() : '') + '*');
    lines.push('*Updated: ' + (item.updatedAt ? new Date(item.updatedAt).toLocaleString() : '') + '*');
  }

  /**
   * Exports all work items to Markdown
   * @param {string} filename - Optional filename
   * @returns {Promise<void>} Resolves when download completes
   */
  function exportAllWorkItemsMarkdown(filename) {
    return QA_DB.getAllWorkItems()
      .then(function(workItems) {
        var markdown = buildMarkdown(workItems);
        return downloadMarkdown(filename, markdown);
      });
  }

  /**
   * Exports ready-for-agent work items to Markdown
   * @param {string} filename - Optional filename
   * @returns {Promise<void>} Resolves when download completes
   */
  function exportReadyForAgentMarkdown(filename) {
    return QA_DB.getAllWorkItems()
      .then(function(workItems) {
        var readyItems = workItems.filter(function(item) {
          return item.state === 'Resolved' || item.state === 'Closed';
        });
        var markdown = buildMarkdown(readyItems);
        return downloadMarkdown(filename, markdown);
      });
  }

  /**
   * Exports needs-clarification work items to Markdown
   * @param {string} filename - Optional filename
   * @returns {Promise<void>} Resolves when download completes
   */
  function exportNeedsClarificationMarkdown(filename) {
    return QA_DB.getAllWorkItems()
      .then(function(workItems) {
        var needsItems = workItems.filter(function(item) {
          return item.humanClarificationNeeded === true;
        });
        var markdown = buildMarkdown(needsItems);
        return downloadMarkdown(filename, markdown);
      });
  }

  /**
   * Exports work items matching a filter to Markdown
   * @param {Function} filterFn - Filter function
   * @param {string} filename - Optional filename
   * @returns {Promise<void>} Resolves when download completes
   */
  function exportFilteredWorkItemsMarkdown(filterFn, filename) {
    return QA_DB.getAllWorkItems()
      .then(function(workItems) {
        var filtered = workItems.filter(filterFn);
        var markdown = buildMarkdown(filtered);
        return downloadMarkdown(filename, markdown);
      });
  }

  /**
   * Downloads markdown as a file
   * @param {string} filename - Name for the downloaded file
   * @param {string} markdown - Markdown content
   */
  function downloadMarkdown(filename, markdown) {
    try {
      var blob = new Blob([markdown], { type: 'text/markdown' });
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
      console.error('[QA_EXPORT_MD] Failed to download markdown:', e);
      throw e;
    }
  }

  // ── EXPOSE NAMESPACE ──────────────────────────────────────────────────────

  window.QA_EXPORT_MD = {
    buildMarkdown: buildMarkdown,
    downloadMarkdown: downloadMarkdown,
    exportAllWorkItemsMarkdown: exportAllWorkItemsMarkdown,
    exportReadyForAgentMarkdown: exportReadyForAgentMarkdown,
    exportNeedsClarificationMarkdown: exportNeedsClarificationMarkdown,
    exportFilteredWorkItemsMarkdown: exportFilteredWorkItemsMarkdown
  };

})();
