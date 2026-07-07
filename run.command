#!/bin/bash
# Double-clickable launcher for the autoclicker (macOS).
# First run: creates a local virtualenv and installs dependencies.
# Every run after that: just launches the app.

cd "$(dirname "$0")" || exit 1

if [ ! -d ".venv" ]; then
    echo "First-time setup — creating virtual environment..."
    python3 -m venv .venv || { echo "Failed to create venv"; read -r; exit 1; }
    ./.venv/bin/pip install --quiet --upgrade pip
    ./.venv/bin/pip install --quiet -r requirements.txt
fi

echo "Starting Autoclicker..."
./.venv/bin/python autoclicker.py
