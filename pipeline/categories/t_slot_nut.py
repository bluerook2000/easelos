# pipeline/categories/t_slot_nut.py
"""T-slot nut generator — drop-in nuts for aluminum extrusion framing."""
from typing import Iterator

import cadquery as cq

from pipeline.materials import get_cnc_materials
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


# (series, nut_width, nut_length, nut_height, thread_size)
TNUT_SPECS = [
    (20, 11, 10, 5, "M3"),
    (20, 11, 10, 5, "M4"),
    (20, 11, 10, 5, "M5"),
    (30, 16, 15, 6, "M5"),
    (30, 16, 15, 6, "M6"),
    (30, 16, 15, 6, "M8"),
    (40, 21, 20, 8, "M6"),
    (40, 21, 20, 8, "M8"),
    (40, 21, 20, 8, "M10"),
]


class TSlotNutGenerator(PartGenerator):
    category = "t_slot_nut"
    manufacturing_type = "cnc_milled"

    def enumerate_variants(self) -> Iterator[PartParams]:
        materials = get_cnc_materials()
        for mat_slug, mat in materials.items():
            for series, nut_w, nut_l, nut_h, thread_size in TNUT_SPECS:
                thread_dia = METRIC_CLEARANCE[thread_size]
                if thread_dia < mat.min_feature_size_mm:
                    continue
                holes = (HoleSpec(thread_size, thread_dia, 0, 0),)
                yield PartParams(
                    category=self.category,
                    shape="t_nut",
                    width_mm=nut_w,
                    height_mm=nut_l,
                    thickness_mm=nut_h,
                    material_slug=mat_slug,
                    hole_specs=holes,
                    extra=f'{{"series": {series}}}',
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
        # Chamfer edges for easier insertion
        try:
            result = result.edges("|Z").chamfer(0.3)
        except Exception:
            pass
        return result

    def part_name(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        import json
        mat = get_material(params.material_slug)
        extra = json.loads(params.extra) if params.extra else {}
        series = extra.get("series", 20)
        thread = params.hole_specs[0].label if params.hole_specs else ""
        return f"{mat.name} {series}-Series T-Slot Nut {thread}"

    def part_description(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        import json
        mat = get_material(params.material_slug)
        extra = json.loads(params.extra) if params.extra else {}
        series = extra.get("series", 20)
        thread = params.hole_specs[0].label if params.hole_specs else ""
        return (
            f"CNC-milled {mat.name.lower()} drop-in T-slot nut for "
            f"{series}-series aluminum extrusion, {thread} thread, "
            f"{params.width_mm:.0f}x{params.height_mm:.0f}x{params.thickness_mm:.0f}mm."
        )
