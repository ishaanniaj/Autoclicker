#!/bin/bash
# Double-clickable launcher for the autoclicker (macOS).
# First run: creates a local virtualenv and installs dependencies.
# Every run after that: just launches the app.

cd "$(dirname "$0")" || exit 1

# Apple's built-in python3 ships a broken Tk that crashes the GUI on
# recent macOS. Prefer a Homebrew python (working Tk 9) when present.
PYTHON=""
for candidate in /opt/homebrew/bin/python3 /usr/local/bin/python3 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
        PYTHON="$candidate"
        break
    fi
done

if [ ! -d ".venv" ]; then
    echo "First-time setup — creating virtual environment ($PYTHON)..."
    "$PYTHON" -m venv .venv || { echo "Failed to create venv"; read -r; exit 1; }
    ./.venv/bin/pip install --quiet --upgrade pip
    ./.venv/bin/pip install --quiet -r requirements.txt
fi

echo "Starting Autoclicker..."
./.venv/bin/python autoclicker.py
