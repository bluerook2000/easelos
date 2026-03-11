# pipeline/categories/base_plate.py
"""Base/chassis plate generator with mounting hole grids."""
from typing import Iterator

import cadquery as cq

from pipeline.materials import MATERIALS
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


PLATE_SIZES = [
    (80, 60),
    (100, 80),
    (120, 80),
    (150, 100),
    (200, 150),
]

GRID_CONFIGS = [
    # (hole_label, grid_rows, grid_cols)
    ("M3", 2, 3),
    ("M4", 3, 4),
    ("M5", 2, 3),
    ("M5", 3, 4),
    ("M6", 2, 3),
]


def _grid_holes(w, h, label, rows, cols, margin=10.0):
    dia = METRIC_CLEARANCE[label]
    holes = []
    for r in range(rows):
        y = -h/2 + margin + (h - 2*margin) * r / max(1, rows - 1) if rows > 1 else 0
        for c in range(cols):
            x = -w/2 + margin + (w - 2*margin) * c / max(1, cols - 1) if cols > 1 else 0
            holes.append(HoleSpec(label, dia, round(x, 2), round(y, 2)))
    return tuple(holes)


class BasePlateGenerator(PartGenerator):
    category = "base_plate"

    def enumerate_variants(self) -> Iterator[PartParams]:
        for mat_slug, mat in MATERIALS.items():
            for thickness in mat.thicknesses_mm:
                for w, h in PLATE_SIZES:
                    for label, rows, cols in GRID_CONFIGS:
                        dia = METRIC_CLEARANCE[label]
                        if dia < mat.min_feature_size_mm:
                            continue
                        holes = _grid_holes(w, h, label, rows, cols)
                        yield PartParams(
                            category=self.category,
                            shape="grid",
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
        return f"{mat.name} Base Plate {params.width_mm:.0f}x{params.height_mm:.0f}mm {params.hole_count}-hole grid"

    def part_description(self, params: PartParams) -> str:
        mat = MATERIALS[params.material_slug]
        return (
            f"Laser-cut {mat.name.lower()} base plate with {params.hole_count}-hole mounting grid, "
            f"{params.width_mm:.0f}x{params.height_mm:.0f}x{params.thickness_mm}mm."
        )
