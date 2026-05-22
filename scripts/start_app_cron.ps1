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

# Start python in SAME console (foreground)
# but capture its PID using Get-Process
$pythonProcess = Start-Process -FilePath "python" -ArgumentList "main.py" -PassThru -NoNewWindow

$pythonPid = $pythonProcess.Id
Write-Host "Application started with PID $pythonPid"

# Ctrl+C handler
$null = Register-EngineEvent ConsoleCancelEvent -Action {
    Write-Host "Stopping application..."

    # Kill entire process tree
    taskkill /PID $pythonPid /T /F | Out-Null 2>&1

    # Extra safety
    Stop-Process -Id $pythonPid -Force -ErrorAction SilentlyContinue

    Write-Host "Application stopped."
    exit
}

# Wait for python to exit
Wait-Process -Id $pythonPid
