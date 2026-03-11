from pipeline.categories.bearing_plate import BearingPlateGenerator
from pipeline.materials import MATERIALS

def test_bearing_plate_generates_valid_solid():
    gen = BearingPlateGenerator()
    assert gen.category == "bearing_plate"
    variants = list(gen.enumerate_variants())
    assert len(variants) >= 50
    assert {v.material_slug for v in variants} == set(MATERIALS.keys())
    # 608_mount shape
    v608 = [v for v in variants if v.shape == "608_mount"]
    assert len(v608) > 0
    solid = gen.generate_solid(v608[0])
    assert solid.val().Volume() > 0
    # 6201_mount shape
    v6201 = [v for v in variants if v.shape == "6201_mount"]
    assert len(v6201) > 0
    solid2 = gen.generate_solid(v6201[0])
    assert solid2.val().Volume() > 0
