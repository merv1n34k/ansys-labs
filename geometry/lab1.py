"""Lab 1 — Static Structural analysis geometry (Variant 13).

Single body: cylindrical vessel shell with flat top lid, spherical bottom lid,
and 4 support pads fused into the vessel wall.
Exports as STEP to step/lab1.step.
"""

from pathlib import Path

import cadquery as cq

from common import make_support_pads, make_vessel_shell

vessel = make_vessel_shell()
pads = make_support_pads(n_pads=4)
body = vessel.union(pads)

step_dir = Path(__file__).parent / "step"
step_dir.mkdir(exist_ok=True)
step_path = step_dir / "lab1.step"

cq.exporters.export(body, str(step_path))

bb = body.val().BoundingBox()
print(f"Exported {step_path.name} (single body) -> BBox: X={bb.xlen:.1f} Y={bb.ylen:.1f} Z={bb.zlen:.1f} mm")
