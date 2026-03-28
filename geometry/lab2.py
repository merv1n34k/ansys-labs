"""Lab 2 — CFX Steady-State geometry, Variant 13.

Pipe with internal cone obstacle (fluid domain).
  - Pipe: D=100 mm, L=300 mm (internal cylinder)
  - Cone: base D=50 mm tapering to D=10 mm, H=50 mm, centered in pipe
    Wide base faces the inlet (against the flow direction)
  - Boolean subtract: pipe minus cone -> fluid domain with cone-shaped void
"""

from pathlib import Path

import cadquery as cq

# Pipe dimensions (mm)
PIPE_D = 100.0
PIPE_R = PIPE_D / 2
PIPE_L = 300.0

# Cone dimensions (mm) — fits within 50x50x50 bounding box
CONE_BASE_D = 50.0
CONE_TIP_D = 10.0
CONE_H = 50.0
CONE_BASE_R = CONE_BASE_D / 2
CONE_TIP_R = CONE_TIP_D / 2

# Pipe runs along X axis (horizontal): X=0 (inlet) to X=PIPE_L (outlet)
# Cone centered at X = PIPE_L / 2, wide base facing inlet (negative X direction)

# Build pipe (fluid domain cylinder along X)
pipe = cq.Workplane("YZ").circle(PIPE_R).extrude(PIPE_L)

# Build cone as a lofted frustum between two circles
cone_center_x = PIPE_L / 2
cone_base_x = cone_center_x - CONE_H / 2  # wide end, faces inlet
cone_tip_x = cone_center_x + CONE_H / 2  # narrow end, faces outlet

cone = (
    cq.Workplane("YZ")
    .workplane(offset=cone_base_x)
    .circle(CONE_BASE_R)
    .workplane(offset=CONE_H)
    .circle(CONE_TIP_R)
    .loft()
)

# Boolean subtract: fluid domain = pipe - cone
fluid_domain = pipe.cut(cone)

# Export
step_dir = Path(__file__).parent / "step"
step_dir.mkdir(exist_ok=True)
step_path = step_dir / "lab2.step"

cq.exporters.export(fluid_domain, str(step_path))

bb = fluid_domain.val().BoundingBox()
print(f"Exported {step_path.name} -> BBox: X={bb.xlen:.1f} Y={bb.ylen:.1f} Z={bb.zlen:.1f} mm")
