# ─────────────────────────────────────────────────────────────
# setup_launcher.ps1 — QA Pilot Windows launcher setup
#
# Run once (right-click → Run with PowerShell):
#   1. Generates a QA Pilot icon (.ico) using Python + Pillow
#   2. Creates a desktop shortcut (.lnk) pointing at build.bat
#      with the custom icon applied
#   3. Optionally pins to taskbar (manual step — Windows blocks
#      programmatic taskbar pinning for security reasons)
#
# Requirements: Python 3 + Pillow
#   pip install pillow
# ─────────────────────────────────────────────────────────────

$ErrorActionPreference = "Stop"
$QARoot    = Split-Path -Parent $MyInvocation.MyCommand.Path
$IconPy    = Join-Path $QARoot "make_icon_win.py"
$IcoFile   = Join-Path $QARoot "qa_pilot.ico"
$BatchFile = Join-Path $QARoot "build.bat"
$Desktop   = [Environment]::GetFolderPath("Desktop")
$Shortcut  = Join-Path $Desktop "QA Pilot.lnk"

Write-Host ""
Write-Host "  ╔══════════════════════════════════════╗"
Write-Host "  ║    QA Pilot Launcher Setup (Win)     ║"
Write-Host "  ╚══════════════════════════════════════╝"
Write-Host ""

# ── Check Python ─────────────────────────────────────────────
Write-Host "  Pre-flight: checking Python..."
$python = $null
foreach ($cmd in @("python","python3")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3") { $python = $cmd; break }
    } catch {}
}

if (-not $python) {
    Write-Warning "Python 3 not found. Icon will not be generated."
    Write-Host "  Install Python from https://python.org then re-run this script."
    Write-Host ""
} else {
    Write-Host "  ✓ $python found"

    # ── Check / install Pillow ───────────────────────────────
    Write-Host "  Checking Pillow..."
    $pillow = & $python -c "import PIL; print('ok')" 2>&1
    if ($pillow -ne "ok") {
        Write-Host "  Installing Pillow..."
        & $python -m pip install pillow --quiet
    }
    Write-Host "  ✓ Pillow ready"

    # ── Generate icon ────────────────────────────────────────
    Write-Host ""
    Write-Host "  Generating qa_pilot.ico..."
    & $python $IconPy
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Icon generation failed. Shortcut will use default icon."
    } else {
        Write-Host "  ✓ Icon saved to qa_pilot.ico"
    }
}

# ── Create desktop shortcut ──────────────────────────────────
Write-Host ""
Write-Host "  Creating desktop shortcut..."

$WScript   = New-Object -ComObject WScript.Shell
$lnk       = $WScript.CreateShortcut($Shortcut)
$lnk.TargetPath       = $BatchFile
$lnk.WorkingDirectory = $QARoot
$lnk.Description      = "Launch QA Pilot (builds dist, starts local server)"
$lnk.WindowStyle      = 1   # Normal window

# Apply custom icon if it was generated, else fall back to cmd.exe icon
if (Test-Path $IcoFile) {
    $lnk.IconLocation = "$IcoFile,0"
} else {
    $lnk.IconLocation = "shell32.dll,21"  # generic 'run' icon
}

$lnk.Save()
Write-Host "  ✓ Shortcut created: $Shortcut"

# ── Done ─────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════════╗"
Write-Host "  ║  ✅  Setup complete!                                 ║"
Write-Host "  ║                                                      ║"
Write-Host "  ║  Double-click 'QA Pilot' on your Desktop to launch. ║"
Write-Host "  ║                                                      ║"
Write-Host "  ║  To pin to taskbar: right-click the shortcut        ║"
Write-Host "  ║  → Show more options → Pin to taskbar               ║"
Write-Host "  ╚══════════════════════════════════════════════════════╝"
Write-Host ""
