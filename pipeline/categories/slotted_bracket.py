# pipeline/categories/slotted_bracket.py
"""Slotted bracket generator — brackets with adjustment slots."""
from typing import Iterator

import cadquery as cq

from pipeline.materials import get_laser_cut_materials
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


SIZES = [
    (40, 25), (50, 30), (60, 40), (80, 50), (100, 60),
]

SLOT_CONFIGS = [
    # (slot_size_label, slot_count, slot_length_mm)
    ("M4", 2, 12),
    ("M5", 2, 15),
    ("M5", 4, 15),
    ("M6", 2, 18),
    ("M6", 4, 18),
]


class SlottedBracketGenerator(PartGenerator):
    category = "slotted_bracket"
    manufacturing_type = "laser_cut"

    def enumerate_variants(self) -> Iterator[PartParams]:
        materials = get_laser_cut_materials()
        for mat_slug, mat in materials.items():
            for thickness in mat.thicknesses_mm:
                for w, h in SIZES:
                    for label, count, slot_len in SLOT_CONFIGS:
                        dia = METRIC_CLEARANCE[label]
                        if dia < mat.min_feature_size_mm:
                            continue
                        if slot_len > min(w, h) - 16:
                            continue
                        # Use HoleSpec to represent slot centers
                        margin = 8.0
                        holes = []
                        if count == 2:
                            x_off = (w / 2) - margin
                            holes = [
                                HoleSpec(label, dia, round(-x_off, 2), 0),
                                HoleSpec(label, dia, round(x_off, 2), 0),
                            ]
                        else:
                            x_off = (w / 2) - margin
                            y_off = (h / 2) - margin
                            for r in range(count // 2):
                                y = -y_off + (2 * y_off * r / max(1, count // 2 - 1)) if count > 2 else 0
                                for c in range(2):
                                    x = -x_off + (2 * x_off * c)
                                    holes.append(HoleSpec(label, dia, round(x, 2), round(y, 2)))
                        yield PartParams(
                            category=self.category,
                            shape="slotted_flat",
                            width_mm=w,
                            height_mm=h,
                            thickness_mm=thickness,
                            material_slug=mat_slug,
                            hole_specs=tuple(holes[:count]),
                            extra=f'{{"slot_length": {slot_len}}}',
                        )

    def generate_solid(self, params: PartParams) -> cq.Workplane:
        import json
        extra = json.loads(params.extra) if params.extra else {}
        slot_len = extra.get("slot_length", 15)

        result = (
            cq.Workplane("XY")
            .rect(params.width_mm, params.height_mm)
            .extrude(params.thickness_mm)
        )
        # Cut slots one at a time, avoiding faces(">Z") after cutThruAll
        if params.hole_specs:
            dia = params.hole_specs[0].diameter_mm
            for h in params.hole_specs:
                result = (
                    cq.Workplane("XY")
                    .add(result)
                    .workplane()
                    .center(h.x_mm, h.y_mm)
                    .slot2D(slot_len, dia, 0)
                    .cutThruAll()
                )
        return result

    def part_name(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        mat = get_material(params.material_slug)
        hole_desc = f"{params.hole_count}x{params.hole_specs[0].label}" if params.hole_specs else ""
        return f"{mat.name} Slotted Bracket {params.width_mm:.0f}x{params.height_mm:.0f}mm {hole_desc}"

    def part_description(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        mat = get_material(params.material_slug)
        return (
            f"Laser-cut {mat.name.lower()} slotted mounting bracket, "
            f"{params.width_mm:.0f}x{params.height_mm:.0f}x{params.thickness_mm}mm, "
            f"with {params.hole_count} adjustment slots for precise positioning."
        )
