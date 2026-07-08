# AutoClicker

A simple cross-platform auto clicker with a small Tkinter GUI. Clicks
automatically at a rate you choose, toggled with the global **`** (backtick) keyboard shortcut.

## Download (macOS, Apple Silicon)
**[⬇︎ Download AutoClicker.dmg](https://github.com/ishaanniaj/Autoclicker/releases/latest/download/AutoClicker.dmg)** —
this link downloads the app directly. Open the `.dmg` and drag **AutoClicker**
onto the **Applications** folder.

First launch: right-click the app → **Open** → **Open** (it isn't signed by a
registered Apple developer). Then enable it under **System Settings → Privacy &
Security → Accessibility** so it can actually click. The app shows a red banner
until that permission is granted.

## Features
- Configurable click interval (hours / minutes / seconds / milliseconds)
- Left, middle, or right mouse button
- Single or double click
- Fixed repeat count or click-until-stopped
- Global keyboard shortcut toggle (**`** backtick) to start/stop without focusing the window

## How to run it
Once installed (see **Download** above), open **Autoclicker** from Launchpad,
Spotlight, or your Applications folder — then:

1. **Grant permission (first time only).** The app shows a red banner until you
   enable it under **System Settings → Privacy & Security → Accessibility**
   (turn **Autoclicker** ON), then quit and reopen. Without this, clicks and the
   keyboard shortcut won't fire.
2. **Set the click speed** in the *Click interval* boxes — hours / minutes /
   seconds / milliseconds (100 ms ≈ 10 clicks per second).
3. **Choose** the mouse **button** (left / middle / right) and **type**
   (single / double).
4. Pick **Until stopped** or a fixed **Repeat** count.
5. Move your cursor to where you want to click, then press **Start** — or tap
   the **`** (backtick) key to start/stop from any app.
6. Press **`** again (or **Stop**) to halt.

The clicker clicks wherever the cursor currently is. Keep the app open while
using it (you can minimize it); quitting it stops the clicking.

## Run from source (developers)
Prefer to run the Python directly instead of the app?

- **Easiest — double-click `run.command`.** It creates a local virtualenv,
  installs dependencies, and launches the GUI. First time: if macOS blocks it,
  right-click → **Open** → **Open**.
- **Manual:**
  ```bash
  pip install -r requirements.txt
  python3 autoclicker.py
  ```
  On macOS use a Homebrew Python — the system Python's Tk toolkit is broken and
  crashes the GUI.

## Build the app & installer (developers)
- **`build_app.command`** — bundles a standalone `Autoclicker.app` with
  [PyInstaller](https://pyinstaller.org), ad-hoc signs it, and installs it to
  `/Applications`.
- **`build_dmg.command`** — packages the installed app into a
  drag-to-Applications `AutoClicker.dmg`.

Build output (`build/`, `dist/`, `*.spec`, `AutoClicker.dmg`) is gitignored.

## Requirements
- **Prebuilt app:** macOS on Apple Silicon (M1–M4), macOS 11+.
- **From source:** Python 3 and [`pynput`](https://pypi.org/project/pynput/)
  (installed automatically by `run.command`, or via `requirements.txt`).
