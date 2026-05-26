#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$REPO_URL       = "https://github.com/Yochananj/CryptDriveClient.git"
$INSTALL_DIR    = "$env:USERPROFILE\.cryptdrive\client"
$VENV_PYTHON    = "$INSTALL_DIR\.venv\Scripts\python.exe"
$CONSTANTS_FILE = "$INSTALL_DIR\src\Dependencies\Constants.py"

Write-Host "`n  ╔════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║   CryptDrive Client Installer  ║" -ForegroundColor Cyan
Write-Host "  ╚════════════════════════════════╝`n" -ForegroundColor Cyan

# ── Dependency checks ─────────────────────────────────────────────────────────
foreach ($cmd in @("git", "python")) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Error "'$cmd' is required but not installed. Aborting."
        exit 1
    }
}

# ── Clone / update repo ───────────────────────────────────────────────────────
Write-Host "Fetching CryptDrive client..." -ForegroundColor Cyan
if (Test-Path "$INSTALL_DIR\.git") {
    git -C $INSTALL_DIR pull --quiet
} else {
    New-Item -ItemType Directory -Force -Path (Split-Path $INSTALL_DIR) | Out-Null
    git clone --quiet $REPO_URL $INSTALL_DIR
}

# ── Prompt for server IP ──────────────────────────────────────────────────────
Write-Host ""
$SERVER_IP = ""
while ($true) {
    $SERVER_IP = Read-Host "Enter the CryptDrive server IP address"
    if ([string]::IsNullOrWhiteSpace($SERVER_IP)) {
        Write-Host "IP address cannot be empty. Please try again." -ForegroundColor Red
    } elseif ($SERVER_IP -notmatch '^[a-zA-Z0-9._-]+$') {
        Write-Host "Invalid format. Please enter a valid IP or hostname." -ForegroundColor Red
    } else {
        break
    }
}

# ── Write server address into constants file ───────────────────────────────────
Write-Host "Configuring server address..." -ForegroundColor Cyan
if (-not (Test-Path $CONSTANTS_FILE)) {
    Write-Error "Constants file not found at $CONSTANTS_FILE"
    exit 1
}

$content = Get-Content $CONSTANTS_FILE -Raw
$updated = $content -replace '(?m)^server_address = ".*"', "server_address = `"$SERVER_IP`""
Set-Content -Path $CONSTANTS_FILE -Value $updated -NoNewline
Write-Host "  Server address set to: $SERVER_IP" -ForegroundColor Green

# ── Create virtual environment ────────────────────────────────────────────────
Write-Host "Setting up Python environment..." -ForegroundColor Cyan
if (-not (Test-Path "$INSTALL_DIR\.venv")) {
    python -m venv "$INSTALL_DIR\.venv"
}

# ── Install dependencies ──────────────────────────────────────────────────────
Write-Host "Installing dependencies..." -ForegroundColor Cyan
& "$INSTALL_DIR\.venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
& "$INSTALL_DIR\.venv\Scripts\pip.exe" install --quiet -e $INSTALL_DIR

# ── Create native launcher ────────────────────────────────────────────────────
$launcherDir = "$env:APPDATA\CryptDrive"
New-Item -ItemType Directory -Force -Path $launcherDir | Out-Null

$vbsPath = "$launcherDir\CryptDrive.vbs"
@"
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """$VENV_PYTHON"" ""$INSTALL_DIR\src\main.py""", 0, False
"@ | Out-File -FilePath $vbsPath -Encoding ASCII

$shell = New-Object -ComObject WScript.Shell

$startMenu = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
$sc = $shell.CreateShortcut("$startMenu\CryptDrive.lnk")
$sc.TargetPath  = $vbsPath
$sc.Description = "CryptDrive - Zero-knowledge encrypted storage"
$sc.Save()

Write-Host "`n✓ CryptDrive installed successfully!" -ForegroundColor Green
Write-Host "  Launch it from your Start Menu or Desktop shortcut." -ForegroundColor Green
