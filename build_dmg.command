#!/bin/bash
# Double-click to build a styled Autoclicker.dmg (drag-to-Applications window).
# Requires Autoclicker.app already installed in /Applications
# (run build_app.command first). Produces Autoclicker.dmg in this folder.

cd "$(dirname "$0")" || exit 1

if [ ! -d "/Applications/Autoclicker.app" ]; then
    echo "Autoclicker.app is not in /Applications — run build_app.command first."
    read -r; exit 1
fi

./.venv/bin/pip install --quiet dmgbuild Pillow 2>/dev/null
./.venv/bin/python make_dmg_bg.py
rm -f Autoclicker.dmg
./.venv/bin/dmgbuild -s dmg_settings.py "Autoclicker" Autoclicker.dmg

echo ""
echo "Built Autoclicker.dmg — upload it to a GitHub release with:"
echo "  gh release upload <tag> Autoclicker.dmg --clobber"
read -r -p "Press Return to close."
