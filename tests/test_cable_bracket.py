from pipeline.categories.cable_bracket import CableBracketGenerator
from pipeline.materials import MATERIALS

def test_cable_bracket_generates_valid_solid():
    gen = CableBracketGenerator()
    assert gen.category == "cable_bracket"
    variants = list(gen.enumerate_variants())
    assert len(variants) >= 50
    assert {v.material_slug for v in variants} == set(MATERIALS.keys())
    # clip shape
    clips = [v for v in variants if v.shape == "clip"]
    assert len(clips) > 0
    solid = gen.generate_solid(clips[0])
    assert solid.val().Volume() > 0
    # guide shape
    guides = [v for v in variants if v.shape == "guide"]
    assert len(guides) > 0
    solid_g = gen.generate_solid(guides[0])
    assert solid_g.val().Volume() > 0
