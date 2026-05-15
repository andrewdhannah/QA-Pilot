# GitHub Release Checklist
## Modular OS v4 — andrewdhannah/Modular-OS-v4

Work through this before or after V1 sprints complete.
Items marked ⚡ are quick (under 2 minutes each).

---

## Files to Add to the Repo

### 1. CHANGELOG.md ⚡
- Copy `CHANGELOG.md` (created by Ash) into the repo root
- Update the [Unreleased] section once OS sprints complete
- Commit and push

### 2. Move Capture1.JPG ⚡
- Create an `assets/` folder in the repo root
- Move `Capture1.JPG` into `assets/screenshot.jpg`
- Update the README if it references the image path
- Commit and push

### 3. Push local Documents/ content
The following files exist locally but are not in the repo:
- `Documents/Architecture.md` → push as `docs/ARCHITECTURE.md`
- `Documents/RoadMap.md` → push as `docs/ROADMAP.md`
These add credibility and context for contributors.

---

## README Fix (2 minutes)

One broken placeholder in the current README.md:

Find this line:
```
https://github.com/username/windows-11-desktop-simulator
```

Replace `username` with the actual GitHub username of the original repo.
If you don't have it, remove the link entirely and just cite the project name.

---

## GitHub Repo Settings (5 minutes total)

### Add Topics ⚡
Go to: repo → ⚙ (gear icon next to About) → Topics

Suggested tags:
```
html javascript css offline training simulator qa-testing
windows11 single-file enterprise onboarding
```

### Update About description ⚡
Current description is the long README opener. Replace with something short:
```
Portable Windows 11-style desktop simulator for QA onboarding training.
Runs from a single HTML file — no install, no server, no dependencies.
```

### Enable GitHub Pages (5 minutes)
This gives you a live demo URL without anyone needing to download.

1. Go to: Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main` / `/ (root)`
4. Save

GitHub will serve `dist.html` at:
`https://andrewdhannah.github.io/Modular-OS-v4/dist.html`

Add that URL to the README and the repo About section.
It's the single most impactful thing for repo credibility.

---

## Create the GitHub Release (10 minutes)

This is the most important missing piece — "No releases published" looks unfinished.

### Step 1 — Tag the current commit
```bash
git tag v0.4.0
git push origin v0.4.0
```

Or create the tag directly in GitHub:
Releases → Draft a new release → Choose a tag → type `v0.4.0` → Create new tag

### Step 2 — Write release notes
Title: `v0.4.0 — Modular OS (Build System + Full App Suite)`

Body (copy/paste and edit):
```
## What's in this release

QA Simulator Desktop is a portable Windows 11-style desktop environment
for QA onboarding training. It runs entirely from a single HTML file —
no install, no server, no internet connection required.

### What's included
- Full OS shell: window manager, taskbar, start menu, notifications, lock screen
- Four mock apps: Dynamics CRM, Azure DevOps, AC Panel, Training
- Junior / Senior role system with field-level access control
- Light / dark theme, wallpaper, fidelity mode
- Scenario data layer (`window.SCENARIOS`)
- Single-file distribution build via `node build.js`

### How to use
Download `dist.html` below and open it in Chrome or Edge.
No setup required.

### Known limitations
- Capstone assessment and certificate flow are in progress (v1.0.0)
- Scenario scoring engine not yet wired to the OS shell
```

### Step 3 — Attach dist.html as a release asset
On the release draft page, drag `dist.html` into the "Attach binaries" area.
This is what gives users the direct download button.

### Step 4 — Publish
Click "Publish release."

---

## After V1 Sprints Complete

When all 10 sprints are done and end-to-end works:

1. Update CHANGELOG.md — move [Unreleased] items to [1.0.0]
2. Tag `v1.0.0`
3. Create a new GitHub release with the updated dist.html
4. Update the README demo link if you've enabled GitHub Pages

---

## Priority Order

| Priority | Task | Time |
|---|---|---|
| 🔴 Must | Create GitHub release (v0.4.0) + attach dist.html | 10 min |
| 🔴 Must | Fix README attribution placeholder | 2 min |
| 🟡 Should | Add CHANGELOG.md | 2 min |
| 🟡 Should | Add GitHub Topics | 2 min |
| 🟡 Should | Enable GitHub Pages | 5 min |
| 🟢 Nice | Update About description | 1 min |
| 🟢 Nice | Move screenshot to assets/ | 2 min |
| 🟢 Nice | Push docs/ARCHITECTURE.md and docs/ROADMAP.md | 5 min |
