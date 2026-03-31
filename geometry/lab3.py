"""Lab 3 — CFX CHT geometry, Variant 13.

Vertical pipe-bundle heat exchanger inside a flat-bottom vessel:
  1. vessel_fluid — cylinder, flow enters bottom face, exits top face
  2. coil_solid_copper — copper pipe wall (6 vertical pipes + U-bends)
  3. coil_fluid — fluid inside the pipe

6 vertical straight pipes at R=130mm, 60deg apart,
connected by semicircular U-bends at alternating bottom/top.
Both pipe ends exit through the vessel top face.
"""

import math
from pathlib import Path

import cadquery as cq
from cadquery import Vector
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakePipeShell

from common import make_vessel_inner_volume, R_IN, SHELL_H

TUBE_OD = 25.0
TUBE_WALL = 2.0
TUBE_OR = TUBE_OD / 2.0
TUBE_IR = (TUBE_OD - 2 * TUBE_WALL) / 2.0

N_PIPES = 6
R_COIL = 130.0
Z_BOTTOM = 80.0
Z_TOP = 880.0
Z_EXIT = SHELL_H
PIPE_ANGLES = [math.radians(i * 360 / N_PIPES) for i in range(N_PIPES)]


def _pipe_pos(i):
    a = PIPE_ANGLES[i]
    return R_COIL * math.cos(a), R_COIL * math.sin(a)


def _make_uturn(x1, y1, x2, y2, z_level, goes_below):
    """Semicircular U-bend connecting two pipe ends at z_level."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    r = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / 2
    if goes_below:
        mid = Vector(mx, my, z_level - r)
    else:
        mid = Vector(mx, my, z_level + r)
    return cq.Edge.makeThreePointArc(
        Vector(x1, y1, z_level), mid, Vector(x2, y2, z_level))


def _make_coil_wire():
    edges = []

    # First pipe: inlet riser down from Z_EXIT to Z_BOTTOM
    x0, y0 = _pipe_pos(0)
    edges.append(cq.Edge.makeLine(
        Vector(x0, y0, Z_EXIT), Vector(x0, y0, Z_BOTTOM)))

    for i in range(N_PIPES - 1):
        x1, y1 = _pipe_pos(i)
        x2, y2 = _pipe_pos(i + 1)
        going_down = (i % 2 == 0)  # pipe i went down

        if going_down:
            # Bottom U-turn, then next pipe goes up
            edges.append(_make_uturn(x1, y1, x2, y2, Z_BOTTOM, goes_below=True))
            edges.append(cq.Edge.makeLine(
                Vector(x2, y2, Z_BOTTOM), Vector(x2, y2, Z_TOP)))
        else:
            # Top U-turn, then next pipe goes down
            edges.append(_make_uturn(x1, y1, x2, y2, Z_TOP, goes_below=False))
            edges.append(cq.Edge.makeLine(
                Vector(x2, y2, Z_TOP), Vector(x2, y2, Z_BOTTOM)))

    # Last pipe outlet riser: from current Z to Z_EXIT
    xl, yl = _pipe_pos(N_PIPES - 1)
    last_going_down = ((N_PIPES - 2) % 2 != 0)
    z_last = Z_BOTTOM if last_going_down else Z_TOP
    edges.append(cq.Edge.makeLine(
        Vector(xl, yl, z_last), Vector(xl, yl, Z_EXIT)))

    return cq.Wire.assembleEdges(edges)


def _sweep(radius, wire):
    start = wire.startPoint()
    tangent = wire.tangentAt(0)
    circle = cq.Wire.makeCircle(radius, center=start, normal=tangent)
    builder = BRepOffsetAPI_MakePipeShell(wire.wrapped)
    builder.SetMode(True)  # Frenet
    builder.Add(circle.wrapped)
    builder.Build()
    builder.MakeSolid()
    solid = cq.Solid(builder.Shape())
    if solid.Volume() < 0:
        solid = cq.Solid(solid.wrapped.Reversed())
    return solid


def build():
    wire = _make_coil_wire()
    print(f"  Wire length: {wire.Length():.0f} mm")

    print("  Sweeping outer tube...")
    outer = _sweep(TUBE_OR, wire)
    print("  Sweeping inner tube...")
    inner = _sweep(TUBE_IR, wire)

    outer_wp = cq.Workplane("XY").newObject([outer])
    inner_wp = cq.Workplane("XY").newObject([inner])

    print("  Cutting coil solid...")
    coil_solid = outer_wp.cut(inner_wp)
    coil_fluid = inner_wp

    print("  Cutting vessel fluid...")
    vessel_fluid = make_vessel_inner_volume(flat_bottom=True)
    vessel_fluid = vessel_fluid.cut(outer_wp)

    return vessel_fluid, coil_solid, coil_fluid


print("Building Lab 3 geometry (pipe bundle, Variant 13) ...")
vessel_fluid, coil_solid, coil_fluid = build()

assy = cq.Assembly()
assy.add(vessel_fluid, name="vessel_fluid", color=cq.Color("CadetBlue"))
assy.add(coil_solid, name="coil_solid_copper", color=cq.Color("Orange"))
assy.add(coil_fluid, name="coil_fluid", color=cq.Color("SteelBlue"))

out_dir = Path(__file__).parent / "step"
out_dir.mkdir(exist_ok=True)
out_path = out_dir / "lab3.step"
assy.export(str(out_path))

x0, y0 = _pipe_pos(0)
xl, yl = _pipe_pos(N_PIPES - 1)
print(f"Exported assembly (3 bodies) -> {out_path}")
print(f"Pipe bundle: {N_PIPES} vertical pipes at R={R_COIL:.0f} mm, Z={Z_BOTTOM:.0f}-{Z_TOP:.0f} mm")
print(f"  Coil inlet:  ({x0:.0f}, {y0:.0f}, {Z_EXIT:.0f})")
print(f"  Coil outlet: ({xl:.0f}, {yl:.0f}, {Z_EXIT:.0f})")
print(f"  Vessel inlet:  bottom face Z=0")
print(f"  Vessel outlet: top face Z={SHELL_H:.0f}")
