/**
 * =============================================================================
 * debug.js — QA-Pilot Debugger Core
 * =============================================================================
 *
 * PURPOSE:
 * Main controller for debug/index.html. Handles:
 *   - Database initialization and storage status display
 *   - Loading and rendering the work items list
 *   - View switching (Work Items / Board / Queries)
 *   - Nav click dispatch (actions route to debug-import-export.js)
 *   - Goose Scale display (always CRUISING in standalone debugger)
 *   - Global state that other debug-*.js files share via window.QD
 *
 * DEPENDENCIES (loaded before this file in index.html):
 *   qa/qa-schema.js, qa/qa-db.js, qa/qa-workitem-api.js,
 *   qa/qa-templates.js, qa/qa-queries.js,
 *   qa/qa-export-json.js, qa/qa-import-json.js, qa/qa-export-md.js
 *
 * SHARED NAMESPACE:
 *   window.QD — shared state used by all debug-*.js files
 *     QD.allItems   : Array — current full work item list
 *     QD.filtered   : Array — currently displayed (after filters)
 *     QD.selected   : Object|null — currently open work item
 *     QD.refresh()  : reloads from DB and re-renders
 *     QD.toast()    : shows a brief notification
 *     QD.showView() : switches main view
 * =============================================================================
 */

(function() {
  'use strict';

  // ── ELEMENTS (cached on DOMContentLoaded) ─────────────────────────────────
  var el = {};

  // ── SHARED STATE ──────────────────────────────────────────────────────────

  // window.QD is the cross-file shared namespace — other debug-*.js files
  // attach their own methods here too.
  window.QD = {
    allItems: [],   // full list from DB
    filtered: [],   // list after filters/search applied
    selected: null, // currently open work item object

    // Provided after init — filled in below
    refresh: null,
    toast: null,
    showView: null
  };

  // ── INIT ──────────────────────────────────────────────────────────────────

  document.addEventListener('DOMContentLoaded', function() {
    // Cache frequently used elements
    el.storageStatus   = document.getElementById('qd-storage-status');
    el.gooseScale      = document.getElementById('qd-goose-scale');
    el.workItemCount   = document.getElementById('qd-work-item-count');
    el.viewContainer   = document.getElementById('qd-view-container');
    el.loading         = document.getElementById('qd-loading');
    el.error           = document.getElementById('qd-error');
    el.errorMessage    = el.error ? el.error.querySelector('.qd-error-message') : null;
    el.empty           = document.getElementById('qd-empty');
    el.retryBtn        = document.getElementById('qd-retry-btn');
    el.newFromEmpty    = document.getElementById('qd-new-from-empty');
    el.workItemsView   = document.getElementById('qd-work-items-view');
    el.workItemsList   = document.getElementById('qd-work-items-list');
    el.boardView       = document.getElementById('qd-board-view');
    el.queriesView     = document.getElementById('qd-queries-view');
    el.navItems        = document.querySelectorAll('.qd-nav-item[data-view]');
    el.actionItems     = document.querySelectorAll('.qd-nav-item[data-action]');

    // Expose QD methods
    window.QD.refresh  = refresh;
    window.QD.toast    = showToast;
    window.QD.showView = showView;

    // Wire nav
    wireNavigation();

    // Wire retry and empty-state buttons
    if (el.retryBtn)    el.retryBtn.addEventListener('click', refresh);
    if (el.newFromEmpty) el.newFromEmpty.addEventListener('click', function() {
      // Route to the new item action — debug-import-export.js handles it
      if (window.QD_IE && typeof window.QD_IE.openNewItemModal === 'function') {
        window.QD_IE.openNewItemModal();
      }
    });

    // Start up
    initDB();
  });

  // ── DATABASE INIT ─────────────────────────────────────────────────────────

  /**
   * Opens the IndexedDB connection and loads initial data.
   * Shows loading state while waiting, error state on failure.
   */
  function initDB() {
    showStateView('loading');

    QA_DB.init()
      .then(function() {
        // DB opened OK — update status indicator
        setStorageStatus('Connected', 'ok');
        return refresh();
      })
      .catch(function(err) {
        console.error('[QD] DB init failed:', err);
        setStorageStatus('Unavailable', 'err');
        showErrorState('Could not connect to IndexedDB. ' + err.message);
      });
  }

  // ── DATA REFRESH ──────────────────────────────────────────────────────────

  /**
   * Reloads all work items from DB and re-renders the current view.
   * Called on init, after create/edit/delete, and on retry.
   * @returns {Promise<void>}
   */
  function refresh() {
    return QA_DB.getAllWorkItems()
      .then(function(items) {
        // Sort by createdAt descending (newest first)
        items.sort(function(a, b) {
          return new Date(b.createdAt || 0) - new Date(a.createdAt || 0);
        });

        window.QD.allItems = items;

        // Apply any active filters (debug-filters.js populates QD.applyFilters)
        if (typeof window.QD.applyFilters === 'function') {
          window.QD.filtered = window.QD.applyFilters(items);
        } else {
          window.QD.filtered = items.slice();
        }

        // Update badge count
        updateItemCount(items.length);

        // Re-render current view
        renderCurrentView();
      })
      .catch(function(err) {
        console.error('[QD] Failed to load work items:', err);
        showErrorState('Failed to load work items: ' + err.message);
      });
  }

  // ── RENDERING ─────────────────────────────────────────────────────────────

  /**
   * Renders whichever view is currently active.
   * Delegates to board/queries renderers if needed.
   */
  function renderCurrentView() {
    var activeNav = document.querySelector('.qd-nav-item.qd-nav-active[data-view]');
    var view = activeNav ? activeNav.getAttribute('data-view') : 'work-items';

    if (view === 'board') {
      // Board rendering is handled by debug-board.js
      if (typeof window.QD_BOARD !== 'undefined' && window.QD_BOARD.render) {
        showView('board');
        window.QD_BOARD.render(window.QD.filtered);
      }
    } else if (view === 'queries') {
      if (typeof window.QD_QUERIES_UI !== 'undefined' && window.QD_QUERIES_UI.render) {
        showView('queries');
        window.QD_QUERIES_UI.render();
      }
    } else {
      renderWorkItemsList(window.QD.filtered);
    }
  }

  /**
   * Renders the flat work items list.
   * Shows empty state if no items match current filters.
   * @param {Array} items - Work items to render
   */
  function renderWorkItemsList(items) {
    if (!el.workItemsList) return;

    if (!items || items.length === 0) {
      // Show empty state only if no filters active; otherwise show "no results"
      var hasFilters = typeof window.QD.hasActiveFilters === 'function'
                       && window.QD.hasActiveFilters();
      if (hasFilters) {
        showView('work-items');
        el.workItemsList.innerHTML =
          '<p style="text-align:center;color:#605e5c;padding:32px 0">' +
          'No work items match your current filters.</p>';
      } else {
        showStateView('empty');
        return;
      }
    } else {
      showView('work-items');
      el.workItemsList.innerHTML = '';
      items.forEach(function(item) {
        el.workItemsList.appendChild(buildWorkItemCard(item));
      });
    }
  }

  /**
   * Builds a single work item card DOM element.
   * @param {Object} item - Work item object from DB
   * @returns {HTMLElement}
   */
  function buildWorkItemCard(item) {
    var card = document.createElement('div');
    card.className = 'qd-work-item-card';
    card.setAttribute('data-id', item.id);

    // Highlight if this is the currently selected item
    if (window.QD.selected && window.QD.selected.id === item.id) {
      card.classList.add('qd-card-selected');
    }

    var typeSlug = typeToSlug(item.workItemType);
    var typeAbbr = typeToAbbr(item.workItemType);
    var stateSlug = stateToSlug(item.state);

    card.innerHTML =
      '<div class="qd-card-type-icon qd-type-' + typeSlug + '">' + typeAbbr + '</div>' +
      '<div class="qd-card-body">' +
        '<div class="qd-card-title">' + escHtml(item.title || '(untitled)') + '</div>' +
        '<div class="qd-card-meta">' +
          '<span class="qd-card-id">' + escHtml(item.id) + '</span>' +
          (item.areaPath ? '<span class="qd-card-area">· ' + escHtml(item.areaPath) + '</span>' : '') +
          (item.assignedTo ? '<span class="qd-card-assigned">· ' + escHtml(item.assignedTo) + '</span>' : '') +
        '</div>' +
      '</div>' +
      '<div class="qd-card-right">' +
        '<span class="qd-status-badge qd-state-' + stateSlug + '">' + escHtml(item.state || 'New') + '</span>' +
        '<span class="qd-priority-badge qd-priority-' + (item.priority || 2) + '">P' + (item.priority || 2) + '</span>' +
      '</div>';

    // Click opens the detail panel
    card.addEventListener('click', function() {
      openDetail(item);
    });

    return card;
  }

  /**
   * Opens the detail panel for a work item.
   * Delegates to debug-panel.js (QD_PANEL.open).
   * @param {Object} item - Work item to display
   */
  function openDetail(item) {
    window.QD.selected = item;

    // Mark the card as selected
    document.querySelectorAll('.qd-work-item-card').forEach(function(c) {
      c.classList.remove('qd-card-selected');
    });
    var card = el.workItemsList
      ? el.workItemsList.querySelector('[data-id="' + item.id + '"]')
      : null;
    if (card) card.classList.add('qd-card-selected');

    // Delegate to panel module
    if (window.QD_PANEL && typeof window.QD_PANEL.open === 'function') {
      window.QD_PANEL.open(item);
    }
  }

  // ── VIEW SWITCHING ─────────────────────────────────────────────────────────

  /**
   * Shows a named main view (work-items, board, queries).
   * Hides loading/error/empty states.
   * @param {string} viewName - 'work-items' | 'board' | 'queries'
   */
  function showView(viewName) {
    // Hide all states first
    ['loading', 'error', 'empty'].forEach(function(s) {
      var e = document.getElementById('qd-' + s);
      if (e) e.classList.remove('qd-visible');
    });

    // Hide all view panes
    var views = document.querySelectorAll('.qd-view');
    views.forEach(function(v) { v.classList.remove('qd-visible'); });

    // Show requested view
    var map = {
      'work-items': el.workItemsView,
      'board':      el.boardView,
      'queries':    el.queriesView
    };
    var target = map[viewName];
    if (target) target.classList.add('qd-visible');
  }

  /**
   * Shows a state overlay (loading, error, empty).
   * @param {string} state - 'loading' | 'error' | 'empty'
   */
  function showStateView(state) {
    // Hide views and other states
    document.querySelectorAll('.qd-view').forEach(function(v) {
      v.classList.remove('qd-visible');
    });
    ['loading', 'error', 'empty'].forEach(function(s) {
      var e = document.getElementById('qd-' + s);
      if (e) e.classList.remove('qd-visible');
    });

    var target = document.getElementById('qd-' + state);
    if (target) target.classList.add('qd-visible');
  }

  /**
   * Shows the error state with a message.
   * @param {string} message
   */
  function showErrorState(message) {
    if (el.errorMessage) el.errorMessage.textContent = message;
    showStateView('error');
  }

  // ── NAVIGATION WIRING ─────────────────────────────────────────────────────

  /**
   * Wires sidebar nav clicks:
   *   data-view items  → switch view
   *   data-action items → delegate to QD_IE (import/export module)
   */
  function wireNavigation() {
    // View nav
    el.navItems.forEach(function(item) {
      item.addEventListener('click', function() {
        var view = this.getAttribute('data-view');

        // Update active state
        el.navItems.forEach(function(n) { n.classList.remove('qd-nav-active'); });
        this.classList.add('qd-nav-active');

        // Switch view
        if (view === 'board') {
          showView('board');
          if (window.QD_BOARD && window.QD_BOARD.render) {
            window.QD_BOARD.render(window.QD.filtered);
          }
        } else if (view === 'queries') {
          showView('queries');
          if (window.QD_QUERIES_UI && window.QD_QUERIES_UI.render) {
            window.QD_QUERIES_UI.render();
          }
        } else {
          renderWorkItemsList(window.QD.filtered);
        }
      });
    });

    // Action nav (new item, import, export)
    el.actionItems.forEach(function(item) {
      item.addEventListener('click', function() {
        var action = this.getAttribute('data-action');
        // Route to import/export module
        if (window.QD_IE) {
          switch (action) {
            case 'new-work-item':  window.QD_IE.openNewItemModal();   break;
            case 'import-json':    window.QD_IE.openImportModal();    break;
            case 'export-json':    window.QD_IE.openExportJsonModal(); break;
            case 'export-md':      window.QD_IE.openExportMdModal();  break;
          }
        }
      });
    });
  }

  // ── STATUS HELPERS ─────────────────────────────────────────────────────────

  function setStorageStatus(text, level) {
    if (!el.storageStatus) return;
    el.storageStatus.textContent = text;
    el.storageStatus.className = 'qd-status-value qd-status-' + (level || 'ok');
  }

  function updateItemCount(n) {
    if (el.workItemCount) el.workItemCount.textContent = n;
  }

  // ── TOAST ──────────────────────────────────────────────────────────────────

  /**
   * Shows a brief notification at the bottom-right of the screen.
   * @param {string} message - Text to display
   * @param {'success'|'error'|'info'} type - Toast style
   * @param {number} [duration=3000] - ms before it fades
   */
  function showToast(message, type, duration) {
    type = type || 'info';
    duration = duration || 3000;

    // Reuse or create toast element
    var toast = document.getElementById('qd-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'qd-toast';
      toast.className = 'qd-toast';
      document.body.appendChild(toast);
    }

    // Clear any running timer
    if (toast._timer) clearTimeout(toast._timer);

    toast.textContent = message;
    toast.className = 'qd-toast qd-toast-' + type;

    // Force reflow so transition fires
    void toast.offsetWidth;
    toast.classList.add('qd-toast-visible');

    toast._timer = setTimeout(function() {
      toast.classList.remove('qd-toast-visible');
    }, duration);
  }

  // ── UTILITY ───────────────────────────────────────────────────────────────

  /**
   * Escapes HTML special characters to prevent XSS in rendered content.
   * @param {string} str
   * @returns {string}
   */
  function escHtml(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /**
   * Converts a work item type string to a CSS slug.
   * E.g. 'Test Case' → 'testcase'
   * @param {string} type
   * @returns {string}
   */
  function typeToSlug(type) {
    var map = {
      'Bug': 'bug', 'Task': 'task', 'Test Case': 'testcase',
      'User Story': 'story', 'Feature': 'feature', 'Issue': 'issue'
    };
    return map[type] || 'bug';
  }

  /**
   * Returns a 1-2 character abbreviation for the type icon.
   * @param {string} type
   * @returns {string}
   */
  function typeToAbbr(type) {
    var map = {
      'Bug': 'B', 'Task': 'T', 'Test Case': 'TC',
      'User Story': 'US', 'Feature': 'F', 'Issue': 'I'
    };
    return map[type] || 'B';
  }

  /**
   * Converts a state string to a CSS slug.
   * @param {string} state
   * @returns {string}
   */
  function stateToSlug(state) {
    var map = {
      'New': 'new', 'Active': 'active',
      'Resolved': 'resolved', 'Closed': 'closed'
    };
    return map[state] || 'new';
  }

  // Expose utility functions so other debug-*.js files can use them
  window.QD.escHtml    = escHtml;
  window.QD.typeToSlug = typeToSlug;
  window.QD.typeToAbbr = typeToAbbr;
  window.QD.stateToSlug = stateToSlug;
  window.QD.openDetail = openDetail;

})();
