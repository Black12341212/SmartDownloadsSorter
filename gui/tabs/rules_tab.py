#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Вкладка: Правила сортировки v3.0
Regex Tester + Nested Rules
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import re


class RulesTab:
    TAB_TITLE = "  Rules  "

    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.Frame(parent)
        self._build()
        self.refresh()

    def _build(self):
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, padx=10, pady=6)

        ttk.Button(toolbar, text=self.app.i18n.t("btn_add_rule"), command=self._add_rule).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text=self.app.i18n.t("btn_edit_rule"), command=self._edit_rule).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text=self.app.i18n.t("btn_delete_rule"), command=self._delete_rule).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text=self.app.i18n.t("btn_reset_defaults"), command=self._reset).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Regex Tester", command=self._open_regex_tester).pack(side=tk.LEFT, padx=8)
        ttk.Button(toolbar, text="Nested Rule", command=self._add_nested_rule).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text=self.app.i18n.t("btn_refresh"), command=self.refresh).pack(side=tk.RIGHT, padx=2)

        cols = ("Category", "Folder", "Extensions", "Conditions")
        self.tree = ttk.Treeview(self.frame, columns=cols, show="headings", selectmode="browse")
        for c in cols:
            self.tree.heading(c, text=c)
            w = 250 if c == "Extensions" else (150 if c == "Conditions" else 200)
            self.tree.column(c, width=w)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scrollbar = ttk.Scrollbar(self.tree, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for cat, rule in self.app.rules_mgr.all().items():
            exts = ", ".join(rule.get("extensions", [])[:5])
            if len(rule.get("extensions", [])) > 5:
                exts += "..."
            conditions = rule.get("conditions")
            cond_str = ""
            if conditions:
                logic = conditions.get("logic", "AND")
                count = len(conditions.get("rules", []))
                cond_str = f"{logic} ({count} rules)"
            self.tree.insert("", tk.END, values=(cat, rule.get("folder", cat), exts, cond_str))

    def _add_rule(self):
        cat = simpledialog.askstring("New Rule", "Category name:")
        if not cat:
            return
        folder = simpledialog.askstring("New Rule", "Folder name:", initialvalue=cat)
        if not folder:
            return
        exts_str = simpledialog.askstring("New Rule", "Extensions (comma-separated):\nExample: .txt,.pdf,.doc")
        exts = [e.strip() for e in exts_str.split(",") if e.strip()] if exts_str else []
        exts = [e if e.startswith(".") else f".{e}" for e in exts]

        self.app.rules_mgr.add(cat, {
            "folder": folder,
            "extensions": exts,
            "name_contains": [],
            "regex": [],
        })
        self.refresh()

    def _edit_rule(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Edit", self.app.i18n.t("msg_select_rule"))
            return
        cat = self.tree.item(sel[0])["values"][0]
        rule = self.app.rules_mgr.get(cat)
        if not rule:
            return

        new_folder = simpledialog.askstring("Edit Rule", f"Folder for '{cat}':",
                                            initialvalue=rule.get("folder", cat))
        if new_folder:
            rule["folder"] = new_folder
            self.app.rules_mgr.update(cat, rule)
            self.refresh()

    def _delete_rule(self):
        sel = self.tree.selection()
        if not sel:
            return
        cat = self.tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Delete", self.app.i18n.t("msg_delete_rule", cat)):
            self.app.rules_mgr.remove(cat)
            self.refresh()

    def _reset(self):
        if messagebox.askyesno("Reset", self.app.i18n.t("msg_reset_rules")):
            self.app.rules_mgr.reset()
            self.refresh()

    def _open_regex_tester(self):
        win = tk.Toplevel(self.frame)
        win.title(self.app.i18n.t("lbl_regex_tester"))
        win.geometry("550x350")
        win.transient(self.frame.winfo_toplevel())

        main = ttk.Frame(win, padding=15)
        main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main, text=self.app.i18n.t("lbl_regex_tester"),
                   font=("", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(main, text=self.app.i18n.t("lbl_test_pattern")).pack(anchor=tk.W)
        pattern_var = tk.StringVar()
        pattern_entry = ttk.Entry(main, textvariable=pattern_var, width=60, font=("Consolas", 10))
        pattern_entry.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(main, text=self.app.i18n.t("lbl_test_string")).pack(anchor=tk.W)
        test_var = tk.StringVar()
        test_entry = ttk.Entry(main, textvariable=test_var, width=60, font=("Consolas", 10))
        test_entry.pack(fill=tk.X, pady=(0, 8))

        result_var = tk.StringVar(value="")
        result_label = ttk.Label(main, textvariable=result_var, font=("", 11))
        result_label.pack(anchor=tk.W, pady=5)

        detail_var = tk.StringVar(value="")
        ttk.Label(main, textvariable=detail_var, foreground="gray", font=("Consolas", 9)).pack(anchor=tk.W)

        def _test():
            pattern = pattern_var.get()
            test_str = test_var.get()
            if not pattern or not test_str:
                result_var.set("")
                detail_var.set("")
                return
            try:
                match = re.search(pattern, test_str)
                if match:
                    result_var.set(self.app.i18n.t("lbl_match_found"))
                    detail_var.set(f"Match: '{match.group()}' at position {match.start()}-{match.end()}")
                    result_label.configure(foreground="green")
                else:
                    result_var.set(self.app.i18n.t("lbl_no_match"))
                    detail_var.set("")
                    result_label.configure(foreground="red")
            except re.error as e:
                result_var.set(f"Error: {e}")
                detail_var.set("")
                result_label.configure(foreground="red")

        pattern_var.trace_add("write", lambda *a: _test())
        test_var.trace_add("write", lambda *a: _test())

        ttk.Button(main, text="Test", command=_test).pack(pady=8)

    def _add_nested_rule(self):
        win = tk.Toplevel(self.frame)
        win.title("Create Nested Rule")
        win.geometry("500x450")
        win.transient(self.frame.winfo_toplevel())

        main = ttk.Frame(win, padding=15)
        main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main, text="Nested/Conditional Rule", font=("", 13, "bold")).pack(anchor=tk.W, pady=(0, 10))

        cat_frame = ttk.Frame(main)
        cat_frame.pack(fill=tk.X, pady=3)
        ttk.Label(cat_frame, text="Category:").pack(side=tk.LEFT)
        cat_var = tk.StringVar()
        ttk.Entry(cat_frame, textvariable=cat_var, width=30).pack(side=tk.LEFT, padx=5)

        folder_frame = ttk.Frame(main)
        folder_frame.pack(fill=tk.X, pady=3)
        ttk.Label(folder_frame, text="Folder:").pack(side=tk.LEFT)
        folder_var = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=folder_var, width=30).pack(side=tk.LEFT, padx=5)

        logic_frame = ttk.Frame(main)
        logic_frame.pack(fill=tk.X, pady=3)
        ttk.Label(logic_frame, text="Logic:").pack(side=tk.LEFT)
        logic_var = tk.StringVar(value="AND")
        ttk.Radiobutton(logic_frame, text="AND (all must match)", variable=logic_var, value="AND").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(logic_frame, text="OR (any can match)", variable=logic_var, value="OR").pack(side=tk.LEFT, padx=5)

        ttk.Label(main, text="Conditions (one per line):", font=("", 10, "bold")).pack(anchor=tk.W, pady=(8, 2))
        ttk.Label(main, text="Format: type:value  |  Types: ext, name, regex, size_min, size_max",
                   foreground="gray").pack(anchor=tk.W)
        ttk.Label(main, text="Example: ext:.pdf  |  name:book  |  size_min:5",
                   foreground="gray").pack(anchor=tk.W)

        conditions_text = tk.Text(main, height=8, width=60, font=("Consolas", 9))
        conditions_text.pack(fill=tk.BOTH, expand=True, pady=5)

        def _create():
            cat = cat_var.get().strip()
            folder = folder_var.get().strip()
            if not cat or not folder:
                messagebox.showwarning("Error", "Category and folder required")
                return

            raw = conditions_text.get("1.0", tk.END).strip()
            condition_list = []
            for line in raw.split("\n"):
                line = line.strip()
                if not line:
                    continue
                parts = line.split(":", 1)
                if len(parts) != 2:
                    continue
                ctype, value = parts
                ctype = ctype.strip().lower()
                value = value.strip()
                if ctype == "ext":
                    exts = [e.strip() for e in value.split(",")]
                    exts = [e if e.startswith(".") else f".{e}" for e in exts]
                    condition_list.append({"type": "extension", "extensions": exts})
                elif ctype == "name":
                    condition_list.append({"type": "name_contains", "keywords": [value]})
                elif ctype == "regex":
                    condition_list.append({"type": "regex", "patterns": [value]})
                elif ctype == "size_min":
                    condition_list.append({"type": "size_min", "value": float(value)})
                elif ctype == "size_max":
                    condition_list.append({"type": "size_max", "value": float(value)})

            if not condition_list:
                messagebox.showwarning("Error", "No valid conditions")
                return

            self.app.rules_mgr.add_nested_rule(cat, folder, {
                "logic": logic_var.get(),
                "rules": condition_list,
            })
            self.refresh()
            win.destroy()

        ttk.Button(main, text="Create Rule", command=_create).pack(pady=8)
