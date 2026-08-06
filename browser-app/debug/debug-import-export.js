/**
 * =============================================================================
 * debug-import-export.js — QA-Pilot Debugger Import / Export / New Item
 * =============================================================================
 *
 * PURPOSE:
 * Wires all modal dialogs to their underlying qa/ modules:
 *
 *   "New Work Item" modal    → QA_TEMPLATES + QA_DB (creates item)
 *   "Import JSON" modal      → QA_IMPORT_JSON (reads file, merges into DB)
 *   "Export JSON" modal      → QA_EXPORT_JSON (downloads .json)
 *   "Export Markdown" modal  → QA_EXPORT_MD   (downloads agent-ready .md)
 *
 * Also handles the Queries view (save / load / delete saved queries).
 *
 * EXPOSES: window.QD_IE
 *   QD_IE.openNewItemModal()    — opens the New Work Item modal
 *   QD_IE.openImportModal()     — opens Import JSON modal
 *   QD_IE.openExportJsonModal() — opens Export JSON modal
 *   QD_IE.openExportMdModal()   — opens Export Markdown modal
 *
 * DEPENDS ON:
 *   window.QD             (debug.js)
 *   window.QA_DB          (qa/qa-db.js)
 *   window.QA_WORKITEM_API (qa/qa-workitem-api.js)
 *   window.QA_TEMPLATES   (qa/qa-templates.js)
 *   window.QA_EXPORT_JSON (qa/qa-export-json.js)
 *   window.QA_IMPORT_JSON (qa/qa-import-json.js)
 *   window.QA_EXPORT_MD   (qa/qa-export-md.js)
 *   window.QA_QUERIES     (qa/qa-queries.js)
 *   window.QA_DB.saveQuery / getAllQueries / deleteQuery
 * =============================================================================
 */

(function() {
  'use strict';

  // ── INIT ──────────────────────────────────────────────────────────────────

  document.addEventListener('DOMContentLoaded', function() {
    wireNewItemModal();
    wireImportModal();
    wireExportJsonModal();
    wireExportMdModal();
    wireQueriesView();
  });

  // ══════════════════════════════════════════════════════════════════════════
  // NEW WORK ITEM MODAL
  // ══════════════════════════════════════════════════════════════════════════

  /**
   * Wires the "New Work Item" modal.
   * On open: renders a template-selection dropdown + full form.
   * On "Create": saves via QA_DB.createWorkItem and refreshes.
   */
  function wireNewItemModal() {
    var modal     = document.getElementById('qd-modal-new-item');
    var closeBtn  = document.getElementById('qd-modal-new-item-close');
    var cancelBtn = document.getElementById('qd-modal-new-item-cancel');
    var saveBtn   = document.getElementById('qd-modal-new-item-save');
    var body      = modal ? modal.querySelector('.qd-modal-body') : null;

    if (!modal || !body) return;

    function closeModal() { modal.classList.remove('qd-modal-open'); }

    if (closeBtn)  closeBtn.addEventListener('click',  closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

    // Close on overlay click
    modal.addEventListener('click', function(e) {
      if (e.target === modal) closeModal();
    });

    // Save / Create button
    if (saveBtn) {
      saveBtn.addEventListener('click', function() {
        createWorkItemFromModal(body, closeModal);
      });
    }
  }

  /**
   * Opens the New Item modal and renders the creation form.
   * Exposed as QD_IE.openNewItemModal().
   */
  function openNewItemModal() {
    var modal = document.getElementById('qd-modal-new-item');
    var body  = modal ? modal.querySelector('.qd-modal-body') : null;
    if (!modal || !body) return;

    // Render the form inside the modal body
    renderNewItemForm(body);
    modal.classList.add('qd-modal-open');
  }

  /**
   * Renders the new work item form inside the modal body.
   * @param {HTMLElement} body
   */
  function renderNewItemForm(body) {
    var types  = QA_WORKITEM_API.WORK_ITEM_TYPES;
    var states = QA_WORKITEM_API.STATES;
    var areas  = QA_WORKITEM_API.DEFAULT_AREA_PATHS;
    var esc    = window.QD.escHtml;

    // Default template to Bug
    var defaultTemplate = QA_TEMPLATES.getTemplate('Bug');

    body.innerHTML =
      // Type selector (changes template defaults)
      '<div class="qd-field-group">' +
        '<label class="qd-field-label">Type <span class="qd-required">*</span></label>' +
        buildSelect('qd-ni-type', types, 'Bug') +
      '</div>' +

      // Title
      '<div class="qd-field-group">' +
        '<label class="qd-field-label">Title <span class="qd-required">*</span></label>' +
        '<input class="qd-field-input" id="qd-ni-title" type="text" ' +
        'placeholder="Brief summary of the issue...">' +
      '</div>' +

      // Priority + Severity
      '<div class="qd-field-group qd-field-row">' +
        '<div class="qd-field-group" style="flex:1">' +
          '<label class="qd-field-label">Priority</label>' +
          buildSelect('qd-ni-priority',
            [['1','1 — Critical'],['2','2 — High'],['3','3 — Medium'],['4','4 — Low']],
            '2') +
        '</div>' +
        '<div class="qd-field-group" style="flex:1">' +
          '<label class="qd-field-label">Severity</label>' +
          buildSelect('qd-ni-severity',
            [['1','1 — Critical'],['2','2 — High'],['3','3 — Medium'],['4','4 — Low']],
            '2') +
        '</div>' +
      '</div>' +

      // Area Path
      '<div class="qd-field-group">' +
        '<label class="qd-field-label">Area Path</label>' +
        buildSelect('qd-ni-area', [''].concat(areas), '') +
      '</div>' +

      // Assigned To
      '<div class="qd-field-group">' +
        '<label class="qd-field-label">Assigned To</label>' +
        '<input class="qd-field-input" id="qd-ni-assigned" type="text" ' +
        'placeholder="e.g. Elyse">' +
      '</div>' +

      // Description
      '<div class="qd-field-group">' +
        '<label class="qd-field-label">Description / Observed Behavior</label>' +
        '<textarea class="qd-field-textarea" id="qd-ni-desc" rows="3" ' +
        'placeholder="What did you see? What went wrong?"></textarea>' +
      '</div>' +

      // Steps to Reproduce
      '<div class="qd-field-group">' +
        '<label class="qd-field-label">Steps to Reproduce</label>' +
        '<div class="qd-steps-list" id="qd-ni-steps">' +
          buildStepRow(1, 'Step 1: ') +
          buildStepRow(2, 'Step 2: ') +
          buildStepRow(3, 'Step 3: ') +
        '</div>' +
        '<button type="button" class="qd-btn qd-btn-sm qd-btn-ghost" ' +
        'id="qd-ni-add-step" style="margin-top:4px">+ Add Step</button>' +
      '</div>' +

      // Agent Instructions
      '<div class="qd-field-group">' +
        '<label class="qd-field-label">Agent Instructions</label>' +
        '<textarea class="qd-field-textarea" id="qd-ni-agent" rows="2" ' +
        'placeholder="Tell the AI agent what to inspect (optional)..."></textarea>' +
      '</div>';

    // Wire add-step button
    var addStepBtn = document.getElementById('qd-ni-add-step');
    if (addStepBtn) {
      addStepBtn.addEventListener('click', function() {
        var stepsEl = document.getElementById('qd-ni-steps');
        if (stepsEl) {
          var idx = stepsEl.querySelectorAll('.qd-step-row').length + 1;
          stepsEl.insertAdjacentHTML('beforeend', buildStepRow(idx, ''));
          wireStepDeletes(stepsEl);
        }
      });
    }

    // Wire step deletes
    wireStepDeletes(document.getElementById('qd-ni-steps'));

    // Focus title
    var titleInput = document.getElementById('qd-ni-title');
    if (titleInput) setTimeout(function() { titleInput.focus(); }, 50);
  }

  /**
   * Reads the new item form, validates, saves, and closes modal.
   * @param {HTMLElement} body - Modal body element
   * @param {Function} closeModal - Callback to close the modal
   */
  function createWorkItemFromModal(body, closeModal) {
    var title = (document.getElementById('qd-ni-title') || {}).value || '';
    title = title.trim();

    if (!title) {
      window.QD.toast('Title is required.', 'error');
      var titleInput = document.getElementById('qd-ni-title');
      if (titleInput) titleInput.focus();
      return;
    }

    // Collect steps
    var stepInputs = body.querySelectorAll('#qd-ni-steps .qd-step-input');
    var steps = [];
    stepInputs.forEach(function(inp) {
      var v = inp.value.trim();
      if (v) steps.push(v);
    });

    var type = (document.getElementById('qd-ni-type')     || {}).value || 'Bug';
    var template = QA_TEMPLATES.getTemplate(type);

    var workItem = QA_WORKITEM_API.normalizeWorkItem(Object.assign({}, template, {
      title:             title,
      workItemType:      type,
      priority:          parseInt((document.getElementById('qd-ni-priority') || {}).value) || 2,
      severity:          parseInt((document.getElementById('qd-ni-severity') || {}).value) || 2,
      areaPath:          (document.getElementById('qd-ni-area')     || {}).value || '',
      assignedTo:        (document.getElementById('qd-ni-assigned') || {}).value || '',
      description:       (document.getElementById('qd-ni-desc')     || {}).value || '',
      stepsToReproduce:  steps,
      agentInstructions: (document.getElementById('qd-ni-agent')    || {}).value || '',
      environment:       QA_WORKITEM_API.getEnvironmentInfo()
    }));

    QA_DB.createWorkItem(workItem)
      .then(function() {
        window.QD.toast('Work item created: ' + workItem.id, 'success');
        closeModal();
        return window.QD.refresh();
      })
      .then(function() {
        // Auto-open the newly created item in the panel
        return QA_DB.getWorkItem(workItem.id);
      })
      .then(function(item) {
        if (item && window.QD.openDetail) {
          window.QD.openDetail(item);
        }
      })
      .catch(function(err) {
        window.QD.toast('Failed to create: ' + err.message, 'error');
        console.error('[QD_IE] createWorkItem error:', err);
      });
  }

  // ══════════════════════════════════════════════════════════════════════════
  // IMPORT JSON MODAL
  // ══════════════════════════════════════════════════════════════════════════

  function wireImportModal() {
    var modal     = document.getElementById('qd-modal-import-json');
    var closeBtn  = document.getElementById('qd-modal-import-json-close');
    var cancelBtn = document.getElementById('qd-modal-import-cancel');
    var confirmBtn = document.getElementById('qd-modal-import-confirm');

    if (!modal) return;

    function closeModal() { modal.classList.remove('qd-modal-open'); }

    if (closeBtn)  closeBtn.addEventListener('click',  closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', function(e) {
      if (e.target === modal) closeModal();
    });

    if (confirmBtn) {
      confirmBtn.addEventListener('click', function() {
        var fileInput   = document.getElementById('qd-import-file-input');
        var overwriteCb = document.getElementById('qd-import-overwrite');
        var file = fileInput && fileInput.files && fileInput.files[0];

        if (!file) {
          window.QD.toast('Please select a JSON file first.', 'error');
          return;
        }

        var overwrite = overwriteCb && overwriteCb.checked;

        QA_IMPORT_JSON.parseImportedFile(file)
          .then(function(payload) {
            return QA_IMPORT_JSON.importPayload(payload, { overwrite: overwrite });
          })
          .then(function(summary) {
            var msg = 'Imported: ' + summary.imported +
                      ', Updated: ' + summary.updated +
                      ', Skipped: ' + summary.skipped;
            window.QD.toast(msg, 'success', 5000);
            closeModal();
            return window.QD.refresh();
          })
          .catch(function(err) {
            window.QD.toast('Import failed: ' + err.message, 'error', 6000);
            console.error('[QD_IE] import error:', err);
          });
      });
    }
  }

  function openImportModal() {
    var modal = document.getElementById('qd-modal-import-json');
    if (modal) {
      // Reset file input
      var fileInput = document.getElementById('qd-import-file-input');
      if (fileInput) fileInput.value = '';
      modal.classList.add('qd-modal-open');
    }
  }

  // ══════════════════════════════════════════════════════════════════════════
  // EXPORT JSON MODAL
  // ══════════════════════════════════════════════════════════════════════════

  function wireExportJsonModal() {
    var modal      = document.getElementById('qd-modal-export-json');
    var closeBtn   = document.getElementById('qd-modal-export-json-close');
    var cancelBtn  = document.getElementById('qd-modal-export-cancel');
    var confirmBtn = document.getElementById('qd-modal-export-confirm');

    if (!modal) return;

    function closeModal() { modal.classList.remove('qd-modal-open'); }

    if (closeBtn)  closeBtn.addEventListener('click',  closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', function(e) {
      if (e.target === modal) closeModal();
    });

    if (confirmBtn) {
      confirmBtn.addEventListener('click', function() {
        var typeRadios   = modal.querySelectorAll('input[name="qd-export-type"]');
        var filenameInput = document.getElementById('qd-export-filename');
        var filename     = filenameInput ? filenameInput.value.trim() : '';
        var exportType   = 'all';

        typeRadios.forEach(function(r) { if (r.checked) exportType = r.value; });

        // Build the appropriate export promise
        var exportPromise;
        if (exportType === 'all') {
          exportPromise = QA_EXPORT_JSON.exportAllWorkItems(filename || undefined);
        } else if (exportType === 'filtered') {
          exportPromise = QA_EXPORT_JSON.exportFilteredWorkItems(function(item) {
            return window.QD.filtered.some(function(f) { return f.id === item.id; });
          }, filename || undefined);
        } else if (exportType === 'ready') {
          exportPromise = QA_EXPORT_JSON.exportFilteredWorkItems(function(item) {
            return item.state === 'Resolved' || item.state === 'Closed';
          }, filename || undefined);
        } else if (exportType === 'needs') {
          exportPromise = QA_EXPORT_JSON.exportFilteredWorkItems(function(item) {
            return item.humanClarificationNeeded === true;
          }, filename || undefined);
        } else {
          exportPromise = QA_EXPORT_JSON.exportAllWorkItems(filename || undefined);
        }

        exportPromise
          .then(function() {
            window.QD.toast('Export downloaded.', 'success');
            closeModal();
          })
          .catch(function(err) {
            window.QD.toast('Export failed: ' + err.message, 'error');
          });
      });
    }
  }

  function openExportJsonModal() {
    var modal = document.getElementById('qd-modal-export-json');
    if (modal) modal.classList.add('qd-modal-open');
  }

  // ══════════════════════════════════════════════════════════════════════════
  // EXPORT MARKDOWN MODAL
  // ══════════════════════════════════════════════════════════════════════════

  function wireExportMdModal() {
    var modal      = document.getElementById('qd-modal-export-md');
    var closeBtn   = document.getElementById('qd-modal-export-md-close');
    var cancelBtn  = document.getElementById('qd-modal-export-md-cancel');
    var confirmBtn = document.getElementById('qd-modal-export-md-confirm');

    if (!modal) return;

    function closeModal() { modal.classList.remove('qd-modal-open'); }

    if (closeBtn)  closeBtn.addEventListener('click',  closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', function(e) {
      if (e.target === modal) closeModal();
    });

    if (confirmBtn) {
      confirmBtn.addEventListener('click', function() {
        var typeRadios    = modal.querySelectorAll('input[name="qd-export-md-type"]');
        var filenameInput = document.getElementById('qd-export-md-filename');
        var filename      = filenameInput ? filenameInput.value.trim() : '';
        var exportType    = 'all';

        typeRadios.forEach(function(r) { if (r.checked) exportType = r.value; });

        // Build filter function based on export type
        var filterFn = null;
        if (exportType === 'ready') {
          filterFn = function(item) {
            return item.state === 'Resolved' || item.state === 'Closed';
          };
        } else if (exportType === 'needs') {
          filterFn = function(item) {
            return item.humanClarificationNeeded === true;
          };
        }

        // QA_EXPORT_MD.exportWorkItems takes items and options
        QA_DB.getAllWorkItems()
          .then(function(items) {
            var toExport = filterFn ? items.filter(filterFn) : items;
            // buildMarkdown returns a string; downloadMarkdown triggers the save
            var markdown = QA_EXPORT_MD.buildMarkdown(toExport);
            var fname = filename || (function() {
              var d = new Date();
              return 'qa-workitems-' +
                d.getFullYear() + '-' +
                String(d.getMonth()+1).padStart(2,'0') + '-' +
                String(d.getDate()).padStart(2,'0') + '.md';
            })();
            QA_EXPORT_MD.downloadMarkdown(fname, markdown);
          })
          .then(function() {
            window.QD.toast('Markdown report downloaded.', 'success');
            closeModal();
          })
          .catch(function(err) {
            window.QD.toast('Export failed: ' + err.message, 'error');
            console.error('[QD_IE] markdown export error:', err);
          });
      });
    }
  }

  function openExportMdModal() {
    var modal = document.getElementById('qd-modal-export-md');
    if (modal) modal.classList.add('qd-modal-open');
  }

  // ══════════════════════════════════════════════════════════════════════════
  // QUERIES VIEW
  // ══════════════════════════════════════════════════════════════════════════

  /**
   * Wires the queries view — loads and displays saved queries,
   * handles "New Query" (saves current filters as a query),
   * and executes a query when clicked.
   */
  function wireQueriesView() {
    var newQueryBtn     = document.getElementById('qd-query-new');
    var queryRefreshBtn = document.getElementById('qd-query-refresh');

    if (newQueryBtn) {
      newQueryBtn.addEventListener('click', promptSaveQuery);
    }

    if (queryRefreshBtn) {
      queryRefreshBtn.addEventListener('click', renderQueriesView);
    }

    // Expose so debug.js can call this when switching to queries view
    window.QD_QUERIES_UI = { render: renderQueriesView };
  }

  /**
   * Renders the list of saved queries from DB.
   */
  function renderQueriesView() {
    var listEl = document.getElementById('qd-queries-list');
    if (!listEl) return;

    QA_DB.getAllQueries()
      .then(function(queries) {
        if (!queries || queries.length === 0) {
          listEl.innerHTML =
            '<div style="text-align:center;color:#605e5c;padding:32px">' +
            '<p>No saved queries.</p>' +
            '<p style="font-size:12px">Use "New Query" to save your current filter settings as a reusable query.</p>' +
            '</div>';
          return;
        }

        listEl.innerHTML = '';
        queries.forEach(function(query) {
          listEl.appendChild(buildQueryItem(query));
        });
      })
      .catch(function(err) {
        console.error('[QD_IE] load queries failed:', err);
      });
  }

  /**
   * Builds a single query list item element.
   * @param {Object} query
   * @returns {HTMLElement}
   */
  function buildQueryItem(query) {
    var item = document.createElement('div');
    item.className = 'qd-query-item';

    var esc = window.QD.escHtml;
    var filterCount = Array.isArray(query.filters) ? query.filters.length : 0;

    item.innerHTML =
      '<div class="qd-card-type-icon" style="background:#8764b8;font-size:11px">Q</div>' +
      '<div class="qd-query-name">' + esc(query.name) + '</div>' +
      '<span class="qd-query-count">' + filterCount + ' filter' + (filterCount !== 1 ? 's' : '') + '</span>' +
      '<button class="qd-btn qd-btn-sm qd-btn-ghost qd-query-del" ' +
      'title="Delete query" style="color:#a19f9d">✕</button>';

    // Run query on click (anywhere except delete button)
    item.addEventListener('click', function(e) {
      if (e.target.classList.contains('qd-query-del')) return;
      runSavedQuery(query);
    });

    // Delete button
    var delBtn = item.querySelector('.qd-query-del');
    if (delBtn) {
      delBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        if (!confirm('Delete query "' + query.name + '"?')) return;
        QA_DB.deleteQuery(query.id)
          .then(function() {
            window.QD.toast('Query deleted.', 'info');
            renderQueriesView();
          })
          .catch(function(err) {
            window.QD.toast('Delete failed: ' + err.message, 'error');
          });
      });
    }

    return item;
  }

  /**
   * Executes a saved query and switches to the work items list with results.
   * @param {Object} query
   */
  function runSavedQuery(query) {
    QA_QUERIES.executeSavedQuery(query.id)
      .then(function(results) {
        window.QD.filtered = results;
        // Switch to work-items view and render results
        var workItemsNav = document.querySelector('.qd-nav-item[data-view="work-items"]');
        if (workItemsNav) {
          document.querySelectorAll('.qd-nav-item[data-view]').forEach(function(n) {
            n.classList.remove('qd-nav-active');
          });
          workItemsNav.classList.add('qd-nav-active');
        }

        // Re-render list with query results
        var listEl = document.getElementById('qd-work-items-list');
        if (listEl) {
          if (window.QD.showView) window.QD.showView('work-items');

          if (results.length === 0) {
            listEl.innerHTML = '<p style="text-align:center;color:#605e5c;padding:32px">Query returned no results.</p>';
          } else {
            listEl.innerHTML = '';
            results.forEach(function(item) {
              var card = buildCard(item);
              listEl.appendChild(card);
            });
          }
        }

        window.QD.toast('Query "' + query.name + '" — ' + results.length + ' result(s).', 'info');
      })
      .catch(function(err) {
        window.QD.toast('Query failed: ' + err.message, 'error');
      });
  }

  /**
   * Prompts for a query name and saves current filters as a query.
   */
  function promptSaveQuery() {
    var name = prompt('Name for this query:');
    if (!name || !name.trim()) return;

    // Build filter array from active filter state
    // (QA_QUERIES format: [{ field, operator, value }])
    var filterClauses = [];

    // We read from the filter checkboxes directly
    var stateBoxes = document.querySelectorAll('[data-filter="state"]:checked');
    stateBoxes.forEach(function(cb) {
      filterClauses.push({ field: 'state', operator: '=', value: cb.value });
    });

    var typeBoxes = document.querySelectorAll('[data-filter="type"]:checked');
    typeBoxes.forEach(function(cb) {
      filterClauses.push({ field: 'workItemType', operator: '=', value: cb.value });
    });

    var areaInput = document.querySelector('[data-filter="areaPath"]');
    if (areaInput && areaInput.value.trim()) {
      filterClauses.push({ field: 'areaPath', operator: 'contains', value: areaInput.value.trim() });
    }

    var queryDoc = {
      id:      'QUERY-' + Date.now(),
      name:    name.trim(),
      filters: filterClauses,
      savedAt: new Date().toISOString()
    };

    QA_DB.saveQuery(queryDoc)
      .then(function() {
        window.QD.toast('Query "' + queryDoc.name + '" saved.', 'success');
        renderQueriesView();
      })
      .catch(function(err) {
        window.QD.toast('Save failed: ' + err.message, 'error');
      });
  }

  // ── SHARED HELPERS ─────────────────────────────────────────────────────────

  /** Builds a <select> element from an options array */
  function buildSelect(id, options, selected) {
    var opts = options.map(function(opt) {
      var val, label;
      if (Array.isArray(opt)) { val = opt[0]; label = opt[1]; }
      else { val = opt; label = opt; }
      return '<option value="' + window.QD.escHtml(String(val)) + '"' +
        (String(selected) === String(val) ? ' selected' : '') + '>' +
        window.QD.escHtml(label) + '</option>';
    }).join('');
    return '<select class="qd-field-select" id="' + id + '">' + opts + '</select>';
  }

  /** Builds a step-to-reproduce input row */
  function buildStepRow(index, value) {
    return '<div class="qd-step-row">' +
      '<span class="qd-step-num">' + index + '.</span>' +
      '<textarea class="qd-step-input" rows="1" ' +
      'placeholder="Step ' + index + '...">' +
      window.QD.escHtml(value || '') + '</textarea>' +
      '<button type="button" class="qd-step-del" title="Remove step">✕</button>' +
    '</div>';
  }

  /** Wires delete + renumber on step rows in a container */
  function wireStepDeletes(stepsEl) {
    if (!stepsEl) return;
    stepsEl.querySelectorAll('.qd-step-del').forEach(function(btn) {
      var newBtn = btn.cloneNode(true);
      btn.parentNode.replaceChild(newBtn, btn);
      newBtn.addEventListener('click', function() {
        this.closest('.qd-step-row').remove();
        var rows = stepsEl.querySelectorAll('.qd-step-row');
        rows.forEach(function(row, i) {
          var num = row.querySelector('.qd-step-num');
          if (num) num.textContent = (i + 1) + '.';
        });
      });
    });
  }

  /** Builds a minimal work item card for the queries results view */
  function buildCard(item) {
    var card = document.createElement('div');
    card.className = 'qd-work-item-card';
    card.setAttribute('data-id', item.id);

    var esc       = window.QD.escHtml;
    var typeSlug  = window.QD.typeToSlug(item.workItemType);
    var typeAbbr  = window.QD.typeToAbbr(item.workItemType);
    var stateSlug = window.QD.stateToSlug(item.state);

    card.innerHTML =
      '<div class="qd-card-type-icon qd-type-' + typeSlug + '">' + typeAbbr + '</div>' +
      '<div class="qd-card-body">' +
        '<div class="qd-card-title">' + esc(item.title || '(untitled)') + '</div>' +
        '<div class="qd-card-meta">' +
          '<span class="qd-card-id">' + esc(item.id) + '</span>' +
          (item.areaPath ? '<span>· ' + esc(item.areaPath) + '</span>' : '') +
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

  // ── EXPOSE ─────────────────────────────────────────────────────────────────

  window.QD_IE = {
    openNewItemModal:    openNewItemModal,
    openImportModal:     openImportModal,
    openExportJsonModal: openExportJsonModal,
    openExportMdModal:   openExportMdModal
  };

})();
