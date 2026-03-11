# pipeline/categories/electronics_panel.py
"""Electronics panel generator — enclosure panels and DIN rail mount plates."""
from typing import Iterator

import cadquery as cq

from pipeline.materials import MATERIALS
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


PANEL_SIZES = [(100, 80), (120, 100), (150, 120), (200, 150), (250, 200)]
PANEL_HOLE_CONFIGS = [
    ("M3", 2, 2),
    ("M3", 2, 3),
    ("M3", 2, 4),
    ("M3", 3, 4),
    ("M4", 2, 2),
    ("M4", 2, 3),
    ("M5", 2, 2),
    ("M5", 2, 3),
]

DIN_RAIL_LENGTHS = [100, 150, 200, 250]
DIN_RAIL_WIDTH = 45


def _grid_holes(w, h, label, rows, cols, margin=10.0):
    dia = METRIC_CLEARANCE[label]
    holes = []
    for r in range(rows):
        y = -h/2 + margin + (h - 2*margin) * r / max(1, rows - 1) if rows > 1 else 0
        for c in range(cols):
            x = -w/2 + margin + (w - 2*margin) * c / max(1, cols - 1) if cols > 1 else 0
            holes.append(HoleSpec(label, dia, round(x, 2), round(y, 2)))
    return tuple(holes)


class ElectronicsPanelGenerator(PartGenerator):
    category = "electronics_panel"

    def enumerate_variants(self) -> Iterator[PartParams]:
        for mat_slug, mat in MATERIALS.items():
            for thickness in mat.thicknesses_mm:
                for w, h in PANEL_SIZES:
                    for label, rows, cols in PANEL_HOLE_CONFIGS:
                        dia = METRIC_CLEARANCE[label]
                        if dia < mat.min_feature_size_mm:
                            continue
                        holes = _grid_holes(w, h, label, rows, cols)
                        yield PartParams(
                            category=self.category,
                            shape="panel",
                            width_mm=w,
                            height_mm=h,
                            thickness_mm=thickness,
                            material_slug=mat_slug,
                            hole_specs=holes,
                        )

                for length in DIN_RAIL_LENGTHS:
                    for mount_label in ["M4", "M5", "M6"]:
                        dia = METRIC_CLEARANCE[mount_label]
                        if dia < mat.min_feature_size_mm:
                            continue
                        margin = 10.0
                        holes = (
                            HoleSpec(mount_label, dia, round(-(length/2 - margin), 2), round(-(DIN_RAIL_WIDTH/2 - margin), 2)),
                            HoleSpec(mount_label, dia, round(length/2 - margin, 2), round(-(DIN_RAIL_WIDTH/2 - margin), 2)),
                            HoleSpec(mount_label, dia, round(-(length/2 - margin), 2), round(DIN_RAIL_WIDTH/2 - margin, 2)),
                            HoleSpec(mount_label, dia, round(length/2 - margin, 2), round(DIN_RAIL_WIDTH/2 - margin, 2)),
                        )
                        yield PartParams(
                            category=self.category,
                            shape="din_rail",
                            width_mm=length,
                            height_mm=DIN_RAIL_WIDTH,
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
        shape_name = {"panel": "Electronics Panel", "din_rail": "DIN Rail Mount Plate"}[params.shape]
        return f"{mat.name} {shape_name} {params.width_mm:.0f}x{params.height_mm:.0f}mm"

    def part_description(self, params: PartParams) -> str:
        mat = MATERIALS[params.material_slug]
        return (
            f"Laser-cut {mat.name.lower()} {params.shape.replace('_', ' ')}, "
            f"{params.width_mm:.0f}x{params.height_mm:.0f}x{params.thickness_mm}mm, "
            f"with {params.hole_count} holes."
        )
