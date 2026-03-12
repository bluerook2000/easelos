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
# New flat laser-cut
from pipeline.categories.hinge import HingeGenerator
from pipeline.categories.flange import FlangeGenerator
from pipeline.categories.slotted_bracket import SlottedBracketGenerator
from pipeline.categories.enclosure_panel import EnclosurePanelGenerator
from pipeline.categories.heatsink_plate import HeatsinkPlateGenerator
# Sheet metal
from pipeline.categories.u_channel import UChannelGenerator
from pipeline.categories.z_bracket import ZBracketGenerator
from pipeline.categories.box_enclosure import BoxEnclosureGenerator
from pipeline.categories.din_rail_bracket import DinRailBracketGenerator
# CNC milled
from pipeline.categories.shaft_coupler import ShaftCouplerGenerator
from pipeline.categories.motor_adapter import MotorAdapterGenerator
from pipeline.categories.t_slot_nut import TSlotNutGenerator
from pipeline.categories.bearing_block import BearingBlockGenerator
from pipeline.categories.spacer_block import SpacerBlockGenerator

ALL_GENERATORS = [
    # Original 9
    MountingBracketGenerator(),
    MotorMountGenerator(),
    GussetPlateGenerator(),
    BasePlateGenerator(),
    StandoffGenerator(),
    SensorMountGenerator(),
    ElectronicsPanelGenerator(),
    BearingPlateGenerator(),
    CableBracketGenerator(),
    # New flat laser-cut (5)
    HingeGenerator(),
    FlangeGenerator(),
    SlottedBracketGenerator(),
    EnclosurePanelGenerator(),
    HeatsinkPlateGenerator(),
    # Sheet metal (4)
    UChannelGenerator(),
    ZBracketGenerator(),
    BoxEnclosureGenerator(),
    DinRailBracketGenerator(),
    # CNC milled (5)
    ShaftCouplerGenerator(),
    MotorAdapterGenerator(),
    TSlotNutGenerator(),
    BearingBlockGenerator(),
    SpacerBlockGenerator(),
]

GENERATOR_MAP = {g.category: g for g in ALL_GENERATORS}
