#!/bin/bash
# Double-click to (re)build AutoClicker.app and install it to /Applications.
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

# Regenerate the .icns from make_icon.py if possible (needs Pillow).
if [ -f make_icon.py ]; then
    ./.venv/bin/pip install --quiet Pillow 2>/dev/null
    if ./.venv/bin/python make_icon.py 2>/dev/null; then
        rm -rf icon.iconset && mkdir icon.iconset
        for sz in 16 32 128 256 512; do
            sips -z $sz $sz icon_1024.png --out "icon.iconset/icon_${sz}x${sz}.png" >/dev/null 2>&1
            sips -z $((sz*2)) $((sz*2)) icon_1024.png --out "icon.iconset/icon_${sz}x${sz}@2x.png" >/dev/null 2>&1
        done
        cp icon_1024.png icon.iconset/icon_512x512@2x.png
        iconutil -c icns icon.iconset -o icon.icns && rm -rf icon.iconset
    fi
fi

ICON_ARG=""
[ -f icon.icns ] && ICON_ARG="--icon icon.icns"

echo "Building AutoClicker.app..."
./.venv/bin/pyinstaller --windowed --name AutoClicker $ICON_ARG \
    --osx-bundle-identifier com.ishaanniaj.autoclicker \
    --noconfirm --clean autoclicker.py

APP="dist/AutoClicker.app"
if [ ! -d "$APP" ]; then
    echo "Build failed — no app produced."; read -r; exit 1
fi

# Install first, then clean + sign the copy. /Applications is not an
# iCloud-synced folder, so it won't keep re-acquiring the com.apple.FinderInfo
# / provenance attributes that make codesign reject the bundle.
echo "Installing to /Applications..."
DEST="/Applications/AutoClicker.app"
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
echo "Done. AutoClicker.app is in your Applications folder."
read -r -p "Press Return to close."
