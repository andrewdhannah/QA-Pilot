@echo off
:: ─────────────────────────────────────────────────────────────
:: QA Pilot — Build + Launch
:: Rebuilds dist.html from source, starts a local server, and
:: opens QA Pilot in the default browser.
::
:: Uses Node.js for both the build AND the server (serve.js),
:: so no Python or other dependencies are needed.
::
:: Edge / Chrome enforce file:// origin restrictions — the local
:: server avoids those errors and ensures the app loads cleanly.
::
:: Requires: Node.js  (https://nodejs.org)
:: ─────────────────────────────────────────────────────────────
setlocal EnableDelayedExpansion
set PORT=8000
set QA_ROOT=%~dp0
if "%QA_ROOT:~-1%"=="\" set QA_ROOT=%QA_ROOT:~0,-1%

echo.
echo  ╔══════════════════════════════════════╗
echo  ║         QA Pilot Launcher            ║
echo  ╚══════════════════════════════════════╝
echo.

:: ── Check Node ───────────────────────────────────────────────
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo  ERROR: Node.js not found.
    echo  Install from https://nodejs.org then re-run.
    echo.
    pause
    exit /b 1
)

:: ── Step 1: Build ────────────────────────────────────────────
echo  [1/3]  Building dist...
cd /d "%QA_ROOT%\desktop"
node build.js
if %errorlevel% neq 0 (
    echo.
    echo  WARNING: Build failed. Opening last successful dist.
    echo.
)
cd /d "%QA_ROOT%"

:: ── Step 2: Start server ─────────────────────────────────────
echo  [2/3]  Starting server on port %PORT%...

:: Kill any process already on this port
for /f "tokens=5" %%P in (
    'netstat -aon 2^>nul ^| findstr /R ":%PORT% " ^| findstr "LISTENING"'
) do taskkill /PID %%P /F >nul 2>&1

:: Start serve.js in background (new window, minimised)
start /MIN "QA Pilot Server" node "%QA_ROOT%\serve.js"

:: Wait up to 5 seconds for the server to respond
set /a TRIES=0
:poll
timeout /t 1 /nobreak >nul
curl -s --head "http://127.0.0.1:%PORT%/" >nul 2>&1
if %errorlevel% equ 0 goto :open
set /a TRIES+=1
if %TRIES% lss 5 goto :poll

:: ── Step 3: Open browser ─────────────────────────────────────
:open
echo  [3/3]  Opening http://127.0.0.1:%PORT%/index.html
start "" "http://127.0.0.1:%PORT%/index.html"

echo.
echo  ─────────────────────────────────────────────────────
echo   QA Pilot is running at http://127.0.0.1:%PORT%/index.html
echo.
echo   A small server window is running in the background.
echo   Close it (or close this window) to stop the server.
echo  ─────────────────────────────────────────────────────
echo.
pause
