# Start Full App (FastAPI + Cron Job)

# Move to project root (directory of this script)
Set-Location -Path (Split-Path $MyInvocation.MyCommand.Path -Parent)
Set-Location ..

# Activate virtual environment
$venv = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venv) {
    & $venv
} else {
    Write-Host "Virtual environment not found. Create it with: python -m venv .venv"
    exit 1
}

# Environment variables
$env:PYTHONUNBUFFERED = "1"
$env:APP_ENV = "local"

# Start application
python main.py
