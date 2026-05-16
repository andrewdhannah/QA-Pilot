# Sprint C-13 — Reports App: Live IndexedDB Analytics
## Copilot Prompt — GitHub repo: andrewdhannah/QA-Pilot

You are working in the QA Pilot repository.
No CDN links, no external imports, no fetch(). File:// safe architecture.
Run `node build.js` from the `desktop/` folder after making changes.

**Prerequisites:** SPRINT-C10 merged (scoring.js bundled). At least one capstone submission
must exist in IndexedDB to test against — run through capstone.html and submit to generate data.

---

## Context

`desktop/apps/reports.html` currently opens but shows stub content — no real data.

The Reports app is the facilitator's window into trainee performance. It should read
capstone results from IndexedDB and present them clearly: who submitted, what scenario,
score, pass/fail, which bugs they missed, which ADO reports were incomplete.

Results are written to IndexedDB by the OS on Submit (via `db.js` bridge).
Read `desktop/js/db.js` to understand the exact store name and record structure
before writing any query code.

---

## Deliverable: `desktop/apps/reports.html`

**Read the existing `reports.html` before writing anything.**
**Read `desktop/js/db.js`** to understand: DB name, store name, key path, and record shape.
Read `apps/settings.html` for sidebar navigation pattern to match.

---

## Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Reports                                              [Refresh] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Summary                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │    3     │  │    2     │  │    1     │  │   72%    │       │
│  │ Sessions │  │  Passed  │  │  Failed  │  │ Avg Score│       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                 │
│  Session Results                                                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Case ID            Scenario   Score   Result  Date      │    │
│  │ capstone-2-17...   case-001   5/6     ✅ Pass  May 14   │    │
│  │ capstone-2-16...   case-001   2/6     ❌ Fail  May 13   │    │
│  │ ...                                                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  [Selected row detail panel — see below]                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Reading from IndexedDB

**Read `desktop/js/db.js` before writing this.** The exact DB name, store name, and
record schema are defined there. Do not guess — use what the file specifies.

Use a standard IndexedDB read pattern:

```javascript
/**
 * loadResults()
 * Opens the QA Pilot IndexedDB and reads all records from the results store.
 * Calls renderResults(records) on success.
 * Shows an error message if the DB cannot be opened or has no records.
 */
function loadResults() {
  var dbName    = /* read from db.js */;
  var storeName = /* read from db.js */;

  var req = indexedDB.open(dbName);

  req.onerror = function() {
    showMessage("Could not open results database.");
  };

  req.onsuccess = function(e) {
    var db    = e.target.result;

    if (!db.objectStoreNames.contains(storeName)) {
      showMessage("No results found. Complete a capstone assessment to generate data.");
      db.close();
      return;
    }

    var tx      = db.transaction(storeName, "readonly");
    var store   = tx.objectStore(storeName);
    var all     = store.getAll();

    all.onsuccess = function() {
      var records = all.result || [];
      if (records.length === 0) {
        showMessage("No results found. Complete a capstone assessment to generate data.");
      } else {
        renderResults(records);
      }
      db.close();
    };

    all.onerror = function() {
      showMessage("Error reading results.");
      db.close();
    };
  };
}
```

Call `loadResults()` on page load and when the Refresh button is clicked.

---

## Summary bar

Calculate from all records:

```javascript
function buildSummary(records) {
  var total   = records.length;
  var passed  = records.filter(function(r) { return r.passed; }).length;
  var failed  = total - passed;
  var avgPct  = total > 0
    ? Math.round(records.reduce(function(sum, r) {
        return sum + (r.percentage || 0);
      }, 0) / total)
    : 0;

  // Update the four stat tiles: total, passed, failed, avgPct
}
```

Colour the "Avg Score" tile: green if ≥ 70%, amber if 50–69%, red if < 50%.

---

## Results table

Columns: Case ID (truncated to 20 chars), Scenario ID, Score (e.g. "5 / 6"), Result (✅ Pass / ❌ Fail), Date (formatted as "May 14 2026").

Sort records by `startedAt` descending (most recent first).

Clicking a row expands a detail panel below the table (or replaces the table footer area):

```
Detail — capstone-2-1715700000000
Scenario:    case-001
Score:       5 / 6  (83%)   ✅ PASS
Started:     May 14 2026, 14:32

Bugs found in CRM:     ✅ status-junior-escalated
                       ❌ future-date-allowed  ← missed

ADO Reports filed:
  ✅ "Status set to Escalated for Junior role"  (complete, correct AC)
  ⚠️  "Date field invalid"  (incomplete — missing steps to reproduce)
```

Map `missedBugs` IDs to readable names using this lookup:

```javascript
var BUG_LABELS = {
  "status-junior-escalated":  "Case Status: Escalated (Junior role violation)",
  "escalation-reason-blank":  "Escalation Reason: blank when Status is Escalated",
  "future-date-allowed":      "Created Date: set to a future date",
};
```

For `badReports`, show the report title (from `r.title`) with ⚠️ and the reason it was incomplete.

---

## postMessage handling

The Reports app is embedded in an OS window. Handle `APP_BOOT`:

```javascript
window.addEventListener("message", function(e) {
  if (e.data && e.data.type === "APP_BOOT") {
    loadResults(); // refresh on boot
  }
});
```

---

## Empty state and error states

| State | Message shown |
|-------|--------------|
| No DB yet | "No results found. Complete a capstone assessment to generate data." |
| DB open error | "Could not open the results database." |
| DB has records but store missing | "Results store not found — the database may be from an older version." |
| Records present | Render normally |

---

## Styling

Match `apps/settings.html` and `apps/dynamics.html` design language.
Summary stat tiles: card-style, centered number in large font, label below.
Results table: clean rows, hover highlight, selected row highlighted.
Detail panel: subtle background, monospace for IDs, colour-coded ✅ / ❌ / ⚠️.
No CDN, no external fonts.

---

## What NOT to Change

- Do not modify `db.js` — read from it, don't edit it
- Do not modify any other app files
- Do not modify `os-core.js` or `build.js`
- Do not add CDN links

---

## After the fix is applied

Update `FEATURE-STATUS.md` in the repo root:

| Row | New status |
|-----|-----------|
| Reports app — App opens | ✅ |
| Reports app — Analytics data | ✅ |

---

## Definition of Done

- [ ] Reports app opens and calls `loadResults()` on boot
- [ ] Summary bar shows total sessions, passed, failed, average score %
- [ ] Results table renders all records sorted newest-first
- [ ] Clicking a row shows the detail panel with bugs found/missed and ADO report quality
- [ ] Refresh button re-queries IndexedDB
- [ ] Empty state message shown when no results exist
- [ ] `APP_BOOT` message handled
- [ ] Styling consistent with other apps
- [ ] No CDN, no external dependencies
