/**
 * =============================================================================
 * debug-board.js — QA-Pilot Debugger Kanban Board
 * =============================================================================
 *
 * PURPOSE:
 * Renders the board view (.qd-board-view) as four columns:
 *   New → Active → Resolved → Closed
 *
 * Each card in the board is clickable and opens the detail panel.
 * Board and list views share the same data (window.QD.filtered).
 *
 * EXPOSES: window.QD_BOARD
 *   QD_BOARD.render(items) — renders the board from an items array
 *
 * DEPENDS ON: window.QD (set by debug.js)
 * =============================================================================
 */

(function() {
  'use strict';

  // ── BOARD CONFIG ──────────────────────────────────────────────────────────

  // Column definitions: name shown in header, CSS modifier class, state value
  var COLUMNS = [
    { label: 'New',      cls: 'qd-board-col-new',      state: 'New'      },
    { label: 'Active',   cls: 'qd-board-col-active',   state: 'Active'   },
    { label: 'Resolved', cls: 'qd-board-col-resolved', state: 'Resolved' },
    { label: 'Closed',   cls: 'qd-board-col-closed',   state: 'Closed'   }
  ];

  // ── INIT ──────────────────────────────────────────────────────────────────

  document.addEventListener('DOMContentLoaded', function() {
    // Wire board-specific buttons
    var boardNewBtn     = document.getElementById('qd-board-new-item');
    var boardRefreshBtn = document.getElementById('qd-board-refresh');

    if (boardNewBtn) {
      boardNewBtn.addEventListener('click', function() {
        if (window.QD_IE && window.QD_IE.openNewItemModal) {
          window.QD_IE.openNewItemModal();
        }
      });
    }

    if (boardRefreshBtn) {
      boardRefreshBtn.addEventListener('click', function() {
        if (window.QD.refresh) window.QD.refresh();
      });
    }
  });

  // ── RENDER ────────────────────────────────────────────────────────────────

  /**
   * Renders the kanban board from an array of work items.
   * Clears and rebuilds .qd-board-container each time.
   * @param {Array} items - Work items (already filtered by debug-filters.js)
   */
  function render(items) {
    var container = document.getElementById('qd-board-container');
    if (!container) return;

    items = items || [];
    container.innerHTML = '';

    // Group items by state
    var grouped = {};
    COLUMNS.forEach(function(col) {
      grouped[col.state] = [];
    });

    items.forEach(function(item) {
      var state = item.state || 'New';
      // Bucket unknown states into New
      if (!grouped[state]) grouped['New'] = grouped['New'] || [];
      if (grouped[state]) {
        grouped[state].push(item);
      } else {
        grouped['New'].push(item);
      }
    });

    // Build each column
    COLUMNS.forEach(function(col) {
      var colItems = grouped[col.state] || [];
      container.appendChild(buildColumn(col, colItems));
    });
  }

  /**
   * Builds a single board column DOM element.
   * @param {Object} col - Column config { label, cls, state }
   * @param {Array} items - Items in this column
   * @returns {HTMLElement}
   */
  function buildColumn(col, items) {
    var colEl = document.createElement('div');
    colEl.className = 'qd-board-column ' + col.cls;

    // Column header
    var header = document.createElement('div');
    header.className = 'qd-board-col-header';
    header.innerHTML =
      '<span>' + col.label + '</span>' +
      '<span class="qd-board-col-count">' + items.length + '</span>';
    colEl.appendChild(header);

    // Card container
    var cardsEl = document.createElement('div');
    cardsEl.className = 'qd-board-col-cards';

    if (items.length === 0) {
      var empty = document.createElement('div');
      empty.style.cssText = 'text-align:center;padding:16px;font-size:12px;color:#a19f9d';
      empty.textContent = 'No items';
      cardsEl.appendChild(empty);
    } else {
      items.forEach(function(item) {
        cardsEl.appendChild(buildCard(item));
      });
    }

    colEl.appendChild(cardsEl);
    return colEl;
  }

  /**
   * Builds a single board card DOM element.
   * @param {Object} item - Work item
   * @returns {HTMLElement}
   */
  function buildCard(item) {
    var card = document.createElement('div');
    card.className = 'qd-board-card';
    card.setAttribute('data-id', item.id);

    var esc       = window.QD.escHtml;
    var typeSlug  = window.QD.typeToSlug(item.workItemType);
    var typeAbbr  = window.QD.typeToAbbr(item.workItemType);

    card.innerHTML =
      '<div class="qd-board-card-title">' + esc(item.title || '(untitled)') + '</div>' +
      '<div class="qd-board-card-meta">' +
        '<span class="qd-card-type-icon qd-type-' + typeSlug + '" ' +
        'style="display:inline-flex;font-size:9px;width:16px;height:16px">' +
          typeAbbr +
        '</span>' +
        '<span style="font-family:monospace;color:#0078d4">' + esc(item.id) + '</span>' +
        (item.assignedTo
          ? '<span>· ' + esc(item.assignedTo) + '</span>'
          : '') +
        '<span class="qd-priority-badge qd-priority-' + (item.priority || 2) + '">' +
          'P' + (item.priority || 2) +
        '</span>' +
      '</div>';

    // Click opens detail panel
    card.addEventListener('click', function() {
      if (window.QD.openDetail) window.QD.openDetail(item);
    });

    return card;
  }

  // ── EXPOSE ─────────────────────────────────────────────────────────────────

  window.QD_BOARD = {
    render: render
  };

})();
