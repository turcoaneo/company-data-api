#!/usr/bin/env bash

cd "$(dirname "$0")/.." || exit 1

# Activate virtual environment
if [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "Virtual environment not found."
    exit 1
fi

export PYTHONUNBUFFERED=1
export APP_ENV=local

python main.py &
APP_PID=$!

# Get process group ID (POSIX only)
pgid=$(ps -o pgid= $APP_PID 2>/dev/null | tr -d ' ')

cleanup() {
    echo "Stopping application..."

    # POSIX kill (Linux / macOS)
    if kill -0 -$pgid 2>/dev/null; then
        kill -TERM -$pgid 2>/dev/null
        sleep 1
        kill -KILL -$pgid 2>/dev/null
    fi

    # Windows kill (Git Bash / MSYS / Cygwin)
    taskkill //PID $APP_PID //T //F >/dev/null 2>&1

    exit 0
}

trap cleanup INT TERM

wait $APP_PID
