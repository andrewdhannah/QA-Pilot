# Sprint C-6 — Microsoft Teams App Shell
## Copilot Prompt — GitHub repo: andrewdhannah/QA-Pilot

You are working in the QA Pilot repository.
No CDN links, no external imports, no fetch(). File:// safe architecture.
Run `node build.js` from the `desktop/` folder after making changes.

---

## Context

QA Pilot Desktop is a Windows 11-style OS simulator. All apps live in `desktop/apps/<id>.html`
and are registered in `desktop/src/os-core.js` under the `APPS` constant.

This sprint adds **Microsoft Teams** as a new app in the OS. The app shell is a faithful
simulation of the real Teams web client: left rail icon bar, a sidebar showing the QA Team
channel, and a main message area. This sprint builds the static shell only — scripted
content and scoring will be wired in later sprints.

---

## Deliverable 1: Register the app in `src/os-core.js`

Add a `teams` entry to the `APPS` constant, after the `browser` entry. Match the exact
format of existing entries (id, title, short, inline SVG icon at 20×20/32×32 viewBox).

```javascript
// ── Microsoft Teams — indigo collaboration icon ──────────────────────────
teams: {
  id: "teams",
  title: "Microsoft Teams",
  short: "Teams",
  icon: `<svg width="20" height="20" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="28" height="28" rx="6" fill="#4f52b2"/><rect x="5" y="9" width="15" height="2.8" rx="1.4" fill="white"/><rect x="10.6" y="9" width="2.8" height="14" rx="1.4" fill="white"/><circle cx="24" cy="10" r="4" fill="#7678ed"/><circle cx="24" cy="9" r="2" fill="white" opacity="0.9"/><path d="M20.5 14.5 Q20.5 12.5 24 12.5 Q27.5 12.5 27.5 14.5" fill="white" opacity="0.75"/></svg>`,
},
```

**Important:** The `APPS` constant is in `src/os-core.js`. Do NOT modify `build.js`.

---

## Deliverable 2: Add a desktop icon in `index.html`

Find the section in `index.html` that contains desktop icon buttons (`data-app="..."` attributes).
Add a Teams icon button following the exact same markup pattern as the existing ones.

```html
<button class="qa-desktop-icon" data-app="teams" aria-label="Microsoft Teams">
  <span class="qa-desktop-icon-img">
    <svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="28" height="28" rx="6" fill="#4f52b2"/><rect x="5" y="9" width="15" height="2.8" rx="1.4" fill="white"/><rect x="10.6" y="9" width="2.8" height="14" rx="1.4" fill="white"/><circle cx="24" cy="10" r="4" fill="#7678ed"/><circle cx="24" cy="9" r="2" fill="white" opacity="0.9"/><path d="M20.5 14.5 Q20.5 12.5 24 12.5 Q27.5 12.5 27.5 14.5" fill="white" opacity="0.75"/></svg>
  </span>
  <span class="qa-desktop-icon-label">Teams</span>
</button>
```

Read the existing icon markup in `index.html` and match the pattern exactly —
class names, structure, and placement may differ slightly from this example.

---

## Deliverable 3: Create `apps/teams.html`

Create a new file `desktop/apps/teams.html`. This is the complete Teams app UI.

### Layout structure

```
┌─────────────────────────────────────────────────────────────────┐
│ [Rail] [Sidebar — 220px] [Main content area — flex 1]           │
└─────────────────────────────────────────────────────────────────┘
```

The app fills its window 100% width and height. Use flexbox.

### Left rail (48px wide)

Vertical strip of icon buttons. Active state uses indigo highlight.
Icons (top to bottom): Activity (bell), Chat (speech bubble), Teams (grid), Calendar (calendar).
Teams icon is the active one by default (indigo highlight circle behind it).
Clicking other rail icons does nothing — they are visual placeholders only.

At the bottom of the rail: a small circular avatar "AH" (Andrew Hannah initials)
in indigo, representing the signed-in user.

### Sidebar (220px wide)

Header: `Microsoft Teams` wordmark in small bold text, dark background.
Below: A collapsible section titled `Your teams` (open by default).
Inside: One team entry: `🔵 QA Team` — clicking it selects the `#General` channel below it.
The `#General` channel is shown selected (indigo left border, slightly highlighted row).
No other teams or channels are needed.

### Main content area

**Channel header bar:**
- `#General` channel name (bold, 15px)
- Description text: `QA Team — Sprint coordination and scenario review`
- Right side: Members icon showing `👤 3 members`

**Message thread area** (scrollable, fills remaining height, light grey background):
Display three placeholder messages to make the channel feel lived-in.
All messages are from before today. Use a realistic Teams message style:
avatar circle with initials | sender name (bold) + timestamp | message body.

Message 1 — from `EH` (Elyse Hannah), yesterday at 9:04 AM:
> "Sprint planning complete. New scenario assigned — check your queue when you're ready."

Message 2 — from `AH` (Andrew Hannah), yesterday at 9:12 AM:
> "Got it. Starting now."

Message 3 — from `QA Bot` (a bot, use a purple 🤖 avatar), yesterday at 9:13 AM:
> "Scenario assigned to Andrew Hannah. Status: In Progress. Good luck! 🎯"

**Message composer** (pinned to bottom, white bar):
A styled input box `placeholder="Type a message..."` with a Send button (paper plane icon ➤).
Typing and sending does nothing in this sprint — the composer is cosmetic only.

### Colour palette

```css
--teams-bg:         #1b1a26;   /* dark rail/sidebar */
--teams-sidebar:    #27263a;   /* sidebar background */
--teams-main:       #f3f2f1;   /* main content background */
--teams-active:     #5b5fc7;   /* active/selected indigo */
--teams-text:       #ffffff;   /* rail/sidebar text */
--teams-text-main:  #242424;   /* main content text */
--teams-border:     #3d3c52;   /* sidebar borders */
--teams-msg-bg:     #ffffff;   /* individual message bubble */
--teams-hover:      #3d3c52;   /* hover state */
--teams-timestamp:  #8e8ea0;   /* grey timestamp text */
```

### Theme handling

Listen for `APP_BOOT` and apply light/dark theme:

```javascript
window.addEventListener("message", function(event) {
  var msg = event.data;
  if (!msg) return;

  if (msg.type === "APP_BOOT" && msg.appId === "teams") {
    applyTheme(msg.theme || "light");
  }

  if (msg.type === "THEME_CHANGE" || msg.type === "ROLE_CHANGE") {
    if (msg.theme) applyTheme(msg.theme);
  }
});

function applyTheme(theme) {
  document.body.classList.remove("theme-light", "theme-dark");
  document.body.classList.add("theme-" + theme);
}
```

In light theme the main content area stays `#f3f2f1` (Teams always uses a light main pane).
The rail and sidebar always use the dark palette regardless of theme.

---

## What NOT to Change

- Do not modify `src/os-core.js` beyond the APPS constant entry
- Do not touch `build.js`, `os.css`, or any other app files
- Do not add CDN links, external fonts, or external images
- Do not rename or alter existing HTML element IDs in `index.html`

---

## Definition of Done

- [ ] `teams` entry added to `APPS` constant in `src/os-core.js` with correct `id`, `title`, `short`, `icon`
- [ ] Desktop icon button for Teams added to `index.html`, matching existing icon pattern
- [ ] `apps/teams.html` exists and renders without JavaScript errors
- [ ] App fills its window: left rail (48px) + sidebar (220px) + main pane (flex)
- [ ] Left rail shows Activity, Chat, Teams, Calendar icons — Teams icon has active/highlighted state
- [ ] Sidebar shows `QA Team` → `#General` channel selected with indigo left accent
- [ ] Main pane shows `#General` header and three placeholder messages in Teams message style
- [ ] Message composer is visible at the bottom with placeholder text and send icon
- [ ] `APP_BOOT` message is handled — `applyTheme()` called on boot
- [ ] `node build.js` runs without errors
- [ ] Opening Teams via double-click on the desktop icon shows the app in a window
