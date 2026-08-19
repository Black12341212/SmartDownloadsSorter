#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Undo: хранение истории перемещений и откат"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

CONFIG_DIR = str(Path(__file__).parent.parent / "config")
HISTORY_FILE = os.path.join(CONFIG_DIR, "history.json")
MAX_HISTORY = 1000


class HistoryManager:
    def __init__(self, history_file=None):
        self.history_file = history_file or HISTORY_FILE
        self.entries = []
        self.load()

    def load(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = f.read().strip()
                    self.entries = json.loads(data) if data else []
        except (json.JSONDecodeError, Exception):
            self.entries = []

    def save(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=4, ensure_ascii=False)

    def record(self, filename, source, dest, category=""):
        entry = {
            "filename": filename,
            "source": source,
            "dest": dest,
            "category": category,
            "timestamp": datetime.now().isoformat(),
        }
        self.entries.append(entry)
        if len(self.entries) > MAX_HISTORY:
            self.entries = self.entries[-MAX_HISTORY:]
        self.save()

    def undo_last(self, count=1):
        undone = []
        for _ in range(min(count, len(self.entries))):
            entry = self.entries.pop()
            src = entry["dest"]
            dst = entry["source"]
            if os.path.exists(src):
                try:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.move(src, dst)
                    undone.append(entry)
                    continue
                except Exception:
                    pass
            # Source file no longer exists or the move back failed:
            # keep the record in history so it is not silently lost.
            self.entries.append(entry)
        self.save()
        return undone

    def undo_session(self, session_timestamp):
        undone = []
        remaining = []
        for entry in self.entries:
            if entry["timestamp"] >= session_timestamp:
                src = entry["dest"]
                dst = entry["source"]
                if os.path.exists(src):
                    try:
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.move(src, dst)
                        undone.append(entry)
                    except Exception:
                        remaining.append(entry)
                else:
                    # Source file no longer exists; nothing to undo.
                    remaining.append(entry)
            else:
                remaining.append(entry)
        self.entries = remaining
        self.save()
        return undone

    def get_entries(self, limit=50):
        return list(reversed(self.entries[-limit:]))

    def clear(self):
        self.entries = []
        self.save()
