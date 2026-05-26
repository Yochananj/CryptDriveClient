#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$INSTALL_DIR   = "$env:USERPROFILE\.cryptdrive\client"
$LAUNCHER_DIR  = "$env:APPDATA\CryptDrive"
$START_MENU    = "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\CryptDrive.lnk"
$DESKTOP_LNK   = "$env:USERPROFILE\Desktop\CryptDrive.lnk"

  Write-Host "`n  ╔═════════════════════════════════╗" -ForegroundColor Red
    Write-Host "  ║  CryptDrive Client Uninstaller  ║" -ForegroundColor Red
    Write-Host "  ╚═════════════════════════════════╝`n" -ForegroundColor Red

Write-Host "The following items will be removed:" -ForegroundColor Cyan
if (Test-Path $INSTALL_DIR)  { Write-Host " - Core files & environment: $INSTALL_DIR" }
if (Test-Path $LAUNCHER_DIR) { Write-Host " - App Launcher (VBS):      $LAUNCHER_DIR" }
if (Test-Path $START_MENU)   { Write-Host " - Start Menu Shortcut:     $START_MENU" }
if (Test-Path $DESKTOP_LNK)  { Write-Host " - Desktop Shortcut:        $DESKTOP_LNK" }

Write-Host ""
$title = "Confirm Uninstallation"
$message = "Are you sure you want to completely remove CryptDrive?"
$options = [System.Management.Automation.Host.ChoiceDescription[]] @(
    New-Object System.Management.Automation.Host.ChoiceDescription "&Yes", "Uninstall the application."
    New-Object System.Management.Automation.Host.ChoiceDescription "&No", "Cancel uninstallation."
)

$result = $host.ui.PromptForChoice($title, $message, $options, 1)

if ($result -ne 0) {
    Write-Host "Uninstallation cancelled." -ForegroundColor Cyan
    exit
}

Write-Host "Removing files..." -ForegroundColor Cyan

if (Test-Path $INSTALL_DIR)  { Remove-Item -Recurse -Force $INSTALL_DIR }
if (Test-Path $LAUNCHER_DIR) { Remove-Item -Recurse -Force $LAUNCHER_DIR }
if (Test-Path $START_MENU)   { Remove-Item -Force $START_MENU }
if (Test-Path $DESKTOP_LNK)  { Remove-Item -Force $DESKTOP_LNK }

Write-Host "`n✓ CryptDrive has been successfully uninstalled." -ForegroundColor Green