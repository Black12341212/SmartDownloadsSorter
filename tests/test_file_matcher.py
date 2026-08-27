from core.file_matcher import check_file_match, analyze_pdf


def _rule(extensions, **kw):
    r = {"folder": "X", "extensions": extensions, "name_contains": [], "regex": []}
    r.update(kw)
    return r


def test_extension_match():
    rule = _rule([".jpg", ".png"])
    assert check_file_match("photo.jpg", "photo.jpg", rule) is True
    assert check_file_match("doc.txt", "doc.txt", rule) is False


def test_name_contains_match():
    rule = _rule([".pdf"], name_contains=["invoice"])
    assert check_file_match("invoice_march.pdf", "invoice_march.pdf", rule) is True
    assert check_file_match("random.pdf", "random.pdf", rule) is False


def test_nested_conditions_and():
    rule = _rule([".pdf"], conditions={
        "logic": "AND",
        "rules": [
            {"type": "name_contains", "keywords": ["book"]},
            {"type": "size_min", "value": 5},
        ],
    })
    assert check_file_match("mybook.pdf", "mybook.pdf", rule) is False  # size unknown
    assert check_file_match("bigbook.pdf", "bigbook.pdf", rule) is False


def test_analyze_pdf_categories():
    cat, _ = analyze_pdf("bigbook.pdf", "bigbook.pdf")
    assert isinstance(cat, str)
    assert cat is not None
