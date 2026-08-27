import os

from core.rules_manager import RulesManager


def test_default_rules_loaded(tmp_path):
    rm = RulesManager(rules_file=str(tmp_path / "rules.json"))
    assert "Images" in rm.all()
    assert rm.get("Images")["folder"] == "Images"


def test_add_remove_rule(tmp_path):
    rm = RulesManager(rules_file=str(tmp_path / "rules.json"))
    rm.add("Custom", {"folder": "Custom", "extensions": [".xyz"]})
    assert "Custom" in rm.all()
    assert rm.remove("Custom") is True
    assert "Custom" not in rm.all()


def test_reset_keeps_default_pdf_flag(tmp_path):
    rm = RulesManager(rules_file=str(tmp_path / "rules.json"))
    assert rm.get("PDF_Other").get("is_default_pdf") is True
