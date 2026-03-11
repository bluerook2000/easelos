# pipeline/categories/gusset_plate.py
"""Gusset plate generator — corner, T, and reinforcement gussets."""
from typing import Iterator

import cadquery as cq

from pipeline.materials import MATERIALS
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


GUSSET_SIZES = [
    (30, 30),
    (40, 40),
    (50, 50),
    (60, 60),
    (80, 80),
    (100, 100),
]

T_GUSSET_SIZES = [
    (40, 60),
    (50, 80),
    (60, 100),
]

HOLE_OPTIONS = [
    ("M4", 2),
    ("M5", 3),
    ("M5", 4),
    ("M6", 4),
    ("M8", 6),
]


def _gusset_holes(w, h, label, count, shape="corner", margin=8.0):
    """Place holes inside gusset profile."""
    dia = METRIC_CLEARANCE[label]
    if shape == "corner":
        cx, cy = -w/6, -h/6  # centroid of right triangle
        if count == 2:
            return (
                HoleSpec(label, dia, round(-(w/2 - margin), 2), round(-(h/2 - margin), 2)),
                HoleSpec(label, dia, round(cx, 2), round(cy, 2)),
            )
        elif count == 3:
            return (
                HoleSpec(label, dia, round(-(w/2 - margin), 2), round(-(h/2 - margin), 2)),
                HoleSpec(label, dia, round(w/2 - margin, 2), round(-(h/2 - margin), 2)),
                HoleSpec(label, dia, round(-(w/2 - margin), 2), round(0, 2)),
            )
        else:
            holes = [
                HoleSpec(label, dia, round(-(w/2 - margin), 2), round(-(h/2 - margin), 2)),
                HoleSpec(label, dia, round(0, 2), round(-(h/2 - margin), 2)),
                HoleSpec(label, dia, round(-(w/2 - margin), 2), round(0, 2)),
                HoleSpec(label, dia, round(cx, 2), round(cy, 2)),
            ]
            if count >= 6:
                holes.extend([
                    HoleSpec(label, dia, round(w/4 - margin, 2), round(-(h/2 - margin), 2)),
                    HoleSpec(label, dia, round(-(w/2 - margin), 2), round(h/4 - margin, 2)),
                ])
            return tuple(holes[:count])
    else:
        holes = []
        if count == 2:
            holes = [
                HoleSpec(label, dia, round(-(w/2 - margin), 2), 0),
                HoleSpec(label, dia, round(w/2 - margin, 2), 0),
            ]
        elif count >= 4:
            holes = [
                HoleSpec(label, dia, round(-(w/2 - margin), 2), round(-(h/2 - margin), 2)),
                HoleSpec(label, dia, round(w/2 - margin, 2), round(-(h/2 - margin), 2)),
                HoleSpec(label, dia, round(-(w/2 - margin), 2), round(h/2 - margin, 2)),
                HoleSpec(label, dia, round(w/2 - margin, 2), round(h/2 - margin, 2)),
            ]
            if count >= 6:
                holes.extend([
                    HoleSpec(label, dia, 0, round(-(h/2 - margin), 2)),
                    HoleSpec(label, dia, 0, round(h/2 - margin, 2)),
                ])
        return tuple(holes[:count])


class GussetPlateGenerator(PartGenerator):
    category = "gusset_plate"

    def enumerate_variants(self) -> Iterator[PartParams]:
        for mat_slug, mat in MATERIALS.items():
            for thickness in mat.thicknesses_mm:
                # Corner gussets (right-triangle profile)
                for w, h in GUSSET_SIZES:
                    for label, count in HOLE_OPTIONS:
                        dia = METRIC_CLEARANCE[label]
                        if dia < mat.min_feature_size_mm:
                            continue
                        if dia * 2 > min(w, h):
                            continue
                        holes = _gusset_holes(w, h, label, count, shape="corner")
                        yield PartParams(
                            category=self.category,
                            shape="corner",
                            width_mm=w,
                            height_mm=h,
                            thickness_mm=thickness,
                            material_slug=mat_slug,
                            hole_specs=holes,
                        )

                # T-gussets
                for w, h in T_GUSSET_SIZES:
                    for label, count in [("M5", 4), ("M6", 6)]:
                        dia = METRIC_CLEARANCE[label]
                        if dia < mat.min_feature_size_mm:
                            continue
                        holes = _gusset_holes(w, h, label, count, shape="t")
                        yield PartParams(
                            category=self.category,
                            shape="t",
                            width_mm=w,
                            height_mm=h,
                            thickness_mm=thickness,
                            material_slug=mat_slug,
                            hole_specs=holes,
                        )

    def generate_solid(self, params: PartParams) -> cq.Workplane:
        if params.shape == "corner":
            w, h = params.width_mm, params.height_mm
            result = (
                cq.Workplane("XY")
                .moveTo(-w/2, -h/2)
                .lineTo(w/2, -h/2)
                .lineTo(-w/2, h/2)
                .close()
                .extrude(params.thickness_mm)
            )
        else:
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
        shape = {"corner": "Corner Gusset", "t": "T-Gusset"}.get(params.shape, "Gusset")
        return f"{mat.name} {shape} {params.width_mm:.0f}x{params.height_mm:.0f}mm"

    def part_description(self, params: PartParams) -> str:
        mat = MATERIALS[params.material_slug]
        return (
            f"Laser-cut {mat.name.lower()} {params.shape} gusset plate, "
            f"{params.width_mm:.0f}x{params.height_mm:.0f}x{params.thickness_mm}mm."
        )
