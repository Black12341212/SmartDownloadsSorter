#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Расписание автосортировки + Scheduled Cleanup"""

import threading
import time
import logging

logger = logging.getLogger("SmartSorter")


class Scheduler:
    def __init__(self, sort_callback, log_callback=None):
        self.sort_callback = sort_callback
        self.log_callback = log_callback
        self.interval_minutes = 15
        self._running = False
        self._timer = None
        self._lock = threading.Lock()
        self._cleanup_callbacks = []

    def set_interval(self, minutes):
        self.interval_minutes = max(1, int(minutes))

    def start(self):
        with self._lock:
            if self._running:
                return
            self._running = True
        # Run the first cycle outside the lock so that stop() can cancel the
        # scheduler immediately instead of blocking until the (possibly long)
        # sort callback finishes.
        self._run_cycle()

    def stop(self):
        with self._lock:
            self._running = False
            if self._timer:
                self._timer.cancel()
                self._timer = None

    def _run_cycle(self):
        if not self._running:
            return
        try:
            self.sort_callback()
        except Exception as e:
            if self.log_callback:
                self.log_callback(f"Scheduler error: {e}")
            logger.error(f"Scheduler error: {e}")
        self._timer = threading.Timer(self.interval_minutes * 60, self._run_cycle)
        self._timer.daemon = True
        self._timer.start()

    def add_cleanup_callback(self, callback):
        self._cleanup_callbacks.append(callback)

    def run_cleanup(self):
        for cb in self._cleanup_callbacks:
            try:
                cb()
            except Exception as e:
                logger.error(f"Cleanup callback error: {e}")

    @property
    def is_running(self):
        return self._running


class CleanupScheduler:
    def __init__(self, cleanup_callback, settings=None):
        self.cleanup_callback = cleanup_callback
        self.settings = settings or {}
        self.enabled = self.settings.get("scheduled_cleanup_enabled", False)
        self.cleanup_day = self.settings.get("scheduled_cleanup_day", "monday")
        self._running = False
        self._thread = None

    def update_settings(self, settings):
        self.settings = settings
        self.enabled = self.settings.get("scheduled_cleanup_enabled", False)
        self.cleanup_day = self.settings.get("scheduled_cleanup_day", "monday")

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _loop(self):
        from datetime import datetime
        DAYS = {
            "monday": 0, "tuesday": 1, "wednesday": 2,
            "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
        }
        target_day = DAYS.get(self.cleanup_day.lower(), 0)
        last_run = None

        while self._running:
            time.sleep(60)
            if not self.enabled:
                continue
            now = datetime.now()
            if now.weekday() == target_day and now.hour == 3:
                today_key = now.strftime("%Y-%m-%d")
                if last_run != today_key:
                    try:
                        self.cleanup_callback()
                        last_run = today_key
                        logger.info("Scheduled cleanup executed")
                    except Exception as e:
                        logger.error(f"Scheduled cleanup error: {e}")

    @property
    def is_running(self):
        return self._running
