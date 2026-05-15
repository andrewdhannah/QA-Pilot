# QA Pilot — One-Time Setup

Follow these steps once to merge both projects into the final folder structure.
After this, everything lives in one place and `node build.js` keeps it all in sync.

---

## Step 1 — Rename the root folder

Rename `Testing Onboarding Offline Site` → `QA Pilot`

On your flash drive or in File Explorer, just right-click the folder and rename it.

---

## Step 2 — Move the OS into a `desktop/` subfolder

Move (or copy) the entire `ModularOSv4` folder from your Desktop into the
`QA Pilot` root folder, then rename it `desktop`.

End result:

```
QA Pilot/
├── index.html          ← Academy login (entry point)
├── course.html
├── lesson-1.html
├── lesson-2.html
├── lesson-3.html
├── lesson-4.html
├── capstone.html
├── certificate.html
├── css/
├── js/
├── data/
├── admin/
└── desktop/            ← Was "ModularOSv4" — renamed to "desktop"
    ├── index.html
    ├── os.css
    ├── src/os-core.js
    ├── apps/
    ├── scenarios/
    ├── build.js        ← Run this after any OS change
    ├── package.json
    ├── os.bundle.js
    └── dist.html
```

---

## Step 3 — Run the build

Open a terminal in the `desktop/` folder and run:

```
node build.js
```

This does three things automatically:
1. Rebuilds `os.bundle.js` (for development)
2. Rebuilds `dist.html` (the standalone distributable OS)
3. Updates `capstone.html` in the parent folder with the new OS content

You'll see:
```
✓ Built: os.bundle.js
✓ Built: dist.html
✓ Synced: capstone.html (getOSContent updated with current OS build)
✓ QA Pilot Desktop build complete.
```

---

## Step 4 — Verify

Open `QA Pilot/index.html` in your browser.
- You should see the QA Pilot Academy login screen.
- Complete a lesson and reach the Capstone — the OS desktop should load.
- Open `QA Pilot/desktop/dist.html` directly — the OS should also work standalone.

---

## Ongoing workflow

| What changed | What to do |
|---|---|
| OS apps, scenarios, or os-core.js | Run `node build.js` from `desktop/` |
| Lesson content (lesson-1.html etc.) | Edit directly — no build step needed |
| Admin settings | Edit directly — no build step needed |
| capstone.html | Do NOT hand-edit — build.js rewrites it automatically |

---

## Distribution (SharePoint / OneNote / USB / Email)

For the **Academy** (full lesson platform): share the entire `QA Pilot/` folder.
For the **OS only** (demo / standalone): share just `QA Pilot/desktop/dist.html` — it is a
single self-contained file and needs nothing else.
