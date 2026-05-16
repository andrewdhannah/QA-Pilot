# QA Platform — Code Commenting Style Guide
## For Gemma: How to Comment Every File You Write or Edit

This guide defines the exact commenting standard for this project.
**Every file you produce must follow this standard without exception.**
These comments exist because the developer learning this codebase needs
to understand not just *what* the code does, but *why* each decision was made.

---

## The Three Levels of Comments

### Level 1 — File Header Block
Every JS file starts with a full header block. Every HTML file's `<script>` tag
starts with a shorter version. Use this exact format:

```javascript
/**
 * =============================================================================
 * filename.js — One-Line Description of What This File Does
 * =============================================================================
 * QA Onboarding Training Platform
 *
 * PURPOSE:
 * 2-4 sentences explaining why this file exists and what problem it solves.
 * Not what functions are in it — that comes later. Why does this file exist
 * as a separate thing?
 *
 * HOW TO USE THIS FILE:
 * Concrete instructions for a developer using this file for the first time.
 * Include any required load order, setup calls, or dependencies.
 *
 * WHAT'S IN HERE:
 * - Section 1: [name] — one-line description
 * - Section 2: [name] — one-line description
 *
 * READS FROM:   [what data sources does this file read]
 * WRITES TO:    [what does this file write to]
 *
 * =============================================================================
 */
```

### Level 2 — Section Headers
Every logical group of functions gets a section header. Use this exact format.
The dashes extend to column 80. Copy the format exactly:

```javascript
// ── SECTION 1: SECTION NAME IN CAPS ───────────────────────────────────────────
```

### Level 3 — Function JSDoc
Every function — no exceptions — gets a JSDoc block immediately above it:

```javascript
/**
 * functionName(param1, param2)
 * One sentence: what this function does.
 *
 * Second paragraph if needed: why this function exists, or important
 * behaviour the caller needs to know about. Skip if one sentence covers it.
 *
 * @param {type} param1 - What this parameter is. Include expected values.
 * @param {type} param2 - What this parameter is. e.g. 'junior' or 'senior'
 * @returns {type} What is returned. e.g. The student object, or null if not found.
 */
function functionName(param1, param2) {
```

### Level 4 — Inline Comments
Non-obvious lines get a short comment on the same line or the line above.
The rule: if you had to think about it for more than 5 seconds, comment it.

```javascript
// RIGHT — explains the why, not just the what:
var tx = _db.transaction(storeName, 'readonly');  // 'readonly' = no writes, safer

// WRONG — just restates the code:
var tx = _db.transaction(storeName, 'readonly');  // creates a transaction
```

---

## Real Worked Example — From This Project's db.js

This is exactly how the commenting standard looks in practice.
Your output should match this quality throughout.

```javascript
/**
 * =============================================================================
 * db.js — IndexedDB Database Module
 * =============================================================================
 * QA Onboarding Training Platform
 *
 * PURPOSE:
 * This is the ONLY file that reads from or writes to IndexedDB.
 * No other file should touch IndexedDB directly. All other files call
 * the functions in this file to read or save data.
 *
 * HOW TO USE THIS FILE:
 * Every page that needs data must:
 *   1. Load this file in a <script> tag.
 *   2. Call initDB() and wait for it to finish before calling anything else.
 * All functions are ASYNCHRONOUS — they return Promises.
 * Use .then() or await to get the result.
 *
 * WHAT'S IN HERE:
 * - Section 1: Database constants
 * - Section 2: Database initialisation (initDB)
 * - Section 3: Internal helper functions (_get, _getAll, _put)
 * - Section 4: Student functions
 * - Section 5: Progress functions
 * - Section 6: Assignment functions
 * - Section 7: Settings functions
 *
 * =============================================================================
 */


// ── SECTION 1: DATABASE CONSTANTS ─────────────────────────────────────────────

// The name IndexedDB uses to identify our database in the browser.
// If you change this name, the browser creates a brand-new empty database.
const DB_NAME = 'qa_onboarding_db';

// Version number. Increment this when you add new stores or change the schema.
// The browser runs the onupgradeneeded handler again when the version increases.
const DB_VERSION = 1;

// Cached database reference. Stored here after initDB() opens the connection
// so we don't have to re-open it on every function call.
let _db = null;


// ── SECTION 2: DATABASE INITIALISATION ────────────────────────────────────────

/**
 * initDB()
 * Opens the IndexedDB database and creates all object stores on first run.
 * Must be called on every page load before any other db function is used.
 *
 * What it does:
 *   - If the database exists: opens it and returns the connection.
 *   - First run: creates all stores, then returns the connection.
 *   - Already open: returns the cached connection immediately (no re-open).
 *
 * @returns {Promise<IDBDatabase>} Resolves with the open database connection.
 */
function initDB() {
  return new Promise(function(resolve, reject) {

    // If we already have an open connection, return it immediately.
    // This prevents opening the database multiple times on the same page.
    if (_db) {
      resolve(_db);
      return;
    }

    // Ask the browser to open (or create) our database at the given version.
    var request = indexedDB.open(DB_NAME, DB_VERSION);

    // onupgradeneeded fires when:
    //   - The database is being created for the first time (new install)
    //   - DB_VERSION has been incremented (schema change)
    // This is the ONLY place where you can create or delete object stores.
    request.onupgradeneeded = function(event) {
      var database = event.target.result;

      // CREATE STUDENTS STORE
      // Stores one record per student. Key field = caseId.
      // { keyPath: 'caseId' } tells IndexedDB to use caseId as the record key.
      if (!database.objectStoreNames.contains('students')) {
        database.createObjectStore('students', { keyPath: 'caseId' });
      }

      // CREATE PROGRESS STORE
      // Stores one progress record per student. Key = caseId.
      if (!database.objectStoreNames.contains('progress')) {
        database.createObjectStore('progress', { keyPath: 'caseId' });
      }
    };

    // onsuccess fires once the database is open and ready to use.
    request.onsuccess = function(event) {
      _db = event.target.result;  // Cache the connection for reuse on this page
      resolve(_db);
    };

    // onerror fires if the browser refused to open the database.
    // Common cause: private/incognito mode with storage blocked.
    request.onerror = function(event) {
      console.error('db.js: Failed to open IndexedDB.', event.target.error);
      reject(event.target.error);
    };
  });
}


// ── SECTION 3: INTERNAL HELPER FUNCTIONS ──────────────────────────────────────
// These wrap the low-level IndexedDB API in reusable Promises.
// They are used only inside this file — call the named functions below instead.

/**
 * _get(storeName, key)
 * Fetches a single record from a store by its primary key.
 * Returns undefined (not null) if no record with that key exists.
 * Internal — use getStudent(), getProgress() etc. from outside this file.
 *
 * @param {string} storeName - Which store to read from. e.g. 'students'
 * @param {string} key       - The key to look up. e.g. 'CASE-00001'
 * @returns {Promise<Object|undefined>} The record, or undefined if not found.
 */
function _get(storeName, key) {
  return new Promise(function(resolve, reject) {
    // 'readonly' transaction — we are only reading, not changing any data.
    var tx = _db.transaction(storeName, 'readonly');
    var store = tx.objectStore(storeName);
    var request = store.get(key);

    request.onsuccess = function() {
      resolve(request.result);  // request.result is the record, or undefined
    };
    request.onerror = function() {
      reject(request.error);
    };
  });
}
```

---

## HTML Page Script Block Standard

For the `<script>` block inside each HTML page, use this format:

```html
<script>
  /**
   * pagename.html — Page Logic
   * ==========================
   * WHAT THIS PAGE DOES:
   * - Bullet 1: what this page shows or handles
   * - Bullet 2: what interactions are available
   *
   * FLOW:
   * 1. initDB() opens the database
   * 2. requireLogin() checks for a valid session — redirects if not found
   * 3. Load student + progress records from IndexedDB
   * 4. Render the page based on those records
   *
   * READS FROM:   IndexedDB via db.js (which stores)
   * WRITES TO:    IndexedDB via db.js (which stores)
   * REDIRECTS TO: where and under what condition
   */


  // ── SECTION 1: PAGE STATE ──────────────────────────────────────────────────
  // Variables that hold the current page's working data.
  // Declared here so all functions can access them.

  var currentSession  = null;   // Set by requireLogin() — contains caseId and role
  var currentStudent  = null;   // Full student record from IndexedDB
  var currentProgress = null;   // Progress record from IndexedDB


  // ── SECTION 2: INITIALISE ─────────────────────────────────────────────────

  // initDB() must complete before we can call any db.js functions.
  // We chain .then() calls to run steps in order after the DB is ready.
  initDB()
    .then(function() {
      // requireLogin() checks sessionStorage for a valid student session.
      // If none found, it redirects to index.html and returns null.
      currentSession = requireLogin();
      if (!currentSession) return;  // Stop here — redirect already fired

      // Load the student record and progress record at the same time.
      // Promise.all() runs both requests in parallel, then waits for both.
      return Promise.all([
        getStudent(currentSession.caseId),
        getProgress(currentSession.caseId),
      ]);
    })
    .then(function(results) {
      if (!results) return;  // requireLogin() redirected — nothing to do

      currentStudent  = results[0];  // Index 0 matches first getStudent() call
      currentProgress = results[1];  // Index 1 matches second getProgress() call

      renderPage();  // Now we have data — build the UI
    })
    .catch(function(error) {
      // Something went wrong with the DB — show a clear error, don't crash silently
      console.error('Page init failed:', error);
      showToast('Unable to load your data. Please refresh.', 'error');
    });


  // ── SECTION 3: RENDER ─────────────────────────────────────────────────────

  /**
   * renderPage()
   * Builds the page UI using the loaded student and progress data.
   * Called once on load after initDB() and data fetches complete.
   */
  function renderPage() {
    // Populate the topbar with the student's name
    document.getElementById('user-name-display').textContent = currentStudent.name;

    // ... rest of render logic
  }

</script>
```

---

## What NOT to Do

```javascript
// ❌ No comment — reader has no idea why this check exists
if (!progress.chaptersRead) progress.chaptersRead = {};

// ✅ Inline comment explains the defensive check
if (!progress.chaptersRead) progress.chaptersRead = {};  // Field may not exist on older records — initialise safely


// ❌ Comment just restates the code
var next = highest + 1;  // add 1 to highest

// ✅ Comment explains the intent
var next = highest + 1;  // Start one above the current maximum, then verify it's not taken


// ❌ Missing JSDoc — reader must read the whole function to understand it
function findStudentByEmail(email) {
  ...
}

// ✅ JSDoc explains inputs, outputs, and edge cases upfront
/**
 * findStudentByEmail(email)
 * Searches all student records for a matching email address.
 * Comparison is case-insensitive — 'Jane@Acme.com' matches 'jane@acme.com'.
 * Returns null (not undefined) when no match is found — easier to check.
 *
 * @param {string} email - The email address to search for.
 * @returns {Promise<Object|null>} The student record, or null if not found.
 */
function findStudentByEmail(email) {
  ...
}
```

---

## Quick Reference Checklist

Before submitting any file, verify:

- [ ] File header block present and filled in (not just copied template)
- [ ] Every logical group has a `// ── SECTION N: NAME ──` header
- [ ] Every function has a JSDoc block (even one-liners)
- [ ] Every non-obvious line has an inline comment explaining *why*
- [ ] No comment just restates what the code already says
- [ ] Section headers in HTML `<script>` blocks match the JS standard
- [ ] Page-level script block starts with the page description comment

## Section 5: Modular OS & Iframe Communication

### 5.1 The Parent-Child Handshake
Since apps (Dynamics/ADO) run in iframes, they must never assume they are the top-level window.
- **Rule:** Always use `window.parent` checks before calling OS functions.
- **Rule:** Use `postMessage` for state updates to ensure the OS shell knows when a "Bug" is logged or a "Case" is opened.

### 5.2 Zero-Dependency Architecture
The simulator must remain a single-file `dist.html` once built.
- **Rule:** No `import` statements for external libraries. 
- **Rule:** All CSS must be scoped with a prefix (e.g., `.dyn-` for Dynamics, `.ado-` for Azure DevOps) to prevent style bleeding when inlined.

### 5.3 Role-Based Logic
- **Rule:** Apps must fetch the current role via `window.parent.QA_OS.getRole()` on init.
- **Rule:** DOM elements restricted by role must be REMOVED, not just hidden, to prevent "Inspect Element" cheating by students.
