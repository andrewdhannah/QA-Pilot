# QA Pilot Sprint Primer — Chrome Extension

One-click sprint prompt injection for DeepSeek, Copilot, and any web AI.

## Install (takes 60 seconds)

1. Open Chrome and go to: `chrome://extensions`
2. Turn on **Developer mode** (toggle, top-right corner)
3. Click **Load unpacked**
4. Select this folder: `QA Pilot/chrome-extension/`
5. The ✈️ icon appears in your Chrome toolbar — pin it for easy access

## How to use

1. Click the toolbar icon to open the popup
2. Pick your template:
   - **Full Sprint** — complete primer with FlightPlan, file reads, code rules, session end
   - **Quick Task** — shorter version for continuing mid-sprint
   - **Custom** — your own freeform prompt (saved automatically)
3. Click **📋 Copy to clipboard**
4. Paste into DeepSeek / Copilot / any AI tool
5. Type your actual sprint task below the pasted header

## Goose Scale badge

Click the ⬜ PREFLIGHT badge to manually update the runway level after
running `flightplan export`. The badge colour changes to match:
- 🟢 Green = CRUISING (healthy)
- 🟡 Yellow = HEADWIND (burning fast)
- 🟠 Orange = TURBULENCE (tight)
- 🔴 Red = HONK (stop now)

The level persists between browser restarts so you can glance at it
before opening a new session.

## Settings

Click ⚙ to customise:
- Project name and your name (auto-filled into the prompt)
- Paths to your handoff doc, style guide, and feature status file
- Custom notes appended to every prompt (e.g. "Elyse is the trainer")

Settings are saved in Chrome local storage — they survive restarts.

## Updating the templates

The template text lives in the `buildFullSprint()` and `buildQuickTask()`
functions in `popup.html`. Edit those directly if you want to change the
wording permanently. No build step needed — just reload the extension in
`chrome://extensions` after saving.

ZYGOTE_VERIFICATION_WORD

TANGERINE_VERIFICATION_99

TANGERINE_VERIFICATION_99

TANGERINE_VERIFICATION_99

TANGERINE_VERIFICATION_99

TANGERINE_VERIFICATION_99

COCONUT_VERIFICATION_66

DASHBOARD_UPGRADE_OK
