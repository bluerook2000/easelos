# tests/test_materials.py
from pipeline.materials import MATERIALS, get_material, get_available_thicknesses


def test_three_materials_defined():
    assert len(MATERIALS) == 3


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


def test_get_available_thicknesses():
    thicknesses = get_available_thicknesses("aluminum")
    assert all(isinstance(t, float) for t in thicknesses)
    assert all(t > 0 for t in thicknesses)


def test_unknown_material_raises():
    import pytest
    with pytest.raises(KeyError):
        get_material("titanium")
