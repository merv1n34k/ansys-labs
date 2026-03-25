"""Lab 1 — Static Structural analysis geometry (Variant 13).

Builds the full vessel assembly:
  - Cylindrical shell with flat top lid and spherical bottom lid
  - 4 cylindrical support legs
Exports a single unioned solid to step/lab1.step.
"""

from pathlib import Path

import cadquery as cq

from common import make_support_legs, make_vessel_shell

# Build vessel shell and support legs
vessel = make_vessel_shell()
legs = make_support_legs(n_legs=4)

# Union everything into a single solid body
assembly = vessel.union(legs)

# Export to STEP
step_dir = Path(__file__).parent / "step"
step_dir.mkdir(exist_ok=True)
step_path = step_dir / "lab1.step"

cq.exporters.export(assembly, str(step_path))

# Print confirmation with bounding box
bb = assembly.val().BoundingBox()
print(
    f"Exported {step_path.name} -> "
    f"BBox: X={bb.xlen:.1f} Y={bb.ylen:.1f} Z={bb.zlen:.1f} mm"
)
