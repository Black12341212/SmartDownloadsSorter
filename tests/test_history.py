import os

from core.history import HistoryManager


def test_undo_moves_file_back(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    f = src / "file.txt"
    f.write_text("hello")
    target = dst / "file.txt"
    f.replace(target)  # the file now physically lives at the destination

    hm = HistoryManager(history_file=str(tmp_path / "history.json"))
    hm.record("file.txt", str(f), str(target), "Documents")
    moved = hm.undo_last(1)
    assert len(moved) == 1
    assert (src / "file.txt").exists()
    assert not target.exists()


def test_undo_missing_source_reports_nothing(tmp_path):
    dst = tmp_path / "dst"
    dst.mkdir()
    missing_dest = dst / "missing.txt"  # current location does not exist

    hm = HistoryManager(history_file=str(tmp_path / "history.json"))
    hm.record("gone.txt", str(tmp_path / "somewhere" / "gone.txt"),
              str(missing_dest), "Documents")
    moved = hm.undo_last(1)
    assert moved == []
