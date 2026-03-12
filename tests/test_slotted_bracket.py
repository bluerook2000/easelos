# tests/test_slotted_bracket.py
"""Tests for slotted bracket generator."""
from pipeline.categories.slotted_bracket import SlottedBracketGenerator


def test_slotted_bracket_generates_valid_solid():
    gen = SlottedBracketGenerator()
    assert gen.category == "slotted_bracket"
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
