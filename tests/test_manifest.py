# tests/test_manifest.py
import json
from pipeline.manifest import Manifest


def test_manifest_new(tmp_path):
    m = Manifest(str(tmp_path / "manifest.json"))
    assert m.is_empty()


def test_manifest_add_and_check(tmp_path):
    m = Manifest(str(tmp_path / "manifest.json"))
    m.mark_generated("part-1", {"width": 50, "holes": 4})
    assert m.is_generated("part-1", {"width": 50, "holes": 4})


def test_manifest_detects_changed_params(tmp_path):
    m = Manifest(str(tmp_path / "manifest.json"))
    m.mark_generated("part-1", {"width": 50, "holes": 4})
    # Different params = not generated
    assert not m.is_generated("part-1", {"width": 60, "holes": 4})


def test_manifest_persists(tmp_path):
    path = str(tmp_path / "manifest.json")
    m1 = Manifest(path)
    m1.mark_generated("part-1", {"width": 50})
    m1.save()

    m2 = Manifest(path)
    assert m2.is_generated("part-1", {"width": 50})


def test_manifest_count(tmp_path):
    m = Manifest(str(tmp_path / "manifest.json"))
    m.mark_generated("part-1", {})
    m.mark_generated("part-2", {})
    assert m.count() == 2
