#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Вкладка: История и Undo v3.0"""

import tkinter as tk
from tkinter import ttk, messagebox


class HistoryTab:
    TAB_TITLE = "  History  "

    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.Frame(parent)
        self._build()
        self.refresh()

    def _build(self):
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, padx=10, pady=6)

        i = self.app.i18n

        ttk.Button(toolbar, text=i.t("btn_undo_last"), command=self._undo_last).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text=i.t("btn_undo_5"), command=self._undo_5).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text=i.t("btn_clear_history"), command=self._clear).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text=i.t("btn_refresh"), command=self.refresh).pack(side=tk.RIGHT, padx=2)

        cols = ("Time", "File", "From", "To", "Category")
        self.tree = ttk.Treeview(self.frame, columns=cols, show="headings", selectmode="browse")
        for c in cols:
            self.tree.heading(c, text=c)
            w = 140 if c == "Time" else 200
            self.tree.column(c, width=w)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scrollbar = ttk.Scrollbar(self.tree, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for entry in self.app.history_mgr.get_entries(limit=200):
            ts = entry.get("timestamp", "")[:19].replace("T", " ")
            self.tree.insert("", tk.END, values=(
                ts,
                entry.get("filename", ""),
                entry.get("source", ""),
                entry.get("dest", ""),
                entry.get("category", ""),
            ))

    def _undo_last(self):
        undone = self.app.history_mgr.undo_last(1)
        if undone:
            messagebox.showinfo(self.app.i18n.t("msg_undo"),
                                self.app.i18n.t("msg_undid", undone[0].get('filename', '')))
            self.refresh()
        else:
            messagebox.showinfo(self.app.i18n.t("msg_undo"), self.app.i18n.t("msg_nothing_undo"))

    def _undo_5(self):
        undone = self.app.history_mgr.undo_last(5)
        if undone:
            messagebox.showinfo(self.app.i18n.t("msg_undo"),
                                self.app.i18n.t("msg_undid_n", len(undone)))
            self.refresh()
        else:
            messagebox.showinfo(self.app.i18n.t("msg_undo"), self.app.i18n.t("msg_nothing_undo"))

    def _clear(self):
        if messagebox.askyesno("Clear", self.app.i18n.t("msg_clear_history")):
            self.app.history_mgr.clear()
            self.refresh()
