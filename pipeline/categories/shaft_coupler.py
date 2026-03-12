# pipeline/categories/shaft_coupler.py
"""Shaft coupler generator — rigid cylindrical couplers."""
from typing import Iterator

import cadquery as cq

from pipeline.materials import get_cnc_materials
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


# (outer_dia, length, bore1, bore2)
COUPLER_SPECS = [
    (15, 20, 5, 5),
    (18, 25, 5, 8),
    (20, 25, 6.35, 6.35),
    (20, 30, 6.35, 8),
    (22, 30, 8, 8),
    (25, 30, 8, 10),
    (25, 35, 10, 10),
    (30, 40, 10, 10),
    (35, 40, 10, 12),
    (40, 50, 12, 12),
]


class ShaftCouplerGenerator(PartGenerator):
    category = "shaft_coupler"
    manufacturing_type = "cnc_milled"

    def enumerate_variants(self) -> Iterator[PartParams]:
        materials = get_cnc_materials()
        for mat_slug, mat in materials.items():
            for od, length, bore1, bore2 in COUPLER_SPECS:
                # Set screw holes — M3 or M4 depending on OD
                set_screw = "M3" if od <= 20 else "M4"
                set_dia = METRIC_CLEARANCE[set_screw]
                if set_dia < mat.min_feature_size_mm:
                    continue
                # Two set screw holes (one per shaft)
                holes = (
                    HoleSpec(set_screw, set_dia, round(od / 2, 2), round(-length / 4, 2)),
                    HoleSpec(set_screw, set_dia, round(od / 2, 2), round(length / 4, 2)),
                )
                # Use width_mm=od, height_mm=length (cylindrical)
                yield PartParams(
                    category=self.category,
                    shape="rigid_coupler",
                    width_mm=od,
                    height_mm=length,
                    thickness_mm=od,  # for cylindrical parts, use OD
                    material_slug=mat_slug,
                    hole_specs=holes,
                    extra=f'{{"bore1": {bore1}, "bore2": {bore2}}}',
                )

    def generate_solid(self, params: PartParams) -> cq.Workplane:
        import json
        extra = json.loads(params.extra) if params.extra else {}
        bore1 = extra.get("bore1", 5)
        bore2 = extra.get("bore2", 5)
        od = params.width_mm
        length = params.height_mm

        # Main cylinder
        result = cq.Workplane("XY").circle(od / 2).extrude(length)

        # Bore 1 from bottom (half depth)
        result = (
            result.faces("<Z").workplane()
            .hole(bore1, length / 2)
        )
        # Bore 2 from top (half depth)
        result = (
            result.faces(">Z").workplane()
            .hole(bore2, length / 2)
        )

        # Chamfer outer edges after bores — best effort
        try:
            result = result.edges("%CIRCLE").chamfer(0.3)
        except Exception:
            pass

        return result

    def part_name(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        import json
        mat = get_material(params.material_slug)
        extra = json.loads(params.extra) if params.extra else {}
        bore1 = extra.get("bore1", 5)
        bore2 = extra.get("bore2", 5)
        return f"{mat.name} Shaft Coupler {bore1}mm to {bore2}mm OD{params.width_mm:.0f}mm"

    def part_description(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        import json
        mat = get_material(params.material_slug)
        extra = json.loads(params.extra) if params.extra else {}
        bore1 = extra.get("bore1", 5)
        bore2 = extra.get("bore2", 5)
        return (
            f"CNC-milled {mat.name.lower()} rigid shaft coupler, "
            f"{bore1}mm to {bore2}mm bore, {params.width_mm:.0f}mm OD, "
            f"{params.height_mm:.0f}mm long, with set screw holes."
        )
