@echo off
REM QA Pilot Academy — Windows Launcher
REM Opens index.html in the default browser with one double-click.
REM Usage: Double-click this file, or run from command prompt: launch.bat

setlocal
set "SCRIPT_DIR=%~dp0"
set "OPEN_FILE=%SCRIPT_DIR%index.html"

if exist "%OPEN_FILE%" (
    start "" "%OPEN_FILE%"
    echo Opening QA Pilot Academy...
) else (
    echo Error: index.html not found in %SCRIPT_DIR%
    echo Make sure this file is in the QA Pilot Academy folder.
    pause
)
