# pipeline/categories/cable_bracket.py
"""Cable bracket generator — clip and guide brackets for cable management."""
from typing import Iterator

import cadquery as cq

from pipeline.materials import MATERIALS
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


CLIP_SIZES = [(25, 15), (30, 20), (35, 22), (40, 25), (50, 30)]
GUIDE_SIZES = [(60, 30), (80, 40), (100, 50), (120, 60)]
MOUNT_OPTIONS = ["M3", "M4", "M5", "M6"]
MOUNT_COUNTS = [2, 4]


class CableBracketGenerator(PartGenerator):
    category = "cable_bracket"

    def enumerate_variants(self) -> Iterator[PartParams]:
        for mat_slug, mat in MATERIALS.items():
            for thickness in mat.thicknesses_mm:
                # Clip brackets
                for w, h in CLIP_SIZES:
                    for mount_label in MOUNT_OPTIONS:
                        m_dia = METRIC_CLEARANCE[mount_label]
                        if m_dia < mat.min_feature_size_mm:
                            continue
                        margin = 5.0
                        holes = (
                            HoleSpec(mount_label, m_dia, round(-(w/2 - margin), 2), 0),
                            HoleSpec(mount_label, m_dia, round(w/2 - margin, 2), 0),
                        )
                        yield PartParams(
                            category=self.category,
                            shape="clip",
                            width_mm=w,
                            height_mm=h,
                            thickness_mm=thickness,
                            material_slug=mat_slug,
                            hole_specs=holes,
                        )

                # Guide brackets
                for w, h in GUIDE_SIZES:
                    for mount_label in MOUNT_OPTIONS:
                        for mount_count in MOUNT_COUNTS:
                            m_dia = METRIC_CLEARANCE[mount_label]
                            if m_dia < mat.min_feature_size_mm:
                                continue
                            margin = 8.0
                            if mount_count == 2:
                                holes = (
                                    HoleSpec(mount_label, m_dia, round(-(w/2 - margin), 2), round(-(h/2 - margin), 2)),
                                    HoleSpec(mount_label, m_dia, round(w/2 - margin, 2), round(-(h/2 - margin), 2)),
                                )
                            else:
                                holes = (
                                    HoleSpec(mount_label, m_dia, round(-(w/2 - margin), 2), round(-(h/2 - margin), 2)),
                                    HoleSpec(mount_label, m_dia, round(w/2 - margin, 2), round(-(h/2 - margin), 2)),
                                    HoleSpec(mount_label, m_dia, round(-(w/2 - margin), 2), round(h/2 - margin, 2)),
                                    HoleSpec(mount_label, m_dia, round(w/2 - margin, 2), round(h/2 - margin, 2)),
                                )
                            yield PartParams(
                                category=self.category,
                                shape="guide",
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
        if params.hole_specs:
            result = (
                result.faces(">Z").workplane()
                .pushPoints([(h.x_mm, h.y_mm) for h in params.hole_specs])
                .hole(params.hole_specs[0].diameter_mm)
            )
        return result

    def part_name(self, params: PartParams) -> str:
        mat = MATERIALS[params.material_slug]
        shape_name = {"clip": "Cable Clip", "guide": "Cable Guide"}[params.shape]
        return f"{mat.name} {shape_name} {params.width_mm:.0f}x{params.height_mm:.0f}mm"

    def part_description(self, params: PartParams) -> str:
        mat = MATERIALS[params.material_slug]
        return (
            f"Laser-cut {mat.name.lower()} cable {params.shape} bracket, "
            f"{params.width_mm:.0f}x{params.height_mm:.0f}x{params.thickness_mm}mm, "
            f"with {params.hole_count} mounting holes."
        )
