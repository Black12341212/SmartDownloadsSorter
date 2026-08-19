#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Иконка в системном трее (pystray)"""

import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox


def create_tray_icon(app):
    try:
        import pystray
        from PIL import Image, ImageDraw
    except ImportError:
        return None

    icon_size = 64
    img = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([8, 8, 56, 56], fill=(70, 130, 180))
    draw.rectangle([16, 16, 48, 48], fill=(255, 255, 255))
    draw.rectangle([24, 24, 40, 40], fill=(70, 130, 180))

    def on_sort(icon, item):
        threading.Thread(target=app.engine.sort, daemon=True).start()

    def on_undo(icon, item):
        app.history_mgr.undo_last(1)

    def on_show(icon, item):
        app.root.after(0, lambda: app.root.deiconify())

    def on_quit(icon, item):
        app.scheduler.stop()
        icon.stop()
        app.root.after(0, app.root.quit)

    menu = pystray.Menu(
        pystray.MenuItem("Sort Now", on_sort),
        pystray.MenuItem("Undo Last", on_undo),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Show", on_show),
        pystray.MenuItem("Quit", on_quit),
    )

    icon = pystray.Icon("SmartSorter", img, "Smart Downloads Sorter", menu)
    return icon
