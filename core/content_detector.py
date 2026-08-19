#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Content-based file type detection (Feature #3)"""

import os
import struct

MAGIC_SIGNATURES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"GIF87a": "image/gif",
    b"GIF89a": "image/gif",
    b"BM": "image/bmp",
    b"RIFF": "audio/wav",
    b"ID3": "audio/mpeg",
    b"\xff\xfb": "audio/mpeg",
    b"\xff\xf3": "audio/mpeg",
    b"\x00\x00\x01\x00": "image/x-icon",
    b"\x00\x00\x02\x00": "image/x-icon",
    b"%PDF": "application/pdf",
    b"PK\x03\x04": "application/zip",
    b"Rar!\x1a\x07": "application/x-rar-compressed",
    b"\x1f\x8b": "application/gzip",
    b"7z\xbc\xaf\x27\x1c": "application/x-7z-compressed",
    b"\xd0\xcf\x11\xe0": "application/msword",
    b"PK\x03\x04\x14": "application/vnd.openxmlformats",
    b"\x00\x01\x00\x00": "font/ttf",
    b"OTTO": "font/otf",
    b"wOFF": "font/woff",
    b"wOF2": "font/woff2",
    b"\x00 ITS": "image/tiff",
    b"II\x2a\x00": "image/tiff",
    b"MM\x00\x2a": "image/tiff",
    b"FLV\x01": "video/x-flv",
    b"\x1a\x45\xdf\xa3": "video/webm",
    b"\x00\x00\x00\x1c": "video/mp4",
    b"\x00\x00\x00\x20": "video/mp4",
    b"\x4f\x67\x67\x53": "audio/ogg",
    b"fLaC": "audio/flac",
    b"\x49\x49\x2a\x00": "image/tiff",
    b"\x4d\x4d\x00\x2a": "image/tiff",
}

CONTENT_TO_CATEGORY = {
    "image/jpeg": "Images",
    "image/png": "Images",
    "image/gif": "Images",
    "image/bmp": "Images",
    "image/svg+xml": "Images",
    "image/tiff": "Images",
    "image/x-icon": "Images",
    "image/webp": "Images",
    "video/mp4": "Videos",
    "video/x-flv": "Videos",
    "video/webm": "Videos",
    "video/x-matroska": "Videos",
    "video/avi": "Videos",
    "audio/mpeg": "Audio",
    "audio/wav": "Audio",
    "audio/ogg": "Audio",
    "audio/flac": "Audio",
    "audio/x-m4a": "Audio",
    "application/pdf": "PDF_Other",
    "application/zip": "Archives",
    "application/x-rar-compressed": "Archives",
    "application/gzip": "Archives",
    "application/x-7z-compressed": "Archives",
    "application/msword": "Documents",
    "application/vnd.openxmlformats": "Documents",
    "font/ttf": "Fonts",
    "font/otf": "Fonts",
    "font/woff": "Fonts",
    "font/woff2": "Fonts",
}


def detect_content_type(filepath):
    """Read the first bytes of a file and return its MIME type."""
    try:
        with open(filepath, "rb") as f:
            header = f.read(32)
        if not header:
            return None
        for signature, mime in MAGIC_SIGNATURES.items():
            if header[:len(signature)] == signature:
                return mime
        text = header.decode("utf-8", errors="ignore").strip()
        if text and all(c.isprintable() or c in "\n\r\t" for c in text[:16]):
            return "text/plain"
        return None
    except (OSError, IOError):
        return None


def detect_file_category(filepath, rules=None):
    """Detect the real category of a file based on content, ignoring extension."""
    mime = detect_content_type(filepath)
    if not mime:
        return None, None
    category = CONTENT_TO_CATEGORY.get(mime)
    if category and rules and category in rules:
        return category, mime
    return category, mime


def get_real_extension(filepath):
    """Return the correct extension based on content type."""
    mime = detect_content_type(filepath)
    if not mime:
        return None
    MIME_TO_EXT = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/bmp": ".bmp",
        "image/tiff": ".tiff",
        "image/x-icon": ".ico",
        "image/webp": ".webp",
        "video/mp4": ".mp4",
        "video/x-flv": ".flv",
        "video/webm": ".webm",
        "audio/mpeg": ".mp3",
        "audio/wav": ".wav",
        "audio/ogg": ".ogg",
        "audio/flac": ".flac",
        "application/pdf": ".pdf",
        "application/zip": ".zip",
        "application/x-rar-compressed": ".rar",
        "application/gzip": ".gz",
        "application/x-7z-compressed": ".7z",
        "font/ttf": ".ttf",
        "font/otf": ".otf",
        "font/woff": ".woff",
        "font/woff2": ".woff2",
        "text/plain": ".txt",
    }
    return MIME_TO_EXT.get(mime)


def should_override_extension(filepath):
    """Check if the file's content type doesn't match its extension."""
    current_ext = os.path.splitext(filepath)[1].lower()
    real_ext = get_real_extension(filepath)
    if real_ext and current_ext != real_ext:
        return True, real_ext
    return False, current_ext
