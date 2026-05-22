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
$pythonProcess = Start-Process -FilePath "python" -ArgumentList "main.py" -PassThru -NoNewWindow
$pythonPid = $pythonProcess.Id

Write-Host "Application started with PID $pythonPid"

# Ctrl+C handler
$null = Register-EngineEvent ConsoleCancelEvent -Action {
    Write-Host "Stopping application..."

    # Kill entire process tree
    taskkill /PID $using:pythonPid /T /F | Out-Null 2>&1
    Stop-Process -Id $using:pythonPid -Force -ErrorAction SilentlyContinue

    # *** IMPORTANT ***
    # Give python time to flush its shutdown logs
    Start-Sleep -Milliseconds 300

    Write-Host "Application stopped."
    exit
}

# Wait for python to exit
Wait-Process -Id $pythonPid

# Final small delay to avoid prompt/log overlap
Start-Sleep -Milliseconds 200
