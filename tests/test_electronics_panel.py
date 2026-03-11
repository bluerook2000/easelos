from pipeline.categories.electronics_panel import ElectronicsPanelGenerator
from pipeline.materials import MATERIALS

def test_electronics_panel_generates_valid_solid():
    gen = ElectronicsPanelGenerator()
    assert gen.category == "electronics_panel"
    variants = list(gen.enumerate_variants())
    assert len(variants) >= 50
    assert {v.material_slug for v in variants} == set(MATERIALS.keys())
    # panel shape
    panels = [v for v in variants if v.shape == "panel"]
    assert len(panels) > 0
    solid = gen.generate_solid(panels[0])
    assert solid.val().Volume() > 0
    # din_rail shape
    dins = [v for v in variants if v.shape == "din_rail"]
    assert len(dins) > 0
    solid_d = gen.generate_solid(dins[0])
    assert solid_d.val().Volume() > 0
