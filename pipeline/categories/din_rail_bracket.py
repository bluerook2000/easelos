# pipeline/categories/din_rail_bracket.py
"""DIN rail bracket generator — brackets for DIN rail mounting."""
from typing import Iterator

import cadquery as cq

from pipeline.materials import get_sheet_metal_materials
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


DIN_RAIL_WIDTH = 35.0  # Standard DIN rail width
CLIP_DEPTH = 7.5       # Standard clip depth

# (plate_width, plate_height)
PLATE_SIZES = [
    (35, 40),
    (35, 60),
    (50, 50),
    (50, 70),
    (60, 60),
    (60, 80),
    (80, 80),
    (80, 100),
]

MOUNT_HOLES = [
    ("M3", 2),
    ("M4", 2),
    ("M4", 4),
]


class DinRailBracketGenerator(PartGenerator):
    category = "din_rail_bracket"
    manufacturing_type = "sheet_metal"

    def enumerate_variants(self) -> Iterator[PartParams]:
        materials = get_sheet_metal_materials()
        for mat_slug, mat in materials.items():
            for thickness in mat.thicknesses_mm:
                for plate_w, plate_h in PLATE_SIZES:
                    for label, count in MOUNT_HOLES:
                        dia = METRIC_CLEARANCE[label]
                        if dia < mat.min_feature_size_mm:
                            continue
                        margin = 8.0
                        holes = []
                        if count == 2:
                            y_off = (plate_h / 2) - margin
                            holes = [
                                HoleSpec(label, dia, 0, round(-y_off, 2)),
                                HoleSpec(label, dia, 0, round(y_off, 2)),
                            ]
                        else:
                            x_off = (plate_w / 2) - margin
                            y_off = (plate_h / 2) - margin
                            for cx in [-x_off, x_off]:
                                for cy in [-y_off, y_off]:
                                    holes.append(HoleSpec(label, dia, round(cx, 2), round(cy, 2)))
                        yield PartParams(
                            category=self.category,
                            shape="din_bracket",
                            width_mm=plate_w,
                            height_mm=plate_h,
                            thickness_mm=thickness,
                            material_slug=mat_slug,
                            hole_specs=tuple(holes[:count]),
                        )

    def generate_solid(self, params: PartParams) -> cq.Workplane:
        t = params.thickness_mm
        plate_w = params.width_mm
        plate_h = params.height_mm

        # Main mounting plate (vertical)
        plate = cq.Workplane("XY").box(plate_w, plate_h, t)
        # Bottom DIN rail clip flange
        clip = (
            cq.Workplane("XY")
            .box(plate_w, t, CLIP_DEPTH)
            .translate((0, -plate_h / 2 + t / 2, -(CLIP_DEPTH / 2 + t / 2)))
        )

        result = plate.union(clip)

        # Mounting holes in plate
        if params.hole_specs:
            result = (
                result.faces(">Z").workplane()
                .pushPoints([(h.x_mm, h.y_mm) for h in params.hole_specs])
                .hole(params.hole_specs[0].diameter_mm)
            )
        return result

    def part_name(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        mat = get_material(params.material_slug)
        hole_desc = f"{params.hole_count}x{params.hole_specs[0].label}" if params.hole_specs else ""
        return f"{mat.name} DIN Rail Bracket {params.width_mm:.0f}x{params.height_mm:.0f}mm {hole_desc}"

    def part_description(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        mat = get_material(params.material_slug)
        return (
            f"Sheet metal {mat.name.lower()} DIN rail mounting bracket, "
            f"{params.width_mm:.0f}x{params.height_mm:.0f}mm plate, "
            f"{params.thickness_mm}mm thick, with standard 35mm DIN rail clip."
        )
