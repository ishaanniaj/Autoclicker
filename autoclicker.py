#!/usr/bin/env python3
"""
Simple cross-platform autoclicker with a small Tkinter GUI.

Features
  - Configurable click interval (hours / minutes / seconds / milliseconds)
  - Left, middle, or right mouse button
  - Single or double click
  - Fixed repeat count or click-until-stopped
  - Global hotkey toggle (default F6) so you can start/stop without
    focusing the window

Requires: pynput   ->   pip install pynput
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox

from pynput.mouse import Button, Controller
from pynput import keyboard


mouse = Controller()

# ---- toggle hotkey (change here if F6 conflicts with something) ----
TOGGLE_KEY = keyboard.Key.f6


class ClickThread(threading.Thread):
    """Background thread that performs the clicking."""

    def __init__(self, interval, button, clicks_per_action, max_actions):
        super().__init__(daemon=True)
        self.interval = interval                 # seconds between actions
        self.button = button                     # pynput Button
        self.clicks_per_action = clicks_per_action  # 1 = single, 2 = double
        self.max_actions = max_actions           # 0 = unlimited
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
            # sleep in small slices so Stop is responsive
            self._stop.wait(self.interval)


class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.click_thread = None
        root.title("Autoclicker")
        root.resizable(False, False)

        pad = {"padx": 6, "pady": 4}

        # ---- Interval ----
        interval_frame = ttk.LabelFrame(root, text="Click interval")
        interval_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=6)

        self.hours = tk.StringVar(value="0")
        self.mins = tk.StringVar(value="0")
        self.secs = tk.StringVar(value="0")
        self.millis = tk.StringVar(value="100")

        for col, (label, var) in enumerate(
            [("hrs", self.hours), ("min", self.mins),
             ("sec", self.secs), ("ms", self.millis)]
        ):
            ttk.Entry(interval_frame, width=5, textvariable=var).grid(
                row=0, column=col * 2, **pad)
            ttk.Label(interval_frame, text=label).grid(
                row=0, column=col * 2 + 1, **pad)

        # ---- Options ----
        opt_frame = ttk.LabelFrame(root, text="Options")
        opt_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=6)

        ttk.Label(opt_frame, text="Button").grid(row=0, column=0, **pad)
        self.button_var = tk.StringVar(value="left")
        ttk.Combobox(
            opt_frame, textvariable=self.button_var, width=8, state="readonly",
            values=["left", "middle", "right"],
        ).grid(row=0, column=1, **pad)

        ttk.Label(opt_frame, text="Type").grid(row=0, column=2, **pad)
        self.type_var = tk.StringVar(value="single")
        ttk.Combobox(
            opt_frame, textvariable=self.type_var, width=8, state="readonly",
            values=["single", "double"],
        ).grid(row=0, column=3, **pad)

        # ---- Repeat ----
        rep_frame = ttk.LabelFrame(root, text="Repeat")
        rep_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=6)

        self.repeat_mode = tk.StringVar(value="forever")
        ttk.Radiobutton(
            rep_frame, text="Until stopped", variable=self.repeat_mode,
            value="forever",
        ).grid(row=0, column=0, sticky="w", **pad)
        ttk.Radiobutton(
            rep_frame, text="Repeat", variable=self.repeat_mode, value="count",
        ).grid(row=1, column=0, sticky="w", **pad)
        self.repeat_count = tk.StringVar(value="10")
        ttk.Entry(rep_frame, width=6, textvariable=self.repeat_count).grid(
            row=1, column=1, **pad)
        ttk.Label(rep_frame, text="times").grid(row=1, column=2, sticky="w")

        # ---- Controls ----
        ctrl_frame = ttk.Frame(root)
        ctrl_frame.grid(row=3, column=0, sticky="ew", padx=8, pady=6)

        self.start_btn = ttk.Button(
            ctrl_frame, text="Start (F6)", command=self.start)
        self.start_btn.grid(row=0, column=0, padx=4)
        self.stop_btn = ttk.Button(
            ctrl_frame, text="Stop (F6)", command=self.stop, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=4)

        self.status = tk.StringVar(value="Idle — press F6 or Start")
        ttk.Label(root, textvariable=self.status, foreground="#666").grid(
            row=4, column=0, pady=(0, 8))

        # ---- Global hotkey listener ----
        self.listener = keyboard.Listener(on_press=self.on_key)
        self.listener.start()

        root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------- helpers ----------
    def compute_interval(self):
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

    def selected_button(self):
        return {
            "left": Button.left,
            "middle": Button.middle,
            "right": Button.right,
        }[self.button_var.get()]

    # ---------- actions ----------
    def start(self):
        if self.click_thread and self.click_thread.is_alive():
            return
        try:
            interval = self.compute_interval()
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
            interval, self.selected_button(), clicks, max_actions)
        self.click_thread.start()

        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status.set("Clicking… press F6 or Stop to halt")
        self._poll_thread()

    def stop(self):
        if self.click_thread:
            self.click_thread.stop()
            self.click_thread = None
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status.set("Stopped")

    def toggle(self):
        if self.click_thread and self.click_thread.is_alive():
            self.stop()
        else:
            self.start()

    def _poll_thread(self):
        """Reset buttons automatically when a finite run finishes."""
        if self.click_thread and not self.click_thread.is_alive():
            self.stop()
            self.status.set("Done")
        elif self.click_thread:
            self.root.after(100, self._poll_thread)

    def on_key(self, key):
        if key == TOGGLE_KEY:
            # marshal back onto the Tk thread
            self.root.after(0, self.toggle)

    def on_close(self):
        self.stop()
        self.listener.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    AutoClickerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
