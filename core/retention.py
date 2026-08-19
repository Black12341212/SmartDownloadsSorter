#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auto-cleanup / Retention Policy (Feature #5)"""

import os
import time
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("SmartSorter")


class RetentionManager:
    def __init__(self, settings=None):
        self.settings = settings or {}
        self.enabled = self.settings.get("retention_enabled", False)
        self.max_age_days = self.settings.get("retention_max_age_days", 30)
        self.target_folders = self.settings.get("retention_folders", [])
        self.file_extensions = self.settings.get("retention_extensions", [".exe", ".msi", ".iso", ".zip", ".rar", ".7z"])

    def update_settings(self, settings):
        self.settings = settings
        self.enabled = self.settings.get("retention_enabled", False)
        self.max_age_days = self.settings.get("retention_max_age_days", 30)
        self.target_folders = self.settings.get("retention_folders", [])

    def scan_old_files(self, base_path):
        if not self.enabled:
            return []
        old_files = []
        cutoff = time.time() - (self.max_age_days * 86400)
        folders = self.target_folders or [base_path]

        for folder_name in folders:
            folder_path = os.path.join(base_path, folder_name)
            if not os.path.isdir(folder_path):
                continue
            for fname in os.listdir(folder_path):
                fpath = os.path.join(folder_path, fname)
                if not os.path.isfile(fpath):
                    continue
                if self.file_extensions:
                    ext = os.path.splitext(fname)[1].lower()
                    if ext not in self.file_extensions:
                        continue
                try:
                    mtime = os.path.getmtime(fpath)
                    if mtime < cutoff:
                        age_days = int((time.time() - mtime) / 86400)
                        size_mb = os.path.getsize(fpath) / (1024 * 1024)
                        old_files.append({
                            "path": fpath,
                            "name": fname,
                            "age_days": age_days,
                            "size_mb": round(size_mb, 2),
                            "folder": folder_name,
                            "mtime": datetime.fromtimestamp(mtime).isoformat(),
                        })
                except OSError:
                    continue

        old_files.sort(key=lambda x: x["age_days"], reverse=True)
        return old_files

    def cleanup(self, base_path, dry_run=False):
        old_files = self.scan_old_files(base_path)
        deleted = []
        freed_bytes = 0

        for item in old_files:
            fpath = item["path"]
            try:
                size = os.path.getsize(fpath)
                if not dry_run:
                    os.remove(fpath)
                deleted.append(item)
                freed_bytes += size
                logger.info(f"{'[DRY RUN] Would delete' if dry_run else 'Deleted'}: {fpath} ({item['age_days']}d old)")
            except OSError as e:
                logger.error(f"Failed to delete {fpath}: {e}")

        return {
            "deleted_count": len(deleted),
            "freed_mb": round(freed_bytes / (1024 * 1024), 2),
            "files": deleted,
            "dry_run": dry_run,
        }

    def get_summary(self, base_path):
        old_files = self.scan_old_files(base_path)
        total_size = sum(f["size_mb"] for f in old_files)
        return {
            "count": len(old_files),
            "total_size_mb": round(total_size, 2),
            "files": old_files[:100],
        }
