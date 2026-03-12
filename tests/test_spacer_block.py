# tests/test_spacer_block.py
"""Tests for spacer_block generator."""
from pipeline.categories.spacer_block import SpacerBlockGenerator


def test_spacer_block_generates_valid_solid():
    gen = SpacerBlockGenerator()
    assert gen.category == "spacer_block"
    assert gen.manufacturing_type == "cnc_milled"

    variants = list(gen.enumerate_variants())
    assert len(variants) >= 50

    # Test first variant generates valid 3D geometry
    params = variants[0]
    solid = gen.generate_solid(params)
    assert solid is not None
    assert solid.val().Volume() > 0

    # Verify name and description are non-empty
    assert len(gen.part_name(params)) > 0
    assert len(gen.part_description(params)) > 0

    # Verify only metal materials used (no plastics)
    materials_used = set(v.material_slug for v in variants)
    assert len(materials_used) >= 3
    plastics = {"delrin", "acrylic", "nylon", "hdpe", "polycarbonate", "uhmwpe"}
    assert materials_used.isdisjoint(plastics), f"CNC should not use plastics: {materials_used & plastics}"
