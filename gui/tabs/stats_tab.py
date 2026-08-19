#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Вкладка: Статистика v3.0"""

import os
import tkinter as tk
from tkinter import ttk
from collections import defaultdict


class StatsTab:
    TAB_TITLE = "  Stats  "

    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.Frame(parent)
        self._build()
        self.refresh()

    def _build(self):
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, padx=10, pady=6)
        ttk.Button(toolbar, text=self.app.i18n.t("btn_refresh"), command=self.refresh).pack(side=tk.RIGHT)

        self.summary_var = tk.StringVar(value=self.app.i18n.t("msg_click_refresh"))
        ttk.Label(self.frame, textvariable=self.summary_var, font=("", 10),
                  padding=10).pack(fill=tk.X)

        cols = ("Extension", "Count", "Size (MB)")
        self.tree = ttk.Treeview(self.frame, columns=cols, show="headings", selectmode="browse")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=200)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scrollbar = ttk.Scrollbar(self.tree, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        path = self.app.engine.downloads_path
        if not os.path.exists(path):
            self.summary_var.set(self.app.i18n.t("msg_path_not_found", path))
            return

        try:
            files = [f for f in os.listdir(path)
                     if os.path.isfile(os.path.join(path, f))]
        except Exception:
            self.summary_var.set(self.app.i18n.t("msg_cannot_read"))
            return

        stats = defaultdict(lambda: {"count": 0, "size": 0})
        total_size = 0
        for fname in files:
            ext = os.path.splitext(fname)[1].lower() or "(no ext)"
            fpath = os.path.join(path, fname)
            try:
                size = os.path.getsize(fpath) / (1024 * 1024)
            except OSError:
                size = 0
            stats[ext]["count"] += 1
            stats[ext]["size"] += size
            total_size += size

        self.summary_var.set(
            f"{self.app.i18n.t('msg_files', len(files))}  |  "
            f"{self.app.i18n.t('msg_total_size', f'{total_size:.1f}')}  |  "
            f"{self.app.i18n.t('msg_categories', len(stats))}"
        )

        sorted_stats = sorted(stats.items(), key=lambda x: x[1]["count"], reverse=True)
        for ext, data in sorted_stats:
            self.tree.insert("", tk.END, values=(
                ext, data["count"], f"{data['size']:.1f}"
            ))
