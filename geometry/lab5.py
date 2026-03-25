"""Lab 5 — Mixing / Immersed Solid geometry, Variant 13.

Two separate bodies:
  1. Vessel inner volume (fluid domain) — same shape as Lab 1 interior
  2. Anchor mixer (U-shaped impeller) — immersed solid

Exports two STEP files: lab5_vessel.step and lab5_mixer.step.
"""

import math
from pathlib import Path

import cadquery as cq

from common import make_vessel_inner_volume, R_IN, SHELL_H

# Mixer dimensions (mm)
SHAFT_D = 30.0
SHAFT_R = SHAFT_D / 2
ARM_WIDTH = 20.0
ARM_THICKNESS = 10.0
ARM_HEIGHT = 800.0
ARM_RADIUS = 230.0  # distance from center axis to arm center
BAR_WIDTH = ARM_WIDTH
BAR_THICKNESS = ARM_THICKNESS

# Shaft extends from hemisphere bottom to vessel top
# Hemisphere bottom is at Z = -R_IN (approx -247.9 mm)
# Vessel top is at Z = SHELL_H (1000 mm)
SHAFT_BOTTOM_Z = -R_IN + 20  # 20mm clearance from hemisphere bottom
SHAFT_TOP_Z = SHELL_H
SHAFT_LENGTH = SHAFT_TOP_Z - SHAFT_BOTTOM_Z


def make_anchor_mixer() -> cq.Workplane:
    """Build the anchor (U-shaped) mixer."""
    # Central shaft
    shaft = (
        cq.Workplane("XY")
        .workplane(offset=SHAFT_BOTTOM_Z)
        .circle(SHAFT_R)
        .extrude(SHAFT_LENGTH)
    )

    # Arms bottom Z: where the hemisphere surface intersects at ARM_RADIUS
    # Hemisphere eq: x^2 + y^2 + z^2 = R_IN^2 => z = -sqrt(R_IN^2 - ARM_RADIUS^2)
    arm_bottom_z = -math.sqrt(R_IN**2 - ARM_RADIUS**2) + 10  # 10mm clearance

    # Two vertical arms at 0 and 180 degrees
    arm1 = (
        cq.Workplane("XZ")
        .workplane(offset=-ARM_THICKNESS / 2)
        .center(ARM_RADIUS, arm_bottom_z)
        .rect(ARM_WIDTH, ARM_HEIGHT)
        .extrude(ARM_THICKNESS)
    )
    arm2 = (
        cq.Workplane("XZ")
        .workplane(offset=-ARM_THICKNESS / 2)
        .center(-ARM_RADIUS, arm_bottom_z)
        .rect(ARM_WIDTH, ARM_HEIGHT)
        .extrude(ARM_THICKNESS)
    )

    # Bottom horizontal bar connecting the two arms
    bar_z = arm_bottom_z  # same Z as arm bottoms
    bar_length = 2 * ARM_RADIUS + ARM_WIDTH  # spans full width between arms
    bar = (
        cq.Workplane("XY")
        .workplane(offset=bar_z - BAR_THICKNESS / 2)
        .rect(bar_length, BAR_WIDTH)
        .extrude(BAR_THICKNESS)
    )

    mixer = shaft.union(arm1).union(arm2).union(bar)
    return mixer


# Build both bodies
vessel = make_vessel_inner_volume()
mixer = make_anchor_mixer()

# Export
step_dir = Path(__file__).parent / "step"
step_dir.mkdir(exist_ok=True)

vessel_path = step_dir / "lab5_vessel.step"
mixer_path = step_dir / "lab5_mixer.step"

cq.exporters.export(vessel, str(vessel_path))
bb_v = vessel.val().BoundingBox()
print(f"Exported {vessel_path.name} -> BBox: X={bb_v.xlen:.1f} Y={bb_v.ylen:.1f} Z={bb_v.zlen:.1f} mm")

cq.exporters.export(mixer, str(mixer_path))
bb_m = mixer.val().BoundingBox()
print(f"Exported {mixer_path.name} -> BBox: X={bb_m.xlen:.1f} Y={bb_m.ylen:.1f} Z={bb_m.zlen:.1f} mm")
