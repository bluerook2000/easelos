from pipeline.categories.standoff import StandoffGenerator
from pipeline.materials import MATERIALS

def test_standoff_generates_valid_solid():
    gen = StandoffGenerator()
    assert gen.category == "standoff"
    variants = list(gen.enumerate_variants())
    assert len(variants) >= 50
    assert {v.material_slug for v in variants} == set(MATERIALS.keys())
    v = next(gen.enumerate_variants())
    solid = gen.generate_solid(v)
    assert solid.val().Volume() > 0
