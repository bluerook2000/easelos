# pipeline/categories/u_channel.py
"""U-channel generator — structural channels with bent flanges."""
from typing import Iterator

import cadquery as cq

from pipeline.materials import get_sheet_metal_materials
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


# (base_width, flange_height, length)
CHANNEL_SIZES = [
    (30, 15, 50),
    (40, 20, 80),
    (50, 25, 100),
    (60, 30, 120),
    (80, 40, 150),
    (100, 50, 200),
]

MOUNT_HOLES = [
    ("M4", 2),
    ("M5", 4),
    ("M6", 4),
]


class UChannelGenerator(PartGenerator):
    category = "u_channel"
    manufacturing_type = "sheet_metal"

    def enumerate_variants(self) -> Iterator[PartParams]:
        materials = get_sheet_metal_materials()
        for mat_slug, mat in materials.items():
            for thickness in mat.thicknesses_mm:
                for base_w, flange_h, length in CHANNEL_SIZES:
                    for label, count in MOUNT_HOLES:
                        dia = METRIC_CLEARANCE[label]
                        if dia < mat.min_feature_size_mm:
                            continue
                        # Holes in the base
                        margin = 8.0
                        holes = []
                        if count == 2:
                            x_off = (base_w / 2) - margin
                            holes = [
                                HoleSpec(label, dia, round(-x_off, 2), 0),
                                HoleSpec(label, dia, round(x_off, 2), 0),
                            ]
                        else:
                            x_off = (base_w / 2) - margin
                            y_off = (length / 2) - margin
                            for cx in [-x_off, x_off]:
                                for cy in [-y_off, y_off]:
                                    holes.append(HoleSpec(label, dia, round(cx, 2), round(cy, 2)))
                        yield PartParams(
                            category=self.category,
                            shape="u_channel",
                            width_mm=base_w,
                            height_mm=length,
                            thickness_mm=thickness,
                            material_slug=mat_slug,
                            hole_specs=tuple(holes[:count]),
                            extra=f'{{"flange_height": {flange_h}}}',
                        )

    def generate_solid(self, params: PartParams) -> cq.Workplane:
        import json
        extra = json.loads(params.extra) if params.extra else {}
        flange_h = extra.get("flange_height", 20)
        t = params.thickness_mm
        base_w = params.width_mm
        length = params.height_mm

        # Build U-channel as union of 3 plates
        # Base plate
        base = cq.Workplane("XY").box(base_w, length, t)
        # Left flange
        left = (
            cq.Workplane("XY")
            .box(t, length, flange_h)
            .translate((-base_w / 2 + t / 2, 0, flange_h / 2 + t / 2))
        )
        # Right flange
        right = (
            cq.Workplane("XY")
            .box(t, length, flange_h)
            .translate((base_w / 2 - t / 2, 0, flange_h / 2 + t / 2))
        )

        result = base.union(left).union(right)

        # Add holes in base
        if params.hole_specs:
            result = (
                result.faces("<Z").workplane()
                .pushPoints([(h.x_mm, h.y_mm) for h in params.hole_specs])
                .hole(params.hole_specs[0].diameter_mm)
            )

        return result

    def part_name(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        import json
        mat = get_material(params.material_slug)
        extra = json.loads(params.extra) if params.extra else {}
        flange_h = extra.get("flange_height", 20)
        return (
            f"{mat.name} U-Channel {params.width_mm:.0f}x{params.height_mm:.0f}mm "
            f"{flange_h:.0f}mm Flanges"
        )

    def part_description(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        import json
        mat = get_material(params.material_slug)
        extra = json.loads(params.extra) if params.extra else {}
        flange_h = extra.get("flange_height", 20)
        return (
            f"Sheet metal {mat.name.lower()} U-channel, "
            f"{params.width_mm:.0f}mm base x {params.height_mm:.0f}mm long, "
            f"{flange_h:.0f}mm flanges, {params.thickness_mm}mm thick."
        )
