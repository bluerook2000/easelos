# tests/test_heatsink_plate.py
"""Tests for heatsink plate generator."""
from pipeline.categories.heatsink_plate import HeatsinkPlateGenerator


def test_heatsink_plate_generates_valid_solid():
    gen = HeatsinkPlateGenerator()
    assert gen.category == "heatsink_plate"
    assert gen.manufacturing_type == "laser_cut"
    variants = list(gen.enumerate_variants())
    assert len(variants) >= 50
    params = variants[0]
    solid = gen.generate_solid(params)
    assert solid is not None
    assert solid.val().Volume() > 0
    assert len(gen.part_name(params)) > 0
    assert len(gen.part_description(params)) > 0
    # Verify metals only (no plastics — heatsinks need thermal conductivity)
    materials_used = set(v.material_slug for v in variants)
    plastics = {"delrin", "acrylic", "nylon", "hdpe", "polycarbonate", "uhmwpe"}
    assert materials_used.isdisjoint(plastics)
