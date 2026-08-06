/**
 * =============================================================================
 * debug-panel.js — QA-Pilot Debugger Detail Panel
 * =============================================================================
 *
 * PURPOSE:
 * Manages the slide-in detail panel (.qd-detail-panel) that shows when Elyse
 * clicks a work item in the list or board.
 *
 * RESPONSIBILITIES:
 *   - Render the full work item detail form (all ADO-style fields)
 *   - Handle tab switching (Details / Discussion / Links / Acceptance Criteria)
 *   - Save field changes back to IndexedDB
 *   - Action buttons: Mark Active, Resolve, Close, Needs Clarification, Reject
 *   - Discussion: add/view comments
 *   - Acceptance Criteria: view list
 *   - Close panel
 *
 * EXPOSES: window.QD_PANEL
 *   QD_PANEL.open(item)  — opens panel and renders item
 *   QD_PANEL.close()     — closes panel
 *   QD_PANEL.refresh()   — re-renders current item from DB
 *
 * DEPENDS ON: window.QD (set by debug.js)
 * =============================================================================
 */

(function() {
  'use strict';

  // ── ELEMENTS ───────────────────────────────────────────────────────────────

  var panel, panelTitle, tabBtns, tabPanes;
  var detailCloseBtn, actionBar;

  // ── INIT ──────────────────────────────────────────────────────────────────

  document.addEventListener('DOMContentLoaded', function() {
    panel         = document.getElementById('qd-detail-panel');
    panelTitle    = document.getElementById('qd-detail-title');
    detailCloseBtn = document.getElementById('qd-detail-close');
    tabBtns       = document.querySelectorAll('#qd-detail-tabs .qd-tab-btn');
    tabPanes      = document.querySelectorAll('.qd-tab-pane');

    if (detailCloseBtn) {
      detailCloseBtn.addEventListener('click', closePanel);
    }

    // Wire tab buttons
    tabBtns.forEach(function(btn) {
      btn.addEventListener('click', function() {
        var tab = this.getAttribute('data-tab');
        switchTab(tab);
      });
    });
  });

  // ── PUBLIC API ─────────────────────────────────────────────────────────────

  /**
   * Opens the panel and renders the given work item.
   * @param {Object} item - Work item from DB
   */
  function openPanel(item) {
    if (!panel) return;
    window.QD.selected = item;

    // Update header title
    if (panelTitle) panelTitle.textContent = item.id || 'Work Item';

    // Render all tabs
    renderDetailsTab(item);
    renderDiscussionTab(item);
    renderLinksTab(item);
    renderACTab(item);

    // Switch to Details tab
    switchTab('details');

    // Slide panel in
    panel.classList.add('qd-panel-open');
  }

  /**
   * Closes the panel and clears selection.
   */
  function closePanel() {
    if (!panel) return;
    panel.classList.remove('qd-panel-open');
    window.QD.selected = null;

    // Deselect card
    document.querySelectorAll('.qd-work-item-card').forEach(function(c) {
      c.classList.remove('qd-card-selected');
    });
  }

  /**
   * Re-reads the current item from DB and re-renders.
   * Called after saves to show the updated data.
   */
  function refreshPanel() {
    var current = window.QD.selected;
    if (!current || !current.id) return;

    QA_DB.getWorkItem(current.id)
      .then(function(item) {
        if (item) {
          openPanel(item);
        }
      })
      .catch(function(err) {
        console.error('[QD_PANEL] refresh failed:', err);
      });
  }

  // ── TAB SWITCHING ─────────────────────────────────────────────────────────

  /**
   * Activates the given tab by name.
   * @param {string} tabName - 'details' | 'discussion' | 'links' | 'acceptance'
   */
  function switchTab(tabName) {
    tabBtns.forEach(function(btn) {
      btn.classList.toggle('qd-tab-active', btn.getAttribute('data-tab') === tabName);
    });
    tabPanes.forEach(function(pane) {
      pane.classList.toggle('qd-tab-active', pane.id === 'qd-tab-' + tabName);
    });
  }

  // ── DETAILS TAB ───────────────────────────────────────────────────────────

  /**
   * Renders the details form with all ADO-style fields and action buttons.
   * @param {Object} item - Work item
   */
  function renderDetailsTab(item) {
    var formEl = document.getElementById('qd-work-item-form');
    if (!formEl) return;

    var esc   = window.QD.escHtml;
    var types = QA_WORKITEM_API.WORK_ITEM_TYPES;
    var states = QA_WORKITEM_API.STATES;
    var areas  = QA_WORKITEM_API.DEFAULT_AREA_PATHS;

    // ── Render the form HTML ─────────────────────────────────────────────────
    formEl.innerHTML =

      // Action bar (status transitions)
      '<div class="qd-action-bar" id="qd-panel-action-bar">' +
        '<div class="qd-action-bar-left">' +
          actionBtn('Active',    'Mark Active',    'qd-btn-primary')  +
          actionBtn('Resolved',  'Mark Resolved',  'qd-btn-outline')  +
          actionBtn('Closed',    'Close',          'qd-btn-ghost')    +
        '</div>' +
        '<div class="qd-action-bar-right">' +
          actionBtn('Rejected',  'Reject',         'qd-btn-danger')   +
        '</div>' +
      '</div>' +

      '<div class="qd-divider"></div>' +

      // Title
      fieldGroup('Title', true,
        '<input class="qd-field-input" id="qd-f-title" type="text" value="' +
        esc(item.title || '') + '">') +

      // Type + State row
      '<div class="qd-field-group qd-field-row">' +
        fieldGroup('Type', true, selectEl('qd-f-type', types, item.workItemType)) +
        fieldGroup('State', true, selectEl('qd-f-state', states, item.state)) +
      '</div>' +

      // Priority + Severity row
      '<div class="qd-field-group qd-field-row">' +
        fieldGroup('Priority', false, selectEl('qd-f-priority',
          [['1','1 — Critical'],['2','2 — High'],['3','3 — Medium'],['4','4 — Low']],
          String(item.priority || 2))) +
        fieldGroup('Severity', false, selectEl('qd-f-severity',
          [['1','1 — Critical'],['2','2 — High'],['3','3 — Medium'],['4','4 — Low']],
          String(item.severity || 2))) +
      '</div>' +

      // Area Path
      fieldGroup('Area Path', false,
        selectEl('qd-f-area', areas, item.areaPath, true)) +

      // Assigned To
      fieldGroup('Assigned To', false,
        '<input class="qd-field-input" id="qd-f-assigned" type="text" ' +
        'placeholder="e.g. Elyse" value="' + esc(item.assignedTo || '') + '">') +

      // Description
      fieldGroup('Description', false,
        '<textarea class="qd-field-textarea" id="qd-f-desc" rows="3">' +
        esc(item.description || '') + '</textarea>') +

      // Steps to Reproduce
      '<div class="qd-field-group">' +
        '<label class="qd-field-label">Steps to Reproduce</label>' +
        '<div class="qd-steps-list" id="qd-f-steps">' +
          renderSteps(item.stepsToReproduce) +
        '</div>' +
        '<button type="button" class="qd-btn qd-btn-sm qd-btn-ghost qd-add-step-btn" ' +
        'id="qd-add-step">+ Add Step</button>' +
      '</div>' +

      // Agent Instructions
      fieldGroup('Agent Instructions', false,
        '<textarea class="qd-field-textarea" id="qd-f-agent" rows="2" ' +
        'placeholder="Tell the AI agent exactly what to inspect...">' +
        esc(item.agentInstructions || '') + '</textarea>') +

      // Page context (read-only info strip)
      (item.whichPage ?
        '<div class="qd-field-group">' +
          '<label class="qd-field-label">Filed On Page</label>' +
          '<code style="font-size:12px;color:#0078d4">' + esc(item.whichPage) + '</code>' +
        '</div>'
      : '') +

      // Save button
      '<button type="button" class="qd-btn qd-btn-primary" id="qd-save-btn">Save Changes</button>';

    // ── Wire events after rendering ──────────────────────────────────────────

    // Action bar buttons (state transitions)
    var actionBarEl = document.getElementById('qd-panel-action-bar');
    if (actionBarEl) {
      actionBarEl.addEventListener('click', function(e) {
        var btn = e.target.closest('[data-state]');
        if (!btn || !window.QD.selected) return;
        var newState = btn.getAttribute('data-state');
        applyStateChange(window.QD.selected.id, newState);
      });
    }

    // Add step button
    var addStepBtn = document.getElementById('qd-add-step');
    if (addStepBtn) {
      addStepBtn.addEventListener('click', function() {
        var stepsEl = document.getElementById('qd-f-steps');
        if (stepsEl) {
          var idx = stepsEl.querySelectorAll('.qd-step-row').length + 1;
          stepsEl.insertAdjacentHTML('beforeend', stepRow(idx, ''));
          wireStepDeletes(stepsEl);
        }
      });
    }

    // Wire existing step deletes
    wireStepDeletes(document.getElementById('qd-f-steps'));

    // Save button
    var saveBtn = document.getElementById('qd-save-btn');
    if (saveBtn) {
      saveBtn.addEventListener('click', function() {
        saveDetails(window.QD.selected);
      });
    }
  }

  /**
   * Collects form values and saves back to IndexedDB.
   * @param {Object} current - The currently open work item
   */
  function saveDetails(current) {
    if (!current) return;

    // Collect steps
    var stepInputs = document.querySelectorAll('#qd-f-steps .qd-step-input');
    var steps = [];
    stepInputs.forEach(function(inp) {
      var v = inp.value.trim();
      if (v) steps.push(v);
    });

    var patch = {
      title:            (document.getElementById('qd-f-title')    || {}).value || current.title,
      workItemType:     (document.getElementById('qd-f-type')     || {}).value || current.workItemType,
      state:            (document.getElementById('qd-f-state')    || {}).value || current.state,
      priority:         parseInt((document.getElementById('qd-f-priority') || {}).value) || current.priority,
      severity:         parseInt((document.getElementById('qd-f-severity') || {}).value) || current.severity,
      areaPath:         (document.getElementById('qd-f-area')     || {}).value || '',
      assignedTo:       (document.getElementById('qd-f-assigned') || {}).value || '',
      description:      (document.getElementById('qd-f-desc')     || {}).value || '',
      stepsToReproduce: steps,
      agentInstructions:(document.getElementById('qd-f-agent')    || {}).value || '',
      updatedAt:        new Date().toISOString()
    };

    QA_DB.updateWorkItem(current.id, patch)
      .then(function() {
        window.QD.toast('Work item saved.', 'success');
        return window.QD.refresh();
      })
      .then(function() {
        // Re-open with fresh data
        return QA_DB.getWorkItem(current.id);
      })
      .then(function(updated) {
        if (updated) openPanel(updated);
      })
      .catch(function(err) {
        window.QD.toast('Save failed: ' + err.message, 'error');
      });
  }

  /**
   * Transitions a work item to a new state.
   * @param {string} id
   * @param {string} newState
   */
  function applyStateChange(id, newState) {
    QA_DB.updateWorkItem(id, { state: newState, updatedAt: new Date().toISOString() })
      .then(function() {
        window.QD.toast('Marked ' + newState + '.', 'success');
        return window.QD.refresh();
      })
      .then(function() {
        return QA_DB.getWorkItem(id);
      })
      .then(function(updated) {
        if (updated) openPanel(updated);
      })
      .catch(function(err) {
        window.QD.toast('Failed: ' + err.message, 'error');
      });
  }

  // ── DISCUSSION TAB ─────────────────────────────────────────────────────────

  /**
   * Renders the discussion (comments) tab.
   * @param {Object} item
   */
  function renderDiscussionTab(item) {
    var listEl = document.getElementById('qd-discussion-list');
    var formEl = document.getElementById('qd-discussion-form');
    var addBtn = document.getElementById('qd-discussion-add');
    if (!listEl) return;

    var discussion = Array.isArray(item.discussion) ? item.discussion : [];
    var esc = window.QD.escHtml;

    // Render existing comments
    if (discussion.length === 0) {
      listEl.innerHTML = '<p style="color:#605e5c;font-size:13px">No comments yet.</p>';
    } else {
      listEl.innerHTML = discussion.map(function(c) {
        return '<div class="qd-comment-card">' +
          '<div class="qd-comment-meta">' +
            '<span class="qd-comment-author">' + esc(c.author || 'unknown') + '</span>' +
            '<span>' + formatDate(c.timestamp) + '</span>' +
          '</div>' +
          '<div class="qd-comment-text">' + esc(c.text || '') + '</div>' +
        '</div>';
      }).join('');
    }

    // Comment form (hidden until Add Comment clicked)
    if (formEl) formEl.innerHTML = '';

    if (addBtn) {
      // Remove old listener by cloning
      var newAddBtn = addBtn.cloneNode(true);
      addBtn.parentNode.replaceChild(newAddBtn, addBtn);

      newAddBtn.addEventListener('click', function() {
        if (formEl) {
          formEl.innerHTML =
            '<div class="qd-comment-form">' +
              '<textarea class="qd-comment-input" id="qd-comment-text" ' +
              'placeholder="Add a comment..."></textarea>' +
              '<div style="display:flex;gap:8px;justify-content:flex-end">' +
                '<button type="button" class="qd-btn qd-btn-sm qd-btn-ghost" ' +
                'id="qd-comment-cancel">Cancel</button>' +
                '<button type="button" class="qd-btn qd-btn-sm qd-btn-primary" ' +
                'id="qd-comment-submit">Add Comment</button>' +
              '</div>' +
            '</div>';

          document.getElementById('qd-comment-cancel').addEventListener('click', function() {
            formEl.innerHTML = '';
          });

          document.getElementById('qd-comment-submit').addEventListener('click', function() {
            var text = (document.getElementById('qd-comment-text') || {}).value || '';
            text = text.trim();
            if (!text) return;

            var comment = {
              author: 'Elyse',
              text: text,
              timestamp: new Date().toISOString()
            };
            var current = window.QD.selected;
            var existing = Array.isArray(current.discussion) ? current.discussion : [];
            existing.push(comment);

            QA_DB.updateWorkItem(current.id, {
              discussion: existing,
              updatedAt: new Date().toISOString()
            })
            .then(function() {
              window.QD.toast('Comment added.', 'success');
              formEl.innerHTML = '';
              // Re-render discussion tab
              return QA_DB.getWorkItem(current.id);
            })
            .then(function(updated) {
              if (updated) {
                window.QD.selected = updated;
                renderDiscussionTab(updated);
              }
            })
            .catch(function(err) {
              window.QD.toast('Failed: ' + err.message, 'error');
            });
          });
        }
      });
    }
  }

  // ── LINKS TAB ─────────────────────────────────────────────────────────────

  /**
   * Renders the related links tab.
   * @param {Object} item
   */
  function renderLinksTab(item) {
    var listEl = document.getElementById('qd-links-list');
    var addBtn = document.getElementById('qd-links-add');
    if (!listEl) return;

    var links = Array.isArray(item.relatedLinks) ? item.relatedLinks : [];
    var esc = window.QD.escHtml;

    if (links.length === 0) {
      listEl.innerHTML = '<p style="color:#605e5c;font-size:13px">No related links.</p>';
    } else {
      listEl.innerHTML = links.map(function(link) {
        return '<div class="qd-ac-item">' +
          '<span class="qd-ac-item-text">' +
            '<strong>' + esc(link.label || link.type || 'Link') + ':</strong> ' +
            esc(link.url || '') +
          '</span>' +
        '</div>';
      }).join('');
    }

    if (addBtn) {
      var newBtn = addBtn.cloneNode(true);
      addBtn.parentNode.replaceChild(newBtn, addBtn);
      newBtn.addEventListener('click', function() {
        var label = prompt('Link label (e.g. "Related bug"):');
        if (!label) return;
        var url = prompt('URL or reference:');
        if (!url) return;

        var current = window.QD.selected;
        var existing = Array.isArray(current.relatedLinks) ? current.relatedLinks : [];
        existing.push({ label: label, url: url, type: 'related' });

        QA_DB.updateWorkItem(current.id, {
          relatedLinks: existing,
          updatedAt: new Date().toISOString()
        })
        .then(function() {
          window.QD.toast('Link added.', 'success');
          return QA_DB.getWorkItem(current.id);
        })
        .then(function(updated) {
          if (updated) {
            window.QD.selected = updated;
            renderLinksTab(updated);
          }
        })
        .catch(function(err) {
          window.QD.toast('Failed: ' + err.message, 'error');
        });
      });
    }
  }

  // ── ACCEPTANCE CRITERIA TAB ────────────────────────────────────────────────

  /**
   * Renders the acceptance criteria tab.
   * @param {Object} item
   */
  function renderACTab(item) {
    var listEl = document.getElementById('qd-ac-list');
    var addBtn = document.getElementById('qd-ac-add');
    if (!listEl) return;

    var criteria = Array.isArray(item.acceptanceCriteria) ? item.acceptanceCriteria : [];
    var esc = window.QD.escHtml;

    if (criteria.length === 0) {
      listEl.innerHTML = '<p style="color:#605e5c;font-size:13px">No acceptance criteria defined.</p>';
    } else {
      listEl.innerHTML =
        '<div class="qd-ac-items">' +
        criteria.map(function(c) {
          return '<div class="qd-ac-item"><span class="qd-ac-item-text">• ' + esc(c) + '</span></div>';
        }).join('') +
        '</div>';
    }

    if (addBtn) {
      var newBtn = addBtn.cloneNode(true);
      addBtn.parentNode.replaceChild(newBtn, addBtn);
      newBtn.addEventListener('click', function() {
        var criterion = prompt('Acceptance criterion (Given/When/Then format recommended):');
        if (!criterion || !criterion.trim()) return;

        var current = window.QD.selected;
        var existing = Array.isArray(current.acceptanceCriteria) ? current.acceptanceCriteria : [];
        existing.push(criterion.trim());

        QA_DB.updateWorkItem(current.id, {
          acceptanceCriteria: existing,
          updatedAt: new Date().toISOString()
        })
        .then(function() {
          window.QD.toast('Criterion added.', 'success');
          return QA_DB.getWorkItem(current.id);
        })
        .then(function(updated) {
          if (updated) {
            window.QD.selected = updated;
            renderACTab(updated);
          }
        })
        .catch(function(err) {
          window.QD.toast('Failed: ' + err.message, 'error');
        });
      });
    }
  }

  // ── RENDER HELPERS ─────────────────────────────────────────────────────────

  /** Builds a labeled form field group */
  function fieldGroup(label, required, inputHtml) {
    return '<div class="qd-field-group">' +
      '<label class="qd-field-label">' + label +
      (required ? '<span class="qd-required">*</span>' : '') +
      '</label>' +
      inputHtml +
    '</div>';
  }

  /** Builds a <select> element */
  function selectEl(id, options, selected, allowBlank) {
    var opts = '';
    if (allowBlank) {
      opts += '<option value="">— None —</option>';
    }
    options.forEach(function(opt) {
      var val, label;
      if (Array.isArray(opt)) { val = opt[0]; label = opt[1]; }
      else { val = opt; label = opt; }
      opts += '<option value="' + window.QD.escHtml(val) + '"' +
        (String(selected) === String(val) ? ' selected' : '') + '>' +
        window.QD.escHtml(label) + '</option>';
    });
    return '<select class="qd-field-select" id="' + id + '">' + opts + '</select>';
  }

  /** Builds a single action button with a data-state attribute */
  function actionBtn(state, label, cls) {
    return '<button type="button" class="qd-btn qd-btn-sm ' + cls + '" ' +
      'data-state="' + state + '">' + label + '</button>';
  }

  /** Renders the list of steps-to-reproduce input rows */
  function renderSteps(stepsArray) {
    if (!Array.isArray(stepsArray) || stepsArray.length === 0) {
      return stepRow(1, '');
    }
    return stepsArray.map(function(s, i) {
      return stepRow(i + 1, s);
    }).join('');
  }

  /** Builds a single step row HTML */
  function stepRow(index, value) {
    return '<div class="qd-step-row">' +
      '<span class="qd-step-num">' + index + '.</span>' +
      '<textarea class="qd-step-input" rows="1" placeholder="Describe step ' + index + '...">' +
      window.QD.escHtml(value || '') + '</textarea>' +
      '<button type="button" class="qd-step-del" title="Remove step">✕</button>' +
    '</div>';
  }

  /** Wires delete buttons on step rows and auto-renumbers */
  function wireStepDeletes(stepsEl) {
    if (!stepsEl) return;
    stepsEl.querySelectorAll('.qd-step-del').forEach(function(btn) {
      // Clone to remove old listeners
      var newBtn = btn.cloneNode(true);
      btn.parentNode.replaceChild(newBtn, btn);
      newBtn.addEventListener('click', function() {
        this.closest('.qd-step-row').remove();
        // Renumber remaining rows
        var rows = stepsEl.querySelectorAll('.qd-step-row');
        rows.forEach(function(row, i) {
          var num = row.querySelector('.qd-step-num');
          if (num) num.textContent = (i + 1) + '.';
        });
      });
    });
  }

  /** Formats an ISO timestamp to a human-readable short form */
  function formatDate(iso) {
    if (!iso) return '';
    try {
      var d = new Date(iso);
      return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch(e) { return iso; }
  }

  // ── EXPOSE ─────────────────────────────────────────────────────────────────

  window.QD_PANEL = {
    open:    openPanel,
    close:   closePanel,
    refresh: refreshPanel
  };

})();
