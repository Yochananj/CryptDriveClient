$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $ProjectRoot ".venv"
$MainFile = Join-Path $ProjectRoot "src\main.py"

Write-Host "==> Project root: $ProjectRoot"

# Find the base Python executable to create the venv
if (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonBin = "py"
}
elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PythonBin = "python3"
}
elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonBin = "python"
}
else {
    Write-Error "Python is not installed or not in PATH."
    exit 1
}

Write-Host "==> Using Python: $(& $PythonBin --version)"

if (-not (Test-Path $VenvDir)) {
    Write-Host "==> Creating virtual environment in $VenvDir"
    & $PythonBin -m venv $VenvDir
}
else {
    Write-Host "==> Virtual environment already exists"
}

$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
if (-not (Test-Path $ActivateScript)) {
    Write-Error "Virtual environment activation script not found: $ActivateScript"
    exit 1
}

# Activate the virtual environment
. $ActivateScript

# Once activated, the venv's executable is always called `python`
Write-Host "==> Upgrading pip"
python -m pip install --upgrade pip

$PyprojectFile = Join-Path $ProjectRoot "pyproject.toml"
if (Test-Path $PyprojectFile) {
    Write-Host "==> Installing project dependencies"
    pip install -e $ProjectRoot
}
else {
    Write-Error "pyproject.toml not found in project root."
    exit 1
}

if (-not (Test-Path $MainFile)) {
    Write-Error "Main file not found: $MainFile"
    exit 1
}

Write-Host "==> Starting application"
python $MainFile