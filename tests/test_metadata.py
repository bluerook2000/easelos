# tests/test_metadata.py
import json
from pipeline.metadata import generate_metadata

REQUIRED_FIELDS = [
    "part_id",
    "category",
    "name",
    "description",
    "manufacturing_type",
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
        manufacturing_type="laser_cut",
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
        manufacturing_type="laser_cut",
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
        manufacturing_type="laser_cut",
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
        manufacturing_type="laser_cut",
    )
    serialized = json.dumps(meta)
    assert isinstance(serialized, str)


def test_metadata_has_manufacturing_type():
    """Metadata includes manufacturing_type field."""
    meta = generate_metadata(
        part_id="test-part",
        category="mounting_bracket",
        name="Test Part",
        description="A test part",
        width_mm=50,
        height_mm=30,
        thickness_mm=3.0,
        hole_count=4,
        hole_specs=[],
        material_slug="aluminum",
        manufacturing_type="laser_cut",
    )
    assert meta["manufacturing_type"] == "laser_cut"


def test_metadata_pricing_with_multiplier():
    """Metadata pricing reflects material multiplier."""
    meta = generate_metadata(
        part_id="test-titanium",
        category="mounting_bracket",
        name="Ti Part",
        description="A titanium part",
        width_mm=50,
        height_mm=30,
        thickness_mm=3.0,
        hole_count=4,
        hole_specs=[],
        material_slug="titanium",
        manufacturing_type="laser_cut",
    )
    # Titanium pricing should be higher than aluminum (4x multiplier)
    assert meta["pricing"]["titanium"][1] > meta["pricing"]["aluminum"][1]


def test_metadata_pricing_material_filtering():
    """CNC parts only include metal materials in pricing, not plastics."""
    meta = generate_metadata(
        part_id="test-cnc",
        category="shaft_coupler",
        name="CNC Part",
        description="A CNC part",
        width_mm=30,
        height_mm=30,
        thickness_mm=20.0,
        hole_count=2,
        hole_specs=[],
        material_slug="aluminum",
        manufacturing_type="cnc_milled",
    )
    # CNC parts should have metals only (8 materials), no plastics
    assert "aluminum" in meta["pricing"]
    assert "titanium" in meta["pricing"]
    assert "delrin" not in meta["pricing"]
    assert "acrylic" not in meta["pricing"]
    assert len(meta["pricing"]) == 8

    # Laser-cut parts should have all 14 materials
    meta_laser = generate_metadata(
        part_id="test-laser",
        category="mounting_bracket",
        name="Laser Part",
        description="A laser part",
        width_mm=50,
        height_mm=30,
        thickness_mm=3.0,
        hole_count=2,
        hole_specs=[],
        material_slug="aluminum",
        manufacturing_type="laser_cut",
    )
    assert len(meta_laser["pricing"]) == 14
    assert "delrin" in meta_laser["pricing"]


def test_metadata_has_glb_in_files():
    """Metadata files dict includes glb when manufacturing_type is not laser_cut."""
    meta = generate_metadata(
        part_id="test-cnc",
        category="shaft_coupler",
        name="CNC Part",
        description="A CNC part",
        width_mm=30,
        height_mm=30,
        thickness_mm=20.0,
        hole_count=2,
        hole_specs=[],
        material_slug="aluminum",
        manufacturing_type="cnc_milled",
    )
    assert "glb" in meta["files"]
    assert meta["files"]["glb"] == "model.glb"

    # Laser-cut should NOT have glb
    meta_laser = generate_metadata(
        part_id="test-laser",
        category="mounting_bracket",
        name="Laser Part",
        description="A laser part",
        width_mm=50,
        height_mm=30,
        thickness_mm=3.0,
        hole_count=2,
        hole_specs=[],
        material_slug="aluminum",
        manufacturing_type="laser_cut",
    )
    assert "glb" not in meta_laser["files"]
