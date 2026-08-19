#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка файлов на соответствие правилам сортировки
v3.0: Added nested/conditional rules support (AND/OR operators)
"""

import os
import re


def get_file_size_mb(filepath):
    try:
        return os.path.getsize(filepath) / (1024 * 1024)
    except OSError:
        return 0


def check_file_match(filename, filepath, rule, real_ext=None):
    file_lower = filename.lower()

    if "size_min_mb" in rule or "size_max_mb" in rule:
        size_mb = get_file_size_mb(filepath)
        if "size_min_mb" in rule and size_mb < rule["size_min_mb"]:
            return False
        if "size_max_mb" in rule and size_mb > rule["size_max_mb"]:
            return False

    if rule.get("is_default_pdf"):
        return False

    conditions = rule.get("conditions", None)
    if conditions:
        return _check_nested_conditions(filename, filepath, rule, conditions, real_ext)

    extension_match = False
    extensions = rule.get("extensions", [])

    if real_ext:
        for ext in extensions:
            if real_ext.lower() == ext.lower():
                extension_match = True
                break

    if not extension_match:
        for ext in extensions:
            if file_lower.endswith(ext.lower()):
                extension_match = True
                break

    if not extension_match and extensions:
        return False

    if extension_match and file_lower.endswith(".pdf"):
        if rule.get("name_contains") or rule.get("regex"):
            name_match = False
            for text in rule.get("name_contains", []):
                if text.lower() in file_lower:
                    name_match = True
                    break
            if not name_match:
                for pattern in rule.get("regex", []):
                    try:
                        if re.search(pattern, filename):
                            name_match = True
                            break
                    except re.error:
                        pass
            return name_match
        else:
            return True

    if extension_match:
        if rule.get("name_contains") or rule.get("regex"):
            for text in rule.get("name_contains", []):
                if text.lower() in file_lower:
                    return True
            for pattern in rule.get("regex", []):
                try:
                    if re.search(pattern, filename):
                        return True
                except re.error:
                    pass
            return False
        else:
            return True

    return False


def _check_nested_conditions(filename, filepath, rule, conditions, real_ext=None):
    logic = conditions.get("logic", "AND").upper()
    checks = []

    for cond in conditions.get("rules", []):
        result = _evaluate_condition(filename, filepath, rule, cond, real_ext)
        checks.append(result)

    if logic == "AND":
        return all(checks)
    elif logic == "OR":
        return any(checks)
    return False


def _evaluate_condition(filename, filepath, rule, condition, real_ext=None):
    ctype = condition.get("type", "")
    file_lower = filename.lower()

    if ctype == "extension":
        exts = condition.get("extensions", [])
        if real_ext:
            return any(real_ext.lower() == e.lower() for e in exts)
        return any(file_lower.endswith(e.lower()) for e in exts)

    elif ctype == "name_contains":
        keywords = condition.get("keywords", [])
        return any(kw.lower() in file_lower for kw in keywords)

    elif ctype == "regex":
        patterns = condition.get("patterns", [])
        for pat in patterns:
            try:
                if re.search(pat, filename):
                    return True
            except re.error:
                pass
        return False

    elif ctype == "size_min":
        return get_file_size_mb(filepath) >= condition.get("value", 0)

    elif ctype == "size_max":
        return get_file_size_mb(filepath) <= condition.get("value", float("inf"))

    elif ctype == "content_type":
        try:
            from core.content_detector import detect_content_type
            mime = detect_content_type(filepath)
            expected = condition.get("mime_types", [])
            return mime in expected if mime else False
        except ImportError:
            return False

    elif ctype == "not_extension":
        exts = condition.get("extensions", [])
        return not any(file_lower.endswith(e.lower()) for e in exts)

    return False


def analyze_pdf(filename, filepath):
    file_lower = filename.lower()
    size_mb = get_file_size_mb(filepath)

    if size_mb > 50:
        return "PDF_Books", "Large PDF (>50MB) - likely a book"
    elif size_mb < 1:
        return "PDF_Forms", "Small PDF (<1MB) - likely a form"

    if any(w in file_lower for w in ["invoice", "receipt", "счет", "чек", "квитанция"]):
        return "PDF_Forms", "Invoice/receipt keywords detected"
    elif any(w in file_lower for w in ["presentation", "slides", "презентация"]):
        return "PDF_Other", "Possibly a presentation"

    return None, None


def test_regex(pattern, test_string):
    try:
        match = re.search(pattern, test_string)
        if match:
            return True, match.group(), match.start(), match.end()
        return False, None, -1, -1
    except re.error as e:
        return False, str(e), -1, -1
