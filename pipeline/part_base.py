# pipeline/part_base.py
"""Base class for parametric part generators."""
import hashlib
import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator

import cadquery as cq

from pipeline.exporter import export_step, export_svg, export_dxf, export_png
from pipeline.metadata import generate_metadata
from pipeline.manifest import Manifest
from pipeline.materials import get_material, MATERIALS


@dataclass(frozen=True)
class HoleSpec:
    """Specification for a single hole."""
    label: str          # e.g. "M5"
    diameter_mm: float  # clearance hole diameter
    x_mm: float         # X position relative to part center
    y_mm: float         # Y position relative to part center


# Standard metric clearance holes (close fit per ISO 273)
METRIC_CLEARANCE: dict[str, float] = {
    "M3": 3.4,
    "M4": 4.5,
    "M5": 5.5,
    "M6": 6.6,
    "M8": 9.0,
    "M10": 11.0,
    "M12": 13.5,
}


@dataclass(frozen=True)
class PartParams:
    """Parameters that fully define a part variant."""
    category: str
    shape: str
    width_mm: float
    height_mm: float
    thickness_mm: float
    material_slug: str
    hole_specs: tuple[HoleSpec, ...]
    # Additional shape-specific params as a frozen dict string
    extra: str = ""

    @property
    def part_id(self) -> str:
        if self.hole_specs:
            # Build label counts sorted alphabetically to encode all hole types
            label_counts: dict[str, int] = {}
            for h in self.hole_specs:
                label_counts[h.label] = label_counts.get(h.label, 0) + 1
            # Sort labels for determinism, join as "2xM5+2xM6"
            parts = []
            for label in sorted(label_counts.keys()):
                parts.append(f"{label_counts[label]}x{label}")
            hole_label = "+".join(parts)

            # When multiple distinct hole labels exist, append a short hash
            # of the full hole layout to disambiguate parts with the same
            # label counts but different hole placements.
            unique_labels = set(label_counts.keys())
            if len(unique_labels) > 1:
                canonical = json.dumps(
                    [(h.label, h.diameter_mm, h.x_mm, h.y_mm) for h in self.hole_specs],
                    separators=(",", ":"),
                )
                suffix = hashlib.sha256(canonical.encode()).hexdigest()[:4]
                hole_label = f"{hole_label}-{suffix}"
        else:
            hole_label = "no-holes"
        return (
            f"{self.category}-{self.shape}-"
            f"{self.width_mm:.0f}x{self.height_mm:.0f}x{self.thickness_mm}-"
            f"{hole_label}-{self.material_slug}"
        )

    @property
    def hole_count(self) -> int:
        return len(self.hole_specs)

    def to_dict(self) -> dict:
        """Serializable dict for manifest hashing."""
        return {
            "category": self.category,
            "shape": self.shape,
            "width_mm": self.width_mm,
            "height_mm": self.height_mm,
            "thickness_mm": self.thickness_mm,
            "material_slug": self.material_slug,
            "holes": [(h.label, h.diameter_mm, h.x_mm, h.y_mm) for h in self.hole_specs],
            "extra": self.extra,
        }


class PartGenerator(ABC):
    """Base class for a part category generator."""

    category: str = ""
    manufacturing_type: str = "laser_cut"  # "laser_cut", "cnc_milled", "sheet_metal"

    @abstractmethod
    def generate_solid(self, params: PartParams) -> cq.Workplane:
        """Generate the 3D CadQuery solid for the given parameters."""
        ...

    @abstractmethod
    def enumerate_variants(self) -> Iterator[PartParams]:
        """Yield all parametric variants for this category."""
        ...

    @abstractmethod
    def part_name(self, params: PartParams) -> str:
        """Human-readable name for the part."""
        ...

    @abstractmethod
    def part_description(self, params: PartParams) -> str:
        """Human-readable description for the part."""
        ...

    def generate_all(
        self,
        output_dir: str,
        manifest: Manifest,
        dry_run: bool = False,
    ) -> list[str]:
        """Generate all variants, skipping those already in the manifest."""
        generated = []
        for params in self.enumerate_variants():
            part_id = params.part_id
            if manifest.is_generated(part_id, params.to_dict()):
                continue

            if dry_run:
                generated.append(part_id)
                continue

            part_dir = os.path.join(output_dir, self.category, part_id)
            os.makedirs(part_dir, exist_ok=True)

            # Generate 3D solid
            solid = self.generate_solid(params)

            # Export all formats
            step_path = os.path.join(part_dir, "part.step")
            svg_path = os.path.join(part_dir, "profile.svg")
            dxf_path = os.path.join(part_dir, "profile.dxf")
            png_path = os.path.join(part_dir, "thumbnail.png")
            meta_path = os.path.join(part_dir, "metadata.json")

            export_step(solid, step_path)
            export_svg(solid, svg_path)
            export_dxf(solid, dxf_path)
            try:
                export_png(svg_path, png_path)
            except RuntimeError:
                pass  # PNG is best-effort

            # Export glTF for 3D parts
            if self.manufacturing_type in ("cnc_milled", "sheet_metal"):
                from pipeline.exporter import export_glb
                glb_path = os.path.join(part_dir, "model.glb")
                export_glb(solid, glb_path)  # best-effort

            # Generate metadata
            hole_spec_dicts = [
                {"size": h.label, "diameter_mm": h.diameter_mm, "x_mm": h.x_mm, "y_mm": h.y_mm}
                for h in params.hole_specs
            ]
            meta = generate_metadata(
                part_id=part_id,
                category=self.category,
                name=self.part_name(params),
                description=self.part_description(params),
                width_mm=params.width_mm,
                height_mm=params.height_mm,
                thickness_mm=params.thickness_mm,
                hole_count=params.hole_count,
                hole_specs=hole_spec_dicts,
                material_slug=params.material_slug,
                manufacturing_type=self.manufacturing_type,
            )
            with open(meta_path, "w") as f:
                json.dump(meta, f, indent=2)

            manifest.mark_generated(part_id, params.to_dict())
            generated.append(part_id)

        return generated
