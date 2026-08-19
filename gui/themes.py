#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dark/Light Theme support for tkinter GUI"""

import tkinter as tk
from tkinter import ttk

DARK_THEME = {
    "bg": "#1e1e1e",
    "fg": "#d4d4d4",
    "bg_secondary": "#2d2d2d",
    "bg_tertiary": "#3c3c3c",
    "accent": "#569cd6",
    "accent_hover": "#6db3f2",
    "error": "#f44747",
    "success": "#6a9955",
    "warning": "#ce9178",
    "border": "#555555",
    "selection": "#264f78",
    "tree_bg": "#1e1e1e",
    "tree_fg": "#d4d4d4",
    "tree_select": "#264f78",
    "text_bg": "#1e1e1e",
    "text_fg": "#d4d4d4",
    "entry_bg": "#3c3c3c",
    "entry_fg": "#d4d4d4",
    "btn_bg": "#0e639c",
    "btn_fg": "#ffffff",
    "btn_active": "#1177bb",
    "disabled_fg": "#808080",
    "link_color": "#569cd6",
    "notebook_bg": "#1e1e1e",
}

LIGHT_THEME = {
    "bg": "#f0f0f0",
    "fg": "#000000",
    "bg_secondary": "#ffffff",
    "bg_tertiary": "#e0e0e0",
    "accent": "#0078d4",
    "accent_hover": "#106ebe",
    "error": "#d32f2f",
    "success": "#388e3c",
    "warning": "#f57c00",
    "border": "#cccccc",
    "selection": "#0078d4",
    "tree_bg": "#ffffff",
    "tree_fg": "#000000",
    "tree_select": "#0078d4",
    "text_bg": "#ffffff",
    "text_fg": "#000000",
    "entry_bg": "#ffffff",
    "entry_fg": "#000000",
    "btn_bg": "#0078d4",
    "btn_fg": "#ffffff",
    "btn_active": "#106ebe",
    "disabled_fg": "#a0a0a0",
    "link_color": "#0078d4",
    "notebook_bg": "#f0f0f0",
}


class ThemeManager:
    def __init__(self):
        self.current_theme = "light"
        self.colors = dict(LIGHT_THEME)
        self._style = None

    def apply_theme(self, root, theme_name="light"):
        self.current_theme = theme_name
        if theme_name == "dark":
            self.colors = dict(DARK_THEME)
            self._apply_dark(root)
        else:
            self.colors = dict(LIGHT_THEME)
            self._apply_light(root)

    def _apply_dark(self, root):
        style = ttk.Style()
        style.theme_use("clam")

        c = DARK_THEME
        style.configure(".", background=c["bg"], foreground=c["fg"],
                         bordercolor=c["border"], darkcolor=c["bg"],
                         lightcolor=c["bg_tertiary"], troughcolor=c["bg_secondary"],
                         selectbackground=c["selection"], selectforeground=c["fg"],
                         fieldbackground=c["entry_bg"], font=("Segoe UI", 9))

        style.configure("TFrame", background=c["bg"])
        style.configure("TLabel", background=c["bg"], foreground=c["fg"])
        style.configure("TButton", background=c["btn_bg"], foreground=c["btn_fg"],
                         bordercolor=c["border"], padding=(8, 4))
        style.map("TButton",
                   background=[("active", c["btn_active"]), ("disabled", c["bg_tertiary"])],
                   foreground=[("disabled", c["disabled_fg"])])

        style.configure("TCheckbutton", background=c["bg"], foreground=c["fg"],
                         indicatorcolor=c["entry_bg"])
        style.map("TCheckbutton",
                   indicatorcolor=[("selected", c["accent"])])

        style.configure("TEntry", fieldbackground=c["entry_bg"], foreground=c["entry_fg"],
                         bordercolor=c["border"])

        style.configure("Treeview",
                         background=c["tree_bg"], foreground=c["tree_fg"],
                         fieldbackground=c["tree_bg"], bordercolor=c["border"],
                         rowheight=24)
        style.configure("Treeview.Heading",
                         background=c["bg_tertiary"], foreground=c["fg"],
                         bordercolor=c["border"])
        style.map("Treeview",
                   background=[("selected", c["tree_select"])],
                   foreground=[("selected", c["fg"])])

        style.configure("TNotebook", background=c["notebook_bg"],
                         bordercolor=c["border"])
        style.configure("TNotebook.Tab", background=c["bg_tertiary"],
                         foreground=c["fg"], padding=(12, 4))
        style.map("TNotebook.Tab",
                   background=[("selected", c["bg"])],
                   foreground=[("selected", c["accent"])])

        style.configure("Horizontal.TScale", background=c["bg"],
                         troughcolor=c["bg_secondary"])
        style.configure("Horizontal.TProgressbar",
                         background=c["accent"], troughcolor=c["bg_secondary"])

        style.configure("Horizontal.TScrollbar",
                         background=c["bg_tertiary"], troughcolor=c["bg_secondary"],
                         bordercolor=c["border"], arrowcolor=c["fg"])

        style.configure("Vertical.TScrollbar",
                         background=c["bg_tertiary"], troughcolor=c["bg_secondary"],
                         bordercolor=c["border"], arrowcolor=c["fg"])

        style.configure("TSeparator", background=c["border"])

        style.configure("TLabelframe", background=c["bg"], foreground=c["fg"],
                         bordercolor=c["border"])
        style.configure("TLabelframe.Label", background=c["bg"], foreground=c["accent"])

        style.configure("TLabel", background=c["bg"], foreground=c["fg"])

        style.configure("Accent.TButton", background=c["accent"], foreground=c["btn_fg"])
        style.map("Accent.TButton",
                   background=[("active", c["accent_hover"])])

        style.configure("Error.TLabel", foreground=c["error"])
        style.configure("Success.TLabel", foreground=c["success"])
        style.configure("Warning.TLabel", foreground=c["warning"])

        root.configure(bg=c["bg"])

    def _apply_light(self, root):
        style = ttk.Style()
        style.theme_use("clam")

        c = LIGHT_THEME
        style.configure(".", background=c["bg"], foreground=c["fg"],
                         bordercolor=c["border"], selectbackground=c["selection"],
                         selectforeground=c["fg"], fieldbackground=c["entry_bg"],
                         font=("Segoe UI", 9))

        style.configure("TFrame", background=c["bg"])
        style.configure("TLabel", background=c["bg"], foreground=c["fg"])
        style.configure("TButton", background=c["bg_tertiary"], foreground=c["fg"],
                         bordercolor=c["border"], padding=(8, 4))
        style.map("TButton",
                   background=[("active", c["accent_hover"]), ("disabled", c["bg_tertiary"])],
                   foreground=[("disabled", c["disabled_fg"])])

        style.configure("TCheckbutton", background=c["bg"], foreground=c["fg"])
        style.configure("TEntry", fieldbackground=c["entry_bg"], foreground=c["entry_fg"])
        style.configure("Treeview", background=c["tree_bg"], foreground=c["tree_fg"],
                         fieldbackground=c["tree_bg"], rowheight=24)
        style.configure("Treeview.Heading", background=c["bg_tertiary"], foreground=c["fg"])
        style.map("Treeview", background=[("selected", c["tree_select"])])

        style.configure("TNotebook", background=c["notebook_bg"])
        style.configure("TNotebook.Tab", background=c["bg_tertiary"], foreground=c["fg"],
                         padding=(12, 4))
        style.map("TNotebook.Tab",
                   background=[("selected", c["bg"])],
                   foreground=[("selected", c["accent"])])

        style.configure("Horizontal.TScale", background=c["bg"],
                         troughcolor=c["bg_secondary"])
        style.configure("Horizontal.TProgressbar",
                         background=c["accent"], troughcolor=c["bg_secondary"])
        style.configure("Horizontal.TScrollbar",
                         background=c["bg_tertiary"], troughcolor=c["bg_secondary"])
        style.configure("Vertical.TScrollbar",
                         background=c["bg_tertiary"], troughcolor=c["bg_secondary"])
        style.configure("TSeparator", background=c["border"])
        style.configure("Accent.TButton", background=c["accent"], foreground=c["btn_fg"])

        root.configure(bg=c["bg"])

    def get_color(self, key):
        return self.colors.get(key, "#000000")
