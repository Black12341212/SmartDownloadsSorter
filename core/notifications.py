#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Notification System (Feature #13)"""

import logging

logger = logging.getLogger("SmartSorter")


class NotificationManager:
    def __init__(self, settings=None):
        self.settings = settings or {}
        self.enabled = self.settings.get("notifications_enabled", True)
        self.show_on_sort = self.settings.get("notify_on_sort", True)
        self._gui_callback = None

    def set_gui_callback(self, callback):
        self._gui_callback = callback

    def update_settings(self, settings):
        self.settings = settings
        self.enabled = self.settings.get("notifications_enabled", True)
        self.show_on_sort = self.settings.get("notify_on_sort", True)

    def notify(self, title, message, level="info"):
        if not self.enabled:
            return
        logger.info(f"NOTIFICATION [{level}]: {title} - {message}")
        if self._gui_callback:
            try:
                self._gui_callback(title, message, level)
            except Exception:
                pass
        self._try_system_tray(title, message)

    def _try_system_tray(self, title, message):
        try:
            import win10toast
            toaster = win10toast.ToastNotifier()
            toaster.show_toast(title, message, duration=5, threaded=True)
        except ImportError:
            pass
        except Exception:
            pass

    def notify_sort_complete(self, result):
        if not self.show_on_sort:
            return
        moved = result.get("moved", 0)
        skipped = result.get("skipped", 0)
        errors = result.get("errors", 0)
        if moved > 0:
            msg = f"Moved: {moved} files"
            if skipped > 0:
                msg += f", Skipped: {skipped}"
            if errors > 0:
                msg += f", Errors: {errors}"
            self.notify("Sort Complete", msg, "info")
        elif errors > 0:
            self.notify("Sort Error", f"{errors} error(s) occurred", "error")

    def notify_watcher_event(self, folder, count):
        self.notify("New Files Detected", f"{count} new file(s) in {folder}", "info")

    def notify_cleanup(self, result):
        deleted = result.get("deleted_count", 0)
        if deleted > 0:
            freed = result.get("freed_mb", 0)
            self.notify("Cleanup Complete", f"Deleted {deleted} files, freed {freed} MB", "info")
