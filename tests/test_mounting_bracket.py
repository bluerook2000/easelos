# tests/test_mounting_bracket.py
import cadquery as cq
from pipeline.categories.mounting_bracket import MountingBracketGenerator
from pipeline.materials import MATERIALS


def test_mounting_bracket_generates_valid_solid():
    """Comprehensive test: category, variant count, solid generation, all materials."""
    gen = MountingBracketGenerator()
    assert gen.category == "mounting_bracket"

    variants = list(gen.enumerate_variants())
    assert len(variants) >= 50

    # All 3 materials represented
    materials_seen = {v.material_slug for v in variants}
    assert materials_seen == set(MATERIALS.keys())

    # First flat variant produces valid solid
    flat_variants = [v for v in variants if v.shape == "flat"]
    assert len(flat_variants) > 0
    solid = gen.generate_solid(flat_variants[0])
    assert solid is not None
    assert solid.val().Volume() > 0

    # L-bracket variant also valid
    l_variants = [v for v in variants if v.shape == "l"]
    assert len(l_variants) > 0
    solid_l = gen.generate_solid(l_variants[0])
    assert solid_l.val().Volume() > 0

    # Part name is reasonable
    name = gen.part_name(flat_variants[0])
    assert isinstance(name, str)
    assert len(name) > 10
