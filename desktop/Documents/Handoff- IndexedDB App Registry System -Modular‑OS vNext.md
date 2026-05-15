📘 Handoff: IndexedDB App Registry System (Modular‑OS vNext)
A future upgrade to replace hard‑coded APPS with a dynamic, database‑driven system.

🎯 Purpose
This system replaces the static APPS object in os-core.js with a dynamic, persistent, IndexedDB‑backed registry.

It enables:

Add/Remove Programs

Enable/Disable apps

Reset app state

Install new apps without editing OS code

Per‑user app configurations

Future “App Store” functionality

A real Settings → Apps & Features panel

This aligns with your training platform’s architecture:
db.js is the only file that touches IndexedDB. Everything else calls db.js.

🧩 System Overview
The App Registry System consists of:

1. New IndexedDB Object Store
Code
apps
Stores metadata for each installed app.

2. New DB Functions in db.js
dbGetApp(id)

dbGetAllApps()

dbSaveApp(app)

dbDeleteApp(id)

3. OS Bootloader Update
os-core.js loads apps from DB instead of a hard‑coded object.

4. Settings → Apps & Features Panel
A UI that lists installed apps and allows:

Enable / Disable

Reset App State

Uninstall

Install New App

5. Optional Future Enhancements
App categories

App permissions

App versioning

App store manifest

🏗️ Data Model
Each app record stored in IndexedDB looks like:

json
{
  "id": "browser",
  "title": "Edge — Training Browser",
  "short": "Browser",
  "icon": "🌐",
  "html": "apps/browser.html",
  "enabled": true,
  "system": false
}
Fields Explained
Field	Purpose
id	Unique app identifier (matches folder name)
title	Full window title
short	Short label for taskbar / start menu
icon	Emoji or SVG
html	Path to the app’s HTML file
enabled	Whether the app appears in the OS
system	If true, cannot be uninstalled (e.g., Settings)


🗄️ Database Schema Update
Add this to onupgradeneeded in db.js:

js
if (!database.objectStoreNames.contains('apps')) {
  database.createObjectStore('apps', { keyPath: 'id' });
}
🧰 New DB Functions
Get one app
js
function dbGetApp(id) {
  return _get('apps', id);
}
Get all apps
js
function dbGetAllApps() {
  return _getAll('apps');
}
Save or update an app
js
function dbSaveApp(app) {
  return _put('apps', app);
}
Delete an app
js
function dbDeleteApp(id) {
  return _delete('apps', id);
}
🚀 OS Bootloader Changes
Replace the static APPS object with:

js
async function loadAppsFromDB() {
  await initDB();
  const apps = await dbGetAllApps();

  window.APPS = {};
  apps.forEach(app => {
    if (app.enabled) {
      window.APPS[app.id] = app;
    }
  });
}
Then in OS boot:

js
await loadAppsFromDB();
OS.boot();
🖥️ Settings → Apps & Features Panel
This becomes a real control panel.

UI Elements per app:
Icon

Title

Enabled toggle

Reset App State button

Uninstall button (unless system: true)

Actions:
Enable/Disable
js
app.enabled = !app.enabled;
dbSaveApp(app);
Reset App State
js
OS.resetAppState(app.id);
Uninstall
js
dbDeleteApp(app.id);
Install New App
A modal that collects:

id

title

icon

html path

Then:

js
dbSaveApp(newApp);
🧱 Initial App Population
On first run, populate the DB with your default apps:

Dynamics

ADO

AC Viewer

Training

Settings

Browser (optional)

This can be done in:

onupgradeneeded

Or a first‑run script in os-core.js

🔮 Future Extensions (Optional)
App Categories
Code
productivity, training, system, tools
App Permissions
Code
canAccessDB, canOpenWindows, canReadScenarios
App Versioning
Code
version: "1.0.3"
App Store
A local JSON manifest that installs apps into IndexedDB.

📦 Deliverables (When You Build This)
When you’re ready to implement this system, Co‑P will generate:

Updated db.js

Updated os-core.js

Updated Settings UI

App installer modal

Migration script for existing apps

All clean, modular, and file://‑safe.

🏁 Status: Tabled for Future Version
This handoff is complete and ready for implementation when you decide to move to:

Modular‑OS v5 — Dynamic App Registry Edition

Whenever you’re ready to pick this back up, just say:

“Co‑P, let’s build the app registry system.”

And we’ll resume right where we left off.