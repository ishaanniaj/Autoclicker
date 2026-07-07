# Autoclicker

A simple cross-platform autoclicker with a small Tkinter GUI.

## Features
- Configurable click interval (hours / minutes / seconds / milliseconds)
- Left, middle, or right mouse button
- Single or double click
- Fixed repeat count or click-until-stopped
- Global hotkey toggle (**F6**) to start/stop without focusing the window

## Install
```bash
pip install -r requirements.txt
```

## Run
```bash
python autoclicker.py
```

## Usage
1. Set the **click interval** (default 100 ms = 10 clicks/sec).
2. Choose the **button** (left/middle/right) and **type** (single/double).
3. Pick **Until stopped** or a fixed **Repeat** count.
4. Position your cursor where you want to click, then press **Start** or **F6**.
5. Press **F6** again (or **Stop**) to halt.

The clicker acts wherever the cursor currently is.

## macOS note
Grant **Accessibility** permission to whatever runs the script
(System Settings → Privacy & Security → Accessibility), otherwise the
clicks and the F6 hotkey will not fire.
