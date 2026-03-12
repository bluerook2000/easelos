# pipeline/categories/motor_adapter.py
"""Motor adapter generator — thick plates with pilot bore and bolt pattern."""
from typing import Iterator
import math

import cadquery as cq

from pipeline.materials import get_cnc_materials
from pipeline.part_base import PartGenerator, PartParams, HoleSpec, METRIC_CLEARANCE


# (frame_size_mm, pilot_bore_mm, bolt_circle_mm, bolt_size, bolt_count, thickness)
NEMA_SPECS = [
    (42.3, 22, 31, "M3", 4, 6),     # NEMA 17
    (42.3, 22, 31, "M3", 4, 8),
    (42.3, 22, 31, "M3", 4, 10),
    (56.4, 38.1, 47.14, "M5", 4, 8),  # NEMA 23
    (56.4, 38.1, 47.14, "M5", 4, 10),
    (56.4, 38.1, 47.14, "M5", 4, 12),
    (86.4, 73, 69.58, "M5", 4, 10),  # NEMA 34
    (86.4, 73, 69.58, "M5", 4, 12),
    (86.4, 73, 69.58, "M5", 4, 15),
]


class MotorAdapterGenerator(PartGenerator):
    category = "motor_adapter"
    manufacturing_type = "cnc_milled"

    def enumerate_variants(self) -> Iterator[PartParams]:
        materials = get_cnc_materials()
        for mat_slug, mat in materials.items():
            for frame, pilot, bc, bolt_size, bolt_count, thickness in NEMA_SPECS:
                bolt_dia = METRIC_CLEARANCE[bolt_size]
                if bolt_dia < mat.min_feature_size_mm:
                    continue
                # Bolt circle holes
                holes = []
                radius = bc / 2
                for i in range(bolt_count):
                    angle = math.pi / 4 + 2 * math.pi * i / bolt_count  # 45 deg offset
                    x = round(radius * math.cos(angle), 2)
                    y = round(radius * math.sin(angle), 2)
                    holes.append(HoleSpec(bolt_size, bolt_dia, x, y))
                # Center pilot bore
                holes.append(HoleSpec("bore", pilot, 0, 0))
                yield PartParams(
                    category=self.category,
                    shape="nema_adapter",
                    width_mm=frame,
                    height_mm=frame,
                    thickness_mm=thickness,
                    material_slug=mat_slug,
                    hole_specs=tuple(holes),
                    extra=f'{{"pilot_bore": {pilot}, "pilot_depth": {thickness - 3}}}',
                )

    def generate_solid(self, params: PartParams) -> cq.Workplane:
        import json
        extra = json.loads(params.extra) if params.extra else {}
        pilot = extra.get("pilot_bore", 22)
        pilot_depth = extra.get("pilot_depth", params.thickness_mm - 3)

        result = (
            cq.Workplane("XY")
            .rect(params.width_mm, params.height_mm)
            .extrude(params.thickness_mm)
        )
        # Pilot bore pocket (not through)
        result = result.faces(">Z").workplane().hole(pilot, pilot_depth)
        # Bolt holes (through)
        bolt_holes = [h for h in params.hole_specs if h.label != "bore"]
        if bolt_holes:
            result = (
                result.faces(">Z").workplane()
                .pushPoints([(h.x_mm, h.y_mm) for h in bolt_holes])
                .hole(bolt_holes[0].diameter_mm)
            )
        # Chamfer outer vertical edges only — best effort
        try:
            result = result.edges("|Z").chamfer(0.3)
        except Exception:
            pass
        return result

    def part_name(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        mat = get_material(params.material_slug)
        nema = {42.3: "NEMA 17", 56.4: "NEMA 23", 86.4: "NEMA 34"}.get(
            params.width_mm, f"{params.width_mm:.0f}mm"
        )
        return f"{mat.name} {nema} Motor Adapter {params.thickness_mm:.0f}mm Thick"

    def part_description(self, params: PartParams) -> str:
        from pipeline.materials import get_material
        import json
        mat = get_material(params.material_slug)
        extra = json.loads(params.extra) if params.extra else {}
        pilot = extra.get("pilot_bore", 22)
        nema = {42.3: "NEMA 17", 56.4: "NEMA 23", 86.4: "NEMA 34"}.get(
            params.width_mm, f"{params.width_mm:.0f}mm frame"
        )
        return (
            f"CNC-milled {mat.name.lower()} {nema} motor adapter plate, "
            f"{params.thickness_mm:.0f}mm thick, {pilot:.0f}mm pilot bore, "
            f"with mounting bolt holes."
        )
