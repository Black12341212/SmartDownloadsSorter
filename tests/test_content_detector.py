import os

from core.content_detector import (
    detect_content_type,
    get_real_extension,
    should_override_extension,
)


def _write(path, data):
    with open(path, "wb") as f:
        f.write(data)


def test_jpeg_magic(tmp_path):
    p = tmp_path / "a.jpg"
    _write(p, b"\xff\xd8\xff" + b"\x00" * 8)
    assert detect_content_type(str(p)) == "image/jpeg"
    assert get_real_extension(str(p)) == ".jpg"


def test_png_magic(tmp_path):
    p = tmp_path / "a.png"
    _write(p, b"\x89PNG\r\n\x1a\n" + b"\x00" * 8)
    assert detect_content_type(str(p)) == "image/png"


def test_mp4_with_ftyp(tmp_path):
    p = tmp_path / "a.mp4"
    _write(p, b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 16)
    assert detect_content_type(str(p)) == "video/mp4"


def test_mp4_false_positive_avoided(tmp_path):
    # A binary file starting with size-like bytes but no 'ftyp' brand must not
    # be misclassified as MP4 (bug #21 regression).
    p = tmp_path / "a.bin"
    _write(p, b"\x00\x00\x00\x1c" + b"\x01\x02\x03\x04" + b"\xff" * 64)
    assert detect_content_type(str(p)) != "video/mp4"


def test_content_override_extension(tmp_path):
    p = tmp_path / "picture.txt"
    _write(p, b"\x89PNG\r\n\x1a\n" + b"\x00" * 8)
    overridden, new_ext = should_override_extension(str(p))
    assert overridden is True
    assert new_ext == ".png"
