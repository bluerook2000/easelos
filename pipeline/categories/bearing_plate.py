# pipeline/categories/bearing_plate.py
"""Bearing plate generator — 608 and 6201 bearing mount plates."""
from typing import Iterator

import cadquery as cq

from pipeline.materials import MATERIALS
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


BEARING_SPECS = {
    "608_mount": {
        "bore_mm": 22.0,
        "plate_sizes": [(40, 40), (50, 50), (60, 60)],
        "mount_holes": ["M4", "M5"],
    },
    "6201_mount": {
        "bore_mm": 32.0,
        "plate_sizes": [(50, 50), (60, 60), (70, 70)],
        "mount_holes": ["M5", "M6"],
    },
    "6202_mount": {
        "bore_mm": 35.0,
        "plate_sizes": [(55, 55), (65, 65), (75, 75)],
        "mount_holes": ["M5", "M6"],
    },
    "6203_mount": {
        "bore_mm": 40.0,
        "plate_sizes": [(60, 60), (70, 70), (80, 80)],
        "mount_holes": ["M5", "M6"],
    },
}


class BearingPlateGenerator(PartGenerator):
    category = "bearing_plate"

    def enumerate_variants(self) -> Iterator[PartParams]:
        for mat_slug, mat in MATERIALS.items():
            for thickness in mat.thicknesses_mm:
                for bearing_name, spec in BEARING_SPECS.items():
                    bore = spec["bore_mm"]
                    for pw, ph in spec["plate_sizes"]:
                        for mount_label in spec["mount_holes"]:
                            m_dia = METRIC_CLEARANCE[mount_label]
                            if m_dia < mat.min_feature_size_mm:
                                continue
                            margin = 8.0
                            holes = (
                                HoleSpec("bore", bore, 0, 0),
                                HoleSpec(mount_label, m_dia, round(-(pw/2 - margin), 2), round(-(ph/2 - margin), 2)),
                                HoleSpec(mount_label, m_dia, round(pw/2 - margin, 2), round(-(ph/2 - margin), 2)),
                                HoleSpec(mount_label, m_dia, round(-(pw/2 - margin), 2), round(ph/2 - margin, 2)),
                                HoleSpec(mount_label, m_dia, round(pw/2 - margin, 2), round(ph/2 - margin, 2)),
                            )
                            yield PartParams(
                                category=self.category,
                                shape=bearing_name,
                                width_mm=pw,
                                height_mm=ph,
                                thickness_mm=thickness,
                                material_slug=mat_slug,
                                hole_specs=holes,
                            )

    def generate_solid(self, params: PartParams) -> cq.Workplane:
        result = (
            cq.Workplane("XY")
            .rect(params.width_mm, params.height_mm)
            .extrude(params.thickness_mm)
        )
        bore_holes = [h for h in params.hole_specs if h.label == "bore"]
        if bore_holes:
            result = result.faces(">Z").workplane().hole(bore_holes[0].diameter_mm)
        mount_holes = [h for h in params.hole_specs if h.label != "bore"]
        if mount_holes:
            result = (
                result.faces(">Z").workplane()
                .pushPoints([(h.x_mm, h.y_mm) for h in mount_holes])
                .hole(mount_holes[0].diameter_mm)
            )
        return result

    def part_name(self, params: PartParams) -> str:
        mat = MATERIALS[params.material_slug]
        bearing = params.shape.replace("_mount", "").upper()
        return f"{mat.name} {bearing} Bearing Plate {params.width_mm:.0f}x{params.height_mm:.0f}mm"

    def part_description(self, params: PartParams) -> str:
        mat = MATERIALS[params.material_slug]
        bearing = params.shape.replace("_mount", "").upper()
        return (
            f"Laser-cut {mat.name.lower()} {bearing} bearing mount plate, "
            f"{params.width_mm:.0f}x{params.height_mm:.0f}x{params.thickness_mm}mm, "
            f"with center bore and 4 mounting holes."
        )
