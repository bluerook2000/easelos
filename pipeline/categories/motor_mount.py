# pipeline/categories/motor_mount.py
"""Motor mount generator — NEMA 17, 23, 34 mounting plates."""
from typing import Iterator

import cadquery as cq

from pipeline.materials import MATERIALS
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


# NEMA motor specs: (frame_mm, bolt_circle_mm, pilot_hole_mm, bolt_size)
NEMA_SPECS = {
    "nema17": {
        "frame_mm": 42.3,
        "bolt_circle_mm": 31.0,
        "pilot_diameter_mm": 22.0,
        "bolt_size": "M3",
        "plate_sizes": [(50, 50), (55, 55), (60, 60)],
    },
    "nema23": {
        "frame_mm": 57.2,
        "bolt_circle_mm": 47.1,
        "pilot_diameter_mm": 38.1,
        "bolt_size": "M5",
        "plate_sizes": [(65, 65), (70, 70), (80, 80)],
    },
    "nema34": {
        "frame_mm": 86.4,
        "bolt_circle_mm": 69.6,
        "pilot_diameter_mm": 73.0,
        "bolt_size": "M5",
        "plate_sizes": [(95, 95), (100, 100), (110, 110)],
    },
}


class MotorMountGenerator(PartGenerator):
    category = "motor_mount"

    def enumerate_variants(self) -> Iterator[PartParams]:
        for material_slug, material in MATERIALS.items():
            for thickness in material.thicknesses_mm:
                for nema_name, spec in NEMA_SPECS.items():
                    bolt_size = spec["bolt_size"]
                    bolt_dia = METRIC_CLEARANCE[bolt_size]
                    if bolt_dia < material.min_feature_size_mm:
                        continue

                    bc = spec["bolt_circle_mm"] / 2

                    for pw, ph in spec["plate_sizes"]:
                        # 4 mounting holes at bolt circle corners + center pilot
                        holes = (
                            HoleSpec(bolt_size, bolt_dia, round(-bc / 1.414, 2), round(-bc / 1.414, 2)),
                            HoleSpec(bolt_size, bolt_dia, round(bc / 1.414, 2), round(-bc / 1.414, 2)),
                            HoleSpec(bolt_size, bolt_dia, round(bc / 1.414, 2), round(bc / 1.414, 2)),
                            HoleSpec(bolt_size, bolt_dia, round(-bc / 1.414, 2), round(bc / 1.414, 2)),
                            HoleSpec("pilot", spec["pilot_diameter_mm"], 0, 0),
                        )
                        yield PartParams(
                            category=self.category,
                            shape=nema_name,
                            width_mm=pw,
                            height_mm=ph,
                            thickness_mm=thickness,
                            material_slug=material_slug,
                            hole_specs=holes,
                        )

    def generate_solid(self, params: PartParams) -> cq.Workplane:
        """Generate motor mount plate with bolt holes and center pilot hole."""
        result = (
            cq.Workplane("XY")
            .rect(params.width_mm, params.height_mm)
            .extrude(params.thickness_mm)
        )
        # Add mounting bolt holes
        mounting_holes = [h for h in params.hole_specs if h.label != "pilot"]
        if mounting_holes:
            result = (
                result.faces(">Z").workplane()
                .pushPoints([(h.x_mm, h.y_mm) for h in mounting_holes])
                .hole(mounting_holes[0].diameter_mm)
            )
        # Add pilot hole
        pilot_holes = [h for h in params.hole_specs if h.label == "pilot"]
        if pilot_holes:
            result = (
                result.faces(">Z").workplane()
                .pushPoints([(h.x_mm, h.y_mm) for h in pilot_holes])
                .hole(pilot_holes[0].diameter_mm)
            )
        return result

    def part_name(self, params: PartParams) -> str:
        material = MATERIALS[params.material_slug]
        nema_label = params.shape.upper().replace("NEMA", "NEMA ")
        return (
            f"{material.name} {nema_label} Motor Mount "
            f"{params.width_mm:.0f}x{params.height_mm:.0f}mm"
        )

    def part_description(self, params: PartParams) -> str:
        material = MATERIALS[params.material_slug]
        return (
            f"Laser-cut {material.name.lower()} {params.shape.upper()} motor mount plate, "
            f"{params.width_mm:.0f}x{params.height_mm:.0f}x{params.thickness_mm}mm, "
            f"with 4 bolt holes and center pilot hole."
        )
