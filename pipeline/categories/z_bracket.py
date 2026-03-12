# pipeline/categories/z_bracket.py
"""Z-bracket generator — offset mounting brackets."""
from typing import Iterator

import cadquery as cq

from pipeline.materials import get_sheet_metal_materials
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


# (plate_width, plate_depth, offset_height, length)
Z_SIZES = [
    (30, 20, 15, 50),
    (40, 25, 20, 80),
    (50, 30, 25, 100),
    (60, 35, 30, 120),
    (80, 50, 40, 150),
]

MOUNT_HOLES = [
    ("M4", 2),
    ("M5", 2),
    ("M5", 4),
    ("M6", 4),
]


class ZBracketGenerator(PartGenerator):
    category = "z_bracket"
    manufacturing_type = "sheet_metal"

    def enumerate_variants(self) -> Iterator[PartParams]:
        materials = get_sheet_metal_materials()
        for mat_slug, mat in materials.items():
            for thickness in mat.thicknesses_mm:
                for plate_w, plate_d, offset_h, length in Z_SIZES:
                    for label, count in MOUNT_HOLES:
                        dia = METRIC_CLEARANCE[label]
                        if dia < mat.min_feature_size_mm:
                            continue
                        margin = 8.0
                        holes = []
                        if count == 2:
                            x_off = (plate_w / 2) - margin
                            holes = [
                                HoleSpec(label, dia, round(-x_off, 2), 0),
                                HoleSpec(label, dia, round(x_off, 2), 0),
                            ]
                        else:
                            x_off = (plate_w / 2) - margin
                            y_off = (length / 2) - margin
                            for cx in [-x_off, x_off]:
                                for cy in [-y_off, y_off]:
                                    holes.append(HoleSpec(label, dia, round(cx, 2), round(cy, 2)))
                        yield PartParams(
                            category=self.category,
                            shape="z_bracket",
                            width_mm=plate_w,
                            height_mm=length,
                            thickness_mm=thickness,
                            material_slug=mat_slug,
                            hole_specs=tuple(holes[:count]),
                            extra=f'{{"plate_depth": {plate_d}, "offset_height": {offset_h}}}',
                        )

    def generate_solid(self, params: PartParams) -> cq.Workplane:
        import json
        extra = json.loads(params.extra) if params.extra else {}
        plate_d = extra.get("plate_depth", 25)
        offset_h = extra.get("offset_height", 20)
        t = params.thickness_mm
        plate_w = params.width_mm
        length = params.height_mm

        top = cq.Workplane("XY").box(plate_d, length, t).translate((0, 0, offset_h + t / 2))
        vertical = (
            cq.Workplane("XY")
            .box(t, length, offset_h)
            .translate((plate_d / 2 - t / 2, 0, offset_h / 2 + t / 2))
        )
        bottom = cq.Workplane("XY").box(plate_d, length, t).translate((plate_d - t, 0, t / 2))

        result = top.union(vertical).union(bottom)

        if params.hole_specs:
            result = (
                result.faces(">Z").workplane()
                .pushPoints([(h.x_mm, h.y_mm) for h in params.hole_specs])
                .hole(params.hole_specs[0].diameter_mm)
            )
        return result

    def part_name(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        import json
        mat = get_material(params.material_slug)
        extra = json.loads(params.extra) if params.extra else {}
        offset_h = extra.get("offset_height", 20)
        return (
            f"{mat.name} Z-Bracket {params.width_mm:.0f}x{params.height_mm:.0f}mm "
            f"{offset_h:.0f}mm Offset"
        )

    def part_description(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        import json
        mat = get_material(params.material_slug)
        extra = json.loads(params.extra) if params.extra else {}
        offset_h = extra.get("offset_height", 20)
        return (
            f"Sheet metal {mat.name.lower()} Z-bracket, "
            f"{params.width_mm:.0f}mm wide x {params.height_mm:.0f}mm long, "
            f"{offset_h:.0f}mm offset, {params.thickness_mm}mm thick."
        )
