#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Движок сортировки файлов - v3.0
Supports: multi-folder, content detection, nested rules, error tracking
"""

import os
import shutil
import threading
from datetime import datetime

from core.rules_manager import RulesManager
from core.file_matcher import check_file_match, analyze_pdf, get_file_size_mb
from core.history import HistoryManager
from core.ignore_list import IgnoreList
from core.logger import log_move, log_error, log_sort_start, log_sort_end


class SorterEngine:
    def __init__(self, downloads_path, rules_manager=None, history_manager=None,
                 ignore_list=None, settings=None, plugin_loader=None):
        self.downloads_path = downloads_path
        self.rules = rules_manager or RulesManager()
        self.history = history_manager or HistoryManager()
        self.ignore = ignore_list or IgnoreList()
        self.settings = settings or {}
        self.plugins = plugin_loader
        self.sort_by_date = self.settings.get("sort_by_date", False)
        self.pdf_settings = self.settings.get("pdf_settings", {
            "enable_smart_pdf": True,
            "pdf_size_analysis": True,
        })
        self.content_detection = self.settings.get("content_detection_enabled", False)
        self.monitored_folders = self.settings.get("monitored_folders", [])
        self.error_count = 0
        self._lock = threading.Lock()

    def sort(self, dry_run=False, target_path=None, only_files=None):
        with self._lock:
            return self._sort_locked(dry_run, target_path, only_files)

    def _sort_locked(self, dry_run=False, target_path=None, only_files=None):
        scan_paths = []
        if target_path:
            scan_paths = [target_path]
        elif self.monitored_folders:
            for folder in self.monitored_folders:
                if os.path.isdir(folder):
                    scan_paths.append(folder)
                else:
                    full = os.path.join(self.downloads_path, folder)
                    if os.path.isdir(full):
                        scan_paths.append(full)
            if not scan_paths and os.path.isdir(self.downloads_path):
                scan_paths = [self.downloads_path]
        else:
            scan_paths = [self.downloads_path]

        total_moved = 0
        total_skipped = 0
        total_errors = 0
        all_moved_files = []
        self.error_count = 0

        for scan_path in scan_paths:
            result = self._sort_single(scan_path, dry_run, only_files)
            total_moved += result["moved"]
            total_skipped += result["skipped"]
            total_errors += result["errors"]
            all_moved_files.extend(result["files"])

        if self.plugins:
            self.plugins.run_on_complete(all_moved_files)

        return {
            "moved": total_moved,
            "skipped": total_skipped,
            "errors": total_errors,
            "files": all_moved_files,
            "session_time": datetime.now().isoformat(),
        }

    def _sort_single(self, scan_path, dry_run, only_files=None):
        if not os.path.exists(scan_path):
            return {"moved": 0, "skipped": 0, "errors": 0, "files": [], "error": f"Path not found: {scan_path}"}

        files = [f for f in os.listdir(scan_path)
                 if os.path.isfile(os.path.join(scan_path, f))]

        if only_files is not None:
            wanted = {os.path.basename(f) for f in only_files}
            files = [f for f in files if f in wanted]

        log_sort_start(scan_path, len(files))

        moved_count = 0
        skipped_count = 0
        error_count = 0
        moved_files = []

        for filename in files:
            if self.ignore.is_ignored(filename):
                skipped_count += 1
                continue

            source_path = os.path.join(scan_path, filename)
            moved = False
            errored = False

            real_ext = None
            if self.content_detection:
                try:
                    from core.content_detector import should_override_extension
                    should_override, new_ext = should_override_extension(source_path)
                    if should_override:
                        real_ext = new_ext
                except ImportError:
                    pass

            for category, rule in self.rules.all().items():
                if not rule.get("is_default_pdf") and check_file_match(filename, source_path, rule, real_ext=real_ext):
                    folder_name = rule.get("folder", category)
                    folder_name = self._apply_date_sort(folder_name, source_path)
                    dest_folder = os.path.join(scan_path, folder_name)

                    result = self._move_file(filename, source_path, dest_folder, category, dry_run)
                    if result["moved"]:
                        moved_count += 1
                        moved_files.append(result)
                        moved = True
                        break
                    elif result.get("error"):
                        errored = True
                        break

            if not moved and not errored and filename.lower().endswith(".pdf"):
                for category, rule in self.rules.all().items():
                    if rule.get("is_default_pdf"):
                        folder_name = rule.get("folder", category)
                        suggested_cat, _ = analyze_pdf(filename, source_path)
                        if suggested_cat and suggested_cat in self.rules.all():
                            folder_name = self.rules.get(suggested_cat).get("folder", suggested_cat)

                        folder_name = self._apply_date_sort(folder_name, source_path)
                        dest_folder = os.path.join(scan_path, folder_name)

                        result = self._move_file(filename, source_path, dest_folder, category, dry_run)
                        if result["moved"]:
                            moved_count += 1
                            moved_files.append(result)
                            moved = True
                        elif result.get("error"):
                            errored = True
                        break

            if errored:
                error_count += 1
            elif not moved:
                skipped_count += 1

        log_sort_end(moved_count, skipped_count, error_count)

        return {
            "moved": moved_count,
            "skipped": skipped_count,
            "errors": error_count,
            "files": moved_files,
        }

    def _apply_date_sort(self, folder_name, filepath):
        if self.sort_by_date:
            try:
                mtime = os.path.getmtime(filepath)
                dt = datetime.fromtimestamp(mtime)
                date_sub = dt.strftime("%Y-%m")
                folder_name = os.path.join(folder_name, date_sub)
            except Exception:
                pass
        return folder_name

    def _move_file(self, filename, source_path, dest_folder, category, dry_run):
        dest_path = os.path.join(dest_folder, filename)
        result = {
            "filename": filename,
            "source": source_path,
            "dest": dest_path,
            "category": category,
            "moved": False,
        }

        if dry_run:
            result["moved"] = True
            return result

        try:
            os.makedirs(dest_folder, exist_ok=True)

            if os.path.exists(dest_path):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(dest_path):
                    dest_path = os.path.join(dest_folder, f"{base}_{counter}{ext}")
                    counter += 1
                result["dest"] = dest_path

            if self.plugins:
                plugin_result = self.plugins.run_on_match(
                    filename, source_path, category, self.rules.get(category) or {}
                )
                if plugin_result:
                    result["metadata"] = plugin_result.get("metadata", {})

            shutil.move(source_path, dest_path)

            self.history.record(filename, source_path, dest_path, category)
            log_move(filename, source_path, dest_path, category)
            result["moved"] = True
        except Exception as e:
            log_error(filename, str(e))
            result["error"] = str(e)

        return result
