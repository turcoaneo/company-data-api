#!/usr/bin/env bash

# ============================================
# Start Full App (FastAPI + Cron Job)
# ============================================

# Move to project root (directory of this script)
cd "$(dirname "$0")/.." || exit 1

# Activate virtual environment
if [ -f ".venv/Scripts/activate" ]; then
    # Windows Git Bash / MSYS2
    source .venv/Scripts/activate
elif [ -f ".venv/bin/activate" ]; then
    # Linux / WSL / macOS
    source .venv/bin/activate
else
    echo "❌ Could not find virtual environment. Run: python -m venv .venv"
    exit 1
fi

# Environment variables
export PYTHONUNBUFFERED=1
export APP_ENV=local

echo "🚀 Starting full application (FastAPI + Cron)..."
python main.py
