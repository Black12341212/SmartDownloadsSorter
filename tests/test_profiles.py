import os

from core.profiles import ProfileManager, sanitize_profile_name


def test_sanitize_strips_path_separators():
    assert sanitize_profile_name("../../evil") == "evil"
    assert ".." not in sanitize_profile_name("../../evil")
    assert sanitize_profile_name("") == "profile"
    assert sanitize_profile_name("my profile!") == "my profile"


def test_save_profile_cannot_escape_dir(tmp_path):
    pm = ProfileManager(profiles_dir=str(tmp_path / "profiles"))
    name = "../../escape"
    pm.save_profile(name, {"Images": {}})
    # File must be inside the profiles directory, not outside it.
    expected = tmp_path / "profiles" / "escape.json"
    assert expected.exists()
    assert not (tmp_path / "escape.json").exists()
