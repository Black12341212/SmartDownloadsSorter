from core.i18n import I18n


def test_default_language_lookup():
    i = I18n("en")
    assert i.t("btn_sort_now") == "Sort Now"


def test_set_language_known_and_custom():
    i = I18n("en")
    i.set_language("ru")
    assert i.t("btn_sort_now") == "Сортировать"
    # Custom (non built-in) languages loaded via config/translations must be
    # selectable (bug #9 regression).
    i.translations["xx"] = {"btn_sort_now": "SORTXX"}
    i.set_language("xx")
    assert i.t("btn_sort_now") == "SORTXX"


def test_available_languages_includes_builtins():
    i = I18n("en")
    langs = i.get_available_languages()
    assert "en" in langs and "ru" in langs
