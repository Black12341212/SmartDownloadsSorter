#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Вкладка: Logging Dashboard (Feature #14)"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from core.logger import read_log_lines, get_log_path


class LoggingTab:
    TAB_TITLE = "  Logs  "

    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.Frame(parent)
        self._auto_refresh = False
        self._build()

    def _build(self):
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, padx=10, pady=6)

        ttk.Label(toolbar, text="Log Level:").pack(side=tk.LEFT, padx=4)
        self.level_var = tk.StringVar(value="ALL")
        levels = ["ALL", "DEBUG", "INFO", "WARNING", "ERROR"]
        ttk.Combobox(toolbar, textvariable=self.level_var, values=levels,
                      state="readonly", width=10).pack(side=tk.LEFT, padx=4)

        ttk.Button(toolbar, text="Refresh", command=self.refresh).pack(side=tk.LEFT, padx=4)

        self.auto_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(toolbar, text="Auto-refresh (5s)",
                         variable=self.auto_var,
                         command=self._toggle_auto).pack(side=tk.LEFT, padx=4)

        ttk.Button(toolbar, text="Clear Log", command=self._clear_display).pack(side=tk.LEFT, padx=4)

        self.line_count_var = tk.StringVar(value="Lines: 0")
        ttk.Label(toolbar, textvariable=self.line_count_var).pack(side=tk.RIGHT, padx=4)

        self.log_text = scrolledtext.ScrolledText(
            self.frame, font=("Consolas", 9), state=tk.DISABLED,
            bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
            selectbackground="#264f78"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.log_text.tag_configure("DEBUG", foreground="#808080")
        self.log_text.tag_configure("INFO", foreground="#d4d4d4")
        self.log_text.tag_configure("WARNING", foreground="#ce9178")
        self.log_text.tag_configure("ERROR", foreground="#f44747")

        self.level_var.trace_add("write", lambda *a: self.refresh())

    def refresh(self):
        level = self.level_var.get()
        lines = read_log_lines(level_filter=level, max_lines=1000)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        for line in lines:
            tag = None
            for lvl in ["ERROR", "WARNING", "INFO", "DEBUG"]:
                if f" {lvl} " in line or line.startswith(f"[{lvl}"):
                    tag = lvl
                    break
            if tag:
                self.log_text.insert(tk.END, line + "\n", tag)
            else:
                self.log_text.insert(tk.END, line + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.line_count_var.set(f"Lines: {len(lines)}")

    def _clear_display(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.line_count_var.set("Lines: 0")

    def _toggle_auto(self):
        self._auto_refresh = self.auto_var.get()
        if self._auto_refresh:
            self._auto_refresh_loop()

    def _auto_refresh_loop(self):
        if not self._auto_refresh:
            return
        self.refresh()
        self.frame.after(5000, self._auto_refresh_loop)
