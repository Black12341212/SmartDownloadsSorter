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


def find_duplicates_by_hash(folder, max_read=65536):
    hash_groups = defaultdict(list)
    for root, _, files in os.walk(folder):
        for fname in files:
            fpath = os.path.join(root, fname)
            try:
                h = hashlib.md5()
                with open(fpath, "rb") as f:
                    chunk = f.read(max_read)
                    h.update(chunk)
                size = os.path.getsize(fpath)
                h.update(str(size).encode())
                key = h.hexdigest()
                hash_groups[key].append(fpath)
            except OSError:
                continue
    return {k: v for k, v in hash_groups.items() if len(v) > 1}


def delete_duplicates(group, keep="newest"):
    deleted = []
    if keep == "newest":
        paths = sorted(group, key=lambda p: os.path.getmtime(p), reverse=True)
    elif keep == "oldest":
        paths = sorted(group, key=lambda p: os.path.getmtime(p))
    else:
        paths = sorted(group, key=lambda p: os.path.getsize(p), reverse=True)

    keep_path = paths[0]
    for path in paths[1:]:
        try:
            os.remove(path)
            deleted.append(path)
        except OSError:
            pass
    return keep_path, deleted


def get_duplicate_summary(folder, use_hash=False):
    if use_hash:
        raw = find_duplicates_by_hash(folder)
    else:
        raw = find_duplicates_by_name_size(folder)

    results = []
    total_wasted = 0
    for key, paths in raw.items():
        size = os.path.getsize(paths[0])
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
