"""Lab 5 — Mixing / Immersed Solid geometry, Variant 13.

Two separate bodies:
  1. Vessel inner volume (fluid domain)
  2. Anchor mixer:
     - Central axle (same diameter as tube, flat ends)
     - U-tube (two arms + bottom bar with round corners)
     - Axle bottom aligned with bottom of horizontal bar

Exports assembly STEP (lab5.step) + individual files for viewing.
"""

import math
from pathlib import Path

import cadquery as cq
from cadquery import Vector

from common import make_vessel_inner_volume, R_IN, SHELL_H

TUBE_D = 12.0
TUBE_R = TUBE_D / 2
ARM_RADIUS = 80.0
CORNER_R = 15.0

ARM_BOTTOM_Z = 150.0
ARM_TOP_Z = 260.0
AXLE_TOP_Z = 330.0
AXLE_BOTTOM_Z = ARM_BOTTOM_Z - TUBE_R


def make_anchor_mixer():
    u_path = (
        cq.Workplane("XZ")
        .moveTo(ARM_RADIUS, ARM_TOP_Z)
        .lineTo(ARM_RADIUS, ARM_BOTTOM_Z + CORNER_R)
        .threePointArc(
            (ARM_RADIUS - CORNER_R * (1 - math.cos(math.pi / 4)),
             ARM_BOTTOM_Z + CORNER_R * (1 - math.sin(math.pi / 4))),
            (ARM_RADIUS - CORNER_R, ARM_BOTTOM_Z),
        )
        .lineTo(-ARM_RADIUS + CORNER_R, ARM_BOTTOM_Z)
        .threePointArc(
            (-ARM_RADIUS + CORNER_R * (1 - math.cos(math.pi / 4)),
             ARM_BOTTOM_Z + CORNER_R * (1 - math.sin(math.pi / 4))),
            (-ARM_RADIUS, ARM_BOTTOM_Z + CORNER_R),
        )
        .lineTo(-ARM_RADIUS, ARM_TOP_Z)
        .consolidateWires()
    )
    wire = u_path.val()
    start = wire.startPoint()
    tangent = wire.tangentAt(0)
    circle = cq.Wire.makeCircle(TUBE_R, center=start, normal=tangent)
    face = cq.Face.makeFromWires(circle)
    u_tube = cq.Workplane("XY").newObject([cq.Solid.sweep(face, wire, isFrenet=True)])

    axle = (
        cq.Workplane("XY")
        .workplane(offset=AXLE_BOTTOM_Z)
        .circle(TUBE_R)
        .extrude(AXLE_TOP_Z - AXLE_BOTTOM_Z)
    )

    mixer = u_tube.union(axle)
    return mixer


vessel = make_vessel_inner_volume()
mixer = make_anchor_mixer()

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
print(f"  Tube D: {TUBE_D:.0f} mm, Axle Z: {AXLE_BOTTOM_Z:.0f}-{AXLE_TOP_Z:.0f} mm")

# Assembly STEP for ANSYS (both bodies in one file, named)
assy = cq.Assembly()
assy.add(vessel, name="vessel_fluid", color=cq.Color("CadetBlue"))
assy.add(mixer, name="mixer", color=cq.Color("Orange"))
assy_path = step_dir / "lab5.step"
assy.export(str(assy_path))
print(f"Exported {assy_path.name} (assembly: vessel_fluid + mixer)")
