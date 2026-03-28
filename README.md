# ANSYS Simulation Pipeline — Labs 1-5 (Variant 13)

Fully scripted pipeline for 5 ANSYS Workbench simulations: parametric CadQuery geometry -> STEP -> ANSYS batch solve -> report-ready results.

## Labs

| Lab | Topic | Solver | Type |
|-----|-------|--------|------|
| 1 | Static Structural (vessel + pads) | ANSYS Mechanical | Steady |
| 2 | Hydrodynamics (pipe + cone) | CFX | Steady |
| 3 | Conjugate Heat Transfer (vessel + coil) | CFX | Steady |
| 4 | Ultrasound (stadium bath + emitter) | CFX | Transient |
| 5 | Mixing / Immersed Solid (vessel + anchor mixer) | CFX | Transient |

## Structure

```
geometry/          CadQuery scripts (Python) -> STEP files
ansys/             ANSYS Workbench journal scripts (.wbjn)
results/lab<N>/    Exported images, CSV, animations
reports/lab<N>/    LaTeX reports
```

## Usage

### Generate geometry (macOS or Linux, needs uv + cadquery)

```bash
make setup         # install dependencies
make allg          # generate all STEP files
make l3g           # or individual lab
```

### Run simulations (Linux, needs ANSYS 2024 R1)

```bash
make l1s           # Lab 1: Static Structural
make l2s           # Lab 2: CFX steady
make l3s           # Lab 3: CFX CHT
make l4s           # Lab 4: CFX transient ultrasound
make l5s           # Lab 5: CFX transient mixing
```

### Compile reports (needs latexmk + texlive)

```bash
make reports
```

## Requirements

- **Geometry**: Python 3.10+, [uv](https://github.com/astral-sh/uv), CadQuery
- **Simulation**: ANSYS 2024 R1 (`runwb2` in PATH)
- **Reports**: LaTeX (latexmk, texlive with T2A/Ukrainian support)
