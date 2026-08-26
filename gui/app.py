#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Главное окно GUI (tkinter) с вкладками
v3.0: Dark theme, i18n, keyboard shortcuts, notifications, watcher, backup
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cloud_sync import SettingsManager
from core.rules_manager import RulesManager
from core.history import HistoryManager
from core.ignore_list import IgnoreList
from core.duplicates import get_duplicate_summary
from core.profiles import ProfileManager
from core.plugin_loader import PluginLoader
from core.scheduler import Scheduler, CleanupScheduler
from core.sorter_engine import SorterEngine
from core.logger import setup_logger
from core.portable import get_config_dir, is_portable_mode
from core.i18n import I18n
from core.watcher import FileWatcher
from core.retention import RetentionManager
from core.notifications import NotificationManager
from core.backup import create_backup, restore_backup
from core.ai_suggester import AISuggester
from gui.themes import ThemeManager

from gui.tabs.main_tab import MainTab
from gui.tabs.rules_tab import RulesTab
from gui.tabs.schedule_tab import ScheduleTab
from gui.tabs.stats_tab import StatsTab
from gui.tabs.duplicates_tab import DuplicatesTab
from gui.tabs.settings_tab import SettingsTab
from gui.tabs.about_tab import AboutTab
from gui.tabs.history_tab import HistoryTab
from gui.tabs.logging_tab import LoggingTab


class SmartSorterApp:
    VERSION = "3.0.2"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Smart Downloads Sorter v{self.VERSION}")
        self.root.geometry("1000x700")
        self.root.minsize(850, 600)

        self.settings_mgr = SettingsManager()
        self.rules_mgr = RulesManager()
        self.history_mgr = HistoryManager()
        self.ignore_list = IgnoreList()
        self.profile_mgr = ProfileManager()
        self.plugin_loader = PluginLoader()
        self.plugin_loader.discover()

        self.i18n = I18n(self.settings_mgr.get("language", "en"))
        self.theme_mgr = ThemeManager()
        self.notification_mgr = NotificationManager(self.settings_mgr.settings)
        self.retention_mgr = RetentionManager(self.settings_mgr.settings)
        self.ai_suggester = AISuggester(self.history_mgr, self.rules_mgr)
        self.watcher = FileWatcher(sort_callback=self._watcher_sort)

        self.engine = SorterEngine(
            downloads_path=self.settings_mgr.get("downloads_path"),
            rules_manager=self.rules_mgr,
            history_manager=self.history_mgr,
            ignore_list=self.ignore_list,
            settings=self.settings_mgr.settings,
            plugin_loader=self.plugin_loader,
        )

        self.scheduler = Scheduler(
            sort_callback=self._auto_sort,
            log_callback=lambda msg: setup_logger().info(msg),
        )

        self.cleanup_scheduler = CleanupScheduler(
            cleanup_callback=self._scheduled_cleanup,
            settings=self.settings_mgr.settings,
        )

        if self.settings_mgr.get("auto_sort_enabled"):
            self.scheduler.set_interval(self.settings_mgr.get("auto_sort_interval", 15))
            self.scheduler.start()

        self._build_ui()
        self._apply_theme()
        self._bind_shortcuts()

        if self.settings_mgr.get("watcher_enabled"):
            self._start_watcher()

        if self.settings_mgr.get("scheduled_cleanup_enabled"):
            self.cleanup_scheduler.start()

    def _build_ui(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=self.i18n.t("menu_sort_now"), command=self._sort_now)
        file_menu.add_command(label=self.i18n.t("menu_dry_run"), command=self._dry_run)
        file_menu.add_separator()
        file_menu.add_command(label=self.i18n.t("menu_exit"), command=self.root.quit)
        menubar.add_cascade(label=self.i18n.t("menu_file"), menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=self.i18n.t("menu_support"), command=self._open_donate)
        help_menu.add_separator()
        help_menu.add_command(label=self.i18n.t("menu_about"), command=self._show_about)
        menubar.add_cascade(label=self.i18n.t("menu_help"), menu=help_menu)
        self.root.config(menu=menubar)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.tabs = {}
        self.tabs["main"] = MainTab(self.notebook, self)
        self.tabs["rules"] = RulesTab(self.notebook, self)
        self.tabs["history"] = HistoryTab(self.notebook, self)
        self.tabs["schedule"] = ScheduleTab(self.notebook, self)
        self.tabs["stats"] = StatsTab(self.notebook, self)
        self.tabs["duplicates"] = DuplicatesTab(self.notebook, self)
        self.tabs["logs"] = LoggingTab(self.notebook, self)
        self.tabs["settings"] = SettingsTab(self.notebook, self)
        self.tabs["about"] = AboutTab(self.notebook, self)

        for key, tab in self.tabs.items():
            self.notebook.add(tab.frame, text=tab.TAB_TITLE)

        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_var = tk.StringVar(value=self.i18n.t("lbl_ready"))
        ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN,
                  anchor=tk.W).pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.donate_btn = ttk.Label(status_frame, text="  Buy me a coffee  ",
                                     cursor="hand2", foreground="#8B6914")
        self.donate_btn.pack(side=tk.RIGHT, padx=4)
        self.donate_btn.bind("<Button-1>", lambda e: self._open_donate())

    def _apply_theme(self):
        theme = self.settings_mgr.get("theme", "default")
        if theme in ("dark", "light"):
            self.theme_mgr.apply_theme(self.root, theme)
        else:
            style = ttk.Style()
            style.theme_use("clam")

    def _bind_shortcuts(self):
        def guarded(action):
            def handler(event):
                if self._is_typing():
                    return
                action()
            return handler

        self.root.bind("<Control-s>", guarded(self._sort_now))
        self.root.bind("<Control-S>", guarded(self._sort_now))
        self.root.bind("<Control-z>", guarded(self._undo_last))
        self.root.bind("<Control-Z>", guarded(self._undo_last))
        self.root.bind("<Control-d>", lambda e: self._dry_run())
        self.root.bind("<Control-D>", lambda e: self._dry_run())
        self.root.bind("<Control-r>", lambda e: self._refresh_current_tab())
        self.root.bind("<Control-R>", lambda e: self._refresh_current_tab())
        self.root.bind("<F5>", lambda e: self._sort_now())
        self.root.bind("<Control-q>", guarded(self.root.quit))
        self.root.bind("<Control-Q>", guarded(self.root.quit))

    def _is_typing(self):
        w = self.root.focus_get()
        return isinstance(w, (tk.Entry, tk.Text, tk.Spinbox,
                              ttk.Entry, ttk.Combobox, ttk.Spinbox))

    def _refresh_current_tab(self):
        current = self.notebook.select()
        for tab in self.tabs.values():
            if str(tab.frame) == str(current):
                if hasattr(tab, "refresh"):
                    tab.refresh()
                break

    def _undo_last(self):
        undone = self.history_mgr.undo_last(1)
        if undone:
            self.status_var.set(f"Undid: {undone[0].get('filename', '')}")
        else:
            self.status_var.set("Nothing to undo")

    def _sort_now(self):
        self.status_var.set(self.i18n.t("lbl_sorting"))
        self.root.update_idletasks()
        threading.Thread(target=self._run_sort_now, daemon=True).start()

    def _run_sort_now(self):
        result = self.engine.sort()
        moved = result.get("moved", 0)
        self.root.after(0, lambda: self._finish_sort_now(result, moved))

    def _finish_sort_now(self, result, moved):
        self.status_var.set(f"Done: {moved} files moved")
        self.notification_mgr.notify_sort_complete(result)
        if hasattr(self.tabs.get("stats"), "refresh"):
            self.tabs["stats"].refresh()
        messagebox.showinfo(self.i18n.t("msg_sort_complete"),
                            self.i18n.t("msg_moved", moved))

    def _dry_run(self):
        self.status_var.set(self.i18n.t("lbl_dry_run"))
        self.root.update_idletasks()
        result = self.engine.sort(dry_run=True)
        moved = result.get("moved", 0)
        self.status_var.set(f"Dry run: {moved} would be moved")
        messagebox.showinfo(self.i18n.t("msg_dry_run"),
                            self.i18n.t("msg_would_move", moved))

    def _auto_sort(self):
        result = self.engine.sort()
        moved = result.get("moved", 0)
        self.root.after(0, lambda: self.status_var.set(f"Auto: {moved} files moved"))
        self.notification_mgr.notify_sort_complete(result)

    def _watcher_sort(self, target_path=None):
        result = self.engine.sort(target_path=target_path)
        moved = result.get("moved", 0)
        if moved > 0:
            self.root.after(0, lambda: self.status_var.set(f"Watcher: {moved} files moved"))
            self.notification_mgr.notify_sort_complete(result)

    def _start_watcher(self):
        paths = self.settings_mgr.get("monitored_folders", [])
        if not paths:
            paths = [self.settings_mgr.get("downloads_path", "")]
        for p in paths:
            if p and os.path.isdir(p):
                self.watcher.add_directory(p)
        self.watcher.start()

    def _stop_watcher(self):
        self.watcher.stop()

    def _scheduled_cleanup(self):
        base = self.settings_mgr.get("downloads_path", "")
        result = self.retention_mgr.cleanup(base)
        self.notification_mgr.notify_cleanup(result)

    def _open_donate(self):
        import webbrowser
        webbrowser.open("https://www.donationalerts.com/r/zenixx5678")

    def _show_about(self):
        self.notebook.select(self.tabs["about"].frame)

    def apply_language(self, lang):
        self.i18n.set_language(lang)
        self.settings_mgr.set("language", lang)

    def apply_theme_to_all(self, theme_name):
        self.theme_mgr.apply_theme(self.root, theme_name)
        self.settings_mgr.set("theme", theme_name)

    def run(self):
        self.root.mainloop()

    def on_close(self):
        self.watcher.stop()
        self.cleanup_scheduler.stop()
        self.scheduler.stop()
        self.root.quit()
        self.root.destroy()


def run_gui():
    app = SmartSorterApp()
    app.root.protocol("WM_DELETE_WINDOW", app.on_close)
    app.run()


if __name__ == "__main__":
    run_gui()
