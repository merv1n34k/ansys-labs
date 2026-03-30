"""Lab 3 — CFX CHT geometry, Variant 13.

Simplified snake/serpentine pipe heat exchanger:
  1. vessel_fluid — vessel inner volume with pipe envelope subtracted
  2. coil_solid_copper — copper pipe wall (serpentine pattern)
  3. coil_fluid — fluid inside the pipe

Snake pipe: 6 horizontal passes in the XZ plane at Y=0,
connected by semicircular U-bends. Inlet/outlet both on +X side.
"""

import math
from pathlib import Path

import cadquery as cq
from cadquery import Vector
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakePipeShell
from OCP.gp import gp_Dir

from common import make_vessel_inner_volume, R_IN, R_OUT, SHELL_H, WALL

# Pipe parameters (mm)
TUBE_OD = 25.0
TUBE_WALL = 2.0
TUBE_ID = TUBE_OD - 2 * TUBE_WALL
TUBE_OR = TUBE_OD / 2.0
TUBE_IR = TUBE_ID / 2.0

# Snake layout
N_PASSES = 6
SPACING = 100.0
START_Z = 200.0
X_LEFT = -150.0
X_RIGHT = 150.0
BEND_R = SPACING / 2.0

# Nozzle — pipe inlet/outlet arms extend outside vessel wall
NOZZLE_LEN = 60.0
NOZZLE_END_X = R_OUT + NOZZLE_LEN

# Vessel nozzles
VESSEL_NZ_R = 20.0
VESSEL_NZ_TOP = SHELL_H - 50.0
VESSEL_NZ_BOT = 50.0


def _make_snake_wire():
    """Build serpentine pipe path: inlet arm + 6 passes + U-bends + outlet arm."""
    pb = cq.Workplane("XZ").moveTo(NOZZLE_END_X, START_Z)

    # Inlet arm: from nozzle face to first run start
    pb = pb.lineTo(X_RIGHT, START_Z)

    z = START_Z
    for i in range(N_PASSES):
        if i % 2 == 0:
            pb = pb.lineTo(X_LEFT, z)
            if i < N_PASSES - 1:
                pb = pb.threePointArc(
                    (X_LEFT - BEND_R, z + BEND_R),
                    (X_LEFT, z + SPACING),
                )
        else:
            pb = pb.lineTo(X_RIGHT, z)
            if i < N_PASSES - 1:
                pb = pb.threePointArc(
                    (X_RIGHT + BEND_R, z + BEND_R),
                    (X_RIGHT, z + SPACING),
                )
        if i < N_PASSES - 1:
            z += SPACING

    # Outlet arm: last run ended at X_RIGHT (N_PASSES-1=5 is odd)
    pb = pb.lineTo(NOZZLE_END_X, z)

    return pb.wire().val()


def _sweep_along(radius, wire):
    """Sweep a circular cross-section along a wire using binormal mode."""
    start = wire.startPoint()
    tangent = wire.tangentAt(0)
    circle = cq.Wire.makeCircle(radius, center=start, normal=tangent)

    builder = BRepOffsetAPI_MakePipeShell(wire.wrapped)
    builder.SetMode(gp_Dir(0, 1, 0))
    builder.Add(circle.wrapped)
    builder.Build()
    builder.MakeSolid()
    return cq.Solid(builder.Shape())


def _make_vessel_nozzle(z, nozzle_r):
    """Vessel nozzle stub at +X direction, from inside wall to outside."""
    start_x = R_IN - 5
    length = NOZZLE_END_X - start_x
    origin = Vector(start_x, 0, z)
    plane = cq.Plane(origin=origin, normal=Vector(1, 0, 0))
    return cq.Workplane(plane).circle(nozzle_r).extrude(length)


def build():
    wire = _make_snake_wire()

    outer_solid = _sweep_along(TUBE_OR, wire)
    inner_solid = _sweep_along(TUBE_IR, wire)

    coil_solid = cq.Workplane("XY").newObject([outer_solid])
    coil_solid = coil_solid.cut(cq.Workplane("XY").newObject([inner_solid]))

    coil_fluid = cq.Workplane("XY").newObject([inner_solid])

    # Vessel fluid with nozzles
    vessel_fluid = make_vessel_inner_volume(flat_bottom=True)
    vessel_noz_top = _make_vessel_nozzle(VESSEL_NZ_TOP, VESSEL_NZ_R)
    vessel_noz_bot = _make_vessel_nozzle(VESSEL_NZ_BOT, VESSEL_NZ_R)
    vessel_fluid = vessel_fluid.union(vessel_noz_top).union(vessel_noz_bot)

    # Subtract pipe envelope from vessel fluid
    coil_envelope = cq.Workplane("XY").newObject([outer_solid])
    vessel_fluid = vessel_fluid.cut(coil_envelope)

    return vessel_fluid, coil_solid, coil_fluid


print("Building Lab 3 geometry (snake pipe, Variant 13) ...")
vessel_fluid, coil_solid, coil_fluid = build()

assy = cq.Assembly()
assy.add(vessel_fluid, name="vessel_fluid", color=cq.Color("CadetBlue"))
assy.add(coil_solid, name="coil_solid_copper", color=cq.Color("Orange"))
assy.add(coil_fluid, name="coil_fluid", color=cq.Color("SteelBlue"))

out_dir = Path(__file__).parent / "step"
out_dir.mkdir(exist_ok=True)
out_path = out_dir / "lab3.step"

assy.export(str(out_path))

END_Z = START_Z + (N_PASSES - 1) * SPACING
print(f"Exported assembly (3 bodies) -> {out_path}")
print(f"Snake pipe: {N_PASSES} passes, Z={START_Z:.0f}-{END_Z:.0f} mm")
print(f"  X range: [{X_LEFT:.0f}, {X_RIGHT:.0f}] mm, bend R={BEND_R:.0f} mm")
print(f"  Pipe inlet face:  X={NOZZLE_END_X:.0f}, Z={START_Z:.0f}")
print(f"  Pipe outlet face: X={NOZZLE_END_X:.0f}, Z={END_Z:.0f}")
print(f"  Vessel inlet:  Z={VESSEL_NZ_TOP:.0f} mm")
print(f"  Vessel outlet: Z={VESSEL_NZ_BOT:.0f} mm")
