#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Экспорт/импорт профилей правил"""

import json
import os
import re
from datetime import datetime

from core.portable import get_config_dir

PROFILES_DIR = os.path.join(get_config_dir(), "profiles")


def sanitize_profile_name(name):
    """Return a safe profile name that cannot escape the profiles directory.

    Strips path separators and other unsafe characters, clamps the length and
    guarantees a non-empty result.
    """
    if not name:
        return "profile"
    safe = re.sub(r'[^A-Za-z0-9_ \-]', '', str(name)).strip()
    safe = safe[:100].strip()
    return safe or "profile"


class ProfileManager:
    def __init__(self, profiles_dir=None):
        self.profiles_dir = profiles_dir or PROFILES_DIR
        os.makedirs(self.profiles_dir, exist_ok=True)

    def list_profiles(self):
        profiles = []
        for f in os.listdir(self.profiles_dir):
            if f.endswith(".json"):
                name = os.path.splitext(f)[0]
                path = os.path.join(self.profiles_dir, f)
                mtime = os.path.getmtime(path)
                profiles.append({
                    "name": name,
                    "path": path,
                    "modified": datetime.fromtimestamp(mtime).isoformat(),
                })
        return profiles

    def save_profile(self, name, rules_data, ignore_data=None, settings_data=None):
        name = sanitize_profile_name(name)
        profile = {
            "name": name,
            "created": datetime.now().isoformat(),
            "rules": rules_data,
            "ignore_list": ignore_data,
            "settings": settings_data,
        }
        path = os.path.join(self.profiles_dir, f"{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=4, ensure_ascii=False)
        return path

    def load_profile(self, name):
        name = sanitize_profile_name(name)
        path = os.path.join(self.profiles_dir, f"{name}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def delete_profile(self, name):
        name = sanitize_profile_name(name)
        path = os.path.join(self.profiles_dir, f"{name}.json")
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def rename_profile(self, old_name, new_name):
        old_name = sanitize_profile_name(old_name)
        new_name = sanitize_profile_name(new_name)
        old_path = os.path.join(self.profiles_dir, f"{old_name}.json")
        new_path = os.path.join(self.profiles_dir, f"{new_name}.json")
        if os.path.exists(old_path) and not os.path.exists(new_path):
            os.rename(old_path, new_path)
            return True
        return False
