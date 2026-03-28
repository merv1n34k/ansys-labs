"""Lab 3 — CFX CHT geometry, Variant 13.

Three-body assembly for conjugate heat transfer simulation:
  1. vessel_fluid — vessel inner volume with coil envelope subtracted
  2. coil_solid_copper — helical copper tube wall
  3. coil_fluid — fluid inside the coil tube

All inlets/outlets are on the same side (0° / +X direction).
Coil is a single sweep along: radial arm + helix + radial arm.
"""

import math
from pathlib import Path

import cadquery as cq
from cadquery import Vector
from OCP.GC import GC_MakeArcOfCircle
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCP.gp import gp_Pnt

from common import make_vessel_inner_volume, R_IN, R_OUT, SHELL_H, WALL

# Coil parameters (mm)
COIL_HELIX_RADIUS = 180.0
COIL_PITCH = 80.0
COIL_TURNS = 8
COIL_HEIGHT = COIL_PITCH * COIL_TURNS  # 640 mm

TUBE_OD = 25.0
TUBE_WALL = 2.0
TUBE_ID = TUBE_OD - 2 * TUBE_WALL  # 21 mm
TUBE_OR = TUBE_OD / 2.0
TUBE_IR = TUBE_ID / 2.0

# Center coil vertically in vessel
COIL_Z_OFFSET = (SHELL_H - COIL_HEIGHT) / 2.0  # 180 mm

# Nozzle parameters — all at angle 0° (+X direction)
NOZZLE_LEN = 60.0
NOZZLE_END_R = R_OUT + NOZZLE_LEN
VESSEL_NOZZLE_R = 20.0
VESSEL_NOZZLE_Z_TOP = SHELL_H - 50.0
VESSEL_NOZZLE_Z_BOT = 50.0

# Coil arm 90° bend
R_BEND = 50.0
SIN45 = math.sin(math.pi / 4)
EAT_ANGLE = 15.0  # degrees trimmed from each helix end


def _make_arc_edge(start, mid, end):
    """Create a circular arc edge through three points."""
    arc = GC_MakeArcOfCircle(
        gp_Pnt(*start.toTuple()),
        gp_Pnt(*mid.toTuple()),
        gp_Pnt(*end.toTuple()),
    ).Value()
    return cq.Edge(BRepBuilderAPI_MakeEdge(arc).Edge())


def _make_coil_wire():
    """Build coil path: straight +X arm + arc + trimmed helix + arc + straight +X arm.

    All arms at Y=0 going +X — nozzle faces align vertically with vessel nozzles.
    Helix eaten by EAT_ANGLE at each end. Arcs curve in opposite Y directions
    (inlet above, outlet below X-axis). Arc angle = 90° - EAT_ANGLE.
    Arc radius = R_H * sin(θ) / (1 - sin(θ)), derived from the constraint
    that arm junction must be at Y=0 with tangent +X.
    """
    eat_rad = math.radians(EAT_ANGLE)
    eat_h = (EAT_ANGLE / 360.0) * COIL_PITCH

    trimmed_height = COIL_HEIGHT - 2 * eat_h
    helix = cq.Wire.makeHelix(
        pitch=COIL_PITCH,
        height=trimmed_height,
        radius=COIL_HELIX_RADIUS,
    )
    helix = helix.rotate((0, 0, 0), (0, 0, 1), EAT_ANGLE)
    helix = helix.moved(cq.Location(Vector(0, 0, COIL_Z_OFFSET + eat_h)))

    h_start = helix.startPoint()
    h_end = helix.endPoint()

    s = math.sin(eat_rad)
    rho = COIL_HELIX_RADIUS * s / (1 - s)
    x_j = COIL_HELIX_RADIUS * math.cos(eat_rad) / (1 - s)

    # --- INLET (bottom, helix start at +EAT_ANGLE) ---
    # Arc center above X-axis: (x_j, +rho)
    # CW from arm junction (270° from center) to helix start (180°+θ from center)
    mid_a_in = math.radians(225 + EAT_ANGLE / 2)
    M_in = Vector(x_j + rho * math.cos(mid_a_in), rho + rho * math.sin(mid_a_in), h_start.z)
    arc_in = _make_arc_edge(Vector(x_j, 0, h_start.z), M_in, h_start)
    line_in = cq.Edge.makeLine(Vector(NOZZLE_END_R, 0, h_start.z), Vector(x_j, 0, h_start.z))

    # --- OUTLET (top, helix end at -EAT_ANGLE) ---
    # Arc center below X-axis: (x_j, -rho)
    # CW from helix end (180°-θ from center) to arm junction (90° from center)
    mid_a_out = math.radians(135 - EAT_ANGLE / 2)
    M_out = Vector(x_j + rho * math.cos(mid_a_out), -rho + rho * math.sin(mid_a_out), h_end.z)
    arc_out = _make_arc_edge(h_end, M_out, Vector(x_j, 0, h_end.z))
    line_out = cq.Edge.makeLine(Vector(x_j, 0, h_end.z), Vector(NOZZLE_END_R, 0, h_end.z))

    all_edges = [line_in, arc_in] + list(helix.Edges()) + [arc_out, line_out]
    return cq.Wire.assembleEdges(all_edges)


def _sweep_along(radius, wire):
    """Sweep a circular cross-section along a composite wire.

    Uses OCC BRepOffsetAPI_MakePipeShell with binormal mode (Z-axis reference)
    to avoid Frenet frame degeneracy on straight segments.
    """
    from OCP.BRepOffsetAPI import BRepOffsetAPI_MakePipeShell
    from OCP.gp import gp_Dir

    start = wire.startPoint()
    tangent = wire.tangentAt(0)
    circle = cq.Wire.makeCircle(radius, center=start, normal=tangent)

    builder = BRepOffsetAPI_MakePipeShell(wire.wrapped)
    builder.SetMode(gp_Dir(0, 0, 1))
    builder.Add(circle.wrapped)
    builder.Build()
    builder.MakeSolid()
    return cq.Solid(builder.Shape())


def _make_vessel_nozzle(z, nozzle_r):
    """Vessel nozzle stub at angle 0° (+X), from inside vessel wall to outside."""
    start_r = R_IN - 5
    length = NOZZLE_END_R - start_r
    origin = Vector(start_r, 0, z)
    plane = cq.Plane(origin=origin, normal=Vector(1, 0, 0))
    return cq.Workplane(plane).circle(nozzle_r).extrude(length)


def build():
    """Build and return (vessel_fluid, coil_solid, coil_fluid)."""
    coil_wire = _make_coil_wire()

    # Single sweep for outer and inner — no unions needed
    outer_solid = _sweep_along(TUBE_OR, coil_wire)
    inner_solid = _sweep_along(TUBE_IR, coil_wire)

    coil_solid = cq.Workplane("XY").newObject([outer_solid])
    coil_solid = coil_solid.cut(cq.Workplane("XY").newObject([inner_solid]))

    coil_fluid = cq.Workplane("XY").newObject([inner_solid])

    # Vessel fluid volume with nozzles
    vessel_fluid = make_vessel_inner_volume()
    vessel_noz_top = _make_vessel_nozzle(VESSEL_NOZZLE_Z_TOP, VESSEL_NOZZLE_R)
    vessel_noz_bot = _make_vessel_nozzle(VESSEL_NOZZLE_Z_BOT, VESSEL_NOZZLE_R)
    vessel_fluid = vessel_fluid.union(vessel_noz_top).union(vessel_noz_bot)

    # Subtract coil envelope from vessel fluid
    coil_envelope = cq.Workplane("XY").newObject([outer_solid])
    vessel_fluid = vessel_fluid.cut(coil_envelope)

    return vessel_fluid, coil_solid, coil_fluid


print("Building Lab 3 geometry (Variant 13) ...")
vessel_fluid, coil_solid, coil_fluid = build()

assy = cq.Assembly()
assy.add(vessel_fluid, name="vessel_fluid", color=cq.Color("CadetBlue"))
assy.add(coil_solid, name="coil_solid_copper", color=cq.Color("Orange"))
assy.add(coil_fluid, name="coil_fluid", color=cq.Color("SteelBlue"))

out_dir = Path(__file__).parent / "step"
out_dir.mkdir(exist_ok=True)
out_path = out_dir / "lab3.step"

assy.export(str(out_path))

coil_wire = _make_coil_wire()
sp = coil_wire.startPoint()
ep = coil_wire.endPoint()
print(f"Exported assembly (3 bodies) -> {out_path}")
print(f"Nozzle layout (all at 0° / +X side):")
print(f"  Vessel inlet:  Z={VESSEL_NOZZLE_Z_TOP:.0f} mm")
print(f"  Vessel outlet: Z={VESSEL_NOZZLE_Z_BOT:.0f} mm")
print(f"  Coil inlet:    Z={COIL_Z_OFFSET:.0f} mm (arm start)")
print(f"  Coil outlet:   Z={COIL_Z_OFFSET + COIL_HEIGHT:.0f} mm (arm end)")
print(f"  Nozzle end faces at X ≈ {NOZZLE_END_R:.0f} mm (select by max X)")
