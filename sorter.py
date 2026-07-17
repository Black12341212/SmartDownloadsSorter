#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Downloads Sorter v2.0
Entry point: GUI + CLI modes
"""

import argparse
import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from core.sorter_engine import SorterEngine
from core.rules_manager import RulesManager
from core.history import HistoryManager
from core.ignore_list import IgnoreList
from core.cloud_sync import SettingsManager
from core.scheduler import Scheduler
from core.logger import setup_logger, log


def run_cli_sort(args):
    settings = SettingsManager()
    engine = SorterEngine(
        downloads_path=args.target or settings.get("downloads_path"),
        rules_manager=RulesManager(),
        history_manager=HistoryManager(),
        ignore_list=IgnoreList(),
        settings=settings.settings,
    )
    result = engine.sort(dry_run=args.dry_run, target_path=args.target)
    print(f"\nResult: {result['moved']} moved, {result['skipped']} skipped, {result['errors']} errors")
    return result


def run_cli_auto(args):
    settings = SettingsManager()
    engine = SorterEngine(
        downloads_path=settings.get("downloads_path"),
        rules_manager=RulesManager(),
        history_manager=HistoryManager(),
        ignore_list=IgnoreList(),
        settings=settings.settings,
    )
    interval = args.interval or settings.get("auto_sort_interval", 15)
    print(f"Auto-sort started: every {interval} minutes. Press Ctrl+C to stop.")

    def auto_tick():
        log.info(f"Auto-sort tick (interval={interval}min)")
        engine.sort()

    scheduler = Scheduler(sort_callback=auto_tick)
    scheduler.set_interval(interval)
    scheduler.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
        print("Auto-sort stopped.")


def run_cli_undo(args):
    history = HistoryManager()
    count = args.count or 1
    undone = history.undo_last(count)
    if undone:
        for entry in undone:
            print(f"Undid: {entry.get('filename', '')}")
        print(f"Undone {len(undone)} operations.")
    else:
        print("Nothing to undo.")


def run_cli_duplicates(args):
    from core.duplicates import get_duplicate_summary
    settings = SettingsManager()
    path = args.target or settings.get("downloads_path")
    results, wasted = get_duplicate_summary(path, use_hash=args.hash)
    if not results:
        print("No duplicates found.")
        return
    print(f"Found {len(results)} duplicate groups, wasted: {wasted / (1024*1024):.1f} MB\n")
    for group in results[:20]:
        print(f"  {group['name']} ({group['count']} copies, {group['size']/(1024*1024):.2f} MB)")
        for p in group["paths"][:3]:
            print(f"    {p}")


def run_gui():
    from gui.app import run_gui
    run_gui()


def main():
    parser = argparse.ArgumentParser(
        description="Smart Downloads Sorter v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sorter.py                  Launch GUI
  python sorter.py --sort           Silent sort of Downloads
  python sorter.py --sort --target D:\\MyFiles  Sort specific folder
  python sorter.py --auto 30        Auto-sort every 30 minutes
  python sorter.py --undo 3         Undo last 3 operations
  python sorter.py --duplicates     Find duplicates
  python sorter.py --dry-run        Dry run without moving files
        """,
    )

    parser.add_argument("--sort", action="store_true",
                        help="Silent sort (no GUI)")
    parser.add_argument("--target", type=str, default=None,
                        help="Target folder to sort")
    parser.add_argument("--auto", type=int, nargs="?", const=15, default=None,
                        help="Auto-sort mode with interval in minutes (default: 15)")
    parser.add_argument("--undo", type=int, nargs="?", const=1, default=None,
                        help="Undo last N operations (default: 1)")
    parser.add_argument("--duplicates", action="store_true",
                        help="Scan for duplicate files")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be moved without actually moving")
    parser.add_argument("--hash", action="store_true",
                        help="Use hash-based duplicate detection (slower)")
    parser.add_argument("--version", action="version", version="Smart Sorter v2.0")

    args = parser.parse_args()

    setup_logger()

    if args.sort:
        run_cli_sort(args)
    elif args.auto is not None:
        run_cli_auto(args)
    elif args.undo is not None:
        run_cli_undo(args)
    elif args.duplicates:
        run_cli_duplicates(args)
    else:
        run_gui()


if __name__ == "__main__":
    main()
