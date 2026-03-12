# pipeline/categories/box_enclosure.py
"""Box enclosure generator — open-top bent enclosures with mounting tabs."""
from typing import Iterator

import cadquery as cq

from pipeline.materials import get_sheet_metal_materials
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


# (base_width, base_depth, wall_height)
BOX_SIZES = [
    (60, 40, 20),
    (80, 60, 25),
    (100, 80, 30),
    (120, 80, 35),
    (150, 100, 40),
    (200, 150, 60),
]

MOUNT_HOLES = [
    ("M3", 4),
    ("M4", 4),
]


class BoxEnclosureGenerator(PartGenerator):
    category = "box_enclosure"
    manufacturing_type = "sheet_metal"

    def enumerate_variants(self) -> Iterator[PartParams]:
        materials = get_sheet_metal_materials()
        for mat_slug, mat in materials.items():
            for thickness in mat.thicknesses_mm:
                for base_w, base_d, wall_h in BOX_SIZES:
                    for label, count in MOUNT_HOLES:
                        dia = METRIC_CLEARANCE[label]
                        if dia < mat.min_feature_size_mm:
                            continue
                        margin = 8.0
                        x_off = (base_w / 2) - margin
                        y_off = (base_d / 2) - margin
                        holes = [
                            HoleSpec(label, dia, round(-x_off, 2), round(-y_off, 2)),
                            HoleSpec(label, dia, round(x_off, 2), round(-y_off, 2)),
                            HoleSpec(label, dia, round(-x_off, 2), round(y_off, 2)),
                            HoleSpec(label, dia, round(x_off, 2), round(y_off, 2)),
                        ]
                        yield PartParams(
                            category=self.category,
                            shape="open_top_box",
                            width_mm=base_w,
                            height_mm=base_d,
                            thickness_mm=thickness,
                            material_slug=mat_slug,
                            hole_specs=tuple(holes[:count]),
                            extra=f'{{"wall_height": {wall_h}}}',
                        )

    def generate_solid(self, params: PartParams) -> cq.Workplane:
        import json
        extra = json.loads(params.extra) if params.extra else {}
        wall_h = extra.get("wall_height", 30)
        t = params.thickness_mm
        base_w = params.width_mm
        base_d = params.height_mm

        # Base plate
        base = cq.Workplane("XY").box(base_w, base_d, t)
        # Front wall
        front = (
            cq.Workplane("XY")
            .box(base_w, t, wall_h)
            .translate((0, -base_d / 2 + t / 2, wall_h / 2 + t / 2))
        )
        # Back wall
        back = (
            cq.Workplane("XY")
            .box(base_w, t, wall_h)
            .translate((0, base_d / 2 - t / 2, wall_h / 2 + t / 2))
        )
        # Left wall
        left = (
            cq.Workplane("XY")
            .box(t, base_d - 2 * t, wall_h)
            .translate((-base_w / 2 + t / 2, 0, wall_h / 2 + t / 2))
        )
        # Right wall
        right = (
            cq.Workplane("XY")
            .box(t, base_d - 2 * t, wall_h)
            .translate((base_w / 2 - t / 2, 0, wall_h / 2 + t / 2))
        )

        result = base.union(front).union(back).union(left).union(right)

        # Mounting holes in base
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
        wall_h = extra.get("wall_height", 30)
        return (
            f"{mat.name} Box Enclosure {params.width_mm:.0f}x{params.height_mm:.0f}mm "
            f"{wall_h:.0f}mm Walls"
        )

    def part_description(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        import json
        mat = get_material(params.material_slug)
        extra = json.loads(params.extra) if params.extra else {}
        wall_h = extra.get("wall_height", 30)
        return (
            f"Sheet metal {mat.name.lower()} open-top box enclosure, "
            f"{params.width_mm:.0f}x{params.height_mm:.0f}mm base, "
            f"{wall_h:.0f}mm walls, {params.thickness_mm}mm thick."
        )
