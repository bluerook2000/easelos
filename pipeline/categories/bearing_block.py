# pipeline/categories/bearing_block.py
"""Bearing block generator — pillow block style with bore and mounting holes."""
from typing import Iterator

import cadquery as cq

from pipeline.materials import get_cnc_materials
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


# (bore_dia, base_width, base_length, height, bolt_size)
BEARING_SPECS = [
    (8, 30, 40, 20, "M4"),
    (10, 35, 45, 22, "M5"),
    (12, 40, 50, 25, "M5"),
    (15, 45, 55, 28, "M6"),
    (20, 55, 65, 32, "M6"),
    (25, 65, 80, 38, "M8"),
    (30, 75, 90, 42, "M8"),
]


class BearingBlockGenerator(PartGenerator):
    category = "bearing_block"
    manufacturing_type = "cnc_milled"

    def enumerate_variants(self) -> Iterator[PartParams]:
        materials = get_cnc_materials()
        for mat_slug, mat in materials.items():
            for bore, base_w, base_l, height, bolt_size in BEARING_SPECS:
                bolt_dia = METRIC_CLEARANCE[bolt_size]
                if bolt_dia < mat.min_feature_size_mm:
                    continue
                margin = 8.0
                x_off = (base_w / 2) - margin
                y_off = (base_l / 2) - margin
                holes = [
                    HoleSpec(bolt_size, bolt_dia, round(-x_off, 2), round(-y_off, 2)),
                    HoleSpec(bolt_size, bolt_dia, round(x_off, 2), round(-y_off, 2)),
                    HoleSpec(bolt_size, bolt_dia, round(-x_off, 2), round(y_off, 2)),
                    HoleSpec(bolt_size, bolt_dia, round(x_off, 2), round(y_off, 2)),
                ]
                yield PartParams(
                    category=self.category,
                    shape="pillow_block",
                    width_mm=base_w,
                    height_mm=base_l,
                    thickness_mm=height,
                    material_slug=mat_slug,
                    hole_specs=tuple(holes),
                    extra=f'{{"bore_dia": {bore}}}',
                )

    def generate_solid(self, params: PartParams) -> cq.Workplane:
        import json
        extra = json.loads(params.extra) if params.extra else {}
        bore = extra.get("bore_dia", 12)

        result = (
            cq.Workplane("XY")
            .rect(params.width_mm, params.height_mm)
            .extrude(params.thickness_mm)
        )
        # Center bore (through)
        result = result.faces(">Z").workplane().hole(bore)
        # Mounting holes (through)
        bolt_holes = list(params.hole_specs)
        if bolt_holes:
            result = (
                result.faces(">Z").workplane()
                .pushPoints([(h.x_mm, h.y_mm) for h in bolt_holes])
                .hole(bolt_holes[0].diameter_mm)
            )
        # Fillet top edges
        try:
            result = result.edges("|Z").fillet(1.0)
        except Exception:
            pass
        return result

    def part_name(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        import json
        mat = get_material(params.material_slug)
        extra = json.loads(params.extra) if params.extra else {}
        bore = extra.get("bore_dia", 12)
        return f"{mat.name} Bearing Block {bore}mm Bore"

    def part_description(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        import json
        mat = get_material(params.material_slug)
        extra = json.loads(params.extra) if params.extra else {}
        bore = extra.get("bore_dia", 12)
        return (
            f"CNC-milled {mat.name.lower()} pillow-block bearing housing, "
            f"{bore}mm bore, {params.width_mm:.0f}x{params.height_mm:.0f}mm base, "
            f"{params.thickness_mm:.0f}mm tall, with 4 mounting holes."
        )
