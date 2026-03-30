"""Lab 2 — CFX Steady-State geometry, Variant 13.

Pipe with internal hopper (hollow cone / frustum shell) obstacle.
  - Pipe: D=100 mm, L=300 mm along X axis
  - Hopper: outer D_large=50 mm -> D_small=25 mm, wall thickness=5 mm, H=50 mm
    Large diameter faces the inlet (against the flow)
  - Boolean subtract: pipe minus hopper shell -> fluid domain
"""

from pathlib import Path

import cadquery as cq

# Pipe dimensions (mm)
PIPE_D = 100.0
PIPE_R = PIPE_D / 2
PIPE_L = 300.0

# Hopper dimensions (mm)
HOPPER_D_LARGE = 50.0
HOPPER_D_SMALL = 25.0
HOPPER_THICKNESS = 5.0
HOPPER_H = 50.0

HOPPER_R_LARGE = HOPPER_D_LARGE / 2   # 25 mm
HOPPER_R_SMALL = HOPPER_D_SMALL / 2   # 12.5 mm
HOPPER_R_LARGE_INNER = HOPPER_R_LARGE - HOPPER_THICKNESS  # 20 mm
HOPPER_R_SMALL_INNER = HOPPER_R_SMALL - HOPPER_THICKNESS  # 7.5 mm

# Pipe along X: X=0 (inlet) to X=300 (outlet)
# Hopper centered at X=150: large end at X=125, small end at X=175
hopper_base_x = PIPE_L / 2 - HOPPER_H / 2  # 125 mm

# Build pipe
pipe = cq.Workplane("YZ").circle(PIPE_R).extrude(PIPE_L)

# Build hopper shell = outer frustum - inner frustum
outer_cone = (
    cq.Workplane("YZ")
    .workplane(offset=hopper_base_x)
    .circle(HOPPER_R_LARGE)
    .workplane(offset=HOPPER_H)
    .circle(HOPPER_R_SMALL)
    .loft()
)

inner_cone = (
    cq.Workplane("YZ")
    .workplane(offset=hopper_base_x)
    .circle(HOPPER_R_LARGE_INNER)
    .workplane(offset=HOPPER_H)
    .circle(HOPPER_R_SMALL_INNER)
    .loft()
)

hopper_shell = outer_cone.cut(inner_cone)

# Fluid domain = pipe - hopper shell
fluid_domain = pipe.cut(hopper_shell)

# Export
step_dir = Path(__file__).parent / "step"
step_dir.mkdir(exist_ok=True)
step_path = step_dir / "lab2.step"

cq.exporters.export(fluid_domain, str(step_path))

bb = fluid_domain.val().BoundingBox()
print(f"Exported {step_path.name} -> BBox: X={bb.xlen:.1f} Y={bb.ylen:.1f} Z={bb.zlen:.1f} mm")
