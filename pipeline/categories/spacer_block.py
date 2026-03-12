# pipeline/categories/spacer_block.py
"""Spacer block generator — precision spacers with through-holes."""
from typing import Iterator

import cadquery as cq

from pipeline.materials import get_cnc_materials
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


# (width, length, height)
SPACER_SIZES = [
    (10, 10, 5),
    (15, 15, 5),
    (15, 15, 10),
    (20, 20, 10),
    (20, 20, 15),
    (25, 25, 10),
    (25, 25, 20),
    (30, 30, 15),
    (30, 30, 25),
    (40, 40, 20),
    (40, 40, 30),
    (50, 50, 25),
]

SPACER_HOLES = [
    ("M3", 1),
    ("M4", 1),
    ("M5", 1),
    ("M6", 1),
]


class SpacerBlockGenerator(PartGenerator):
    category = "spacer_block"
    manufacturing_type = "cnc_milled"

    def enumerate_variants(self) -> Iterator[PartParams]:
        materials = get_cnc_materials()
        for mat_slug, mat in materials.items():
            for w, l, h in SPACER_SIZES:
                for label, count in SPACER_HOLES:
                    dia = METRIC_CLEARANCE[label]
                    if dia < mat.min_feature_size_mm:
                        continue
                    # Single center through-hole only if it fits
                    if dia >= min(w, l) - 4:
                        continue
                    holes = (HoleSpec(label, dia, 0, 0),)
                    yield PartParams(
                        category=self.category,
                        shape="spacer",
                        width_mm=w,
                        height_mm=l,
                        thickness_mm=h,
                        material_slug=mat_slug,
                        hole_specs=holes,
                    )

    def generate_solid(self, params: PartParams) -> cq.Workplane:
        result = (
            cq.Workplane("XY")
            .rect(params.width_mm, params.height_mm)
            .extrude(params.thickness_mm)
        )
        # Center through-hole
        if params.hole_specs:
            result = result.faces(">Z").workplane().hole(params.hole_specs[0].diameter_mm)
        # Chamfer all vertical edges
        try:
            result = result.edges("|Z").chamfer(0.5)
        except Exception:
            pass
        return result

    def part_name(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        mat = get_material(params.material_slug)
        hole_desc = params.hole_specs[0].label if params.hole_specs else ""
        return (
            f"{mat.name} Spacer Block "
            f"{params.width_mm:.0f}x{params.height_mm:.0f}x{params.thickness_mm:.0f}mm "
            f"{hole_desc}"
        )

    def part_description(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        mat = get_material(params.material_slug)
        if params.hole_specs:
            return (
                f"CNC-milled {mat.name.lower()} precision spacer block, "
                f"{params.width_mm:.0f}x{params.height_mm:.0f}x{params.thickness_mm:.0f}mm, "
                f"with {params.hole_specs[0].label} through-hole."
            )
        return (
            f"CNC-milled {mat.name.lower()} precision spacer block, "
            f"{params.width_mm:.0f}x{params.height_mm:.0f}x{params.thickness_mm:.0f}mm."
        )
