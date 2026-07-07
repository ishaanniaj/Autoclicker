# Autoclicker

A simple cross-platform autoclicker with a small Tkinter GUI. Clicks
automatically at a rate you choose, toggled with the global **`** (backtick) hotkey.

## Features
- Configurable click interval (hours / minutes / seconds / milliseconds)
- Left, middle, or right mouse button
- Single or double click
- Fixed repeat count or click-until-stopped
- Global hotkey toggle (**`** backtick) to start/stop without focusing the window

## Run it (easiest — macOS app)
There's a standalone **`Autoclicker.app`** — no Terminal, no Python needed.

- Build/install it by **double-clicking `build_app.command`** (see
  [Build the .app](#build-the-app) below). It lands in your **Applications**
  folder; launch it from Launchpad, Spotlight, or drag it to your Dock.
- First launch only: macOS may warn it's from an unidentified developer —
  **right-click the app → Open → Open**.

## Run it (script — macOS)
1. Open the `Autoclicker` folder in Finder.
2. **Double-click `run.command`.**
   - First time only: if macOS blocks it, **right-click → Open → Open**.
3. The window opens. Set your speed, position the mouse, press **Start** or the **`** key.

The first double-click auto-installs everything into a local `.venv`;
later runs launch instantly.

## Build the .app
Double-click **`build_app.command`** (or run it from a terminal). It sets up
the environment, bundles the app with [PyInstaller](https://pyinstaller.org),
ad-hoc signs it, and copies it to `/Applications`. Re-run it any time you
change the code. Build output (`build/`, `dist/`, `*.spec`) is gitignored.

## Run it (manual / other platforms)
```bash
pip install -r requirements.txt
python autoclicker.py
```

## Usage
1. Set the **click interval** (default 100 ms = 10 clicks/sec).
2. Choose the **button** (left/middle/right) and **type** (single/double).
3. Pick **Until stopped** or a fixed **Repeat** count.
4. Position your cursor where you want to click, then press **Start** or the **`** key.
5. Press **`** again (or **Stop**) to halt.

The clicker acts wherever the cursor currently is.

## macOS permission note
Grant **Accessibility** permission to whatever runs the script
(System Settings → Privacy & Security → Accessibility), otherwise the
clicks and the backtick hotkey will not fire.

## Requirements
- Python 3
- [`pynput`](https://pypi.org/project/pynput/) (installed automatically by `run.command`, or via `requirements.txt`)
