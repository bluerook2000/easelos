# tests/test_gusset_plate.py
from pipeline.categories.gusset_plate import GussetPlateGenerator
from pipeline.materials import MATERIALS


def test_gusset_plate_generates_valid_solid():
    gen = GussetPlateGenerator()
    assert gen.category == "gusset_plate"

    variants = list(gen.enumerate_variants())
    assert len(variants) >= 50

    # All materials
    assert {v.material_slug for v in variants} == set(MATERIALS.keys())

    # Corner gusset valid solid
    corner = [v for v in variants if v.shape == "corner"]
    assert len(corner) > 0
    solid = gen.generate_solid(corner[0])
    assert solid.val().Volume() > 0
