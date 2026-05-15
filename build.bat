@echo off
cd /d "%~dp0desktop"
node build.js
cd /d "%~dp0"
pause
