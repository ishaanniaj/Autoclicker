#!/usr/bin/env python3
"""
Simple cross-platform autoclicker with a small Tkinter GUI.

Features
  - Configurable click interval (hours / minutes / seconds / milliseconds)
  - Left, middle, or right mouse button
  - Single or double click
  - Fixed repeat count or click-until-stopped
  - Global hotkey toggle (default backtick ` ) so you can start/stop
    without focusing the window

Requires: pynput   ->   pip install pynput
"""

import os
import sys
import threading
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox

from pynput.mouse import Button, Controller
from pynput import keyboard


mouse = Controller()


def _debug(msg):
    """Append a line to the file named by AUTOCLICKER_DEBUG, if set."""
    path = os.environ.get("AUTOCLICKER_DEBUG")
    if not path:
        return
    try:
        with open(path, "a") as fh:
            fh.write(msg + "\n")
    except OSError:
        pass


# ---- toggle hotkey: the backtick ` key (top-left, above Tab) ----
TOGGLE_CHAR = "`"
TOGGLE_LABEL = "`"
TOGGLE_KEYCODE = 50   # macOS virtual key code for the ` / ~ key (kVK_ANSI_Grave)

# ---- color palette (light, iOS-ish) ----
BG = "#f2f2f7"
CARD = "#ffffff"
BORDER = "#e3e3e8"
TEXT = "#1d1d1f"
MUTED = "#8a8a8e"
ACCENT = "#0a84ff"
GREEN = "#34c759"
GREEN_H = "#2eb350"
RED = "#ff3b30"
RED_H = "#e0352b"
DISABLED_BG = "#d1d1d6"
DISABLED_FG = "#f2f2f7"


class SolidButton(tk.Label):
    """A flat, colored button (Tk's native buttons ignore color on macOS)."""

    def __init__(self, master, text, color, hover, command, font):
        super().__init__(master, text=text, bg=color, fg="#ffffff",
                         font=font, padx=30, pady=11)
        self.color = color
        self.hover = hover
        self.command = command
        self.enabled = True
        self.configure(cursor="pointinghand")
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self.bind("<Button-1>", self._click)

    def _enter(self, _):
        if self.enabled:
            self.configure(bg=self.hover)

    def _leave(self, _):
        if self.enabled:
            self.configure(bg=self.color)

    def _click(self, _):
        if self.enabled and self.command:
            self.command()

    def set_enabled(self, on):
        self.enabled = on
        if on:
            self.configure(bg=self.color, fg="#ffffff", cursor="pointinghand")
        else:
            self.configure(bg=DISABLED_BG, fg=DISABLED_FG, cursor="arrow")


class HotkeyManager:
    """Global start/stop hotkey.

    macOS is fussy about global keyboard hooks inside a bundled .app:
      - pynput's listener queries the Text Input Source API off the main
        thread -> macOS 26 aborts with a dispatch-queue assertion.
      - A Quartz event-tap callback re-entering Tkinter corrupts the Python
        interpreter state -> fatal error.
    Both crash the app. The robust approach is to touch nothing off the main
    thread: poll the raw key state from Tk's own event loop with `after()`,
    and toggle on a fresh key-down edge. Other platforms use pynput.
    """

    POLL_MS = 45

    def __init__(self, root, on_toggle, keycode, char):
        self.root = root
        self.on_toggle = on_toggle
        self.keycode = keycode
        self._prev_down = False
        self._active = True
        self._quartz = None
        self._listener = None
        if sys.platform == "darwin":
            try:
                import Quartz
                self._quartz = Quartz
                self._poll()
            except ImportError:
                self._active = False  # fall back to the on-screen buttons
        else:
            self._start_pynput(char)

    def _poll(self):
        if not self._active:
            return
        q = self._quartz
        try:
            # Combined session state reflects both real hardware keys and
            # posted events (HID-only state misses some cases).
            down = bool(q.CGEventSourceKeyState(
                q.kCGEventSourceStateCombinedSessionState, self.keycode))
        except Exception:
            down = False
        if down and not self._prev_down:      # rising edge = one press
            _debug("hotkey edge -> toggle")
            self.on_toggle()
        self._prev_down = down
        self.root.after(self.POLL_MS, self._poll)

    def _start_pynput(self, char):
        def on_press(key):
            try:
                if key.char == char:
                    self.root.after(0, self.on_toggle)
            except AttributeError:
                pass
        self._listener = keyboard.Listener(on_press=on_press)
        self._listener.start()

    def stop(self):
        self._active = False
        if self._listener is not None:
            self._listener.stop()


class ClickThread(threading.Thread):
    """Background thread that performs the clicking."""

    def __init__(self, interval, button, clicks_per_action, max_actions):
        super().__init__(daemon=True)
        self.interval = interval                     # seconds between actions
        self.button = button                         # pynput Button
        self.clicks_per_action = clicks_per_action   # 1 = single, 2 = double
        self.max_actions = max_actions               # 0 = unlimited
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        count = 0
        while not self._stop.is_set():
            mouse.click(self.button, self.clicks_per_action)
            count += 1
            if self.max_actions and count >= self.max_actions:
                break
            self._stop.wait(self.interval)


class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.click_thread = None
        root.title("Autoclicker")
        root.configure(bg=BG)
        root.resizable(False, False)

        # ---- fonts derived from the system default (robust across machines) ----
        base = tkfont.nametofont("TkDefaultFont").actual("family")
        self.f_title = tkfont.Font(family=base, size=22, weight="bold")
        self.f_sub = tkfont.Font(family=base, size=12)
        self.f_section = tkfont.Font(family=base, size=11, weight="bold")
        self.f_body = tkfont.Font(family=base, size=13)
        self.f_entry = tkfont.Font(family=base, size=15)
        self.f_unit = tkfont.Font(family=base, size=12)
        self.f_btn = tkfont.Font(family=base, size=15, weight="bold")
        self.f_hint = tkfont.Font(family=base, size=11)

        # combobox styling
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Big.TCombobox", padding=4, arrowsize=14)

        outer = tk.Frame(root, bg=BG, padx=20, pady=18)
        outer.pack(fill="both", expand=True)

        # ---- header ----
        tk.Label(outer, text="Autoclicker", font=self.f_title,
                 bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(outer, text="Clicks automatically at the speed you choose",
                 font=self.f_sub, bg=BG, fg=MUTED).pack(anchor="w", pady=(0, 14))

        # ---- interval card ----
        card1 = self._card(outer)
        self._section(card1, "CLICK SPEED")

        row = tk.Frame(card1, bg=CARD)
        row.pack(anchor="w", pady=(8, 2))

        self.hours = tk.StringVar(value="0")
        self.mins = tk.StringVar(value="0")
        self.secs = tk.StringVar(value="0")
        self.millis = tk.StringVar(value="100")

        for i, (label, var) in enumerate(
            [("hrs", self.hours), ("min", self.mins),
             ("sec", self.secs), ("ms", self.millis)]
        ):
            self._entry(row, var).grid(row=0, column=i * 2, padx=(0, 4))
            tk.Label(row, text=label, font=self.f_unit, bg=CARD,
                     fg=MUTED).grid(row=0, column=i * 2 + 1, padx=(0, 14))
            var.trace_add("write", self._update_rate)

        self.rate_lbl = tk.Label(card1, text="", font=self.f_body,
                                 bg=CARD, fg=ACCENT)
        self.rate_lbl.pack(anchor="w", pady=(6, 0))

        # ---- options card ----
        card2 = self._card(outer)
        self._section(card2, "OPTIONS")

        orow = tk.Frame(card2, bg=CARD)
        orow.pack(anchor="w", pady=(8, 0))

        tk.Label(orow, text="Button", font=self.f_body, bg=CARD,
                 fg=TEXT).grid(row=0, column=0, sticky="w")
        self.button_var = tk.StringVar(value="left")
        ttk.Combobox(orow, textvariable=self.button_var, width=8,
                     state="readonly", style="Big.TCombobox", font=self.f_body,
                     values=["left", "middle", "right"]).grid(
            row=0, column=1, padx=(8, 22))

        tk.Label(orow, text="Type", font=self.f_body, bg=CARD,
                 fg=TEXT).grid(row=0, column=2, sticky="w")
        self.type_var = tk.StringVar(value="single")
        ttk.Combobox(orow, textvariable=self.type_var, width=8,
                     state="readonly", style="Big.TCombobox", font=self.f_body,
                     values=["single", "double"]).grid(row=0, column=3, padx=(8, 0))

        # ---- repeat card ----
        card3 = self._card(outer)
        self._section(card3, "REPEAT")

        self.repeat_mode = tk.StringVar(value="forever")
        tk.Radiobutton(
            card3, text="Until stopped", variable=self.repeat_mode,
            value="forever", font=self.f_body, bg=CARD, fg=TEXT,
            activebackground=CARD, selectcolor=CARD, highlightthickness=0,
        ).pack(anchor="w", pady=(8, 0))

        rrow = tk.Frame(card3, bg=CARD)
        rrow.pack(anchor="w", pady=(2, 0))
        tk.Radiobutton(
            rrow, text="Repeat", variable=self.repeat_mode, value="count",
            font=self.f_body, bg=CARD, fg=TEXT, activebackground=CARD,
            selectcolor=CARD, highlightthickness=0,
        ).grid(row=0, column=0)
        self.repeat_count = tk.StringVar(value="10")
        self._entry(rrow, self.repeat_count, width=5).grid(
            row=0, column=1, padx=6)
        tk.Label(rrow, text="times", font=self.f_body, bg=CARD,
                 fg=TEXT).grid(row=0, column=2)

        # ---- controls ----
        ctrl = tk.Frame(outer, bg=BG)
        ctrl.pack(pady=(16, 4))
        self.start_btn = SolidButton(ctrl, "▶  Start", GREEN, GREEN_H,
                                     self.start, self.f_btn)
        self.start_btn.grid(row=0, column=0, padx=6)
        self.stop_btn = SolidButton(ctrl, "■  Stop", RED, RED_H,
                                    self.stop, self.f_btn)
        self.stop_btn.grid(row=0, column=1, padx=6)
        self.stop_btn.set_enabled(False)

        tk.Label(outer, text=f"Shortcut:  press  {TOGGLE_LABEL}  to start / stop",
                 font=self.f_hint, bg=BG, fg=MUTED).pack(pady=(8, 2))

        self.status = tk.StringVar(value="● Idle")
        self.status_lbl = tk.Label(outer, textvariable=self.status,
                                   font=self.f_body, bg=BG, fg=MUTED)
        self.status_lbl.pack()

        self._update_rate()

        # ---- global hotkey ----
        self.hotkey = HotkeyManager(root, self.toggle, TOGGLE_KEYCODE, TOGGLE_CHAR)
        root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------- UI helpers ----------
    def _card(self, parent):
        card = tk.Frame(parent, bg=CARD, highlightbackground=BORDER,
                        highlightthickness=1, padx=16, pady=12)
        card.pack(fill="x", pady=6)
        return card

    def _section(self, parent, text):
        tk.Label(parent, text=text, font=self.f_section, bg=CARD,
                 fg=MUTED).pack(anchor="w")

    def _entry(self, parent, var, width=6):
        return tk.Entry(parent, textvariable=var, width=width,
                        font=self.f_entry, justify="center", relief="flat",
                        bg="#f7f7fa", fg=TEXT, highlightthickness=1,
                        highlightbackground=BORDER, highlightcolor=ACCENT,
                        insertbackground=TEXT)

    def _update_rate(self, *_):
        try:
            seconds = self._compute_interval()
        except ValueError:
            self.rate_lbl.config(text="⚠ enter a speed above zero")
            return
        if seconds < 1:
            self.rate_lbl.config(text=f"≈ {1 / seconds:.0f} clicks per second")
        elif seconds < 60:
            unit = "second" if seconds == 1 else "seconds"
            self.rate_lbl.config(text=f"1 click every {seconds:g} {unit}")
        else:
            mins = seconds / 60
            unit = "minute" if mins == 1 else "minutes"
            self.rate_lbl.config(text=f"1 click every {mins:g} {unit}")

    # ---------- logic ----------
    def _compute_interval(self):
        try:
            seconds = (
                int(self.hours.get() or 0) * 3600
                + int(self.mins.get() or 0) * 60
                + int(self.secs.get() or 0)
                + int(self.millis.get() or 0) / 1000.0
            )
        except ValueError:
            raise ValueError("Interval fields must be whole numbers.")
        if seconds <= 0:
            raise ValueError("Interval must be greater than zero.")
        return seconds

    def _selected_button(self):
        return {"left": Button.left, "middle": Button.middle,
                "right": Button.right}[self.button_var.get()]

    def start(self):
        if self.click_thread and self.click_thread.is_alive():
            return
        try:
            interval = self._compute_interval()
            max_actions = 0
            if self.repeat_mode.get() == "count":
                max_actions = int(self.repeat_count.get() or 0)
                if max_actions <= 0:
                    raise ValueError("Repeat count must be greater than zero.")
        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
            return

        clicks = 2 if self.type_var.get() == "double" else 1
        self.click_thread = ClickThread(
            interval, self._selected_button(), clicks, max_actions)
        self.click_thread.start()

        self.start_btn.set_enabled(False)
        self.stop_btn.set_enabled(True)
        self.status.set("● Clicking…")
        self.status_lbl.config(fg=GREEN)
        self._poll_thread()

    def stop(self):
        if self.click_thread:
            self.click_thread.stop()
            self.click_thread = None
        self.start_btn.set_enabled(True)
        self.stop_btn.set_enabled(False)
        self.status.set("● Stopped")
        self.status_lbl.config(fg=MUTED)

    def toggle(self):
        if self.click_thread and self.click_thread.is_alive():
            self.stop()
        else:
            self.start()

    def _poll_thread(self):
        if self.click_thread and not self.click_thread.is_alive():
            self.stop()
            self.status.set("● Done")
        elif self.click_thread:
            self.root.after(100, self._poll_thread)

    def on_close(self):
        self.stop()
        self.hotkey.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    AutoClickerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
