# tests/test_materials.py
from pipeline.materials import MATERIALS, get_material, get_available_thicknesses


def test_original_three_materials_still_present():
    """Original 3 Ponoko materials are still defined."""
    assert "aluminum" in MATERIALS
    assert "steel" in MATERIALS
    assert "stainless" in MATERIALS


def test_fourteen_materials_defined():
    """All 14 materials are registered."""
    assert len(MATERIALS) == 14
    expected_slugs = {
        "aluminum", "steel", "stainless",
        "aluminum_6061", "steel_4140", "titanium", "brass", "copper",
        "delrin", "acrylic", "nylon", "hdpe", "polycarbonate", "uhmwpe",
    }
    assert set(MATERIALS.keys()) == expected_slugs


def test_aluminum_properties():
    mat = get_material("aluminum")
    assert mat.name == "5052-H32 Aluminum"
    assert mat.slug == "aluminum"
    assert mat.density_g_cm3 == 2.68
    assert len(mat.thicknesses_mm) == 3


def test_steel_properties():
    mat = get_material("steel")
    assert mat.name == "A1011 Hot Rolled Carbon Steel"
    assert mat.slug == "steel"
    assert mat.density_g_cm3 == 7.87
    assert len(mat.thicknesses_mm) == 3


def test_stainless_properties():
    mat = get_material("stainless")
    assert mat.name == "#4 304 Stainless Steel"
    assert mat.slug == "stainless"
    assert mat.density_g_cm3 == 8.0
    assert len(mat.thicknesses_mm) == 3


def test_new_metal_properties():
    """New metals have valid properties."""
    ti = get_material("titanium")
    assert ti.density_g_cm3 == 4.51
    assert len(ti.thicknesses_mm) == 3
    assert ti.min_feature_size_mm > 0

    brass = get_material("brass")
    assert brass.density_g_cm3 == 8.47
    assert len(brass.thicknesses_mm) == 3


def test_new_plastic_properties():
    """Plastics have valid properties."""
    delrin = get_material("delrin")
    assert delrin.density_g_cm3 == 1.41
    assert len(delrin.thicknesses_mm) == 3

    acrylic = get_material("acrylic")
    assert acrylic.density_g_cm3 == 1.19
    assert len(acrylic.thicknesses_mm) == 3


def test_material_categories():
    """Materials have a 'category' field: metal or plastic."""
    metals = [m for m in MATERIALS.values() if m.category == "metal"]
    plastics = [m for m in MATERIALS.values() if m.category == "plastic"]
    assert len(metals) == 8
    assert len(plastics) == 6


def test_get_available_thicknesses():
    thicknesses = get_available_thicknesses("aluminum")
    assert all(isinstance(t, float) for t in thicknesses)
    assert all(t > 0 for t in thicknesses)


def test_unknown_material_raises():
    """Requesting a non-existent material raises KeyError."""
    import pytest
    with pytest.raises(KeyError):
        get_material("unobtanium")


def test_material_getter_functions():
    """Material getter functions return correct subsets."""
    from pipeline.materials import get_metals, get_plastics, get_laser_cut_materials, get_cnc_materials, get_sheet_metal_materials

    metals = get_metals()
    assert len(metals) == 8
    assert all(m.category == "metal" for m in metals.values())

    plastics = get_plastics()
    assert len(plastics) == 6
    assert all(m.category == "plastic" for m in plastics.values())

    laser = get_laser_cut_materials()
    assert len(laser) == 14

    cnc = get_cnc_materials()
    assert len(cnc) == 8

    sheet = get_sheet_metal_materials()
    assert len(sheet) == 8
