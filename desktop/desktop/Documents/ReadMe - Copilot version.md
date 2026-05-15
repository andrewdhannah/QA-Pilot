{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;\red38\green34\blue31;}
{\*\expandedcolortbl;;\cssrgb\c19608\c17647\c16078;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # Modular\uc0\u8209 OS v4  \
### Windows\uc0\u8209 11\u8209 Style QA Simulator Desktop\
\
Modular\uc0\u8209 OS v4 is a fully offline, self\u8209 contained Windows\u8209 11\u8209 style desktop simulator designed for QA training, scenario\u8209 based workflows, and enterprise\u8209 safe distribution.  \
It runs entirely from a single HTML file (for distribution) while maintaining a clean, modular development structure.\
\
This project powers realistic training scenarios for Dynamics, Azure DevOps, case investigation workflows, and role\uc0\u8209 based UI behavior \'97 all inside a simulated OS environment.\
\
---\
\
## \uc0\u10024  Features\
\
### \uc0\u55357 \u56741 \u65039  Windows\u8209 11\u8209 Style Desktop\
- Start Menu (centered)\
- Taskbar with pinned apps\
- Quick Settings panel\
- Notification Center\
- Lock screen with live clock/date\
- Smooth window manager (drag, snap, maximize, minimize, z\uc0\u8209 index)\
- Role switching (Junior \uc0\u8596  Senior Investigator)\
\
### \uc0\u55356 \u57256  Appearance & Personalization\
- Light/Dark theme\
- Background selector (Default / Sunrise / Glow)\
- Brightness control\
- **Visual Fidelity Mode**  \
  - **Windows 11 Mode** (Mica, Acrylic, Fluent shadows)  \
  - **Classic Mode** (lightweight, high\uc0\u8209 contrast)\
\
### \uc0\u55357 \u56550  Modular App System\
- Dynamics CRM (scenario\uc0\u8209 driven)\
- Azure DevOps (bug logging)\
- AC Panel (Acceptance Criteria)\
- Training (scenario loader)\
- Settings (live OS configuration)\
\
### \uc0\u55357 \u56538  Scenario Engine\
- Load scenarios via `window.OS.loadScenario(id)`\
- Fully isolated app iframes using `srcdoc`\
- No external network requests\
\
### \uc0\u55357 \u56594  Enterprise\u8209 Friendly\
- Runs from `file://`\
- Runs inside OneNote\
- No server required\
- No external dependencies\
- Fully self\uc0\u8209 contained build output\
\
---\
\
## \uc0\u55358 \u56817  Project Structure\
\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading98\sa240\pardirnatural\partightenfactor0

\fs30 \cf2 \kerning1\expnd0\expndtw1
apps\
/scenarios\
/src/os-core.js\
/os.css\
index.html (dev only)\
build.js\
dist/qa-desktop.html (generated)\
\
---\
\
## \uc0\u55357 \u56960  Development\
\
1. Edit modular files (`os-core.js`, `os.css`, apps, scenarios)\
2. Run the bundler:\
node build.js\
4. For distribution, use the generated `qa-desktop.html` (single-file build)\
---\
## \uc0\u55357 \u56550  Distribution\
The build script produces:\
dist/qa-desktop.html\
\
This file contains:\
- Inlined CSS\
- Inlined JS bundle\
- Embedded apps\
- Embedded scenarios\
\
It is the **only file** required for:\
- OneNote embedding  \
- Email distribution  \
- Offline training  \
- Enterprise environments  \
--\
## \uc0\u55357 \u56541  Documentation\
- [CHANGELOG.md](CHANGELOG.md)\
- [ARCHITECTURE.md](ARCHITECTURE.md)\
- [ROADMAP.md](ROADMAP.md)\
---\
## \uc0\u55358 \u56605  Contributions\
Pull requests are welcome.  \
This project is intentionally modular so new apps, scenarios, and UI components can be added easily.\
---\
## \uc0\u55357 \u57057 \u65039  License\
MIT License.\
}