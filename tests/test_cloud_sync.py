import os

from core.cloud_sync import SettingsManager, sync_to_cloud


def test_corrupt_settings_falls_back_to_defaults(tmp_path):
    settings_file = tmp_path / "settings.json"
    settings_file.write_text("{ this is not valid json ")
    sm = SettingsManager(settings_file=str(settings_file))
    assert sm.get("downloads_path")
    assert sm.get("auto_sort_interval") == 15


def test_settings_type_coercion(tmp_path):
    settings_file = tmp_path / "settings.json"
    settings_file.write_text('{"auto_sort_interval": "not-a-number", "watcher_enabled": "yes"}')
    sm = SettingsManager(settings_file=str(settings_file))
    assert isinstance(sm.get("auto_sort_interval"), int)
    # An unparseable numeric value falls back to the default (15).
    assert sm.get("auto_sort_interval") == 15
    assert sm.get("watcher_enabled") is True


def test_sync_to_cloud_copies_matching_category(tmp_path):
    source_dir = tmp_path / "src"
    cloud_dir = tmp_path / "cloud"
    source_dir.mkdir()
    cloud_dir.mkdir()
    moved = source_dir / "photo.jpg"
    moved.write_bytes(b"data")
    dest = source_dir / "Images" / "photo.jpg"
    dest.parent.mkdir()
    moved.replace(dest)

    items = [{"category": "Images", "dest": str(dest)}]
    copied = sync_to_cloud(str(source_dir), str(cloud_dir), ["Images"], items)
    assert len(copied) == 1
    assert any(p.endswith("Images" + os.sep + "photo.jpg") for p in copied)
