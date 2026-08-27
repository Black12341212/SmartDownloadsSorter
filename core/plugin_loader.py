#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Загрузчик пользовательских плагинов"""

import importlib.util
import logging
import os
from pathlib import Path

logger = logging.getLogger("SmartSorter")

PLUGINS_DIR = str(Path(__file__).parent.parent / "plugins")


class BasePlugin:
    name = "BasePlugin"
    description = "Base plugin class"
    version = "1.0"
    tab_title = None

    def __init__(self):
        self._log_callback = None

    def set_log_callback(self, callback):
        self._log_callback = callback

    def log(self, message):
        """Emit a plugin message.

        Routed through the registered GUI/log callback when available so the
        output is visible in the application log instead of stdout.
        """
        if self._log_callback:
            try:
                self._log_callback(message)
                return
            except Exception:
                pass
        logger.info(f"[{self.name}] {message}")

    def on_file_matched(self, filename, filepath, category, rule):
        return {"filename": filename, "category": category, "metadata": {}}

    def on_sort_complete(self, results):
        pass

    def get_gui_tab(self, parent, app):
        """Return a tkinter widget to add as a tab, or None for no tab."""
        return None

    def get_menu_entries(self, app):
        """Return a list of (label, callback) tuples for the Plugins menu."""
        return []


class PluginLoader:
    def __init__(self, plugins_dir=None):
        self.plugins_dir = plugins_dir or PLUGINS_DIR
        self.plugins = []
        self.enabled = {}
        self._log_callback = None

    def set_log_callback(self, callback):
        self._log_callback = callback
        for plugin in self.plugins:
            plugin.set_log_callback(callback)

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
                        instance.set_log_callback(self._log_callback)
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

    def get_gui_tabs(self, app):
        tabs = []
        for plugin in self.plugins:
            if not self.is_enabled(plugin.name):
                continue
            try:
                widget = plugin.get_gui_tab(app.root, app)
                if widget is not None:
                    title = getattr(plugin, "tab_title", plugin.name) or plugin.name
                    tabs.append((title, widget))
            except Exception:
                pass
        return tabs

    def get_menu_entries(self, app):
        entries = []
        for plugin in self.plugins:
            if not self.is_enabled(plugin.name):
                continue
            try:
                entries.extend(plugin.get_menu_entries(app))
            except Exception:
                pass
        return entries

    def get_plugins_info(self):
        return [
            {"name": p.name, "description": p.description, "version": p.version}
            for p in self.plugins
        ]
