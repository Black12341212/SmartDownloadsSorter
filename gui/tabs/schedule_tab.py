#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Вкладка: Расписание автосортировки v3.0
With Scheduled Cleanup support
"""

import tkinter as tk
from tkinter import ttk


class ScheduleTab:
    TAB_TITLE = "  Schedule  "

    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.Frame(parent)
        self._build()

    def _build(self):
        main = ttk.Frame(self.frame, padding=20)
        main.pack(fill=tk.BOTH, expand=True)

        i = self.app.i18n

        ttk.Label(main, text=i.t("lbl_auto_sort_scheduler"), font=("", 14, "bold")).pack(pady=(0, 20))

        opt_frame = ttk.Frame(main)
        opt_frame.pack(fill=tk.X, pady=5)

        self.enabled_var = tk.BooleanVar(
            value=self.app.settings_mgr.get("auto_sort_enabled", False)
        )
        ttk.Checkbutton(opt_frame, text=i.t("lbl_auto_sort"),
                         variable=self.enabled_var).pack(side=tk.LEFT)

        int_frame = ttk.Frame(main)
        int_frame.pack(fill=tk.X, pady=5)

        ttk.Label(int_frame, text=i.t("lbl_interval")).pack(side=tk.LEFT)
        self.interval_var = tk.IntVar(
            value=self.app.settings_mgr.get("auto_sort_interval", 15)
        )
        self.interval_scale = ttk.Scale(int_frame, from_=1, to=60,
                                         variable=self.interval_var, orient=tk.HORIZONTAL,
                                         length=300)
        self.interval_scale.pack(side=tk.LEFT, padx=10)
        self.interval_label = ttk.Label(int_frame, textvariable=self.interval_var, width=4)
        self.interval_label.pack(side=tk.LEFT)

        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=20)

        self.start_btn = ttk.Button(btn_frame, text=i.t("btn_start"), command=self._start)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(btn_frame, text=i.t("btn_stop"), command=self._stop)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.status_var = tk.StringVar(value=i.t("lbl_status_stopped"))
        ttk.Label(btn_frame, textvariable=self.status_var, font=("", 10)).pack(
            side=tk.LEFT, padx=20
        )

        info = ttk.Label(main, text=i.t("lbl_scheduler_info"), foreground="gray")
        info.pack(pady=10)

        if self.enabled_var.get():
            self.status_var.set(i.t("lbl_status_running"))

        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        ttk.Label(main, text=i.t("lbl_cleanup_schedule"), font=("", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))

        cleanup_frame = ttk.Frame(main)
        cleanup_frame.pack(fill=tk.X, pady=5)

        self.cleanup_enabled_var = tk.BooleanVar(
            value=self.app.settings_mgr.get("scheduled_cleanup_enabled", False)
        )
        ttk.Checkbutton(cleanup_frame, text=i.t("lbl_cleanup_schedule"),
                         variable=self.cleanup_enabled_var).pack(side=tk.LEFT)

        day_frame = ttk.Frame(main)
        day_frame.pack(fill=tk.X, pady=5)
        ttk.Label(day_frame, text=i.t("lbl_cleanup_day")).pack(side=tk.LEFT)
        self.cleanup_day_var = tk.StringVar(
            value=self.app.settings_mgr.get("scheduled_cleanup_day", "monday")
        )
        ttk.Combobox(day_frame, textvariable=self.cleanup_day_var,
                      values=["monday", "tuesday", "wednesday", "thursday",
                              "friday", "saturday", "sunday"],
                      state="readonly", width=12).pack(side=tk.LEFT, padx=5)

        cleanup_btn_frame = ttk.Frame(main)
        cleanup_btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(cleanup_btn_frame, text=i.t("btn_start") + " Cleanup",
                    command=self._start_cleanup).pack(side=tk.LEFT, padx=5)
        ttk.Button(cleanup_btn_frame, text=i.t("btn_stop") + " Cleanup",
                    command=self._stop_cleanup).pack(side=tk.LEFT, padx=5)

        self.cleanup_status_var = tk.StringVar(value=i.t("lbl_status_stopped"))
        ttk.Label(cleanup_btn_frame, textvariable=self.cleanup_status_var).pack(side=tk.LEFT, padx=10)

    def _start(self):
        interval = self.interval_var.get()
        self.app.settings_mgr.set("auto_sort_interval", interval)
        self.app.settings_mgr.set("auto_sort_enabled", True)
        self.app.scheduler.set_interval(interval)
        self.app.scheduler.start()
        self.status_var.set(f"{self.app.i18n.t('lbl_status_running')} (every {interval} min)")

    def _stop(self):
        self.app.scheduler.stop()
        self.app.settings_mgr.set("auto_sort_enabled", False)
        self.status_var.set(self.app.i18n.t("lbl_status_stopped"))

    def _start_cleanup(self):
        self.app.settings_mgr.set("scheduled_cleanup_enabled", True)
        self.app.settings_mgr.set("scheduled_cleanup_day", self.cleanup_day_var.get())
        self.app.cleanup_scheduler.update_settings(self.app.settings_mgr.settings)
        self.app.cleanup_scheduler.start()
        self.cleanup_status_var.set(self.app.i18n.t("lbl_status_running"))

    def _stop_cleanup(self):
        self.app.cleanup_scheduler.stop()
        self.app.settings_mgr.set("scheduled_cleanup_enabled", False)
        self.cleanup_status_var.set(self.app.i18n.t("lbl_status_stopped"))
