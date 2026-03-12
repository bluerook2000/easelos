# tests/test_hinge.py
"""Tests for hinge generator."""
import cadquery as cq
from pipeline.categories.hinge import HingeGenerator
from pipeline.materials import MATERIALS


def test_hinge_generates_valid_solid():
    gen = HingeGenerator()
    assert gen.category == "hinge"
    assert gen.manufacturing_type == "laser_cut"

    variants = list(gen.enumerate_variants())
    assert len(variants) >= 50

    # Test first variant generates valid geometry
    params = variants[0]
    solid = gen.generate_solid(params)
    assert solid is not None
    assert solid.val().Volume() > 0

    # Verify name and description are non-empty
    assert len(gen.part_name(params)) > 0
    assert len(gen.part_description(params)) > 0

    # Verify multiple materials are represented
    materials_used = set(v.material_slug for v in variants)
    assert len(materials_used) >= 3

    # Verify multiple shapes
    shapes_used = set(v.shape for v in variants)
    assert len(shapes_used) >= 2
