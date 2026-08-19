#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Загрузка, сохранение и CRUD правил сортировки
v3.0: Added nested/conditional rules support
"""

import copy
import json
import os
from pathlib import Path

CONFIG_DIR = str(Path(__file__).parent.parent / "config")
RULES_FILE = os.path.join(CONFIG_DIR, "rules.json")

DEFAULT_RULES = {
    "Images": {
        "folder": "Images",
        "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".raw"],
        "name_contains": [],
        "regex": []
    },
    "Videos": {
        "folder": "Videos",
        "extensions": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".ts"],
        "name_contains": [],
        "regex": []
    },
    "Documents": {
        "folder": "Documents",
        "extensions": [".doc", ".docx", ".txt", ".odt", ".rtf", ".pages"],
        "name_contains": [],
        "regex": []
    },
    "Spreadsheets": {
        "folder": "Documents/Spreadsheets",
        "extensions": [".xls", ".xlsx", ".csv", ".ods", ".numbers"],
        "name_contains": [],
        "regex": []
    },
    "Presentations": {
        "folder": "Documents/Presentations",
        "extensions": [".ppt", ".pptx", ".odp", ".key"],
        "name_contains": [],
        "regex": []
    },
    "PDF_Books": {
        "folder": "PDF/Books",
        "extensions": [".pdf"],
        "name_contains": ["book", "книга", "учебник", "tutorial", "guide", "manual"],
        "regex": ["(?i)(book|guide|tutorial|manual|учебник)"],
        "size_min_mb": 5
    },
    "PDF_Articles": {
        "folder": "PDF/Articles",
        "extensions": [".pdf"],
        "name_contains": ["article", "статья", "paper", "journal"],
        "regex": ["(?i)(article|paper|journal|статья)"],
        "size_max_mb": 5
    },
    "PDF_Scans": {
        "folder": "PDF/Scans",
        "extensions": [".pdf"],
        "name_contains": ["scan", "скан", "copy", "копия"],
        "regex": ["(?i)(scan|скан|copy)"]
    },
    "PDF_Forms": {
        "folder": "PDF/Forms",
        "extensions": [".pdf"],
        "name_contains": ["form", "форма", "заявление", "договор", "contract", "invoice", "receipt"],
        "regex": ["(?i)(form|заявка|заявление|договор|contract|invoice|receipt|счет)"]
    },
    "PDF_Other": {
        "folder": "PDF/Other",
        "extensions": [".pdf"],
        "name_contains": [],
        "regex": [],
        "is_default_pdf": True
    },
    "Archives": {
        "folder": "Archives",
        "extensions": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
        "name_contains": [],
        "regex": []
    },
    "Audio": {
        "folder": "Audio",
        "extensions": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus"],
        "name_contains": [],
        "regex": []
    },
    "Programs": {
        "folder": "Programs",
        "extensions": [".exe", ".msi", ".app", ".dmg", ".deb", ".rpm", ".apk"],
        "name_contains": [],
        "regex": []
    },
    "Code": {
        "folder": "Code",
        "extensions": [".py", ".js", ".html", ".css", ".cpp", ".java", ".c", ".h", ".php", ".sql", ".json", ".xml", ".yaml", ".yml", ".ts", ".jsx", ".tsx", ".go", ".rs", ".rb"],
        "name_contains": [],
        "regex": []
    },
    "Fonts": {
        "folder": "Fonts",
        "extensions": [".ttf", ".otf", ".woff", ".woff2", ".eot"],
        "name_contains": [],
        "regex": []
    },
    "Models3D": {
        "folder": "Models3D",
        "extensions": [".stl", ".obj", ".fbx", ".blend", ".3ds", ".dae", ".glb", ".gltf"],
        "name_contains": [],
        "regex": []
    },
    "Subtitles": {
        "folder": "Subtitles",
        "extensions": [".srt", ".sub", ".ass", ".vtt", ".ssa"],
        "name_contains": [],
        "regex": []
    },
    "ISO_DiscImages": {
        "folder": "ISO",
        "extensions": [".iso", ".img", ".vmdk", ".vhd", ".vhdx", ".bin", ".cue", ".nrg"],
        "name_contains": [],
        "regex": []
    }
}


class RulesManager:
    def __init__(self, rules_file=None):
        self.rules_file = rules_file or RULES_FILE
        self.rules = {}
        self.load()

    def load(self):
        os.makedirs(os.path.dirname(self.rules_file), exist_ok=True)
        try:
            if os.path.exists(self.rules_file):
                with open(self.rules_file, "r", encoding="utf-8") as f:
                    data = f.read().strip()
                    if data:
                        self.rules = json.loads(data)
                    else:
                        self.rules = copy.deepcopy(DEFAULT_RULES)
                        self.save()
            else:
                self.rules = copy.deepcopy(DEFAULT_RULES)
                self.save()
        except (json.JSONDecodeError, Exception):
            self.rules = copy.deepcopy(DEFAULT_RULES)

    def save(self):
        os.makedirs(os.path.dirname(self.rules_file), exist_ok=True)
        with open(self.rules_file, "w", encoding="utf-8") as f:
            json.dump(self.rules, f, indent=4, ensure_ascii=False)

    def add(self, category, rule):
        self.rules[category] = rule
        self.save()

    def remove(self, category):
        if category in self.rules:
            del self.rules[category]
            self.save()
            return True
        return False

    def update(self, category, rule):
        self.rules[category] = rule
        self.save()

    def reset(self):
        self.rules = copy.deepcopy(DEFAULT_RULES)
        self.save()

    def get(self, category):
        return self.rules.get(category)

    def all(self):
        return self.rules

    def categories(self):
        return list(self.rules.keys())

    def export_data(self):
        return dict(self.rules)

    def import_data(self, data):
        self.rules = copy.deepcopy(data)
        self.save()

    def add_nested_rule(self, category, folder, conditions, extensions=None):
        rule = {
            "folder": folder,
            "extensions": extensions or [],
            "name_contains": [],
            "regex": [],
            "conditions": conditions,
        }
        self.add(category, rule)

    def set_conditions(self, category, logic="AND", condition_list=None):
        rule = self.get(category)
        if not rule:
            return False
        rule["conditions"] = {
            "logic": logic,
            "rules": condition_list or [],
        }
        self.update(category, rule)
        return True

    def remove_conditions(self, category):
        rule = self.get(category)
        if not rule:
            return False
        rule.pop("conditions", None)
        self.update(category, rule)
        return True
