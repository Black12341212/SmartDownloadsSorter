import os

from core.duplicates import (
    find_duplicates_by_hash,
    find_duplicates_by_name_size,
)


def _make(root, name, content):
    os.makedirs(root, exist_ok=True)
    p = os.path.join(root, name)
    with open(p, "wb") as f:
        f.write(content)
    return p


def test_hash_finds_true_duplicates(tmp_path):
    d = str(tmp_path)
    _make(d, "a.bin", b"same-content" * 100)
    _make(d, "b.bin", b"same-content" * 100)
    groups = find_duplicates_by_hash(d)
    assert len(groups) == 1


def test_hash_no_false_positive_on_divergent_tail(tmp_path):
    # Same length and same first 64KB but different tail must not collide.
    head = b"\x00" * 65536
    d = str(tmp_path)
    _make(d, "a.bin", head + b"AAAA")
    _make(d, "b.bin", head + b"BBBB")
    groups = find_duplicates_by_hash(d)
    assert len(groups) == 0


def test_name_size_groups(tmp_path):
    d = str(tmp_path)
    _make(os.path.join(d, "sub1"), "a.bin", b"content-xyz")
    _make(os.path.join(d, "sub2"), "a.bin", b"content-xyz")
    _make(d, "c.bin", b"different")
    groups = find_duplicates_by_name_size(d)
    assert len(groups) == 1
