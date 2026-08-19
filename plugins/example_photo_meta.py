#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example Plugin: Photo EXIF Metadata Extractor
Demonstrates how to write a plugin for SmartSorter.

Place this file in the plugins/ folder.
"""

import os
from core.plugin_loader import BasePlugin


class PhotoMetaPlugin(BasePlugin):
    name = "PhotoMeta"
    description = "Extracts basic photo metadata (dimensions, size)"
    version = "1.0"

    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}

    def on_file_matched(self, filename, filepath, category, rule):
        ext = os.path.splitext(filename)[1].lower()
        if ext not in self.IMAGE_EXTENSIONS:
            return None

        metadata = {}
        try:
            metadata["file_size"] = os.path.getsize(filepath)
        except OSError:
            pass

        if ext in {".jpg", ".jpeg", ".png", ".webp"}:
            try:
                from PIL import Image
                with Image.open(filepath) as img:
                    metadata["width"], metadata["height"] = img.size
                    metadata["format"] = img.format
            except Exception:
                pass

        return {
            "filename": filename,
            "category": category,
            "metadata": metadata,
        }

    def on_sort_complete(self, results):
        count = sum(1 for r in results if r.get("metadata", {}).get("width"))
        if count:
            print(f"[PhotoMeta] Extracted metadata for {count} images")
