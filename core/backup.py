#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Backup / Restore configuration (Feature #9)"""

import json
import os
import zipfile
import shutil
from datetime import datetime
from core.portable import get_config_dir

BACKUP_MARKER = "__backup_manifest__.json"


def create_backup(output_path=None):
    config_dir = get_config_dir()
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(config_dir, f"backup_{timestamp}.zip")

    files_to_backup = []
    for root, dirs, files in os.walk(config_dir):
        for fname in files:
            if fname.endswith(".zip"):
                continue
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, config_dir)
            files_to_backup.append(rel_path)

    manifest = {
        "version": "3.0",
        "created": datetime.now().isoformat(),
        "files": files_to_backup,
    }

    try:
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(BACKUP_MARKER, json.dumps(manifest, indent=2))
            for rel_path in files_to_backup:
                full_path = os.path.join(config_dir, rel_path)
                zf.write(full_path, rel_path)
        return {"success": True, "path": output_path, "files_count": len(files_to_backup)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def restore_backup(backup_path):
    config_dir = get_config_dir()
    if not os.path.exists(backup_path):
        return {"success": False, "error": "Backup file not found"}

    try:
        with zipfile.ZipFile(backup_path, "r") as zf:
            if BACKUP_MARKER not in zf.namelist():
                return {"success": False, "error": "Invalid backup file (no manifest)"}

            manifest = json.loads(zf.read(BACKUP_MARKER))
            restored_files = []
            skipped_files = []

            config_dir_abs = os.path.abspath(config_dir)
            for rel_path in manifest.get("files", []):
                if rel_path == BACKUP_MARKER:
                    continue
                if rel_path in zf.namelist():
                    target = os.path.abspath(os.path.join(config_dir, rel_path))
                    if target != config_dir_abs and not target.startswith(config_dir_abs + os.sep):
                        skipped_files.append(rel_path)
                        continue
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    with zf.open(rel_path) as src, open(target, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    restored_files.append(rel_path)
                else:
                    skipped_files.append(rel_path)

            return {
                "success": True,
                "restored": len(restored_files),
                "skipped": len(skipped_files),
                "files": restored_files,
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_backups():
    config_dir = get_config_dir()
    backups = []
    for fname in os.listdir(config_dir):
        if fname.startswith("backup_") and fname.endswith(".zip"):
            fpath = os.path.join(config_dir, fname)
            size = os.path.getsize(fpath)
            backups.append({
                "name": fname,
                "path": fpath,
                "size_mb": round(size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat(),
            })
    backups.sort(key=lambda x: x["created"], reverse=True)
    return backups
