{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;\f1\fswiss\fcharset0 Helvetica-Bold;}
{\colortbl;\red255\green255\blue255;\red38\green34\blue31;\red0\green0\blue0;\red0\green0\blue0;
\red243\green226\blue213;}
{\*\expandedcolortbl;;\cssrgb\c19608\c17647\c16078;\cssrgb\c0\c0\c0;\cssrgb\c0\c0\c0\c84706\cname labelColor;
\cssrgb\c96471\c90980\c86667;}
{\*\listtable{\list\listtemplateid1\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid1\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid1}
{\list\listtemplateid2\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid101\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid2}
{\list\listtemplateid3\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid201\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid3}
{\list\listtemplateid4\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid301\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid4}
{\list\listtemplateid5\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid401\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid5}
{\list\listtemplateid6\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid501\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid6}
{\list\listtemplateid7\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid601\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid7}
{\list\listtemplateid8\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid701\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid8}
{\list\listtemplateid9\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid801\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid9}}
{\*\listoverridetable{\listoverride\listid1\listoverridecount0\ls1}{\listoverride\listid2\listoverridecount0\ls2}{\listoverride\listid3\listoverridecount0\ls3}{\listoverride\listid4\listoverridecount0\ls4}{\listoverride\listid5\listoverridecount0\ls5}{\listoverride\listid6\listoverridecount0\ls6}{\listoverride\listid7\listoverridecount0\ls7}{\listoverride\listid8\listoverridecount0\ls8}{\listoverride\listid9\listoverridecount0\ls9}}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # Architecture  \
### Modular\uc0\u8209 OS v4 \'97 Windows\u8209 11\u8209 Style QA Simulator Desktop\
\
This document describes the internal architecture of Modular\uc0\u8209 OS v4, including the OS engine, window manager, app system, scenario loader, and build pipeline.\
\
---\
\
# 1. High\uc0\u8209 Level Overview\
\
Modular\uc0\u8209 OS v4 is composed of:\
\
- **OS Engine** (`src/os-core.js`)\
- **UI Layer** (`os.css`)\
- **Apps** (`/apps/*.html`)\
- **Scenarios** (`/scenarios/*.js`)\
- **Dev Shell** (`index.html`)\
- **Bundler** (`build.js`)\
- **Distribution Output** (`dist/qa-desktop.html`)\
\
The system behaves like a lightweight Windows 11 shell running entirely offline.\
\
---\
\
# 2. OS Engine (`os-core.js`)\
\
The OS engine is responsible for:\
\
### Window Manager\
- Create windows\
- Drag windows\
- Snap left/right\
- Maximize/minimize\
- Z\uc0\u8209 index stacking\
- Active window tracking\
- Smooth movement\
\
### Start Menu\
- App launcher\
- Role switcher\
- Live updates\
\
### Taskbar\
- App grouping\
- Window activation\
- Minimize/restore logic\
\
### Quick Settings\
- Theme switching\
- Brightness control\
- Background selection\
- Visual Fidelity Mode\
\
### Notification Center\
- Push notifications\
- Clear notifications\
\
### Lock Screen\
- Live clock/date\
- Unlock behavior\
\
### OS API (exposed to apps)\
```js\
window.OS = \{\
  getRole(),\
  getFidelity(),\
  setTheme(),\
  setBackground(),\
  setFidelity(),\
  notify(),\
  openApp(),\
  installApp(),\
  uninstallApp(),\
  loadScenario(),\
  completeTask()\
\}\
\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading45\sb240\sa200\pardirnatural\partightenfactor0

\f1\b\fs44 \cf2 \kerning1\expnd-1\expndtw-4
3. App System
\f0\b0\fs30 \cf3 \kerning1\expnd0\expndtw0 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading98\sa240\pardirnatural\partightenfactor0
\cf2 \kerning1\expnd0\expndtw1
Apps are loaded into iframes using:\
<iframe srcdoc="..."></iframe>\
Each app is:\cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sb80\sa200\pardirnatural\partightenfactor0
\ls1\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Fully isolated\cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sa200\pardirnatural\partightenfactor0
\ls1\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Self\uc0\u8209 contained\cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sa280\pardirnatural\partightenfactor0
\ls1\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Communicates only via 
\fs28 \cb5 \kerning1\expnd0\expndtw1
window.parent.OS
\fs30 \cf4 \cb1 \kerning1\expnd0\expndtw0 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading98\sa240\pardirnatural\partightenfactor0
\cf2 \kerning1\expnd0\expndtw1
Apps include:\cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sb80\sa200\pardirnatural\partightenfactor0
\ls2\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Dynamics\cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sa200\pardirnatural\partightenfactor0
\ls2\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Azure DevOps\cf4 \kerning1\expnd0\expndtw0 \
\ls2\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}AC Panel\cf4 \kerning1\expnd0\expndtw0 \
\ls2\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Training\cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sa280\pardirnatural\partightenfactor0
\ls2\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Settings\cf4 \kerning1\expnd0\expndtw0 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\sa240\pardirnatural\partightenfactor0

\fs24 \cf0 ---
\fs30 \cf4 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading45\sb240\sa200\pardirnatural\partightenfactor0

\f1\b\fs44 \cf2 \kerning1\expnd-1\expndtw-4
4. Scenario Engine
\f0\b0\fs30 \cf4 \kerning1\expnd0\expndtw0 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading98\sa240\pardirnatural\partightenfactor0
\cf2 \kerning1\expnd0\expndtw1
Scenarios are stored in 
\fs28 \cf2 \cb5 \kerning1\expnd0\expndtw1
/scenarios/*.js
\fs30 \cf2 \cb1 \kerning1\expnd0\expndtw1
 and loaded via:\
window.OS.loadScenario(id)\
Apps can:\cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sb80\sa200\pardirnatural\partightenfactor0
\ls3\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Load scenario data\cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sa200\pardirnatural\partightenfactor0
\ls3\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Display scenario fields\cf4 \kerning1\expnd0\expndtw0 \
\ls3\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Trigger notifications\cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sa280\pardirnatural\partightenfactor0
\ls3\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Complete tasks\cf4 \kerning1\expnd0\expndtw0 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\sa240\pardirnatural\partightenfactor0

\fs24 \cf0 ---
\fs30 \cf4 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading45\sb240\sa200\pardirnatural\partightenfactor0

\f1\b\fs44 \cf2 \kerning1\expnd-1\expndtw-4
5. Visual Fidelity Modes
\f0\b0\fs30 \cf4 \kerning1\expnd0\expndtw0 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading46\sb320\sa120\pardirnatural\partightenfactor0

\f1\b\fs36 \cf2 \kerning1\expnd-1\expndtw-1
Windows 11 Mode
\f0\b0\fs30 \cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sb80\sa200\pardirnatural\partightenfactor0
\ls4\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Mica\uc0\u8209 like backgrounds\cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sa200\pardirnatural\partightenfactor0
\ls4\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Acrylic blur\cf4 \kerning1\expnd0\expndtw0 \
\ls4\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Fluent shadows\cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sa280\pardirnatural\partightenfactor0
\ls4\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Floating Start menu\cf4 \kerning1\expnd0\expndtw0 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading46\sb80\sa120\pardirnatural\partightenfactor0

\f1\b\fs36 \cf2 \kerning1\expnd-1\expndtw-1
Classic Mode
\f0\b0\fs30 \cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sb80\sa200\pardirnatural\partightenfactor0
\ls5\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Lightweight surfaces\cf3 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sa200\pardirnatural\partightenfactor0
\ls5\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Reduced blur\cf3 \kerning1\expnd0\expndtw0 \
\ls5\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Higher contrast\cf3 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sa280\pardirnatural\partightenfactor0
\ls5\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Faster rendering\cf3 \kerning1\expnd0\expndtw0 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading98\sa240\pardirnatural\partightenfactor0
\cf2 \kerning1\expnd0\expndtw1
Controlled via:\
shell.dataset.fidelity = "win11" | "classic"\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading45\sb240\sa200\pardirnatural\partightenfactor0

\f1\b\fs44 \cf2 \kerning1\expnd-1\expndtw-4
6. Build Pipeline
\f0\b0\fs30 \cf4 \kerning1\expnd0\expndtw0 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading46\sb320\sa120\pardirnatural\partightenfactor0

\f1\b\fs36 \cf2 \kerning1\expnd-1\expndtw-1
Development
\f0\b0\fs30 \cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sb80\sa200\pardirnatural\partightenfactor0
\ls6\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Modular files\cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sa200\pardirnatural\partightenfactor0
\ls6\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Local server recommended\cf3 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sa280\pardirnatural\partightenfactor0
\ls6\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Fast iteration\cf3 \kerning1\expnd0\expndtw0 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading46\sb80\sa120\pardirnatural\partightenfactor0

\f1\b\fs36 \cf2 \kerning1\expnd-1\expndtw-1
Distribution
\f0\b0\fs30 \cf3 \kerning1\expnd0\expndtw0 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading74\sa240\pardirnatural\partightenfactor0

\fs28 \cf2 \cb5 \kerning1\expnd0\expndtw1
build.js
\fs30 \cf2 \cb1 \kerning1\expnd0\expndtw1
 produces:\
dist/qa-desktop.html\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading98\sa240\pardirnatural\partightenfactor0
\cf2 \kerning1\expnd0\expndtw1
This file:\cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sb80\sa200\pardirnatural\partightenfactor0
\ls7\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Inlines CSS\cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sa200\pardirnatural\partightenfactor0
\ls7\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Inlines JS bundle\cf4 \kerning1\expnd0\expndtw0 \
\ls7\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Embeds apps\cf4 \kerning1\expnd0\expndtw0 \
\ls7\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Embeds scenarios\cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sa280\pardirnatural\partightenfactor0
\ls7\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Requires no external files\cf4 \kerning1\expnd0\expndtw0 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\sa240\pardirnatural\partightenfactor0

\fs24 \cf0 ---
\fs30 \cf4 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading45\sb240\sa200\pardirnatural\partightenfactor0

\f1\b\fs44 \cf2 \kerning1\expnd-1\expndtw-4
7. Why This Architecture Works
\f0\b0\fs30 \cf4 \kerning1\expnd0\expndtw0 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading46\sb320\sa120\pardirnatural\partightenfactor0

\f1\b\fs36 \cf2 \kerning1\expnd-1\expndtw-1
For Development
\f0\b0\fs30 \cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sb80\sa200\pardirnatural\partightenfactor0
\ls8\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Modular\cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sa200\pardirnatural\partightenfactor0
\ls8\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Maintainable\cf4 \kerning1\expnd0\expndtw0 \
\ls8\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Easy to debug\cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sa280\pardirnatural\partightenfactor0
\ls8\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Easy to extend\cf4 \kerning1\expnd0\expndtw0 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading46\sb80\sa120\pardirnatural\partightenfactor0

\f1\b\fs36 \cf2 \kerning1\expnd-1\expndtw-1
For Distribution
\f0\b0\fs30 \cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sb80\sa200\pardirnatural\partightenfactor0
\ls9\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Single file\cf4 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sa200\pardirnatural\partightenfactor0
\ls9\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Offline\cf4 \kerning1\expnd0\expndtw0 \
\ls9\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}OneNote\uc0\u8209 compatible\cf4 \kerning1\expnd0\expndtw0 \
\ls9\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}Enterprise\uc0\u8209 safe\cf3 \kerning1\expnd0\expndtw0 \
\ls9\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}No caching issues\cf3 \kerning1\expnd0\expndtw0 \
\pard\slleading138\sa280\pardirnatural\partightenfactor0
\ls9\ilvl0\cf2 \kerning1\expnd0\expndtw1
{\listtext	\uc0\u8226 	}No file:// restrictions\cf3 \kerning1\expnd0\expndtw0 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\sa240\pardirnatural\partightenfactor0

\fs24 \cf3 ---
\fs30 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading45\sb240\sa200\pardirnatural\partightenfactor0

\f1\b\fs44 \cf2 \kerning1\expnd-1\expndtw-4
8. Future Extensions
\f0\b0\fs30 \cf3 \kerning1\expnd0\expndtw0 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\slleading98\sa240\pardirnatural\partightenfactor0
\cf2 \kerning1\expnd0\expndtw1
See ROADMAP.md for planned features.}