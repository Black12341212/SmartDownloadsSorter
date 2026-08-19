#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Игнор-лист: правила исключений"""

import fnmatch
import json
import os
from pathlib import Path

CONFIG_DIR = str(Path(__file__).parent.parent / "config")
IGNORE_FILE = os.path.join(CONFIG_DIR, "ignore_list.json")

DEFAULT_IGNORE = [
    "Thumbs.db",
    "desktop.ini",
    ".DS_Store",
    "*.tmp",
    "~*",
    "*.crdownload",
    "*.part",
    "*.aria2",
]


class IgnoreList:
    def __init__(self, ignore_file=None):
        self.ignore_file = ignore_file or IGNORE_FILE
        self.patterns = []
        self.load()

    def load(self):
        os.makedirs(os.path.dirname(self.ignore_file), exist_ok=True)
        try:
            if os.path.exists(self.ignore_file):
                with open(self.ignore_file, "r", encoding="utf-8") as f:
                    data = f.read().strip()
                    self.patterns = json.loads(data) if data else list(DEFAULT_IGNORE)
                if not self.patterns:
                    self.patterns = list(DEFAULT_IGNORE)
            else:
                self.patterns = list(DEFAULT_IGNORE)
                self.save()
        except (json.JSONDecodeError, Exception):
            self.patterns = list(DEFAULT_IGNORE)

    def save(self):
        os.makedirs(os.path.dirname(self.ignore_file), exist_ok=True)
        with open(self.ignore_file, "w", encoding="utf-8") as f:
            json.dump(self.patterns, f, indent=4, ensure_ascii=False)

    def is_ignored(self, filename):
        for pattern in self.patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
            if fnmatch.fnmatch(filename.lower(), pattern.lower()):
                return True
        return False

    def add(self, pattern):
        if pattern not in self.patterns:
            self.patterns.append(pattern)
            self.save()

    def remove(self, pattern):
        if pattern in self.patterns:
            self.patterns.remove(pattern)
            self.save()

    def get_all(self):
        return list(self.patterns)
