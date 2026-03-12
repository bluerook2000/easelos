# pipeline/materials.py
"""Material definitions for laser cutting, CNC milling, and sheet metal."""
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
    category: str = "metal"  # "metal" or "plastic"
    price_multiplier: float = 1.0  # relative to aluminum baseline


# Thicknesses chosen as the 3 closest to user-requested 1.5/3/6mm
# from actual Ponoko stock for each material.
MATERIALS: dict[str, Material] = {
    # --- Original 3 metals (Ponoko stock) ---
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
        category="metal",
        price_multiplier=1.0,
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
        category="metal",
        price_multiplier=1.0,
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
        category="metal",
        price_multiplier=1.0,
    ),
    # --- New metals ---
    "aluminum_6061": Material(
        name="6061-T6 Aluminum",
        slug="aluminum_6061",
        ponoko_slug="6061-t6-aluminum",
        density_g_cm3=2.70,
        thicknesses_mm=(1.6, 3.2, 6.35),
        kerf_width_mm=0.2,
        min_feature_size_mm=4.8,
        min_part_size_mm=25.4,
        max_sheet_mm=(1200.0, 600.0),
        category="metal",
        price_multiplier=1.1,
    ),
    "steel_4140": Material(
        name="4140 Alloy Steel",
        slug="steel_4140",
        ponoko_slug="4140-alloy-steel",
        density_g_cm3=7.85,
        thicknesses_mm=(1.6, 3.2, 6.35),
        kerf_width_mm=0.25,
        min_feature_size_mm=1.5,
        min_part_size_mm=25.4,
        max_sheet_mm=(600.0, 600.0),
        category="metal",
        price_multiplier=1.8,
    ),
    "titanium": Material(
        name="Grade 2 Titanium",
        slug="titanium",
        ponoko_slug="grade-2-titanium",
        density_g_cm3=4.51,
        thicknesses_mm=(1.0, 1.6, 3.2),
        kerf_width_mm=0.3,
        min_feature_size_mm=3.0,
        min_part_size_mm=25.4,
        max_sheet_mm=(600.0, 300.0),
        category="metal",
        price_multiplier=4.0,
    ),
    "brass": Material(
        name="360 Brass",
        slug="brass",
        ponoko_slug="360-brass",
        density_g_cm3=8.47,
        thicknesses_mm=(1.6, 3.2, 6.35),
        kerf_width_mm=0.2,
        min_feature_size_mm=2.0,
        min_part_size_mm=25.4,
        max_sheet_mm=(600.0, 300.0),
        category="metal",
        price_multiplier=2.0,
    ),
    "copper": Material(
        name="110 Copper",
        slug="copper",
        ponoko_slug="110-copper",
        density_g_cm3=8.96,
        thicknesses_mm=(1.6, 3.2, 6.35),
        kerf_width_mm=0.25,
        min_feature_size_mm=2.5,
        min_part_size_mm=25.4,
        max_sheet_mm=(600.0, 300.0),
        category="metal",
        price_multiplier=2.2,
    ),
    # --- Plastics (laser-cut only) ---
    "delrin": Material(
        name="Delrin (Acetal)",
        slug="delrin",
        ponoko_slug="delrin-acetal",
        density_g_cm3=1.41,
        thicknesses_mm=(1.5, 3.0, 6.0),
        kerf_width_mm=0.15,
        min_feature_size_mm=1.0,
        min_part_size_mm=25.4,
        max_sheet_mm=(800.0, 450.0),
        category="plastic",
        price_multiplier=0.7,
    ),
    "acrylic": Material(
        name="Cast Acrylic",
        slug="acrylic",
        ponoko_slug="cast-acrylic",
        density_g_cm3=1.19,
        thicknesses_mm=(1.5, 3.0, 6.0),
        kerf_width_mm=0.15,
        min_feature_size_mm=1.0,
        min_part_size_mm=25.4,
        max_sheet_mm=(800.0, 450.0),
        category="plastic",
        price_multiplier=0.6,
    ),
    "nylon": Material(
        name="Nylon 6/6",
        slug="nylon",
        ponoko_slug="nylon-6-6",
        density_g_cm3=1.14,
        thicknesses_mm=(1.5, 3.0, 6.0),
        kerf_width_mm=0.15,
        min_feature_size_mm=1.0,
        min_part_size_mm=25.4,
        max_sheet_mm=(800.0, 450.0),
        category="plastic",
        price_multiplier=0.75,
    ),
    "hdpe": Material(
        name="HDPE",
        slug="hdpe",
        ponoko_slug="hdpe",
        density_g_cm3=0.97,
        thicknesses_mm=(1.5, 3.0, 6.0),
        kerf_width_mm=0.2,
        min_feature_size_mm=1.5,
        min_part_size_mm=25.4,
        max_sheet_mm=(800.0, 450.0),
        category="plastic",
        price_multiplier=0.55,
    ),
    "polycarbonate": Material(
        name="Polycarbonate",
        slug="polycarbonate",
        ponoko_slug="polycarbonate",
        density_g_cm3=1.20,
        thicknesses_mm=(1.5, 3.0, 6.0),
        kerf_width_mm=0.15,
        min_feature_size_mm=1.0,
        min_part_size_mm=25.4,
        max_sheet_mm=(800.0, 450.0),
        category="plastic",
        price_multiplier=0.8,
    ),
    "uhmwpe": Material(
        name="UHMW-PE",
        slug="uhmwpe",
        ponoko_slug="uhmw-pe",
        density_g_cm3=0.93,
        thicknesses_mm=(3.0, 6.0, 12.0),
        kerf_width_mm=0.2,
        min_feature_size_mm=1.5,
        min_part_size_mm=25.4,
        max_sheet_mm=(600.0, 300.0),
        category="plastic",
        price_multiplier=0.9,
    ),
}


def get_material(slug: str) -> Material:
    """Get material by slug. Raises KeyError if not found."""
    return MATERIALS[slug]


def get_available_thicknesses(slug: str) -> tuple[float, ...]:
    """Get available Ponoko thicknesses for a material."""
    return MATERIALS[slug].thicknesses_mm


def get_metals() -> dict[str, Material]:
    """Get all metal materials."""
    return {k: v for k, v in MATERIALS.items() if v.category == "metal"}


def get_plastics() -> dict[str, Material]:
    """Get all plastic materials."""
    return {k: v for k, v in MATERIALS.items() if v.category == "plastic"}


def get_laser_cut_materials() -> dict[str, Material]:
    """Get all materials suitable for laser cutting (all materials)."""
    return dict(MATERIALS)


def get_cnc_materials() -> dict[str, Material]:
    """Get materials suitable for CNC milling (metals only)."""
    return get_metals()


def get_sheet_metal_materials() -> dict[str, Material]:
    """Get materials suitable for sheet metal bending (metals only)."""
    return get_metals()
