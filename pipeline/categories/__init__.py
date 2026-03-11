# pipeline/categories/__init__.py
"""Part category generators — registry of all available categories."""
from pipeline.categories.mounting_bracket import MountingBracketGenerator
from pipeline.categories.motor_mount import MotorMountGenerator
from pipeline.categories.gusset_plate import GussetPlateGenerator
from pipeline.categories.base_plate import BasePlateGenerator
from pipeline.categories.standoff import StandoffGenerator
from pipeline.categories.sensor_mount import SensorMountGenerator
from pipeline.categories.electronics_panel import ElectronicsPanelGenerator
from pipeline.categories.bearing_plate import BearingPlateGenerator
from pipeline.categories.cable_bracket import CableBracketGenerator

ALL_GENERATORS = [
    MountingBracketGenerator(),
    MotorMountGenerator(),
    GussetPlateGenerator(),
    BasePlateGenerator(),
    StandoffGenerator(),
    SensorMountGenerator(),
    ElectronicsPanelGenerator(),
    BearingPlateGenerator(),
    CableBracketGenerator(),
]

GENERATOR_MAP = {g.category: g for g in ALL_GENERATORS}
