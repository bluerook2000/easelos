# tests/test_metadata.py
import json
from pipeline.metadata import generate_metadata

REQUIRED_FIELDS = [
    "part_id",
    "category",
    "name",
    "description",
    "width_mm",
    "height_mm",
    "thickness_mm",
    "width_in",
    "height_in",
    "area_sq_in",
    "hole_count",
    "hole_specs",
    "material",
    "material_name",
    "weight_estimate_g",
    "complexity",
    "size_category",
    "pricing",
    "files",
]


def test_metadata_has_all_required_fields():
    meta = generate_metadata(
        part_id="bracket-l-50x30x1.6-4xM5-aluminum",
        category="mounting_bracket",
        name="L-Bracket 50x30mm 4xM5 Aluminum",
        description="Aluminum L-bracket with 4 M5 mounting holes",
        width_mm=50.0,
        height_mm=30.0,
        thickness_mm=1.6,
        hole_count=4,
        hole_specs=[{"size": "M5", "diameter_mm": 5.0, "x_mm": 15.0, "y_mm": 0.0}],
        material_slug="aluminum",
    )
    for field in REQUIRED_FIELDS:
        assert field in meta, f"Missing field: {field}"


def test_pricing_has_all_tiers():
    meta = generate_metadata(
        part_id="test",
        category="test",
        name="Test",
        description="Test",
        width_mm=50.0,
        height_mm=30.0,
        thickness_mm=1.6,
        hole_count=4,
        hole_specs=[],
        material_slug="aluminum",
    )
    pricing = meta["pricing"]
    for material in ["aluminum", "steel", "stainless"]:
        assert material in pricing, f"Missing material pricing: {material}"
        for qty in [1, 10, 100, 500, 1000, 10000]:
            assert qty in pricing[material] or str(qty) in pricing[material]


def test_weight_estimate_reasonable():
    meta = generate_metadata(
        part_id="test",
        category="test",
        name="Test",
        description="Test",
        width_mm=50.0,
        height_mm=30.0,
        thickness_mm=3.2,
        hole_count=0,
        hole_specs=[],
        material_slug="aluminum",
    )
    # 50x30x3.2mm aluminum, density 2.68 g/cm3
    # volume = 5.0 * 3.0 * 0.32 = 4.8 cm3, weight ~ 12.86g
    weight = meta["weight_estimate_g"]
    assert 10 < weight < 20


def test_metadata_serializable():
    meta = generate_metadata(
        part_id="test",
        category="test",
        name="Test",
        description="Test",
        width_mm=50.0,
        height_mm=30.0,
        thickness_mm=1.6,
        hole_count=0,
        hole_specs=[],
        material_slug="aluminum",
    )
    serialized = json.dumps(meta)
    assert isinstance(serialized, str)
