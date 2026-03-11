# pipeline/materials.py
"""Material definitions mapped to real Ponoko stock."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Material:
    name: str
    slug: str
    ponoko_slug: str
    density_g_cm3: float
    thicknesses_mm: tuple[float, ...]
    kerf_width_mm: float
    min_feature_size_mm: float
    min_part_size_mm: float
    max_sheet_mm: tuple[float, float]  # (x, y)


# Thicknesses chosen as the 3 closest to user-requested 1.5/3/6mm
# from actual Ponoko stock for each material.
MATERIALS: dict[str, Material] = {
    "aluminum": Material(
        name="5052-H32 Aluminum",
        slug="aluminum",
        ponoko_slug="standard-aluminum",
        density_g_cm3=2.68,
        thicknesses_mm=(1.6, 2.5, 3.2),
        kerf_width_mm=0.2,
        min_feature_size_mm=4.8,
        min_part_size_mm=25.4,
        max_sheet_mm=(1200.0, 600.0),
    ),
    "steel": Material(
        name="A1011 Hot Rolled Carbon Steel",
        slug="steel",
        ponoko_slug="a1011-hot-rolled-carbon-steel",
        density_g_cm3=7.87,
        thicknesses_mm=(1.52, 2.66, 3.43),
        kerf_width_mm=0.2,
        min_feature_size_mm=1.0,
        min_part_size_mm=25.4,
        max_sheet_mm=(1200.0, 600.0),
    ),
    "stainless": Material(
        name="#4 304 Stainless Steel",
        slug="stainless",
        ponoko_slug="4-304-stainless-steel",
        density_g_cm3=8.0,
        thicknesses_mm=(1.52, 2.54, 3.05),
        kerf_width_mm=0.2,
        min_feature_size_mm=3.0,
        min_part_size_mm=25.4,
        max_sheet_mm=(1200.0, 600.0),
    ),
}


def get_material(slug: str) -> Material:
    """Get material by slug. Raises KeyError if not found."""
    return MATERIALS[slug]


def get_available_thicknesses(slug: str) -> tuple[float, ...]:
    """Get available Ponoko thicknesses for a material."""
    return MATERIALS[slug].thicknesses_mm
