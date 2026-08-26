#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Анализ дубликатов файлов"""

import hashlib
import os
from collections import defaultdict


def find_duplicates_by_name_size(folder):
    groups = defaultdict(list)
    for root, _, files in os.walk(folder):
        for fname in files:
            fpath = os.path.join(root, fname)
            try:
                size = os.path.getsize(fpath)
                base = os.path.splitext(fname)[0].lower()
                key = (base, size)
                groups[key].append(fpath)
            except OSError:
                continue
    return {k: v for k, v in groups.items() if len(v) > 1}


def quick_hash(path, max_read=65536):
    h = hashlib.md5()
    with open(path, "rb") as f:
        chunk = f.read(max_read)
        h.update(chunk)
    size = os.path.getsize(path)
    h.update(str(size).encode())
    return h.hexdigest()


def _try_quick_hash(path, max_read=65536):
    try:
        return quick_hash(path, max_read)
    except OSError:
        return None


def find_duplicates_by_hash(folder, max_read=65536):
    hash_groups = defaultdict(list)
    for root, _, files in os.walk(folder):
        for fname in files:
            fpath = os.path.join(root, fname)
            try:
                h = quick_hash(fpath, max_read)
                hash_groups[h].append(fpath)
            except OSError:
                continue
    return {k: v for k, v in hash_groups.items() if len(v) > 1}


def delete_duplicates(group, keep="newest", verify_hash=False):
    """Delete duplicate copies within one scanned group.

    Only paths that still exist are considered. If verify_hash is True and
    any file in the group differs by content (quick hash), nothing is deleted.
    Returns (keep_path, deleted).
    """
    deleted = []
    existing = []
    for p in group:
        try:
            if os.path.isfile(p):
                existing.append((p, os.path.getmtime(p)))
        except OSError:
            continue

    if not existing:
        return None, deleted

    if len(existing) < 2:
        return existing[0][0], deleted

    if verify_hash:
        ref = _try_quick_hash(existing[0][0])
        if ref is None:
            return existing[0][0], []
        verified = [(p, m) for p, m in existing if _try_quick_hash(p) == ref]
        if len(verified) != len(existing):
            # Group is no longer a set of true duplicates: refuse to delete.
            return existing[0][0], []
        existing = verified

    if keep == "oldest":
        existing.sort(key=lambda pm: pm[1])
    elif keep == "largest":
        existing.sort(key=lambda pm: _safe_size(pm[0]), reverse=True)
    else:  # newest
        existing.sort(key=lambda pm: pm[1], reverse=True)

    keep_path = existing[0][0]
    for path, _ in existing[1:]:
        try:
            os.remove(path)
            deleted.append(path)
        except OSError:
            pass
    return keep_path, deleted


def _safe_size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


def get_duplicate_summary(folder, use_hash=False):
    if use_hash:
        raw = find_duplicates_by_hash(folder)
    else:
        raw = find_duplicates_by_name_size(folder)

    results = []
    total_wasted = 0
    for key, paths in raw.items():
        size = _safe_size(paths[0])
        wasted = size * (len(paths) - 1)
        total_wasted += wasted
        results.append({
            "name": os.path.basename(paths[0]),
            "paths": paths,
            "size": size,
            "count": len(paths),
            "wasted": wasted,
        })
    results.sort(key=lambda x: x["wasted"], reverse=True)
    return results, total_wasted
