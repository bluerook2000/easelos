# tests/test_integration.py
"""Integration tests for the full pipeline."""
import json
import os

import cadquery as cq
import ezdxf

from pipeline.categories import ALL_GENERATORS, GENERATOR_MAP
from pipeline.manifest import Manifest
from pipeline.materials import MATERIALS


def test_smoke_generate_all_categories(tmp_path):
    """Generate 2 parts per category and validate all output formats."""
    manifest = Manifest(str(tmp_path / "manifest.json"))
    output_dir = str(tmp_path / "output")
    total_generated = 0

    for gen in ALL_GENERATORS:
        variants = list(gen.enumerate_variants())[:2]
        assert len(variants) > 0, f"No variants for {gen.category}"

        for params in variants:
            solid = gen.generate_solid(params)
            assert solid is not None
            assert solid.val().Volume() > 0

            part_dir = os.path.join(output_dir, gen.category, params.part_id)
            os.makedirs(part_dir, exist_ok=True)

            from pipeline.exporter import export_step, export_svg, export_dxf
            step_path = os.path.join(part_dir, "part.step")
            svg_path = os.path.join(part_dir, "profile.svg")
            dxf_path = os.path.join(part_dir, "profile.dxf")

            export_step(solid, step_path)
            export_svg(solid, svg_path)
            export_dxf(solid, dxf_path)

            # Validate STEP
            reimported = cq.importers.importStep(step_path)
            assert reimported is not None

            # Validate SVG
            svg_content = open(svg_path).read()
            assert "<svg" in svg_content

            # Validate DXF
            doc = ezdxf.readfile(dxf_path)
            assert len(list(doc.modelspace())) > 0

            total_generated += 1

    assert total_generated >= 46


def test_incremental_generation(tmp_path):
    """Running generation twice should skip already-generated parts."""
    manifest = Manifest(str(tmp_path / "manifest.json"))
    output_dir = str(tmp_path / "output")

    gen = ALL_GENERATORS[0]

    generated1 = gen.generate_all(output_dir, manifest)
    assert len(generated1) > 0
    manifest.save()

    manifest2 = Manifest(str(tmp_path / "manifest.json"))
    generated2 = gen.generate_all(output_dir, manifest2)
    assert len(generated2) == 0


def test_total_variant_count():
    """Verify we meet the 10,000+ parts target."""
    total = 0
    for gen in ALL_GENERATORS:
        count = len(list(gen.enumerate_variants()))
        assert count >= 50, f"{gen.category} has only {count} variants (need >= 50)"
        total += count
    assert total >= 10000, f"Total variants: {total} (need >= 10000)"


def test_metadata_schema(tmp_path):
    """Verify JSON metadata has all 20 required fields for one part."""
    gen = ALL_GENERATORS[0]
    params = next(gen.enumerate_variants())

    from pipeline.metadata import generate_metadata
    meta = generate_metadata(
        part_id=params.part_id,
        category=gen.category,
        name=gen.part_name(params),
        description=gen.part_description(params),
        width_mm=params.width_mm,
        height_mm=params.height_mm,
        thickness_mm=params.thickness_mm,
        hole_count=params.hole_count,
        hole_specs=[{"size": h.label, "diameter_mm": h.diameter_mm, "x_mm": h.x_mm, "y_mm": h.y_mm} for h in params.hole_specs],
        material_slug=params.material_slug,
        manufacturing_type="laser_cut",
    )

    # All 20 required fields
    required_fields = [
        "part_id", "category", "name", "description", "manufacturing_type",
        "width_mm", "height_mm", "thickness_mm",
        "width_in", "height_in", "area_sq_in",
        "hole_count", "hole_specs",
        "material", "material_name",
        "weight_estimate_g", "complexity", "size_category",
        "pricing", "files",
    ]
    for field in required_fields:
        assert field in meta, f"Missing: {field}"

    # Pricing for 14 materials (laser-cut) x 6 quantities
    from pipeline.materials import get_laser_cut_materials
    for mat_slug in get_laser_cut_materials():
        assert mat_slug in meta["pricing"], f"Missing pricing for {mat_slug}"
        for qty in [1, 10, 100, 500, 1000, 10000]:
            assert qty in meta["pricing"][mat_slug]
    assert len(meta["pricing"]) == 14  # all materials for laser-cut

    # JSON serializable
    json.dumps(meta)


def test_all_23_categories_registered():
    """ALL_GENERATORS has 23 entries."""
    assert len(ALL_GENERATORS) == 23
    assert len(GENERATOR_MAP) == 23
    expected = {
        "mounting_bracket", "motor_mount", "gusset_plate",
        "base_plate", "standoff", "sensor_mount",
        "electronics_panel", "bearing_plate", "cable_bracket",
        "hinge", "flange", "slotted_bracket", "enclosure_panel", "heatsink_plate",
        "u_channel", "z_bracket", "box_enclosure", "din_rail_bracket",
        "shaft_coupler", "motor_adapter", "t_slot_nut", "bearing_block", "spacer_block",
    }
    assert set(GENERATOR_MAP.keys()) == expected


def test_part_id_deterministic():
    """Same params produce the same part_id."""
    gen = ALL_GENERATORS[0]
    params = next(gen.enumerate_variants())
    id1 = params.part_id
    id2 = params.part_id
    assert id1 == id2


def test_ponoko_constraint_no_undersized_holes():
    """Every hole diameter >= material's min_feature_size_mm."""
    for gen in ALL_GENERATORS:
        for params in gen.enumerate_variants():
            mat = MATERIALS[params.material_slug]
            for hole in params.hole_specs:
                assert hole.diameter_mm >= mat.min_feature_size_mm, (
                    f"Part {params.part_id}: hole {hole.label} diameter "
                    f"{hole.diameter_mm}mm < min feature size {mat.min_feature_size_mm}mm "
                    f"for {mat.name}"
                )


def test_smoke_3d_parts_export_glb(tmp_path):
    """CNC and sheet metal parts export glTF files."""
    from pipeline.categories.shaft_coupler import ShaftCouplerGenerator
    from pipeline.exporter import export_glb
    gen = ShaftCouplerGenerator()
    params = next(gen.enumerate_variants())
    solid = gen.generate_solid(params)
    glb_path = str(tmp_path / "model.glb")
    result = export_glb(solid, glb_path)
    assert result is True
    assert os.path.exists(glb_path)
    assert os.path.getsize(glb_path) > 100


def test_pricing_multipliers_applied():
    """Different materials produce different prices in metadata."""
    from pipeline.metadata import generate_metadata
    meta = generate_metadata(
        part_id="test", category="test", name="Test", description="Test",
        width_mm=50, height_mm=30, thickness_mm=3.0,
        hole_count=2, hole_specs=[], material_slug="aluminum",
        manufacturing_type="laser_cut",
    )
    # Titanium should be 4x aluminum
    assert meta["pricing"]["titanium"][1] > meta["pricing"]["aluminum"][1]
    assert abs(meta["pricing"]["titanium"][1] / meta["pricing"]["aluminum"][1] - 4.0) < 0.01
