# pipeline/categories/standoff.py
"""Standoff/spacer plate generator — round plates with center + mounting holes."""
import math
from typing import Iterator

import cadquery as cq

from pipeline.materials import MATERIALS
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


DIAMETERS = [15, 20, 25, 30, 40]
CENTER_HOLES = ["M3", "M4", "M5", "M6"]
OUTER_HOLE_COUNTS = [2, 4]


class StandoffGenerator(PartGenerator):
    category = "standoff"

    def enumerate_variants(self) -> Iterator[PartParams]:
        for mat_slug, mat in MATERIALS.items():
            for thickness in mat.thicknesses_mm:
                for diameter in DIAMETERS:
                    for center_label in CENTER_HOLES:
                        center_dia = METRIC_CLEARANCE[center_label]
                        if center_dia < mat.min_feature_size_mm:
                            continue
                        if center_dia >= diameter / 2:
                            continue  # center hole too big for disc

                        for outer_count in OUTER_HOLE_COUNTS:
                            outer_label = center_label
                            outer_dia = METRIC_CLEARANCE[outer_label]
                            r_mount = diameter * 0.3
                            if r_mount - outer_dia / 2 < 2:
                                continue

                            holes = [HoleSpec(center_label, center_dia, 0, 0)]
                            for i in range(outer_count):
                                angle = 2 * math.pi * i / outer_count
                                x = round(r_mount * math.cos(angle), 2)
                                y = round(r_mount * math.sin(angle), 2)
                                holes.append(HoleSpec(outer_label, outer_dia, x, y))

                            yield PartParams(
                                category=self.category,
                                shape="round",
                                width_mm=diameter,
                                height_mm=diameter,
                                thickness_mm=thickness,
                                material_slug=mat_slug,
                                hole_specs=tuple(holes),
                            )

    def generate_solid(self, params: PartParams) -> cq.Workplane:
        r = params.width_mm / 2
        result = cq.Workplane("XY").circle(r).extrude(params.thickness_mm)
        center = [h for h in params.hole_specs if h.x_mm == 0 and h.y_mm == 0]
        if center:
            result = result.faces(">Z").workplane().hole(center[0].diameter_mm)
        outer = [h for h in params.hole_specs if not (h.x_mm == 0 and h.y_mm == 0)]
        if outer:
            result = (
                result.faces(">Z").workplane()
                .pushPoints([(h.x_mm, h.y_mm) for h in outer])
                .hole(outer[0].diameter_mm)
            )
        return result

    def part_name(self, params: PartParams) -> str:
        mat = MATERIALS[params.material_slug]
        return f"{mat.name} Standoff Plate {params.width_mm:.0f}mm dia"

    def part_description(self, params: PartParams) -> str:
        mat = MATERIALS[params.material_slug]
        return (
            f"Laser-cut {mat.name.lower()} round standoff plate, "
            f"{params.width_mm:.0f}mm diameter x {params.thickness_mm}mm, "
            f"with {params.hole_count} holes."
        )
