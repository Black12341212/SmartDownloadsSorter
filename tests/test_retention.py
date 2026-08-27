import os
import time

from core.retention import RetentionManager


def test_retention_absolute_folder_path(tmp_path):
    old_dir = tmp_path / "archive"
    old_dir.mkdir()
    f = old_dir / "setup.exe"
    f.write_bytes(b"x" * 1024)
    # Force an old mtime.
    past = time.time() - (40 * 86400)
    os.utime(f, (past, past))

    base = str(tmp_path / "downloads")
    os.makedirs(base, exist_ok=True)

    rm = RetentionManager({
        "retention_enabled": True,
        "retention_max_age_days": 30,
        "retention_folders": [str(old_dir)],
        "retention_extensions": [".exe"],
    })
    result = rm.cleanup(base)
    assert result["deleted_count"] == 1
    assert not f.exists()


def test_retention_relative_folder_path(tmp_path):
    base = tmp_path / "downloads"
    base.mkdir()
    old_dir = base / "archive"
    old_dir.mkdir()
    f = old_dir / "installer.exe"
    f.write_bytes(b"x" * 1024)
    past = time.time() - (40 * 86400)
    os.utime(f, (past, past))

    rm = RetentionManager({
        "retention_enabled": True,
        "retention_max_age_days": 30,
        "retention_folders": ["archive"],
        "retention_extensions": [".exe"],
    })
    result = rm.cleanup(str(base))
    assert result["deleted_count"] == 1
