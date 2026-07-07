#!/bin/bash
# Double-click to (re)build Autoclicker.app and install it to /Applications.
# Uses the local .venv (set up by run.command). Safe to run repeatedly.

cd "$(dirname "$0")" || exit 1

# Prefer Homebrew python (working Tk); fall back to system python3.
PYTHON=""
for candidate in /opt/homebrew/bin/python3 /usr/local/bin/python3 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
        PYTHON="$candidate"
        break
    fi
done

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment ($PYTHON)..."
    "$PYTHON" -m venv .venv || { echo "Failed to create venv"; read -r; exit 1; }
fi

echo "Installing build dependencies..."
./.venv/bin/pip install --quiet --upgrade pip
./.venv/bin/pip install --quiet -r requirements.txt pyinstaller

echo "Building Autoclicker.app..."
./.venv/bin/pyinstaller --windowed --name Autoclicker --noconfirm --clean autoclicker.py

APP="dist/Autoclicker.app"
if [ ! -d "$APP" ]; then
    echo "Build failed — no app produced."; read -r; exit 1
fi

# Clean extended-attribute cruft and ad-hoc sign so Gatekeeper is happy.
xattr -cr "$APP"
codesign --force --deep -s - "$APP"

echo "Installing to /Applications..."
rm -rf /Applications/Autoclicker.app
cp -R "$APP" /Applications/
xattr -cr /Applications/Autoclicker.app
codesign --force --deep -s - /Applications/Autoclicker.app

echo ""
echo "Done. Autoclicker.app is in your Applications folder."
read -r -p "Press Return to close."
