# tests/test_base_plate.py
from pipeline.categories.base_plate import BasePlateGenerator
from pipeline.materials import MATERIALS


def test_base_plate_generates_valid_solid():
    gen = BasePlateGenerator()
    assert gen.category == "base_plate"
    variants = list(gen.enumerate_variants())
    assert len(variants) >= 50
    assert {v.material_slug for v in variants} == set(MATERIALS.keys())
    v = next(gen.enumerate_variants())
    solid = gen.generate_solid(v)
    assert solid.val().Volume() > 0
