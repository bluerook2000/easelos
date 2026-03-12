# pipeline/metadata.py
"""Generate JSON metadata for a parametric part."""
from pipeline.materials import (
    MATERIALS, get_material,
    get_laser_cut_materials, get_cnc_materials, get_sheet_metal_materials,
)
from pipeline.pricing import get_all_prices, get_complexity, get_size_category, PROCESS_MULTIPLIERS


MM_PER_INCH = 25.4

# Which material set to price for each manufacturing type.
# CNC and sheet metal use metals only (per D7); laser cut uses all materials.
_MATERIAL_SETS: dict[str, object] = {
    "laser_cut": get_laser_cut_materials,
    "cnc_milled": get_cnc_materials,
    "sheet_metal": get_sheet_metal_materials,
}


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
    manufacturing_type: str = "laser_cut",
) -> dict:
    """Generate complete metadata dict for a part.

    Pricing is computed for materials valid for the manufacturing type:
    - laser_cut: all 14 materials
    - cnc_milled: metals only (8 materials)
    - sheet_metal: metals only (8 materials)
    """
    width_in = width_mm / MM_PER_INCH
    height_in = height_mm / MM_PER_INCH
    area_sq_in = width_in * height_in

    material = get_material(material_slug)
    volume_cm3 = (width_mm / 10) * (height_mm / 10) * (thickness_mm / 10)
    weight_g = round(volume_cm3 * material.density_g_cm3, 2)

    complexity = get_complexity(hole_count)
    size_category = get_size_category(width_in, height_in)

    process_mult = PROCESS_MULTIPLIERS.get(manufacturing_type, 1.0)

    # Pricing for materials valid for this manufacturing type
    get_materials = _MATERIAL_SETS.get(manufacturing_type, get_laser_cut_materials)
    pricing = {}
    for mat_slug, mat in get_materials().items():
        pricing[mat_slug] = get_all_prices(
            hole_count, width_in, height_in,
            material_multiplier=mat.price_multiplier,
            process_multiplier=process_mult,
        )

    files = {
        "step": "part.step",
        "svg": "profile.svg",
        "dxf": "profile.dxf",
        "png": "thumbnail.png",
        "metadata": "metadata.json",
    }
    # Add glb for 3D parts
    if manufacturing_type in ("cnc_milled", "sheet_metal"):
        files["glb"] = "model.glb"

    return {
        "part_id": part_id,
        "category": category,
        "name": name,
        "description": description,
        "manufacturing_type": manufacturing_type,
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
        "files": files,
    }
