#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Вкладка: Настройки v3.0 - all new settings sections"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog, scrolledtext


class SettingsTab:
    TAB_TITLE = "  Settings  "

    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.Frame(parent)
        self._build()

    def _build(self):
        canvas = tk.Canvas(self.frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        main = scroll_frame

        i = self.app.i18n

        # --- General ---
        ttk.Label(main, text=i.t("lbl_general"), font=("", 12, "bold")).pack(anchor=tk.W, padx=10, pady=(10, 5))

        path_frame = ttk.Frame(main)
        path_frame.pack(fill=tk.X, padx=10, pady=2)
        ttk.Label(path_frame, text=i.t("lbl_downloads_folder")).pack(side=tk.LEFT)
        self.path_var = tk.StringVar(value=self.app.settings_mgr.get("downloads_path"))
        ttk.Entry(path_frame, textvariable=self.path_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(path_frame, text=i.t("btn_browse"), command=self._browse_path).pack(side=tk.LEFT)

        # Multi-folder support
        folders_frame = ttk.Frame(main)
        folders_frame.pack(fill=tk.X, padx=10, pady=2)
        ttk.Label(folders_frame, text=i.t("lbl_monitor_folders")).pack(side=tk.LEFT)
        self.folders_var = tk.StringVar(value=", ".join(self.app.settings_mgr.get("monitored_folders", [])))
        ttk.Entry(folders_frame, textvariable=self.folders_var, width=50).pack(side=tk.LEFT, padx=5)

        date_frame = ttk.Frame(main)
        date_frame.pack(fill=tk.X, padx=10, pady=2)
        self.date_sort_var = tk.BooleanVar(value=self.app.settings_mgr.get("sort_by_date", False))
        ttk.Checkbutton(date_frame, text=i.t("lbl_sort_by_date"),
                         variable=self.date_sort_var).pack(side=tk.LEFT)

        startup_frame = ttk.Frame(main)
        startup_frame.pack(fill=tk.X, padx=10, pady=2)
        self.startup_var = tk.BooleanVar(value=self.app.settings_mgr.get("launch_on_startup", False))
        ttk.Checkbutton(startup_frame, text=i.t("lbl_launch_startup"),
                         variable=self.startup_var).pack(side=tk.LEFT)

        # --- Language ---
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(main, text=i.t("lbl_language"), font=("", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)

        lang_frame = ttk.Frame(main)
        lang_frame.pack(fill=tk.X, padx=10, pady=2)
        ttk.Label(lang_frame, text=i.t("lbl_language") + ":").pack(side=tk.LEFT)
        self.lang_var = tk.StringVar(value=self.app.settings_mgr.get("language", "en"))
        lang_names = {"en": "English", "ru": "Русский"}
        ttk.Combobox(lang_frame, textvariable=self.lang_var, values=list(lang_names.keys()),
                      state="readonly", width=15).pack(side=tk.LEFT, padx=5)

        # --- Theme ---
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(main, text=i.t("lbl_theme"), font=("", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)

        theme_frame = ttk.Frame(main)
        theme_frame.pack(fill=tk.X, padx=10, pady=2)
        ttk.Label(theme_frame, text=i.t("lbl_theme") + ":").pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value=self.app.settings_mgr.get("theme", "default"))
        ttk.Combobox(theme_frame, textvariable=self.theme_var,
                      values=["default", "light", "dark"],
                      state="readonly", width=15).pack(side=tk.LEFT, padx=5)

        # --- Portable Mode ---
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(main, text=i.t("lbl_portable"), font=("", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)

        portable_frame = ttk.Frame(main)
        portable_frame.pack(fill=tk.X, padx=10, pady=2)
        self.portable_var = tk.BooleanVar(value=self.app.settings_mgr.get("portable_mode", False))
        ttk.Checkbutton(portable_frame, text=i.t("lbl_portable"),
                         variable=self.portable_var).pack(side=tk.LEFT)

        # --- Content Detection ---
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(main, text=i.t("lbl_content_detection"), font=("", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)

        cd_frame = ttk.Frame(main)
        cd_frame.pack(fill=tk.X, padx=10, pady=2)
        self.content_det_var = tk.BooleanVar(value=self.app.settings_mgr.get("content_detection_enabled", False))
        ttk.Checkbutton(cd_frame, text=i.t("lbl_content_detection_info"),
                         variable=self.content_det_var).pack(side=tk.LEFT)

        # --- Notifications ---
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(main, text=i.t("lbl_notifications"), font=("", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)

        notif_frame = ttk.Frame(main)
        notif_frame.pack(fill=tk.X, padx=10, pady=2)
        self.notif_var = tk.BooleanVar(value=self.app.settings_mgr.get("notify_on_sort", True))
        ttk.Checkbutton(notif_frame, text=i.t("lbl_notify_on_sort"),
                         variable=self.notif_var).pack(side=tk.LEFT)

        # --- Filesystem Watcher ---
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(main, text=i.t("lbl_monitoring"), font=("", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)

        watcher_frame = ttk.Frame(main)
        watcher_frame.pack(fill=tk.X, padx=10, pady=2)
        self.watcher_var = tk.BooleanVar(value=self.app.settings_mgr.get("watcher_enabled", False))
        ttk.Checkbutton(watcher_frame, text=i.t("lbl_watcher_enabled"),
                         variable=self.watcher_var).pack(side=tk.LEFT)

        ttk.Label(main, text=i.t("lbl_watcher_info"), foreground="gray").pack(anchor=tk.W, padx=10)

        # --- Retention Policy ---
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(main, text=i.t("lbl_retention"), font=("", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)

        ret_frame = ttk.Frame(main)
        ret_frame.pack(fill=tk.X, padx=10, pady=2)
        self.retention_var = tk.BooleanVar(value=self.app.settings_mgr.get("retention_enabled", False))
        ttk.Checkbutton(ret_frame, text=i.t("lbl_retention_enabled"),
                         variable=self.retention_var).pack(side=tk.LEFT)

        days_frame = ttk.Frame(main)
        days_frame.pack(fill=tk.X, padx=10, pady=2)
        ttk.Label(days_frame, text=i.t("lbl_retention_days")).pack(side=tk.LEFT)
        self.retention_days_var = tk.IntVar(value=self.app.settings_mgr.get("retention_max_age_days", 30))
        ttk.Spinbox(days_frame, from_=1, to=365, textvariable=self.retention_days_var,
                     width=6).pack(side=tk.LEFT, padx=5)

        ret_folders_frame = ttk.Frame(main)
        ret_folders_frame.pack(fill=tk.X, padx=10, pady=2)
        ttk.Label(ret_folders_frame, text=i.t("lbl_retention_folders")).pack(side=tk.LEFT)
        self.retention_folders_var = tk.StringVar(value=", ".join(self.app.settings_mgr.get("retention_folders", [])))
        ttk.Entry(ret_folders_frame, textvariable=self.retention_folders_var, width=50).pack(side=tk.LEFT, padx=5)

        # --- Cloud Sync ---
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(main, text=i.t("lbl_cloud_sync"), font=("", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)

        cloud_frame = ttk.Frame(main)
        cloud_frame.pack(fill=tk.X, padx=10, pady=2)
        ttk.Label(cloud_frame, text=i.t("msg_cloud_folder")).pack(side=tk.LEFT)
        self.cloud_var = tk.StringVar(value=self.app.settings_mgr.get("cloud_path", ""))
        ttk.Entry(cloud_frame, textvariable=self.cloud_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(cloud_frame, text=i.t("btn_browse"), command=self._browse_cloud).pack(side=tk.LEFT)

        ttk.Label(main, text=i.t("msg_cloud_cats")).pack(anchor=tk.W, padx=10, pady=(5, 0))
        self.cloud_cats_var = tk.StringVar(
            value=", ".join(self.app.settings_mgr.get("cloud_categories", []))
        )
        ttk.Entry(main, textvariable=self.cloud_cats_var, width=60).pack(anchor=tk.W, padx=10)

        # --- Cloud API ---
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(main, text=i.t("lbl_cloud_api"), font=("", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)

        for provider in ["Google Drive", "OneDrive", "Dropbox"]:
            p_frame = ttk.Frame(main)
            p_frame.pack(fill=tk.X, padx=10, pady=2)
            ttk.Label(p_frame, text=provider + ":", width=14).pack(side=tk.LEFT)
            status = "Not connected"
            ttk.Label(p_frame, text=status, foreground="gray").pack(side=tk.LEFT, padx=5)
            ttk.Button(p_frame, text=i.t("lbl_connect"), state=tk.DISABLED).pack(side=tk.LEFT, padx=4)

        # --- Ignore List ---
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(main, text=i.t("lbl_ignore_list"), font=("", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)

        self.ignore_text = tk.Text(main, height=6, width=70, font=("Consolas", 9))
        self.ignore_text.pack(anchor=tk.W, padx=10)
        self._load_ignore()

        ttk.Button(main, text=i.t("btn_save_ignore"), command=self._save_ignore).pack(
            anchor=tk.W, padx=10, pady=2
        )

        # --- Profiles ---
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(main, text=i.t("lbl_profiles"), font=("", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)

        prof_frame = ttk.Frame(main)
        prof_frame.pack(fill=tk.X, padx=10, pady=2)
        ttk.Button(prof_frame, text=i.t("btn_export_profile"), command=self._export_profile).pack(side=tk.LEFT, padx=2)
        ttk.Button(prof_frame, text=i.t("btn_import_profile"), command=self._import_profile).pack(side=tk.LEFT, padx=2)
        ttk.Button(prof_frame, text=i.t("btn_delete_profile"), command=self._delete_profile).pack(side=tk.LEFT, padx=2)

        profiles = self.app.profile_mgr.list_profiles()
        self.profile_list_var = tk.StringVar(value=", ".join(p["name"] for p in profiles) or i.t("lbl_no_profiles"))
        ttk.Label(main, textvariable=self.profile_list_var, foreground="gray").pack(anchor=tk.W, padx=10)

        # --- Backup / Restore ---
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(main, text=i.t("lbl_backup_restore"), font=("", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)

        ttk.Label(main, text=i.t("lbl_backup_desc"), foreground="gray").pack(anchor=tk.W, padx=10)
        backup_frame = ttk.Frame(main)
        backup_frame.pack(fill=tk.X, padx=10, pady=2)
        ttk.Button(backup_frame, text=i.t("lbl_backup"), command=self._backup).pack(side=tk.LEFT, padx=4)
        ttk.Button(backup_frame, text=i.t("lbl_restore"), command=self._restore).pack(side=tk.LEFT, padx=4)

        # --- Plugins ---
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(main, text=i.t("lbl_plugins"), font=("", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)

        plugins = self.app.plugin_loader.get_plugins_info()
        if plugins:
            for p in plugins:
                ttk.Label(main, text=f"  {p['name']} v{p['version']}: {p['description']}").pack(
                    anchor=tk.W, padx=10
                )
        else:
            ttk.Label(main, text="  " + i.t("lbl_no_plugins"),
                      foreground="gray").pack(anchor=tk.W, padx=10)

        # --- Scheduled Cleanup ---
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(main, text=i.t("lbl_cleanup_schedule"), font=("", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)

        sched_frame = ttk.Frame(main)
        sched_frame.pack(fill=tk.X, padx=10, pady=2)
        self.cleanup_var = tk.BooleanVar(value=self.app.settings_mgr.get("scheduled_cleanup_enabled", False))
        ttk.Checkbutton(sched_frame, text=i.t("lbl_cleanup_schedule"),
                         variable=self.cleanup_var).pack(side=tk.LEFT)

        day_frame = ttk.Frame(main)
        day_frame.pack(fill=tk.X, padx=10, pady=2)
        ttk.Label(day_frame, text=i.t("lbl_cleanup_day")).pack(side=tk.LEFT)
        self.cleanup_day_var = tk.StringVar(value=self.app.settings_mgr.get("scheduled_cleanup_day", "monday"))
        ttk.Combobox(day_frame, textvariable=self.cleanup_day_var,
                      values=["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
                      state="readonly", width=12).pack(side=tk.LEFT, padx=5)

        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(main, text=i.t("btn_save"), command=self._save_all).pack(
            anchor=tk.W, padx=10, pady=10
        )

    def _browse_path(self):
        path = filedialog.askdirectory(title="Select downloads folder")
        if path:
            self.path_var.set(path)

    def _browse_cloud(self):
        path = filedialog.askdirectory(title="Select cloud folder")
        if path:
            self.cloud_var.set(path)

    def _load_ignore(self):
        self.ignore_text.delete("1.0", tk.END)
        for pattern in self.app.ignore_list.get_all():
            self.ignore_text.insert(tk.END, pattern + "\n")

    def _save_ignore(self):
        raw = self.ignore_text.get("1.0", tk.END).strip()
        patterns = [l.strip() for l in raw.split("\n") if l.strip()]
        self.app.ignore_list.patterns = patterns
        self.app.ignore_list.save()

    def _export_profile(self):
        name = simpledialog.askstring("Export Profile", "Profile name:")
        if not name:
            return
        self.app.profile_mgr.save_profile(
            name,
            self.app.rules_mgr.export_data(),
            self.app.ignore_list.get_all(),
            self.app.settings_mgr.settings,
        )
        messagebox.showinfo("Export", f"Profile '{name}' exported")

    def _import_profile(self):
        name = simpledialog.askstring("Import Profile", "Profile name:")
        if not name:
            return
        profile = self.app.profile_mgr.load_profile(name)
        if not profile:
            messagebox.showerror("Error", f"Profile '{name}' not found")
            return
        if "rules" in profile:
            self.app.rules_mgr.import_data(profile["rules"])
        if "ignore_list" in profile:
            self.app.ignore_list.patterns = profile["ignore_list"]
            self.app.ignore_list.save()
        self._load_ignore()
        messagebox.showinfo("Import", f"Profile '{name}' imported")

    def _delete_profile(self):
        name = simpledialog.askstring("Delete Profile", "Profile name:")
        if name and messagebox.askyesno("Delete", f"Delete profile '{name}'?"):
            self.app.profile_mgr.delete_profile(name)

    def _backup(self):
        result = create_backup_dialog(self.app.root)
        if result:
            messagebox.showinfo("Backup", f"Backup created: {result}")

    def _restore(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Select backup file",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )
        if path:
            result = restore_backup(path)
            if result.get("success"):
                messagebox.showinfo("Restore", f"Restored {result.get('restored', 0)} files")
            else:
                messagebox.showerror("Error", result.get("error", "Unknown error"))

    def _save_all(self):
        self.app.settings_mgr.set("downloads_path", self.path_var.get())
        self.app.settings_mgr.set("cloud_path", self.cloud_var.get())
        self.app.settings_mgr.set("sort_by_date", self.date_sort_var.get())
        self.app.settings_mgr.set("launch_on_startup", self.startup_var.get())
        self.app.settings_mgr.set("language", self.lang_var.get())
        self.app.settings_mgr.set("theme", self.theme_var.get())
        self.app.settings_mgr.set("portable_mode", self.portable_var.get())
        self.app.settings_mgr.set("content_detection_enabled", self.content_det_var.get())
        self.app.settings_mgr.set("notifications_enabled", self.notif_var.get())
        self.app.settings_mgr.set("notify_on_sort", self.notif_var.get())
        self.app.settings_mgr.set("watcher_enabled", self.watcher_var.get())
        self.app.settings_mgr.set("retention_enabled", self.retention_var.get())
        self.app.settings_mgr.set("retention_max_age_days", self.retention_days_var.get())
        self.app.settings_mgr.set("scheduled_cleanup_enabled", self.cleanup_var.get())
        self.app.settings_mgr.set("scheduled_cleanup_day", self.cleanup_day_var.get())

        folders = [f.strip() for f in self.folders_var.get().split(",") if f.strip()]
        self.app.settings_mgr.set("monitored_folders", folders)

        cats = [c.strip() for c in self.cloud_cats_var.get().split(",") if c.strip()]
        self.app.settings_mgr.set("cloud_categories", cats)

        ret_folders = [f.strip() for f in self.retention_folders_var.get().split(",") if f.strip()]
        self.app.settings_mgr.set("retention_folders", ret_folders)

        self._save_ignore()
        self.app.engine.downloads_path = self.path_var.get()
        self.app.engine.sort_by_date = self.date_sort_var.get()
        self.app.engine.content_detection = self.content_det_var.get()
        self.app.engine.monitored_folders = folders
        self.app.notification_mgr.update_settings(self.app.settings_mgr.settings)
        self.app.retention_mgr.update_settings(self.app.settings_mgr.settings)
        self.app.cleanup_scheduler.update_settings(self.app.settings_mgr.settings)

        try:
            self.app.apply_language(self.lang_var.get())
        except Exception:
            pass

        try:
            theme = self.theme_var.get()
            if theme in ("dark", "light"):
                self.app.apply_theme_to_all(theme)
        except Exception:
            pass

        try:
            if self.watcher_var.get():
                self.app._start_watcher()
            else:
                self.app._stop_watcher()
        except Exception:
            pass

        try:
            if self.cleanup_var.get():
                self.app.cleanup_scheduler.start()
            else:
                self.app.cleanup_scheduler.stop()
        except Exception:
            pass

        try:
            from core.portable import enable_portable_mode, disable_portable_mode
            if self.portable_var.get():
                enable_portable_mode()
            else:
                disable_portable_mode()
        except Exception:
            pass

        try:
            from core.autostart import set_startup
            set_startup(self.startup_var.get())
        except Exception:
            pass

        messagebox.showinfo("Settings", self.app.i18n.t("msg_settings_saved"))


def create_backup_dialog(parent):
    from tkinter import filedialog
    path = filedialog.asksaveasfilename(
        title="Save backup",
        defaultextension=".zip",
        filetypes=[("ZIP files", "*.zip")],
        initialfile="backup.zip"
    )
    if path:
        result = create_backup(path)
        if result.get("success"):
            return result.get("path")
        else:
            messagebox.showerror("Backup Error", result.get("error", "Unknown"))
    return None


def restore_backup(path):
    from core.backup import restore_backup as do_restore
    return do_restore(path)


from core.backup import create_backup
