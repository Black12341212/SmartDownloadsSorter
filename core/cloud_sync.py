#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Интеграция с облачными хранилищами + Portable Mode support"""

import json
import os
import shutil
from pathlib import Path


def _get_config_dir():
    try:
        from core.portable import get_config_dir
        return get_config_dir()
    except ImportError:
        return str(Path(__file__).parent.parent / "config")


def _get_settings_file():
    return os.path.join(_get_config_dir(), "settings.json")


DEFAULT_SETTINGS = {
    "downloads_path": str(Path.home() / "Downloads"),
    "cloud_path": "",
    "cloud_categories": [],
    "auto_sort_interval": 15,
    "auto_sort_enabled": False,
    "sort_by_date": False,
    "launch_on_startup": False,
    "theme": "default",
    "language": "en",
    "monitored_folders": [],
    "content_detection_enabled": False,
    "notifications_enabled": True,
    "notify_on_sort": True,
    "retention_enabled": False,
    "retention_max_age_days": 30,
    "retention_folders": [],
    "retention_extensions": [".exe", ".msi", ".iso", ".zip", ".rar", ".7z"],
    "watcher_enabled": False,
    "watcher_interval": 5,
    "portable_mode": False,
    "cloud_api_enabled": False,
    "cloud_api_provider": "",
    "cloud_api_token": "",
    "scheduled_cleanup_enabled": False,
    "scheduled_cleanup_day": "monday",
    "scheduled_cleanup_folders": [],
    "pdf_settings": {
        "enable_smart_pdf": True,
        "pdf_size_analysis": True,
        "pdf_name_patterns": True,
    }
}


class SettingsManager:
    def __init__(self, settings_file=None):
        self.settings_file = settings_file or _get_settings_file()
        self.settings = dict(DEFAULT_SETTINGS)
        self.load()

    def load(self):
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = f.read().strip()
                    if data:
                        saved = json.loads(data)
                        self._deep_update(self.settings, saved)
        except (json.JSONDecodeError, Exception):
            pass

    def save(self):
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4, ensure_ascii=False)

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save()

    def _deep_update(self, base, override):
        for k, v in override.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict):
                self._deep_update(base[k], v)
            else:
                base[k] = v


def sync_to_cloud(source_path, cloud_path, categories_to_sync, moved_files):
    if not cloud_path or not os.path.exists(cloud_path):
        return []
    copied = []
    for item in moved_files:
        cat = item.get("category", "")
        if categories_to_sync and cat not in categories_to_sync:
            continue
        src = item["dest"]
        if not os.path.exists(src):
            continue
        rel = os.path.relpath(src, os.path.dirname(source_path))
        dst = os.path.join(cloud_path, rel)
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            copied.append(dst)
        except Exception:
            pass
    return copied
