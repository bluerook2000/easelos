# tests/test_enclosure_panel.py
"""Tests for enclosure panel generator."""
from pipeline.categories.enclosure_panel import EnclosurePanelGenerator


def test_enclosure_panel_generates_valid_solid():
    gen = EnclosurePanelGenerator()
    assert gen.category == "enclosure_panel"
    assert gen.manufacturing_type == "laser_cut"
    variants = list(gen.enumerate_variants())
    assert len(variants) >= 50
    params = variants[0]
    solid = gen.generate_solid(params)
    assert solid is not None
    assert solid.val().Volume() > 0
    assert len(gen.part_name(params)) > 0
    assert len(gen.part_description(params)) > 0
    materials_used = set(v.material_slug for v in variants)
    assert len(materials_used) >= 3
