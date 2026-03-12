# pipeline/categories/flange.py
"""Flange generator — pipe and tube flanges with bolt circles."""
import math
from typing import Iterator

import cadquery as cq

from pipeline.materials import get_laser_cut_materials
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


PIPE_FLANGE_SPECS = [
    # (outer_dia_mm, inner_dia_mm, bolt_circle_mm, bolt_count, bolt_size)
    (60, 22, 45, 4, "M5"),
    (80, 28, 60, 4, "M6"),
    (100, 35, 75, 6, "M6"),
    (120, 42, 90, 6, "M8"),
    (150, 55, 115, 8, "M8"),
    (200, 75, 155, 8, "M8"),
]


def _bolt_circle_holes(bc_dia: float, count: int, label: str) -> tuple[HoleSpec, ...]:
    """Place holes evenly on a bolt circle."""
    dia = METRIC_CLEARANCE[label]
    radius = bc_dia / 2
    holes = []
    for i in range(count):
        angle = 2 * math.pi * i / count
        x = round(radius * math.cos(angle), 2)
        y = round(radius * math.sin(angle), 2)
        holes.append(HoleSpec(label, dia, x, y))
    return tuple(holes)


class FlangeGenerator(PartGenerator):
    category = "flange"
    manufacturing_type = "laser_cut"

    def enumerate_variants(self) -> Iterator[PartParams]:
        materials = get_laser_cut_materials()
        for mat_slug, mat in materials.items():
            for thickness in mat.thicknesses_mm:
                for od, id_, bc, bolt_count, bolt_size in PIPE_FLANGE_SPECS:
                    bolt_dia = METRIC_CLEARANCE[bolt_size]
                    if bolt_dia < mat.min_feature_size_mm:
                        continue
                    if id_ < mat.min_feature_size_mm:
                        continue
                    # Center bore + bolt circle holes
                    bolt_holes = _bolt_circle_holes(bc, bolt_count, bolt_size)
                    center_hole = HoleSpec("bore", id_, 0, 0)
                    all_holes = (center_hole,) + bolt_holes
                    yield PartParams(
                        category=self.category,
                        shape="pipe_flange",
                        width_mm=od,
                        height_mm=od,
                        thickness_mm=thickness,
                        material_slug=mat_slug,
                        hole_specs=all_holes,
                    )

    def generate_solid(self, params: PartParams) -> cq.Workplane:
        od = params.width_mm
        bore_holes = [h for h in params.hole_specs if h.label == "bore"]
        bolt_holes = [h for h in params.hole_specs if h.label != "bore"]

        result = (
            cq.Workplane("XY")
            .circle(od / 2)
            .extrude(params.thickness_mm)
        )
        # Bore hole
        if bore_holes:
            result = result.faces(">Z").workplane().hole(bore_holes[0].diameter_mm)
        # Bolt holes
        if bolt_holes:
            result = (
                result.faces(">Z").workplane()
                .pushPoints([(h.x_mm, h.y_mm) for h in bolt_holes])
                .hole(bolt_holes[0].diameter_mm)
            )
        return result

    def part_name(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        mat = get_material(params.material_slug)
        bolt_holes = [h for h in params.hole_specs if h.label != "bore"]
        hole_desc = f"{len(bolt_holes)}x{bolt_holes[0].label}" if bolt_holes else ""
        return f"{mat.name} Pipe Flange {params.width_mm:.0f}mm OD {hole_desc}"

    def part_description(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        mat = get_material(params.material_slug)
        bore_holes = [h for h in params.hole_specs if h.label == "bore"]
        bore_dia = bore_holes[0].diameter_mm if bore_holes else 0
        return (
            f"Laser-cut {mat.name.lower()} pipe flange, "
            f"{params.width_mm:.0f}mm OD x {bore_dia:.0f}mm bore, "
            f"{params.thickness_mm}mm thick, with {params.hole_count - 1} bolt holes."
        )
