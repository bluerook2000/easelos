# pipeline/categories/hinge.py
"""Hinge generator — piano-style and butt hinges."""
from typing import Iterator

import cadquery as cq

from pipeline.materials import get_laser_cut_materials
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


# Piano hinge: long rectangle with knuckle holes along one edge
PIANO_SIZES = [
    (100, 25),  # 100mm long, 25mm wide (per leaf)
    (150, 30),
    (200, 35),
    (250, 40),
]

# Butt hinge: square-ish leaves
BUTT_SIZES = [
    (40, 30),
    (50, 40),
    (60, 50),
    (75, 60),
    (100, 75),
]

HINGE_HOLES = [
    ("M3", 3),
    ("M4", 4),
    ("M5", 4),
    ("M4", 6),
]


def _hinge_holes(w: float, h: float, count: int, label: str) -> tuple[HoleSpec, ...]:
    """Place holes in a hinge leaf pattern."""
    dia = METRIC_CLEARANCE[label]
    margin = 8.0
    holes = []
    if count <= 2:
        # Two holes centered vertically, spaced along length
        x_off = (w / 2) - margin
        holes = [
            HoleSpec(label, dia, -x_off, 0),
            HoleSpec(label, dia, x_off, 0),
        ]
    else:
        cols = 2
        rows = count // cols
        x_off = (w / 2) - margin
        y_off = (h / 2) - margin
        for r in range(rows):
            y = -y_off + (2 * y_off * r / max(1, rows - 1)) if rows > 1 else 0
            for c in range(cols):
                x = -x_off + (2 * x_off * c / max(1, cols - 1)) if cols > 1 else 0
                holes.append(HoleSpec(label, dia, round(x, 2), round(y, 2)))
    return tuple(holes[:count])


class HingeGenerator(PartGenerator):
    category = "hinge"
    manufacturing_type = "laser_cut"

    def enumerate_variants(self) -> Iterator[PartParams]:
        materials = get_laser_cut_materials()
        for mat_slug, mat in materials.items():
            for thickness in mat.thicknesses_mm:
                # Piano hinges
                for w, h in PIANO_SIZES:
                    for label, count in [("M3", 4), ("M4", 6)]:
                        dia = METRIC_CLEARANCE[label]
                        if dia < mat.min_feature_size_mm:
                            continue
                        holes = _hinge_holes(w, h, count, label)
                        yield PartParams(
                            category=self.category,
                            shape="piano",
                            width_mm=w,
                            height_mm=h,
                            thickness_mm=thickness,
                            material_slug=mat_slug,
                            hole_specs=holes,
                        )

                # Butt hinges
                for w, h in BUTT_SIZES:
                    for label, count in HINGE_HOLES:
                        dia = METRIC_CLEARANCE[label]
                        if dia < mat.min_feature_size_mm:
                            continue
                        if dia * 2 > min(w, h):
                            continue
                        holes = _hinge_holes(w, h, count, label)
                        yield PartParams(
                            category=self.category,
                            shape="butt",
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
        from pipeline.materials import get_material
        mat = get_material(params.material_slug)
        shape = "Piano Hinge" if params.shape == "piano" else "Butt Hinge"
        hole_desc = f"{params.hole_count}x{params.hole_specs[0].label}" if params.hole_specs else "No Holes"
        return f"{mat.name} {shape} {params.width_mm:.0f}x{params.height_mm:.0f}mm {hole_desc}"

    def part_description(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        mat = get_material(params.material_slug)
        shape = "piano-style" if params.shape == "piano" else "butt"
        return (
            f"Laser-cut {mat.name.lower()} {shape} hinge leaf, "
            f"{params.width_mm:.0f}x{params.height_mm:.0f}x{params.thickness_mm}mm, "
            f"with {params.hole_count} mounting holes."
        )
