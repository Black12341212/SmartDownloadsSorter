#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Portable mode: all configs stored next to exe/script, not in home directory"""

import os
import sys
from pathlib import Path


def is_portable_mode():
    """Check if running in portable mode (exe dir contains .portable marker or --portable flag)."""
    if "--portable" in sys.argv:
        return True
    return os.path.exists(os.path.join(get_app_dir(), ".portable"))


def get_app_dir():
    """Get the application base directory."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_config_dir():
    """Get config directory: next to app in portable mode, or in user home."""
    app_dir = get_app_dir()
    if is_portable_mode():
        config_dir = os.path.join(app_dir, "config")
    else:
        config_dir = str(Path(__file__).parent.parent / "config")
    os.makedirs(config_dir, exist_ok=True)
    return config_dir


def get_data_dir():
    """Get data directory for logs, profiles, etc."""
    return get_config_dir()


def enable_portable_mode():
    """Create .portable marker file to enable portable mode."""
    marker = os.path.join(get_app_dir(), ".portable")
    with open(marker, "w") as f:
        f.write("portable")
    return True


def disable_portable_mode():
    """Remove .portable marker file."""
    marker = os.path.join(get_app_dir(), ".portable")
    if os.path.exists(marker):
        os.remove(marker)
    return True
