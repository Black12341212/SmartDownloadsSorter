#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Вкладка: Сортировка (главная) v3.0
Drag & Drop + File Preview
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os


class MainTab:
    TAB_TITLE = "  Sort  "

    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.Frame(parent)
        self._preview_window = None
        self._build()
        self._setup_drag_drop()

    def _build(self):
        top = ttk.Frame(self.frame)
        top.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(top, text=self.app.i18n.t("lbl_downloads_folder"), font=("", 10)).pack(side=tk.LEFT)
        self.path_var = tk.StringVar(value=self.app.engine.downloads_path)
        self.path_entry = ttk.Entry(top, textvariable=self.path_var, width=50)
        self.path_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(top, text=self.app.i18n.t("btn_browse"), command=self._browse).pack(side=tk.LEFT, padx=2)

        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill=tk.X, padx=10)

        self.sort_btn = ttk.Button(btn_frame, text=self.app.i18n.t("btn_sort_now"), command=self._sort)
        self.sort_btn.pack(side=tk.LEFT, padx=4)

        self.dry_btn = ttk.Button(btn_frame, text=self.app.i18n.t("btn_dry_run"), command=self._dry_run)
        self.dry_btn.pack(side=tk.LEFT, padx=4)

        ttk.Button(btn_frame, text=self.app.i18n.t("btn_refresh"), command=self._refresh_log).pack(
            side=tk.LEFT, padx=4
        )

        self.progress = ttk.Progressbar(btn_frame, mode="indeterminate", length=200)
        self.progress.pack(side=tk.RIGHT, padx=4)

        self.log_area = scrolledtext.ScrolledText(self.frame, height=20, width=90,
                                                   font=("Consolas", 9), state=tk.DISABLED)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        drop_label = ttk.Label(self.frame, text=self.app.i18n.t("lbl_drag_drop"),
                                foreground="gray", font=("", 9))
        drop_label.pack(pady=(0, 5))

    def _setup_drag_drop(self):
        try:
            self.frame.drop_target_register(tk.DND_FILES)
            self.frame.dnd_bind("<<Drop>>", self._on_drop)
        except Exception:
            try:
                import tkinterdnd2
                self.frame.drop_target_register(tkinterdnd2.DND_FILES)
                self.frame.dnd_bind("<<Drop>>", self._on_drop)
            except Exception:
                pass

    def _on_drop(self, event):
        files = self.frame.tk.splitlist(event.data)
        if files:
            self._preview_files(list(files))

    def _preview_files(self, filepaths):
        win = tk.Toplevel(self.frame)
        win.title(self.app.i18n.t("lbl_file_preview"))
        win.geometry("600x500")
        win.transient(self.frame.winfo_toplevel())

        ttk.Label(win, text=self.app.i18n.t("lbl_file_preview"),
                   font=("", 14, "bold")).pack(pady=10)

        cols = ("File", "Size", "Type", "Action")
        tree = ttk.Treeview(win, columns=cols, show="headings", selectmode="extended")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=150 if c != "File" else 250)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        file_data = []
        for fp in filepaths:
            if os.path.isfile(fp):
                name = os.path.basename(fp)
                size = os.path.getsize(fp) / (1024 * 1024)
                ext = os.path.splitext(name)[1].lower() or "(no ext)"
                tree.insert("", tk.END, values=(name, f"{size:.2f} MB", ext, "Sort by rules"))
                file_data.append(fp)

        def _sort_dropped():
            from core.sorter_engine import SorterEngine
            for fp in file_data:
                if os.path.isfile(fp):
                    directory = os.path.dirname(fp)
                    self.app.engine.downloads_path = directory
                    self.app.engine.sort(target_path=directory)
            self._append_log(f"Sorted {len(file_data)} dropped files")
            win.destroy()

        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text=self.app.i18n.t("btn_sort_now"), command=_sort_dropped).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side=tk.LEFT, padx=5)

    def _browse(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Select folder to sort")
        if path:
            self.path_var.set(path)
            self.app.engine.downloads_path = path

    def _sort(self):
        self.app.engine.downloads_path = self.path_var.get()
        self.sort_btn.config(state=tk.DISABLED)
        self.progress.start(10)
        threading.Thread(target=self._run_sort, args=(False,), daemon=True).start()

    def _dry_run(self):
        self.app.engine.downloads_path = self.path_var.get()
        self.sort_btn.config(state=tk.DISABLED)
        self.progress.start(10)
        threading.Thread(target=self._run_sort, args=(True,), daemon=True).start()

    def _run_sort(self, dry_run):
        import io
        import sys
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            result = self.app.engine.sort(dry_run=dry_run)
        finally:
            sys.stdout = old_stdout
        output = buf.getvalue()
        self.frame.after(0, lambda: self._show_result(output, result, dry_run))

    def _show_result(self, output, result, dry_run):
        self.progress.stop()
        self.sort_btn.config(state=tk.NORMAL)
        self._append_log(output if output else str(result))
        self.app.status_var.set(
            f"{'Dry run' if dry_run else 'Sort'}: {result.get('moved', 0)} files"
        )
        self.app.notification_mgr.notify_sort_complete(result)

    def _append_log(self, text):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, text + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)

    def _refresh_log(self):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state=tk.DISABLED)
