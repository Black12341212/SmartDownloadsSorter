#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Filesystem Watcher: real-time file monitoring and sorting (Feature #1)"""

import os
import time
import threading
import logging

logger = logging.getLogger("SmartSorter")


class FileWatcher:
    """Simple polling-based filesystem watcher.
    Uses watchdog if available, otherwise falls back to polling.
    """

    def __init__(self, sort_callback, interval_seconds=5):
        self.sort_callback = sort_callback
        self.interval_seconds = interval_seconds
        self._running = False
        self._thread = None
        self._watched_dirs = set()
        self._known_files = {}
        self._lock = threading.Lock()
        self._observer = None

    def add_directory(self, path):
        if os.path.isdir(path):
            with self._lock:
                self._watched_dirs.add(path)
                self._known_files[path] = self._scan_dir(path)

    def remove_directory(self, path):
        with self._lock:
            self._watched_dirs.discard(path)
            self._known_files.pop(path, None)

    def get_directories(self):
        with self._lock:
            return list(self._watched_dirs)

    def start(self):
        if self._running:
            return
        self._running = True
        try:
            self._start_watchdog()
        except Exception:
            logger.info("Watchdog not available, using polling watcher")
            self._start_polling()

    def _start_watchdog(self):
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        class Handler(FileSystemEventHandler):
            def __init__(self, watcher_ref):
                self.watcher = watcher_ref

            def on_created(self, event):
                if not event.is_directory:
                    self.watcher._on_file_event(event.src_path)

            def on_modified(self, event):
                if not event.is_directory:
                    self.watcher._on_file_event(event.src_path)

        self._observer = Observer()
        handler = Handler(self)
        with self._lock:
            for d in self._watched_dirs:
                try:
                    self._observer.schedule(handler, d, recursive=False)
                except Exception as e:
                    logger.warning(f"Cannot watch {d}: {e}")
        self._observer.start()
        logger.info("Watchdog observer started")

    def _start_polling(self):
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def _poll_loop(self):
        while self._running:
            time.sleep(self.interval_seconds)
            with self._lock:
                dirs_to_check = list(self._watched_dirs)
            for d in dirs_to_check:
                try:
                    current_files = self._scan_dir(d)
                    old_files = self._known_files.get(d, {})
                    new_files = set(current_files.keys()) - set(old_files.keys())
                    if new_files:
                        logger.info(f"Detected {len(new_files)} new file(s) in {d}")
                        self._known_files[d] = current_files
                        for fname in new_files:
                            self._on_file_event(os.path.join(d, fname))
                    self._known_files[d] = current_files
                except Exception as e:
                    logger.error(f"Polling error for {d}: {e}")

    def _scan_dir(self, path):
        files = {}
        try:
            for f in os.listdir(path):
                fp = os.path.join(path, f)
                if os.path.isfile(fp):
                    files[f] = os.path.getmtime(fp)
        except OSError:
            pass
        return files

    def _on_file_event(self, filepath):
        try:
            time.sleep(0.5)
            if os.path.exists(filepath) and os.path.isfile(filepath):
                self.sort_callback(target_path=os.path.dirname(filepath))
        except Exception as e:
            logger.error(f"Watcher event error: {e}")

    def stop(self):
        self._running = False
        if self._observer:
            try:
                self._observer.stop()
                self._observer.join(timeout=3)
            except Exception:
                pass
            self._observer = None
        if self._thread:
            self._thread = None
        logger.info("FileWatcher stopped")

    @property
    def is_running(self):
        return self._running
