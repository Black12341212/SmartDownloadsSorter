#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Вкладка: Поиск дубликатов v3.0"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from core.duplicates import get_duplicate_summary, delete_duplicates


class DuplicatesTab:
    TAB_TITLE = "  Duplicates  "

    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.Frame(parent)
        self._build()

    def _build(self):
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, padx=10, pady=6)

        i = self.app.i18n

        self.use_hash_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(toolbar, text=i.t("lbl_use_hash"),
                         variable=self.use_hash_var).pack(side=tk.LEFT)

        ttk.Button(toolbar, text=i.t("btn_scan"), command=self._scan).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text=i.t("btn_delete"), command=self._delete_selected).pack(
            side=tk.LEFT, padx=4
        )

        self.summary_var = tk.StringVar(value="")
        ttk.Label(toolbar, textvariable=self.summary_var).pack(side=tk.RIGHT)

        cols = ("File", "Copies", "Size (MB)", "Wasted (MB)", "Path")
        self.tree = ttk.Treeview(self.frame, columns=cols, show="headings", selectmode="extended")
        for c in cols:
            self.tree.heading(c, text=c)
            w = 120 if c in ("Copies", "Size (MB)", "Wasted (MB)") else 300
            self.tree.column(c, width=w)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scrollbar = ttk.Scrollbar(self.tree, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh(self):
        pass

    def _scan(self):
        path = self.app.engine.downloads_path
        if not os.path.exists(path):
            messagebox.showerror(self.app.i18n.t("msg_error"),
                                 self.app.i18n.t("msg_path_not_found", path))
            return

        self.tree.delete(*self.tree.get_children())
        results, wasted = get_duplicate_summary(path, self.use_hash_var.get())
        self.summary_var.set(self.app.i18n.t("msg_duplicates_found",
                                              len(results), f"{wasted/(1024*1024):.1f}"))

        for group in results:
            paths_str = "\n".join(group["paths"][:3])
            self.tree.insert("", tk.END, values=(
                group["name"],
                group["count"],
                f"{group['size']/(1024*1024):.2f}",
                f"{group['wasted']/(1024*1024):.2f}",
                paths_str,
            ))

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        if not messagebox.askyesno(self.app.i18n.t("msg_confirm"),
                                    self.app.i18n.t("msg_delete_duplicates", len(sel))):
            return
        deleted_total = 0
        for item in sel:
            vals = self.tree.item(item)["values"]
            name = vals[0]
            path = self.app.engine.downloads_path
            from core.duplicates import find_duplicates_by_name_size
            groups = find_duplicates_by_name_size(path)
            for key, paths in groups.items():
                if os.path.basename(paths[0]) == name:
                    _, deleted = delete_duplicates(paths)
                    deleted_total += len(deleted)
                    break
        self.tree.delete(*sel)
        self.summary_var.set(self.app.i18n.t("msg_deleted_n", deleted_total))
