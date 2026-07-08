#!/bin/bash
# Double-click to build a styled AutoClicker.dmg (drag-to-Applications window).
# Requires AutoClicker.app already installed in /Applications
# (run build_app.command first). Produces AutoClicker.dmg in this folder.

cd "$(dirname "$0")" || exit 1

if [ ! -d "/Applications/AutoClicker.app" ]; then
    echo "AutoClicker.app is not in /Applications — run build_app.command first."
    read -r; exit 1
fi

./.venv/bin/pip install --quiet dmgbuild Pillow 2>/dev/null
./.venv/bin/python make_dmg_bg.py
rm -f AutoClicker.dmg
./.venv/bin/dmgbuild -s dmg_settings.py "AutoClicker" AutoClicker.dmg

echo ""
echo "Built AutoClicker.dmg — upload it to a GitHub release with:"
echo "  gh release upload <tag> AutoClicker.dmg --clobber"
read -r -p "Press Return to close."
