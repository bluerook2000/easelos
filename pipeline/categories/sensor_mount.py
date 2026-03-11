# pipeline/categories/sensor_mount.py
"""Sensor mount generator — proximity sensor and limit switch mounts."""
from typing import Iterator

import cadquery as cq

from pipeline.materials import MATERIALS
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


PROXIMITY_SIZES = [(30, 20), (40, 25), (50, 30)]
LIMIT_SWITCH_SIZES = [(35, 20), (45, 25), (50, 30)]

SENSOR_HOLES = ["M3", "M4", "M5"]
MOUNT_HOLES = ["M3", "M4", "M5", "M6"]


class SensorMountGenerator(PartGenerator):
    category = "sensor_mount"

    def enumerate_variants(self) -> Iterator[PartParams]:
        for mat_slug, mat in MATERIALS.items():
            for thickness in mat.thicknesses_mm:
                # Proximity sensor mounts
                for w, h in PROXIMITY_SIZES:
                    for sensor_label in SENSOR_HOLES:
                        for mount_label in MOUNT_HOLES:
                            s_dia = METRIC_CLEARANCE[sensor_label]
                            m_dia = METRIC_CLEARANCE[mount_label]
                            if s_dia < mat.min_feature_size_mm or m_dia < mat.min_feature_size_mm:
                                continue
                            margin = 6.0
                            holes = (
                                HoleSpec(sensor_label, s_dia, round(-(w/4), 2), round(h/2 - margin, 2)),
                                HoleSpec(sensor_label, s_dia, round(w/4, 2), round(h/2 - margin, 2)),
                                HoleSpec(mount_label, m_dia, round(-(w/2 - margin), 2), round(-(h/2 - margin), 2)),
                                HoleSpec(mount_label, m_dia, round(w/2 - margin, 2), round(-(h/2 - margin), 2)),
                            )
                            yield PartParams(
                                category=self.category,
                                shape="proximity",
                                width_mm=w,
                                height_mm=h,
                                thickness_mm=thickness,
                                material_slug=mat_slug,
                                hole_specs=holes,
                            )

                # Limit switch mounts
                for w, h in LIMIT_SWITCH_SIZES:
                    for mount_label in MOUNT_HOLES:
                        m_dia = METRIC_CLEARANCE[mount_label]
                        # Use the smallest valid sensor hole for the material
                        sensor_label = None
                        for sl in SENSOR_HOLES:
                            if METRIC_CLEARANCE[sl] >= mat.min_feature_size_mm:
                                sensor_label = sl
                                break
                        if sensor_label is None:
                            continue
                        s_dia = METRIC_CLEARANCE[sensor_label]
                        if m_dia < mat.min_feature_size_mm:
                            continue
                        margin = 6.0
                        holes = (
                            HoleSpec(sensor_label, s_dia, round(-(w/4), 2), round(h/2 - margin, 2)),
                            HoleSpec(sensor_label, s_dia, round(w/4, 2), round(h/2 - margin, 2)),
                            HoleSpec(mount_label, m_dia, round(-(w/2 - margin), 2), round(-(h/2 - margin), 2)),
                            HoleSpec(mount_label, m_dia, round(w/2 - margin, 2), round(-(h/2 - margin), 2)),
                        )
                        yield PartParams(
                            category=self.category,
                            shape="limit_switch",
                            width_mm=w,
                            height_mm=h,
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
        by_dia = {}
        for h in params.hole_specs:
            by_dia.setdefault(h.diameter_mm, []).append(h)
        for dia, hole_group in by_dia.items():
            result = (
                result.faces(">Z").workplane()
                .pushPoints([(h.x_mm, h.y_mm) for h in hole_group])
                .hole(dia)
            )
        return result

    def part_name(self, params: PartParams) -> str:
        mat = MATERIALS[params.material_slug]
        shape_name = {"proximity": "Proximity Sensor Mount", "limit_switch": "Limit Switch Mount"}[params.shape]
        return f"{mat.name} {shape_name} {params.width_mm:.0f}x{params.height_mm:.0f}mm"

    def part_description(self, params: PartParams) -> str:
        mat = MATERIALS[params.material_slug]
        return (
            f"Laser-cut {mat.name.lower()} {params.shape.replace('_', ' ')} mount, "
            f"{params.width_mm:.0f}x{params.height_mm:.0f}x{params.thickness_mm}mm, "
            f"with {params.hole_count} holes."
        )
