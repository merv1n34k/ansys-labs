"""Lab 3 — CFX CHT geometry, Variant 13.

Conical helix heat exchanger inside a flat-bottom vessel:
  1. vessel_fluid — cylinder, flow enters bottom face, exits top face
  2. coil_solid_copper — copper pipe wall (conical helix)
  3. coil_fluid — fluid inside the pipe

Conical helix: 5 turns, R=180mm at bottom narrowing to R=60mm at top.
Coil inlet/outlet are pipe end faces inside the vessel.
"""

import math
from pathlib import Path

import cadquery as cq
from cadquery import Vector
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakePipeShell
from OCP.gp import gp_Dir

from common import make_vessel_inner_volume, R_IN, R_OUT, SHELL_H

# Pipe parameters (mm)
TUBE_OD = 25.0
TUBE_WALL = 2.0
TUBE_ID = TUBE_OD - 2 * TUBE_WALL
TUBE_OR = TUBE_OD / 2.0
TUBE_IR = TUBE_ID / 2.0

# Conical helix layout
N_TURNS = 5
R_BOTTOM = 180.0    # radius at bottom (large end)
R_TOP = 60.0        # radius at top (narrow end)
Z_START = 100.0     # helix bottom
Z_END = 900.0       # helix top
NUM_POINTS = 150    # spline resolution


def _make_helix_wire():
    """Build conical helix wire from sampled spline points."""
    points = []
    for i in range(NUM_POINTS + 1):
        frac = i / NUM_POINTS
        angle = 2 * math.pi * N_TURNS * frac
        r = R_BOTTOM + (R_TOP - R_BOTTOM) * frac
        z = Z_START + (Z_END - Z_START) * frac
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        points.append(Vector(x, y, z))

    edge = cq.Edge.makeSpline([p for p in points])
    return cq.Wire.assembleEdges([edge])


def _sweep_along(radius, wire):
    """Sweep a circular cross-section along a wire."""
    start = wire.startPoint()
    tangent = wire.tangentAt(0)
    circle = cq.Wire.makeCircle(radius, center=start, normal=tangent)

    builder = BRepOffsetAPI_MakePipeShell(wire.wrapped)
    builder.SetMode(gp_Dir(0, 0, 1))
    builder.Add(circle.wrapped)
    builder.Build()
    builder.MakeSolid()
    return cq.Solid(builder.Shape())


def build():
    wire = _make_helix_wire()

    outer_solid = _sweep_along(TUBE_OR, wire)
    inner_solid = _sweep_along(TUBE_IR, wire)

    coil_solid = cq.Workplane("XY").newObject([outer_solid])
    coil_solid = coil_solid.cut(cq.Workplane("XY").newObject([inner_solid]))

    coil_fluid = cq.Workplane("XY").newObject([inner_solid])

    # Vessel: flat-bottom cylinder, subtract coil envelope
    vessel_fluid = make_vessel_inner_volume(flat_bottom=True)
    coil_envelope = cq.Workplane("XY").newObject([outer_solid])
    vessel_fluid = vessel_fluid.cut(coil_envelope)

    return vessel_fluid, coil_solid, coil_fluid


print("Building Lab 3 geometry (conical helix, Variant 13) ...")
vessel_fluid, coil_solid, coil_fluid = build()

assy = cq.Assembly()
assy.add(vessel_fluid, name="vessel_fluid", color=cq.Color("CadetBlue"))
assy.add(coil_solid, name="coil_solid_copper", color=cq.Color("Orange"))
assy.add(coil_fluid, name="coil_fluid", color=cq.Color("SteelBlue"))

out_dir = Path(__file__).parent / "step"
out_dir.mkdir(exist_ok=True)
out_path = out_dir / "lab3.step"

assy.export(str(out_path))

# Helix endpoint info
start_x = R_BOTTOM
end_x = R_TOP * math.cos(2 * math.pi * N_TURNS)
end_y = R_TOP * math.sin(2 * math.pi * N_TURNS)
print(f"Exported assembly (3 bodies) -> {out_path}")
print(f"Conical helix: {N_TURNS} turns, R={R_BOTTOM:.0f}->{R_TOP:.0f} mm, Z={Z_START:.0f}-{Z_END:.0f} mm")
print(f"  Coil inlet face:  ({start_x:.0f}, 0, {Z_START:.0f})")
print(f"  Coil outlet face: ({end_x:.0f}, {end_y:.0f}, {Z_END:.0f})")
print(f"  Vessel inlet:  bottom face Z=0")
print(f"  Vessel outlet: top face Z={SHELL_H:.0f}")
