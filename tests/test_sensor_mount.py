from pipeline.categories.sensor_mount import SensorMountGenerator
from pipeline.materials import MATERIALS

def test_sensor_mount_generates_valid_solid():
    gen = SensorMountGenerator()
    assert gen.category == "sensor_mount"
    variants = list(gen.enumerate_variants())
    assert len(variants) >= 50
    assert {v.material_slug for v in variants} == set(MATERIALS.keys())
    # proximity shape
    prox = [v for v in variants if v.shape == "proximity"]
    assert len(prox) > 0
    solid = gen.generate_solid(prox[0])
    assert solid.val().Volume() > 0
    # limit_switch shape
    ls = [v for v in variants if v.shape == "limit_switch"]
    assert len(ls) > 0
    solid_ls = gen.generate_solid(ls[0])
    assert solid_ls.val().Volume() > 0
