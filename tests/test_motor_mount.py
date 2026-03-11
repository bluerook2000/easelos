# tests/test_motor_mount.py
from pipeline.categories.motor_mount import MotorMountGenerator
from pipeline.materials import MATERIALS


def test_motor_mount_generates_valid_solid():
    gen = MotorMountGenerator()
    assert gen.category == "motor_mount"

    variants = list(gen.enumerate_variants())
    assert len(variants) >= 50

    # All materials represented
    assert {v.material_slug for v in variants} == set(MATERIALS.keys())

    # NEMA shapes present
    shapes = {v.shape for v in variants}
    assert "nema17" in shapes
    assert "nema23" in shapes
    assert "nema34" in shapes

    # First nema17 variant produces valid solid
    nema17 = [v for v in variants if v.shape == "nema17"]
    assert len(nema17) > 0
    solid = gen.generate_solid(nema17[0])
    assert solid.val().Volume() > 0
