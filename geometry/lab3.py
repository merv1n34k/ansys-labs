"""Lab 3 — CFX CHT geometry, Variant 13.

Three-body assembly for conjugate heat transfer simulation:
  1. Vessel fluid volume (with coil envelope subtracted)
  2. Coil solid (copper tube wall)
  3. Coil fluid volume (inside the tube)

Helical coil heat exchanger sits inside the cylindrical vessel from common.py.
"""

import math
from pathlib import Path

import cadquery as cq
from cadquery import Vector

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

# Nozzle parameters
NOZZLE_R = 20.0
NOZZLE_LEN = 60.0
VESSEL_NOZZLE_Z_TOP = SHELL_H - 50.0
VESSEL_NOZZLE_Z_BOT = 50.0


def _make_helix_wire():
    """Create a helical wire centred on Z-axis."""
    helix = cq.Wire.makeHelix(
        pitch=COIL_PITCH,
        height=COIL_HEIGHT,
        radius=COIL_HELIX_RADIUS,
    )
    helix = helix.moved(cq.Location(Vector(0, 0, COIL_Z_OFFSET)))
    return helix


def _sweep_circle_along_helix(radius, helix):
    """Sweep a circular cross-section along the helix to create a tube."""
    # Get start point and tangent
    start = helix.startPoint()
    # Create circle at start, perpendicular to helix tangent
    # For a helix, the start tangent is approximately in the XY plane
    circle = cq.Wire.makeCircle(
        radius,
        center=start,
        normal=Vector(0, 0, 1),  # approximate — Frenet frame handles it
    )
    face = cq.Face.makeFromWires(circle)
    solid = cq.Solid.sweep(face, helix, isFrenet=True)
    return solid


def _make_radial_nozzle(z, angle_deg, nozzle_r, length=None):
    """Create a cylindrical nozzle stub extending radially outward at height z."""
    if length is None:
        length = NOZZLE_LEN + WALL + 10
    angle_rad = math.radians(angle_deg)
    dx = math.cos(angle_rad)
    dy = math.sin(angle_rad)
    origin = Vector((R_IN - 5) * dx, (R_IN - 5) * dy, z)
    direction = Vector(dx, dy, 0)
    plane = cq.Plane(origin=origin, normal=direction)
    return cq.Workplane(plane).circle(nozzle_r).extrude(length)


def build():
    """Build and return (vessel_fluid, coil_solid, coil_fluid)."""
    helix = _make_helix_wire()

    # Sweep outer and inner tubes
    outer_solid = _sweep_circle_along_helix(TUBE_OR, helix)
    inner_solid = _sweep_circle_along_helix(TUBE_IR, helix)

    # Coil solid (copper) = outer - inner
    coil_solid = cq.Workplane("XY").newObject([outer_solid])
    coil_inner_wp = cq.Workplane("XY").newObject([inner_solid])
    coil_solid = coil_solid.cut(coil_inner_wp)

    # Coil fluid = inner bore
    coil_fluid = cq.Workplane("XY").newObject([inner_solid])

    # Coil nozzle stubs at helix endpoints
    start_pt = helix.startPoint()
    end_pt = helix.endPoint()
    start_angle = math.degrees(math.atan2(start_pt.y, start_pt.x))
    end_angle = math.degrees(math.atan2(end_pt.y, end_pt.x))

    # Outer nozzle stubs (for coil solid envelope)
    noz_start_outer = _make_radial_nozzle(start_pt.z, start_angle, TUBE_OR)
    noz_end_outer = _make_radial_nozzle(end_pt.z, end_angle, TUBE_OR)
    # Inner nozzle stubs (for coil fluid)
    noz_start_inner = _make_radial_nozzle(start_pt.z, start_angle, TUBE_IR)
    noz_end_inner = _make_radial_nozzle(end_pt.z, end_angle, TUBE_IR)

    # Add nozzle stubs to coil solid, subtract inner bores
    coil_solid = coil_solid.union(noz_start_outer).union(noz_end_outer)
    coil_solid = coil_solid.cut(noz_start_inner).cut(noz_end_inner)

    # Add nozzle stubs to coil fluid
    coil_fluid = coil_fluid.union(noz_start_inner).union(noz_end_inner)

    # Vessel fluid volume
    vessel_fluid = make_vessel_inner_volume()
    # Vessel nozzles
    vessel_noz_top = _make_radial_nozzle(VESSEL_NOZZLE_Z_TOP, 0.0, NOZZLE_R)
    vessel_noz_bot = _make_radial_nozzle(VESSEL_NOZZLE_Z_BOT, 180.0, NOZZLE_R)
    vessel_fluid = vessel_fluid.union(vessel_noz_top).union(vessel_noz_bot)

    # Subtract coil envelope from vessel fluid
    coil_envelope = cq.Workplane("XY").newObject([outer_solid])
    coil_envelope = coil_envelope.union(noz_start_outer).union(noz_end_outer)
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
print(f"Exported assembly (3 bodies) -> {out_path}")
