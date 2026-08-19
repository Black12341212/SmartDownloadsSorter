#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Загрузчик пользовательских плагинов"""

import importlib.util
import os
from pathlib import Path

PLUGINS_DIR = str(Path(__file__).parent.parent / "plugins")


class BasePlugin:
    name = "BasePlugin"
    description = "Base plugin class"
    version = "1.0"

    def on_file_matched(self, filename, filepath, category, rule):
        return {"filename": filename, "category": category, "metadata": {}}

    def on_sort_complete(self, results):
        pass


class PluginLoader:
    def __init__(self, plugins_dir=None):
        self.plugins_dir = plugins_dir or PLUGINS_DIR
        self.plugins = []
        self.enabled = {}

    def discover(self):
        self.plugins = []
        if not os.path.exists(self.plugins_dir):
            return
        for fname in os.listdir(self.plugins_dir):
            if fname.startswith("_") or not fname.endswith(".py"):
                continue
            path = os.path.join(self.plugins_dir, fname)
            try:
                spec = importlib.util.spec_from_file_location(fname[:-3], path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and
                            issubclass(attr, BasePlugin) and
                            attr is not BasePlugin):
                        instance = attr()
                        self.plugins.append(instance)
            except Exception:
                pass

    def set_enabled(self, plugin_name, enabled):
        self.enabled[plugin_name] = enabled

    def is_enabled(self, plugin_name):
        return self.enabled.get(plugin_name, True)

    def run_on_match(self, filename, filepath, category, rule):
        result = {"filename": filename, "category": category, "metadata": {}}
        for plugin in self.plugins:
            if not self.is_enabled(plugin.name):
                continue
            try:
                modified = plugin.on_file_matched(filename, filepath, category, rule)
                if modified:
                    result["filename"] = modified.get("filename", result["filename"])
                    result["category"] = modified.get("category", result["category"])
                    result["metadata"].update(modified.get("metadata", {}))
            except Exception:
                pass
        return result

    def run_on_complete(self, results):
        for plugin in self.plugins:
            if not self.is_enabled(plugin.name):
                continue
            try:
                plugin.on_sort_complete(results)
            except Exception:
                pass

    def get_plugins_info(self):
        return [
            {"name": p.name, "description": p.description, "version": p.version}
            for p in self.plugins
        ]
