#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Логирование всех операций сортировки в sorter.log
v3.0: Enhanced with log level filtering support
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(log_dir=None, max_bytes=5*1024*1024, backup_count=3):
    if log_dir is None:
        try:
            from core.portable import get_config_dir
            log_dir = get_config_dir()
        except ImportError:
            log_dir = str(Path(__file__).parent.parent / "config")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "sorter.log")

    logger = logging.getLogger("SmartSorter")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    file_handler = RotatingFileHandler(
        log_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)-7s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_fmt)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    return logger


log = setup_logger()


def log_move(filename, source, dest, category=""):
    log.info(f"MOVED  {filename} -> {dest}  [category={category}]")


def log_error(filename, error):
    log.error(f"ERROR  {filename}: {error}")


def log_undo(filename, dest, source):
    log.info(f"UNDO   {filename}  {dest} -> {source}")


def log_sort_start(path, file_count):
    log.info(f"START  Sorting {path} ({file_count} files)")


def log_sort_end(moved, skipped, errors):
    log.info(f"END    Moved={moved} Skipped={skipped} Errors={errors}")


def log_auto_tick(interval):
    log.debug(f"AUTO   Scheduler tick (interval={interval}min)")


def log_plugin(plugin_name, message):
    log.info(f"PLUGIN [{plugin_name}] {message}")


def get_log_path():
    try:
        from core.portable import get_config_dir
        return os.path.join(get_config_dir(), "sorter.log")
    except ImportError:
        return str(Path(__file__).parent.parent / "config" / "sorter.log")


def read_log_lines(level_filter=None, max_lines=500):
    log_path = get_log_path()
    lines = []
    if not os.path.exists(log_path):
        return lines
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
        for line in all_lines:
            if level_filter and level_filter != "ALL":
                if f"[{level_filter}" not in line and f"{level_filter} " not in line:
                    continue
            lines.append(line.rstrip())
        return lines[-max_lines:]
    except Exception:
        return []
