#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Автозапуск при входе в систему (Windows)"""

import os
import sys
import winreg


APP_NAME = "SmartSorter"


def get_exe_path():
    if getattr(sys, "frozen", False):
        return sys.executable
    return os.path.abspath(sys.argv[0])


def is_startup_enabled():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ,
        )
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False


def set_startup(enable=True):
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        if enable:
            exe = get_exe_path()
            if getattr(sys, "frozen", False):
                value = f'"{exe}" --auto-silent'
            else:
                value = f'"{sys.executable}" "{exe}" --auto-silent'
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, value)
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception:
        return False
