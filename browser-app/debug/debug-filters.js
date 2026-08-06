/**
 * =============================================================================
 * debug-filters.js — QA-Pilot Debugger Filter & Search
 * =============================================================================
 *
 * PURPOSE:
 * Handles all filtering and search on the work items list:
 *   - Live text search (title, id, description, assignedTo)
 *   - Checkbox filters (State, Type)
 *   - Text input filters (Area Path, Assigned To)
 *   - Filter count badge on the filter button
 *   - Clear all filters
 *
 * HOW IT WORKS:
 * This module attaches to the toolbar's search box and filter dropdown,
 * then sets window.QD.applyFilters so that debug.js calls it on every
 * refresh. It also calls window.QD.refresh() directly when the user
 * changes filter inputs.
 *
 * EXPOSES: window.QD.applyFilters, window.QD.hasActiveFilters
 * =============================================================================
 */

(function() {
  'use strict';

  // ── FILTER STATE ──────────────────────────────────────────────────────────

  // Active filter values — updated whenever the user changes inputs
  var filters = {
    search:     '',      // text search string
    states:     [],      // e.g. ['New', 'Active']
    types:      [],      // e.g. ['Bug', 'Task']
    areaPath:   '',      // substring match
    assignedTo: ''       // substring match
  };

  // ── INIT ──────────────────────────────────────────────────────────────────

  document.addEventListener('DOMContentLoaded', function() {
    wireSearch();
    wireFilterDropdown();

    // Register the filter function on the shared QD namespace.
    // debug.js calls this on every refresh() so the list always respects filters.
    window.QD.applyFilters    = applyFilters;
    window.QD.hasActiveFilters = hasActiveFilters;
  });

  // ── SEARCH ────────────────────────────────────────────────────────────────

  /**
   * Wires the search input for live filtering.
   */
  function wireSearch() {
    var searchInput = document.getElementById('qd-search-input');
    var searchClear = document.getElementById('qd-search-clear');

    if (searchInput) {
      searchInput.addEventListener('input', function() {
        filters.search = this.value.trim().toLowerCase();
        triggerRerender();
      });
    }

    if (searchClear) {
      searchClear.addEventListener('click', function() {
        filters.search = '';
        if (searchInput) {
          searchInput.value = '';
          searchInput.focus();
        }
        triggerRerender();
      });
    }
  }

  // ── FILTER DROPDOWN ───────────────────────────────────────────────────────

  /**
   * Wires the filter button, dropdown open/close, checkbox changes,
   * text input changes, Apply and Clear buttons.
   */
  function wireFilterDropdown() {
    var filterBtn      = document.getElementById('qd-filter-btn');
    var dropdown       = document.getElementById('qd-filter-dropdown');
    var filterApplyBtn = document.getElementById('qd-filter-apply');
    var filterClearBtn = document.getElementById('qd-filter-clear');
    var filterCount    = document.querySelector('#qd-filter-btn .qd-filter-count');

    // Toggle dropdown open/close
    if (filterBtn && dropdown) {
      filterBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        dropdown.classList.toggle('qd-open');
      });

      // Close dropdown when clicking outside
      document.addEventListener('click', function(e) {
        if (!dropdown.contains(e.target) && e.target !== filterBtn) {
          dropdown.classList.remove('qd-open');
        }
      });
    }

    // Apply button — reads all inputs, updates filters, re-renders
    if (filterApplyBtn) {
      filterApplyBtn.addEventListener('click', function() {
        readDropdownFilters(dropdown);
        updateFilterCount(filterCount);
        if (dropdown) dropdown.classList.remove('qd-open');
        triggerRerender();
      });
    }

    // Clear button — resets everything
    if (filterClearBtn) {
      filterClearBtn.addEventListener('click', function() {
        clearDropdownInputs(dropdown);
        filters.states     = [];
        filters.types      = [];
        filters.areaPath   = '';
        filters.assignedTo = '';
        updateFilterCount(filterCount);
        triggerRerender();
      });
    }
  }

  /**
   * Reads all dropdown checkbox/input values into the filters object.
   * @param {HTMLElement} dropdown
   */
  function readDropdownFilters(dropdown) {
    if (!dropdown) return;

    // State checkboxes
    var stateBoxes = dropdown.querySelectorAll('[data-filter="state"]');
    filters.states = [];
    stateBoxes.forEach(function(cb) {
      if (cb.checked) filters.states.push(cb.value);
    });

    // Type checkboxes
    var typeBoxes = dropdown.querySelectorAll('[data-filter="type"]');
    filters.types = [];
    typeBoxes.forEach(function(cb) {
      if (cb.checked) filters.types.push(cb.value);
    });

    // Text inputs
    var areaInput     = dropdown.querySelector('[data-filter="areaPath"]');
    var assignedInput = dropdown.querySelector('[data-filter="assignedTo"]');
    filters.areaPath   = areaInput     ? areaInput.value.trim().toLowerCase()     : '';
    filters.assignedTo = assignedInput ? assignedInput.value.trim().toLowerCase() : '';
  }

  /**
   * Clears all dropdown inputs back to default.
   * @param {HTMLElement} dropdown
   */
  function clearDropdownInputs(dropdown) {
    if (!dropdown) return;
    dropdown.querySelectorAll('input[type="checkbox"]').forEach(function(cb) {
      cb.checked = false;
    });
    dropdown.querySelectorAll('input[type="text"]').forEach(function(inp) {
      inp.value = '';
    });
  }

  /**
   * Updates the filter count badge.
   * Shows the number of active filter dimensions (not individual values).
   * @param {HTMLElement} countEl
   */
  function updateFilterCount(countEl) {
    if (!countEl) return;
    var count = 0;
    if (filters.states.length > 0)   count++;
    if (filters.types.length > 0)    count++;
    if (filters.areaPath)            count++;
    if (filters.assignedTo)          count++;
    countEl.textContent = count > 0 ? String(count) : '';
    countEl.setAttribute('data-count', count);
  }

  // ── FILTER LOGIC ──────────────────────────────────────────────────────────

  /**
   * Applies all active filters to an array of work items.
   * Called by debug.js after every DB refresh.
   * @param {Array} items - Full work item array from DB
   * @returns {Array} Filtered subset
   */
  function applyFilters(items) {
    if (!items) return [];

    return items.filter(function(item) {
      // ── Text search ──────────────────────────────────────────────────────
      if (filters.search) {
        var searchTarget = [
          item.id || '',
          item.title || '',
          item.description || '',
          item.assignedTo || '',
          item.areaPath || ''
        ].join(' ').toLowerCase();

        if (searchTarget.indexOf(filters.search) === -1) return false;
      }

      // ── State filter ─────────────────────────────────────────────────────
      if (filters.states.length > 0) {
        if (filters.states.indexOf(item.state) === -1) return false;
      }

      // ── Type filter ──────────────────────────────────────────────────────
      if (filters.types.length > 0) {
        if (filters.types.indexOf(item.workItemType) === -1) return false;
      }

      // ── Area path filter ─────────────────────────────────────────────────
      if (filters.areaPath) {
        var area = (item.areaPath || '').toLowerCase();
        if (area.indexOf(filters.areaPath) === -1) return false;
      }

      // ── Assigned to filter ───────────────────────────────────────────────
      if (filters.assignedTo) {
        var assigned = (item.assignedTo || '').toLowerCase();
        if (assigned.indexOf(filters.assignedTo) === -1) return false;
      }

      return true;
    });
  }

  /**
   * Returns true if any filter is currently active.
   * Used by debug.js to decide whether to show "no results" vs empty state.
   * @returns {boolean}
   */
  function hasActiveFilters() {
    return !!(
      filters.search ||
      filters.states.length > 0 ||
      filters.types.length > 0 ||
      filters.areaPath ||
      filters.assignedTo
    );
  }

  // ── TRIGGER RE-RENDER ─────────────────────────────────────────────────────

  /**
   * Re-applies filters to the current item list and re-renders.
   * Does NOT hit the DB — just re-filters the in-memory list.
   */
  function triggerRerender() {
    if (!window.QD || !window.QD.allItems) return;

    window.QD.filtered = applyFilters(window.QD.allItems);

    // Re-render the list view directly (avoiding a full DB refresh)
    var listEl = document.getElementById('qd-work-items-list');
    if (!listEl) return;

    var items = window.QD.filtered;
    var esc   = window.QD.escHtml;

    if (!items || items.length === 0) {
      if (hasActiveFilters()) {
        // Show in the list area rather than swapping to empty state
        listEl.innerHTML =
          '<p style="text-align:center;color:#605e5c;padding:32px 0">' +
          'No work items match your current filters.</p>';
        // Make sure work-items view is showing
        if (window.QD.showView) window.QD.showView('work-items');
      } else {
        // True empty — show the full empty state
        var emptyEl = document.getElementById('qd-empty');
        var viewsEl = document.querySelectorAll('.qd-view');
        if (emptyEl) {
          viewsEl.forEach(function(v) { v.classList.remove('qd-visible'); });
          ['loading','error'].forEach(function(s) {
            var e = document.getElementById('qd-' + s);
            if (e) e.classList.remove('qd-visible');
          });
          emptyEl.classList.add('qd-visible');
        }
      }
      return;
    }

    // Ensure work-items view is visible
    if (window.QD.showView) window.QD.showView('work-items');

    // Re-render cards
    listEl.innerHTML = '';
    items.forEach(function(item) {
      var card = buildCard(item, esc);
      listEl.appendChild(card);
    });
  }

  /**
   * Builds a work item card element.
   * Mirrors the logic in debug.js — kept in sync manually.
   * @param {Object} item
   * @param {Function} esc
   * @returns {HTMLElement}
   */
  function buildCard(item, esc) {
    var card = document.createElement('div');
    card.className = 'qd-work-item-card';
    card.setAttribute('data-id', item.id);

    if (window.QD.selected && window.QD.selected.id === item.id) {
      card.classList.add('qd-card-selected');
    }

    var typeSlug  = window.QD.typeToSlug(item.workItemType);
    var typeAbbr  = window.QD.typeToAbbr(item.workItemType);
    var stateSlug = window.QD.stateToSlug(item.state);

    card.innerHTML =
      '<div class="qd-card-type-icon qd-type-' + typeSlug + '">' + typeAbbr + '</div>' +
      '<div class="qd-card-body">' +
        '<div class="qd-card-title">' + esc(item.title || '(untitled)') + '</div>' +
        '<div class="qd-card-meta">' +
          '<span class="qd-card-id">' + esc(item.id) + '</span>' +
          (item.areaPath ? '<span class="qd-card-area">· ' + esc(item.areaPath) + '</span>' : '') +
          (item.assignedTo ? '<span class="qd-card-assigned">· ' + esc(item.assignedTo) + '</span>' : '') +
        '</div>' +
      '</div>' +
      '<div class="qd-card-right">' +
        '<span class="qd-status-badge qd-state-' + stateSlug + '">' + esc(item.state || 'New') + '</span>' +
        '<span class="qd-priority-badge qd-priority-' + (item.priority || 2) + '">P' + (item.priority || 2) + '</span>' +
      '</div>';

    card.addEventListener('click', function() {
      if (window.QD.openDetail) window.QD.openDetail(item);
    });

    return card;
  }

})();
