#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Вкладка: О программе + QR-код + кнопка Поддержать v3.0"""

import tkinter as tk
from tkinter import ttk
import webbrowser


class AboutTab:
    TAB_TITLE = "  About  "

    DONATE_URL = "https://www.donationalerts.com/r/zenixx5678"

    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.Frame(parent)
        self._build()

    def _build(self):
        center = ttk.Frame(self.frame, padding=30)
        center.pack(expand=True)

        ttk.Label(center, text="Smart Downloads Sorter",
                  font=("", 18, "bold")).pack(pady=(0, 5))
        ttk.Label(center, text=f"Version {self.app.VERSION}",
                  font=("", 12), foreground="gray").pack(pady=(0, 15))

        features = [
            "Real-time file monitoring (Filesystem Watcher)",
            "Multi-folder support",
            "Content-based file detection",
            "AI-powered rule suggestions",
            "Auto-cleanup / Retention policy",
            "Drag & Drop file sorting",
            "Regex Tester",
            "Dark/Light theme",
            "Backup / Restore configuration",
            "Keyboard shortcuts (Ctrl+S, Ctrl+Z, Ctrl+D)",
            "File preview",
            "Nested/Conditional rules (AND/OR)",
            "Notification system",
            "Logging dashboard",
            "Portable mode",
            "I18n (English/Russian)",
            "Scheduled cleanup",
        ]

        ttk.Label(center, text="New in v3.0:", font=("", 11, "bold")).pack(anchor=tk.W, pady=(10, 5))
        for feat in features:
            ttk.Label(center, text=f"  * {feat}", font=("", 9)).pack(anchor=tk.W)

        ttk.Separator(center, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        ttk.Label(center, text=self.app.i18n.t("lbl_support"),
                  font=("", 12, "bold")).pack(pady=(0, 5))
        ttk.Label(center, text=self.app.i18n.t("lbl_support_desc"),
                  font=("", 10)).pack(pady=(0, 10))

        ttk.Label(center, text=self.DONATE_URL,
                  font=("", 9), foreground="blue").pack(pady=2)

        donate_btn = ttk.Button(center, text="  Support Project  ",
                                 command=self._open_donate)
        donate_btn.pack(pady=10)

        ttk.Separator(center, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        ttk.Label(center, text=self.app.i18n.t("lbl_links"), font=("", 11, "bold")).pack(pady=(0, 5))

        links_frame = ttk.Frame(center)
        links_frame.pack()
        ttk.Label(links_frame, text="GitHub:", foreground="gray").grid(row=0, column=0, sticky=tk.E, padx=5)

        ttk.Separator(center, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        ttk.Label(center, text=self.app.i18n.t("lbl_made_with"),
                  font=("", 9), foreground="gray").pack()

    def _open_donate(self):
        webbrowser.open(self.DONATE_URL)
