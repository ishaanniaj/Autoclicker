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

# Install first, then clean + sign the copy. /Applications is not an
# iCloud-synced folder, so it won't keep re-acquiring the com.apple.FinderInfo
# / provenance attributes that make codesign reject the bundle.
echo "Installing to /Applications..."
DEST="/Applications/Autoclicker.app"
rm -rf "$DEST"
cp -R "$APP" "$DEST"

find "$DEST" -name '.DS_Store' -delete 2>/dev/null
xattr -cr "$DEST"
xattr -d com.apple.FinderInfo "$DEST" 2>/dev/null
codesign --force --deep -s - "$DEST"
codesign --verify --deep --strict "$DEST" \
    && echo "Signature verified." \
    || echo "Warning: signature check reported an issue (app usually still runs)."

echo ""
echo "Done. Autoclicker.app is in your Applications folder."
read -r -p "Press Return to close."
