# pipeline/categories/enclosure_panel.py
"""Enclosure panel generator — front/rear panels with cutouts."""
from typing import Iterator

import cadquery as cq

from pipeline.materials import get_laser_cut_materials
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


PANEL_SIZES = [
    (100, 60), (120, 80), (150, 100), (200, 120), (250, 150), (300, 200),
]

MOUNT_HOLES = [
    ("M3", 4),
    ("M4", 4),
    ("M4", 6),
]


class EnclosurePanelGenerator(PartGenerator):
    category = "enclosure_panel"
    manufacturing_type = "laser_cut"

    def enumerate_variants(self) -> Iterator[PartParams]:
        materials = get_laser_cut_materials()
        for mat_slug, mat in materials.items():
            for thickness in mat.thicknesses_mm:
                for w, h in PANEL_SIZES:
                    for label, count in MOUNT_HOLES:
                        dia = METRIC_CLEARANCE[label]
                        if dia < mat.min_feature_size_mm:
                            continue
                        margin = 6.0
                        holes = []
                        x_off = (w / 2) - margin
                        y_off = (h / 2) - margin
                        if count == 4:
                            for cx in [-x_off, x_off]:
                                for cy in [-y_off, y_off]:
                                    holes.append(HoleSpec(label, dia, round(cx, 2), round(cy, 2)))
                        else:
                            for r in range(3):
                                y = -y_off + y_off * r
                                for c in range(2):
                                    x = -x_off + 2 * x_off * c
                                    holes.append(HoleSpec(label, dia, round(x, 2), round(y, 2)))
                        yield PartParams(
                            category=self.category,
                            shape="front_panel",
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
        if params.hole_specs:
            result = (
                result.faces(">Z").workplane()
                .pushPoints([(h.x_mm, h.y_mm) for h in params.hole_specs])
                .hole(params.hole_specs[0].diameter_mm)
            )
        return result

    def part_name(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        mat = get_material(params.material_slug)
        hole_desc = f"{params.hole_count}x{params.hole_specs[0].label}" if params.hole_specs else ""
        return f"{mat.name} Enclosure Panel {params.width_mm:.0f}x{params.height_mm:.0f}mm {hole_desc}"

    def part_description(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        mat = get_material(params.material_slug)
        return (
            f"Laser-cut {mat.name.lower()} enclosure panel, "
            f"{params.width_mm:.0f}x{params.height_mm:.0f}x{params.thickness_mm}mm, "
            f"with {params.hole_count} corner mounting holes."
        )
