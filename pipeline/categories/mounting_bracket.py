# pipeline/categories/mounting_bracket.py
"""Mounting bracket generator — flat, L, U, and angle brackets."""
import json
from typing import Iterator

import cadquery as cq

from pipeline.materials import MATERIALS
from pipeline.part_base import (
    PartGenerator,
    PartParams,
    HoleSpec,
    METRIC_CLEARANCE,
)


# Bracket dimension presets (width_mm, height_mm)
FLAT_SIZES = [
    (30, 20),
    (40, 25),
    (50, 30),
    (60, 40),
    (80, 50),
    (100, 60),
    (120, 80),
]

# L-bracket: flat pattern width = leg1 + leg2, height = bracket width
L_SIZES = [
    # (leg1, leg2, bracket_width) -> flat pattern (leg1+leg2, bracket_width)
    (25, 25, 20),
    (30, 30, 25),
    (40, 30, 30),
    (50, 40, 35),
    (60, 40, 40),
]

# Hole pattern presets: (hole_size_label, count)
HOLE_PATTERNS = [
    ("M3", 2),
    ("M4", 4),
    ("M5", 4),
    ("M5", 6),
    ("M6", 4),
    ("M8", 4),
]


def _distribute_holes(
    width_mm: float,
    height_mm: float,
    count: int,
    hole_label: str,
    edge_margin_mm: float = 8.0,
) -> tuple[HoleSpec, ...]:
    """Distribute holes in a grid pattern within the rectangle."""
    diameter = METRIC_CLEARANCE[hole_label]

    if count <= 0:
        return ()

    if count == 1:
        return (HoleSpec(hole_label, diameter, 0, 0),)

    if count == 2:
        x_off = (width_mm / 2) - edge_margin_mm
        return (
            HoleSpec(hole_label, diameter, -x_off, 0),
            HoleSpec(hole_label, diameter, x_off, 0),
        )

    # For 4+ holes, use a rectangular grid
    cols = 2
    rows = max(1, count // cols)
    remaining = count - (cols * rows)

    x_off = (width_mm / 2) - edge_margin_mm
    y_off = (height_mm / 2) - edge_margin_mm

    holes = []
    for r in range(rows):
        y = -y_off + (2 * y_off * r / max(1, rows - 1)) if rows > 1 else 0
        for c in range(cols):
            x = -x_off + (2 * x_off * c / max(1, cols - 1)) if cols > 1 else 0
            holes.append(HoleSpec(hole_label, diameter, round(x, 2), round(y, 2)))
    # Add remaining holes along the center
    for i in range(remaining):
        y = -y_off + (2 * y_off * (i + 1) / (remaining + 1))
        holes.append(HoleSpec(hole_label, diameter, 0, round(y, 2)))

    return tuple(holes[:count])


class MountingBracketGenerator(PartGenerator):
    category = "mounting_bracket"

    def enumerate_variants(self) -> Iterator[PartParams]:
        for material_slug, material in MATERIALS.items():
            for thickness in material.thicknesses_mm:
                # Flat brackets
                for w, h in FLAT_SIZES:
                    for hole_label, hole_count in HOLE_PATTERNS:
                        # Skip if holes too big for the part
                        hole_dia = METRIC_CLEARANCE[hole_label]
                        if hole_dia * 2 > min(w, h):
                            continue
                        # Skip if min feature size violated
                        if hole_dia < material.min_feature_size_mm:
                            continue
                        holes = _distribute_holes(w, h, hole_count, hole_label)
                        yield PartParams(
                            category=self.category,
                            shape="flat",
                            width_mm=w,
                            height_mm=h,
                            thickness_mm=thickness,
                            material_slug=material_slug,
                            hole_specs=holes,
                        )

                # L-brackets (flat pattern for laser cutting)
                for leg1, leg2, bw in L_SIZES:
                    flat_w = leg1 + leg2
                    for hole_label, hole_count in [("M4", 4), ("M5", 4), ("M6", 4)]:
                        hole_dia = METRIC_CLEARANCE[hole_label]
                        if hole_dia < material.min_feature_size_mm:
                            continue
                        holes = _distribute_holes(flat_w, bw, hole_count, hole_label)
                        yield PartParams(
                            category=self.category,
                            shape="l",
                            width_mm=flat_w,
                            height_mm=bw,
                            thickness_mm=thickness,
                            material_slug=material_slug,
                            hole_specs=holes,
                            extra=json.dumps({"leg1": leg1, "leg2": leg2}),
                        )

    def generate_solid(self, params: PartParams) -> cq.Workplane:
        if params.shape == "l" and params.extra:
            return self._generate_l_bracket(params)
        return self._generate_flat_bracket(params)

    def _generate_flat_bracket(self, params: PartParams) -> cq.Workplane:
        """Generate a flat mounting plate."""
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

    def _generate_l_bracket(self, params: PartParams) -> cq.Workplane:
        """Generate an L-bracket as a flat pattern for laser cutting."""
        import json as _json
        extra = _json.loads(params.extra) if params.extra else {}
        leg1 = extra.get("leg1", params.width_mm / 2)
        leg2 = extra.get("leg2", params.width_mm / 2)
        flat_w = leg1 + leg2

        result = (
            cq.Workplane("XY")
            .rect(flat_w, params.height_mm)
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
        material = MATERIALS[params.material_slug]
        shape_name = {"flat": "Flat Bracket", "l": "L-Bracket"}.get(params.shape, "Bracket")
        hole_desc = f"{params.hole_count}x{params.hole_specs[0].label}" if params.hole_specs else "No Holes"
        return (
            f"{material.name} {shape_name} "
            f"{params.width_mm:.0f}x{params.height_mm:.0f}mm "
            f"{hole_desc}"
        )

    def part_description(self, params: PartParams) -> str:
        material = MATERIALS[params.material_slug]
        return (
            f"Laser-cut {material.name.lower()} {params.shape} mounting bracket, "
            f"{params.width_mm:.0f}x{params.height_mm:.0f}x{params.thickness_mm}mm, "
            f"with {params.hole_count} mounting holes."
        )
