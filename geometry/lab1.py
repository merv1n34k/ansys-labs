"""Lab 1 — Static Structural analysis geometry (Variant 13).

Builds a named assembly:
  - "vessel" — cylindrical shell with flat top lid and spherical bottom lid
  - "pads"   — 4 rectangular support pads on the vessel wall
Exports as STEP assembly with named bodies to step/lab1.step.
"""

from pathlib import Path

import cadquery as cq

from common import make_support_pads, make_vessel_shell

vessel = make_vessel_shell()
pads = make_support_pads(n_pads=4)

assy = cq.Assembly()
assy.add(vessel, name="vessel", color=cq.Color("LightGray"))
assy.add(pads, name="pads", color=cq.Color("OrangeRed"))

step_dir = Path(__file__).parent / "step"
step_dir.mkdir(exist_ok=True)
step_path = step_dir / "lab1.step"

assy.export(str(step_path))
print(f"Exported {step_path.name} (2 named bodies: vessel, pads)")
