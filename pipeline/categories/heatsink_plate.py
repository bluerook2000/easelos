# pipeline/categories/heatsink_plate.py
"""Heatsink plate generator — finned plates for thermal management."""
from typing import Iterator

import cadquery as cq

from pipeline.materials import get_laser_cut_materials
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


SIZES = [
    (40, 30), (50, 40), (60, 50), (80, 60), (100, 80), (120, 80),
]

MOUNT_HOLES = [
    ("M3", 2),
    ("M3", 4),
    ("M4", 4),
]


class HeatsinkPlateGenerator(PartGenerator):
    category = "heatsink_plate"
    manufacturing_type = "laser_cut"

    def enumerate_variants(self) -> Iterator[PartParams]:
        materials = get_laser_cut_materials()
        for mat_slug, mat in materials.items():
            if mat.category == "plastic":
                continue  # plastics are poor heat conductors
            for thickness in mat.thicknesses_mm:
                for w, h in SIZES:
                    for label, count in MOUNT_HOLES:
                        dia = METRIC_CLEARANCE[label]
                        if dia < mat.min_feature_size_mm:
                            continue
                        margin = 6.0
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
                            for cx in [-x_off, x_off]:
                                for cy in [-y_off, y_off]:
                                    holes.append(HoleSpec(label, dia, round(cx, 2), round(cy, 2)))
                        yield PartParams(
                            category=self.category,
                            shape="finned",
                            width_mm=w,
                            height_mm=h,
                            thickness_mm=thickness,
                            material_slug=mat_slug,
                            hole_specs=tuple(holes[:count]),
                        )

    def generate_solid(self, params: PartParams) -> cq.Workplane:
        result = (
            cq.Workplane("XY")
            .rect(params.width_mm, params.height_mm)
            .extrude(params.thickness_mm)
        )
        # Add mounting holes
        if params.hole_specs:
            result = (
                result.faces(">Z").workplane()
                .pushPoints([(h.x_mm, h.y_mm) for h in params.hole_specs])
                .hole(params.hole_specs[0].diameter_mm)
            )
        # Add fin slots (parallel cuts along the length)
        fin_width = 2.0  # slot width
        fin_spacing = 4.0  # center-to-center
        num_fins = int((params.height_mm - 16) / fin_spacing)
        slot_length = params.width_mm - 20  # leave material at ends
        if num_fins > 1 and slot_length > 5:
            start_y = -(num_fins - 1) * fin_spacing / 2
            for i in range(num_fins):
                y = start_y + i * fin_spacing
                try:
                    result = (
                        cq.Workplane("XY")
                        .add(result)
                        .workplane()
                        .center(0, y)
                        .slot2D(slot_length, fin_width, 0)
                        .cutThruAll()
                    )
                except Exception:
                    pass  # Skip slot if geometry fails
        return result

    def part_name(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        mat = get_material(params.material_slug)
        return f"{mat.name} Heatsink Plate {params.width_mm:.0f}x{params.height_mm:.0f}mm"

    def part_description(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        mat = get_material(params.material_slug)
        return (
            f"Laser-cut {mat.name.lower()} heatsink plate with fin slots, "
            f"{params.width_mm:.0f}x{params.height_mm:.0f}x{params.thickness_mm}mm, "
            f"for passive thermal management."
        )
