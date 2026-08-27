import os

from core.sorter_engine import SorterEngine
from core.rules_manager import RulesManager
from core.history import HistoryManager
from core.ignore_list import IgnoreList


def _engine(tmp_path, downloads):
    return SorterEngine(
        downloads_path=str(downloads),
        rules_manager=RulesManager(rules_file=str(tmp_path / "rules.json")),
        history_manager=HistoryManager(history_file=str(tmp_path / "history.json")),
        ignore_list=IgnoreList(ignore_file=str(tmp_path / "ignore.json")),
        settings={},
    )


def test_sort_moves_file_by_extension(tmp_path):
    downloads = tmp_path / "downloads"
    downloads.mkdir()
    (downloads / "photo.jpg").write_bytes(b"data")
    engine = _engine(tmp_path, downloads)
    result = engine.sort()
    assert result["moved"] == 1
    assert (downloads / "Images" / "photo.jpg").exists()


def test_sort_renames_on_conflict(tmp_path):
    downloads = tmp_path / "downloads"
    downloads.mkdir()
    (downloads / "photo.jpg").write_bytes(b"data")
    images = downloads / "Images"
    images.mkdir()
    (images / "photo.jpg").write_bytes(b"existing")
    engine = _engine(tmp_path, downloads)
    result = engine.sort()
    assert result["moved"] == 1
    assert (images / "photo_1.jpg").exists()


def test_sort_dry_run_moves_nothing(tmp_path):
    downloads = tmp_path / "downloads"
    downloads.mkdir()
    (downloads / "photo.jpg").write_bytes(b"data")
    engine = _engine(tmp_path, downloads)
    result = engine.sort(dry_run=True)
    assert result["moved"] == 1
    assert not (downloads / "Images" / "photo.jpg").exists()
