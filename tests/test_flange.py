# tests/test_flange.py
"""Tests for flange generator."""
from pipeline.categories.flange import FlangeGenerator


def test_flange_generates_valid_solid():
    gen = FlangeGenerator()
    assert gen.category == "flange"
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
