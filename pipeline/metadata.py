# pipeline/metadata.py
"""Generate JSON metadata for a parametric part."""
from pipeline.materials import MATERIALS, get_material
from pipeline.pricing import get_all_prices, get_complexity, get_size_category


MM_PER_INCH = 25.4


def generate_metadata(
    part_id: str,
    category: str,
    name: str,
    description: str,
    width_mm: float,
    height_mm: float,
    thickness_mm: float,
    hole_count: int,
    hole_specs: list[dict],
    material_slug: str,
) -> dict:
    """Generate complete metadata dict for a part.

    Pricing is computed for ALL 3 materials regardless of the part's
    primary material, since the Ponoko matrix is material-independent.
    """
    width_in = width_mm / MM_PER_INCH
    height_in = height_mm / MM_PER_INCH
    area_sq_in = width_in * height_in

    material = get_material(material_slug)
    volume_cm3 = (width_mm / 10) * (height_mm / 10) * (thickness_mm / 10)
    weight_g = round(volume_cm3 * material.density_g_cm3, 2)

    complexity = get_complexity(hole_count)
    size_category = get_size_category(width_in, height_in)

    # Pricing for all 3 materials (same matrix, but labeled per material)
    base_prices = get_all_prices(hole_count, width_in, height_in)
    pricing = {}
    for mat_slug in MATERIALS:
        pricing[mat_slug] = {qty: price for qty, price in base_prices.items()}

    return {
        "part_id": part_id,
        "category": category,
        "name": name,
        "description": description,
        "width_mm": round(width_mm, 2),
        "height_mm": round(height_mm, 2),
        "thickness_mm": thickness_mm,
        "width_in": round(width_in, 2),
        "height_in": round(height_in, 2),
        "area_sq_in": round(area_sq_in, 2),
        "hole_count": hole_count,
        "hole_specs": hole_specs,
        "material": material_slug,
        "material_name": material.name,
        "weight_estimate_g": weight_g,
        "complexity": complexity,
        "size_category": size_category,
        "pricing": pricing,
        "files": {
            "step": "part.step",
            "svg": "profile.svg",
            "dxf": "profile.dxf",
            "png": "thumbnail.png",
            "metadata": "metadata.json",
        },
    }
